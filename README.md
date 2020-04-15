# mysql database backup script
# Purpose and description 

This is python script to perform mysql backup and upload to S3 storage.
It uses mysqldump utility, and backups up all databases.
After backup is done it can be encrypted and uploaded to Amazon S3 storage.
Note: please see flags

Since script uses msyqldump utility make sure mysql binaries are available and added to OS Path.
If not, please create symbolic links.

You can call this script from any server which has mysqldump utility and direct connection
to mysql database server on default TCP port 3306.

Copy python script backup.py and configuration files (credentials.json, inputParameters.json)
to working directory. Please modify configuration files according to you setup and requirements.

# Security:

Since connection keys, user, password are used in credentials.json file please restrict access to this
file only to dedicated user or groups.
It is strongly recommended to run this script using dedicated service user.

# Mysql setup

Please follow mysql user guide how to setup dedicatedbackup user and grant relevant credentials.
Please allow connections on TCP port 3306.
Please update input .json files accordingly

# How to install script

    1. Download packages and extract to working directory
     - It is also possible to use git clone:
        
        git clone https://github.com/Justinas-Ba/mysqlBackup.gi
    
    2. change directory to working directory.
    3. Since setup.py file is prepared you can install script using pip:
        
        pip install .
    
    4. This will install required libraries
    5. You can now run backup script

# How to install dependencies manually

This scirpt uses libraries that are not included in Python standard library.
Please install libraries using pip:

    "pip install boto3"
    "pip install cryptography"

# How to use script:

From command line shell launch script using parameters:

    "python backup.py --action start --upload"
    or 
    "python backup.py --action start"
    
    Launc script in silent mode:
    "python backup.py --action start &"

# Help page:

1. How to make backup:
    This is command line script. Please execute it from shell console:
    "python backup.py --action start"

2. How to upload backup to cloud:
    "python backup.py --action start --upload"

3. How to stop backup:
    "python backup.py --action stop"

usage: backup.py [-h] [--cfg CFG] [--creds CREDS] [--upload] --action
                 {start,stop,progress}

optional arguments:
  -h, --help            show this help message and exit
  --cfg CFG             input parameters .json file with full path
  --creds CREDS         credentials .json file with full path
  --upload              upload backup to objet storage S3
  --action {start,stop,progress}


