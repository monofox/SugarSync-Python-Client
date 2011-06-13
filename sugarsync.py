#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-

import urllib.request, urllib.error, urllib.parse
from configparser import SafeConfigParser
from httplib2 import Http, Response
import re
import datetime

class SugarSync:
    def __init__(self):
        # will be written to config.ini on exit and loaded on startup
        self.username = ''
        self.password = ''
        self.accessKeyId = ''
        self.privateAccessKey = ''
        self.apiURL = ''
        self.token = None
        self.tokenExpire = None
        self.xmlHead = '<?xml version="1.0" encoding="UTF-8" ?>'
        self.config = None
        self.exit = False

        # user info
        self.nickname = ''
        self.salt = ''
        self.quotaLimit = 0
        self.quotaUsage = 0

        #folder
        self.folder = {}

        # Call functions
        self.readConfig()
        self.checkAuth()
        self.cmd()
        self.writeConfig()

    def cmd(self):
        self.exit = False
        while self.exit is False:
            print("\n\n\n \
                   ==== M - E - N - U ====\n\n \
                   0: Exit\n \
                   1: Authenticate\n \
                   2: User info\n \
                   3: load contents collection\n \
                   4: Creating a new folder\n \
                   5: Delete a folder\n \
                   6: Creating a new file\n \
                   7: Delete a file\n \
                   8: Rename a folder\n \
                   9: Rename a file\n \
                   10: Moving a file ::: DOES NOT WORK!\n \
                   11: Copy a file ::: DOES NOT WORK (400)\n \
                   12: Upload a file\n \
                   13: Download a file")

            want = int(input("What do you want?\n"))
            if want == 0:
                print("\nExiting...\n")
                self.exit = True
            elif want == 1:
                print("\nAuthenticating...\n")
                self.auth()
            elif want == 2:
                print("\nUser info...\n")
                self.getUser()
            elif want == 3:
                print('\nCollecting all files...\n')
                self.getAllFilesCollection()
            elif want == 4:
                print('\nCreating a new folder...\n')
                # we need path:
                path = input('Folder path: ')
                newfolder = input('Foldername: ')

                self.createFolder(path, newfolder)
            elif want == 5:
                print('\nDeleting a folder...\n')
                # we need the folder id
                foldername = input('Folder ID: ')
                
                self.deleteFolder(foldername)
            elif want == 6:
                print('\nCreating a new file...\n')
                # we need path:
                path = input('Folder path: ')
                # we need filename
                newfile = input('Filename: ')
                # and last but not least: media type
                media = input('MediaType (ex. text/plain, image/jpeg): ')

                self.createFile(path, newfile, media)
            elif want == 7:
                print('\nDeleting a file...\n')
                # we need the file id
                filename = input('File ID: ')
                
                self.deleteFile(filename)
            elif want == 8:
                print('\nRenaming a folder...\n')
                # we need folder
                path = input('Folder: ')
                # we need new name
                name = input('New folder name: ')

                self.renameFolder(path, name)
            elif want == 9:
                print('\nRenaming a file...\n')
                # we need folder
                path = input('File: ')
                # we need new name
                name = input('New file name: ')

                self.renameFile(path, name)
            elif want == 10:
                print('\nMoving a file...\n')
                # we need the file
                file = input('File: ')
                # we need the new path
                path = input('New path (collection): ')

                self.moveFile(file, path)
            elif want == 11:
                print('\nCopy a file...\n')
                # we need the source
                source = input('Source file: ')
                # we need the target folder
                target = input('Target folder: ')
                # we need the name
                name = input('Name (in future on blank it will receive actual name): ')

                self.copyFile(source, target, name)
            elif want == 12:
                print('\nUploading a file...\n')
                # we need the filename
                file = input('File to be uploaded (local!): ')
                # remote file
                filename = input('File in SugarSync: ')

                self.uploadFile(file, filename)
            elif want == 13:
                print('\nDownloading a file...\n')
                # we need the file
                file = input('File (remote): ')
                # save to?
                saveto = input('Save to (with filename): ')

                self.getFile(file, saveto)
            else:
                print("\n\nWRONG input - Try again!\n\n")

    
    def readConfig(self):
        self.config = SafeConfigParser()
        self.config.read(['config.ini'])

        self.username = self.config.get('user', 'username')
        self.password = self.config.get('user', 'password')
        self.accessKeyId = self.config.get('connection', 'accessKeyId')
        self.privateAccessKey = self.config.get('connection', 'privateAccessKey')
        self.apiURL = self.config.get('connection', 'url')

        self.token = self.config.get('auth', 'token')
        self.tokenExpire = self.config.get('auth', 'tokenExpire')
        # user
        self.quotaLimit = self.config.get('quota', 'limit')
        self.quotaUsage = self.config.get('quota', 'usage')
        
        # folder
        for k,v in self.config.items('folder'):
            self.folder[k] = v


    def writeConfig(self):
        self.config.set('user', 'username', str(self.username))
        self.config.set('user', 'password', str(self.password))
        self.config.set('connection', 'accessKeyId', str(self.accessKeyId))
        self.config.set('connection', 'privateAccessKey', str(self.privateAccessKey))
        self.config.set('connection', 'url', str(self.apiURL))
        self.config.set('auth', 'token', str(self.token))
        self.config.set('auth', 'tokenExpire', str(self.tokenExpire))
        self.config.set('quota', 'limit', str(self.quotaLimit))
        self.config.set('quota', 'usage', str(self.quotaUsage))

        for k,v in self.folder.items():
            self.config.set('folder', k, v)

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def sendRequest(self, path, data = {}, token = True, post = True, headers = {}):
        response = None

        if post:
            headers['Content-Type'] = 'application/xml; charset=UTF-8'
        if token:
            headers['Authorization'] = self.token
        
        try:
            if post:
                request = urllib.request.Request(self.apiURL+path, data.encode('utf8'))
                for k,v in headers.items():
                    request.add_header(k, v)

                response = urllib.request.urlopen(request)
            elif len(data) == 0:
                request = urllib.request.Request(self.apiURL+path)
                request.add_header('Authorization', self.token)

                response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            print('Error while requesting API call: %s (%s)' % (e.msg, e.code))
        except urllib.error.URLError as e:
            print('Error while requesting API call: %s' % (e.reason))
            
        return response
 
    def sendRequestPut(self, url, data = {}):
        response = None

        headers = {'Authorization': self.token, 'Content-Type': 'application/xml; charset=UTF-8'}
        h = Http(disable_ssl_certificate_validation=True)
        resp, content = h.request(self.apiURL+url, 'PUT', data.encode('utf8'), headers)

        if content is not None:
            content = content.decode('utf8')
        
        return (resp, content)

    def sendRequestDelete(self, url):
        response = None
        
        headers = {'Authorization': self.token}
        h = Http(disable_ssl_certificate_validation=True)
        resp, content = h.request(self.apiURL+url, 'DELETE', None, headers)

        if content is not None:
            content = content.decode('utf8')

        return (resp, content)

    def parseDate(self, date):
        pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})T([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2})\.([0-9]{1,3})((\-|\+)([0-9]{1,2})):([0-9]{1,2})'
        m = re.compile(pattern)

        match = m.match(date)
        if match is not None:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            hour = int(match.group(4))
            minute = int(match.group(5))
            second = int(match.group(6))
            offsetOperand = match.group(9)
            offsetMulti = int(offsetOperand+'1')*-1
            offsetHour = int(match.group(10))
            offsetMinute = int(match.group(11))

            # now correct hour
            hour = hour+offsetHour*offsetMulti
            minute = minute+offsetMinute*offsetMulti

            if minute > 59:
                diff = minute/60.0
                hour+= int(diff)
                diff = diff-int(diff)
                minute = diff*60

            if hour >= 24:
                diff = hour/24
                day += int(diff)
                diff = diff-int(diff)
                hour = diff*24

            dd = datetime.datetime(year, month, day, hour, minute, second)

            return dd
        else:
            return None

    def checkAuth(self):
        # check whether token is expired or not!
        date = self.parseDate(self.tokenExpire)
        date2 = datetime.datetime.utcnow()

        # compare: if date <= date2: self.auth, else: nothing!
        if date != None:
            if date <= date2:
                self.auth()
                return False
            else:
                return True
        else:
            return True


    def auth(self):
        data = XMLElement('authRequest')
        data.setHead(self.xmlHead)

        data.addChild(XMLElement('username').addChild(XMLTextNode(self.username)))
        data.addChild(XMLElement('password').addChild(XMLTextNode(self.password)))
        data.addChild(XMLElement('accessKeyId').addChild(XMLTextNode(self.accessKeyId)))
        data.addChild(XMLElement('privateAccessKey').addChild(XMLTextNode(self.privateAccessKey)))
        
        response = self.sendRequest('/authorization', data.toString(), False)
        if response is not None:
            info = response.info()
            self.token = info['Location']
            resp = XMLElement.parse(response.read().decode('utf8'))
            self.tokenExpire = resp.expiration

    def addElementToDatabase(self, file, location):
        pass

    def createFile(self, path, filename, media):
        data = XMLElement('file')
        data.setHead(self.xmlHead)

        data.addChild(XMLElement('displayName').addChild(XMLTextNode(filename)))
        data.addChild(XMLElement('mediaType').addChild(XMLTextNode(media)))

        response = self.sendRequest('/folder/%s' % path, data.toString(), False)
        if response is not None:
            info = response.info()
            code = response.getcode()
            location = info['Location']
            if code == 201:
                self.addElementToDatabase('%s/%s' % (path, filename), location)
                print('File created with success. Location: %s' % location)
            else:
                print('File could not be deleted (Code: %s)!' % (code))

    def renameFile(self, path, newname):
        data = XMLElement('file')
        data.setHead(self.xmlHead)

        data.addChild(XMLElement('displayName').addChild(XMLTextNode(newname)))

        resp, content = self.sendRequestPut('/file/%s' % path, data.toString())

        if resp is not None:
            if int(resp['status']) == 200:
                print('File renamed.')
            else:
                print('File could not be renamed (Code: %s)!' % (resp['status']))

    def moveFile(self, file, newpath):
        data = XMLElement('file')
        data.setHead(self.xmlHead)

        data.addChild(XMLElement('ParentCollection').addChild(XMLTextNode(newpath)))

        resp, content = self.sendRequestPut('/file/%s' % file, data.toString())
        
        if resp is not None:
            if int(resp['status']) == 200:
                print('File moved.')
            else:
                print('File could not be moved (Code: %s)!' % (resp['status']))

    def getFileInfo(self, filename):
        pass
    
    def getFile(self, filename, saveto):
        response = self.sendRequest('/file/%s/data' % filename, {}, True, False)

        if response is not False:
            info = response.info()
            code = response.getcode()
            data = response.read().decode('utf8')

            if code == 200:
                # now write
                try:
                    d = open(saveto, 'w')
                    d.write(data)
                    d.close()

                    print('File downloaded and saved.')
                except:
                    print('File downloaded but not saved.')
            else:
                print('File could not be downloaded (Code: %s)!' % (code))

    def uploadFile(self, file, filename):
        # we will read file
        data = None

        try:
            d = open(file, 'r')
            data = d.read()
        except:
            print('ERROR: File could not been read!')

        if data is not None:
            resp, content = self.sendRequestPut('/file/%s/data' % filename, data)

            if resp is not None:
                if int(resp['status']) == 204:
                    print('File uploaded.')
                else:
                    print('File could not be uploaded (Code: %s)!' % (resp['status']))

    def updateFile(self, filename, name, mediaType, parent = None):
        pass

    def copyFile(self, source, target, name):
        data = XMLElement('fileCopy')
        data.setHead(self.xmlHead)
        data.setAttribute('source', self.apiURL+'/file/'+source)

        data.addChild(XMLElement('displayName').addChild(XMLTextNode(name)))

        response = self.sendRequest('/folder/%s' % target, data.toString())
        
        if response is not None:
            info = response.info()
            code = response.getcode()
            location = info['Location']

            if code == 201:
                self.addElementToDatabase('%s/%s' % (target, name), location)
                print('File copied with sucess. Location: %s' % location)
            else:
                print('File could not be copied (Code: %s)!' % (code))

    def deleteFile(self, filename):
        resp, content = self.sendRequestDelete('/file/'+filename)   

        if resp is not None:
            if int(resp['status']) == 204:
                print('File deleted.')
            else:
                print('File could not be deleted (Code: %s)!' % (resp['status']))

    def createFolder(self, path, foldername):
        data = XMLElement('folder')
        data.setHead(self.xmlHead)

        data.addChild(XMLElement('displayName').addChild(XMLTextNode(foldername)))

        response = self.sendRequest('/folder/%s' % path, data.toString())

        if response is not None:
            info = response.info()
            code = response.getcode()
            location = info['Location']
            if code == 201:
                self.addElementToDatabase('%s/%s' % (path, foldername), location)
                print('Folder created with success. Location: %s' % location)
            else:
                print('Folder could not be deleted (Code: %s)!' % (code))

    def renameFolder(self, path, newfolder):
        data = XMLElement('folder')
        data.setHead(self.xmlHead)

        data.addChild(XMLElement('displayName').addChild(XMLTextNode(newfolder)))

        resp, content = self.sendRequestPut('/folder/%s' % path, data.toString())

        if resp is not None:
            if int(resp['status']) == 204:
                print('Folder renamed.')
            else:
                print('Folder could not be renamed (Code: %s)!' % (resp['status']))

    def getFolderInfo(self, foldername):
        pass

    def deleteFolder(self, foldername):
        resp, content = self.sendRequestDelete('/folder/'+foldername)   

        if resp is not None:
            if int(resp['status']) == 204:
                print('Folder deleted.')
            else:
                print('Folder could not be deleted (Code: %s)!' % (resp['status']))

    def getUser(self): 
        response = self.sendRequest('/user', {}, True, False)

        if response is not None:
            resp = XMLElement.parse(response.read().decode('utf8'))
            self.username = resp.username
            self.nickname = resp.nickname
            self.quotaLimit = resp.quota.limit
            self.quotaUsage = resp.quota.usage
            print("Username:\t", self.username)
            print("Nickname:\t", self.nickname)
            print("Space Limit:\t", self.quotaLimit, "Bytes")
            print("Space Used:\t", self.quotaUsage, "Bytes\n")

    def getWorkspace(self, pcid):
        pass

    def getCollectionContentInfo(self, typ = 'all', start = 0, maxnumber = 500):

        pass

    def getAllFilesCollection(self):
        response = self.sendRequest('/user', {}, True, False)
        
        if response is not None:
            data = XMLElement.parse(response.read().decode('utf8'))
            self.quotaLimit = data.quota.limit
            self.quotaUsage = data.quota.usage
        
            self.folder['workspaces'] = data.workspaces
            self.folder['syncfolders'] = data.syncfolders
            self.folder['deleted'] = data.deleted
            self.folder['magicBriefcase'] = data.magicBriefcase
            self.folder['webArchive'] = data.webArchive
            self.folder['mobilePhotos'] = data.mobilePhotos
            self.folder['albums'] = data.albums
            self.folder['recentactivities'] = data.recentActivities
            self.folder['receivedshares'] = data.receivedShares
            self.folder['publiclinks'] = data.publicLinks
        
            print("Data loaded! \n\n")

