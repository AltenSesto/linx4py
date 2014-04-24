#linx4py

Linx4Py is a python wrapper for Linx, a distributed communication protocol. 

##Requirements

- Linx 2.5.1 (Can be found at http://sourceforge.net/projects/linx/)
- Python 3
- Linux

##Installation

Get and install Linx as described in the Linx project readme. Make sure that the kernel module linx.ko is loaded in your system.

Add linx4py to your pythonpath like this: 
```shell
export PYTHONPATH="${PYTHONPATH}"
```
Or install linx4py automatically using the setup.py script.
```shell
python setup.py install
```

##Using linx4py
Linx4py concists of 3 layers, linx_wrapper.py, linx_wrapper.py and linx.py. When using linx4py it is possible to directly use any of these layers to contact linx, it will then contact any underlying layer and finally call the linx c interface.

###linx.py
linx.py is the easiest way of using linx4py, it aims to take care of all the background process for you leaving your code as clean and elegant as possible, it only covers the usual workflow of sending and receiving signals, however you are always able to accept and use the underlying adapter and wrapper if you need to make a more complicated call to linx. When you use linx through linx.py the library will automatically handle allocation and casting to the correct signal object for you.

To create a linx node
```python
linxInstance = Linx("example_client")
```
We need to add the Signal unions we want to work with to linx so it can cast to them dynamically.

To do this
```python
linxInstance.add_union_type(LINX_SIGNAL)
```
To send messages you will need to find another linx node, to find a linx node
```python
node_id = linxInstance.hunt("other_node",1000)
```
To send a signal
```python
sendSignal = REQUEST_SIGNAL()
linxInstance.send(sendSignal,node_id)
```
Finally to recieve a signal
```python
receiveSignal = linxInstance.receive(1000)
```
###linx_adapter.py
linx_adapter.py provides a slightly more detailed way to use the linx api. It provides a compromise between low level control and ease of use. 

To create a linx node
```python
linxInstance = LinxAdapter()
linxInstance.open("example_client",0,None)
```
To find another linx node
```python
linxInstance.hunt("other_node",None)
signal = linxInstance.receive_w_tmo(LINX_SIGNAL(),10000,LINX_OS_HUNT_SIG_SEL)
node_id = linxInstance.find_sender(signal)
```
To send a signal
```python
s = LINX_SIGNAL()
s.sig_no = REQUEST_SIGNAL_NO
signal =linxInstance.alloc(s)
linxInstance.send(signal,node_id)
```
To receive a signal
```python
signal = linxInstance.receive_w_tmo(LINX_SIGNAL(),10000,LINX_NO_SIG_SEL)
```

###linx_wrapper.py
linx_wrapper.py is a 1 to 1 mapping to the linx API, it covers the entire api and strives to follow the design of the api as closely as possible.

To create a linx node 
```python
wrapper = LinxWrapper()
name = "example_client"
options = 0
args = None
linx = wrapper.linx_open(name.encode('ascii','ignore'),options,args)
```
To find another node
```python
wrapper.linx_hunt(linx,"other_node",None)
sp = pointer(pointer(BaseSignal()))
wrapper.set_signal_class(BaseSignal)
wrapper.linx_receive_w_tmo(linx,sp,1000,LINX_OS_HUNT_SIG_SEL)
node_id = wrapper.linx_sender(linx,sp)
```
To send a signal
```python
size = sizeof(LINX_SIGNAL)
sig_no = REQUEST_SIGNAL_NO
wrapper.set_signal_class(LINX_SIGNAL)
signal = wrapper.linx_alloc(linx, size,sig_no)
wrapper.linx_send(linx, pointer(signal),node_id),0)
```
To recieve a signal
```python
sp = pointer(pointer(LINX_SIGNAL()))
wrapper.linx_receive(linx,sp,LINX_NO_SIG_SEL)
```

Linx4py comes with a comprehensive set of unit tests, to learn more of how to use linx4py and the expected behaviour please refer to the project unit tests.
