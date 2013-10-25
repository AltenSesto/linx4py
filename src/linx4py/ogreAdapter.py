'''
Created on 23 okt 2013

@author: Bjorn Arnelid

OgreAdapter is used to work with the ogre workflow, using linx4py.
There are still several things to do here. The better option is probably to use 
linx4py instead of pyogre, at least for straight forward linx calls. 
 
'''

import linx

from ctypes import Structure, c_uint


class Linx(object):
    '''
    Instances of his class represents a LINX endpoint on the host.

    Public methods:
        hunt()    -- Hunt for a target process by name
        attach()  -- Start supervision of a target process
        detach()  -- Dtop supervision of a target process
        send()    -- Send a signal to a target process
        receive() -- Receive a signal
        pid()     -- Return the endpoint proxy pid

    Usage:
        >>> import ogre, signals
        >>> gw = ogre.create('linx', 'unit_test')
        >>> gw.hunt('ogre_echo')
        >>> pid = gw.receive().sender()

        Send a signal to the target process
        >>> sig = signals.SyncReq()
        >>> sig.t1 = 47
        >>> gw.send(sig, pid)

        Receive the reply signal
        >>> reply = gw.receive()
        >>> print reply.t1
        47
        >>> gw.close()
        gw.close()
    '''
    linxInstance = None

    def __init__(self,name):
        '''
        Create a LINX endpoint. 

        Parameters:
            name -- the LINX endpoint name

        Usage:
            gw = ogre.Linx('test')
            ...
            gw.close()
        '''
        self.adapter = linx.LinxAdapter()
    
    def __del__(self):
        """
        Delete the LINX connection.
        """
        self.close()

    def close(self):
        """
        Terminate the LINX connection
        """
        self.adapter.close()
    
    def pid(self):
        """
        Return the endpoint proxy pid.
        """
        return self.adapter.getSPID()
    
    def hunt(self, name, hunt_sig = None):
        """
        Search for a process by name.

        When the process is found a signal is sent back to the calling
        process with signal number ogre.HUNT_SIG. If a hunt signal is
        specified, it is used instead

        Parameters:
            name      -- the process name
            hunt_sig  -- (optional) a signal to be sent back when
                         the specified process is found

        Usage:
            gw = ogre.Linx('test')
            gw.hunt('ogre_echo')
            pid = gw.receive().sender()
        """
        self.adapter.hunt(name, hunt_sig)
    
    def attach(self, pid, attach_sig = None):
        """
        Attach to a remote process to detect if the process is
        terminated. The attach_signal is stored within linx endpoint
        until the process is terminated. If no signal is specified, the
        linx endpoint allocates a default signal with signal number
        ATTACH_SIG.
    
        Parameters:
            pid        -- the pid of the process to attach to
            attach_sig -- the signal to send if when pid dies (optional)
    
        Usage:
            gw.hunt('ogre_echo')
            pid = gw.receive().sender()
            ref = gw.attach(pid)
        """
        return self.adapter.attach(attach_sig, pid)
    
    def detach(self, ref):
        """
        Remove a signal previously attached by the caller.

        Parameters:
            ref -- a reference returned by a previous attach()

        Usage:
            ref = gw.attach(pid)
            ...
            gw.detach(ref)
        """
        self.adapter.detach(ref)
    
    def send(self, sig, pid, sender = None):
        """
        Send an OSE signal toID the specified process.

        Parameters:
            sig    -- the signal toID send
            pid    -- the pid of the process the signal will be sent toID
            sender -- the pid of the process specified as sender, default None

        Usage:
            mysig = TestReq()
            mysig.a = 10
            mysig.b = 20
            gw.send(mysig, targetpid)
        """
        self.adapter.send(sig, pid, sender)
    
    def receive(self, sig_sel=None, timeout=None):
        """
        Receive a signal.

        Sig_sel is a sequence of signal numbers to be received. The
        method returns when a signal matching any of the specified
        signal numbers is found. If the timeout expires None is
        returned.

        Parameters:
            sig_sel -- a sequence of signal numbers (default all_sig)
            timeout -- the timeout value in seconds (optional)

        Usage
            mysignal = gw.receive()            # receive any signal
            mysignal = gw.receive([MY_SIG])    # receive MY_SIG only
            mysignal = gw.receive(timeout=1000) # wait max 1 second
        """
        sig = BASIC_LINX_SIGNAL()
        sp = self.adapter.receivePointerWTMO(sig, timeout, sig_sel)
        # Fix this using signal collection 
        #signal = signalAdapter.castToCorrect(sp)
        return sp
        
        
    def init_async_receive(self, sig_sel=None):
        """
        Initiate a non blocking receive operation. The signal is later
        retreived by a call to async_receive().

        Parameters:
            sig_sel -- a sequence of signal numbers

        Usage:
            gw.init_async_receive()
            signal = gw.async_receive()
            gw.cancel_async_receive()
        """
        # This will be truly async, not fake async as the ol ogre linx solution
        pass

    def cancel_async_receive(self):
        """
        Cancel a async_receive operation started with a call to
        init_async_receive()
        """
        pass
    
    def async_receive(self, sig_sel=None):
        """
        This methid is used for receiving signals in a non blocking
        mode. The receive operation is initiated with a call to
        init_async_receive().

        Parameters:
            sig_sel -- same as in init_async_receive

        Usage:
            gw.init_async_receive()
            fd = gw.get_blocking_object()
            (rfd, wdf, wfd) = select.select([fd], [], [])
            if fd in rfd:
                signal = gw.async_receive()
                ...
            gw.cancel_async_receive()
        """
        pass
    
    def get_blocking_object(self):
        """
        Returns a file descriptor that can be used in a select() call to
        wait for any signal from the linx endpoint.
        """
        pass
    
    
    
class BASIC_LINX_SIGNAL(Structure):
    _fields_ = [("sig_no", c_uint), ]