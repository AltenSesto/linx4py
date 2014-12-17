# -------------------------------------------------------------------------------
# Copyright (c) 2013 Alten AB.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
#
# Contributors:
#     Bjorn Arnelid - initial API and implementation
# -------------------------------------------------------------------------------
'''
Module for using linx in python.

Use Linx object to send and receive linx signals.
'''
from ctypes import memmove, addressof, sizeof, c_uint
from linx4py.linx_adapter import LinxAdapter
from linx4py.linx_wrapper import BaseSignal
from linx4py.linx_constants import LINX_OS_HUNT_SIG_SEL
from linx4py.signal_collection import SignalCollection


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
        self.signal_collection = SignalCollection()

    def __del__(self):
        '''
        Destructor
        closes linx socket and frees adapter and signal collection for garbage
        collection
        '''
        if(self.adapter.instance is not None):
            self.adapter.close()
        self.adapter = None
        self.signal_collection = None

    def hunt(self, name, timeout):
        '''
        findServer
        Hunts for server with name and returns serverID
        '''
        self.adapter.hunt(name, None)
        hunt_sig = LINX_OS_HUNT_SIG_SEL
        signal = self.adapter.receive_w_tmo(BaseSignal(), timeout, hunt_sig)
        if(signal is None):
            return None
        return self.adapter.find_sender(signal)

    def send(self, signal, target_id, sender_id=None):
        '''
        send
        Sends signal to_id server, The signal is consumed and cannot be used
        again after send
        '''
        signal_union = self.signal_collection.create_union_from_signal(signal)
        send_union = self.adapter.alloc(signal_union)
        buffer_size = min(sizeof(signal_union), sizeof(send_union))
        memmove(addressof(send_union), addressof(signal_union), buffer_size)
        self.adapter.send(send_union, target_id, sender_id)

    def get_sender(self, signal):
        '''
        get_sender
        Gets sender ID from signal
        '''
        return self.adapter.find_sender(signal)

    def receive(self, timeout=None, sig_selection=None):
        '''
        receive
        Receives signal from server within timeout
        '''
        signal = BaseSignal()
        if sig_selection is not None:
            SigSelectArray = c_uint * len(sig_selection)
            sig_selection = SigSelectArray(*sig_selection)
        sp = self.adapter.receive_pointer_w_tmo(signal, timeout, sig_selection)
        return self.signal_collection.cast_to_correct(sp)

    def add_union_type(self, SignalClass):
        '''
        addSignalType
        Add a signal class to signal_collection, signal can then be collected
        dynamically by looking at the signalID
        '''
        self.signal_collection.add_union(SignalClass)
