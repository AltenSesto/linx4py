'''
Created on 28 okt 2013

@author: bjorn
'''
import unittest
from ctypes import pointer

from linx4py.signalCollection import SignalCollection
from linx4py.linxAdapter import LinxException
from signals import LINX_SIGNAL, REQUEST_SIGNAL, REQUEST_SIGNAL_NO, REPLY_SIGNAL_NO

class SignalCollectionTest(unittest.TestCase):

    def testAddSignalContainsRequest(self):
        sc = SignalCollection()
        request = REQUEST_SIGNAL()
        sc.addSignal(LINX_SIGNAL)
        signal = sc.createSignal(REQUEST_SIGNAL_NO)
        self.assertEqual(request.sig_no, 0x3340)
        self.assertEqual(request.sig_no, signal.sig_no)

    def testCastToCorrectSignal(self):
        sc = SignalCollection()
        sc.addSignal(LINX_SIGNAL)
        sig = LINX_SIGNAL()
        sig.sig_no = REPLY_SIGNAL_NO
        sig.reply.seqno = 1
        sp = pointer(sig)
        signal = sc.castToCorrect(sp)
        self.assertEqual(signal.sig_no, REPLY_SIGNAL_NO)
        self.assertEqual(signal.seqno, 1)

    def testCastToNonExisting(self):
        sc = SignalCollection()
        sig = LINX_SIGNAL()
        # Intresting, sc remembered old signals.... 
        sig.sig_no = 55
        sp = pointer(sig)
        self.failUnlessRaises(LinxException, sc.castToCorrect, sp)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()