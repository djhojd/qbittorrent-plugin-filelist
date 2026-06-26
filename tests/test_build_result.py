import filelist

FL = filelist.filelist


def _sample():
    return {
        'id': 42,
        'name': 'Some.Movie.2024',
        'category': 'Filme HD',
        'size': 1610612736,
        'seeders': 10,
        'leechers': 2,
        'upload_date': '2024-01-15 12:30:00',
        'download_link': 'https://filelist.io/download.php?id=42&passkey=abc',
    }


def test_maps_all_fields():
    inst = FL(config_path='nonexistent.ini')
    r = inst._build_result(_sample(), passkey='abc')
    assert r['link'] == 'https://filelist.io/download.php?id=42&passkey=abc'
    assert r['name'] == '[Filme HD] Some.Movie.2024'
    assert r['size'] == '1610612736'
    assert r['seeds'] == 10
    assert r['leech'] == 2
    assert r['engine_url'] == 'https://filelist.io'
    assert r['desc_link'] == 'https://filelist.io/details.php?id=42'
    assert r['pub_date'] == 1705321800


def test_falls_back_to_constructed_link_with_passkey():
    inst = FL(config_path='nonexistent.ini')
    t = _sample()
    del t['download_link']
    r = inst._build_result(t, passkey='abc')
    assert r['link'] == 'https://filelist.io/download.php?id=42&passkey=abc'


def test_missing_numeric_fields_default_to_minus_one():
    inst = FL(config_path='nonexistent.ini')
    t = {'id': 1, 'name': 'X', 'download_link': 'u'}
    r = inst._build_result(t, passkey='abc')
    assert r['size'] == '-1'
    assert r['seeds'] == -1
    assert r['leech'] == -1
    assert r['pub_date'] == -1
