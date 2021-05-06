import sqlite3
import pandas as pd
from config import Config

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input


db = sqlite3.connect(Config.db_filename)
df_foreigners = pd.read_sql_query("SELECT * FROM ratio_foreigner_players", db)
df_averages = pd.read_sql_query("SELECT * FROM avg_players", db)
leagues = df_foreigners["league"].unique()
roles = df_averages["role"].unique()
avgs = [col for col in df_averages.columns if "avg_" in col]

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
    ),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='leaguefilter2',
                options=[
                    {'label': league, 'value': league} for league in leagues
                ], value='serie-a'
            ),
		], style={'width': '33%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id="rolefilter",
                options=[
                    {"label": role, "value": role} for role in roles
                ], value="Goalkeeper"
            ),
		], style={"width": "33%", "display": "inline-block"}),
        html.Div([
            dcc.Dropdown(
                id="avgfilter",
                options=[
                    {"label": avg, "value": avg} for avg in avgs
                ], value="avg_height"
            ),
		], style={"width": "33%", "display": "inline-block"}),
    ]),
    html.Div([
        dcc.Graph(
            id="averages-chart", config={"displayModeBar": False},
        )], className="card",
    ),
])


@app.callback(
    Output("foreigners-chart", "figure"),
    Input("leaguefilter", "value"),
)
def update_chart(league):
    filtered_df = df_foreigners.loc[df_foreigners["league"] == league, :]
    foreigners_chart_figure = {
        "data": [{
            "x": filtered_df["season"],
            "y": filtered_df["ratio_foreigners"],
            "type": "lines",
        }], "layout": {"title": f"Percentage foreign players for {league}"}
    }

    return foreigners_chart_figure


@app.callback(
    Output("averages-chart", "figure"),
    Input("leaguefilter2", "value"),
    Input("rolefilter", "value"),
    Input("avgfilter", "value")
)
def update_avg_chart(league, role, avg):
    df_mask = (
        (df_averages["league"] == league) &
        (df_averages["role"] == role)
    )
    filtered_df = df_averages.loc[df_mask, :]

    avg_chart_figure = {
        "data": [{
            "x": filtered_df["season"],
            "y": filtered_df[avg],
            "type": "lines",
        }], "layout": {"title": f"Average {role} player {avg[4:]} for {league}"}
    }

    return avg_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)
