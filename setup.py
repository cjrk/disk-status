#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name="disk-status",
      version="0.1.0",
      author="Christian Jurke",
      description="Batch-Test speed and health assesments on drives",

      py_modules = ['disk_status'],
      entry_points={
          'console_scripts':
            ['disk-status = disk_status:main']
      },
      install_requires=['setuptools'],
      dependency_links = [
      	'https://github.com/cjrk/shell.py/tarball/master#egg=shell.py>=1.0.3'
      ]
)
