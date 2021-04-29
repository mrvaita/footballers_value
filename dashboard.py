import sqlite3
import pandas as pd
from config import Config

import dash
import dash_core_components as dcc
import dash_html_components as html


db = sqlite3.connect(Config.db_filename)
df = pd.read_sql_query("SELECT * FROM ratio_foreigner_players", db)
df1 = df.loc[df["league"] == "serie-a"]
df2 = df.loc[df["league"] == "1-bundesliga"]
print(df.head())

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children="Football player analytics",),
        html.P(
            children="Analyse football players for the top five european"
            " football competitions between 1970 and 2021",
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": df1["season"],
                        "y": df1["ratio_foreigners"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "ratio foreigner players for serie a"},
            },
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": df2["season"],
                        "y": df2["ratio_foreigners"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "ratio foreigner players for first bundesliga"},
            },
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
