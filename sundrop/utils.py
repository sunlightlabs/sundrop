import os
from fabric.api import cd, sudo, put

def copy_dir(local_dir, remote_dir, user):
    # go into project home dir
    with cd(remote_dir):
        # get all files in local dir
        for root, dirs, files in os.walk(local_dir):
            # try and create directory if there are files to be put here
            if files:
                remote_root = root.replace(local_dir, '')
                sudo('mkdir -p {0}'.format(remote_root), user=user)

                # copy over files
                for file in files:
                    remote_file = os.path.join(remote_root, file)
                    put(os.path.join(root, file), remote_file, use_sudo=True,
                        mirror_local_mode=True)
                    sudo('chown {0}:{0} {1}'.format(user, remote_file))

