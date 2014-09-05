#! /usr/bin/env python
"""!
Setup metadata for the TSI python package
"""
__author__ = "Ben Johnston"
__revision__ = "0.1"
__date__ = "Tue Apr 15 20:04:32 EST 2014"
__license__ = "GPL"
##IMPORTS#####################################################################
from distutils.core import setup
##############################################################################
setup(
name='TSI',
description='Modules for use with the eBIRD',
author='Ben Johnston',
author_email='bjohnston24@gmail.com',
version=__revision__,
packages=['TSI'],
license='GPL',
long_description='')