import filelist

FL = filelist.filelist


def test_download_torrent_prints_download_file_output(capsys):
    FL(config_path='x.ini').download_torrent('https://filelist.io/download.php?id=1')
    out = capsys.readouterr().out.strip()
    assert out == '/tmp/fake.torrent https://filelist.io/download.php?id=1'
