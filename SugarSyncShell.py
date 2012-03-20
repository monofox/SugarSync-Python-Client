#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-
#
# author: Alexander Straube
# author: Lukas Schreiner
# 
# For editors/contributors: please add an author tag above - 
# for a full list ;-)
# 
# Be careful! This communicates directly with sugarsync! (only names are cached!)

from SugarSyncCollection import SugarSyncCollection
from SugarSyncDirectory import SugarSyncDirectory
from SugarSyncFile import SugarSyncFile
from Colors import Colors
from console import Console
from Printer import Printer
from XMLElement import XMLElement
from XMLTextNode import XMLTextNode
import os, os.path, readline, atexit
from pickle import Pickler, Unpickler

#TODO: implement readline for move & others.
class SugarSyncShell:
    TYPE_FILE = 1
    TYPE_FOLDER = 2
    TYPE_ALL = 4

    def __init__(self, sugarsync, startdir=None, collection=True):
        self.sugarsync = sugarsync
        self.virtualfs = startdir # starts with startdir
        self.localPath = os.getcwd()
        self.path = [startdir]
        self.run = True
        self.histfile = os.path.join(os.environ["HOME"], ".pyhist")
        try:    
            readline.read_history_file(self.histfile)
        except IOError:
            pass
        atexit.register(readline.write_history_file, self.histfile)

        self.cmds = {
                'clear': self.clear,
                'cd': self.cd,
                'file': self.info,
                'history': self.history,
                'get': self.get,
                'put': self.put,
                'rm': self.rm,
                'ls': self.ls,
                'lpwd': self.lpwd,
                'lcd' : self.lcd,
                'lmkdir': self.lmkdir,
                'pwd': self.pwd,
                'help': self.help,
                'refresh': self.refresh,
                'save': self.save,
                'load': self.load,
                'exit': self.exit
                }
        self.names = []

        self.cmd()

    def save(self, param):
        # saves the shell with all the supdirs.
        with open('syncdata.bin', 'wb') as f:
            Pickler(f, 3).dump(self.path)

        print('Data saved...')

    def load(self, param):
        if os.path.isfile('syncdata.bin'):
            with open('syncdata.bin', 'rb') as f:
                self.path = Unpickler(f).load()

            self.clear()
            print('Data loaded...')
        else:
            print('File not found. Session saved?')

    def getPath(self, withHeader=True, colorize=True):
        # the beginning:
        if len(self.sugarsync.nickname) > 0:
            h = self.sugarsync.nickname + ' '
        else:
            h = self.sugarsync.username[:self.sugarsync.username.find('@')] + ' '

        if colorize:
            h = Colors.c(h, Colors.YELLOWL)

        p = ''

        for f in self.path:
            p = p + f.getName() + '/'
        
        if colorize:
            p = Colors.c(p, Colors.BLUE)

        if withHeader:
            return h + p
        else:
            return p

    def cmd(self):
        while self.run:
            want = input('%s %s ' % (self.getPath(), Colors.c('$', Colors.BLUE)))
            cmd = ''
            param = ''
            # its always the same: command parameters - there is no &&, ||, |, &, etc. pp.

            index = want.find(' ')
            if index > 0:
                cmd = want[:index]
                param = want[index:]
            else:
                cmd = want
                param = ''

            try:
                self.cmds[cmd](param)
            except KeyError as ke:
                print('Wrong input.')
            except Exception as e:
                print('Error processing action.', e)

    def searchPath(self, path, typ):
        data = None
        elm = self.path[len(self.path)-1]
        elm = elm.getChildren()

        if elm is not None:
            keys = list(elm.keys())
            i = 0
            while data is None and i < len(keys):
                if str(elm[keys[i]].getName()).strip() == path.strip() and (
                        (isinstance(elm[keys[i]], SugarSyncDirectory) and typ == SugarSyncShell.TYPE_FOLDER)
                        or   (isinstance(elm[keys[i]], SugarSyncFile) and typ == SugarSyncShell.TYPE_FILE)
                        or   typ == SugarSyncShell.TYPE_ALL
                        ):
                    data = elm[keys[i]]

                i = i+1

        return data

    def clear(self, param):
        (width, height) = Console.getTerminalSize()
        for f in range(0,height):
            print('');

    def help(self, param):
        # this is a method to display the help
        print('Following commands are possible:')
        for cmd in self.cmds:
            print(cmd)

    def cd(self, param):
        # TODO: at this point its very pre-release...
        # we have to trim the param
        param = param.strip()
        if param[len(param)-1:] == '/':
            param = param[:-1]

        # and split on / ?

        if param == '.':
            return True
        elif param == '..':
            self.path.pop()
        else:
            # search
            path = self.searchPath(param, SugarSyncShell.TYPE_FOLDER)
            if path is not None:
                self.path.append(path)
                return True
            else:
                print('Could not change the directory.')
                return False
    

    def ls(self, param):
        # get actual element:
        elm = self.path[len(self.path)-1]

        print(Colors.c('./', Colors.BLUE))
        if len(self.path) > 1:
            print(Colors.c('../', Colors.BLUE))

        for k,v in elm.getChildren().items():
            if isinstance(v, SugarSyncDirectory):
                print(Colors.c(str(k) + '/', Colors.BLUE))
            else:
                print(k)

    def pwd(self, param):
        print(self.getPath(False, False)) # withour header and without color

    def history(self, param):
        param = param.strip()
        
        if param in ['.', './', '..', '../'] or param[len(param)-1:] == '/':
            print('It can be only a file.')
            return False

        elm = self.searchPath(param, SugarSyncShell.TYPE_FILE)
        if elm is not None:
            elm.printVersions()
        else:
            print('Path not found.')

    def info(self, param):
        param = param.strip()
        
        if param in ['.', './']:
            elm = self.path[len(self.path)-1]
        elif param in ['..', '../'] and len(self.path) > 1:
            elm = self.path[len(self.path)-2]
        elif param not in ['.', '..']:
            elm = self.searchPath(param, SugarSyncShell.TYPE_ALL)
        else:
            print('Invalid path.')
            return False

        if elm is not None:
            elm.printInfo()
        else:
            print('Path not found.')

    def get(self, param):
        # at this point it can only be a file
        param = param.strip()

        if param in ['.', '..'] or param[len(param)-1:] == '/':
            print('It can be only a file at this development point.')
            return False
        
        elm = self.searchPath(param, SugarSyncShell.TYPE_FILE)
        if elm is not None:
            # filename ? and check if its exist...
            fname = str(elm.getName())
            if os.path.lexists(self.localPath+'/'+fname):
                # overwrite?
                overwrite = None
                while overwrite is None:
                    ow = input('Overwrite "%s/%s"? (N/y)' % (self.localPath,fname))
                    ow = ow.strip()
                    if ow in ['y', 'Y']:
                        overwrite = True
                    elif ow in ['n', 'N', '']:
                        overwrite = False
                    else:
                        print('I have not understand your answer "%s".' % (ow))

                if overwrite and not os.path.isfile(self.localPath+'/'+fname):
                        print('Can not overwrite something which is not a file.')
                        overwrite = None
            else:
                overwrite = True

            if overwrite and os.path.lexists(self.localPath+'/'+fname):
                os.remove(self.localPath+'/'+fname)
            
            if overwrite:
                self.sugarsync.getFile(elm.getLink(), self.localPath+'/'+fname)

        else:
            print('Could not find the file.')
            return False

    def put(self, param):
        param = param.strip()

        if param in ['.', '..'] or param[len(param)-1:] == '/':
            print('It can be only a file at this development point.')
            return False

        # exist param local?
        if os.path.isfile(self.localPath+'/'+param):
            # exist it in this path online?
            elm = self.searchPath(param, SugarSyncShell.TYPE_FILE)
            if elm is not None:
                # found. Overwrite?
                overwrite = None
                while overwrite is None:
                    ow = input('Such a file exist already online. Overwrite "%s"? (N/y)' % (param))
                    ow = ow.strip()
                    if ow in ['y', 'Y']:
                        overwrite = True
                    elif ow in ['n', 'N', '']:
                        overwrite = False
                    else:
                        print('I have not understand your answer "%s".' % (ow))

                if overwrite and not isinstance(elm, SugarSyncFile):
                    print('Can not overwrite something which is not a file.')
                    overwrite = None
            else:
                overwrite = True
            
            create = overwrite and elm is None
            if not create:
                filename = str(elm.getLink())
            else:
                filename = str(self.path[len(self.path)-1].getLink()) + '/' + param

            self.sugarsync.uploadFile(self.localPath+'/'+param, filename, create)
        else:
            print('Could not find the file.')

    def rm(self, param):
        param = param.strip()
        
        if param in ['.', '..'] or param[len(param)-1:] == '/':    
            print('It can be only a file at this development point.')
            return False

        # exist file?
        elm = self.searchPath(param, SugarSyncShell.TYPE_FILE)
        if elm is not None:
            # found.. delete it *hrhrhr* ;-)
            self.sugarsync.deleteFile(elm.getLink())
        else:
            print('Could not find the file.')

    def refresh(self, param):
        param = param.strip()
        elm = None

        if len(param) > 0:
            elm = self.searchPath(param, SugarSyncShell.TYPE_FOLDER)
        else:
            elm = self.path[len(self.path)-1]
    
        if elm is None:
            print('Folder not found.')
        else:
            elm.refresh()

    def lcd(self, param):
        param = param.strip()
        # change local path
        os.chdir(param)
        self.localPath = os.getcwd()

    def lmkdir(self, param):
        param = param.strip()
        dirs = param.split('/')
        if dirs[len(dirs)-1].strip() == '':
            dirs.pop(len(dirs)-1)

        if len(dirs) < 1:
            print('You have to specify a directory to create.')
        else:
            try:
                if len(dirs) == 1:
                    os.mkdir(param)
                    print('Folder was create.')
                else:
                    os.makedirs(param, exist_ok=True)
            except:
                print('Folder could not be created.')

    def lpwd(self, param):
        # we do not accept any param
        print('Local Path: ' + os.getcwd())

    def lrm(self, param):
        param = param.strip()
        
        if os.path.isfile(param):
            try:
                os.remove(param)
                print('File could be deleted.')
            except:
                print('There was an error deleting the file.')
        elif os.path.isdir(param):
            print('I only support files at this point of development.')


    def exit(self, param):
        print('Goodbye ;-)')
        self.run = False
            

