#!/usr/bin/env python
"""
Use bellow commands to install libraries:

pip install boto3
pip install cryptography

"""

import cryptography, json, os, sys, subprocess, time, argparse
import boto3
from botocore.exceptions import *
from cryptography.fernet import Fernet

FLAGFILE = 'progress.file'

def getHelp():
    with open("helpPage.txt", 'r') as helpPage:
        print(helpPage.read())

def setFileFlag(controlFlag):

    """
    Creates and sets Backup control file
    """
    if controlFlag:
        with open(FLAGFILE, "w") as f:
            f.write('Backup is running')
    else:
        if os.path.isfile(FLAGFILE):
            os.unlink(FLAGFILE)

def isflagSet():
    """
    Checks if backup process file is set
    """
    return os.path.isfile(FLAGFILE)


def makeBakup(params, credentials):

    """
    Backup function takes two input parameter files: 
    - inputParamters.json with mysql backup options
    - credentials.json with username and password strings

    Uses mysqldump utility and returns backupFile object

    """

    mysqlUser = credentials.get('mysqlUser')
    mysqlPass = credentials.get('mysqlPassword')
    hostname = params.get('mysqlHost')
    BackupOutput = params.get('OutputLocation')

    try:
        timestamp = str(int(time.time()))
        backupProcess = subprocess.Popen("mysqldump -h" + hostname + " -u" + mysqlUser + " -p" + mysqlPass +
            " --all-databases >" + BackupOutput +"/" + hostname + "_" + timestamp + ".sql", shell=True)
        # Allow backup process to run. Read all input and output
        backupProcess.communicate()
        # Check if backup completed succesfully
        if(backupProcess.returncode != 0):
            print("Backup failed")
        print("Backup completed succesfully") 
        backupFile = BackupOutput +"/" + hostname + "_" + timestamp + ".sql"
        print("Backup file: " +str(backupFile))
        return backupFile
    except Exception as e:
        print("An error occured: " +str(e))
        raise e


def encryptBackup(backupFile,creds):

    """

    EncryptBackup functions uses Fernet encryption module.
    Is is symetric encryption function which uses AES algorithm.
    If key is not provided it generates and stores encryption key.
    Function takes two input parameters:
    - backupFile object, which  is passed to encryption functions
    - credentials file which was provided in command line by user

    Returns encrypted backup file object
    """
    # try to get encryption key
    try:
        credentials = getParams(creds)
        encryptionKeyFile = credentials.get('encryptionKey', False)
        print("Using EncryptionKeyFile: "+str(encryptionKeyFile))
        # Check if encryption file path is provided and exists 
        if ((not encryptionKeyFile) or not os.path.exists(encryptionKeyFile)):
            print("Encryption key not available. Creating new encryption key")
            createKey()
            encryptionKeyFile = "encryptionKey.key"
            # Update .json file with new key
            print("Updating credentials  .json file with new key file")
            with open(creds, "r") as inputFile:
                params = json.load(inputFile)
            params['encryptionKey'] = encryptionKeyFile
            with open(creds, "w") as inputFile:
                json.dump(params, inputFile)
            print("credentials .json file updated")
        # Encryption key file  is loaded as Fernet key
        encryptionKey = loadKey(encryptionKeyFile)
        print("Encryption keys are loaded")
        # Get Fernet encryption function
        encryptionFunction = Fernet(encryptionKey)
        print("Encryption function is loaded")
        print("Reading and encrypting backup file")
        with open(backupFile, "rb") as bkpFile:
            bkpFileData = bkpFile.read()
            bkpFile.close()
        encryptedBkpFile = encryptionFunction.encrypt(bkpFileData)
        # Overwrite file with encrypted data
        with open(backupFile, "wb") as newFile:
            newFile.write(encryptedBkpFile)
            newFile.close()
        print("Backup file encrypted succesfully")
        return backupFile
    except Exception as e:
        print("An error occured while encrypting backup. Please check if encryption key file is valid")
        print(str(e))
        raise e
    

def loadKey(encryptionKeyFile):

    """
    loads provided encryption key file
    """
    print("Loading Encryption key file")
    return open(encryptionKeyFile, "rb").read()

def createKey():
    
    """

    Function creates Fernet encryption key for encrypting backup file
    Fernet encryption key is used in encryption function
    Key is created and stored in encryptionKey.key file 
    """
    try:
        print("creating encryption key...")
        encKey = Fernet.generate_key()
        with open("encryptionKey.key", "wb") as encryptionKey:
            encryptionKey.write(encKey)
            encryptionKey.close()   
    except Exception as e:
        print("An error occured while creating an Encryption key: " +str(e))
        raise e

