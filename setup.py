#!/usr/bin/python
# coding=utf-8
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import os
import os.path


from setuptools import find_packages
from setuptools import setup


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(CURRENT_DIR)

LICENCE = open('LICENSE').read()
README = open('README.md').read()
REQUIREMENTS = open('requirements.txt').read().split('\n')

setup(name='heat_resource_fetcher',
      version='0.9',
      packages=find_packages(),
      install_requires=REQUIREMENTS,
      scripts=['bin/heat_resource_fetcher'],
      license=LICENCE,
      long_description=README,
)
