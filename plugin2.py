
import re
import os
import os.path
import sys
import logging

import sublime
import sublime_plugin
#import time
# from .parse import *
from .const.const import *

class Generator2Command(sublime_plugin.TextCommand):

    def __init__(self, x):
        self.conns = []

        self.logger = logging.getLogger('driver_generator')
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s\t%(levelname)s: function:\"%(funcName)s\" : %(message)s')
        ch.setFormatter(formatter)
        self.logger.handlers = []
        self.logger.addHandler(ch)

        super(Generator2Command, self).__init__(x)


    def run(self, edit):
        self.conns = []
        self.find_conns()
        self.logger.log(logging.DEBUG, "lel")


    def find_conns(self):
        "znajdź nazwy plików conn"
        found = False
        regions = self.view.find_all("conn_file:")
        for r in regions :
            l = self.view.line(r)
            #print("find_conns found region: ", "b: ",  l.begin(), " e:", l.end(), " s:", l.size())
            #print(self.view.substr(l))
            reg_match = conn_file_name.match(self.view.substr(l))
            if reg_match : 
                pwd = os.path.dirname(os.path.abspath(__file__))
                full_path = str(pwd) + "\\" + reg_match.group(1)
                #print("filename:", full_path)
                self.conns.append(full_path)
                found = True
        self.logger.debug("conns: " + str(self.conns))
        if not found :
            self.logger.error("NO CONN FILES FOUND!")

    def  find_tasks(self) :
        "wytnij fragment definicji"
        regions = self.view.find_all("tasks_to_generate([\s|\S])+end_of_tasks_to_generate")
        self.logger.debug("find_tasks len(regions)=",len(regions))
        return [ self.view.substr(r) for r in regions ]

    def find_groups(self, task):
        "znajdź fragmenty o wspólnych ścieżkach globalnych"
        groups = []
