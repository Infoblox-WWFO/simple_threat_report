============
Introduction
============

This script forms part of the Threat Intelligence toolkit whose aim is to 
provide demonstration scripts for BloxOne ThreatDefense. These can be used
for API demonstrations, or help to simplify PoCs for Threat Intelligence, 
demonstrating the value of TIDE and our threat intel offerings.

The simple_tide_report.py script is designed to read a list of hostnames, URLs
or IP address from a file and generate a simplified CSV report from TIDE data.

The script can look at both the 'Active State' and complete TIDE data, in
addition to having the ability to use a local sqlite database containing
local TIDE data generated [#]_

This documentation assumes that you have python3 installed and are familiar with 
both the Unix command line, files and the use of pip/pip3 to install any 
appropriate modules.


.. [#] Please see the create-threat-intel-db.sh tool for more details
