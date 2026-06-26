import filelist

FL = filelist.filelist


def test_loads_valid_credentials(creds_file):
    inst = FL(config_path=creds_file)
    username, passkey, err = inst._load_credentials()
    assert err is None
    assert username == 'tester'
    assert passkey == 'secretkey123'


def test_missing_file_returns_error(tmp_path):
    inst = FL(config_path=tmp_path / 'nope.ini')
    username, passkey, err = inst._load_credentials()
    assert username is None and passkey is None
    assert 'missing' in err.lower()


def test_placeholder_values_rejected(tmp_path):
    p = tmp_path / 'credentials.ini'
    p.write_text("[filelist]\nusername = YOUR_USERNAME\npasskey = YOUR_PASSKEY\n")
    inst = FL(config_path=p)
    username, passkey, err = inst._load_credentials()
    assert err is not None and username is None


def test_empty_values_rejected(tmp_path):
    p = tmp_path / 'credentials.ini'
    p.write_text("[filelist]\nusername =\npasskey =\n")
    inst = FL(config_path=p)
    _, _, err = inst._load_credentials()
    assert err is not None
