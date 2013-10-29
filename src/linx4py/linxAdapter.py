'''
Created on 15 okt 2013

@author: Bjorn Arnelid
'''

from ctypes import pointer, sizeof, c_uint
from linxWrapper import LinxWrapper
from linxConstants import LINX_NO_SIG_SEL


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
    
    def receiveWTMO(self, sig, timeout = None, sigsel = LINX_NO_SIG_SEL):
        '''
        receiveWTMO
        receive signal declared in sigsel within timeout. Method will return None
        if no signal is recieved within timeout
        '''
        sp = self.receivePointerWTMO(sig, timeout, sigsel)
        if(not sp):
            return None
        return sp.contents
    
    def receivePointerWTMO(self, sig, timeout = None, sigsel = LINX_NO_SIG_SEL):
        '''
        recievePointerWTMO
        Same as receiveWTMO but returns pointer instead for signal (useful when casting)
        '''
        state = -1
        spp = pointer(pointer(sig))
        self.wrapper.setSignalClass(sig.__class__)
        if(timeout == None):
            state = self.wrapper.linx_receive(self.instance, spp, sigsel)
        else:
            state = self.wrapper.linx_receive_w_tmo(self.instance, spp, timeout, sigsel)
        if(state == -1):
            raise LinxException("Linx exited in fail state when waiting for signal")
        sp = spp.contents
        return sp

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
        return state
    
    def detach(self, reference):
        '''
        detach
        Method to detach attached session
        '''
        attref = pointer(c_uint(reference))
        return self.wrapper.linx_detach(self.instance, attref)
        
    def alloc(self, signal):
        '''
        alloc
        Method to allocate buffer space for signal to send
        '''
        # TODO We shouldnt accept a signal, that is not intuitive
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
        
    def send(self, signal, toID, fromID = None):
        '''
        send
        Method to send signal to target, the method will "consume" the signal, 
        freeing the linx bufferspace
        '''
        #Should fail if None
        state = -1
        if(signal == None):
            raise LinxException("Signal cannot be None")
        spp = pointer(pointer(signal))
        if(fromID == None):
            state = self.wrapper.linx_send(self.instance, spp, toID)
        else:
            state = self.wrapper.linx_send_w_s(self.instance, spp, fromID, toID)
        signal = None
        if(state == -1):
            raise LinxException("LinxAdapter failed to send signal")
        return state
    
    def close(self):
        state = self.wrapper.linx_close(self.instance)
        if state == -1:
            raise LinxException("Linx failed to close")
        self.instance = None
        return state
    
    def getSPID(self):
        '''
        getSPID
        Method to get linx instance ID
        '''
        return self.wrapper.linx_get_spid(self.instance)

class LinxException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)