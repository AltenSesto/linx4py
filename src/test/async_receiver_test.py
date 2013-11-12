'''
Created on 24 okt 2013

@author: bjorn
'''
import unittest
import time
#import xmlrunner
from ctypes import c_uint

from linx4py.linx_adapter import LinxAdapter
from linx4py.async_receiver import AsyncReceiver

from test.signals import LINX_SIGNAL

from test import server

class AsyncReceiverTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.server_name = "example_server"
        self.server = server.get_server(self.server_name)
        
    @classmethod
    def tearDownClass(self):
        self.server.stop()

    def setUp(self):
        linxInstance = self.open_linx("MyReceiver")
        self.receiver = AsyncReceiver(linxInstance)
        self.receiver.add_union_type(LINX_SIGNAL)
        self.receiver.init_receive()

    def tearDown(self):
        self.receiver.stopReceive()

    def open_linx(self, clientName):
        linxInstance = LinxAdapter()
        linxInstance.open(clientName, 0, None)
        return linxInstance

    def getHuntSignal(self):
        SigArrayType =  c_uint * 2
        return SigArrayType(1,251)
    
    def findServer(self, linxInstance, name):
        linxInstance.hunt(name, None)
        hunt = self.getHuntSignal()
        signal = linxInstance.receive_w_tmo(LINX_SIGNAL(), 10000, hunt)
        return linxInstance.find_sender(signal)

    def sendSignal(self, linxInstance, signalNo, serverID, receiverID):
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal =linxInstance.alloc(s)
        signal.request.seqno = signalNo
        return linxInstance.send(signal, serverID, receiverID)
    
    def testReceiveSignalAsync(self):
        receiverID = self.receiver.adapter.get_spid()
        senderInstance = self.open_linx("MySenderName")
        serverID = self.findServer(senderInstance, self.server_name)
        self.sendSignal(senderInstance, 1, serverID, receiverID)
        # Making sure we would have timed out if not async
        time.sleep(2) 
        signal = self.receiver.receive()
        self.assertEqual(0x3341, signal.sig_no)
        
    def testReceiveAsyncEmpty(self):
        signal = self.receiver.receive()
        self.assertIsNone(signal, "signal should be None when que is empty")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testReceiveSignal']
    unittest.main()
    #unittest.main(testRunner=xmlrunner.XMLTestRunner(output="unittests"))