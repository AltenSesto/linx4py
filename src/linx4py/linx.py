'''
Created on 22 okt 2013

@author: Bjorn Arnelid
'''
from ctypes import memmove, addressof, sizeof, c_uint
from linxAdapter import LinxAdapter
from linxWrapper import BaseSignal
from linxConstants import LINX_OS_HUNT_SIG_SEL
from signalCollection import SignalCollection

class Linx(object):
    '''
    Class for communicating with other systems through Linx signals. 
    '''

    def __init__(self, name):
        '''
        Constructor
        Sets up default linx socket on computer with the name provided
        '''
        self.adapter = LinxAdapter()
        self.adapter.open(name, 0, None)
        self.signalCollection = SignalCollection()
        
    def __del__(self):
        '''
        Destructor
        closes linx socket and frees adapter and signal collection for garbage collection
        '''
        if(not self.adapter.instance == None):
            self.adapter.close()
        self.adapter = None
        self.signalCollection = None
        
    def hunt(self, name, timeout):
        '''
        findServer
        Hunts for server with name and returns serverID
        '''
        self.adapter.hunt(name, None)
        huntSig = LINX_OS_HUNT_SIG_SEL
        signal = self.adapter.receiveWTMO(BaseSignal(), timeout, huntSig)
        return self.adapter.findSender(signal)
    
    def send(self, signal, targetID, senderID = None):
        '''
        send
        Sends signal toID server, The signal is consumed and cannot be used again after send
        '''
        signalUnion = self.signalCollection.createUnionfromSignal(signal)
        sendUnion = self.adapter.alloc(signalUnion)
        bufferSize = min(sizeof(signalUnion), sizeof(sendUnion))
        memmove(addressof(sendUnion), addressof(signalUnion), bufferSize)
        self.adapter.send(sendUnion, targetID, senderID)

    def getSender(self, signal):
        '''
        getSender
        Gets sender ID from signal
        '''
        return self.adapter.findSender(signal)
    
    
    def receive(self, timeout = None, sigSelection = None):
        '''
        receive
        Receives signal from server within timeout
        '''
        signal = BaseSignal()
        if not sigSelection == None:
            SigSelectArray = c_uint * len(sigSelection)
            sigSelection = SigSelectArray(*sigSelection)
        sp = self.adapter.receivePointerWTMO(signal, timeout, sigSelection)
        return self.signalCollection.castToCorrect(sp)
        
    def addUnionType(self, SignalClass):
        '''
        addSignalType
        Add a signal class to signalCollection, signal can then be collected dynamically 
        by looking at the signalID
        '''
        self.signalCollection.addUnion( SignalClass)