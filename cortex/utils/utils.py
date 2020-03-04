from configparser import ConfigParser

def read_config(path):
    config = ConfigParser()
    config.read(path)
    return config