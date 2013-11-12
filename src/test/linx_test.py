'''
Created on 22 okt 2013

@author: Bjorn Arnelid
'''
import unittest
#import xmlrunner

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

    def testLinxcreateInstance(self):
        linxInstance = linx.Linx("MyClientName")
        self.assertIsNotNone(linxInstance.adapter, "Linx should have linx object")
        
    def testFindServerReturnsID(self):
        linxInstance = linx.Linx("MyClientName")
        serverID = linxInstance.hunt(self.server_name, 1000)
        self.assertGreater(serverID, 0, "serverID must be greater then 0 but is " + str(serverID))

    def testReceiveSignalID(self):
        linxInstance = linx.Linx("MyClientName")
        serverID = linxInstance.hunt(self.server_name, 1000)
        linxInstance.add_union_type(LINX_SIGNAL)
        sendSignal = REQUEST_SIGNAL()
        linxInstance.send(sendSignal, serverID)
        receiveSignal = linxInstance.receive(1000)
        self.assertEquals(receiveSignal.sig_no, 0x3341)
        
    def testRecieveSignalContent(self):
        linxInstance = linx.Linx("MyClientName")
        serverID = linxInstance.hunt(self.server_name, 1000)
        linxInstance.add_union_type(LINX_SIGNAL)
        sendSignal = REQUEST_SIGNAL()
        sendSignal.seqno = 1
        linxInstance.send(sendSignal, serverID)
        receiveSignal = linxInstance.receive(1000)
        self.assertEquals(receiveSignal.seqno, 1)
        
    def testReceiveWithFilter(self):
        linxInstance = linx.Linx("MyClientName")
        serverID = linxInstance.hunt(self.server_name, 1000)
        linxInstance.add_union_type(LINX_SIGNAL)
        sendSignal = REQUEST_SIGNAL()
        sendSignal.seqno = 2
        linxInstance.send(sendSignal, serverID)
        receiveSignal = linxInstance.receive(1000, [1, 0x3341])
        self.assertEquals(receiveSignal.seqno, 2)
        
    def testGetSender(self):
        linxInstance = linx.Linx("MyClientName")
        serverID = linxInstance.hunt(self.server_name, 1000)
        linxInstance.add_union_type(LINX_SIGNAL)
        sendSignal = REQUEST_SIGNAL()
        linxInstance.send(sendSignal, serverID)
        receiveSignal = linxInstance.receive(1000)
        self.assertEqual(linxInstance.get_sender(receiveSignal), serverID)
        
    def testAddSignal(self):
        linxInstance = linx.Linx("MyClientName")
        linxInstance.add_union_type(LINX_SIGNAL)
        self.assertEqual(linxInstance.signal_collection._signals[0x3340], LINX_SIGNAL)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    #unittest.main(testRunner=xmlrunner.XMLTestRunner(output="unittests"))