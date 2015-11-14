#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os.path

import ConfigParser



SECTION_GLOBAL = 'GlobalParam'
OPTION_LANG = 'language'

class Configurations:
    PATH = './HomePy.cfg'

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        if os.path.isfile(self.PATH):
            print 'Found configurations...'
        else:
            print 'Making configuration file...'
            # Make config file
            self.config.add_section(SECTION_GLOBAL)
            self.config.set(SECTION_GLOBAL, OPTION_LANG, 'en')
            # Write configurations to 'HomePy.cfg'
            with open(self.PATH, 'wb') as configfile:
                config.write(configfile)

        print 'Read configurations...'
        self.config.read(self.PATH)


    def get_language(self):
        if self.config.has_section(SECTION_GLOBAL) and self.config.has_option(SECTION_GLOBAL, OPTION_LANG):
            return self.config.get(SECTION_GLOBAL, OPTION_LANG)
        else:
            self.set_language('en')
            return 'en'

    def set_language(self, code):
        self.config.set(SECTION_GLOBAL, OPTION_LANG, code)
        # Write configurations to 'HomePy.cfg'
        with open(self.PATH, 'wb') as configfile:
            self.config.write(configfile)



