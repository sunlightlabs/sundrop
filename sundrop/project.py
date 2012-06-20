import os
import time
from fabric.api import (local, sudo, run, env, cd, put, get, settings,
                        hide, abort, puts, task)
from fabric.colors import red, green
from fabric.contrib.files import append, contains, exists
import boto

from .utils import copy_dir
from .server import meet

@task
def install_extra_packages():
    packages = env.proj.get('extra_packages', None)
    if packages:
        sudo('aptitude update')
        sudo('aptitude install -y {0}'.format(' '.join(packages)))

@task
def add_related_servers():
    for hostname, ip in env.proj.get('related_servers', {}).iteritems():
        meet(hostname, ip)

def _get_ec2_metadata(type):
    with hide('running', 'stdout',  'stderr'):
        r = sudo('wget -q -O - http://169.254.169.254/latest/meta-data/{0}'.format(type))
        return r

@task
def add_user_ebs():
    add_ebs(env.proj['ebs_size_gb'],
            '/projects/{0}'.format(env.projname))
    sudo('useradd {0} --home-dir /projects/{0} --base-dir /etc/skel --shell /bin/bash'.format(env.projname))
    # chown it all
    sudo('chown {0}:{0} /projects/{0}'.format(env.projname))


def add_ebs(size_gb, path):
    ec2 = boto.connect_ec2(env.AWS_KEY, env.AWS_SECRET)
    # get ec2 metadata
    zone = _get_ec2_metadata('placement/availability-zone')
    instance_id = _get_ec2_metadata('instance-id')

    # create and attach drive
    volume = ec2.create_volume(size_gb, zone)

    # figure out where drive should be mounted
    letters = 'fghijklmnopqrstuvw'

    for letter in letters:
        drv = '/dev/xvd{0}'.format(letter)

        # skip this letter if already mounted
        if contains('/proc/partitions', 'xvd{0}'.format(letter)):
            continue

        # attach the drive, replacing xv with sd b/c of amazon quirk
        volume.attach(instance_id, drv.replace('xv', 's'))
        # break if we suceeded
        break
    else:
        # only executed if we didn't break
        abort('unable to mount drive')
        # TODO: ensure drive is cleaned up

    ec2.create_tags([volume.id],
                    {'Name': '{0} for {1}'.format(path, instance_id)})

    puts('waiting for {0}...'.format(drv))
    while not exists(drv):
        time.sleep(1)

    # format and mount the drive
    sudo('mkfs.xfs {0}'.format(drv))
    append('/etc/fstab', '{0} {1} xfs defaults 0 0'.format(drv, path),
           use_sudo=True)

    # make & mount
    sudo('mkdir -p {0}'.format(path))
    sudo('mount {0}'.format(path))



@task
def make_homedir():
    # make subdirs
    sudo('mkdir -p /projects/{0}/logs'.format(env.projname), user=env.projname)
    sudo('mkdir -p /projects/{0}/src'.format(env.projname),  user=env.projname)
    sudo('mkdir -p /projects/{0}/data'.format(env.projname), user=env.projname)
    sudo('mkdir -p /projects/{0}/.ssh'.format(env.projname), user=env.projname)


@task
def make_key():
    sudo("ssh-keygen -t rsa -C '{0} deploy key' -N '' -f /projects/{0}/.ssh/id_rsa".format(
        env.projname), user=env.projname)
    sudo('cat /projects/{0}/.ssh/id_rsa.pub'.format(env.projname),
         user=env.projname)



@task
def checkout():
    with cd('~{0}/src'.format(env.projname)):
        for src in env.proj['src']:
            sudo('git clone {0}'.format(src['gitrepo']), user=env.projname)
            with cd(src['dirname']):
                sudo('git checkout {0}'.format(src.get('branch', 'master')),
                     user=env.projname)

@task
def make_venv():
    sudo('virtualenv /projects/{0}/virt'.format(env.projname),
         user=env.projname)
    with cd('~{0}/src'.format(env.projname)):
        for src in env.proj['src']:
            reqfile = '{0}/{1}'.format(src['dirname'],
                                       src.get('requirements_file',
                                               'requirements.txt'))

            if exists(reqfile):
                sudo('source ~{0}/virt/bin/activate && '
                     'pip install -r {1}'.format(env.projname, reqfile))

@task
def pushkeys():
    ssh_key = '{projdir}/ssh/id_rsa'.format(**env)
    if os.path.exists(ssh_key):
        put(ssh_key, '/projects/{projname}/.ssh/id_rsa'.format(**env),
            use_sudo=True, mode=044)

