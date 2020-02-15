import tempfile
import json
import os
import struct
import glob

import analysis


format_string = "2Q"

def locate_logs(sourcepath: str) -> list:
    source_logs = glob.glob(os.path.join(sourcepath,"*.log"))

    if len(source_logs) == 0:
        print("Could not locate any log files in the source directory '%s'." % sourcepath)
        exit()

    print("Located %d log file(s).\n" % len(source_logs))

    return source_logs

def read_config(configpath: str) -> dict:
    calibrations = {}

    # Load calibration information from config.
    try: 
        with open(configpath, "r") as config_json:
            config_map = json.load(config_json)

            try:
                for panel in config_map[0]["panels"]:
                    for src in panel["data"]:
                        calibrations[src["source"]] = (src["calibration"], panel["unit"])

            except KeyError:
                print("Please provide a valid RESFET Dashboard config file. The provied .json file does not follow the structure.")
                exit()

    except IOError:
        print("RESFET Dashboard config file '%s' could not be located. Please specify the location using --config parameter." % configpath)
        exit()

    return calibrations

def decode_calibrate_logs(source_logs: list, calibrations: dict, tempdir) -> list:
    decoded_logs = []
    for filename in source_logs:
        file_head, file_tail = os.path.split(filename)

        calibration = analysis.match_calibration_and_file(calibrations, file_tail)

        if not calibration:
            print("Could not calibrate '%s' because no matching calibration is found in config" % (file_tail))
            exit()

        print("Decoding and calibrating '%s' with '%s'..." % (file_tail, calibration))

        lambda_funct = eval("lambda x: "+calibrations[calibration][0])

        # mtype = bytes([9 + i])
        with open(filename, 'rb') as f, open(os.path.join(tempdir, file_tail), 'w') as p:

            f.seek(0, 2)
            file_size = f.tell()
            f.seek(0, 0)

            # print("File size", file_size, file_size / 260.0)

            for _ in range(int(file_size // 260)):
                data_line = f.read(260)
                data_bytes = bytes(data_line)

                # TODO do some verification with the header type
                header = data_bytes[:4]
                data = data_bytes[4:]
                # print("data size", len(data))
                for i in range(256 // 16):
                    d, t = struct.unpack(format_string, bytes(data[i*16:i*16+16]))

                    cal = lambda_funct(d)

                    p.write(str(t) + " " + str(d) + " " + str(cal) + "\n")
        decoded_logs.append(os.path.join(tempdir, file_tail))
    
    print("")
    return decoded_logs