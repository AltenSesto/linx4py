'''
Created on 22 okt 2013

@author: Bjorn Arnelid
'''

from linxAdapter import LinxAdapter
from linxWrapper import BaseSignal
from linxConstants import LINX_OS_HUNT_SIG_SEL, LINX_NO_SIG_SEL

class Linx(object):
    '''
    Class for communicating with other systems through Linx signals. 
    '''
    adapter = None

    def __init__(self, name):
        '''
        Constructor
        Sets up default linx socket on computer with the name provided
        '''
        self.adapter = LinxAdapter()
        self.adapter.open(name, 0, None)
        
    def __del__(self):
        if(not self.adapter.instance == None):
            self.adapter.close()
        self.adapter = None
        
    def findServer(self, name, timeout):
        '''
        findServer
        Hunts for server with name and returns serverID
        '''
        
        self.adapter.hunt(name, None)
        huntSig = LINX_OS_HUNT_SIG_SEL
        signal = self.adapter.receiveWTMO(BaseSignal(), timeout, huntSig)
        return self.adapter.findSender(signal)
        
    def createSignal(self, signalClass, sigNo):
        sig = signalClass()
        sig.sig_no = sigNo
        return self.adapter.alloc(sig)
    
    def send(self, signal, serverID):
        '''
        send
        Sends signal to server, The signal is consumed and cannot be used again after send
        '''
        self.adapter.send(signal, serverID)

    
    def receive(self, signal, timeout):
        '''
        receive
        Receives signal from server within timeout
        '''
        huntSig = LINX_NO_SIG_SEL
        return self.adapter.receiveWTMO(signal, timeout, huntSig)
        
    