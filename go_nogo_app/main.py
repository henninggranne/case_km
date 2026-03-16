"""
main.py
-------
Entry point for the GO / NO-GO vessel weather assessment application.
 
Workflow:
    1. Define vessel position and heading.
    2. Fetch oceanographic forecast data from the MET API.
    3. Parse the raw JSON into a structured numpy array.
    4. Evaluate GO / NO-GO status for each forecast timestep.
    5. Persist results to a local SQLite database.
    6. Export results to static HTML: http://127.0.0.1:5500/static/index.html
"""
 
from go_nogo_app.case import fetch_data_from_json, fetch_json, fetch_go_nogo_status, fetch_statistics
from go_nogo_app.db import create_data_table, create_statistics_table, insert_full_data_table, insert_statistics_table, print_table, reset_tables
from go_nogo_app.export import export_plot_json, export_statistics_json, export_to_json
import os


def main():
    """
    Orchestrates the full data pipeline:
    fetch -> parse -> evaluate -> store -> export.
    """
    
    # Ensure all output paths are relative to this file, not the working directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

     # --- Input parameters ---
    lat = 65.31            # Latitude of the vessel position (decimal degrees)
    lon = 7.34             # Longitude of the vessel position (decimal degrees)
    vessel_heading = 180   # Vessel heading in degrees (0–360, clockwise from north)

    # Possible other test place
    # lat = 57.435198
    # lon = 6.980868

    # --- Data retrieval ---
    # Fetch raw JSON forecast from the MET Oceanforecast API
    raw_json = fetch_json(lat, lon)
 
    # Extract relevant fields (time, wave direction, wave height) into a numpy array
    time, data = fetch_data_from_json(raw_json)
 
    # Compute GO (1) / NO-GO (0) status and applied threshold for each timestep based on wave conditions
    wave_threshold, go_nogo = fetch_go_nogo_status(data, vessel_heading)

    # Compute summary statistics over the full timeseries
    wave_heights = data[1, :]
    go, nogo, highest_go_streak, max_wave_height = fetch_statistics(go_nogo, wave_heights)

    # --- Persistence ---
    database_name = "datapoints"
    reset_tables(database_name)
    create_data_table(database_name)                                              # Create data table if it does not exist
    create_statistics_table(database_name)                                        # Create statistics table if it does not exist
    insert_full_data_table(database_name, time, data, go_nogo, wave_threshold)    # Insert all timesteps into the DB
    insert_statistics_table(database_name, go, nogo, highest_go_streak, max_wave_height)  # Insert statistics in table
    #print_table(database_name)

    # --- Export for static HTML frontend ---
    export_plot_json(database_name)
    export_statistics_json(database_name)


if __name__ == "__main__":
    main()