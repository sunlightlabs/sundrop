from fabric.api import sudo, task
from fabric.contrib.files import append
from .utils import add_ebs

@task
def mongodb(size_gb, replset=None, iops=400):
    add_ebs(size_gb, '/var/lib/mongodb/', iops=iops)
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

    # add arbiter?

@task
def jenkins(size_gb):
    add_ebs(size_gb, '/var/lib/jenkins/')
    sudo('wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -')
    append('/etc/apt/sources.list.d/jenkins.list',
           'deb http://pkg.jenkins-ci.org/debian binary/', use_sudo=True)
    sudo('apt-get update')
    sudo('apt-get install -y openjdk-6-jre openjdk-6-jdk jenkins')

@task
def munin(munin_local_ip, munin_host):
    sudo('apt-get install -y munin-node')
    # edit local /etc/munin/munin-node.conf to allow access from munin
    append('/etc/munin/munin-node.conf', 'allow {0}'.format(munin_local_ip),
           use_sudo=True)
    sudo('restart munin-node')
    # add a file to munin:/etc/munin/munin-conf.d
    # """[openstates;atlanta]\n    address 10.118.193.75"""

