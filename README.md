#linx4py

Linx4Py is a python wrapper for Linx, a distributed communication protocol. 

###Requirements

- Linx 2.5.1 (Can be found at http://sourceforge.net/projects/linx/)
- Python 3
- Linux

###Installation

Get and install Linx as described in the Linx project readme. Make sure that the kernel module linx.ko is loaded in your system.

Add linx4py to your pythonpath like this: 
```shell
export PYTHONPATH="${PYTHONPATH}"
```
Or install linx4py automatically using the setup.py script.
```shell
python setup.py install
```
