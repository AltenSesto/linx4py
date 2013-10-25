'''
Created on 24 okt 2013

@author: bjorn
'''

from threading import Thread

from linxWrapper import BaseSignal
from linxConstants import LINX_NO_SIG_SEL
from signalCollection import SignalCollection

class AsyncReceiver(Thread):
    '''
    classdocs
    '''
    
    # Lets try to receive every second so that Thread does not become to unresponsive
    receiveTimeout = 1000

    def __init__(self,adapter):
        '''
        Constructor
        '''
        Thread.__init__(self)
        self.signals = []
        self.signalCollection = SignalCollection()
        self.adapter = adapter
        
    def initReceive(self, sigsel = LINX_NO_SIG_SEL):
        '''
        Start receiving signals, note that this will tie up the linx socket making it 
        impossible to do any other operations on it
        '''
        self.sigsel = sigsel
        self.start()
        
    def run(self):
        self.main()
            
    def main(self):
        '''
        lets think about blocking signals....
        '''
        self.shouldQuit = False
        while(not self.shouldQuit):
            sig = BaseSignal()
            sp = self.adapter.receivePointerWTMO(sig, self.receiveTimeout, self.sigsel)
            self.signals.append(sp)
            
    def addSignalType(self, signalID, SignalClass):
        '''
        addSignalType
        Add a signal class to signalCollection, signal can then be collected dynamically 
        by looking at the signalID
        '''
        self.signalCollection.addSignal(signalID, SignalClass)
    
    def receive(self):
        '''
        Get and remove first signal in signal list
        '''
        if(not self.signals):
            return None
        sp = self.signals.pop(0)
        return self.signalCollection.castToCorrect(sp)

    def stopReceive(self):
        '''
        Stop Async reciever
        '''
        self.shouldQuit = True