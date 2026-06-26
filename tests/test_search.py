import json

import filelist

FL = filelist.filelist


def test_search_prints_results(fakes, creds_file):
    helpers, novaprinter = fakes
    helpers._state['response'] = json.dumps([
        {'id': 1, 'name': 'A', 'category': 'Filme HD', 'size': 100,
         'seeders': 5, 'leechers': 1, 'upload_date': '2024-01-15 12:30:00',
         'download_link': 'https://filelist.io/download.php?id=1&passkey=k'},
    ])
    FL(config_path=creds_file).search('matrix', 'movies')
    assert len(novaprinter.printed) == 1
    assert novaprinter.printed[0]['name'] == '[Filme HD] A'


def test_search_builds_correct_url(fakes, creds_file):
    helpers, _ = fakes
    FL(config_path=creds_file).search('matrix', 'movies')
    url = helpers._state['last_url']
    assert 'username=tester' in url
    assert 'passkey=secretkey123' in url
    assert 'action=search-torrents' in url
    assert 'type=name' in url
    assert 'category=1%2C2%2C3%2C4%2C6%2C19%2C20%2C25%2C26' in url


def test_search_uses_imdb_type(fakes, creds_file):
    helpers, _ = fakes
    FL(config_path=creds_file).search('tt0111161', 'all')
    url = helpers._state['last_url']
    assert 'type=imdb' in url
    assert 'query=tt0111161' in url


def test_search_missing_credentials_prints_nothing(fakes, tmp_path, capsys):
    _, novaprinter = fakes
    FL(config_path=tmp_path / 'nope.ini').search('x', 'all')
    assert novaprinter.printed == []
    assert 'FileList' in capsys.readouterr().err


def test_search_network_error_is_swallowed(fakes, creds_file, capsys):
    helpers, novaprinter = fakes
    helpers._state['response'] = RuntimeError('boom')
    FL(config_path=creds_file).search('x', 'all')
    assert novaprinter.printed == []
    assert 'boom' in capsys.readouterr().err


def test_search_empty_result(fakes, creds_file):
    helpers, novaprinter = fakes
    helpers._state['response'] = '[]'
    FL(config_path=creds_file).search('x', 'all')
    assert novaprinter.printed == []
