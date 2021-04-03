class Config:
    base_url = "https://www.transfermarkt.com"

    league_urls = [
        "/1-bundesliga/startseite/wettbewerb/L1",
        "/premier-league/startseite/wettbewerb/GB1",
        "/primera-division/startseite/wettbewerb/ES1",
        "/serie-a/startseite/wettbewerb/IT1",
        "/ligue-1/startseite/wettbewerb/FR1",
    ]

    season_suffix_url = "/plus/?saison_id={}"

    team_detailed_suffix_url = "/plus/1"
