'''
Created on 30 okt 2013

@author: Bjorn Arnelid
'''
import unittest
import xmlrunner
from ctypes import sizeof, pointer, c_uint8, c_int

from linx4py.linx_wrapper import LinxWrapper
from linx4py.linx_constants import LINX_OS_HUNT_SIG_SEL, LINX_NO_SIG_SEL, BaseSignal

from test import server
from test.signals import REQUEST_SIGNAL, REQUEST_SIGNAL_NO, LINX_SIGNAL

class LinxWrapperTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.server_name = "example_server"
        self.process = server.get_server(self.server_name)
        
    @classmethod
    def tearDownClass(self):
        self.process.stop()

    def test_linx_open(self):
        wrapper = LinxWrapper()
        name = "example_client"
        options = 0
        args = None
        self.assertIsNotNone(wrapper.linx_open(name, options, args), "wrapper.linx_open should not return None")
    
    def open_linx(self, wrapper):
        name = "example_client"
        options = 0
        args = None
        return wrapper.linx_open(name, options, args)

    def test_linx_close(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        self.assertEqual(wrapper.linx_close(linx), 0)

    def test_linx_get_descriptor(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        self.assertGreater(wrapper.linx_get_descriptor(linx), 0)

    def test_linx_alloc(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        size = sizeof(REQUEST_SIGNAL)
        sig_no = REQUEST_SIGNAL_NO
        wrapper.set_signal_class(REQUEST_SIGNAL)
        self.assertTrue(wrapper.linx_alloc(linx, size, sig_no), "linx_alloc should not return LINX_NIL")

    def create_request_signal(self, linx, wrapper):
        size = sizeof(LINX_SIGNAL)
        sig_no = REQUEST_SIGNAL_NO
        wrapper.set_signal_class(LINX_SIGNAL)
        return wrapper.linx_alloc(linx, size, sig_no)
            
    def test_linx_free_buf(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        sig = self.create_request_signal(linx, wrapper)
        self.assertEqual(wrapper.linx_free_buf(linx, sig), 0)

    def get_server(self, wrapper, linx):
        wrapper.linx_hunt(linx, self.server_name, None)
        sp = pointer(pointer(BaseSignal()))
        wrapper.set_signal_class(BaseSignal)
        wrapper.linx_receive_w_tmo(linx, sp, 1000, LINX_OS_HUNT_SIG_SEL)
        return wrapper.linx_sender(linx, sp)

    def test_linx_send(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        toID = self.get_server(wrapper, linx)
        sig = self.create_request_signal(linx, wrapper)
        self.assertEqual(wrapper.linx_send(linx, pointer(sig), toID), 0)

    def test_linx_send_w_s(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        toID = self.get_server(wrapper, linx)
        fromID = wrapper.linx_get_spid(linx)
        sig = self.create_request_signal(linx, wrapper)
        self.assertEqual(wrapper.linx_send_w_s(linx, pointer(sig), fromID, toID), 0)

    def test_linx_send_w_opt(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        toID = self.get_server(wrapper, linx)
        fromID = wrapper.linx_get_spid(linx)
        sig = self.create_request_signal(linx, wrapper)
        OptArrCls = c_int * 3
        optArr = OptArrCls(1, 1, 0)
        self.assertEqual(wrapper.linx_send_w_opt(linx, pointer(sig), fromID, toID,
                                               optArr), 0)

    def test_linx_sigattr(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        toID = self.get_server(wrapper, linx)
        sig = self.create_request_signal(linx, wrapper)
        #This tells the server to return with opts
        sig.contents.request.seqno = -1
        wrapper.linx_send(linx, sig, toID)
        sp = pointer(pointer(LINX_SIGNAL()))
        wrapper.linx_receive_w_tmo(linx, sp, 1000, LINX_NO_SIG_SEL)
        value = pointer(c_uint8())
        wrapper.linx_sigattr(linx, sp, 1, value)
        self.assertEqual(value.contents.value, 1)

    def test_linx_receive(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        toID = self.get_server(wrapper, linx)
        sig = self.create_request_signal(linx, wrapper)
        sig.contents.request.seqno = 1
        wrapper.linx_send(linx, sig, toID)
        sp = pointer(pointer(LINX_SIGNAL()))
        wrapper.linx_receive(linx, sp, LINX_NO_SIG_SEL)
        self.assertEqual(sp.contents.contents.reply.seqno, 1)

    def test_linx_receive_w_tmo(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        toID = self.get_server(wrapper, linx)
        sig = self.create_request_signal(linx, wrapper)
        sig.contents.request.seqno = 2
        wrapper.linx_send(linx, sig, toID)
        sp = pointer(pointer(LINX_SIGNAL()))
        wrapper.linx_receive_w_tmo(linx, sp, 1000, LINX_NO_SIG_SEL)
        self.assertEqual(sp.contents.contents.reply.seqno, 2)
        
    def test_linx_receive_from(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        toID = self.get_server(wrapper, linx)
        sig = self.create_request_signal(linx, wrapper)
        sig.contents.request.seqno = 3
        wrapper.linx_send(linx, sig, toID)
        sp = pointer(pointer(LINX_SIGNAL()))
        wrapper.linx_receive_from(linx, sp, 1000, LINX_NO_SIG_SEL, toID)
        self.assertEqual(sp.contents.contents.reply.seqno, 3)

    def test_linx_sender(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        toID = self.get_server(wrapper, linx)
        sig = self.create_request_signal(linx, wrapper)
        wrapper.linx_send(linx, sig, toID)
        sp = pointer(pointer(LINX_SIGNAL()))
        wrapper.linx_receive_w_tmo(linx, sp, 1000, LINX_NO_SIG_SEL)
        self.assertEqual(wrapper.linx_sender(linx, sp), toID)

    def test_linx_sigsize(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        sig = self.create_request_signal(linx, wrapper)
        self.assertEqual(wrapper.linx_sigsize(linx, sig), sizeof(sig.contents))

    def test_linx_set_sigsize(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        sig = self.create_request_signal(linx, wrapper)
        old_size = sizeof(sig.contents)
        wrapper.linx_set_sigsize(linx, sig, sizeof(sig.contents)+4)
        self.assertEqual(wrapper.linx_sigsize(linx, sig), old_size + 4)

    def test_linx_hunt(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        self.assertEqual(wrapper.linx_hunt(linx, self.server_name, None), 0)

    def test_linx_hunt_from(self):
        wrapper = LinxWrapper()
        linx = self.open_linx(wrapper)
        from_id = wrapper.linx_get_spid(linx)
        self.assertEqual(wrapper.linx_hunt_from(linx, self.server_name, None, from_id), 0)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="unittests"))