def _get_conf(name):
    # check for server-specific conf
    sconf = os.path.join(env.projdir, env.server_type, name)
    if os.path.exists(sconf):
        return sconf
    else:
        return os.path.join(env.projdir, name)

@task
def pushconf():
    nginx_config = _get_conf('nginx.conf')
    uwsgi_config = _get_conf('uwsgi.ini')
    upstart_config = _get_conf('upstart.conf')
    cron_config = _get_conf('cron')
    upstart_init_dir = _get_conf('init/')

    if os.path.exists(nginx_config):
        put(nginx_config,
            '/etc/nginx/sites-available/{0}'.format(env.projname),
            use_sudo=True, mode=0466)
        sudo('ln -sf /etc/nginx/sites-available/{0} '
             '/etc/nginx/sites-enabled/{0}'.format(env.projname))

    if os.path.exists(uwsgi_config):
        put(uwsgi_config,
            '/etc/uwsgi/apps-available/{0}.ini'.format(env.projname),
            use_sudo=True, mode=0466)
        sudo('ln -sf /etc/uwsgi/apps-available/{0}.ini '
             '/etc/uwsgi/apps-enabled/{0}.ini'.format(env.projname))

    if os.path.exists(upstart_config):
        put(upstart_config, '/etc/init/{0}.conf'.format(env.projname),
            use_sudo=True, mode=0466)

    if os.path.exists(upstart_init_dir):
        copy_dir(upstart_init_dir, '/etc/init/')

    if os.path.exists(cron_config):
        # copy cron over, update it, and drop it
        put(cron_config, '/tmp/croncfg')
        sudo('cat /tmp/croncfg | crontab -', user=env.projname)
        sudo('rm /tmp/croncfg')


def _remotediff(localfile, remote_path):
    if os.path.exists(localfile):
        tmpname = '/tmp/{0}-{1}'.format(env.projname,
                                        os.path.basename(localfile))
        with hide('running', 'stdout',  'stderr'):
            get(remote_path, tmpname)
            with settings(hide('warnings'), warn_only=True):
                res = local('diff {0} {1}'.format(localfile, tmpname),
                            capture=True)
            if res.failed:
                puts(red('{0} differs from remote'.format(localfile)))
                puts(res)
            else:
                puts(green('{0} matches remote'.format(localfile)))
        os.remove(tmpname)

# @task -- promoted to top level
def checkconf():
    """ check local config vs. deployed """
    nginx_config = _get_conf('nginx.conf')
    uwsgi_config = _get_conf('uwsgi.ini')
    upstart_config = _get_conf('upstart.conf')
    cron_config = _get_conf('cron')

    _remotediff(nginx_config,
                '/etc/nginx/sites-available/{0}'.format(env.projname))
    _remotediff(uwsgi_config,
                '/etc/uwsgi/apps-available/{0}.ini'.format(env.projname))
    _remotediff(upstart_config,
                '/etc/init/{0}.conf'.format(env.projname))
    with settings(hide('running', 'stderr', 'stdout', 'warnings'), warn_only=True):
        sudo('crontab -l > /tmp/crondump-{0}'.format(env.projname),
             user=env.projname)
    _remotediff(cron_config,
                '/tmp/crondump-{0}'.format(env.projname))

@task
def push_extras():
    local_dir = _get_conf('extra')
    remote_dir = '/projects/{0}'.format(env.projname)
    copy_dir(local_dir, remote_dir, env.projname)

# @task -- promoted to top level
def update():
    """ update all git repositories """
    for src in env.proj['src']:
        with cd('~{0}/src/{1}'.format(env.projname, src['dirname'])):
            sudo('git pull', user=env.projname)


@task
def restart_nginx():
    sudo('/etc/init.d/nginx restart')


@task
def restart_uwsgi():
    sudo('/etc/init.d/uwsgi restart {0}'.format(env.projname))


@task
def postinstall():
    for pi_cmd in env.proj.get('post_install', []):
        sudo(pi_cmd)


# @task -- promoted to top level
def deploy():
    """ deploy a project from scratch """
    # mount drive
    add_user_ebs()

    add_related_servers()

    install_extra_packages()

    # fill out home dir
    make_homedir()
    pushkeys()
    checkout()

    # if explicity set venv=false, skip venv
    if not env.proj.get('venv', True):
        puts('skipping venv creation')
    else:
        make_venv()

    # push any extras that may exist
    push_extras()

    # push server-wide changes
    pushconf()

    # do post-install hooks
    postinstall()

@task
def tail(logname):
    sudo('tail -f /projects/{projname}/logs/{0}'.format(logname, **env))
