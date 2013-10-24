'''
Created on 22 okt 2013

@author: Bjorn Arnelid
'''
import unittest

import server
from linx4py import linx
from signals import LINX_SIGNAL

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.server_name = "example_server"
        self.process = server.getServer(self.server_name)
        
    @classmethod
    def tearDownClass(self):
        self.process.stop()

    def testLinxcreateInstance(self):
        linxInstance = linx.Linx("MyClientName")
        self.assertIsNotNone(linxInstance.adapter, "Linx should have linx object")
        
    def testFindServerReturnsID(self):
        linxInstance = linx.Linx("MyClientName")
        serverID = linxInstance.findServer(self.server_name, 1000)
        self.assertGreater(serverID, 0, "serverID must be greater then 0 but is " + str(serverID))

    def testReceiveSignalID(self):
        linxInstance = linx.Linx("MyClientName")
        serverID = linxInstance.findServer(self.server_name, 1000)
        sendSignal = linxInstance.createSignal(LINX_SIGNAL, 0x3340)
        sendSignal.request.seqno = 1
        linxInstance.send(sendSignal, serverID)
        receiveSignal = linxInstance.receive(LINX_SIGNAL(), 1000)
        self.assertEquals(receiveSignal.sig_no, 0x3341)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()