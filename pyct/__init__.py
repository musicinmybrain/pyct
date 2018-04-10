DOIT_CONFIG = {
    'verbosity': 2,
    'backend': 'sqlite3',
}

import os
import sys
import configparser

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from doit import get_var
from doit.action import CmdAction

from .util import get_tox_cmds

# doit bug in 0.29, which is last version to support py27
try:
    get_var("ecosystem")
except AttributeError:
    from doit import doit_cmd
    doit_cmd.reset_vars()
    del doit_cmd

# TODO: one day might have more sophisticated backend management...
ecosystem = get_var("ecosystem",os.getenv("PYCT_ECOSYSTEM","pip"))
if ecosystem == 'pip':
    from ._pip import * # noqa: api
elif ecosystem == 'conda':
    from ._conda import * # noqa: api

# TODO: support some limited form of dry run (but should be at doit
# level)
# action that just prepends echo to command, does "echo calling fn %s"%fn_name for pyfunc, etc, ...
#dryrun = get_var("dryrun",False)


env_suffix = {
    'name':'environment_suffix',
    'long':'environment-suffix',
    'short': 's',
    'type':str,
    'default':'default'
}


############################################################
# COMMON TASKS


########## TESTING ##########

def task_test():
    class thing:
        def __init__(self,what):
            self.what=what
        def __call__(self,environment_suffix):
            cmds = get_tox_cmds("%s-%s-%s"%( "py%s%s"%sys.version_info[0:2],self.what,environment_suffix))
            # hack to support multiple commands :(
            return " && ".join(cmds)

    # read the possibilities from tox.ini, but could instead have standard ones
    # as a way of suggesting what projects should make available 
    toxconf = configparser.ConfigParser()
    toxconf.read('tox.ini')
    # not sure how I was supposed to do this (gets all, flakes, unit, etc...)
    for t in toxconf['tox']['envlist'].split('-')[1][1:-1].split(','): 
        yield {'actions':[CmdAction(thing(t))],
               'doc':'Run "%s" tests'%t,
               'basename': 'test_'+t,
               'params':[env_suffix]}


# note: groups of tests with doit would be more flexible, but would
# duplicate tox


########## DOCS ##########

def task_build_docs():
    """build docs"""

    # TODO: these should be required when figure out dodo params
    org = { 'name':'org',
            'long':'org',
            'type':str,
            'default':'' }
    repo = { 'name':'repo',
             'long':'repo',
             'type':str,
             'default':'' }

    return {
        'params': [org, repo],
        'actions': [
            'nbsite_nbpagebuild.py %(org)s %s(repo)s ./examples ./doc',
            'sphinx-build -b html ./doc ./doc/_build/html',
            'nbsite_fix_links.py ./doc/_build/html',
            'touch ./doc/_build/html/.nojekyll',
            'nbsite_cleandisthtml.py ./doc/_build/html take_a_chance'
        ]
    }
