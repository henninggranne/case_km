"""
export.py
---------
Handles all data export functionality for the Go/No-Go vessel weather assessment application.

Responsibilities:
    - Querying processed data and statistics from the SQLite database.
    - Exporting forecast data to JSON for frontend table rendering.
    - Generating interactive Plotly figures and exporting them as JSON.
    - Exporting summary statistics to JSON for frontend display.
"""

import sqlite3
import json
import plotly.graph_objects as go

def export_to_json(name: str, filepath: str = "static/data.json") -> None:
    """
    Exports all results from the created database to JSON format for frontend.

    Args:
        name:     Base name of the database file (without .db extension).
        filepath: Output path for the JSON file.
    """

    con = sqlite3.connect(f"{name}.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM data")

    rows = cur.fetchall()
    
    data = [
        {
            "id": row[0],
            "time": row[1],
            "wave_direction_b": row[2],
            "wave_height": row[3],
            "go_nogo_status": row[4]
        }
        for row in rows
    ]
    with open(filepath, "w") as f:
        json.dump(data, f)


def export_plot_json(name: str, filepath: str = "../static/plot.json") -> None:
    """
    Generate an interactive Plotly figure and export it as JSON for frontend rendering.
 
    Produces three traces:
        - Wave Height:       Significant wave height over time.
        - GO/NO-GO:          Operational status (1 = GO, 0 = NO-GO) over time.
        - Wave Height Limit: The applicable threshold at each timestep.
 
    Args:
        name:     Base name of the database file (without .db extension).
        filepath: Output path for the JSON file. Defaults to static/plot.json.
    """

    con = sqlite3.connect(f"{name}.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM data")

    rows = cur.fetchall()

    time = [row[1] for row in rows]
    waveheight = [row[3] for row in rows]
    go_nogo = [row[4] for row in rows]
    wave_threshold = [row[5] for row in rows]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time,
        y=waveheight,
        name="Wave Height (m)",
        showlegend=True,
    ))
    fig.add_trace(go.Scatter(
        x=time,
        y=go_nogo,
        name="GO/NO-GO",
        showlegend=True
    ))
    fig.add_trace(go.Scatter(
        x=time,
        y=wave_threshold,
        name="Wave Height Limit (m)",
        showlegend=True
    ))

    with open(filepath, "w") as f:
        f.write(fig.to_json())


def export_statistics_json(name: str, filepath: str = "../static/stats.json") -> None:
    """
    Export summary statistics from the 'stats' table to a JSON file for frontend consumption.
 
    Args:
        name:     Base name of the database file (without .db extension).
        filepath: Output path for the JSON file. Defaults to static/stats.json.
    """
    
    con = sqlite3.connect(f"{name}.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM stats")

    rows = cur.fetchall()

    stats = [
        {
            "id": row[0],
            "go_hours": row[1],
            "nogo_hours": row[2],
            "go_streak": row[3],
            "max_wave_height": row[4]
        }
        for row in rows
    ]
    
    with open(filepath, "w") as f:
        json.dump(stats, f)
