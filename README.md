# Resfet Analysis Tool
This tool allows to analyze RESFET and RESFET Dashboard sensor log data.

## Usage
After cloning the repository run `python3 ./main.py --src 'logsdir' --type 'resfet/dashboard' --config 'path/to/dashboard_config.json'` The analysis will take 10-15 seconds depending on the source log type. If `--type resfet` is supplied, then the source logs will be encoded, calibrated using `--config` parameter, and saved into a temporary directory. After the analysis is completed, graphs will be launched in the default web browser.
