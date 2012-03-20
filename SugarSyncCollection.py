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

from SugarSyncFile import SugarSyncFile
from SugarSyncDirectory import SugarSyncDirectory
from Printer import Printer
class SugarSyncCollection:

    def __init__(self, sync, link):
        self.sync = sync
        self.link = link
        self.name = ''
        self.ctime = None
        self.iconID = None

        self.parent = None
        self.children = {}

        self.start = 0
        self.end = 0
        self.maxEntries = 500
        self.hasMore = False

        self.loadCollection()

    def loadCollection(self):
        data = self.sync.getCollectionContentInfo(self.link, 'all', self.start, self.maxEntries)
        if data is None:
            print('Fatal Error on parsing collection content!')

        else:
            print('Wait and analyze the class')
            for collection in data.childs:
                tmp = None
                if collection.hasAttribute('type') and collection.getAttribute('type') == 'syncFolder':
                    tmp = SugarSyncDirectory(self.sync, collection.ref)
                    tmp.setName(collection.displayName)
                    tmp.setParent(self)
                else:
                    tmp = SugarSyncFile(self.sync, collection.ref)
                    tmp.setParent(self)

                if tmp is not None:
                    self.addChild(tmp)

    def addChild(self, child):
        self.children[child.getName()] = child

    def getChildren(self):
        return self.children

    def removeChild(self, child):
        try:
            del self.children[child.getName()]
        except KeyError as ke:
            print('Key %s does not exist.' % child.getName())

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setParent(self, parent):
        self.parent = parent

    def getParent(self):
        return self.parent

    def printInfo(self):
        # TODO implement me! ;-) (Problem with collection link
        output = '%s: workspace or collection. icon id: %i, created on %s' % (
                self.name, 0, ' TODO - not implemented yet - '
                )

        print(output)

