import json
import os
import unittest
from bs4 import BeautifulSoup
from transfermarkt.utils import *
from transfermarkt.db_utils import *
from transfermarkt.scrape_transfermarkt import *


TESTDATA_ROOT = os.path.join(os.path.dirname(__file__), 'resources/')


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.testfile = open(os.path.join(TESTDATA_ROOT, "handa.html"))
        self.testdata = BeautifulSoup(self.testfile.read(), "html.parser")

    def tearDown(self):
        self.testfile.close()

    def test_convert_market_value(self):
        assert convert_market_value("€1.50m") == 1.5
        assert convert_market_value("€500Th.") == 0.5
        assert convert_market_value("-") == None

    def test_extract_date(self):
        assert extract_date("Jan 01, 1995 (28)") == "1995-01-01"
        assert extract_date("-") == None

    def test_extract_age(self):
        assert extract_age("Jan 01, 1995 (28)") == 28
        assert extract_age("-") == None

    def test_extract_nationality(self):
        assert extract_nationality(self.testdata) == "Slovenia"

    def test_extract_nation_flag_url(self):
        assert extract_nation_flag_url(self.testdata) == "https://tmssl.akamaized.net/images/flagge/verysmall/155.png?lm=1520611569"

    def test_convert_date(self):
        assert convert_date("Jan 01, 2021") == "2021-01-01"
        assert convert_date(None) == None
        assert convert_date("-") == None

    def test_format_height(self):
        assert format_height("1,56 m") == 156
        assert format_height("1,8 m") == 180
        assert format_height("-") == None


class TestDbUtils(unittest.TestCase):

    def setUp(self):
        self.insertqueryfile = open(os.path.join(TESTDATA_ROOT, "handa.sql"))
        self.testfile = open(os.path.join(TESTDATA_ROOT, "handa_extracted.json"))
        self.insertquery = self.insertqueryfile.read()
        self.testdata = json.load(self.testfile)

    def tearDown(self):
        self.insertqueryfile.close()
        self.testfile.close()

    def test_create_insert_query(self):
        assert create_insert_query([self.testdata], 2020) == self.insertquery
        assert create_insert_query([], 2020) == "--"

    def test_read_query_file(self):
        assert read_query_file("resources/handa.sql") == self.insertquery

    def test_sql_quote(self):
        assert sql_quote(None) == "NULL"
        assert sql_quote("a") == "'a'"
        assert sql_quote(35) == "'35'"
        assert sql_quote(3.2) == "'3.2'"


class ScrapeTransfermarkt(unittest.TestCase):

    def setUp(self):
        self.testfile = open(os.path.join(TESTDATA_ROOT, "handa_extracted.json"))
        self.testdata = json.load(self.testfile)
        self.testdata.pop("updated_on")

    def tearDown(self):
        self.testfile.close()

    def test_get_season_urls(self):
        assert get_season_urls(2020) == \
            ['https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1/plus/?saison_id=2020',
             'https://www.transfermarkt.com/1-bundesliga/startseite/wettbewerb/L1/plus/?saison_id=2020',
             'https://www.transfermarkt.com/primera-division/startseite/wettbewerb/ES1/plus/?saison_id=2020',
             'https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1/plus/?saison_id=2020',
             'https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1/plus/?saison_id=2020']
        assert get_season_urls(1970) == \
            ['https://www.transfermarkt.com/1-bundesliga/startseite/wettbewerb/L1/plus/?saison_id=1970',
             'https://www.transfermarkt.com/primera-division/startseite/wettbewerb/ES1/plus/?saison_id=1970',
             'https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1/plus/?saison_id=1970',
             'https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1/plus/?saison_id=1970']

    def test_get_teams_urls(self):
        assert sorted(get_teams_urls('https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1/plus/?saison_id=2020')) == \
            sorted([
                ('https://www.transfermarkt.com/inter-mailand/kader/verein/46/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/ac-mailand/kader/verein/5/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/atalanta-bergamo/kader/verein/800/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/us-sassuolo/kader/verein/6574/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/cagliari-calcio/kader/verein/1390/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/hellas-verona/kader/verein/276/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/fc-bologna/kader/verein/1025/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/sampdoria-genua/kader/verein/1038/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/spezia-calcio/kader/verein/3522/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/fc-crotone/kader/verein/4083/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/juventus-turin/kader/verein/506/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/ssc-neapel/kader/verein/6195/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/as-rom/kader/verein/12/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/lazio-rom/kader/verein/398/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/ac-florenz/kader/verein/430/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/fc-turin/kader/verein/416/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/udinese-calcio/kader/verein/410/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/parma-calcio-1913/kader/verein/130/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/genua-cfc/kader/verein/252/saison_id/2020/plus/1', 'serie-a'),
                ('https://www.transfermarkt.com/benevento-calcio/kader/verein/4171/saison_id/2020/plus/1', 'serie-a')]
            )

    def test_get_players_data(self):
        handa = get_players_data(('https://www.transfermarkt.com/inter-mailand/kader/verein/46/saison_id/2020/plus/1', 'serie-a'))[0]
        handa.pop("updated_on")
        assert handa == self.testdata
