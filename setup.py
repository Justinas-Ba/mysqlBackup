  
from setuptools import setup

setup(name = 'mysqlbackups',
    version = '1',
    description = 'Make mysql backup',
    author = 'Justinas',
    author_email = 'justas147@gmail.com',
    url = 'https://github.com/Justinas-Ba/mysqlBackup.git',
    install_requires = [
        'boto3',
        'cryptography'],
)
