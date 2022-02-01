import pycurl
from io import BytesIO
from webdav3.client import Client
Test mod
class UConnect:
    url = None
    client = None

    def __init__(self, url, username, password, port=21, ftps=False, debugflag=False, mode=1):
        if 'http' in url or 'https' in url:                                 
            options = {
                'webdav_hostname': url,
                'webdav_login':    username,
                'webdav_password': password
            }
            self.client = Client(options)
            self.url = url   
            self.client.verify = False                        
        else:
            self.client = pycurl.Curl()
            self.client.reset()
            self.url = url
            self.client.setopt(pycurl.URL, url)
            self.line = username + ':' + password
            self.client.setopt(pycurl.USERPWD, self.line)
            self.ftps = ftps
            self.port = port
            self.debugflag = debugflag
            self.client.setopt(pycurl.FTP_USE_EPSV, mode)
            if self.ftps:
                self.client.setopt(pycurl.SSL_VERIFYPEER, False)
                self.client.setopt(pycurl.SSL_VERIFYHOST, False)
                self.client.setopt(pycurl.FTP_SSL, pycurl.FTPSSL_ALL)
                self.client.setopt(pycurl.FTPSSLAUTH, pycurl.FTPAUTH_DEFAULT)                
            self.client.setopt(pycurl.PORT, self.port)
            if self.debugflag:
                self.client.setopt(pycurl.VERBOSE, True)
                self.client.setopt(pycurl.DEBUGFUNCTION, self.debug)

    def upload(self, source, destination):
        try:
            url = '/'.join((self.url, destination))
            self.client.setopt(pycurl.URL, url)
            self.client.setopt(pycurl.UPLOAD, True)
            self.client.setopt(pycurl.READFUNCTION,  open(source, 'rb').read)
            self.client.setopt(pycurl.FTP_CREATE_MISSING_DIRS, 1)
            self.client.perform()
        except pycurl.error as ex:
            raise ex
        
    def mkdir(self, foldername):
        try:
            if self.client.check(foldername)==False:                       
              self.client.mkdir(foldername)           
        except pycurl.error as ex:
            raise ex    
        
    def uploadhttp(self, source, destination):
        try:                               
            self.client.upload_sync(remote_path=destination, local_path=source)                     
        except pycurl.error as ex:
            raise ex
                  
    def deletehttp(self,destination):
        try:                                       
            self.client.clean(destination)                     
        except pycurl.error as ex:
            raise ex

    def download(self, source, destination):
        try:
            url = '/'.join((self.url, source))
            self.client.setopt(pycurl.URL, url)
            self.client.setopt(pycurl.WRITEFUNCTION, open(destination, "wb").write)
            self.client.perform()
        except pycurl.error as ex:
            raise ex

    def delete(self, source, tree='D'):
        files = self.list(source)
        if tree == 'D':
            for file in files:
                self.__delete(source + "/" + file)
            command = 'RMD ' + source
            self.client.setopt(pycurl.CUSTOMREQUEST, command)
            try:
                self.client.perform()
            except pycurl.error as ex:
                code = int(self.client.getinfo(pycurl.RESPONSE_CODE))
                if code != 250:
                    raise ex
        elif tree == 'F':
            self.__delete(source)
        self.client.close()

    def __delete(self, source):
        try:
            command = 'DELE ' + source
            self.client.setopt(pycurl.CUSTOMREQUEST, command)
            try:
                self.client.perform()
            except pycurl.error as ex:
                code = int(self.client.getinfo(pycurl.RESPONSE_CODE))
                if code != 250:
                    raise ex
        except Exception as ex:
            raise ex

    def close(self):
        self.client.close()

    def reset(self):
        self.client.reset()

    def debug(self, detype, demsg):
        print(demsg)

    def list(self, source):
        try:
            buffer = BytesIO()
            command = 'LIST ' + source
            self.client.setopt(pycurl.CUSTOMREQUEST, command)
            self.client.setopt(pycurl.WRITEDATA, buffer)
            try:
                self.client.perform()
            except pycurl.error as ex:
                code = int(self.client.getinfo(pycurl.RESPONSE_CODE))
                if code != 250:
                    raise ex
                return True
            result = buffer.getvalue().decode()
            lines = result.splitlines()
            data = []
            for line in lines:
                if line != '':
                    parts = line.split()
                    if not parts[-1].startswith('.'):
                        data.append(parts[-1])
            return data
        except Exception as ex:
            raise ex

    def reconnect(self, mode=1):
        self.client.close()
        self.client = pycurl.Curl()
        self.client.setopt(pycurl.URL, self.url)
        self.client.setopt(pycurl.USERPWD, self.line)
        self.client.setopt(pycurl.FTP_USE_EPSV, mode)
        if self.ftps:
            self.client.setopt(pycurl.SSL_VERIFYPEER, False)
            self.client.setopt(pycurl.SSL_VERIFYHOST, False)
            self.client.setopt(pycurl.FTP_SSL, pycurl.FTPSSL_ALL)
            self.client.setopt(pycurl.FTPSSLAUTH, pycurl.FTPAUTH_DEFAULT)
        self.client.setopt(pycurl.PORT, self.port)
        if self.debugflag:
            self.client.setopt(pycurl.VERBOSE, True)
            self.client.setopt(pycurl.DEBUGFUNCTION, self.debug)
