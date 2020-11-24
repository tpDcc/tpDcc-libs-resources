#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains style implementation
"""

from __future__ import print_function, division, absolute_import

import os
import re
import logging
from collections import Counter

import qtsass

from tpDcc.managers import resources
from tpDcc.libs.python import color, python, path as path_utils
from tpDcc.libs.resources.core import utils

LOGGER = logging.getLogger('tpDcc-libs-qt')


class StyleSheet(object):

    class Types(object):
        NORMAL = 'normal'
        DARK = 'dark'
        LIGHT = 'light'

    EXTENSION = 'css'

    @classmethod
    def from_path(cls, path, **kwargs):
        """
        Returns stylesheet from given path
        :param path: str
        :param kwargs: dict
        :return: StyleSheet
        """

        stylesheet = cls()
        data = stylesheet.read(path)
        data = StyleSheet.include_paths(path, data)
        data = StyleSheet.format(data, **kwargs)
        stylesheet.set_data(data)

        return stylesheet

    @classmethod
    def from_text(cls, text, options=None):
        """
        Returns stylesheet from given text and options
        :param text: str
        :param options: dict
        :return: StyleSheet
        """

        stylesheet = cls()
        data = stylesheet.format(text, options=options)
        stylesheet.set_data(data)

        return stylesheet

    @staticmethod
    def read(path):
        """
        Reads style data from given path
        :param path: str
        :return: str
        """

        data = ''
        if path and os.path.isfile(path):
            with open(path, 'r') as f:
                data = f.read()

        return data

    @classmethod
    def include_paths(cls, file_path, data):
        if not file_path or not os.path.isfile(file_path):
            return data

        file_dir = os.path.dirname(file_path)
        included_data = list()
        for line in data.split('\n'):
            if not line.startswith('#include '):
                included_data.append(line)
                continue
            file_name_to_include = line.replace('#include ', '').replace('\r', '')
            file_to_include = os.path.abspath(os.path.join(file_dir, file_name_to_include))
            if not os.path.isfile(file_to_include):
                continue

            load_data = cls.read(file_to_include)
            new_data = cls.include_paths(file_to_include, load_data)

            if new_data:
                included_data.append('\n/*Included from: {}*/'.format(file_to_include))
            for load_line in new_data.split('\n'):
                included_data.append(load_line)

        return '\n'.join(included_data)

    @classmethod
    def format(cls, data=None, options=None, dpi=1, **kwargs):
        """
        Returns style with proper format
        :param data: str
        :param options: dict
        :param dpi: float
        :param is_saas: bool
        :return: str
        """

        theme_name = (kwargs.get('theme_name', 'default') or 'default').lower()

        if options:
            keys = list(options.keys())

            # We sort keys in the following way:
            # 1. Keys which value is type specific and are dynamic. Use [ ] and @. Also the keys using more @ are first.
            # 2. Keys which value is typed [ ]
            # 3. Other keys.

            type_keys_dynamic = list()
            type_keys = list()
            other_keys = list()
            for key in keys:
                value = str(options[key])
                freqs = Counter(value)
                reps = freqs.get('@', 0)
                if not reps:
                    if '[' in key or ']' in key:
                        type_keys.append(key)
                    else:
                        other_keys.append(key)
                else:
                    type_keys_dynamic.append(key)

            def _sort_dynamic_keys(x):
                value = str(options[x])
                count = Counter(value)
                return count.get('@', 0) + len(x)

            def _sort_type_keys(x):
                value = str(options[x])
                count = Counter(value)
                total = count.get('[', 0) + count.get(']', 0)
                return total

            if python.is_python2():
                type_keys.sort(key=_sort_type_keys, reverse=True)
                type_keys_dynamic.sort(key=_sort_dynamic_keys, reverse=True)
            else:
                type_keys = sorted(type_keys, key=_sort_type_keys, reverse=True)
                type_keys_dynamic = sorted(type_keys_dynamic, key=_sort_dynamic_keys, reverse=True)

            sorted_keys = list(type_keys_dynamic + type_keys + other_keys)

            for key in sorted_keys:
                key_value = options[key]
                str_key_value = str(key_value)
                option_value = str(key_value)
                if str_key_value.startswith('@^'):
                    option_value = str(utils.dpi_scale(int(str_key_value[2:])))
                if str_key_value.startswith('^'):
                    option_value = str(utils.dpi_scale(int(str_key_value[1:])))
                if 'icon' in key:
                    resource_paths = list()
                    resource_folders = [options.get('style_resources'), options.get('theme_resources')]
                    for resource_folder in resource_folders:
                        if not resource_folder or not os.path.isdir(resource_folder):
                            continue
                        resource_paths.append(os.path.join(resource_folder, str(key_value)))
                    resource_paths.append(resources.get('icons', theme_name, str(key_value)))
                    resource_path = None
                    for path in resource_paths:
                        if not path or not os.path.isfile(path):
                            continue
                        resource_path = path
                        break
                    if resource_path and os.path.isfile(resource_path):
                        option_value = path_utils.clean_path(resource_path)
                elif color.string_is_hex(str_key_value):
                    try:
                        color_list = color.hex_to_rgba(str_key_value)
                        option_value = 'rgba({}, {}, {}, {})'.format(
                            color_list[0], color_list[1], color_list[2], color_list[3])
                    except ValueError:
                        # This exception will be raised if we try to convert an attribute that is not a color.
                        option_value = key_value

                data = data.replace('@{}'.format(key), option_value)

        re_dpi = re.compile('[0-9]+[*]DPI')
        new_data = list()

        for line in data.split('\n'):
            dpi_ = re_dpi.search(line)
            if dpi_:
                new = dpi_.group().replace('DPI', str(dpi))
                val = int(eval(new))
                line = line.replace(dpi_.group(), str(val))
            new_data.append(line)

        data = '\n'.join(new_data)

        # try:
        #     data = qtsass.compile(data)
        # except Exception as exc:
        #     LOGGER.warning(
        #         'Error while compiling SAAS style file! Maybe the style will not appear properly: {}.'.format(exc))

        return data

    def __init__(self):
        super(StyleSheet, self).__init__()

        self._data = ''

    def data(self):
        """
        Returns style data
        :return: str
        """

        return self._data

    def set_data(self, data):
        """
        Sets style data
        :param data: str
        """

        self._data = data
