#!/usr/bin/python

"""
Configure and start nginx service
"""

from subprocess import call
import os
import sys

ENV_RESOURCES_PATH = os.getenv("RESOURCES_PATH", "/resources")

# Basic Auth

ENV_NAME_SERVICE_USER = "WORKSPACE_AUTH_USER"
ENV_NAME_SERVICE_PASSWORD = "WORKSPACE_AUTH_PASSWORD"
ENV_SERVICE_USER = None
ENV_SERVICE_PASSWORD = None

if ENV_NAME_SERVICE_USER in os.environ:
    ENV_SERVICE_USER = os.environ[ENV_NAME_SERVICE_USER]
if ENV_NAME_SERVICE_PASSWORD in os.environ:
    ENV_SERVICE_PASSWORD = os.environ[ENV_NAME_SERVICE_PASSWORD]

NGINX_FILE = "/etc/nginx/nginx.conf"

# Replace base url placeholders with actual base url -> should 
call("sed -i 's@{WORKSPACE_BASE_URL}@" + os.getenv("WORKSPACE_BASE_URL", "").rstrip('/') + "@g' " + NGINX_FILE, shell=True)

# Activate or deactivate jupyter based authentication for tooling
call("sed -i 's@{AUTHENTICATE_VIA_JUPYTER}@" + os.getenv("AUTHENTICATE_VIA_JUPYTER", "false").lower().strip() + "@g' " + NGINX_FILE, shell=True)

call("sed -i 's@{SHARED_LINKS_ENABLED}@" + os.getenv("SHARED_LINKS_ENABLED", "false").lower().strip() + "@g' " + NGINX_FILE, shell=True)

# Replace key hash with actual sha1 hash of key
try:
    with open(os.getenv("HOME", "/root") + "/.ssh/id_ed25519", "r") as f:
        private_key = f.read()

    import hashlib
    key_hasher = hashlib.sha1()
    key_hasher.update(str.encode(str(private_key).lower().strip()))
    key_hash = key_hasher.hexdigest()
    
    call("sed -i 's@{KEY_HASH}@" + str(key_hash) + "@g' " + NGINX_FILE, shell=True)
except Exception as e:
    print(e)

# PREPARE SSL SERVING
ENV_NAME_SERVICE_SSL_ENABLED = "WORKSPACE_SSL_ENABLED"
if ENV_NAME_SERVICE_SSL_ENABLED in os.environ \
        and (os.environ[ENV_NAME_SERVICE_SSL_ENABLED] is True \
                or os.environ[ENV_NAME_SERVICE_SSL_ENABLED] == "true" \
                or os.environ[ENV_NAME_SERVICE_SSL_ENABLED] == "on"):
    ENV_SSL_RESOURCES_PATH =  os.getenv("SSL_RESOURCES_PATH", "/resources/ssl")

    call("sed -i 's@#ssl_certificate_key@ssl_certificate_key " + ENV_SSL_RESOURCES_PATH + "/cert.key;@g' " + NGINX_FILE, shell=True)
    call("sed -i 's@#ssl_certificate@ssl_certificate " + ENV_SSL_RESOURCES_PATH + "/cert.crt;@g' " + NGINX_FILE, shell=True)
    # activate ssl in listen
    call("sed -i -r 's/listen ([0-9]+);/listen \\1 ssl;/g' " + NGINX_FILE, shell=True)
###

# PREPARE BASIC AUTH
# Basic Auth enablment is important for a standalone workspace deployment, as there the 
# /tools path is not protected by Jupyter's token!
if ENV_SERVICE_USER and ENV_SERVICE_PASSWORD:

    call("sed -i 's/#auth_basic /auth_basic /g' " + NGINX_FILE, shell=True)
    call("sed -i 's/#auth_basic_user_file/auth_basic_user_file/g' " + NGINX_FILE, shell=True)

    # create basic auth user
    call("echo '" + ENV_SERVICE_PASSWORD + "' | htpasswd -b -i -c /etc/nginx/.htpasswd '"\
            + ENV_SERVICE_USER +"'", shell=True)
###

# create / copy certificates
call(ENV_RESOURCES_PATH + "/scripts/setup-certs.sh", shell=True)
