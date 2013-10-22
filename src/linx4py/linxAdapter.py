'''
Created on 15 okt 2013

@author: Bjorn Arnelid
'''

from ctypes import pointer, sizeof
from linxWrapper import LinxWrapper


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
        
    def open(self, clientName,options, args):
        '''
        open
        Opens linx socket using clientName as handle. options and args is also sent
        into the api
        '''
        # Should fail if None
        if(clientName == None):
            raise LinxException("Client Name must not be None")
        ref = self.wrapper.linx_open(clientName,options,None)
        if not ref:
            raise LinxException("Linx exited in fail state when initializing")
        self.instance = ref
                
    def hunt(self, huntPath, huntSignal):
        '''
        hunt
        Hunts for server on huntPath. Return signal is either huntSignal or 
        LINX_OS_HUNT_SIG if huntSignal is set to None
        '''
        #Should fail if None
        if(huntPath == None):
            raise LinxException("HuntPath must not be None")
        state = self.wrapper.linx_hunt(self.instance, huntPath, huntSignal)
        if(state == -1):
            raise LinxException("Linx exited in fail state when hunting for server " + huntPath)
        return state
    
    def receiveWTMO(self, sig, timeout, sigsel):
        '''
        receiveWTMO
        receive signal declared in sigsel within timeout. Method will throw 
        LinxException if no signal is received before timeout
        '''
        spp = pointer(pointer(sig))
        self.wrapper.setSignalClass(sig.__class__)
        state = self.wrapper.linx_receive_w_tmo(self.instance, spp, timeout, sigsel)
        if(state == -1):
            raise LinxException("Linx exited in fail state when waiting for signal")
        if(not spp.contents):
            return None
        sp = spp.contents
        return sp.contents
    
    def findSender(self, signal):
        '''
        findSender
        Looks for the sender of signal
        '''
        #Should fail if None
        if(signal == None):
            raise LinxException("Signal cannot be None")
        self.wrapper.setSignalClass(signal.__class__)
        spp = pointer(pointer(signal))
        sender = self.wrapper.linx_sender(self.instance, spp)
        if(sender == 0):
            raise LinxException(("Linx returned errorstate %d", sender))
        return sender
    
    def attach(self, signal, server):
        '''
        attach
        Method to get notification when server is terminated
        '''
        # None means use default
        if(signal == None):
            spp = None
        else:
            spp = pointer(pointer(signal))
        state = self.wrapper.linx_attach(self.instance, spp, server)
        if(state == 0):
            raise LinxException("Linx failed to attach to server with ID " + str(server))
        
    def alloc(self, signal):
        '''
        alloc
        Method to allocate buffer space for signal to send
        '''
        self.wrapper.setSignalClass(signal.__class__)
        sp = self.wrapper.linx_alloc(self.instance, sizeof(signal), signal.sig_no)
        if(not sp):
            raise LinxException("Linx failed to alloc signal")
        return sp.contents
    
    def free(self, signal):
        '''
        free
        Method to free up signal buffer in linx.
        '''
        spp = pointer(pointer(signal))
        self.wrapper.setSignalClass(signal.__class__)
        return self.wrapper.linx_free_buf(self.instance, spp)
        
    def send(self, signal, to):
        '''
        send
        Method to send signal to target
        '''
        #Should fail if None
        if(signal == None):
            raise LinxException("Signal cannot be None")
        spp = pointer(pointer(signal))
        state = self.wrapper.linx_send(self.instance, spp, to)
        if(state == -1):
            raise LinxException("LinxAdapter failed to send signal")
        return state
    
class LinxException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)