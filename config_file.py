import ConfigParser
import subprocess

class ConfigFile(object):
    def __init__(self):
        self.parser = ConfigParser.ConfigParser()
        self.parser.read("pi-jukebox.conf")
        # MPD configuration settings
        self.settings = []
        self.settings.append({'section': 'MPD Settings', 'key': 'host', 'value': 'localhost', 'first_time': False})
        self.settings.append({'section': 'MPD Settings', 'key': 'port', 'value': 6600, 'first_time': False})
        self.settings.append({'section': 'MPD Settings', 'key': 'music directory', 'value': None, 'first_time': True})
        self.initialize()

    def initialize(self):
        for setting in self.settings:
            if self.setting_exists(setting['section'], setting['key']):
                setting['value'] = self.setting_get(setting['section'], setting['key'])
            elif not setting['first_time']:
                self.setting_set(setting['section'], setting['key'], setting['value'])

    def setting_get(self, section, key):
        if self.setting_exists(section, key):
            value = self.parser.get(section, key)
            return value

    def setting_set(self, section, key, value):
        file = open("pi-jukebox.conf", 'w')
        try:
            self.parser.add_section(section)
        except Exception:
            pass
        self.parser.set(section, key, value)
        self.parser.write(file)
        file.close()

    def setting_exists(self, section, key):
        return self.parser.has_option(section, key)
        pass

    def section_get(self, section):
        dict1 = {}
        options = self.parser.options(section)
        for option in options:
           setting = self.parser.getboolean(section, option)
        return dict1

config_file = ConfigFile()