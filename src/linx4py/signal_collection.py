'''
Created on 24 okt 2013

@author: Bjorn Arnelid
'''

from ctypes import POINTER, cast

from linx4py.linx_adapter import LinxError
from linx4py.linx_constants import BaseSignal

class SignalCollection(object):
    '''
    SignalCollection
    Classed used for keeping signaltypes in order to convert them during 
    send and receive
    '''
    def __init__(self):
        self._signals = { }
        self._sig_table = { }
        # Add Hunt signal
        self._signals[252] = BaseSignal
        self._sig_table[BaseSignal] = 252

    def cast_to_correct(self, pointer):
        '''
        cast_to_correct
        Method to cast Union to correct sub-signal
        '''
        if(not pointer):
            return None
        sig_no = pointer.contents.sig_no
        try:
            SignalClass = self._signals[sig_no]
            casted = cast(pointer, POINTER(SignalClass))
            signal = casted.contents
            name = self._get_signal_reference_name(signal, sig_no)
            if name == None:
                return signal
            return getattr(signal, name)
        except KeyError:
            raise LinxError("Signal %d must be in collection" % sig_no)

    def _get_signal_reference_name(self, signal, sig_no):
        '''
        _get_signal_reference_name
        private method to get field name containing signal for sig_no
        '''
        try:
            for name, value in signal._fields_:
                if not name == 'sig_no':
                    ref = self._sig_table[value]
                    if ref == sig_no:
                        return name
        except KeyError:
            raise LinxError("Signal %d must be in collection" % sig_no)

    def add_union(self, SignalClass):
        '''
        add_union
        Method to add union containing _signals used by signalCollection
        '''
        for name, Value in SignalClass._fields_:
            if not name == 'sig_no':
                signal = Value()
                self._sig_table[Value] = signal.sig_no
                self._signals[signal.sig_no] = SignalClass

    def create_union_from_signal(self, signal):
        '''
        createUnionFromSignal
        Creates Union containing signal as field
        '''
        sig_no = signal.sig_no
        Cls = self._signals[sig_no]
        return_signal = Cls()
        name = self._get_signal_reference_name(return_signal, sig_no)
        setattr(return_signal, name, signal)
        return return_signal
