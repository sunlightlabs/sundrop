from fabric.api import sudo, task
from fabric.contrib.files import append
from .utils import add_ebs

@task
def mongodb(size_gb):
    add_ebs(size_gb, '/var/lib/mongodb/')
    sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
    append('/etc/apt/sources.list.d/mongo.list',
     'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen',
           use_sudo=True)
    sudo('apt-get update')
    sudo('apt-get install -y mongodb-10gen')
