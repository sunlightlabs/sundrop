import os
import json
import ConfigParser

from fabric.api import env, task, abort, puts
env.use_ssh_config = True

from . import server
from . import project

# project config

PROJECTS = {
    'microsfm': {
        'src': [
            {'gitrepo': 'git://github.com/mediastandardstrust/superfastmatch.git',
             'dirname': 'superfastmatch'},
        ],
        'extra_packages': ['libunwind7-dev', 'zlib1g-dev', 'subversion'],
    }
}

def _load_json(fname):
    fname = os.path.join(env.CONFIG_DIR, fname)
    try:
        return json.load(open(fname))
    except Exception as e:
        abort('unable to load {0}: {1}'.format(fname, e))

def _init():
    CONFIG_FILE = os.path.expanduser('~/.sundeploy')
    cp = ConfigParser.ConfigParser()
    cp.read(CONFIG_FILE)
    try:
        env.CONFIG_DIR = os.path.expanduser(cp.get('sundeploy', 'config_dir'))
    except:
        abort('no [sundeploy] config_dir set in {0}'.format(CONFIG_FILE))

    env.SERVERS = _load_json('servers.json')
    env.PROJECTS = _load_json('projects.json')

# always call init
_init()

@task
def lsserver():
    for p in env.SERVERS:
        puts('    {0}'.format(p))

@task
def lsproj():
    for p in env.PROJECTS:
        puts('    {0}'.format(p))

@task
def proj(projname):
    env.projname = projname
    env.projdir = os.path.join(env.CONFIG_DIR, projname)
    env.proj = env.PROJECTS[projname]
    # right now we only support production, staging support coming
    env.server = env.SERVERS[env.PROJECTS[projname]['production']]
    env.hosts = [env.PROJECTS[projname]['production']]
