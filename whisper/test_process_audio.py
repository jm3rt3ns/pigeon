from .processor import process_audio

test_dir = "test files\\All My Ways Are Known to You\\"


def test__slide_change_directions_match_timestamps():
    with open(test_dir + "lyrics.md", "rt") as lyrics_file:
        with open(test_dir + "audio.mp3", "rt") as audio_file:
            with open(test_dir + "timestamps.md", "rt") as timestamps_file:
                # extract the lyrics into slides based on the new lines
                slide_dict = get_slide_info(lyrics_file)

                # extract the validation data from timestamps.md
                for idx, line in enumerate(timestamps_file.readlines()):
                    if idx == 0:
                        print("HEADER...")
                        continue

                    (
                        audio_clip_start,
                        audio_clip_end,
                        min_expected_time,
                        max_expected_time,
                        expected_slide,
                    ) = line.split(",")

                    min_expected_time = int(min_expected_time)
                    max_expected_time = int(max_expected_time)

                    # run the processor and receive the slide commands and timestamps back
                    predicted_slide, transition_time = process_audio(
                        audio_file, slide_dict
                    )

                    assert predicted_slide == int(expected_slide)
                    assert (
                        transition_time > min_expected_time
                        and transition_time < max_expected_time
                    )


def get_slide_info(lyrics_file):
    slides = lyrics_file.read().split("\n\n")
    slide_dict = {}
    for idx, slide in enumerate(slides):
        slide_dict[idx] = slide.split("\n")

    print(slide_dict)
    return slide_dict
