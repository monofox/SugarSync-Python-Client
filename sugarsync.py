#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import re
import ConfigParser
import datetime

class SugarSync:
    def __init__(self):
        # TODO all should be layed out!
        self.username = 'lukas.schreiner@gmail.com'
        self.password = ''
        self.accessKeyId = ''
        self.privateAccessKey = ''
        self.apiURL = 'https://api.sugarsync.com'
        self.token = None
        self.tokenExpire = None
        self.xmlHead = '<?xml version="1.0" encoding="UTF-8" ?>'
        self.config = None

        self.readConfig()

        self.auth()

        self.writeConfig()
    
    def readConfig(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(['config.ini'])

        self.username = self.config.get('user', 'username')
        self.password = self.config.get('user', 'password')
        self.accessKeyId = self.config.get('connection', 'accessKeyId')
        self.privateAccessKey = self.config.get('connection', 'privateAccessKey')
        self.apiURL = self.config.get('connection', 'url')

        self.token = self.config.get('auth', 'token')
        self.tokenExpire = self.config.get('auth', 'tokenExpire')

    def writeConfig(self):
        self.config.set('user', 'username', self.username)
        self.config.set('user', 'password', self.password)
        self.config.set('connection', 'accessKeyId', self.accessKeyId)
        self.config.set('connection', 'privateAccessKey', self.privateAccessKey)
        self.config.set('connection', 'url', self.apiURL)
        self.config.set('auth', 'token', self.token)
        self.config.set('auth', 'tokenExpire', self.tokenExpire)

        with open('config.ini', 'wb') as configfile:
            self.config.write(configfile)

    def sendRequest(self, path, data):
        response = None

        try:
            request = urllib2.Request(self.apiURL+path, data, {'Content-type': 'application/xml; charset=UTF-8'})
            response = urllib2.urlopen(request)
        except urllib2.URLError as e:
            print 'Error while requesting API call: %s' % (e.reason)
            
        return response
    
    def parseDate(self, date):
        pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})T([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2})\.([0-9]{1,3})((\-|\+)([0-9]{1,2})):([0-9]{1,2})'
        m = re.compile(pattern)

        match = m.match(date)
        if match is not None:
            year = match.group(1)
            month = match.group(2)
            day = match.group(3)
            hour = match.group(4)
            minute = match.group(5)
            second = match.group(6)
            offsetOperand = match.group(9)
            offsetMulti = offsetOperand+'1'
            offsetHour = match.group(10)
            offsetMinute = match.group(11)

            # now correct hour
            hour = hour+offsetHour*offsetMulti
            minute = minute+offsetMinute*offstMulti

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

    def authOkay(self):
        # check whether token is expired or not!


    def auth(self):
        data = XMLElement('authRequest')
        data.setHead(self.xmlHead)

        data.addChild(XMLElement('username').addChild(XMLTextNode(self.username)))
        data.addChild(XMLElement('password').addChild(XMLTextNode(self.password)))
        data.addChild(XMLElement('accessKeyId').addChild(XMLTextNode(self.accessKeyId)))
        data.addChild(XMLElement('privateAccessKey').addChild(XMLTextNode(self.privateAccessKey)))
        
        response = self.sendRequest('/authorization', data.toString())
        info = response.info()
        self.token = info['Location']
        resp = XMLElement.parse(response.read())
        self.tokenExpire = resp.expiration

        
    def getFileInfo(self, filename):
        pass
    
    def getFile(self, filename):
        pass

    def uploadFile(self, filename):
        pass

    def updateFile(self, filename, name, mediaType, parent = None):
        pass

    def copyFile(self, src, tar, name):
        pass

    def deleteFile(self, filename):
        pass

    def createFolder(self, foldername):
        pass

    def renameFolder(self, foldername, newfolder):
        pass

    def getFolderInfo(self, foldername):
        pass

    def deleteFolder(self, foldername):
        pass

    def getUser(self):
        pass

    def getWorkspace(self, pcid):
        pass

    def getCollectionContentInfo(self, typ = 'all', start = 0, maxnumber = 500):
        pass




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
            print "Element doesn't exist!"
    
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
        for k,f in self.attributes:
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
                    print '  .%s: %r' % (name, value)

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
