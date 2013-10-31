'''
Created on 24 okt 2013

@author: bjorn
'''
import unittest
import time
import xmlrunner
from ctypes import c_uint

from linx4py.linx_adapter import LinxAdapter
from linx4py.async_receiver import AsyncReceiver

from signals import LINX_SIGNAL

import server

class AsyncReceiverTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.server_name = "example_server"
        self.process = server.getServer(self.server_name)
        
    @classmethod
    def tearDownClass(self):
        self.process.stop()

    def openLinx(self, clientName):
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
        receiverInstance = self.openLinx("MyReceiverName")
        receiverID = receiverInstance.get_spid()
        senderInstance = self.openLinx("MySenderName")
        serverID = self.findServer(senderInstance, self.server_name)
        receiver = AsyncReceiver(receiverInstance)
        receiver.add_union_type(LINX_SIGNAL)
        receiver.init_receive()
        self.sendSignal(senderInstance, 1, serverID, receiverID)
        # Making sure we would have timed out if not async
        time.sleep(2) 
        signal = receiver.receive()
        receiver.stopReceive()
        self.assertEqual(0x3341, signal.sig_no)
        
    def testReceiveAsyncEmpty(self):
        receiverInstance = self.openLinx("MyReceiverName")
        receiver = AsyncReceiver(receiverInstance)
        receiver.init_receive()
        signal = receiver.receive()
        receiver.stopReceive()
        self.assertIsNone(signal, "signal should be None when que is empty")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testReceiveSignal']
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="unittests"))