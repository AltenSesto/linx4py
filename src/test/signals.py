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
Created on 24 okt 2013

@author: bjorn
'''

from ctypes import Structure, Union, c_int, c_uint

REQUEST_SIGNAL_NO = 0x3340
class REQUEST_SIGNAL(Structure):
    _fields_ = [("sig_no", c_uint),
                ("seqno", c_int)
                ]
    def __init__(self):
        super(Structure, self).__init__()
        self.sig_no = REQUEST_SIGNAL_NO

REPLY_SIGNAL_NO = 0x3341
class REPLY_SIGNAL(Structure):
    _fields_ = [("sig_no", c_uint),
                ("seqno", c_int)
                ]
    def __init__(self):
        super(Structure, self).__init__()
        self.sig_no = REPLY_SIGNAL_NO
    
class LINX_SIGNAL(Union):
    '''
    LinxAdapter Signal,
    Taken from linx basic example
    '''
    _fields_ = [("sig_no", c_uint),
                ("request", REQUEST_SIGNAL), 
                ("reply", REPLY_SIGNAL),
                ]
    
class BASE_SIGNAL(Structure):
    _fields_ = [("sig_no", c_uint),
                 ]
