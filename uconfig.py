import configparser
from pathlib import Path


class Uconfig:
    config = None

    def __init__(self, file=str((Path(__file__).parent / "../config.ini").resolve())):
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.file=file
        self.config.read(file)

    def updateconfig(self, section='', key='', value=''):
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(self.file)
        cfgfile = open(self.file, 'w')
        config.set(str(section), str(key), str(value))
        config.write(cfgfile)
        cfgfile.close()
