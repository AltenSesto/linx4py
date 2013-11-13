'''
Created on 22 okt 2013

@author: Bjorn Arnelid
'''
import unittest
import xmlrunner

from test import  server
from linx4py import linx
from test.signals import LINX_SIGNAL, REQUEST_SIGNAL

class LinxTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.server_name = "example_server"
        self.server = server.get_server(self.server_name)
        
    @classmethod
    def tearDownClass(self):
        self.server.stop()

    def setUp(self):
        self.linxInstance = linx.Linx("MyClientName")
        self.server_id = self.linxInstance.hunt(self.server_name, 1000)
        self.linxInstance.add_union_type(LINX_SIGNAL)

    def tearDown(self):
        self.linxInstance = None
        self.server_id = None


    def test_linx_create_instance(self):
        self.assertIsNotNone(self.linxInstance.adapter, "Linx should have linx object")
        
    def test_find_server_returns_id(self):
        self.assertGreater(self.server_id, 0, "serverID must be greater then 0 but is " + str(self.server_id))

    def test_receive_signal_id(self):
        sendSignal = REQUEST_SIGNAL()
        self.linxInstance.send(sendSignal, self.server_id)
        receiveSignal = self.linxInstance.receive(1000)
        self.assertEquals(receiveSignal.sig_no, 0x3341)
        
    def test_recieve_signal_content(self):
        sendSignal = REQUEST_SIGNAL()
        sendSignal.seqno = 1
        self.linxInstance.send(sendSignal, self.server_id)
        receiveSignal = self.linxInstance.receive(1000)
        self.assertEquals(receiveSignal.seqno, 1)
        
    def test_receive_with_filter(self):
        sendSignal = REQUEST_SIGNAL()
        sendSignal.seqno = 2
        self.linxInstance.send(sendSignal, self.server_id)
        receiveSignal = self.linxInstance.receive(1000, [1, 0x3341])
        self.assertEquals(receiveSignal.seqno, 2)
        
    def test_get_sender(self):
        sendSignal = REQUEST_SIGNAL()
        self.linxInstance.send(sendSignal, self.server_id)
        receiveSignal = self.linxInstance.receive(1000)
        self.assertEqual(self.linxInstance.get_sender(receiveSignal), self.server_id)
        
    def test_add_signal(self):
        self.assertEqual(self.linxInstance.signal_collection._signals[0x3340], LINX_SIGNAL)

    def test_hunt_timeout(self):
        self.assertIsNone(self.linxInstance.hunt("NoServer", 5),
                          "Linx should return None if no server is found")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="unittests"))