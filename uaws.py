import boto3
import logging
import botocore
from .uconfig import Uconfig
import os


class UAws:
    """
        This is the base class to connect to AWS API
        author      Vandana Vasudevan <vandana.vasudevan@drd.co.in>
        license     Uboss License 1.0 This is a private property of DRD Communications & Software Pvt Ltd, India.(DRDINDIA)
        copyright   2018 DRDINDIA, All Rights Reserved
        version     $Id: ulog.py 35458 2019-12-06 09:27:37Z ralaad.pr $
        """

    FOLDER_DEFAULT = 0
    FOLDER_BUSINESSNOTE = 1
    FOLDER_COMPANYLOGO = 2
    FOLDER_COMPANYBANNER = 3
    FOLDER_DEVICELOGO = 4
    FOLDER_FEATUREREQUEST = 5
    FOLDER_PORTALUSER = 6
    FOLDER_INVOICELOGO = 8
    FOLDER_NOTIFICATION = 9
    FOLDER_TICKET = 16
    FOLDER_RELEASENOTE = 21
    FOLDER_BULKJOB = 23
    FOLDER_ANNOUNNCEMENTREPOSITORY = 24
    FOLDER_NUMBERPORT = 26
    FOLDER_ADHOC= 27
    FOLDER_UNITYLOGO = 28
    FOLDER_FTPPULLER = 30
    FOLDER_TEMPLATE_DOCUMENT = 31

    
    def __init__(self):
        self.config = Uconfig()
        self.s3client = None
        self.bucket = self.config.config['awss3']['bucket']
        self.connect()

    def connect(self):
        """This function is used to connect to AWS.
        created by  Vandana Vasudevan<vandanavasudevan@drd.co.in>
        created on  26-Apr-2021 """
        logging.getLogger("botocore").setLevel(logging.WARNING)
        logging.getLogger("s3transfer").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        self.s3client = boto3.client(
            's3',
            region_name=self.config.config['awss3']['region'],
            aws_access_key_id=self.config.config['awss3']['accesskey'],
            aws_secret_access_key=self.config.config['awss3']['secretkey']
        )

    def download(self, source, destination):
        """This function is used to download file from AWS.
        created by  Vandana Vasudevan<vandanavasudevan@drd.co.in>
        created on  26-Apr-2021 """
        try:
            return self.s3client.download_file(self.bucket, source, destination)
        except Exception as ex:
            raise ex

    def upload(self, source, destination, extra_args):
        """This function is used to upload to AWS.
        created by  Vandana Vasudevan<vandanavasudevan@drd.co.in>
        created on  26-Apr-2021 """
        try:
            return self.s3client.upload_file(source, self.bucket, destination, extra_args)
        except Exception as ex:
            raise ex

    def getlist(self, prefix, company_type, company_id, folder_id):
        try:
            prefix = self.getkey(prefix, company_type, company_id, folder_id)
            result = self.s3client.list_objects(Bucket=self.bucket, Prefix=prefix, Delimiter='/')
            if 'Contents' in result:
                return result['Contents']
            return []
        except Exception as ex:
            raise ex

    def delete(self):
        pass

    def isexist(self, key):
        try:
            self.s3client.head_object(Bucket=self.bucket, Key=key)
        except botocore.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == "404":
                status = False
            else:
                raise ex
        else:
            status = True
        return status
            
    def getkey(self, file_name, company_type, company_id, folder_id):
        """This function is used to get fle location.
        created by  Jilcy T j<jilcy.tj@drd.co.in>
        created on  03-Sep-2021 """
        try:
            foldername = {
                0: 'default',
                1: 'business-note',
                2: 'company-logo',
                3: 'company-banner',
                4: 'device-logo',
                5: 'feature-request',
                6: 'portal-user',
                8: 'invoice-logo',
                9: 'notification',
                16: 'ticket',
                21: 'release-note',
                23: 'bulk-job',
                24: 'announcement-repository',
                26: 'number-port',
                27: 'ad-hoc',
                28: 'unity-logo',
                30: 'ftp-puller',
                31: 'cdr-template'
            }

            companytypes = {
                0: 'system',
                1: 'platform-owner',
                2: 'distributor',
                3: 'reseller',
                4: 'business',
                5: 'site',
                6: 'user'
            }
            if company_type == 0:
                return companytypes[company_type] + "/" + foldername[folder_id] + "/" + file_name
            else:
                return companytypes[company_type] + "/" + str(company_id) + "/" + foldername[folder_id] + "/" + file_name
        except Exception as ex:
            raise ex

    def getlocalfilepath(self, file_name):
        """This function is used to get temp fle location.
        created by  Archana Gopal<archana.gopal@drd.co.in>
        created on  18-Oct-2021 """
        try:
            tempfolder_path = self.config.config['settings']['rootpath'].rstrip('/') + "/temp/image/"
            if os.path.exists(tempfolder_path):
                tempfile_path = tempfolder_path + file_name
                if os.path.exists(tempfile_path):
                    os.remove(tempfile_path)
                return tempfile_path
            else:
                raise FileNotFoundError('Path (' + tempfolder_path + ') not found')
        except Exception as ex:
            raise ex


