'''
Created on 24 okt 2013

@author: Bjorn Arnelid
'''

from ctypes import POINTER, cast

from linxAdapter import LinxException

class SignalCollection(object):
    signals = { }
    sigTable = { }
    
    def castToCorrect(self, pointer):
        if(not pointer):
            return None
        sig_no = pointer.contents.sig_no
        try:
            SignalClass = self.signals[sig_no]
            casted = cast(pointer, POINTER(SignalClass))
            signal = casted.contents
            name = self.getSignalReferenceName(signal, sig_no)
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
    
    def addSignals(self, SignalClass):
        for name, Value in SignalClass._fields_:
            if not name == 'sig_no':
                signal = Value()
                self.sigTable[Value] = signal.sig_no
                self.signals[signal.sig_no] = SignalClass
        
    def createSignal(self, sig_no, sig_class = None):
        if not sig_no in self.signals:
            self.addSignal(sig_class)
        Cls = self.signals[sig_no]
        sig = Cls()
        sig.sig_no = sig_no
        return sig
    
    def createUnionfromSignal(self, signal):
        sigNo = signal.sig_no
        Cls = self.signals[sigNo]
        returnSignal = Cls()
        name = self.getSignalReferenceName(returnSignal, sigNo)
        setattr(returnSignal, name, signal)
        return returnSignal
