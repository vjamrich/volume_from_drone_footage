import os
import json

with open('config.json') as json_file:
    config = json.load(json_file)

metashape_loc = config["metashape location"]
cmd = "\"" + metashape_loc + "\" -r main.py"

os.system(cmd)
