#-------------------------------------------------------------------------------
# Copyright (c) 2013 Alten AB.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
# 
# Contributors:
#     Bjorn Arnelid - initial API and implementation
#-------------------------------------------------------------------------------
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
        unicode_string = "example_server"
        self.server_name = unicode_string.encode('ascii','ignore')
        self.server = server.get_server(self.server_name)
        
    @classmethod
    def tearDownClass(self):
        self.server.stop()

    def setUp(self):
        self.wrapper = LinxWrapper()
        name = "example_client"
        options = 0
        args = None
        self.linx = self.wrapper.linx_open(name.encode('ascii','ignore'),
                                           options, args)
        self.serverID = self.get_server(self.wrapper, self.linx)
        self.sig = self.create_request_signal(self.linx, self.wrapper)

    def tearDown(self):
        # Closing linx and cleaning up seems to result in segfault in the linx
        # module
        pass

    def get_server(self, wrapper, linx):
        wrapper.linx_hunt(linx, self.server_name, None)
        sp = pointer(pointer(BaseSignal()))
        wrapper.set_signal_class(BaseSignal)
        wrapper.linx_receive_w_tmo(linx, sp, 1000, LINX_OS_HUNT_SIG_SEL)
        return wrapper.linx_sender(linx, sp)

    def create_request_signal(self, linx, wrapper):
        size = sizeof(LINX_SIGNAL)
        sig_no = REQUEST_SIGNAL_NO
        wrapper.set_signal_class(LINX_SIGNAL)
        return wrapper.linx_alloc(linx, size, sig_no)

 
    def test_linx_get_descriptor(self):
        self.assertGreater(self.wrapper.linx_get_descriptor(self.linx), 0)
 
    def test_linx_alloc(self):
        size = sizeof(REQUEST_SIGNAL)
        sig_no = REQUEST_SIGNAL_NO
        self.wrapper.set_signal_class(REQUEST_SIGNAL)
        self.assertTrue(self.wrapper.linx_alloc(self.linx, size, sig_no),
                        "linx_alloc should not return LINX_NIL")
             
    def test_linx_free_buf(self):
        self.assertEqual(self.wrapper.linx_free_buf(self.linx, self.sig), 0)
 
    def test_linx_send(self):
        self.assertEqual(self.wrapper.linx_send(self.linx, pointer(self.sig),
                                                self.serverID), 0)
 
    def test_linx_send_w_s(self):
        fromID = self.wrapper.linx_get_spid(self.linx)
        self.assertEqual(self.wrapper.linx_send_w_s(self.linx,
                                                    pointer(self.sig),
                                                    fromID,
                                                    self.serverID), 0)
 
    def test_linx_send_w_opt(self):
        fromID = self.wrapper.linx_get_spid(self.linx)
        OptArrCls = c_int * 3
        optArr = OptArrCls(1, 1, 0)
        self.assertEqual(self.wrapper.linx_send_w_opt(self.linx,
                                                      pointer(self.sig),
                                                      fromID,
                                                      self.serverID,
                                                      optArr), 0)
 
    def test_linx_sigattr(self):
        #This tells the server to return with opts
        self.sig.contents.request.seqno = -1
        self.wrapper.linx_send(self.linx, self.sig, self.serverID)
        sp = pointer(pointer(LINX_SIGNAL()))
        self.wrapper.linx_receive_w_tmo(self.linx, sp, 1000, LINX_NO_SIG_SEL)
        value = pointer(c_uint8())
        self.wrapper.linx_sigattr(self.linx, sp, 1, value)
        self.assertEqual(value.contents.value, 1)
 
    def test_linx_receive(self):
        self.sig.contents.request.seqno = 1
        self.wrapper.linx_send(self.linx, self.sig, self.serverID)
        sp = pointer(pointer(LINX_SIGNAL()))
        self.wrapper.linx_receive(self.linx, sp, LINX_NO_SIG_SEL)
        self.assertEqual(sp.contents.contents.reply.seqno, 1)
 
    def test_linx_receive_w_tmo(self):
        self.sig.contents.request.seqno = 2
        self.wrapper.linx_send(self.linx, self.sig, self.serverID)
        sp = pointer(pointer(LINX_SIGNAL()))
        self.wrapper.linx_receive_w_tmo(self.linx, sp, 1000, LINX_NO_SIG_SEL)
        self.assertEqual(sp.contents.contents.reply.seqno, 2)
         
    def test_linx_receive_from(self):
        self.sig.contents.request.seqno = 3
        self.wrapper.linx_send(self.linx, self.sig, self.serverID)
        sp = pointer(pointer(LINX_SIGNAL()))
        self.wrapper.linx_receive_from(self.linx, sp, 1000, LINX_NO_SIG_SEL,
                                       self.serverID)
        self.assertEqual(sp.contents.contents.reply.seqno, 3)
 
    def test_linx_sender(self):
        self.wrapper.linx_send(self.linx, self.sig, self.serverID)
        sp = pointer(pointer(LINX_SIGNAL()))
        self.wrapper.linx_receive_w_tmo(self.linx, sp, 1000, LINX_NO_SIG_SEL)
        self.assertEqual(self.wrapper.linx_sender(self.linx, sp), self.serverID)
 
    def test_linx_sigsize(self):
        self.assertEqual(self.wrapper.linx_sigsize(self.linx, self.sig), sizeof(self.sig.contents))
 
    def test_linx_set_sigsize(self):
        old_size = sizeof(self.sig.contents)
        self.wrapper.linx_set_sigsize(self.linx, self.sig,
                                      sizeof(self.sig.contents)+4)
        self.assertEqual(self.wrapper.linx_sigsize(self.linx, self.sig),
                         old_size+4)
 
    def test_linx_hunt_from(self):
        from_id = self.wrapper.linx_get_spid(self.linx)
        self.assertEqual(self.wrapper.linx_hunt_from(self.linx,
                                                     self.server_name,
                                                     None,
                                                     from_id), 0)
 
    def test_linx_attach(self):
        self.assertGreater(self.wrapper.linx_attach(self.linx, None,
                                                    self.serverID), 0)

#     def test_linx_get_name(self):
#         self.fail("Not Implemented")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="unittests"))
