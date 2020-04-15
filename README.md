# mysqlBackup script
# Purpose: Script to perform mysql backup

This is python script to perform mysql backup.
It uses mysqldump utility, and backups up all databases.
After backup is done it can be encrypted and  uploaded to Amazon S3 storage.

Since script uses msyqldump utility make sure mysql binaries are added to OS Path.
If not, please create symbolic links.

Copy python script backup.py and configuration files (credentials.json, inputParameters.json)
to working directory. Please modify configuration files according to you setup and requirements.

# Security:

Since connection keys, user, password are used in credentials.json file please restrict access to this
file only to dedicated user or groups.
It is strongly recommended to run this script using dedicated service user.

# How to use script:

From command line shell launch script using parameters:

"python backup.py --action start --upload"
or 
"python backup.py --action start"

# Help page:

1. How to make backup:
    This is command line script. Please execute it from shell console:
    "python backup.py --action start"

2. How to upload backup to cloud:
    "python backup.py --action start --upload"

3. How to stop backup:
    "python backup.py --action stop"

4. How to install dependencies
    This scirpt uses libraries that are not included in Python standard package.
    Please install libraries using pip:

    "pip install boto3"
    "pip install cryptography"

usage: backup.py [-h] [--cfg CFG] [--creds CREDS] [--upload] --action
                 {start,stop,progress}

optional arguments:
  -h, --help            show this help message and exit
  --cfg CFG             input parameters .json file with full path
  --creds CREDS         credentials .json file with full path
  --upload              upload backup to objet storage S3
  --action {start,stop,progress}


