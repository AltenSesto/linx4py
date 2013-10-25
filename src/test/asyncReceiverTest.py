'''
Created on 24 okt 2013

@author: bjorn
'''
import unittest
import time
from ctypes import c_uint

from linx4py.linxAdapter import LinxAdapter
from signals import LINX_SIGNAL
from linx4py.asyncReceiver import AsyncReceiver
import server

class Test(unittest.TestCase):
    
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
        signal = linxInstance.receiveWTMO(LINX_SIGNAL(), 10000, hunt)
        return linxInstance.findSender(signal)

    def sendSignal(self, linxInstance, signalNo, serverID, receiverID):
        s = LINX_SIGNAL()
        s.sig_no = 0x3340
        signal =linxInstance.alloc(s)
        signal.request.seqno = signalNo
        return linxInstance.send(signal, serverID, receiverID)
    
#     def testReceiveSignalAsync(self):
#         receiverInstance = self.openLinx("MyReceiverName")
#         receiverID = receiverInstance.getSPID()
#         senderInstance = self.openLinx("MySenderName")
#         serverID = self.findServer(senderInstance, self.server_name)
#         receiver = AsyncReceiver(receiverInstance)
#         receiver.initReceive()
#         self.sendSignal(senderInstance, 1, serverID, receiverID)
#         time.sleep(1)
#         sp = receiver.receive()
#         receiver.stopReceive()
#         self.assertEqual(0x3341, sp.contents.reply.sig_no)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testReceiveSignal']
    unittest.main()