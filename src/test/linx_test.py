'''
Created on 15 okt 2013

@author: Bjorn Arnelid
'''
from ctypes import POINTER, c_uint, c_int, Structure, Union
import subprocess
import unittest

from linx4py import linxWrapper
from linx4py import linxAdapter


class Test(unittest.TestCase):
    '''
    Unit tests for linx module in linx4py, requires following:
    Linx2.5.1 installed on current computer
    LinxAdapter kernel modules loaded into system
    LD_LIBRARY_PATH set to point at linx libraries 
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
        
    def testRecieveWTMOErrorWhenTimeOut(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.hunt("not_existing_server", None)
        hunt = self.getHuntSignal()
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.receiveWTMO, LINX_SIGNAL(), 
                              500, hunt)
    
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
        linxInstance.hunt("example_server", None)
        hunt = self.getHuntSignal()
        signal = linxInstance.receiveWTMO(LINX_SIGNAL(), 10000, hunt)
        return linxInstance.findSender(signal)
        
    def testAllocReturnsSignal(self):
        linxInstance = self.openLinx("MyClientName")
        s = REQUEST_SIGNAL(0x3340, 1)
        signal = linxInstance.alloc(s)
        self.assertEquals(signal.sig_no, 0x3340, ("LinxAdapter should return REQUEST_SIGNAL but returns sig_no ", signal.sig_no))
        
    def testAllocThrowsExceptionWhenFails(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.wrapper = TestAllocWrapper()
        s = REQUEST_SIGNAL(0x3340, 1)
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.alloc, s)
        
    def testFreeBufferShouldNotReturnNegative(self):
        linxInstance = self.openLinx("MyClientName")
        s = REQUEST_SIGNAL(0x3340, 1)
        signal = linxInstance.alloc(s)
        self.assertNotEqual(-1, linxInstance.free(signal), "Free buffer returned errorcode -1")
        
    def testThrowErrorWhenSignalNull(self):
        linxInstance = self.openLinx("MyClientName")
        self.findServer(linxInstance, "example_server")
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.send, None, 0)
        
    def testSendSignalDoesNotReturnError(self):
        linxInstance = self.openLinx("MyClientName")
        serverID = self.findServer(linxInstance, "example_server")
        s = REQUEST_SIGNAL(0x3340, 2)
        signal =linxInstance.alloc(s)
        state = linxInstance.send(signal, serverID)
        self.assertNotEqual(-1, state, "LinxAdapter send should not return -1")
        
    def testSendSignalThrowExceptionWhenFail(self):
        linxInstance = self.openLinx("MyClientName")
        s = REQUEST_SIGNAL(0x3340, 2)
        signal =linxInstance.alloc(s)
        self.failUnlessRaises(linxAdapter.LinxException, linxInstance.send, signal, 42)
        
    def sendSignal(self, linxInstance, signal, serverID):
        s = REQUEST_SIGNAL(0x3340, 2)
        signal =linxInstance.alloc(s)
        return linxInstance.send(signal, serverID)
    
    def testReplyIsResponseSignal(self):
        linxInstance = self.openLinx("MyClientName")
        serverID = self.findServer(linxInstance, "example_server")
        self.sendSignal(linxInstance, REQUEST_SIGNAL(0x3340, 2), serverID)
        SigArrayType = c_uint * 1
        anySig = SigArrayType(0)
        signal = linxInstance.receiveWTMO(LINX_SIGNAL(), 10000, anySig)
        self.assertEquals(signal.sig_no, 0x3341,("LinxAdapter should return REPLY_SIGNAL but returns sig_no %d", signal.sig_no))
        
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