'''
Created on 24 okt 2013

@author: Bjorn Arnelid
'''

from ctypes import POINTER, cast

from linxAdapter import LinxException
from linxWrapper import BaseSignal

class SignalCollection(object):
    '''
    SignalCollection
    Classed used for keeping signaltypes in order to convert them during 
    send and receive
    '''
    def __init__(self):
        self.signals = { }
        self.sigTable = { }
        # Add Hunt signal
        self.signals[252] = BaseSignal
        self.sigTable[BaseSignal] = 252

    def castToCorrect(self, pointer):
        '''
        castToCorrect
        Method to cast Union to correct sub-signal
        '''
        if(not pointer):
            return None
        sig_no = pointer.contents.sig_no
        try:
            SignalClass = self.signals[sig_no]
            casted = cast(pointer, POINTER(SignalClass))
            signal = casted.contents
            name = self._getSignalReferenceName(signal, sig_no)
            if name == None:
                return signal
            return getattr(signal, name)
        except KeyError:
            raise LinxException("Signal %d must be in collection" % sig_no)

    def _getSignalReferenceName(self, signal, sigNo):
        '''
        _getSignalReferenceName
        private method to get field name containing signal for sig_no
        '''
        try:
            for name, value in signal._fields_:
                if not name == 'sig_no':
                    ref = self.sigTable[value]
                    if ref == sigNo:
                        return name
        except KeyError:
            raise LinxException("Signal %d must be in collection" % sigNo)

    def addUnion(self, SignalClass):
        '''
        addUnion
        Method to add union containing signals used by signalCollection
        '''
        for name, Value in SignalClass._fields_:
            if not name == 'sig_no':
                signal = Value()
                self.sigTable[Value] = signal.sig_no
                self.signals[signal.sig_no] = SignalClass

    def createUnionfromSignal(self, signal):
        '''
        createUnionFromSignal
        Creates Union containing signal as field
        '''
        sigNo = signal.sig_no
        Cls = self.signals[sigNo]
        returnSignal = Cls()
        name = self._getSignalReferenceName(returnSignal, sigNo)
        setattr(returnSignal, name, signal)
        return returnSignal
