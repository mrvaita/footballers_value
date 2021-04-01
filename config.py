class Config:
    base_url = "https://www.transfermarkt.com"

    league_urls = [
        "/1-bundesliga/startseite/wettbewerb/L1",
        "/premier-league/startseite/wettbewerb/GB1",
        "/premier-league/startseite/wettbewerb/GB1",
        "/serie-a/startseite/wettbewerb/IT1",
        "/ligue-1/startseite/wettbewerb/FR1",
    ]

    season_suffix_url = "/plus/?saison_id={}"

    serie_a_teams = [
		'/inter-mailand/startseite/verein/46/saison_id/2020',
        '/ac-mailand/startseite/verein/5/saison_id/2020',
        '/atalanta-bergamo/startseite/verein/800/saison_id/2020',
        '/us-sassuolo/startseite/verein/6574/saison_id/2020',
        '/cagliari-calcio/startseite/verein/1390/saison_id/2020',
        '/hellas-verona/startseite/verein/276/saison_id/2020',
        '/fc-bologna/startseite/verein/1025/saison_id/2020',
        '/sampdoria-genua/startseite/verein/1038/saison_id/2020',
        '/spezia-calcio/startseite/verein/3522/saison_id/2020',
        '/fc-crotone/startseite/verein/4083/saison_id/2020',
        '/juventus-turin/startseite/verein/506/saison_id/2020',
        '/ssc-neapel/startseite/verein/6195/saison_id/2020',
        '/as-rom/startseite/verein/12/saison_id/2020',
        '/lazio-rom/startseite/verein/398/saison_id/2020',
        '/ac-florenz/startseite/verein/430/saison_id/2020',
        '/fc-turin/startseite/verein/416/saison_id/2020',
        '/udinese-calcio/startseite/verein/410/saison_id/2020',
        '/parma-calcio-1913/startseite/verein/130/saison_id/2020',
        '/genua-cfc/startseite/verein/252/saison_id/2020',
        '/benevento-calcio/startseite/verein/4171/saison_id/2020',
    ]

    team_detailed_suffix_url = "/plus/1"
