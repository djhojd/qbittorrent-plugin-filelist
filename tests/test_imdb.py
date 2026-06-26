import filelist

FL = filelist.filelist


def test_detects_bare_imdb_id():
    assert FL._detect_imdb('tt0111161') == 'tt0111161'


def test_detects_imdb_in_url():
    assert FL._detect_imdb('https://www.imdb.com/title/tt0111161/') == 'tt0111161'


def test_detects_8_digit_id():
    assert FL._detect_imdb('tt12345678') == 'tt12345678'


def test_plain_text_returns_none():
    assert FL._detect_imdb('the matrix 1999') is None


def test_handles_url_escaped_input():
    assert FL._detect_imdb('the%20matrix') is None
