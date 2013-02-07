import os
import time
from fabric.api import cd, sudo, put, abort, env, hide, puts
from fabric.contrib.files import append, contains, exists
import boto

def _get_ec2_metadata(type):
    with hide('running', 'stdout',  'stderr'):
        r = sudo('wget -q -O - http://169.254.169.254/latest/meta-data/{0}'.format(type))
        return r

def copy_dir(local_dir, remote_dir, user=None):
    # get all files in local dir
    for root, dirs, files in os.walk(local_dir):
        # try and create directory if there are files to be put here
        if files:
            remote_root = os.path.join(remote_dir, root.replace(local_dir, ''))
            sudo('mkdir -p {0}'.format(remote_root), user=user)

            # copy over files
            for file in files:
                remote_file = os.path.join(remote_root, file)
                put(os.path.join(root, file), remote_file, use_sudo=True,
                    mirror_local_mode=True)
                if user:
                    sudo('chown {0}:{0} {1}'.format(user, remote_file))


def add_ebs(size_gb, path, iops=None):
    ec2 = boto.connect_ec2(env.AWS_KEY, env.AWS_SECRET)
    # get ec2 metadata
    zone = _get_ec2_metadata('placement/availability-zone')
    instance_id = _get_ec2_metadata('instance-id')

    # create and attach drive
    volume = ec2.create_volume(size_gb, zone,
                               #volume_type='io1' if iops else 'standard',
                               #iops=iops
                              )

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


