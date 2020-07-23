import os
import json
import scan

with open('config.json') as json_file:
    config = json.load(json_file)
    input_path = config["input path"]

paths = [x[0] for x in os.walk(input_path)]
paths = paths[1:]

for path in paths:
    project = scan.Scan(input_location=path, config=config)
