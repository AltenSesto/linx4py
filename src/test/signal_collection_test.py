'''
Created on 28 okt 2013

@author: bjorn
'''
import unittest
import xmlrunner
from ctypes import pointer

from linx4py.signal_collection import SignalCollection
from linx4py.linx_adapter import LinxError
from test.signals import LINX_SIGNAL, REQUEST_SIGNAL, REPLY_SIGNAL_NO, BASE_SIGNAL

class SignalCollectionTest(unittest.TestCase):

    def testAddUnionContainsRequest(self):
        sc = SignalCollection()
        sc.add_union(LINX_SIGNAL)
        request = REQUEST_SIGNAL()
        sp = pointer(request)
        signal = sc.cast_to_correct(sp)
        self.assertEqual(request.sig_no, signal.sig_no)
        
    def testSignalCollectionAlwaysContainHunt(self):
        sc = SignalCollection()
        hunt = BASE_SIGNAL()
        hunt.sig_no = 252
        sp = pointer(hunt)
        outSignal = sc.cast_to_correct(sp)
        self.assertEqual(252, outSignal.sig_no)

    def testCastToCorrectSignal(self):
        sc = SignalCollection()
        sc.add_union(LINX_SIGNAL)
        sig = LINX_SIGNAL()
        sig.sig_no = REPLY_SIGNAL_NO
        sig.reply.seqno = 1
        sp = pointer(sig)
        signal = sc.cast_to_correct(sp)
        self.assertEqual(signal.sig_no, REPLY_SIGNAL_NO)
        self.assertEqual(signal.seqno, 1)

    def testCastToNonExisting(self):
        sc = SignalCollection()
        sig = LINX_SIGNAL()
        # Intresting, sc remembered old signals.... 
        sig.sig_no = 55
        sp = pointer(sig)
        self.failUnlessRaises(LinxError, sc.cast_to_correct, sp)
        
    def testCreateUnionFromSignalReturnsUnion(self):
        sc = SignalCollection()
        sc.add_union(LINX_SIGNAL)
        inSignal = REQUEST_SIGNAL()
        outSignal = sc.create_union_from_signal(inSignal)
        self.assertEqual(inSignal.sig_no, outSignal.sig_no)
        
    def testCreateUnionFromSignalReturnsCorrectData(self):
        sc = SignalCollection()
        sc.add_union(LINX_SIGNAL)
        inSignal = REQUEST_SIGNAL()
        inSignal.seqno = 2
        outSignal = sc.create_union_from_signal(inSignal)
        self.assertEqual(inSignal.seqno, outSignal.request.seqno)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="unittests"))