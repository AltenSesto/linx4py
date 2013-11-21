#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Copyright (c) 2013 Alten AB.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
# 
# Contributors:
#     Bjorn Arnelid - initial API and implementation
#-------------------------------------------------------------------------------
from distutils.core import setup


setup(
      name='Linx4Py',
      version='0.1',
      author='Bjorn Arnelid',
      author_email='bjar@xdin.com',
      description='Linx communication bindings for python',
      license = 'GNU Public License v3.0',
      keywords = 'linx message passing',
      package_dir = {"": "src"},
      packages=['linx4py'],
     )