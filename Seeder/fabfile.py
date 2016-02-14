import os

from fabric.api import local, task

commands = {
    'runserver': ['./manage.py runserver 0.0.0.0:8000'],
    'syncdb': ['./manage.py migrate'],
    'static': ['./manage.py collectstatic --noinput'],
    'pull': ['git pull --rebase'],
    'touch_reload': ['touch ../../reload_seeder.touch'],
    'reqs': [
        'pip install -r ../requirements.txt --upgrade',
        'pip install -r ../requirements_dev.txt --upgrade'],
    'push_messages': [
        './manage.py makemessages -a',
        'tx push -t -s'],
    'pull_messages': [
        'tx pull -a',
        './manage.py compilemessages'
    ]
}


@task(alias='ym')
def yapf_migrations():
    """
    Refines migrations files so they would comply to pep8
    """
    from settings.base import INSTALLED_APPS
    for app in INSTALLED_APPS:
        migration_dir = os.path.join(app, 'migrations')
        if os.path.isdir(app) and os.path.isdir(migration_dir):
            local('yapf -r -i {0}'.format(migration_dir))


@task(alias='rns')
def runserver():
    map(local, commands['runserver'])


@task(alias='sdb')
def syncdb():
    map(local, commands['syncdb'])


@task(alias='cs')
def collect_static():
    map(local, commands['static'])


@task(alias='mpull')
def pull_messages():
    map(local, commands['pull_messages'])


@task(alias='mpush')
def push_messages():
    pull_messages()
    map(local, commands['push_messages'])


@task(alias='s')
def shell():
    local('./manage.py shell')


@task(alias='dl')
def deploy():
    map(local,
        commands['reqs'] +
        commands['pull_messages'] +
        commands['syncdb'] +
        commands['static'] +
        commands['touch_reload']
        )

@task
def run_local():
    map(local,
        commands['reqs'] +
        commands['syncdb'] +
        commands['static'] +
        commands['runserver']
        )