import filelist

FL = filelist.filelist


def test_parses_valid_datetime_to_utc_epoch():
    assert FL._parse_pub_date('2024-01-15 12:30:00') == 1705321800


def test_empty_returns_minus_one():
    assert FL._parse_pub_date('') == -1
    assert FL._parse_pub_date(None) == -1


def test_malformed_returns_minus_one():
    assert FL._parse_pub_date('not a date') == -1
