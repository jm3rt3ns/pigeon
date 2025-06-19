import re


def get_verses(file_path):
    with open(file_path, "rt") as markdown_file:
        result = re.split(r"\n\n", markdown_file.read())
        return result