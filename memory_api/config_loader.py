import json

def load_config(file_name):
    with open(file_name, "r") as f:
        return json.load(f)