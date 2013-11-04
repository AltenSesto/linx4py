'''
This module is a thin wrapper for calling Linx API

Classes: 
LinxWrapper - Used to call Linx API from python.
LINX - Data structure representing a Linx object in liblinx.so

@author: Bjorn Arnelid
'''
from ctypes import CDLL, POINTER, Structure, c_uint, c_int, c_char_p, c_void_p, c_longlong

from linx_constants import BaseSignal

class LinxWrapper(object):

    '''
    Represent liblinx.so, mirroring the Linx API as closely as possible.

    Mirrors linx.h as closely as possible. The user must have Linx 2.5.1 installed
    and kernel modules loaded in order to use this Class. For more Information on
    how to install Linx see http://sourceforge.net/projects/linx/.
    '''

    def __init__(self):
        '''
        Constructor

        Loads liblinx and assigns SignalClass to default BaseSignal.
        '''
        self.liblinx = CDLL("liblinx.so")
        self.SignalClass = BaseSignal
        
    def linx_open(self, name, options, arg):
        '''
        Open linx socket and return linx representation.

        Matches linx function:
        LINX *linx_open(const char *name, uint32_t options, void *arg); 
        '''
        linx_open = self.liblinx.linx_open
        linx_open.argtypes = [c_char_p, c_uint, c_void_p]
        linx_open.restype = POINTER(LINX)
        return linx_open(name, options, arg)

    def linx_close(self, linx):
        '''
        Close linx socket.

        Matches linx function:
        int linx_close(LINX * linx);
        '''
        linx_close = self.liblinx.linx_close
        linx_close.argtypes = [POINTER(LINX)]
        return linx_close(linx)

    def linx_get_descriptor(self, linx):
        '''
        Get socket descriptor associated with linx.

        Matches linx function:
        int linx_get_descriptor(LINX * linx);
        '''
        linx_get_descriptor = self.liblinx.linx_get_descriptor
        linx_get_descriptor.argtypes = [POINTER(LINX)]
        return linx_get_descriptor(linx)

    def linx_alloc(self, linx, size, sig_no):
        '''
        Allocate bufferspace and return pointer to SignalClass object.

        Matches linx function:
        union LINX_SIGNAL *linx_alloc(LINX * linx, LINX_OSBUFSIZE size, LINX_SIGSELECT sig_no);
        '''
        linx_alloc = self.liblinx.linx_alloc
        linx_alloc.argtypes = [POINTER(LINX), c_int, c_uint]
        linx_alloc.restype = POINTER(self.SignalClass)
        return linx_alloc(linx, size, sig_no)

    def linx_free_buf(self, linx, sig):
        '''
        Free bufferspace populated by sig.

        Matches linx function:
        int linx_free_buf(LINX * linx, union LINX_SIGNAL **sig);
        '''
        linx_free_buf = self.liblinx.linx_free_buf
        linx_free_buf.argtypes = [POINTER(LINX), POINTER(POINTER(self.SignalClass))]
        return linx_free_buf(linx, sig)

    def linx_send(self, linx, sig, to_id):
        '''
        Send sig to to_id.

        Matches linx function:
        int linx_send(LINX * linx, union LINX_SIGNAL **sig, LINX_SPID to);
        '''
        linx_send = self.liblinx.linx_send
        linx_send.argtypes = [POINTER(LINX), POINTER(POINTER(self.SignalClass)), c_uint]
        return linx_send(linx, sig, to_id)

    def linx_send_w_s(self, linx, sig, from_id, to_id):
        '''
        Send sig to to_id setting sender to from_id.

        Matches linx function:
        int linx_send_w_s(LINX * linx, union LINX_SIGNAL **sig, LINX_SPID from, LINX_SPID to);
        '''
        linx_send_w_s = self.liblinx.linx_send_w_s
        linx_send_w_s.argtypes = [POINTER(LINX), POINTER(POINTER(self.SignalClass)),
                                  c_uint, c_uint]
        return linx_send_w_s(linx, sig, from_id, to_id)

    def linx_send_w_opt(self, linx, sig, from_id, to_id, taglist):
        '''
        Send sig to to_id with sender from_id specifying options to taglist.

        Matches linx function:
        int linx_send_w_opt(LINX * linx, union LINX_SIGNAL **sig, LINX_SPID from,
                            LINX_SPID to, int32_t *taglist);
        '''
        linx_send_w_opt = self.liblinx.linx_send_w_opt
        linx_send_w_opt.argtypes = [POINTER(LINX), POINTER(POINTER(self.SignalClass)),
                                    c_uint, c_uint, POINTER(c_int)]
        return linx_send_w_opt(linx, sig, from_id, to_id, taglist)

    def linx_sigattr(self, linx, sig, attr, value):
        '''
        set value to signal attribute attr for received signal sig.

        Matches linx function:
        int linx_sigattr(const LINX *linx, const union LINX_SIGNAL **sig, uint32_t attr,
                        void **value);
        '''
        linx_sigattr = self.liblinx.linx_sigattr
        linx_sigattr.argtypes = [POINTER(LINX), POINTER(POINTER(self.SignalClass)),
                                 c_uint]
        return linx_sigattr(linx, sig, attr, value)

    def linx_receive(self, linx, sig, sig_sel):
        '''
        Receive signal in sig_sel without timeout and set it to sig.

        Matches linx function:
        int linx_receive(LINX * linx, union LINX_SIGNAL **sig, const LINX_SIGSELECT * sig_sel);
        '''
        linx_receive = self.liblinx.linx_receive
        linx_receive.argtypes = [POINTER(LINX), POINTER(POINTER(self.SignalClass)), 
                                       POINTER(c_uint)]
        return linx_receive(linx, sig, sig_sel)

    def linx_receive_w_tmo(self, linx, sig, tmo, sig_sel):
        '''
        Receive signal in sig_sel with timeout tmo and set it to sig.

        Matches linx function:
        int linx_receive_w_tmo(LINX * linx, union LINX_SIGNAL **sig, 
                               LINX_OSTIME tmo, const LINX_SIGSELECT * sig_sel);
        '''
        linx_receive_w_tmo = self.liblinx.linx_receive_w_tmo
        linx_receive_w_tmo.argtypes = [POINTER(LINX), POINTER(POINTER(self.SignalClass)), 
                                       c_uint, POINTER(c_uint)]
        return linx_receive_w_tmo(linx, sig, tmo, sig_sel)

    def linx_receive_from(self, linx, sig, tmo, sig_sel, from_id):
        '''
        Receive signal in sig_sel from from_id with timeout tmo and set it to sig.

        Matches linx function:
        int linx_receive_from(LINX * linx, union LINX_SIGNAL **sig, LINX_OSTIME tmo,
                              const LINX_SIGSELECT * sig_sel, LINX_SPID from);
        '''
        linx_receive_from = self.liblinx.linx_receive_from
        linx_receive_from.argtypes = [POINTER(LINX), POINTER(POINTER(self.SignalClass)),
                                      c_uint, POINTER(c_uint), c_uint]
        return linx_receive_from(linx, sig, tmo, sig_sel, from_id)

    def linx_sender(self, linx, sig):
        '''
        Get sender id from received signal sig.

        Matches linx function:
        LINX_SPID linx_sender(LINX * linx, union LINX_SIGNAL **sig);
        '''
        linx_sender = self.liblinx.linx_sender
        linx_sender.argtypes = [POINTER(LINX), POINTER(POINTER(self.SignalClass))]
        return linx_sender(linx, sig)

    def linx_sigsize(self, linx, sig):
        '''
        Return signal buffer size of sig.
        
        Matches linx function:
        LINX_OSBUFSIZE linx_sigsize(LINX * linx, union LINX_SIGNAL **sig);
        '''
        linx_sigsize = self.liblinx.linx_sigsize
        linx_sigsize.argtypes = [POINTER(LINX), POINTER(POINTER(self.SignalClass))]
        return linx_sigsize(linx, sig)

    def linx_set_sigsize(self, linx, sig, sigsize):
        '''
        Set signal buffer size for sig.
        
        Matches linx function:
        int linx_set_sigsize(LINX * linx, union LINX_SIGNAL **sig, LINX_OSBUFSIZE sigsize);
        '''
        linx_set_sigsize = self.liblinx.linx_set_sigsize
        linx_set_sigsize.argtypes = [POINTER(LINX), POINTER(POINTER(self.SignalClass)),
                                     c_int]
        return linx_set_sigsize(linx, sig, sigsize)

    def linx_hunt(self, linx, name, hunt_sig):
        '''
        Send hunt signal using hunt_sig to server identified by name.

        Matches linx function:
        int linx_hunt(LINX * linx, const char *name, union LINX_SIGNAL **hunt_sig);
        '''
        linx_hunt = self.liblinx.linx_hunt
        linx_hunt.argtypes = [POINTER(LINX), c_char_p, POINTER(POINTER(self.SignalClass))]
        return linx_hunt(linx, name, hunt_sig)

    def linx_hunt_from(self, linx, name, hunt_sig, from_id):
        '''
        Send hunt signal using hunt_sig to server identified by name with return id from.
        
        Matches linx function:
        int linx_hunt_from(LINX * linx, const char *name, union LINX_SIGNAL **hunt_sig,
                           LINX_SPID from);
        '''
        linx_hunt_from = self.liblinx.linx_hunt_from
        linx_hunt_from.argtypes = [POINTER(LINX), c_char_p, POINTER(POINTER(self.SignalClass)),
                                   c_uint]
        return linx_hunt_from(linx, name, hunt_sig, from_id)

    def linx_attach(self, linx, sig, spid):
        '''
        Attach to server spid and return reference.

        Matches linx function:
        LINX_OSATTREF linx_attach(LINX * linx, union LINX_SIGNAL **sig, LINX_SPID spid);
        '''
        linx_attach = self.liblinx.linx_attach
        linx_attach.argtypes = [POINTER(LINX), POINTER(POINTER(self.SignalClass)), c_uint]
        return linx_attach(linx, sig, spid)

    def linx_detach(self, linx, attref):
        '''
        Detach from attached server attref.

        Matches linx function:
        int linx_detach(LINX * linx, LINX_OSATTREF * attref);
        '''
        linx_detach = self.liblinx.linx_detach
        linx_detach.argtypes = [POINTER(LINX), POINTER(c_uint)]
        return linx_detach(linx, attref)

    def linx_get_spid(self, linx):
        '''
        Get linx objects id.

        Matches linx function:
        LINX_SPID linx_get_spid(LINX * linx);
        '''
        linx_get_spid = self.liblinx.linx_get_spid
        linx_get_spid.argtypes = [POINTER(LINX)]
        return linx_get_spid(linx)
    
    def set_signal_class(self, signalClass):
        '''
        Set signal class to signalClass needed whan handling signal pointers in wrapper.
        '''
        self.SignalClass = signalClass

class LINK(Structure):
    pass
LINK._fields_ = [("next", POINTER(LINK)),
                 ("prev", POINTER(LINK))
                 ]


class linx_sndrcv_param(Structure):
    _fields_ = [("from", c_uint),
                ("to", c_uint),
                ("size", c_uint),
                ("sig_attr", c_uint),
                ("sigselect_size", c_uint),
                ("tmo", c_uint),
                ("sigselect", c_longlong),
                ("buffer", c_longlong),
                ("real_buf", c_longlong)
                ]


class LINXSigAdm(Structure):
    pass


class LINX(Structure):
    """
    Representation of LINX object. 
    
    Use this to connect to linx through LinxWrapper.
    """
    _fields_ = [("owned_sig", LINK),
                ("magic", c_uint),
                ("socket", c_int),
                ("spid", c_uint),
                ("free_buffer", POINTER(LINXSigAdm))
                ]


LINXSigAdm._fields_ = [("link", LINK),
                ("owner", POINTER(LINX)),
                ("true_size", c_int),
                ("sndrcv", linx_sndrcv_param)
                ]
