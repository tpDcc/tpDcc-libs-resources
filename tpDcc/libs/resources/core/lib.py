#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for tpDcc-libs-resources
"""

from __future__ import print_function, division, absolute_import

import os
import sys
import logging.config

from Qt.QtWidgets import QApplication

LIB_ID = 'tpDcc-libs-resources'
LIB_ENV = LIB_ID.replace('-', '_').upper()

from tpDcc.core import library
from tpDcc.managers import resources

# Import resources (Do not remove)
from tpDcc.libs.resources import res


class ResourcesLib(library.DccLibrary, object):
    def __init__(self, *args, **kwargs):
        super(ResourcesLib, self).__init__(*args, **kwargs)

    @classmethod
    def config_dict(cls, file_name=None):
        base_tool_config = library.DccLibrary.config_dict(file_name=file_name)
        tool_config = {
            'name': 'Resources Library',
            'id': LIB_ID,
            'supported_dccs': {'maya': ['2017', '2018', '2019', '2020']},
            'tooltip': 'Library to manage resources'
        }
        base_tool_config.update(tool_config)

        return base_tool_config

    @classmethod
    def load(cls):

        app = QApplication.instance() or QApplication(sys.argv)
        resources_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        resources.register_resource(resources_path, key='tpDcc-libs-resources')


def create_logger(dev=False):
    """
    Creates logger for current tpDcc-libs-resources package
    """

    logger_directory = os.path.normpath(os.path.join(os.path.expanduser('~'), 'tpDcc', 'logs', 'libs'))
    if not os.path.isdir(logger_directory):
        os.makedirs(logger_directory)

    logging_config = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '__logging__.ini'))

    logging.config.fileConfig(logging_config, disable_existing_loggers=False)
    logger = logging.getLogger('tpDcc-libs-resources')
    dev = os.getenv('TPDCC_DEV', dev)
    if dev:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    return logger


create_logger()
