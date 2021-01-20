# coding = utf-8
import logging
import time

import yaml


def load_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as fin:
        data = yaml.load(fin, Loader=yaml.FullLoader)
    return data


def to_yaml(obj, filepath):
    with open(filepath, 'w', encoding='utf-8') as fout:
        yaml.dump(obj, fout, allow_unicode=True)


def read_metadata_from_file(filepath):
    import taglib
    instance = taglib.File(filepath)
    return instance.tags




if __name__ == '__main__':
    tags = read_metadata_from_file('1.jpg')
    print(tags)