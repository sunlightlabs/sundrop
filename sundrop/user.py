from fabric.api import sudo, task
from .utils import copy_dir

@task
def add(user):
    """ create a new user with sudo rights """
    sudo('useradd {0} --base-dir /etc/skel --home-dir /home/{0} --create-home '
         '--shell /bin/bash --groups admin'.format(user))
    sudo('passwd {0}'.format(user))
    copy_dir('_users/{0}/'.format(user), '/home/{0}/'.format(user), user)
