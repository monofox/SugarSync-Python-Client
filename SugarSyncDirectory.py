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

class SugarSyncDirectory:
    # this is mainly for directories. But collections are nearly identicaly.
    # so we will handle it normal and will create subdirs

    def __init__(self, sync, link, collection=False):
        self.sync = sync
        
        # attributes
        # if this directory is a fake and so
        # a collection: set it to true
        self.collection = collection

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
        self.children = [] # or dict ( with id : object ) ?

        if self.collection:
            self.initCollection()
        elif not self.retrieveInfo():
            print('Error retrieving information for \'%s\'' % link)

    def initCollection(self):
        if self.collection:
            f = self.sync.getCollectionContentInfo(self.link) # we can use self.link, because its full link.
            # then do it.
            # TODO .
    
    # adding is simple. But removing? xD
    def addChild(self, child):
        self.children.add(child)

    # easy too ;-)
    def removeChild(self, child):
        self.children.remove(child)

    def getTime(self):
        return self.ctime

    def getParent(self):
        return self.parent

    def retrieveInfo(self):
        pass

    def getName(self):
        # why adding '/' at the end? So we can see that this is a directory
        # later via colors?
        return '%s/' % self.name

    def setParent(self, parent):
        self.parent = parent


