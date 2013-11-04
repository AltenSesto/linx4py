'''
Created on 15 okt 2013

@author: Bjorn Arnelid
'''

from ctypes import pointer, sizeof, c_uint
from linx_wrapper import LinxWrapper
from linx_constants import LINX_NO_SIG_SEL


class LinxAdapter(object):
    '''
    Wrapper for communicating with Linx from Python.
    '''
    # Use this to call the linx api
    wrapper = None
    # Linx instance passed into the wrapper to access linx
    instance = None

    def __init__(self):
        '''
        Constructor
        Creates instance to use and creates handle to linx API
        '''
        self.wrapper = LinxWrapper()
        
    def open(self, client_name, options=0, args = None):
        '''
        Open linx socket.

        Opens linx socket using client_name as handle. options and args is also sent
        into the api
        '''
        # Should fail if None
        if(client_name == None):
            raise LinxError("Client Name must not be None")
        ref = self.wrapper.linx_open(client_name, options, args)
        if not ref:
            raise LinxError("Linx exited in fail state when initializing")
        self.instance = ref

    def hunt(self, hunt_path, hunt_signal):
        '''
        Hunt for linx node.

        Hunts for server on hunt_path. Return signal is either hunt_signal or
        LINX_OS_HUNT_SIG if hunt_signal is set to None
        '''
        #Should fail if None
        if(hunt_path == None):
            raise LinxError("HuntPath must not be None")
        state = self.wrapper.linx_hunt(self.instance, hunt_path, hunt_signal)
        if(state == -1):
            raise LinxError("Linx exited in fail state when hunting for server " + hunt_path)
        return state

    def receive_w_tmo(self, sig, timeout=None, sigsel=LINX_NO_SIG_SEL):
        '''
        Receive signal using timeout as timout limit if set.

        receive signal declared in sigsel within timeout. Method will return None
        if no signal is recieved within timeout
        '''
        sp = self.receive_pointer_w_tmo(sig, timeout, sigsel)
        if(not sp):
            return None
        return sp.contents

    def receive_pointer_w_tmo(self, sig, timeout=None, sigsel=LINX_NO_SIG_SEL):
        '''
        receive pointer containing signal using timout as timeout if set.

        Same as receive_w_tmo but returns pointer instead for signal (useful when casting)
        '''
        state = -1
        spp = pointer(pointer(sig))
        self.wrapper.set_signal_class(sig.__class__)
        if(timeout == None):
            state = self.wrapper.linx_receive(self.instance, spp, sigsel)
        else:
            state = self.wrapper.linx_receive_w_tmo(self.instance, spp, timeout, sigsel)
        if(state == -1):
            raise LinxError("Linx exited in fail state when waiting for signal")
        sp = spp.contents
        return sp

    def find_sender(self, signal):
        '''
        Find sender for signal.

        Looks for the sender of signal
        '''
        #Should fail if None
        if(signal == None):
            raise LinxError("Signal cannot be None")
        self.wrapper.set_signal_class(signal.__class__)
        spp = pointer(pointer(signal))
        sender = self.wrapper.linx_sender(self.instance, spp)
        if(sender == 0):
            raise LinxError(("Linx returned errorstate %d", sender))
        return sender

    def attach(self, signal, server):
        '''
        Attach to linx node.

        Method to get notification when server is terminated
        '''
        # None means use default
        if(signal == None):
            spp = None
        else:
            spp = pointer(pointer(signal))
        state = self.wrapper.linx_attach(self.instance, spp, server)
        if(state == 0):
            raise LinxError("Linx failed to attach to server with ID " + str(server))
        return state

    def detach(self, reference):
        '''
        Detach from linx node.

        Method to detach attached session
        '''
        attref = pointer(c_uint(reference))
        return self.wrapper.linx_detach(self.instance, attref)

    def alloc(self, signal):
        '''
        Allocate bufferspace for signal.

        Method to allocate buffer space for signal to send
        '''
        # TODO We shouldnt accept a signal, that is not intuitive
        self.wrapper.set_signal_class(signal.__class__)
        sp = self.wrapper.linx_alloc(self.instance, sizeof(signal), signal.sig_no)
        if(not sp):
            raise LinxError("Linx failed to alloc signal")
        return sp.contents

    def free(self, signal):
        '''
        Free allocated buffermemory for signal.

        Method to free up signal buffer in linx.
        '''
        spp = pointer(pointer(signal))
        self.wrapper.set_signal_class(signal.__class__)
        return self.wrapper.linx_free_buf(self.instance, spp)

    def send(self, signal, to_id, from_id=None):
        '''
        Send signal to to_id.

        Method to send signal to target, the method will "consume" the signal,
        freeing the linx bufferspace
        '''
        #Should fail if None
        state = -1
        if(signal == None):
            raise LinxError("Signal cannot be None")
        spp = pointer(pointer(signal))
        if(from_id == None):
            state = self.wrapper.linx_send(self.instance, spp, to_id)
        else:
            state = self.wrapper.linx_send_w_s(self.instance, spp, from_id, to_id)
        signal = None
        if(state == -1):
            raise LinxError("LinxAdapter failed to send signal")
        return state

    def close(self):
        '''
        Close linx socket.

        Method to close linx connection 
        '''
        state = self.wrapper.linx_close(self.instance)
        if state == -1:
            raise LinxError("Linx failed to close")
        self.instance = None
        return state

    def get_spid(self):
        '''
        get_spid
        Method to get linx instance ID
        '''
        return self.wrapper.linx_get_spid(self.instance)

class LinxError(Exception):
    '''
    Standard exception thrown by linx.
    '''
    def __init__(self, value):
        '''
        Constructor.
        '''
        super(LinxError, self).__init__()
        self.value = value

    def __str__(self):
        '''
        To string method.
        '''
        return repr(self.value)
