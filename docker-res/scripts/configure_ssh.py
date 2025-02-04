#!/usr/bin/python

"""
Configure ssh service
"""

from subprocess import call
import os
import sys

HOME = os.getenv("HOME", "/root")

# Export environment for ssh sessions
#call("printenv > $HOME/.ssh/environment", shell=True)
with open(HOME + "/.ssh/environment", 'w') as fp:
    for env in os.environ:
        if env == "LS_COLORS":
            continue
        # ignore most variables that get set by kubernetes if enableServiceLinks is not disabled
        # https://github.com/kubernetes/kubernetes/pull/68754
        if "SERVICE_PORT" in env.upper():
            continue
        if "SERVICE_HOST" in env.upper():
            continue
        if "PORT" in env.upper() and "TCP" in env.upper():
            continue
        fp.write(env + "=" + str(os.environ[env]) + "\n")

### Generate SSH Key (for ssh access, also remote kernel access)
# Generate a key pair without a passphrase (having the key should be enough) that can be used to ssh into the container
# Add the public key to authorized_keys so someone with the public key can use it to ssh into the container
SSH_KEY_NAME = "id_ed25519" # use default name instead of workspace_key
# TODO add container and user information as a coment via -C
if not os.path.exists("~/.ssh/"+SSH_KEY_NAME):
    # create ssh key if it does not exist yet
    call("ssh-keygen -f ~/.ssh/{} -t ed25519 -q -N \"\" > /dev/null".format(SSH_KEY_NAME), shell=True)
call("chmod 600 ~/.ssh/{}".format(SSH_KEY_NAME), shell=True)
# echo "" >> ~/.ssh/authorized_keys will prepend a new line before the key is added to the file
call("echo "" >> ~/.ssh/authorized_keys && cat ~/.ssh/{}.pub | tee -a ~/.ssh/authorized_keys".format(SSH_KEY_NAME), shell=True)
# Add identity to ssh agent -> e.g. can be used for git authorization
call("eval \"$(ssh-agent -s)\" && ssh-add ~/.ssh/"+SSH_KEY_NAME + " > /dev/null", shell=True)
###