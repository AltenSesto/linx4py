'''
Created on 22 okt 2013

@author: Bjorn Arnelid
'''

from ctypes import c_uint

# SIG_SEL for accepting standard LINX_OS_HUNT_SIG
OneSignalSigSelect = c_uint * 2
LINX_OS_HUNT_SIG_SEL =  OneSignalSigSelect(1,251)

#SIG_SEL for accepting any LINX_SIGNAL
OneSignalSigSelect = c_uint * 1
LINX_NO_SIG_SEL = OneSignalSigSelect(0) 