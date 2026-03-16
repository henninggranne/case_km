import numpy as np
from go_nogo_app.case import fetch_statistics

def test_fetch_go_nogo_stats_all_go():
    go_nogo_list = [1, 1, 1, 1]
    wave_height_list = np.array([0, 0, 0, 0])
    go_hr, nogo_hr, go_streak, _ = fetch_statistics(go_nogo_list, wave_height_list)
    assert go_hr == 4
    assert nogo_hr == 0
    assert go_streak == 4

def test_fetch_go_nogo_stats_all_nogo():
    go_nogo_list = [0, 0, 0, 0]
    wave_height_list = np.array([0, 0, 0, 0])
    go_hr, nogo_hr, go_streak, _ = fetch_statistics(go_nogo_list, wave_height_list)
    assert go_hr == 0
    assert nogo_hr == 4
    assert go_streak == 0

def test_fetch_go_nogo_stats_mixed1():
    go_nogo_list = [1, 0, 1, 0]
    wave_height_list = np.array([0, 0, 0, 0])
    go_hr, nogo_hr, go_streak, _ = fetch_statistics(go_nogo_list, wave_height_list)
    assert go_hr == 2
    assert nogo_hr == 2
    assert go_streak == 1

def test_fetch_go_nogo_stats_mixed2():
    go_nogo_list = [0, 1, 0, 1]
    wave_height_list = np.array([0, 0, 0, 0])
    go_hr, nogo_hr, go_streak, _ = fetch_statistics(go_nogo_list, wave_height_list)
    assert go_hr == 2
    assert nogo_hr == 2
    assert go_streak == 1

def test_fetch_go_nogo_stats_mixed3():
    go_nogo_list = [1, 1, 0, 0]
    wave_height_list = np.array([0, 0, 0, 0])
    go_hr, nogo_hr, go_streak, _ = fetch_statistics(go_nogo_list, wave_height_list)
    assert go_hr == 2
    assert nogo_hr == 2
    assert go_streak == 2

def test_fetch_go_nogo_stats_mixed4():
    go_nogo_list = [0, 0, 1, 1]
    wave_height_list = np.array([0, 0, 0, 0])
    go_hr, nogo_hr, go_streak, _ = fetch_statistics(go_nogo_list, wave_height_list)
    assert go_hr == 2
    assert nogo_hr == 2
    assert go_streak == 2