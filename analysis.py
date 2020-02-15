import re
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

patterns = {
    'LC_MAIN': '.*LC_MAIN.*',
    'LC1': '.*LC1.*',
    'LC2': '.*LC2.*',
    'LC3': '.*LC3.*',
    'PT_COMB': '.*PT_COMB.*',
    'PT_INJE': '.*PT_INJE.*',
    'PT_FEED': '.*PT_FEED.*',
    'TC1': '.*TC1.*',
    'TC2': '.*TC2.*',
    'TC3': '.*TC3.*'
}

def match_calibration_and_file(calibrations: list, filename: str) -> str:

    for pattern in patterns:
        r = re.compile(pattern)

        for calibration in calibrations:

            if r.match(filename) != None and r.match(calibration) != None:
                return calibration

    return None

def match_name_and_file(filename: str) -> str:

    for pattern in patterns:
        r = re.compile(pattern)

        if r.match(filename) != None:
            return pattern

    return None


def locate_ignition(df) -> list:
    """
    Locates the ignition timestamp range, given the sequence of
    main loadcell information. This range will be used as a base for
    other sensor information. If there are multiple ignitions in a single
    log file, then this will locate the latest instance.
    """
    
    # Selecting data where the reading is close to maximum.
    max_reading = df[2].max()
    df_sub = df[df[2] >= max_reading - max_reading / 2]

    # Selecting time frames.
    first = df_sub.iloc[0][0]
    last = df_sub.iloc[-1][0]

    # Finding difference
    diff = last - first

    if first - diff / 2 < 0:
        print("Not enough data points to analyze. Please make sure that the log is at least twice as long as the burn time.")
        exit()

    return [first, last, first - diff / 2, last + diff / 2]

def plot_graph(sources, source, timeframes):

    # Load data and select range.
    df = pd.read_csv(sources[source], header=None, delim_whitespace=True)
    df = df[(df[0] >= timeframes[2]) & (df[0] <= timeframes[3])]

    # Label time frames.
    first = timeframes[0]
    last = timeframes[1]
    
    start = timeframes[2]
    end = timeframes[3]

    diff = timeframes[1] - timeframes[0]

    # If we are analyzing LC_MAIN, then add zero offset to values.
    if source == "LC_MAIN":
        zerooffset = df[(df[0] >= start) & (df[0] <= start + diff / 4)][2].mean()
        df[2] = df[2] + abs(zerooffset)

    # Rearrange timestamps.
    df[0] = (df[0] - start) / 1000000
    
    # Perform filtering.
    df[3] = df[2].rolling(window=20,center=False).median()

    # Set unit
    unit = "N/A"

    if source.find("LC") >= 0:
        unit = "LBS"
    elif source.find("PT") >= 0:
        unit = "PSI"
    elif source.find("TC") >= 0:
        unit = "°C"

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df[0], y=df[2],
                        mode='lines',
                        name='Raw'))

    fig.add_trace(go.Scatter(x=df[0], y=df[3],
                        mode='lines',
                        name='Denoised'))

    fig.update_layout(title=source,
                    xaxis_title='Time (s)',
                    yaxis_title=unit)

    fig.show()