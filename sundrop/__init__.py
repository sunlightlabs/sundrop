import os
import json
import ConfigParser

from fabric.api import env, task, abort, puts
env.use_ssh_config = True

# get all commands
from . import server
from . import project
from . import user

# and promote a few to top level
from project import deploy, update, checkconf

def _load_json(fname):
    fname = os.path.join(env.CONFIG_DIR, fname)
    try:
        return json.load(open(fname))
    except Exception as e:
        abort('unable to load {0}: {1}'.format(fname, e))


def _init():
    CONFIG_FILE = os.path.expanduser('~/.sundrop')
    cp = ConfigParser.ConfigParser()
    cp.read(CONFIG_FILE)
    try:
        env.CONFIG_DIR = os.path.expanduser(cp.get('sundrop', 'config_dir'))
    except:
        abort('no [sundrop] config_dir set in {0}'.format(CONFIG_FILE))

    try:
        env.AWS_KEY = cp.get('aws', 'key')
    except:
        pass
    try:
        env.AWS_SECRET = cp.get('aws', 'secret')
    except:
        pass

    env.PROJECTS = _load_json('projects.json')


# always call init
_init()


@task
def lsproj():
    for p in env.PROJECTS:
        puts('    {0}'.format(p))


@task
def production():
    if env.hosts:
        abort('multiple hosts specified: "{0}" and "production"'.format(
            ','.join(env.hosts)
        ))
    env.server_type = 'production'


@task
def staging():
    if env.hosts:
        abort('multiple hosts specified: "{0}" and "staging"'.format(
            ','.join(env.hosts)
        ))
    env.server_type = 'staging'


@task
def proj(projname):
    env.projname = projname
    env.projdir = os.path.join(env.CONFIG_DIR, projname)
    env.proj = env.PROJECTS[projname]
    if not env.hosts:
        if not hasattr(env, 'server_type'):
            abort('no hosts specified, use -H or production|staging')
        else:
            if env.server_type not in env.proj:
                abort('no {server_type} host specified for {projname}'.format(
                    **env))
            else:
                env.hosts = [env.proj[env.server_type]]
