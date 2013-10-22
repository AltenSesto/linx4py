'''
Created on 22 okt 2013

@author: Bjorn Arnelid
'''
import unittest
import subprocess

from linx4py import linx
from linxAdapterTest import LINX_SIGNAL

class Test(unittest.TestCase):


    @classmethod
    def setUpClass(self):
        self.process = subprocess.Popen("linx_basic_server")

    def testLinxcreateInstance(self):
        linxInstance = linx.Linx("MyClientName")
        self.assertIsNotNone(linxInstance.adapter, "Linx should have linx object")
        
    def testFindServerReturnsID(self):
        linxInstance = linx.Linx("MyClientName")
        serverID = linxInstance.findServer("example_server", 1000)
        self.assertGreater(serverID, 0, "serverID must be greater then 0 but is " + str(serverID))

    def testReceiveSignalID(self):
        linxInstance = linx.Linx("MyClientName")
        serverID = linxInstance.findServer("example_server", 1000)
        sendSignal = linxInstance.createSignal(LINX_SIGNAL, 0x3340)
        sendSignal.request.seqno = 1
        linxInstance.send(sendSignal, serverID)
        receiveSignal = linxInstance.receive(LINX_SIGNAL(), 1000)
        self.assertEquals(receiveSignal.sig_no, 0x3341)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()