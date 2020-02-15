import sys

def read_commandline_arguments() -> dict:
    """
    Reads the command line arguments and provides a setting
    mapping for program's use.
    """

    valid_syntax = "./main.py [--src \"dir\"] [--out \"dir\"] [--type \"dashboard/arca\"] [--config \"dir\"]"

    settings = {
        "--src": "./",
        "--out": "./",
        "--type": "dashboard",
        "--config": "./config.json"
    }

    # Validate the length of the arguments.
    if len(sys.argv) == 1 or (len(sys.argv) - 1) % 2 == 0:

        # Pair arguments and values.
        for i in range(1, len(sys.argv), 2):

            # Valid inputs.
            if sys.argv[i] not in settings.keys():
                print("Invalid argument '%s'. Run with %s" % (sys.argv[i], valid_syntax))
                exit()

            settings[sys.argv[i]] = sys.argv[i+1]
    else: 
        print("Missing arguments. Run with %s" % (valid_syntax))
        exit()

    return settings