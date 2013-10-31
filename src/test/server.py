'''
Created on 23 okt 2013

@author: bjorn
'''
from threading import Thread
from ctypes import pointer, c_int

from linx4py import linx
from signals import LINX_SIGNAL, REPLY_SIGNAL

server = None

class TestServer(Thread):
    name = None
    should_quit = None
    timeout = 3000
    
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        self.should_quit = False
        
    def run(self):
        print "Starting server thread"
        self.main()
        
    def stop(self):
        print "Server: Stop requested"
        self.should_quit = True
        
    def main(self):
        print "Server started."
        linx_instance = linx.Linx(self.name)
        linx_instance.add_union_type(LINX_SIGNAL)
        while(not self.should_quit):
            sig = linx_instance.receive(self.timeout)
            if(sig == None):
                print "Server: Idle too long, terminating."
                self.should_quit = True
            elif(sig.sig_no == 0x3340):
                print "Server: REQUEST_SIG received."
                clientID = linx_instance.get_sender(sig)
                if sig.seqno == -1:
                    print "Server: Sending REPLY_SIG with opt"
                    sendSignal = linx_instance.adapter.alloc(REPLY_SIGNAL())
                    serverID = linx_instance.adapter.get_spid()
                    OptArrCls = c_int * 3
                    inArr = OptArrCls(1, 1, 0)
                    linx_instance.adapter.wrapper.linx_send_w_opt(linx_instance.adapter.instance,
                                                                 pointer(pointer(sendSignal)),
                                                                 serverID, clientID, inArr)
                else:
                    print "Server: Sending REPLY_SIG."
                    sendSignal = REPLY_SIGNAL()
                    sendSignal.seqno = sig.seqno
                    linx_instance.send(sendSignal, clientID)
            else:
                print "Server: Unexpected signal received (sig_no = %d) - ignored" % sig.sig_no
                linx_instance.adapter.free(sig)
        print "Server: Stopping, goodbye!"

def getServer(name):
    global server
    if(server == None):
        server = TestServer(name)
        server.start()
    else:
        server.should_quit = False
    return server

if __name__ == '__main__':
    server = getServer("example_server")