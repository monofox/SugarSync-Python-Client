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

class SugarSyncFile:

    def __init__(self, sync, link):
        self.sync = sync
        self.link = link
        self.parent = None

    def setParent(self, parent):
        self.parent = parent
