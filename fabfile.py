from fabric.api import task, put, env

env.hosts = ['ournewballandchain.com']
env.user = 'ubuntu'
env.keyfile_name = '~/.ec2/weddingkey.pem'

def setup():
    sudo("apt-get -y install apache2-mpm-worker mosh")

def update():
    put('static/*', '/var/www/', use_sudo=True)

