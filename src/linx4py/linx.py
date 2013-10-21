'''
Created on 15 okt 2013

@author: bjorn
'''

from ctypes import pointer
from linxWrapper import LinxWrapper, LINX_SIGNAL


class Linx(object):
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
        # Linx library will crash and burn when name is NULL
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
        #TODO huntsignal is pointer-to-pointer
        #Linx library will crash and burn when huntPath is NULL
        if(huntPath == None):
            raise LinxException("HuntPath must not be None")
        state = self.wrapper.linx_hunt(self.instance, huntPath, huntSignal)
        if(state == -1):
            raise LinxException("Linx exited in fail state when hunting for server " + huntPath)
        return state
    
    def receiveWTMO(self, timeout, sigsel):
        '''
        receiveWTMO
        receive signal declared in sigsel within timeout. Method will throw 
        LinxException if no signal is received before timeout
        '''
        signal = LINX_SIGNAL()
        spp = pointer(pointer(signal))
        state = self.wrapper.linx_receive_w_tmo(self.instance, spp, timeout, sigsel)
        if(state == -1):
            raise LinxException("Linx exited in fail state when waiting for signal")
        if(not spp.contents):
            raise LinxException("Linx timed out waiting for signal")
        sp = spp.contents
        return sp.contents
    
    def findSender(self, signal):
        '''
        findSender
        Looks for the sender of signal
        '''
        spp = pointer(pointer(signal))
        sender = self.wrapper.linx_sender(self.instance, spp)
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
        
    def send(self):
        '''
        send
        '''
        self.wrapper.linx_send()
        raise LinxException("Linx failed to send signal")
    
class LinxException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)
