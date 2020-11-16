#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpDcc-libs-unittest function core implementations
"""

from __future__ import print_function, division, absolute_import

from tpDcc.core import library

LIB_ID = 'tpDcc-libs-resources'
LIB_ENV = LIB_ID.replace('-', '_').upper()


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
