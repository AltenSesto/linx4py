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
'''
This module contains common constants used in linx4py.

Constants: 
LINX_OS_HUNT_SIG_SEL - Default hunt signal selection.
LINX_NO_SIG_SEL - Empty signal selection, meaning that any signal is received.
BaseSignal - Standard signal only containing sig_no.
'''
from ctypes import c_uint, Structure


# SIG_SEL for accepting standard LINX_OS_HUNT_SIG
OneSignalSigSelect = c_uint * 2
LINX_OS_HUNT_SIG_SEL =  OneSignalSigSelect(1,251)


#SIG_SEL for accepting any LINX_SIGNAL
OneSignalSigSelect = c_uint * 1
LINX_NO_SIG_SEL = OneSignalSigSelect(0)


class BaseSignal(Structure):
    _fields_ = [("sig_no", c_uint),
                ]
