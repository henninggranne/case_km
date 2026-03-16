"""
case.py
-------
Handles all oceanographic data retrieval and Go/No-Go decision logic.
 
Responsibilities:
    - Fetching raw forecast JSON from the MET Oceanforecast API.
    - Parsing the JSON response into a structured numpy array.
    - Evaluating Go/No-Go operational status based on wave height and direction
      relative to the vessel heading.
    - Computing summary statistics over the full forecast timeseries.
"""

import numpy as np
import requests


def fetch_json(lat: float, lon: float, your_email: str = "granne.97gmail.com") -> dict:

    """
    Fetch oceanographic forecast data from the MET Oceanforecast API (v2.0).
 
    The MET API requires a User-Agent header identifying the application and a
    contact email. Requests without it will receive a 403 response.
    See: https://api.met.no/doc/FAQ
 
    Args:
        lat:        Latitude of the target position (decimal degrees).
        lon:        Longitude of the target position (decimal degrees).
        your_email: Contact email included in the User-Agent header.
 
    Returns:
        A dict containing the full parsed JSON response on success.
        A descriptive error string if the request fails.
    """
 
    url_api = f"https://api.met.no/weatherapi/oceanforecast/2.0/complete?lat={str(lat)}&lon={str(lon)}"

    # A header with User-Agent is needed to avoid getting a 403 (failure) response. For info see: https://api.met.no/doc/FAQ
    your_email = "granne.97@gmail.com"
    headers = {"User-Agent": f"case_km/1.0 {your_email}"}

    response = requests.get(url_api, headers= headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403:
        returnstring = "Did you remember to add a User-Agent?"
        return returnstring
    else:
        return (
            f"Something else went wrong. "
            f"Please see the relevant response: {response.status_code} in the API documentation"
        )


def fetch_data_from_json(json_data: dict) -> tuple[list, np.ndarray]:

    """
    Extract relevant forecast fields from the MET API JSON response.

    Iterates over each timestep in the timeseries and collects:
        - Forecast timestamp
        - Sea surface wave from direction (degrees)
        - Sea surface wave height (metres)

    Args:
        json_data: Parsed JSON dict as returned by fetch_json().

    Returns:
        A tuple of:
            - time_list: list of timestamp strings, length N.
            - data:      numpy array of shape (2, N) where N is the number of timesteps:
                            Row 0: wave_direction_i 
                            Row 1: wave_height
    """

    timeseries = json_data["properties"]["timeseries"]

    time_list = []
    wave_direction_i_list = []
    wave_height_list = []

    for instance in timeseries:
        time = instance["time"]
        wave_direction_i = instance["data"]["instant"]["details"]["sea_surface_wave_from_direction"]
        wave_height = instance["data"]["instant"]["details"]["sea_surface_wave_height"]

        time_list.append(time)
        wave_direction_i_list.append(wave_direction_i)
        wave_height_list.append(wave_height)

    return_data = [time_list, wave_direction_i_list, wave_height_list]
    return_data = np.array(return_data)
    return time_list, np.array([wave_direction_i_list, wave_height_list])


def fetch_go_nogo_status(data: np.ndarray, vessel_heading: float) -> tuple[list, list]:
    """
    Evaluate the GoO (1) / NO-GO (0) operational status for each forecast timestep.
 
    Decision logic is based on the relative wave direction with respect to the
    vessel heading and a wave-height threshold that varies by exposure angle:
 
        Beam seas  (wave_direction_b in 30–150° or 210–330°): threshold = 2.5 m
        Bow / stern seas (all other angles):                   threshold = 3.5 m
 
    Args:
        data:            Numpy array of shape (2, N) as returned by fetch_data_from_json().
                         Rows: [wave_direction_i, wave_height]
        vessel_heading:  Vessel heading in degrees (0–360, clockwise from north).
 
    Returns:
        A tuple of two lists, each of length N:
            - wave_threshold_list: Applied wave height threshold (m) for each timestep.
            - go_nogo_list:        Operational status, 1 = GO, 0 = NO-GO.
    """

    go_nogo_list = []
    wave_threshold_list = []

    # Transpose to iterate row-wise over timesteps: each row = [direction, height]
    for instance in data.T:
        wave_direction_i = float(instance[0])   # Direction from north
        wave_height = float(instance[1])        # Significant wave height

        # Compute wave direction relative to vessel's bow
        wave_direction_b = wave_direction_i - vessel_heading
        if wave_direction_b < 0:
            wave_direction_b += 360

        # Beam sea condition: waves arriving from the side (port or starboard)
        is_beam_sea = (
            (30 < wave_direction_b < 150) or
            (210 < wave_direction_b < 330)
        )

        # Apply stricter threshold for beam seas, more lenient for bow/stern
        wave_threshold = 2.5 if is_beam_sea else 3.5
        go_nogo_list.append(0 if wave_height > wave_threshold else 1)
        wave_threshold_list.append(wave_threshold)

    return wave_threshold_list, go_nogo_list


def fetch_statistics(go_nogo_list: list, wave_height_list: np.ndarray) -> tuple[int, int, int, float]:
    """
    Compute summary statistics over the full forecast timeseries.
 
    Args:
        go_nogo_list:     List of GO (1) / NO-GO (0) values, length N.
        wave_height_list: Numpy array of significant wave heights (m), length N.
 
    Returns:
        A tuple of:
            - go:                Total number of GO timesteps.
            - nogo:              Total number of NO-GO timesteps.
            - highest_go_streak: Length of the longest consecutive GO period.
            - max_wave_height:   Maximum wave height across the full timeseries (m).
    """

    go = 0
    nogo = 0
    go_streak = 0
    highest_go_streak = 0
    for i, go_nogo in enumerate(go_nogo_list):
        if go_nogo == 1:
            go += 1
            
            if i == 0:
                go_streak = 1
            if i > 0 and go_nogo_list[i-1] != 1:
                go_streak = 1
            elif i > 0 and go_nogo_list[i-1] == 1:
                go_streak += 1
        else:
            nogo += 1
            go_streak = 0
        if go_streak > highest_go_streak:
            highest_go_streak = go_streak

    max_wave_height = float(max(wave_height_list))
        
    return go, nogo, highest_go_streak, max_wave_height
