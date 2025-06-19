from .helpers.helpers import get_verses


def test_verses_split_as_expected():
    result = get_verses("./test files/we gather together.md")

    assert len(result) == 3