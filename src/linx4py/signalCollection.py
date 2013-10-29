'''
Created on 24 okt 2013

@author: Bjorn Arnelid
'''

from ctypes import POINTER, cast

from linxAdapter import LinxException
from linxWrapper import BaseSignal

class SignalCollection(object):
    
    def __init__(self):
        self.signals = { }
        self.sigTable = { }
        # Add Hunt signal
        self.signals[252] = BaseSignal
        self.sigTable[BaseSignal] = 252
    
    def castToCorrect(self, pointer):
        if(not pointer):
            return None
        sig_no = pointer.contents.sig_no
        try:
            SignalClass = self.signals[sig_no]
            casted = cast(pointer, POINTER(SignalClass))
            signal = casted.contents
            name = self.getSignalReferenceName(signal, sig_no)
            if name == None:
                return signal
            return getattr(signal, name)
        except KeyError:
            raise LinxException("Signal %d must be in collection" % sig_no)
        
    def getSignalReferenceName(self, signal, sigNo):
        try:
            for name, value in signal._fields_:
                if not name == 'sig_no':
                    ref = self.sigTable[value]
                    if ref == sigNo:
                        return name
        except KeyError:
            raise LinxException("Signal %d must be in collection" % sigNo)
    
    def addUnion(self, SignalClass):
        for name, Value in SignalClass._fields_:
            if not name == 'sig_no':
                signal = Value()
                self.sigTable[Value] = signal.sig_no
                self.signals[signal.sig_no] = SignalClass

    def createUnionfromSignal(self, signal):
        sigNo = signal.sig_no
        Cls = self.signals[sigNo]
        returnSignal = Cls()
        name = self.getSignalReferenceName(returnSignal, sigNo)
        setattr(returnSignal, name, signal)
        return returnSignal
