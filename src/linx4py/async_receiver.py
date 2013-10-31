'''
Created on 24 okt 2013

@author: bjorn
'''

from threading import Thread

from linx_constants import LINX_NO_SIG_SEL, BaseSignal
from signal_collection import SignalCollection

class AsyncReceiver(Thread):
    '''
    classdocs
    '''
    
    # Lets try to receive every second so that Thread does not become to unresponsive
    receive_timeout = 1000

    def __init__(self,adapter):
        '''
        Constructor
        '''
        Thread.__init__(self)
        self._signals = []
        self.signal_collection = SignalCollection()
        self.adapter = adapter
        
    def init_receive(self, sigsel = LINX_NO_SIG_SEL):
        '''
        Start receiving _signals, note that this will tie up the linx socket making it 
        impossible to do any other operations on it
        '''
        self.sigsel = sigsel
        self.start()
        
    def run(self):
        self.main()
            
    def main(self):
        '''
        lets think about blocking _signals....
        '''
        self.should_quit = False
        while(not self.should_quit):
            sig = BaseSignal()
            sp = self.adapter.receive_pointer_w_tmo(sig, self.receive_timeout, self.sigsel)
            self._signals.append(sp)
            
    def add_union_type(self, SignalClass):
        '''
        addSignalType
        Add a signal class to signal_collection, signal can then be collected dynamically 
        by looking at the signalID
        '''
        self.signal_collection.add_union(SignalClass)
    
    def receive(self):
        '''
        Get and remove first signal in signal list
        '''
        if(not self._signals):
            return None
        sp = self._signals.pop(0)
        return self.signal_collection.cast_to_correct(sp)

    def stopReceive(self):
        '''
        Stop Async reciever
        '''
        self.should_quit = True