import filelist

FL = filelist.filelist


def test_known_category_maps_to_ids():
    assert FL.supported_categories['movies'] == '1,2,3,4,6,19,20,25,26'
    assert FL.supported_categories['tv'] == '21,23,27'


def test_all_is_empty_string():
    assert FL.supported_categories['all'] == ''


def test_books_is_not_supported():
    assert 'books' not in FL.supported_categories
