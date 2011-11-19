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

class SugarSyncDirectory:
    # this is mainly for directories. But collections are nearly identicaly.
    # so we will handle it normal and will create subdirs

    def __init__(self, sync, link):
        self.sync = sync
        
        # link can be a link or an dsid
        # we have to find it out. I think the best is via collection=True or False
        self.link = link

        # it could be interesting on 'cd ..' (going level up)
        self.parent = None

        # when was the folder created?
        self.ctime = None

        # we need the name.
        self.name = ''

        # nearly i've forgotten the children :D
        self.children = {} # or dict ( with id : object ) ?

        if not self.retrieveInfo():
            print('Error retrieving information for \'%s\'' % link)

    # adding is simple. But removing? xD
    def addChild(self, child):
        self.children[child.getName()] = child

    # easy too ;-)
    def removeChild(self, child):
        try:
            del self.children.remove[child]
        except:
            print("Child doesn't exist!")

    def getChildren(self):
        return self.children

    def getTime(self):
        return self.ctime

    def getParent(self):
        return self.parent

    def retrieveInfo(self):
        pass

    def getName(self):
        return self.name

    def setName(self, name):
        if isinstance(name, XMLElement):
            self.name = name.getValue()
        else:
            self.name = name

    def setParent(self, parent):
        self.parent = parent


