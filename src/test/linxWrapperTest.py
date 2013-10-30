'''
Created on 30 okt 2013

@author: Bjorn Arnelid
'''
import unittest
import xmlrunner
from ctypes import sizeof, pointer, c_uint8, c_int, c_void_p, cast, POINTER

from linx4py.linxWrapper import LinxWrapper, BaseSignal
from linx4py.linxConstants import LINX_OS_HUNT_SIG_SEL, LINX_NO_SIG_SEL
from test import server
from test.signals import REQUEST_SIGNAL, REQUEST_SIGNAL_NO, LINX_SIGNAL

class LinxWrapperTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.server_name = "example_server"
        self.process = server.getServer(self.server_name)
        
    @classmethod
    def tearDownClass(self):
        self.process.stop()

    def testLinxOpen(self):
        wrapper = LinxWrapper()
        name = "example_client"
        options = 0
        args = None
        self.assertIsNotNone(wrapper.linx_open(name, options, args), "wrapper.linx_open should not return None")
    
    def openLinx(self, wrapper):
        name = "example_client"
        options = 0
        args = None
        return wrapper.linx_open(name, options, args)

    def testLinxClose(self):
        wrapper = LinxWrapper()
        linx = self.openLinx(wrapper)
        self.assertEqual(wrapper.linx_close(linx), 0)

    def testLinxGetDescriptor(self):
        wrapper = LinxWrapper()
        linx = self.openLinx(wrapper)
        self.assertGreater(wrapper.linx_get_descriptor(linx), 0)

    def testLinxAlloc(self):
        wrapper = LinxWrapper()
        linx = self.openLinx(wrapper)
        size = sizeof(REQUEST_SIGNAL)
        sig_no = REQUEST_SIGNAL_NO
        wrapper.setSignalClass(REQUEST_SIGNAL)
        self.assertTrue(wrapper.linx_alloc(linx, size, sig_no), "linx_alloc should not return LINX_NIL")

    def createRequestSignal(self, linx, wrapper):
        size = sizeof(LINX_SIGNAL)
        sig_no = REQUEST_SIGNAL_NO
        wrapper.setSignalClass(LINX_SIGNAL)
        return wrapper.linx_alloc(linx, size, sig_no)
            
    def testLinxFreeBuf(self):
        wrapper = LinxWrapper()
        linx = self.openLinx(wrapper)
        sig = self.createRequestSignal(linx, wrapper)
        self.assertEqual(wrapper.linx_free_buf(linx, sig), 0)

    def getServer(self, wrapper, linx):
        wrapper.linx_hunt(linx, self.server_name, None)
        sp = pointer(pointer(BaseSignal()))
        wrapper.setSignalClass(BaseSignal)
        wrapper.linx_receive_w_tmo(linx, sp,
                                          1000, LINX_OS_HUNT_SIG_SEL)
        return wrapper.linx_sender(linx, sp)

    def testLinxSend(self):
        wrapper = LinxWrapper()
        linx = self.openLinx(wrapper)
        toID = self.getServer(wrapper, linx)
        sig = self.createRequestSignal(linx, wrapper)
        self.assertEqual(wrapper.linx_send(linx, pointer(sig), toID), 0)

    def testLinxSendWS(self):
        wrapper = LinxWrapper()
        linx = self.openLinx(wrapper)
        toID = self.getServer(wrapper, linx)
        fromID = wrapper.linx_get_spid(linx)
        sig = self.createRequestSignal(linx, wrapper)
        self.assertEqual(wrapper.linx_send_w_s(linx, pointer(sig), fromID, toID), 0)

    def testLinxSendWOpt(self):
        wrapper = LinxWrapper()
        linx = self.openLinx(wrapper)
        toID = self.getServer(wrapper, linx)
        fromID = wrapper.linx_get_spid(linx)
        sig = self.createRequestSignal(linx, wrapper)
        OptArrCls = c_int * 3
        optArr = OptArrCls(1, 1, 0)
        self.assertEqual(wrapper.linx_send_w_opt(linx, pointer(sig), fromID, toID,
                                               optArr), 0)

#     def testLinxSigattr(self):
#         wrapper = LinxWrapper()
#         linx = self.openLinx(wrapper)
#         toID = self.getServer(wrapper, linx)
#         fromID = wrapper.linx_get_spid(linx)
#         sig = self.createRequestSignal(linx, wrapper)
#         OptArrCls = c_int * 3
#         inArr = OptArrCls(1, 0, 0)
#         wrapper.linx_send_w_opt(linx, sig, fromID, toID, inArr)
#         sp = pointer(pointer(LINX_SIGNAL()))
#         wrapper.linx_receive_w_tmo(linx, sp,
#                                           1000, LINX_NO_SIG_SEL)
#         value = pointer(pointer(c_uint8()))
#         wrapper.linx_sigattr(linx, sp, 1, value)
#         #vp = cast(value, POINTER(c_uint8))
# #         if(vp.contents):
# #             print vp.contents
# #         else:
# #             print "0"
#         self.assertEqual(value.contents.contents, 1)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="unittests"))