import sqlite3
import pandas as pd
from config import Config

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input


db = sqlite3.connect(Config.db_filename)
df = pd.read_sql_query("SELECT * FROM ratio_foreigner_players", db)
df1 = df.loc[df["league"] == "serie-a"]
df2 = df.loc[df["league"] == "1-bundesliga"]
leagues = df["league"].unique()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='leaguefilter',
                options=[
                    {'label': league, 'value': league} for league in leagues
                ], value='serie-a'
            ),
		], style={'width': '49%', 'display': 'inline-block'}),
    ]),
    html.Div([
        dcc.Graph(
            id="foreigners-chart", config={"displayModeBar": False},
        )], className="card",
    )
])


@app.callback(
    Output("foreigners-chart", "figure"),
    Input("leaguefilter", "value"),
)
def update_chart(league):
    filtered_df = df.loc[df["league"] == league, :]
    foreigners_chart_figure = {
        "data": [{
            "x": filtered_df["season"],
            "y": filtered_df["ratio_foreigners"],
            "type": "lines",
        }], "layout": {"title": f"Percentage foreign players for {league}"}
    }

    return foreigners_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)
