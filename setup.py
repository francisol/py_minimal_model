#!/usr/bin/env python
# coding:utf-8

import minimal_model
from setuptools import setup


setup(
        name='minimal_model',     
        version=minimal_model.VERSION,   
        description='compute a minimal model',   
        author='', 
        install_requires=['python-sat','psutil'],
        author_email='',  
        url='',  
        scripts=['cli/minimal_model'],
        packages=['minimal_model'],
)