class XMLElement:
    
    def __init__(self, name=''):
        self.name = name
        self.attributes = {}
        self.childs = []
        self.childIsText = False
        self.head = None
        self.value = None
        
    def getName(self):
        return self.name
    
    def setHead(self, value):
        self.head = value
        
    def removeHead(self):
        self.head = None
    
    def setAttribute(self, name, value):
        self.attributes[name] = value
    
    def removeAttribute(self, name):
        try:
            del self.attributes[name]
        except:
            print("Element doesn't exist!")
    
    def addChild(self, elm):
        # there can't be more than 1 child if elm == XMLTextNode
        
        self.childs.append(elm)
        
        # we want an dynamic element!
        if elm.getName() is None:
            # this is an XMLTextNode
            self.value = elm.getValue()
        else:
            setattr(self, elm.getName(), elm)
        
        return self # for compact usage
        
    
    def getAttributes(self):
        attr = ''
        for k,f in self.attributes.items():
            attr = attr+' %s="%s"' % (k, f)
    
        return attr
    
    def getChilds(self):
        xml = ''
        for f in self.childs:
            xml = xml+f.toString()
            
        return xml
    
    def toString(self):
        xml = ''
        if self.head is not None:
            xml = self.head
        xml = xml + '<%s%s>%s</%s>' % (self.name, self.getAttributes(), self.getChilds(), self.name)
        
        return xml
    
    @staticmethod
    def parse(data, first = True):
        xmlpar = []
        
        pattern = '<([^<>]+)>(.+)</\\1>'
        m = re.compile(pattern, re.I | re.S)
        
        if m.search(data) is not None:
            xml = m.findall(data)
            for f in xml:
                # 0: key, 1: value
                xmltmp = XMLElement(f[0])
                
                # we need childs!
                ch = XMLElement.parse(f[1], False)
                if ch is not None:
                    for k in ch:
                        xmltmp.addChild(k)
                
                xmlpar.append(xmltmp)
        elif data is not None:
            xmlpar.append(XMLTextNode(data))
        else:
            xmlpar = None
        
        if first and xmlpar is not None and len(xmlpar) == 1:
            xmlpar = xmlpar[0]
        
        return xmlpar
    
    def repr(self):
        self.__repr__(True)
    
    def __repr__(self, ram = False):
        if self.value == None or ram:
            # normal resp
            return "<%s instance at %s>" % (self.__class__,id(self))
        else:
            return self.value
    
