import filelist

FL = filelist.filelist


def test_prefixes_category():
    t = {'name': 'Some.Movie.2024', 'category': 'Filme HD'}
    assert FL._format_name(t) == '[Filme HD] Some.Movie.2024'


def test_appends_flags():
    t = {'name': 'X', 'category': 'Filme HD', 'freeleech': 1,
         'doubleup': 1, 'internal': 1}
    assert FL._format_name(t) == '[Filme HD] X [FreeLeech] [2x] [Internal]'


def test_missing_category_is_omitted():
    t = {'name': 'X'}
    assert FL._format_name(t) == 'X'


def test_falsy_flags_not_shown():
    t = {'name': 'X', 'category': 'Audio', 'freeleech': 0, 'doubleup': 0}
    assert FL._format_name(t) == '[Audio] X'
