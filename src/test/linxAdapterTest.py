'''
Created on 15 okt 2013

@author: Bjorn Arnelid
'''
import unittest
import xmlrunner
from ctypes import POINTER, cast

from linx4py.linx_adapter import LinxAdapter, LinxError
from linx4py.linx_wrapper import LinxWrapper, LINX
from linx4py.linx_constants import LINX_OS_HUNT_SIG_SEL, LINX_NO_SIG_SEL

import server
from signals import LINX_SIGNAL, BASE_SIGNAL

class LinxAdapterTest(unittest.TestCase):
    '''
    Unit tests for linx module in linx4py, requires following:
    Linx2.5.1 installed on current computer
    LinxAdapter kernel modules loaded into system
    '''
    

    @classmethod
    def setUpClass(self):
        self.server_name = "example_server"
        self.process = server.get_server(self.server_name)
        
    @classmethod
    def tearDownClass(self):
        self.process.stop()

    def testLinxShouldThrowExceptionifNameisNone(self):
        linxInstance = LinxAdapter()
        self.failUnlessRaises(LinxError, linxInstance.open, None, 0, None)

    def testLinxShouldThrowExceptionWhenFail(self):
        linxInstance = LinxAdapter()
        linxInstance.wrapper = TestOpenWrapper()
        self.failUnlessRaises(LinxError, linxInstance.open, "MyClientName", 0, None)

    def open_linx(self, clientName):
        linxInstance = LinxAdapter()
        linxInstance.open(clientName, 0, None)
        return linxInstance
    
    def testHuntThrowsExceptionWhenNameNone(self):
        linxInstance = self.open_linx("MyClientName")
        self.failUnlessRaises(LinxError, linxInstance.hunt, None, None)
     
    def testHuntReturns0(self):
        linxInstance = self.open_linx("MyClientName")
        status = linxInstance.hunt(self.server_name, None)
        self.assertEqual(0, status, ("Hunt should return 0 but returns %d", status))
        
    def testHuntThrowsExceptionWhenNotOpen(self):
        linxInstance = self.open_linx("MyClientName")
        linxInstance.wrapper = TestHuntWrapper() 
        self.failUnlessRaises(LinxError, linxInstance.hunt, self.server_name, None)

    def testRecieveWTMONoneWhenTimeOut(self):
        linxInstance = self.open_linx("MyClientName")
        linxInstance.hunt("not_existing_server", None)
        signal = linxInstance.receive_w_tmo(LINX_SIGNAL(), 500, LINX_OS_HUNT_SIG_SEL)
        self.assertIsNone(signal, "Should return None but is " + str(signal))
    
    def testRecieveWTMOReturnsOSHuntSignal(self):
        linxInstance = self.open_linx("MyClientName")
        linxInstance.hunt(self.server_name, None)
        signal =  linxInstance.receive_w_tmo(LINX_SIGNAL(), 10000, LINX_OS_HUNT_SIG_SEL)
        self.assertEquals(251, signal.sig_no, "Function exited with Errorcode")
        
    def testFindSenderFromSignal(self):
        linxInstance = self.open_linx("MyClientName")
        linxInstance.hunt(self.server_name, None)
        signal =  linxInstance.receive_w_tmo(LINX_SIGNAL(), 10000, LINX_OS_HUNT_SIG_SEL)
        self.assertNotEqual(0, linxInstance.find_sender(signal))
        
    def testFindSenderThrowErrorWhenFail(self):
        linxInstance = self.open_linx("MyClientName")
        linxInstance.wrapper = TestSenderWrapper()
        s = LINX_SIGNAL()
        self.failUnlessRaises(LinxError, linxInstance.find_sender, s)
        
    def testThrowErrorWhenAttachFails(self):
        linxInstance = self.open_linx("MyClientName")
        linxInstance.hunt(self.server_name, None)
        linxInstance.receive_w_tmo(LINX_SIGNAL(), 10000, LINX_OS_HUNT_SIG_SEL)
        self.failUnlessRaises(LinxError, linxInstance.attach, None, 0)
         
    def testAttachToServer(self):
        linxInstance = self.open_linx("MyClientName")
        linxInstance.hunt(self.server_name, None)
        signal = linxInstance.receive_w_tmo(LINX_SIGNAL(), 10000, LINX_OS_HUNT_SIG_SEL)
        serverID = linxInstance.find_sender(signal)
        self.assertNotEqual(0, linxInstance.attach(None, serverID))
        
    def testDetachFromServer(self):
        linxInstance = self.open_linx("MyClientName")
        linxInstance.hunt(self.server_name, None)
        signal = linxInstance.receive_w_tmo(LINX_SIGNAL(), 10000, LINX_OS_HUNT_SIG_SEL)
        serverID = linxInstance.find_sender(signal)
        ref = linxInstance.attach(None, serverID)
        state = linxInstance.detach(ref)
        self.assertNotEqual(-1, state, "State should not be -1")
        
    def findServer(self, linxInstance, name):
        linxInstance.hunt(name, None)
        signal = linxInstance.receive_w_tmo(LINX_SIGNAL(), 10000, LINX_OS_HUNT_SIG_SEL)
        return linxInstance.find_sender(signal)
        
    def testAllocReturnsSignal(self):
        linxInstance = self.open_linx("MyClientName")
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal = linxInstance.alloc(s)
        self.assertIsNotNone(signal.sig_no, "LinxAdapter should return REQUEST_SIGNAL")
        
    def testAllocThrowsExceptionWhenFails(self):
        linxInstance = self.open_linx("MyClientName")
        linxInstance.wrapper = TestAllocWrapper()
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        self.failUnlessRaises(LinxError, linxInstance.alloc, s)
        
    def testFreeBufferShouldNotReturnNegative(self):
        linxInstance = self.open_linx("MyClientName")
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal = linxInstance.alloc(s)
        self.assertNotEqual(-1, linxInstance.free(signal), "Free buffer returned errorcode -1")
        
    def testGetPID(self):
        linxInstance = self.open_linx("MyClientName")
        self.assertGreater(linxInstance.get_spid(), 0, "SPID should be greater then 0 but is %d" 
                           % linxInstance.get_spid())
        
    def testSendSignalThrowErrorWhenSignalNull(self):
        linxInstance = self.open_linx("MyClientName")
        self.findServer(linxInstance, self.server_name)
        self.failUnlessRaises(LinxError, linxInstance.send, None, 0)
        
    def testSendSignalDoesNotReturnError(self):
        linxInstance = self.open_linx("MyClientName")
        serverID = self.findServer(linxInstance, self.server_name)
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal =linxInstance.alloc(s)
        signal.request.seqno = 1
        state = linxInstance.send(signal, serverID)
        self.assertNotEqual(-1, state, "LinxAdapter send should not return -1")
        
    def testSendSignalWithOtherSenderDoNotReturnError(self):
        senderInstance = self.open_linx("MySenderName")
        receiverInstance = self.open_linx("MyReceiverName")
        receiverID = receiverInstance.get_spid()
        serverID = self.findServer(senderInstance, self.server_name)
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal =senderInstance.alloc(s)
        signal.request.seqno = 1
        senderInstance.send(signal, serverID, receiverID)
        self.assertIsNotNone(receiverInstance.receive_w_tmo(s, 10000, LINX_NO_SIG_SEL), 
                             "Received signal must not be None")
        
    def testSendSignalThrowExceptionWhenFail(self):
        linxInstance = self.open_linx("MyClientName")
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal =linxInstance.alloc(s)
        signal.request.seqno = 2
        self.failUnlessRaises(LinxError, linxInstance.send, signal, 42)
        
    def sendSignal(self, linxInstance, signalNo, serverID):
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal =linxInstance.alloc(s)
        signal.request.seqno = signalNo
        return linxInstance.send(signal, serverID)
    
    def testReplyIsResponseSignal(self):
        linxInstance = self.open_linx("MyClientName")
        serverID = self.findServer(linxInstance, self.server_name)
        self.sendSignal(linxInstance, 3, serverID)
        signal = linxInstance.receive_w_tmo(LINX_SIGNAL(), 10000, LINX_NO_SIG_SEL)
        self.assertEquals(signal.reply.sig_no, 0x3341,("LinxAdapter should return REPLY_SIGNAL but returns sig_no %d", signal.reply.sig_no))
        
    def testCanReadReplySeqno(self):
        linxInstance = self.open_linx("MyClientName")
        serverID = self.findServer(linxInstance, self.server_name)
        self.sendSignal(linxInstance, 4, serverID)
        signal = linxInstance.receive_w_tmo(LINX_SIGNAL(), 10000, LINX_NO_SIG_SEL)
        self.assertEquals(signal.reply.seqno, 4,("LinxAdapter should return REPLY_SIGNAL but returns sig_no %d", signal.reply.seqno))
        
    def testCanReceiveWithouthuntSig(self):
        linxInstance = self.open_linx("MyClientName")
        serverID = self.findServer(linxInstance, self.server_name)
        self.sendSignal(linxInstance, 5, serverID)
        signal = linxInstance.receive_w_tmo(LINX_SIGNAL(), 10000, None)
        self.assertIsNotNone(signal, "received signal should not be None!")
        
    def testCanReceiveWithoutTimeout(self):
        linxInstance = self.open_linx("MyClientName")
        serverID = self.findServer(linxInstance, self.server_name)
        self.sendSignal(linxInstance, 6, serverID)
        signal = linxInstance.receive_w_tmo(LINX_SIGNAL(), None, LINX_NO_SIG_SEL)
        self.assertIsNotNone(signal, "received signal should not be None!")
        
    def testCastSignalToOther(self):
        linxInstance = self.open_linx("MyClientName")
        serverID = self.findServer(linxInstance, self.server_name)
        self.sendSignal(linxInstance, 7, serverID)
        sp = linxInstance.receive_pointer_w_tmo(BASE_SIGNAL(), 10000, None)
        signal = cast(sp, POINTER(LINX_SIGNAL))
        self.assertEquals(7, signal.contents.reply.seqno)
        
    def testCloseLinxInstanceIsNone(self):
        linxInstance = self.open_linx("MyClientName")
        linxInstance.close()
        self.assertIsNone(linxInstance.instance, "Instance should be NullPointer after close")
        
    def testCloseLinxThrowsExceptionWhenFail(self):
        linxInstance = LinxAdapter()
        linxInstance.wrapper = TestCloseWrapper()
        linxInstance.instance = LINX()
        self.failUnlessRaises(LinxError, linxInstance.close)





class TestOpenWrapper(LinxWrapper):
    # Overrides LinxWrapper 
    # and pretends something went horribly wrong when calling linx_open
    def linx_open(self, name, options, arg):
        # Returns c NULL pointer
        return POINTER(LINX)()

class TestHuntWrapper(LinxWrapper):
    # Overrides LinxWrapper 
    # and pretends something went horribly wrong when calling linx_hunt
    def linx_hunt(self, linx, name, hunt_sig):
        return -1
    
class TestSenderWrapper(LinxWrapper):
    # Overrides LinxWrapper 
    # and pretends something went horribly wrong when calling linx_sender
    def linx_sender(self, linx, sig):
        return 0
    
class TestAllocWrapper(LinxWrapper):
    # Overrides LinxWrapper 
    # and pretends something went horribly wrong when calling linx_alloc
    def linx_alloc(self, linx, size, sig_no):
        return POINTER(LINX_SIGNAL)()
    
class TestCloseWrapper(LinxWrapper):
    # Overrides LinxWrapper 
    # and pretends something went horribly wrong when calling linx_close
    def linx_close(self, linx):
        return -1
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="unittests"))