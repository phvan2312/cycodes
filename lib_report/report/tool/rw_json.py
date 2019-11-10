import os
import json


def write_json_to_file(obj, file_path):
    folder = os.path.dirname(file_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(file_path, 'w', encoding='utf-8') as fp:
        json.dump(obj, fp, ensure_ascii=False, indent=4)


def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as fp:
        return json.load(fp)
