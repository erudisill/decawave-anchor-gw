Decawave Anchor Gateway
=======================

Small console app that reads measurement data from an anchor and sends results to a TCP port.



Caveats
-------
	* Purely console driven, requires Ctl-C to exit
	* No logging at the moment
	* Pretty sparse exception handling - this is primarily a development tool ;)

Dependencies
------------
pyserial
jsonpickle