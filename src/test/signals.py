'''
Created on 24 okt 2013

@author: bjorn
'''

from ctypes import Structure, Union, c_int, c_uint
class REQUEST_SIGNAL(Structure):
    _fields_ = [("sig_no", c_uint),
                ("seqno", c_int)
                ]
    
class REPLY_SIGNAL(Structure):
    _fields_ = [("sig_no", c_uint),
                ("seqno", c_int)
                ]
    
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