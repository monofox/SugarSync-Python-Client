#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author: Alexander Straube
# author: Lukas Schreiner
# 
# For editors/contributors: please add an author tag above - 
# for a full list ;-)
#
# For debugging: please use the pudb from
# https://github.com/orsenthil/pudb.git
# because the original does not support python3!
from SugarSyncInstance import SugarSyncInstance
from Printer import Printer
import pyinotify

class SugarSyncNotifier:  
    EVT_CREATE = 1
    EVT_DELETE = 2
    EVT_MODIFY = 4
    
    def __init__(self, sync):
        self.sync = sync
        self.wm = None
        self.notifier = None
        self.watchPaths = []
        self.mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY

        SugarSyncInstance.notifier = self

    def startNotifier(self):
        self.wm = pyinotify.WatchManager()
        self.notifier = pyinotify.ThreadedNotifier(self.wm, NotifyHandler())
        self.notifier.start()

    def addNotifierPath(self, path, rdir):
        self.watchPaths.append(NotifyItem(path, self.wm.add_watch(path, self.mask, rec=True), rdir))

    def removeNotifierPath(self, path):
        # we have to go through all items, because
        # we can define more than one notifier for the same path.
        toRemove = []
        for f in self.watchPaths:
            if f.getPath() == path:
                values = f.getWatcher().values()
                for v in values:
                    self.wm.rm_watch(v)
                toRemove.append(f)

        for f in toRemove:
            self.watchPaths.remove(f)

    def removeNotifierPathRemote(self, rdir):
        # we have to go through all items, because
        # we can define more than one notifier for the same path.
        toRemove = []
        for f in self.watchPaths:
            if f.getRemoteDir() == path:
                values = f.getWatcher().values()
                for v in values:
                    self.wm.rm_watch(v)
                toRemove.append(f)

        for f in toRemove:
            self.watchPaths.remove(f)

    def notify(self, event, evtType):
        # search all notify items
        for f in self.watchPaths:
            # for the same put put, we abspath it ;-)
            if os.path.abspath(event.path) == f.getPath():
                if evtType == SugarSyncNotifier.EVT_CREATE:
                    f.getRemoteDir().notifyCreate(event)
                elif evtType == SugarSyncNotifier.EVT_DELETE:
                    f.getRemoteDir().notifyDelete(event)
                elif evtType == SugarSyncNotifier.EVT_MODIFY:
                    f.getRemoteDir().notifyModify(event)

    def stopNotifier(self):
        for f in self.watchPaths:
            values = f.getWatcher().values()
            for v in values:
                self.wm.rm_watch(v)
            # following thing does not work. Issue #33: https://github.com/seb-m/pyinotify/issues/33
            #self.wm.rm_watch(f.getWatcher().values())

        self.watchPaths = []
        # following thing does not work. Issue #33: https://github.com/seb-m/pyinotify/issues/33
        self.notifier.stop()

    def __del__(self):
        self.stopNotifier()
        self.notifier = None
        self.wm = None
        SugarSyncInstance.notifier = None

class NotifyItem:
    
    def __init__(self, path, watcher, remoteDir):
        self.path = path
        self.watcher = watcher
        self.remoteDir = remoteDir

    def setPath(self, path):
        self.path = path

    def getPath(self):
        return self.path

    def setWatcher(self, watcher):
        self.watcher = watcher

    def getWatcher(self):
        return self.watcher

    def setRemoteDir(self, rdir):
        self.remoteDir = rdir

    def getRemoteDir(self):
        return self.remoteDir

    def __del__(self):
        self.remoteDir = None
        self.watcher = None
    
class NotifyHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        notifier = SugarSyncInstance.notifier
        # at this point we will inform the notifier!
        notifier.notify(event, SugarSyncNotifier.EVT_CREATE)
        print("Creating:", event.pathname)

    def process_IN_DELETE(self, event):
        notifier = SugarSyncInstance.notifier
        # at this point we will inform the notifier!
        notifier.notify(event, SugarSyncNotifier.EVT_DELETE)
        print("Removing:", event.pathname)

    def process_IN_MODIFY(self, event):
        notifier = SugarSyncInstance.notifier
        # at this point we will inform the notifier!
        notifier.notify(event, SugarSyncNotifier.EVT_MODIFY)
        print("Modified:", event.pathname) 