def uploadtoCloud(encryptedBackupFile, creds):
    
    """
    Function uploads encrypted backup file to AWS S3
    Reads credentials .json file for connection parameters
    Returns True if upload was succesfull
    """
    
    # Reads credentials file and aquires connection keys
    credentials = getParams(creds)
    access_key = credentials.get("S3_access_key", False)
    secret_key = credentials.get("S3_secret_key", False)
    bucket_name = credentials.get("S3_bucket_name", False)
    
    # Proceed only if credentials are provided
    # Does not check credentials validity

    if (access_key and secret_key and bucket_name): 
        s3 = boto3.client('s3')
        try:
            with open(encryptedBackupFile, 'rb') as data:
                s3FileName = os.path.basename(encryptedBackupFile)
                s3.upload_fileobj(data, bucket_name, s3FileName)
                print("Backup file uploaded succesfully")
                return True
        except Exception as e:
            print("An error occured while uploading file" +str(e))
            raise e

def getParams(inputFile):
    """
    Reads .json file as input. Returns dictionary object
    """
    with open(inputFile) as inputFile:
        # json will be converted to dictionary object
        params = json.load(inputFile)
        return params

def main(argv=sys.argv[1:]):

    """
    Entry function for Backup script.
    Helper functions are invoked accordingly:
        makeBackup, encryptBackup, uploadtoCloud
    
    Uses argparse module to parse command line arguments
    """
    
    # Set command line paramters using argparse module
    parser = argparse.ArgumentParser(description=getHelp())
    #parser = argparse.ArgumentParser(description='MySQL backup tool')
    parser.add_argument("--cfg", required=False, default= "inputParameters.json", type=str, help="input parameters .json file with full path")
    parser.add_argument("--creds", required=False, default= "credentials.json", type=str, help="credentials .json file with full path")
    parser.add_argument("--upload", required=False, action="store_true", help="upload backup to objet storage S3")
    parser.add_argument("--action", required=True, choices=["start", "stop", "progress"], 
                        type=str, help="Backup process control options")

    # Initialize command line parameters
    args = parser.parse_args()
    cfg = args.cfg
    creds = args.creds
    upload = args.upload
    action = args.action

    if action == 'start':
        print ("Starting Backup script")
        setFileFlag(True)

    if action == 'stop':
        if isflagSet():
            print ("Stopping backup script")
            setFileFlag(False)
            sys.exit()
        else:
            print ("Backup is not running. Please start backup")
            sys.exit()

    if action == 'progress':
        if isflagSet():
            print("Backup is running")
            sys.exit()
        else:
            print ("Backup is not running")
            sys.exit()
    
    while isflagSet():
        try:
            """
            If configuration and credentials files were passed program starts backup process
            """
            if (cfg and creds): 
                try:
                    print("Reading input files")
                    params = getParams(cfg)
                    credentials = getParams(creds)
                except Exception as e:
                    print("An error occurred while reading file. Please check file/file path")
                    raise Exception("There is an error: {}".format(e))
                    #sys.exit(1)
                print("Reading configuration and credentials file completed")
                print("Starting mysql backup with input parameters")
                backupCompleted = False
                # backupStarted = False -> not used in this release
                try:
                        backupFile = makeBakup(params, credentials)
                        print("mysql backup completed succesfully")
                        setFileFlag(False)
                        backupCompleted = True
                        # backupStarted = False -> not used in this release

                except Exception as e:
                    print("An error occured while performing backup")
                    # backupStarted = False -> not used in this release
                    raise Exception("There is an error: {}".format(e))
                    #sys.exit(str(e))

            """
            If upload flag is set Backup file will be encrypted and uploaded to cloud storage
            """  
            if  (backupCompleted and upload):
                print("Starting encryption process before uploading")
                try:
                    encryptedBackupFile = encryptBackup(backupFile,creds)
                    if uploadtoCloud(encryptedBackupFile, creds):
                        print("Backup script completed. Exiting ...")
                        setFileFlag(False)
                        sys.exit(0)
                except Exception as e:
                    print("An error occured:" +str(e))
                    raise e
            else:
                sys.exit(0)
                break     
        except Exception as e:
            # backupStarted = False -> not used in this release
            raise e


if __name__=="__main__":
    main()