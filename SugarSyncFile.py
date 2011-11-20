#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author: Lukas Schreiner
# 
# For editors/contributors: please add an author tag above - 
# for a full list ;-)
# 
# For debugging: please use the pudb from
# https://github.com/orsenthil/pudb.git
# because the original does not support python3!
from XMLElement import XMLElement

class SugarSyncFile:

    def __init__(self, sync, link):
        self.sync = sync
        self.name = None
        self.parent = None

        if link is not None:
            self.setLink(link)
        else:
            self.link = link

    def setLink(self, link):
        if isinstance(link, XMLElement):
            link = link.getValue()
        
        # we have to remove the api url
        links = link.split('/')
        link = links[len(links)-1]
        self.link = link

    def getLink(self):
        return self.link

    def setParent(self, parent):
        self.parent = parent

    def getParent(self):
        return self.parent

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name
