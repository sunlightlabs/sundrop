from fabric.api import sudo, task
from fabric.contrib.files import append
from .utils import add_ebs

@task
def mongodb(size_gb, replset=None):
    add_ebs(size_gb, '/var/lib/mongodb/')
    sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
    append('/etc/apt/sources.list.d/mongo.list',
     'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen',
           use_sudo=True)
    sudo('apt-get update')
    sudo('apt-get install -y mongodb-10gen')
    if replset:
        append('/etc/mongodb.conf', 'replSet = {0}'.format(replset),
               use_sudo=True)
    sudo('restart mongodb')

    # add arbiter

@task
def munin(munin_local_ip, munin_host):
    sudo('apt-get install -y munin-node')
    # edit local /etc/munin/munin-node.conf to allow access from munin
    append('/etc/munin/munin-node.conf', 'allow {0}'.format(munin_local_ip),
           use_sudo=True)
    sudo('restart munin-node')
    # add a file to munin:/etc/munin/munin-conf.d
    # """[openstates;atlanta]\n    address 10.118.193.75"""

