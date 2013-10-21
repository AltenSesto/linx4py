'''
Created on 17 okt 2013

@author: Bjorn Arnelid
'''

from ctypes import CDLL, POINTER, Structure, c_uint, c_int, c_char_p, c_void_p

class LinxWrapper(object):
    '''
    LinxWrapper
    Linxwrapper mirrors linx.h directly making the function calls as similar as possible
    '''
    liblinx = None
    signalClass = None

    def __init__(self):
        '''
        Constructor
        '''
        self.liblinx = CDLL("liblinx.so")
        self.signalClass = BaseSignal
        
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
        linx_hunt.argtypes = [POINTER(LINX), c_char_p, POINTER(POINTER(self.signalClass))]
        return linx_hunt(linx, name, hunt_sig)
    
    def linx_receive_w_tmo(self,linx, sig, tmo, sig_sel):
        '''
        linx_receive_w_tmo
        Matches linx function:
        int linx_receive_w_tmo(LINX * linx, union LINX_SIGNAL **sig, 
                               LINX_OSTIME tmo, const LINX_SIGSELECT * sig_sel);
        '''
        linx_receive_w_tmo = self.liblinx.linx_receive_w_tmo
        linx_receive_w_tmo.argtypes = [POINTER(LINX), POINTER(POINTER(self.signalClass)), 
                                       c_uint, POINTER(c_uint)]
        return linx_receive_w_tmo(linx, sig, tmo, sig_sel)
    
    def linx_sender(self, linx, sig):
        '''
        linx_sender
        Matches linx function:
        LINX_SPID linx_sender(LINX * linx, union LINX_SIGNAL **sig);
        '''
        linx_sender = self.liblinx.linx_sender
        linx_sender.argtypes = [POINTER(LINX), POINTER(POINTER(self.signalClass))]
        return linx_sender(linx, sig)
        
    def linx_attach(self, linx, sig, spid):
        '''
        linx_attach
        Matches linx function:
        LINX_OSATTREF linx_attach(LINX * linx, union LINX_SIGNAL **sig, LINX_SPID spid);
        '''
        linx_attach = self.liblinx.linx_attach
        linx_attach.argtypes = [POINTER(LINX), POINTER(POINTER(self.signalClass)), c_uint]
        return linx_attach(linx, sig, spid)
    
    def linx_alloc(self, linx, size, sig_no):
        '''
        linx_alloc
        Matches linx function:
        union LINX_SIGNAL *linx_alloc(LINX * linx, LINX_OSBUFSIZE size, LINX_SIGSELECT sig_no);
        '''
        linx_alloc = self.liblinx.linx_alloc
        linx_alloc.argtypes = [POINTER(LINX), c_int, c_uint]
        linx_alloc.restype = POINTER(self.signalClass)
        return linx_alloc(linx, size, sig_no)
    
    def linx_free_buf(self, linx, sig):
        '''
        linx_free
        Matches linx function:
        int linx_free_buf(LINX * linx, union LINX_SIGNAL **sig);
        '''
        linx_free_buf = self.liblinx.linx_free_buf
        linx_free_buf.argtypes = [POINTER(LINX), POINTER(POINTER(self.signalClass))]
        return linx_free_buf(linx, sig)
    
    def setSignalClass(self, signalClass):
        '''
        getSignalClassFrom
        Utility function to get the correct class for signal from pointer
        '''
        self.signalClass = signalClass
        
    def linx_send(self, linx, sig, to):
        '''
        linx_send
        Matches linx function:
        int linx_send(LINX * linx, union LINX_SIGNAL **sig, LINX_SPID to);
        '''
        linx_send = self.liblinx.linx_send
        linx_send.argtypes = [POINTER(LINX), POINTER(POINTER(self.signalClass)), c_uint]
        return linx_send(linx, sig, to)
        
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

class BaseSignal(Structure):
    _fields_ = [("sig_no", c_uint),
                 ]
