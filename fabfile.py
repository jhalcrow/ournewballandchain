from fabric.api import task, put, env, sudo, run
from fabric.context_managers import cd

env.hosts = ['ournewballandchain.com']
env.user = 'ubuntu'
env.key_filename = '~/.ec2/weddingkey.pem'
env.forward_agent = True

repo_url = "git@github.com:jhalcrow/ournewballandchain.git"

def setup():
    sudo("apt-get -y install apache2-mpm-worker mosh git")
    run("git clone %s" % repo_url)

def deploy():
    with cd("ournewballandchain"):
        run("git pull")
        sudo("cp -r ournewballandchain/static/* /var/www")
        sudo("/srv/rsvp/bin/python setup.py install")
        sudo("cp rsvp_wsgi.py /srv/rsvp")
        sudo("supervisorctl restart rsvp")

