import sys
import os
import tempfile

import commandline
import fileio
import analysis

import pandas as pd

# ==============================================
# Validate the command line arguments.
# ==============================================
settings = commandline.read_commandline_arguments()


# ==============================================
# Load all the sensor information from the --src
# directory.
# ==============================================
source_logs = fileio.locate_logs(settings["--src"])


# ==============================================
# If the script is reading data from RESFET,
# then we need to decode the log data. After the
# decoding is done, we also need to calibrate
# using RESFET Dashboard config.
# ==============================================

if settings["--type"] == "dashboard":
    print("Using 'dashboard' logs. Skipping decoding and calibration...\n")
    pass
elif settings["--type"] == "resfet":
    print("Using 'resfet' logs. Performing decoding and calibration...\n")
    # Create a temporary directory to store decoded logs.
    tempdir = tempfile.TemporaryDirectory()

    calibrations = fileio.read_config(settings["--config"])
    source_logs = fileio.decode_calibrate_logs(source_logs, calibrations, tempdir.name)

else:
    print("Wrong --type entered. This program only accepts 'dashboard' and 'resfet' as arguments for --type.")
    exit()


# ==============================================
# Perform data analysis.
# ==============================================

sources = {}
for source in source_logs:
    file_head, file_tail = os.path.split(source)
    pattern_name = analysis.match_name_and_file(file_tail)
    sources[pattern_name] = source

    if not sources[pattern_name]:
        print("Failed to identify '%s'. Verify that this log file matches with a sensor output." % source)
        exit()
    
    print("Identified '%s' as SOURCE: '%s'..." % (file_tail, pattern_name))

print("\nAll incoming log file(s) were identified as a verified source.\n")

# Load LC_MAIN data
df = pd.read_csv(sources["LC_MAIN"], header=None, delim_whitespace=True)

# Locate the timeframes to analyze.
print("Analyzing LC_MAIN data to select ignition time range...")
timeframes = analysis.locate_ignition(df)
print("Ignition times are located in range %d - %d.\n" % (timeframes[2], timeframes[3]))

# Plot graphs.
analysis.plot_graph(sources, "LC_MAIN", timeframes)
analysis.plot_graph(sources, "PT_COMB", timeframes)
analysis.plot_graph(sources, "PT_INJE", timeframes)
analysis.plot_graph(sources, "PT_FEED", timeframes)