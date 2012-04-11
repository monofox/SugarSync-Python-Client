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
from SugarSyncFile import SugarSyncFile
from Printer import Printer
from SugarSync import SugarSync
from SugarSyncInstance import SugarSyncInstance

class SugarSyncDirectory:
    # this is mainly for directories. But collections are nearly identicaly.
    # so we will handle it normal and will create subdirs

    def __init__(self, link):
        # link can be a link or an dsid
        # we have to find it out. I think the best is via collection=True or False
        if link is not None:
            self.setLink(link)
        else:
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

    def getSortList(self):
        return self.sortList

    def setLink(self, link):
        if isinstance(link, XMLElement):
            link = link.getValue()
        
        # we have to remove the api url
        links = link.split('/')
        link = links[len(links)-1]
        self.link = str(link)

    def getLink(self):
        return self.link

    # easy too ;-)
    def removeChild(self, child):
        try:
            del self.children.remove[child]
        except:
            print("Child doesn't exist!")

    def getChildren(self):
        return self.children

    def setTime(self, time):
        dt = SugarSync.parseDate(time)
        if dt is not None:
            self.ctime = dt
        else:
            print('Error on setting creation time.')

    def getTime(self):
        return self.ctime

    def getParent(self):
        return self.parent

    def retrieveInfo(self):
        # first folder informations
        informations = SugarSync.getFolderInfo(self.link)
        if informations is not None:
            self.setName(informations.displayName)
            self.setTime(informations.timeCreated.getValue())
            self.retrieveChildren()
            return True
        else:
            return False

    def retrieveChildren(self):
        data = SugarSync.getFolderContents(self.link)
        # we have to split all elements and check whether its a folder or a file
        childs = data.getChildren()

        if childs is not None:
            for c in childs:
                if c.getName() == 'collection' and c.getAttribute('type') == 'folder':
                    elm = SugarSyncDirectory(c.ref)
                else:
                    elm = SugarSyncFile(c.ref)
                
                elm.setName(str(c.displayName))
                elm.setParent(self)
                self.addChild(elm)

    def searchChild(self, filename):
        i = 0
        found = False

        while i < len(self.children) and not found:
            if isinstance(self.children[i], SugarSyncFile) \
                    and self.children[i].getName() == filename:
                found = True

            i += 1

        return self.children[i-1]

    def refresh(self):
        self.children = {}
        self.retrieveChildren()

    def getName(self):
        return self.name

    def setName(self, name):
        if isinstance(name, XMLElement):
            self.name = name.getValue()
        else:
            self.name = name

    def setParent(self, parent):
        self.parent = parent

    def printInfo(self):
        create = self.ctime.strftime('%d/%m/%Y %H:%M')
        output = '%s: directory, created on %s' % (self.name, create)
        print(output)

    def notifyCreate(self, evt):
        # if its a directory, we will set a new notify item ;-)
        # (after creating the dirctory)
        pass

    def notifyDelete(self, evt):
        # if its a directory, the directory will remove the watcher - if there exist any.
        pass

    def notifyModify(self, evt):
        # we have to upload it / update it.
        child = self.searchChild(evt.name)
        child.update(evt.pathname)

