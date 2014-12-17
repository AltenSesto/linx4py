# ------------------------------------------------------------------------------
# Copyright (c) 2013 Alten AB.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
#
# Contributors:
#     Bjorn Arnelid - initial API and implementation
# ------------------------------------------------------------------------------
'''
Module for asynchronous receiving of linx signals.
'''
import time
from threading import Thread

from linx4py.linx_constants import LINX_NO_SIG_SEL, BaseSignal
from linx4py.signal_collection import SignalCollection


class AsyncReceiver(Thread):
    '''
    Thread for receiving signals
    '''

    # Lets try to receive every second so that Thread does not become to
    # unresponsive
    receive_timeout = 1000

    def __init__(self, adapter):
        '''
        Constructor
        '''
        Thread.__init__(self)
        self.initializing = True
        self._signals = []
        self.signal_collection = SignalCollection()
        self.adapter = adapter

    def init_receive(self, sigsel=LINX_NO_SIG_SEL):
        '''
        Start receiving _signals, note that this will tie up the linx socket
        making it impossible to do any other operations on it
        '''
        self.should_quit = False
        self.sigsel = sigsel
        self.start()

    def run(self):
        print("Receiver: Starting")
        self.main()

    def main(self):
        '''
        Main thread.
        '''
        self.initializing = False
        while(not self.should_quit):
            sig = BaseSignal()
            sp = self.adapter.receive_pointer_w_tmo(sig, self.receive_timeout,
                                                    self.sigsel)
            self._signals.append(sp)
        self.adapter.close()
        print("Receiver: Stopping, good bye!")

    def add_union_type(self, SignalClass):
        '''
        addSignalType
        Add a signal class to signal_collection, signal can then be collected
        dynamically by looking at the signalID
        '''
        self.signal_collection.add_union(SignalClass)

    def receive(self):
        '''
        Get and remove first signal in signal list
        '''
        while self.initializing:
            time.sleep(0.001)
        if(not self._signals):
            return None
        sp = self._signals.pop(0)
        return self.signal_collection.cast_to_correct(sp)

    def stopReceive(self):
        '''
        Stop Async reciever
        '''
        while self.initializing:
            time.sleep(0.001)
        print("Receiver: Stop requested")
        self.should_quit = True
