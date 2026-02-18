"""Disc Rip Automation — automates MakeMKV disc ripping on Windows.

Watches for disc insertion, classifies content (film vs TV show),
creates organized folder structure, rips, and ejects.

Configure via environment variables (see .env.example).

Usage:
    python disc_rip.py                 # Normal operation — watch and rip
    python disc_rip.py --clear-batch   # Reset TV show batch state
"""

import os
import sys
import json
import time
import ctypes
import subprocess
import re
import shutil
from pathlib import Path
from dataclasses import dataclass


# ── Configuration (all overridable via env vars) ───────────────────────────

MAKEMKV_PATH  = os.getenv("MAKEMKV_PATH", r"C:\Program Files (x86)\MakeMKV\makemkvcon64.exe")
FILMS_DIR     = Path(os.getenv("FILMS_DIR", r"D:\Films"))
SHOWS_DIR     = Path(os.getenv("SHOWS_DIR", r"D:\Shows"))
DISC_DRIVE    = os.getenv("DISC_DRIVE", "D:")
DISC_INDEX    = int(os.getenv("DISC_INDEX", "0"))
MIN_FEATURE   = int(os.getenv("MIN_FEATURE_MINUTES", "60"))
MIN_EPISODE   = int(os.getenv("MIN_EPISODE_MINUTES", "15"))
MAX_EPISODE   = int(os.getenv("MAX_EPISODE_MINUTES", "65"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "10"))
BATCH_FILE    = Path(os.getenv("BATCH_STATE_FILE", "batch_state.json"))


# ── Data ───────────────────────────────────────────────────────────────────

@dataclass
class Title:
    index: int
    name: str
    duration_sec: int

    @property
    def minutes(self):
        return self.duration_sec / 60

    @property
    def duration_str(self):
        h, rem = divmod(self.duration_sec, 3600)
        m, s = divmod(rem, 60)
        return f"{h}:{m:02d}:{s:02d}"


# ── Disc Operations ───────────────────────────────────────────────────────

def disc_present():
    """Check if a disc is loaded in the optical drive."""
    drive = DISC_DRIVE.rstrip("\\") + "\\"
    buf = ctypes.create_unicode_buffer(261)
    return bool(ctypes.windll.kernel32.GetVolumeInformationW(
        drive, buf, 261, None, None, None, None, 0
    ))


def wait_for_disc():
    print(f"Waiting for disc in {DISC_DRIVE} ...")
    while not disc_present():
        time.sleep(POLL_INTERVAL)
    print("Disc detected.\n")


def eject_disc():
    winmm = ctypes.windll.winmm
    winmm.mciSendStringW(f"open {DISC_DRIVE} type cdaudio alias disc", None, 0, None)
    winmm.mciSendStringW("set disc door open", None, 0, None)
    winmm.mciSendStringW("close disc", None, 0, None)
    print("Disc ejected.")


# ── MakeMKV Integration ───────────────────────────────────────────────────

def scan_disc():
    """Scan disc with makemkvcon. Returns (disc_name, [Title])."""
    print("Scanning disc...")
    proc = subprocess.run(
        [MAKEMKV_PATH, "-r", "info", f"disc:{DISC_INDEX}"],
        capture_output=True, text=True, timeout=300
    )

    disc_name = "Unknown"
    titles = {}

    for line in proc.stdout.splitlines():
        # Disc name
        if m := re.match(r'CINFO:2,0,"(.+)"', line):
            disc_name = m.group(1)
        # Title name
        if m := re.match(r'TINFO:(\d+),2,0,"(.+)"', line):
            titles.setdefault(int(m.group(1)), {})["name"] = m.group(2)
        # Duration
        if m := re.match(r'TINFO:(\d+),9,0,"(\d+):(\d+):(\d+)"', line):
            idx = int(m.group(1))
            titles.setdefault(idx, {})["dur"] = (
                int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4))
            )

    parsed = [
        Title(i, t.get("name", f"Title {i}"), t.get("dur", 0))
        for i, t in sorted(titles.items()) if t.get("dur", 0) > 0
    ]

    print(f"Disc: {disc_name}")
    for t in parsed:
        print(f"  [{t.index}] {t.name} ({t.duration_str})")

    return disc_name, parsed


