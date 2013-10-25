'''
Created on 24 okt 2013

@author: Bjorn Arnelid
'''

from ctypes import POINTER, cast


class SignalCollection(object):
    signals = { }
    
    def castToCorrect(self, pointer):
        if(not pointer):
            return None
        sig_no = pointer.contents.sig_no
        SignalClass = self.signals[sig_no]
        casted = cast(pointer, POINTER(SignalClass))
        return casted.contents
    
    def addSignal(self, sig_no, SignalClass):
        self.signals[sig_no] = SignalClass
        
    def createSignal(self, sig_no, sig_class = None):
        if not sig_no in self.signals:
            self.addSignal(sig_no, sig_class)
        Cls = self.signals[sig_no]
        sig = Cls()
        sig.sig_no = sig_no
        return sig
            