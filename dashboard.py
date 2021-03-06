"""Dashboard to visualize football players data.

This script allows the visualization of some data about football players
performing in the five most important european football competitions (Serie A,
1-Bundesliga, Premier League, La Liga and League 1).
Two visualisations compose the dashboard. The first one shows how the number of
foreign players (expressed in percentage) performing in each league changes
1970 until today.
The second visualisation shows how average age, height and value of the players
groupd by role change from 1970 until today.
"""

import sqlite3
import pandas as pd
from config import Config

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input

from flask import Flask, request, abort, redirect
import git
import hashlib
import hmac
import os


db = sqlite3.connect(Config.db_filename)
df_foreigners = pd.read_sql_query("SELECT * FROM ratio_foreigner_players", db)
df_averages = pd.read_sql_query("SELECT * FROM avg_players", db)
leagues = df_foreigners["league"].unique()
roles = df_averages["role"].unique()
avgs = [col for col in df_averages.columns if "avg_" in col]

server = Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname="/dashboard/")

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
    """This callback recalculate the visualisation after parameter selection in
    the corresponding dropdown menu associated to the graph.

    Args:
    league str: The league name.

    Returns:
    the recalculated DASH chart
    """

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
    """This callback recalculate the visualisation after parameter selection in
    the corresponding dropdown menu associated to the graph.

    Args:
    league str: The league name.
    role str: The football role of interest.
    avg str: The average parameter of interest.

    Returns:
    the recalculated DASH chart
    """

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
        }], "layout": {
                "title": f"Average {role} player {avg[4:]} for {league}"
            }
    }

    return avg_chart_figure


@server.route("/")
def render_dashboard():
    return redirect("/dashboard")


# -------------------------- Github Webhook --------------------------

@server.route("/update_server", methods=["POST"])
def webhook():
    """A github webhook pushes a payload to this route once changes are made to
    the remote repo. The request is first validated and only afterwards the
    changes are pulled from the main branch.

    Returns:
    str: a message to the client that performed the request.
    """

    if request.method == "POST":

        # Validate request
        abort_code = 418
        x_hub_signature = request.headers.get("X-Hub-Signature")
        if not is_valid_signature(x_hub_signature, request.data):
            print(f"Deploy signature failed: {x_hub_signature}")
            abort(abort_code)

        # Pull changes from main branch
        repo = git.Repo("/home/pi/Documents/git-repos/footballers_value")
        origin = repo.remotes.origin
        origin.pull()

        return "Server updated successfully!!", 200
    else:
        return "Wrong event type!", 400


def is_valid_signature(
        x_hub_signature, data, private_key=os.getenv("SECRET_KEY")):
    """Verify webhook signature.

    Args:
    x_hub_signature str: the signature and the hash algorithm from the Github
        Webhook.
    data str: the data from the request.
    private_key str: the local secret key.

    Returns:
    boolean: True if signature is valid and False otherwise.
    """
    hash_algorithm, github_signature = x_hub_signature.split("=", 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, "latin-1")
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)

    return hmac.compare_digest(mac.hexdigest(), github_signature)
