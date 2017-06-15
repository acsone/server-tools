# coding: utf-8
from . import controllers  # noqa
import odoo
from cProfile import Profile
from . import core
from .core import profiling
from odoo.http import JsonRequest
from odoo.service.server import ThreadedServer
import os
import logging


_logger = logging.getLogger(__name__)


def patch_odoo():
    """Modify odoo/Odoo entry points so that profile can record.

    Odoo is a multi-threaded program. Therefore, the :data:`profile` object
    needs to be enabled/disabled each in each thread to capture all the
    execution.

    For instance, odoo 7 spawns a new thread for each request.
    """
    _logger.info('Patching odoo.addons.web.http.JsonRequest.dispatch')
    orig_dispatch = JsonRequest.dispatch

    def dispatch(*args, **kwargs):
        with profiling():
            return orig_dispatch(*args, **kwargs)
    JsonRequest.dispatch = dispatch


def dump_stats():
    """Dump stats to standard file"""
    _logger.info('Dump stats')
    core.profile.dump_stats(os.path.expanduser('~/.odoo_server.stats'))

def create_profile():
    """Create the global, shared profile object."""
    _logger.info('Create core.profile')
    core.profile = Profile()


def patch_stop():
    """When the server is stopped then save the result of cProfile stats"""
    origin_stop = ThreadedServer.stop

    _logger.info('Patching odoo.service.server.ThreadedServer.stop')

    def stop(*args, **kwargs):
        if odoo.tools.config['test_enable']:
            dump_stats()
        return origin_stop(*args, **kwargs)
    ThreadedServer.stop = stop


def post_load():
    _logger.info('Post load')
    create_profile()
    patch_odoo()
    if odoo.tools.config['test_enable']:
        # Enable profile in test mode for orm methods.
        _logger.info('Enabling core and apply patch')
        core.enabled = True
        patch_stop()