def rip_titles(indices, output_dir):
    """Rip the given title indices to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for idx in indices:
        subprocess.run(
            [MAKEMKV_PATH, "mkv", f"disc:{DISC_INDEX}", str(idx), str(output_dir)],
            timeout=7200
        )


# ── Content Classification ────────────────────────────────────────────────

def classify(titles):
    """Auto-detect content type. Returns (type, main_titles, extras)."""
    episodes = [t for t in titles if MIN_EPISODE <= t.minutes <= MAX_EPISODE]
    features = [t for t in titles if t.minutes >= MIN_FEATURE]

    # Multiple mid-length titles → TV show
    if len(episodes) >= 2:
        extras = [t for t in titles if t not in episodes]
        return "show", sorted(episodes, key=lambda t: t.index), extras

    # One long title → film
    if features:
        main = max(features, key=lambda t: t.duration_sec)
        return "film", [main], [t for t in titles if t is not main]

    # Fallback: longest title is main content
    main = max(titles, key=lambda t: t.duration_sec)
    return "film", [main], [t for t in titles if t is not main]


# ── Batch State (multi-disc TV shows) ─────────────────────────────────────

def load_batch():
    return json.loads(BATCH_FILE.read_text()) if BATCH_FILE.exists() else None


def save_batch(state):
    BATCH_FILE.write_text(json.dumps(state, indent=2))


def clear_batch():
    BATCH_FILE.unlink(missing_ok=True)


# ── Helpers ────────────────────────────────────────────────────────────────

def clean_disc_name(raw):
    """Turn 'THE_MATRIX_DISC1' into 'The Matrix'."""
    name = re.sub(r'[_]', ' ', raw)
    name = re.sub(r'\s*(disc|disk|d)\s*\d+\s*$', '', name, flags=re.IGNORECASE)
    return name.strip().title()


def safe_filename(name):
    """Remove characters illegal in Windows filenames."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()


# ── User Prompting (once per batch) ───────────────────────────────────────

def prompt_once(disc_name, detected_type, main_titles):
    """Prompt user to confirm or correct autodetected settings."""
    pretty = clean_disc_name(disc_name)

    print(f"\n{'─' * 50}")
    print(f"  Detected:  {detected_type.upper()}")
    print(f"  Name:      {pretty}")
    print(f"  Titles:    {len(main_titles)} main")
    print(f"{'─' * 50}")

    choice = input(f"Type [{'F' if detected_type == 'film' else 'S'}] (F=film, S=show): ").strip().upper()
    if choice == "F":
        detected_type = "film"
    elif choice == "S":
        detected_type = "show"

    name = input(f"Name [{pretty}]: ").strip() or pretty
    result = {"type": detected_type, "name": name}

    if detected_type == "show":
        s = input("Season [1]: ").strip()
        result["season"] = int(s) if s else 1
        e = input("Starting episode [1]: ").strip()
        result["next_episode"] = int(e) if e else 1

    return result


# ── Ripping Logic ─────────────────────────────────────────────────────────

def rip_film(name, main, extras):
    folder = FILMS_DIR / safe_filename(name)

    print(f"\nRipping feature -> {folder}")
    rip_titles([main[0].index], folder)

    if extras:
        bts = folder / "Behind the Scenes"
        print(f"Ripping {len(extras)} extras -> {bts}")
        rip_titles([t.index for t in extras], bts)


def rip_show(name, season, start_ep, episodes, extras):
    season_dir = SHOWS_DIR / safe_filename(name) / f"Season {season:02d}"
    season_dir.mkdir(parents=True, exist_ok=True)

    for i, ep in enumerate(episodes):
        ep_num = start_ep + i
        label = f"{safe_filename(name)} - S{season:02d}E{ep_num:02d}"
        print(f"\nRipping {label}")

        # Rip to temp dir so we can rename the output
        tmp = season_dir / f"_tmp_ep{ep_num}"
        rip_titles([ep.index], tmp)

        for f in tmp.iterdir():
            if f.suffix.lower() == ".mkv":
                f.rename(season_dir / f"{label}.mkv")
        shutil.rmtree(tmp, ignore_errors=True)

    if extras:
        bts = season_dir / "Behind the Scenes"
        print(f"Ripping {len(extras)} extras -> {bts}")
        rip_titles([t.index for t in extras], bts)

    next_ep = start_ep + len(episodes)
    save_batch({"name": name, "season": season, "next_episode": next_ep})
    print(f"Batch saved — next disc starts at E{next_ep:02d}")


# ── Main Loop ─────────────────────────────────────────────────────────────

def process_disc():
    disc_name, titles = scan_disc()
    if not titles:
        print("No titles found on disc.")
        eject_disc()
        return

    content_type, main, extras = classify(titles)

    # If a batch is active (multi-disc TV show), offer to continue it
    batch = load_batch()
    if batch:
        print(f"\nActive batch: {batch['name']} S{batch['season']:02d}, "
              f"next E{batch['next_episode']:02d}")
        if input("Continue this batch? [Y/n]: ").strip().lower() not in ("n", "no"):
            rip_show(batch["name"], batch["season"], batch["next_episode"], main, extras)
            eject_disc()
            return
        clear_batch()

    # No batch — prompt once for this disc/batch
    settings = prompt_once(disc_name, content_type, main)

    if settings["type"] == "film":
        rip_film(settings["name"], main, extras)
    else:
        rip_show(
            settings["name"], settings["season"],
            settings["next_episode"], main, extras
        )

    eject_disc()


def main():
    print("=== Disc Rip Automation ===")
    print(f"Films -> {FILMS_DIR}  |  Shows -> {SHOWS_DIR}  |  Drive: {DISC_DRIVE}\n")

    if "--clear-batch" in sys.argv:
        clear_batch()
        print("Batch state cleared.\n")

    try:
        while True:
            wait_for_disc()
            process_disc()
            print()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
