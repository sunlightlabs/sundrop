"""
    server-specific sundeploy tasks
"""
from fabric.api import sudo, task
from fabric.contrib.files import append

@task
def set_hostname(hostname):
    append('/etc/hosts', '127.0.0.1 {0}'.format(hostname), use_sudo=True)
    sudo('echo "{0}" > /etc/hostname'.format(hostname))
    sudo('start hostname')

@task
def install_base_packages():
    packages = ('xfsprogs', 'python-dev', 'build-essential',
                'git', 'python-virtualenv', 'nginx', 'uwsgi',
                'uwsgi-plugin-python', 'python-psycopg2')
    sudo('aptitude update')
    sudo('aptitude install {0}'.format(' '.join(packages)))
