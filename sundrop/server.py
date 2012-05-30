"""
    server-specific sundrop tasks
"""
from fabric.api import sudo, task
from fabric.contrib.files import append

@task
def hostname(hostname):
    append('/etc/hosts', '127.0.0.1 {0}'.format(hostname), use_sudo=True)
    sudo('echo "{0}" > /etc/hostname'.format(hostname))
    sudo('start hostname')

@task
def meet(hostname, ip):
    append('/etc/hosts', '{0} {1}'.format(ip, hostname), use_sudo=True)

@task
def install_packages(*roles):
    packages = {'core': ('xfsprogs', 'build-essential', 'git', 'mercurial',
                         'munin-node'),
                'python': ('python-dev', 'python-virtualenv', 'nginx', 'uwsgi',
                           'uwsgi-plugin-python'),
               }
    sudo('aptitude update')
    sudo('aptitude upgrade')
    for role in roles:
        sudo('aptitude install -y {0}'.format(' '.join(packages[role])))


@task
def init(name, *roles):
    hostname(name)
    install_packages(*roles)
