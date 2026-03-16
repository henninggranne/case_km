"""
db.py
-----
SQLite persistence layer for the Go/No-Go vessel weather assessment application.
 
Provides functions to:
    - Create and reset forecast data and statistics tables.
    - Insert individual or bulk forecast entries.
    - Print the full table contents to stdout.
 
Schema (table: data):
    id               INTEGER  Primary key, auto-incremented.
    time             TEXT     Forecast timestamp.
    wave_direction_b REAL     Wave direction relative to vessel bow (degrees).
    wave_height      REAL     Significant wave height (metres).
    go_nogo_status   INT      Operational status: 1 = GO, 0 = NO-GO.
    wave_threshold   REAL     Applied wave height threshold (m) for this timestep.
 
Schema (table: stats):
    id               INTEGER  Primary key, auto-incremented.
    go_hours         INT      Total number of GO timesteps.
    nogo_hours       INT      Total number of NO-GO timesteps.
    go_streak        INT      Longest consecutive GO period (timesteps).
    max_wave_height  REAL     Maximum wave height across the full timeseries (m).
"""

import sqlite3
import numpy as np

def create_data_table(name: str) -> None:
    """
    Create the 'data' table in the specified SQLite database if it does not exist.
 
    Args:
        name: Base name of the database file (without .db extension).
    """

    con = sqlite3.connect(f"{name}.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT NOT NULL, 
    wave_direction_b REAL, 
    wave_height REAL,
    go_nogo_status INT,
    wave_threshold REAL
    )
    """)
    con.commit()
    con.close()


def create_statistics_table(name: str) -> None:
    """
    Create the 'stats' table in the specified SQLite database if it does not exist.
 
    Args:
        name: Base name of the database file (without .db extension).
    """

    con = sqlite3.connect(f"{name}.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    go_hours INT,
    nogo_hours INT,
    go_streak INT,
    max_wave_height REAL
    )
    """)
    con.commit()
    con.close()

def reset_tables(name: str) -> None:
    """
    Drop all tables, clearing all existing data.
    Called at the start of each run to ensure a fresh dataset.
    """
    con = sqlite3.connect(f"{name}.db")
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS data")
    cur.execute("DROP TABLE IF EXISTS stats")
    con.commit()
    con.close()


def insert_entry_data_table(name: str, time: str, data: np.ndarray, go_nogo_status: int, wave_threshold: float, con: sqlite3.Connection | None = None) -> None:
    """
    Insert a single forecast timestep into the 'data' table.
 
    Args:
        name:           Base name of the target database file (without .db extension).
        time:           Timestamp string for this timestep.
        data:           Numpy array with two elements: [wave_direction_b, wave_height].
                        Typically a column slice from the (2, N) numpy data array.
        go_nogo_status: Operational status for this timestep (1 = GO, 0 = NO-GO).
        wave_threshold: Applied wave height threshold (m) for this timestep.
        con:            Optional existing database connection. If provided, the caller
                        is responsible for committing and closing. If None, a new
                        connection is opened and closed automatically.
    """

    own_connection = con is None
    if own_connection:
        con = sqlite3.connect(f"{name}.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO data (time, wave_direction_b, wave_height, go_nogo_status, wave_threshold) VALUES (?, ?, ?, ?, ?)",
        (time, data[0], data[1], go_nogo_status, wave_threshold)
    )
    if own_connection:
        con.commit()
        con.close()

def insert_full_data_table(name: str, time: list, data: np.ndarray, go_nogo_status: list, wave_threshold: list) -> None:
    """
    Insert all forecast timesteps into the 'data' table in a single batch operation.
 
    Iterates over each timestep, pairing the timestamp, data column, and
    Go/No-Go status value, delegating each row to insert_entry_data_table.
    A single shared connection is opened for the full batch and committed
    once all rows are inserted, ensuring atomicity.
 
    Args:
        name:           Base name of the target database file (without .db extension).
        time:           List of timestamp strings, length N.
        data:           Numpy array of shape (2, N): [wave_directions, wave_heights].
        go_nogo_status: List of length N with GO (1) / NO-GO (0) values.
        wave_threshold: List of length N with applied wave height thresholds (m).
    """

    con = sqlite3.connect(f"{name}.db")
    n_timesteps = len(go_nogo_status)

    for i in range(n_timesteps):
        insert_entry_data_table(name, time[i], data[:,i], go_nogo_status[i], wave_threshold[i], con=con)

    con.commit()
    con.close()


def insert_statistics_table(name: str, go_hours: int, nogo_hours: int, go_streak: int, max_wave_height: float) -> None:
    """
    Insert a single row of summary statistics into the 'stats' table.
 
    Args:
        name:            Base name of the target database file (without .db extension).
        go_hours:        Total number of GO timesteps.
        nogo_hours:      Total number of NO-GO timesteps.
        go_streak:       Longest consecutive GO period (hours).
        max_wave_height: Maximum wave height across the full timeseries (m).
    """

    con = sqlite3.connect(f"{name}.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO stats (go_hours, nogo_hours, go_streak, max_wave_height) VALUES (?, ?, ?, ?)",
        (go_hours, nogo_hours, go_streak, max_wave_height)
    )
    con.commit()
    con.close()



def print_table(name: str) -> None:
    """
    Fetch and print all rows from the 'data' table to stdout.
 
    Intended for quick inspection during development and debugging.
    Each row is printed as a tuple: (id, time, wave_direction_b, wave_height, go_nogo_status).
 
    Args:
        name: Base name of the database file (without .db extension).
    """

    conn = sqlite3.connect(f"{name}.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM data")

    rows = cur.fetchall()

    for row in rows:
        print(row)

    conn.close()
