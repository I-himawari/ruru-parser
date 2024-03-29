from ..ruru_parser import ruru_parser
import unittest
import pytest


class test_ruru_parserのurl取得テスト(unittest.TestCase):

    def setUp(self):
        self.parse_result = ruru_parser(url='https://ruru-jinro.net/log5/log419460.html')

    def test_metaテスト(self):
        """metaの出力結果を返す"""
        meta = self.parse_result['meta']
        assert meta['villagers_name'] == '17A普通'
        assert meta['villagers_number'] == '17'
        assert meta['role_pattern'] == 'A'
        assert meta['timestamp'] == 1494763375
        assert meta['victory'] == 'wolf'

    def test_playerの出力テスト(self):
        """playerの出力結果を返す"""
        player = self.parse_result['player']
        assert len(player) == 17


class test_ruru_parserの廃村取得(unittest.TestCase):

    def setUp(self):
        self.parse_result = ruru_parser(url='https://ruru-jinro.net/log5/log426926.html')

    def test_metaテスト(self):
        """metaの出力結果を返す"""
        meta = self.parse_result['meta']
        assert meta['victory'] == 'del'
