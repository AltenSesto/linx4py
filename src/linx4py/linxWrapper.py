'''
Created on 17 okt 2013

@author: bjorn
'''

from ctypes import CDLL, POINTER, Structure, Union, c_uint, c_int, c_char_p, c_void_p

class LinxWrapper(object):
    '''
    LinxWrapper
    Linxwrapper mirrors linx.h directly making the function calls as similar as possible
    '''
    liblinx = None

    def __init__(self):
        '''
        Constructor
        '''
        self.liblinx = CDLL("liblinx.so")
        
    def linx_open(self, name, options, arg):
        '''
        linx_open
        Matches linx function:
        LINX *linx_open(const char *name, uint32_t options, void *arg); 
        '''
        linx_open = self.liblinx.linx_open
        linx_open.argtypes = [c_char_p, c_uint, c_void_p]
        linx_open.restype = POINTER(LINX)
        return linx_open(name,options,arg)
    
    def linx_hunt(self, linx, name, hunt_sig):
        '''
        linx_hunt
        Matches linx function:
        int linx_hunt(LINX * linx, const char *name, union LINX_SIGNAL **hunt_sig);
        '''
        linx_hunt = self.liblinx.linx_hunt
        linx_hunt.argtypes = [POINTER(LINX), c_char_p, POINTER(POINTER(LINX_SIGNAL))]
        return linx_hunt(linx, name, hunt_sig)
    
    def linx_receive_w_tmo(self,linx, sig, tmo, sig_sel):
        '''
        linx_receive_w_tmo
        Matches linx function:
        int linx_receive_w_tmo(LINX * linx, union LINX_SIGNAL **sig, 
                               LINX_OSTIME tmo, const LINX_SIGSELECT * sig_sel);
        '''
        linx_receive_w_tmo = self.liblinx.linx_receive_w_tmo
        linx_receive_w_tmo.argtypes = [POINTER(LINX), POINTER(POINTER(LINX_SIGNAL)), 
                                       c_uint, POINTER(c_uint)]
        return linx_receive_w_tmo(linx, sig, tmo, sig_sel)
    
    def linx_sender(self, linx, sig):
        '''
        linx_sender
        Matches linx function:
        LINX_SPID linx_sender(LINX * linx, union LINX_SIGNAL **sig);
        '''
        linx_sender = self.liblinx.linx_sender
        linx_sender.argtypes = [POINTER(LINX), POINTER(POINTER(LINX_SIGNAL))]
        return linx_sender(linx, sig)
        
    def linx_attach(self, linx, sig, spid):
        '''
        linx_attach
        Matches linx function:
        LINX_OSATTREF linx_attach(LINX * linx, union LINX_SIGNAL **sig, LINX_SPID spid);
        '''
        linx_attach = self.liblinx.linx_attach
        linx_attach.argtypes = [POINTER(LINX), POINTER(POINTER(LINX_SIGNAL)), c_uint]
        state = linx_attach(linx, sig, spid)
        return state
    
    def linx_send(self):
        '''
        linx_send
        Matches linx function:
        LINX_SPID linx_sender(LINX * linx, union LINX_SIGNAL **sig);
        '''
        
        
class LINK(Structure):
    pass
 
LINK._fields_ = [("next", POINTER(LINK)),
                 ("prev", POINTER(LINK))
                 ]

class LINXSigAdm(Structure):
    pass

class LINX(Structure):
    _fields_ = [("owned_sig", LINK),
                ("magic", c_uint),
                ("socket", c_int),
                ("spid", c_uint),
                ("free_buffer", POINTER(LINXSigAdm))
                ]

class LINX_SIGNAL(Union):
    '''
    Linx Signal,
    You may have do dynamically add fields to this signal to handle signal data
    '''
    _fields_ = [("sig_no", c_uint)
                ]