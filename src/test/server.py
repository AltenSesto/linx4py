'''
Created on 23 okt 2013

@author: bjorn
'''
from threading import Thread

from linx4py import linx
from signals import LINX_SIGNAL

server = None

class TestServer(Thread):
    name = None
    shouldQuit = None
    timeout = 3000
    
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        self.shouldQuit = False
        
    def run(self):
        print "Starting server thread"
        self.main()
        
    def stop(self):
        print "Server: Stop requested"
        self.shouldQuit = True
        
    def main(self):
        print "Server started."
        linxInstance = linx.Linx(self.name)
        while(not self.shouldQuit):
            sig = linxInstance.receive(LINX_SIGNAL(), self.timeout)
            if(sig == None):
                print "Server: Idle too long, terminating."
                self.shouldQuit = True
            elif(sig.sig_no == 0x3340):
                print "Server: REQUEST_SIG received."
                clientID = linxInstance.adapter.findSender(sig)
                print "Server: Sending REPLY_SIG."
                sig.sig_no = 0x3341
                linxInstance.send(sig, clientID)
            else:
                print "Server: Unexpected signal received (sig_no = %d) - ignored" % sig.sig_no
                linxInstance.adapter.free(sig)
        print "Server: Stopping, goodbye!"

def getServer(name):
    global server
    if(server == None):
        server = TestServer(name)
        server.start()
    else:
        server.shouldQuit = False
    return server

if __name__ == '__main__':
    server = getServer("example_server")