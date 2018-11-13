import json

def write_json(path, data):
    with open(path, 'w') as file:
        json.dump(data, file)

def read_json(path):
    with open(path, 'r') as file:
        out = json.load(file)
    return out
