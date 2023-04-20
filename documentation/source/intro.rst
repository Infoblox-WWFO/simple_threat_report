============
Introduction
============

This script forms part of the Threat Intelligence toolkit whose aim is to 
provide demonstration scripts for BloxOne ThreatDefense. These can be used
for API demonstrations, or help to simplify PoCs for Threat Intelligence, 
demonstrating the value of BloxOne ThreatDefense and our threat intel offerings.

The simple_threat.py script is designed to read a list of hostnames, URLs
or IP address from a file and generate a simplified CSV report from BloxOne
ThreatDefense data.

The script can look at both the 'Active State' and complete TIDE data, in
addition to having the ability to use a local sqlite database containing
local TIDE data generated [#]_

In addition to TIDE data, for hosts, the script can now also look at web
categorisation data. In addition, it is also now possible to check not just 
the host itself, but also (where the domain name is >2 labels) check the 
status of the associated parent domain when not threat data is found. 

.. note::

	Both of these options require API access to BloxOne and are not available
	when using a local threat database.


.. [#] Please see the create-threat-intel-db.sh tool for more details
