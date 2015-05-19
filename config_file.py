import ConfigParser
import subprocess

class ConfigFile(object):
    def __init__(self):
        self.parser = ConfigParser.ConfigParser()
        self.parser.optionxform = str
        self.parser.read("pi-jukebox.conf")
        # MPD configuration settings
        self.settings = []
        self.radio_stations = []
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
            for setting in self.settings:
                if setting['section'] == 'Radio stations':
                    self.radio_stations.append((setting['key'], setting['value']))

    def setting_get(self, section, key):
        if self.setting_exists(section, key):
            value = self.parser.get(section, key)
            return value

    def setting_set(self, section, key, value):
        """ Write a setting to the configuration file
        """
        file = open("pi-jukebox.conf", 'w')
        try:
            self.parser.add_section(section)
        except Exception:
            pass
        self.parser.set(section, key, value)
        self.parser.write(file)
        file.close()

    def setting_remove(self, section, key):
        """ Remove a setting to the configuration file
        """
        file = open("pi-jukebox.conf", 'w')
        try:
            self.parser.remove_option(section, key)
        except Exception:
            pass
        self.parser.write(file)
        file.close()

    def section_exists(self, section):
        return self.parser.has_section(section)

    def setting_exists(self, section, key):
        return self.parser.has_option(section, key)

    def radio_station_set(self, name, URL):
        """ Edits or creates radio station entry """
        self.setting_set('Radio stations', name, URL)

    def radio_stations_get(self):
        """ Get's radio stations from the configuration file and returns them in a list """
        self.radio_stations = []
        options = self.parser.options('Radio stations')
        for option in options:
            description = option
            URL = self.setting_get('Radio stations', option)
            self.radio_stations.append((description, URL))
        return self.radio_stations

    def section_get(self, section):
        dict1 = {}
        options = self.parser.options(section)
        for option in options:
           setting = self.parser.getboolean(section, option)
        return dict1

config_file = ConfigFile()