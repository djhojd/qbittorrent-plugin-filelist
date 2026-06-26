import filelist


def test_module_has_main_guarded_entry():
    src = open(filelist.__file__, encoding='utf-8').read()
    assert "if __name__ == '__main__':" in src