class XMLTextNode:
    
    def __init__(self, value=''):
        self.value = value
        
    def getName(self):
        return None
        
    def setValue(self, value):
        self.value = value
        
    def getValue(self):
        return self.value
        
    def toString(self):
        return self.value

class Printer:
    def __init__ (self, PrintableClass):
        for name in dir(PrintableClass):
            if name is not "__abstractmethods__":
                value = getattr(PrintableClass,name)
                if  '_' not in str(name).join(str(value)):
                    print('  .%s: %r' % (name, value))

# auth: https://www.sugarsync.com/developers/rest-api-reference/actions/authorization/index.html
string = '<?xml version="1.0" encoding="UTF-8" ?><authorization><expiration>2010-10-22T02:01:54.964-07:00</expiration><user>https://api.sugarsync.com/user/566494</user></authorization>'
# user info: https://www.sugarsync.com/developers/rest-api-reference/actions/retrievingUserRepresentation/index.html
string = '<?xml version="1.0" encoding="UTF-8"?><user><username>jsmith@sharpcast.com</username><nickname>jsmith</nickname><quota><limit>2000000000</limit> <!-- total storage available to the user, in bytes -->     <usage>345000000</usage>  <!-- total storage in use by the user, in bytes --></quota><workspaces>https://api.sugarsync.com/workspace<workspaces/><syncfolders>https://api.sugarsync.com/folder<syncfolders/></user>'
# file info: https://www.sugarsync.com/developers/rest-api-reference/actions/retrievingFileRepresentation/index.html
string = '<?xml version="1.0" encoding="UTF-8"?><file><displayName>Foo</displayName><size>120233</size><lastModified>2009-09-25T16:49:56.000-07:00</lastModified><timeCreated>2009-09-25T16:49:56.000-07:00</timeCreated><mediaType>image/jpeg</mediaType><presentOnServer>true</presentOnServer><parent>http://api.sugarsync.com/folder/xyzzy</parent><fileData>http://api.sugarsync.com/file/abc123/data</fileData></file>'
# folder info: https://www.sugarsync.com/developers/rest-api-reference/actions/retrievingFolderRepresentation/index.html
# workspace info: https://www.sugarsync.com/developers/rest-api-reference/actions/retrievingWorkspaceRepresentation/index.html
# CollectionContents info: https://www.sugarsync.com/developers/rest-api-reference/actions/retrievingCollectionContentsRepresentation/index.html
# create file: https://www.sugarsync.com/developers/rest-api-reference/actions/CreatingFiles/index.html
# create folder: https://www.sugarsync.com/developers/rest-api-reference/actions/CreatingFolders/index.html
# update folder state: https://www.sugarsync.com/developers/rest-api-reference/actions/updatingFolderState/index.html
# update file info: https://www.sugarsync.com/developers/rest-api-reference/actions/updatingFileInformation/index.html
# delete folder: https://www.sugarsync.com/developers/rest-api-reference/actions/deletingFolders/index.html
# delete file: https://www.sugarsync.com/developers/rest-api-reference/actions/deletingFiles/index.html
# copy file: https://www.sugarsync.com/developers/rest-api-reference/actions/CopyingFiles/index.html
# putting filedata: https://www.sugarsync.com/developers/rest-api-reference/actions/puttingFileData/index.html
# getting filedata: https://www.sugarsync.com/developers/rest-api-reference/actions/gettingFileData/index.html
# files collection: https://www.sugarsync.com/developers/rest-api-reference/actions/allFilesCollection/index.html
# version history: https://www.sugarsync.com/developers/rest-api-reference/actions/versionHistory/index.html
# public link manage: https://www.sugarsync.com/developers/rest-api-reference/actions/publicLinkManagement/index.html
# photo album access: https://www.sugarsync.com/developers/rest-api-reference/actions/photoAlbumAccess/index.html
# image transcoding: https://www.sugarsync.com/developers/rest-api-reference/actions/imageTranscoding/index.html
#resp = XMLElement.parse(string)
#Printer(resp)

ss = SugarSync()
