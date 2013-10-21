'''
Created on 15 okt 2013

@author: bjorn
'''
from ctypes import POINTER, c_uint
import subprocess
import unittest

from linx4py import linxWrapper
from linx4py import linx


class Test(unittest.TestCase):
    '''
    Unit tests for linx module in linx4py, requires following:
    Linx2.5.1 installed on current computer
    Linx kernel modules loaded into system
    LD_LIBRARY_PATH set to point at linx libraries 
    '''
    process = None

    @classmethod
    def setUpClass(self):
        self.process = subprocess.Popen("linx_basic_server")

    def testLinxShouldThrowExceptionifNameisNone(self):
        linxInstance = linx.Linx()
        self.failUnlessRaises(linx.LinxException, linxInstance.open, None, 0, None)

    def testLinxShouldThrowExceptionWhenFail(self):
        linxInstance = linx.Linx()
        linxInstance.wrapper = TestOpenWrapper()
        self.failUnlessRaises(linx.LinxException, linxInstance.open, "MyClientName", 0, None)
        
    def testGetLinxInstance(self):
        linxInstance = linx.Linx()
        linxInstance.open("MyClientName", 0, None)
        self.assertTrue(isinstance(linxInstance.instance, POINTER(linxWrapper.LINX)), 
                        "Should be a LINX pointer Structure but is " + linxInstance.instance.__class__.__name__)
    
    def openLinx(self, clientName):
        linxInstance = linx.Linx()
        linxInstance.open(clientName, 0, None)
        return linxInstance
    
    def testHuntThrowsExceptionWhenNameNone(self):
        linxInstance = self.openLinx("MyClientName")
        self.failUnlessRaises(linx.LinxException, linxInstance.hunt, None, None)
     
    def testHuntReturns0(self):
        linxInstance = self.openLinx("MyClientName")
        status = linxInstance.hunt("example_server", None)
        self.assertEqual(0, status, ("Hunt should return 0 but returns %d", status))
        
    def testHuntThrowsExceptionWhenNotOpen(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.wrapper = TestHuntWrapper() 
        self.failUnlessRaises(linx.LinxException, linxInstance.hunt, "example_server", None)
        
    def getHuntSignal(self):
        SigArrayType =  c_uint * 2
        return SigArrayType(1,251)
        
    def testRecieveWTMOErrorWhenTimeOut(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.hunt("not_existing_server", None)
        hunt = self.getHuntSignal()
        self.failUnlessRaises(linx.LinxException, linxInstance.receiveWTMO, 500, hunt)
    
    def testRecieveWTMOReturnsOSHuntSignal(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.hunt("example_server", None)
        hunt = self.getHuntSignal()
        signal =  linxInstance.receiveWTMO(10000, hunt)
        self.assertEquals(251, signal.sig_no, "Function exited with Errorcode")
        
    def testFindSenderFromSignal(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.hunt("example_server", None)
        hunt = self.getHuntSignal()
        signal =  linxInstance.receiveWTMO(10000, hunt)
        self.assertNotEqual(0, linxInstance.findSender(signal))
        
    def testThrowErrorWhenAttachFails(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.hunt("example_server", None)
        hunt = self.getHuntSignal()
        linxInstance.receiveWTMO(10000, hunt)
        self.failUnlessRaises(linx.LinxException, linxInstance.attach, None, 0)
         
    def testAttachToServer(self):
        linxInstance = self.openLinx("MyClientName")
        linxInstance.hunt("example_server", None)
        hunt = self.getHuntSignal()
        signal = linxInstance.receiveWTMO(10000, hunt)
        serverID = linxInstance.findSender(signal)
        self.assertNotEqual(0, linxInstance.attach(None, serverID))
        
    def findServer(self, linxInstance, name):
        linxInstance.hunt("example_server", None)
        hunt = self.getHuntSignal()
        signal = linxInstance.receiveWTMO(10000, hunt)
        return linxInstance.findSender(signal)
        
    def testThrowErrorWhenSendFails(self):
        linxInstance = self.openLinx("MyClientName")
        serverID = self.findServer(linxInstance, "example_server")
        self.failUnlessRaises(linx.LinxException, linxInstance.send)
        
    def testSendSignalDoesNotReturn0(self):
        linxInstance = self.openLinx("MyClientName")
        serverID = self.findServer(linxInstance, "example_server")
        state = linxInstance.send()
        self.assertNotEqual(-1, state, "Linx send should not return -1")
        
class TestOpenWrapper(linxWrapper.LinxWrapper):
    # Overrides LinxWrapper 
    # and pretends something went horribly wrong when calling linx_open
    def linx_open(self, name, options, arg):
        # Returns c NULL pointer
        return POINTER(linxWrapper.LINX)()

class TestHuntWrapper(linxWrapper.LinxWrapper):
    # Overrides LinxWrapper 
    # and pretends something went horribly wrong whne calling linx_hunt
    def linx_hunt(self, linx, name, hunt_sig):
        return -1
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()