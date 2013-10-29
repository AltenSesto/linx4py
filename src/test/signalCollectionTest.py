'''
Created on 28 okt 2013

@author: bjorn
'''
import unittest
import xmlrunner
from ctypes import pointer

from linx4py.signalCollection import SignalCollection
from linx4py.linxAdapter import LinxException
from signals import LINX_SIGNAL, REQUEST_SIGNAL, REQUEST_SIGNAL_NO, REPLY_SIGNAL_NO, BASE_SIGNAL

class SignalCollectionTest(unittest.TestCase):

    def testAddUnionContainsRequest(self):
        sc = SignalCollection()
        request = REQUEST_SIGNAL()
        sc.addUnion(LINX_SIGNAL)
        signal = sc.createSignal(REQUEST_SIGNAL_NO)
        self.assertEqual(request.sig_no, 0x3340)
        self.assertEqual(request.sig_no, signal.sig_no)
        
    def testSignalCollectionAlwaysContainHunt(self):
        sc = SignalCollection()
        hunt = BASE_SIGNAL()
        hunt.sig_no = 252
        sp = pointer(hunt)
        outSignal = sc.castToCorrect(sp)
        self.assertEqual(252, outSignal.sig_no)

    def testCastToCorrectSignal(self):
        sc = SignalCollection()
        sc.addUnion(LINX_SIGNAL)
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
        
    def testCreateUnionFromSignalReturnsUnion(self):
        sc = SignalCollection()
        sc.addUnion(LINX_SIGNAL)
        inSignal = REQUEST_SIGNAL()
        outSignal = sc.createUnionfromSignal(inSignal)
        self.assertEqual(inSignal.sig_no, outSignal.sig_no)
        
    def testCreateUnionFromSignalReturnsCorrectData(self):
        sc = SignalCollection()
        sc.addUnion(LINX_SIGNAL)
        inSignal = REQUEST_SIGNAL()
        inSignal.seqno = 2
        outSignal = sc.createUnionfromSignal(inSignal)
        self.assertEqual(inSignal.seqno, outSignal.request.seqno)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="unittests"))