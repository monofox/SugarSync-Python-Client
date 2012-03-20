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
from Printer import Printer

class SugarSyncFile:

    def __init__(self, sync, link):
        self.sync = sync
        self.name = None
        self.parent = None
        self.timeCreated = None
        self.size = 0
        self.lastModified = None
        self.mediaType = None
        self.presentOnServer = True
        self.versions = []
        self.link = link

        if link is not None:
            self.setLink(link)

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

    def setMediaType(self, mediaType):
        self.mediaType = mediaType

    def getMediaType(self):
        return self.mediaType

    def setSize(self, size):
        self.size = int(str(size))

    def getSize(self):
        return self.size

    def setTimeCreated(self, tc):
        self.timeCreated = self.sync.parseDate(tc)

    def getTimeCreated(self):
        return self.timeCreated

    def setLastModified(self, lm):
        self.lastModified = self.sync.parseDate(lm)

    def getLastModified(self):
        return self.lastModified

    def setPresentOnServer(self, pos):
        if type(pos).__name__ == 'str':
            pos = pos == 'true' and True or False

        self.presentOnServer = pos

    def returnPresentOnServer(self):
        return self.presentOnServer

    def getInfo(self):
        data = self.sync.getFileInfo(self.link)
        self.size = int(str(data.size))
        self.presentOnServer = str(data.presentOnServer) == 'true' and True or False
        self.timeCreated = self.sync.parseDate(str(data.timeCreated))
        self.lastModified = self.sync.parseDate(str(data.lastModified))
        self.mediaType = str(data.mediaType)

    def setVersions(self):
        self.versions = self.sync.getFileHistory(self.link)

    def getVersions(self):
        if len(self.versions) <= 0:
            self.setVersions()

        return self.versions

    def printVersions(self):
        versions = self.getVersions()
        
        if len(versions) > 0:
            print('The versions of file %s:' % (self.name))
        else:
            print('There are no versions of the file %s.' % (self.name))

        for v in versions:
            v.printInfo()
    
    def printInfo(self):
        if self.timeCreated is None and self.lastModified is None:
            self.getInfo()

        if self.timeCreated is not None:
            create = self.timeCreated.strftime('%d/%m/%Y %H:%M')
        else: 
            create = None

        modified = self.lastModified.strftime('%d/%m/%Y %H:%M')

        if create is not None:
            output = '%s: %s, size of %i bytes, created on %s and modified on %s. It is%spresent on the server' % (
                    self.name, self.mediaType, self.size, create, modified, self.presentOnServer and ' ' or ' not '
                    )
        else:
            # this should only be possible when file is a version
            output = '%s: %s, size of %i bytes, creation time is not known and modified on %s. It is%spresent on the server' % (
                    self.name, self.mediaType, self.size, modified, self.presentOnServer and ' ' or ' not '
                    )


        print(output)

