'''
Created on 15 okt 2013

@author: Bjorn Arnelid
'''
from ctypes import POINTER, c_uint, c_int, Structure, Union
import subprocess
import unittest

from linx4py import linxWrapper, linxAdapter

class Test(unittest.TestCase):
    '''
    Unit tests for linx module in linx4py, requires following:
    Linx2.5.1 installed on current computer
    LinxAdapter kernel modules loaded into system
    '''
    process = None

    @classmethod
    def setUpClass(self):
        self.process = subprocess.Popen("linx_basic_server")

    def testLinxShouldThrowExceptionifNameisNone(self):
        linxInstance = linxAdapter.LinxAdapter()
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.open, None, 0, None)

    def testLinxShouldThrowExceptionWhenFail(self):
        linxInstance = linxAdapter.LinxAdapter()
        linxInstance.wrapper = TestOpenWrapper()
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.open, "MyClientName", 0, None)

    def openLinx(self, clientName):
        linxInstance = linxAdapter.LinxAdapter()
        linxInstance.open(clientName, 0, None)
        return linxInstance
    
    def testHuntThrowsExceptionWhenNameNone(self):
        linxInstance = self.openLinx("MyClientName")
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.hunt, None, None)
     
    def testHuntReturns0(self):
        linxInstance = self.openLinx("MyClientName")
        status = linxInstance.hunt("example_server", None)
        self.assertEqual(0, status, ("Hunt should return 0 but returns %d", status))
        
    def testHuntThrowsExceptionWhenNotOpen(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.wrapper = TestHuntWrapper() 
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.hunt, "example_server", None)
        
    def getHuntSignal(self):
        SigArrayType =  c_uint * 2
        return SigArrayType(1,251)
        
    def testRecieveWTMONoneWhenTimeOut(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.hunt("not_existing_server", None)
        hunt = self.getHuntSignal()
        signal = linxInstance.receiveWTMO(LINX_SIGNAL(), 500, hunt)
        self.assertIsNone(signal, "Should return None but is " + str(signal))
    
    def testRecieveWTMOReturnsOSHuntSignal(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.hunt("example_server", None)
        hunt = self.getHuntSignal()
        signal =  linxInstance.receiveWTMO(LINX_SIGNAL(), 10000, hunt)
        self.assertEquals(251, signal.sig_no, "Function exited with Errorcode")
        
    def testFindSenderFromSignal(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.hunt("example_server", None)
        hunt = self.getHuntSignal()
        signal =  linxInstance.receiveWTMO(LINX_SIGNAL(), 10000, hunt)
        self.assertNotEqual(0, linxInstance.findSender(signal))
        
    def testFindSenderThrowErrorWhenFail(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.wrapper = TestSenderWrapper()
        s = LINX_SIGNAL()
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.findSender, s)
        
    def testThrowErrorWhenAttachFails(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.hunt("example_server", None)
        hunt = self.getHuntSignal()
        linxInstance.receiveWTMO(LINX_SIGNAL(), 10000, hunt)
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.attach, None, 0)
         
    def testAttachToServer(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.hunt("example_server", None)
        hunt = self.getHuntSignal()
        signal = linxInstance.receiveWTMO(LINX_SIGNAL(), 10000, hunt)
        serverID = linxInstance.findSender(signal)
        self.assertNotEqual(0, linxInstance.attach(None, serverID))
        
    def findServer(self, linxInstance, name):
        linxInstance.hunt(name, None)
        hunt = self.getHuntSignal()
        signal = linxInstance.receiveWTMO(LINX_SIGNAL(), 10000, hunt)
        return linxInstance.findSender(signal)
        
    def testAllocReturnsSignal(self):
        linxInstance = self.openLinx("MyClientName")
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal = linxInstance.alloc(s)
        self.assertIsNotNone(signal.sig_no, "LinxAdapter should return REQUEST_SIGNAL")
        
    def testAllocThrowsExceptionWhenFails(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.wrapper = TestAllocWrapper()
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.alloc, s)
        
    def testFreeBufferShouldNotReturnNegative(self):
        linxInstance = self.openLinx("MyClientName")
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal = linxInstance.alloc(s)
        self.assertNotEqual(-1, linxInstance.free(signal), "Free buffer returned errorcode -1")
        
    def testThrowErrorWhenSignalNull(self):
        linxInstance = self.openLinx("MyClientName")
        self.findServer(linxInstance, "example_server")
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.send, None, 0)
        
    def testSendSignalDoesNotReturnError(self):
        linxInstance = self.openLinx("MyClientName")
        serverID = self.findServer(linxInstance, "example_server")
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal =linxInstance.alloc(s)
        signal.request.seqno = 1
        state = linxInstance.send(signal, serverID)
        self.assertNotEqual(-1, state, "LinxAdapter send should not return -1")
        
    def testSendSignalThrowExceptionWhenFail(self):
        linxInstance = self.openLinx("MyClientName")
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal =linxInstance.alloc(s)
        signal.request.seqno = 2
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.send, signal, 42)
        
    def sendSignal(self, linxInstance, signalNo, serverID):
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal =linxInstance.alloc(s)
        signal.request.seqno = signalNo
        return linxInstance.send(signal, serverID)
    
    def testReplyIsResponseSignal(self):
        linxInstance = self.openLinx("MyClientName")
        serverID = self.findServer(linxInstance, "example_server")
        self.sendSignal(linxInstance, 3, serverID)
        SigArrayType = c_uint * 1
        anySig = SigArrayType(0)
        signal = linxInstance.receiveWTMO(LINX_SIGNAL(), 10000, anySig)
        self.assertEquals(signal.reply.sig_no, 0x3341,("LinxAdapter should return REPLY_SIGNAL but returns sig_no %d", signal.reply.sig_no))
        
    def testCanReadReplySeqno(self):
        linxInstance = self.openLinx("MyClientName")
        serverID = self.findServer(linxInstance, "example_server")
        self.sendSignal(linxInstance, 4, serverID)
        SigArrayType = c_uint * 1
        anySig = SigArrayType(0)
        signal = linxInstance.receiveWTMO(LINX_SIGNAL(), 10000, anySig)
        self.assertEquals(signal.reply.seqno, 4,("LinxAdapter should return REPLY_SIGNAL but returns sig_no %d", signal.reply.seqno))
        
    def testCloseLinxInstanceIsNone(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.close()
        print linxInstance.instance
        self.assertFalse(linxInstance.instance, "Instance should be NullPointer after close")
        
    def testCloseLinxThrowsExceptionWhenFail(self):
        linxInstance = linxAdapter.LinxAdapter()
        linxInstance.wrapper = TestCloseWrapper()
        linxInstance.instance = linxWrapper.LINX()
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.close)
        
class TestOpenWrapper(linxWrapper.LinxWrapper):
    # Overrides LinxWrapper 
    # and pretends something went horribly wrong when calling linx_open
    def linx_open(self, name, options, arg):
        # Returns c NULL pointer
        return POINTER(linxWrapper.LINX)()

class TestHuntWrapper(linxWrapper.LinxWrapper):
    # Overrides LinxWrapper 
    # and pretends something went horribly wrong when calling linx_hunt
    def linx_hunt(self, linx, name, hunt_sig):
        return -1
    
class TestSenderWrapper(linxWrapper.LinxWrapper):
    # Overrides LinxWrapper 
    # and pretends something went horribly wrong when calling linx_sender
    def linx_sender(self, linx, sig):
        return 0
    
class TestAllocWrapper(linxWrapper.LinxWrapper):
    # Overrides LinxWrapper 
    # and pretends something went horribly wrong when calling linx_alloc
    def linx_alloc(self, linx, size, sig_no):
        return POINTER(LINX_SIGNAL)()
    
class TestCloseWrapper(linxWrapper.LinxWrapper):
    # Overrides LinxWrapper 
    # and pretends something went horribly wrong when calling linx_close
    def linx_close(self, linx):
        return -1
    
class REQUEST_SIGNAL(Structure):
    _fields_ = [("sig_no", c_uint),
                ("seqno", c_int)
                ]
    
class REPLY_SIGNAL(Structure):
    _fields_ = [("sig_no", c_uint),
                ("seqno", c_int)
                ]
    
class LINX_SIGNAL(Union):
    '''
    LinxAdapter Signal,
    Taken from linx basic example
    '''
    _fields_ = [("sig_no", c_uint),
                ("request", REQUEST_SIGNAL), 
                ("reply", REPLY_SIGNAL),
                ]
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()