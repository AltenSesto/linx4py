'''
Created on 24 okt 2013

@author: Bjorn Arnelid
'''

from ctypes import POINTER, cast

signals = { }

def castToCorrect(pointer):
    sig_no = pointer.contents.sig_no
    global signals
    SignalClass = signals[sig_no]
    casted = cast(pointer, POINTER(SignalClass))
    return casted.contents

def addSignal(sig_no, SignalClass):
    global signals
    signals[sig_no] = SignalClass