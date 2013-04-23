from setuptools import setup

setup(
    name='Our New Ball and Chain RSVP',
    version='0.1',
    description='RSVP',
    author='Jonathan Halcrow',
    url='http://www.github.com/jhalcrow/ournewballandchain.git',
    package_data={'ournewballandchain': 
        [
        'templates/base.html',
        'templates/rsvp_form.html',
        'templates/rsvp_form_prefill.html',
        ]},
    packages=['ournewballandchain']
)
