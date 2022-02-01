import ssl
import uuid
import socket
import errno
import hashlib
import xmltodict
import time
from .udb import Udb
from .ulog import Ulog
from .ufunctions import exception, keys_exists


class UBroadWorks:
    """
    This is the base calss for all the broadworks services
    author      Renjith Mohan <renjith.mohan@drdindia.co.in>
    license     Uboss License 1.0 This is a private property of DRD Communications & Software Pvt Ltd, India.(DRDINDIA)
    copyright   2018 DRDINDIA, All Rights Reserved
    version     $Id: ubroadworks.py 51136 2020-06-25 09:52:27Z sanal.ks $
    """
    __socket = None
    __session_id = None

    hostname = None
    port = None
    password = None
    broadworksloginid = None
    companyid = None
    companytype = None
    islogined = False
    tlsenabled = False
    timeout = 60
    log = Ulog('uboss')

    def __init__(self):
        pass

    @classmethod
    def connect(cls, hostname, port=80):
        try:
            starttime = time.time()
            try:
                hostip = socket.gethostbyname(hostname)
            except:
                hostip = hostname
            context = None
            if cls.tlsenabled:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = 0
            UBroadWorks.__socket = socket.create_connection((hostip, port),cls.timeout)
            if cls.tlsenabled:
                UBroadWorks.__socket = context.wrap_socket(UBroadWorks.__socket, server_hostname=hostname)
            af = UBroadWorks.__socket.family
            file = UBroadWorks.__socket.makefile('rb')
            later = time.time()
            difference = int(later - starttime)
            cls.log.info("Broadworks connect : Time taken: " + str(difference))
            return True 
        except Exception as ex:
            cls.log.error(exception())
            raise ex

    @classmethod
    def basexml(cls, requestname, commandxml):
        try:
            if UBroadWorks.__socket is not None:
                if UBroadWorks.__session_id is None:
                    UBroadWorks.__session_id = uuid.uuid4()
                requestname = str(requestname)
                request = '<?xml version="1.0" encoding="ISO-8859-1" ?>' \
                          '<BroadsoftDocument protocol="OCI" xmlns="C">' \
                          '<sessionId xmlns="">' + str(UBroadWorks.__session_id) + '</sessionId>' \
                          '<command echo="' + requestname + '" xsi:type="' + requestname + '" ' \
                          'xmlns="" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'\
                          + str(commandxml) + \
                          '</command></BroadsoftDocument>'
                return request.encode()
            else:
                raise ConnectionError('Socket connection closed')
        except Exception as ex:
            cls.log.error(exception())
            raise ex

    @classmethod
    def sendrequest(cls, request):
        try:
            if UBroadWorks.__socket is not None:
                cls.logprovision('(client to server)' + str(request))
                try:
                    UBroadWorks.__socket.sendall(request)
                except socket.error as ex:
                    if ex.errno != errno.EPIPE:
                        raise ex
                    cls.log.error("Broken pipe error occured, trying to reconnect")
                    cls.connect(UBroadWorks.hostname, UBroadWorks.port)
                    request = cls.basexml('AuthenticationRequest', '<userId>' + UBroadWorks.broadworksloginid + '</userId>')
                    response = cls.sendrequest(request)
                    nonce = response['BroadsoftDocument']['command']['nonce']
                    if nonce:
                        group = nonce + ':' + hashlib.sha1(UBroadWorks.password.encode()).hexdigest()
                        signedpassword = hashlib.md5(group.encode()).hexdigest()
                        request = cls.basexml('LoginRequest14sp4', '<userId>' + UBroadWorks.broadworksloginid + '</userId><signedPassword>'
                                              + signedpassword + '</signedPassword>')
                        response = cls.sendrequest(request)
                        logintype = response['BroadsoftDocument']['command']['loginType']
                        if logintype:
                            cls.islogined = True
                        else:
                            cls.islogined = False
                    if cls.islogined:
                        cls.log.error("Broken pipe error occured and reconnected successfully")
                    else:
                        cls.log.error("Broken pipe error occured and not able to reconnect")
                        raise ex
                    UBroadWorks.__socket.sendall(request)
                response = b''
                while True:
                    packet = UBroadWorks.__socket.recv(2048)
                    response += packet
                    if response.find(b'</BroadsoftDocument>') != -1:
                        break
                cls.logprovision('(server to client)' + str(response.decode("utf-8").strip()))
                return cls.response(response.decode("utf-8").strip())
            else:
                raise ConnectionError('Socket connection closed')
        except Exception as ex:
            cls.log.error(exception())
            raise ex

    @classmethod
    def close(cls):
        UBroadWorks.__socket.close()
        UBroadWorks.__session_id = None
        UBroadWorks.__socket = None
        UBroadWorks.hostname = None
        UBroadWorks.port = None
        UBroadWorks.password = None
        UBroadWorks.broadworksloginid = None
        UBroadWorks.companyid = None
        UBroadWorks.companytype = None
        cls.islogined = False

    @classmethod
    def response(cls, xml):
        try:
            return xmltodict.parse(xml)
        except Exception as ex:
            cls.log.error(exception())
            raise ex

    @classmethod
    def geterror(cls, response):
        error = None
        if keys_exists(response['BroadsoftDocument']['command'], '@type'):
            if response['BroadsoftDocument']['command']['@type'] == 'Error' or response['BroadsoftDocument']['command']['@type'] == 'Warning':

                if keys_exists(response['BroadsoftDocument']['command'], 'detail'):
                    error = "[BW-ERROR] " + response['BroadsoftDocument']['command']['summary'] + ". " + response['BroadsoftDocument']['command']['detail']
                else:
                    error = "[BW-ERROR] " + response['BroadsoftDocument']['command']['summary']
        return error

    @classmethod
    def logprovision(cls, log):
        try:
            udb = Udb(True)
            udb.execute("AddProvisionLog @level=?, @servername=?, @broadworksloginid=?, @message=?, @exception=?, @portaluserid=?, @CompanyId=?, @CompanyType=?", ['info', UBroadWorks.hostname, UBroadWorks.broadworksloginid, log, '', 0,
                                                                                                                                                                   UBroadWorks.companyid, UBroadWorks.companytype])
        except Exception as ex:
            raise ex

