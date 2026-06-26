# VERSION: 1.0
# AUTHORS: djhojd

import configparser
import json
import logging
import pathlib
import re
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from urllib.parse import unquote, urlencode

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter


class filelist(object):
    url = 'https://filelist.io'
    name = 'FileList'
    api_url = 'https://filelist.io/api.php'

    supported_categories = {
        'all':      '',
        'movies':   '1,2,3,4,6,19,20,25,26',
        'tv':       '21,23,27',
        'music':    '5,11,12',
        'games':    '9,10',
        'anime':    '24',
        'software': '8,17,22',
    }

    _IMDB_RE = re.compile(r'(tt\d{7,8})')
    _PLACEHOLDERS = {'', 'yourname', 'YOUR_USERNAME', 'YOUR_PASSKEY',
                     'abc123def456...'}

    def __init__(self, config_path=None, log_path=None):
        if config_path is None:
            config_path = pathlib.Path(__file__).parent / 'credentials.ini'
        self._config_path = pathlib.Path(config_path)
        if log_path is None:
            log_path = pathlib.Path(__file__).parent / 'filelist.log'
        self._logger = self._build_logger(pathlib.Path(log_path))

    @staticmethod
    def _build_logger(log_path):
        # One logger per log file path; the rotating handler is attached once.
        # delay=True means the file is not created until something is logged,
        # so merely instantiating the plugin leaves no stray log file.
        logger = logging.getLogger('qbt-filelist:' + str(log_path))
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            try:
                handler = RotatingFileHandler(
                    str(log_path), maxBytes=512 * 1024, backupCount=2,
                    encoding='utf-8', delay=True)
                handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(levelname)s %(message)s'))
                logger.addHandler(handler)
            except Exception:
                # Never let logging setup break the plugin.
                logger.addHandler(logging.NullHandler())
        return logger

    @staticmethod
    def _redact(text, secret):
        text = str(text)
        if secret:
            text = text.replace(secret, '***')
        return text

    def download_torrent(self, info):
        print(download_file(info))

    def search(self, what, cat='all'):
        username, passkey, err = self._load_credentials()
        if err:
            print("FileList: " + err, file=sys.stderr)
            self._logger.error("credentials: %s", err)
            return
        category = self.supported_categories.get(cat, '')
        imdb = self._detect_imdb(what)
        params = urlencode({
            'username': username,
            'passkey': passkey,
            'action': 'search-torrents',
            'type': 'imdb' if imdb else 'name',
            'query': imdb if imdb else unquote(what),
            'category': category,
        })
        try:
            response = retrieve_url("{0}?{1}".format(self.api_url, params))
            data = json.loads(response)
        except Exception as exc:
            safe = self._redact(exc, passkey)
            print("FileList: request failed: {0}".format(safe), file=sys.stderr)
            self._logger.error("request failed for q=%r cat=%s: %s",
                               what, cat, safe)
            return
        if not data:
            self._logger.info("search q=%r cat=%s -> 0 results", what, cat)
            return
        count = 0
        for torrent in data:
            try:
                prettyPrinter(self._build_result(torrent, passkey))
                count += 1
            except Exception as exc:
                row_id = torrent.get('id') if isinstance(torrent, dict) else '?'
                self._logger.warning("skipped malformed row id=%s: %s",
                                     row_id, exc)
        self._logger.info("search q=%r cat=%s -> %d results", what, cat, count)

    def _load_credentials(self):
        parser = configparser.ConfigParser()
        read_ok = parser.read(str(self._config_path))
        if not read_ok or not parser.has_section('filelist'):
            return None, None, \
                "missing/invalid credentials file at {0}".format(self._config_path)
        section = parser['filelist']
        username = section.get('username', '').strip()
        passkey = section.get('passkey', '').strip()
        if (username in self._PLACEHOLDERS) or (passkey in self._PLACEHOLDERS):
            return None, None, \
                "username/passkey not filled in {0}".format(self._config_path)
        return username, passkey, None

    @classmethod
    def _detect_imdb(cls, what):
        match = cls._IMDB_RE.search(unquote(what))
        return match.group(1) if match else None

    @staticmethod
    def _parse_pub_date(value):
        if not value:
            return -1
        try:
            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return int(dt.replace(tzinfo=timezone.utc).timestamp())
        except (ValueError, TypeError):
            return -1

    @staticmethod
    def _format_name(torrent):
        name = torrent.get('name', 'N/A')
        category = torrent.get('category')
        if category:
            name = "[{0}] {1}".format(category, name)
        if torrent.get('freeleech'):
            name += ' [FreeLeech]'
        if torrent.get('doubleup'):
            name += ' [2x]'
        if torrent.get('internal'):
            name += ' [Internal]'
        return name

    def _build_result(self, torrent, passkey):
        tid = torrent.get('id')
        link = torrent.get('download_link') or \
            "{0}/download.php?id={1}&passkey={2}".format(self.url, tid, passkey)
        return {
            'link': link,
            'name': self._format_name(torrent),
            'size': str(torrent.get('size', -1)),
            'seeds': torrent.get('seeders', -1),
            'leech': torrent.get('leechers', -1),
            'engine_url': self.url,
            'desc_link': "{0}/details.php?id={1}".format(self.url, tid),
            'pub_date': self._parse_pub_date(torrent.get('upload_date')),
        }


if __name__ == '__main__':
    # Manual run: python filelist.py <category> <query...>
    engine = filelist()
    category = sys.argv[1] if len(sys.argv) > 1 else 'all'
    query = '+'.join(sys.argv[2:]) if len(sys.argv) > 2 else 'test'
    engine.search(query, category)
