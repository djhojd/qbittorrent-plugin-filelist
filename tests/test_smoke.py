import filelist


def test_class_attributes_present():
    assert filelist.filelist.name == 'FileList'
    assert filelist.filelist.url == 'https://filelist.io'
    assert 'all' in filelist.filelist.supported_categories
