#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for tpDcc-libs-resources
"""

import os
import sys

from Qt.QtWidgets import QApplication

from tpDcc.managers import resources


def init(*args, **kwargs):
    """
    Initializes library
    """

    # Import resources (Do not remove)
    from tpDcc.libs.resources import res

    app = QApplication.instance() or QApplication(sys.argv)

    register_resources()


def register_resources():
    """
    Registers tpDcc.libs.qt resources path
    """

    resources_path = os.path.dirname(os.path.abspath(__file__))
    resources.register_resource(resources_path, key='tpDcc-libs-resources')
