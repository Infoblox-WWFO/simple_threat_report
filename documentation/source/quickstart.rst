*****************
Quick Start Guide
*****************

The simplest place to start is to run the :mod:`simple_threat_report` Script
with the -h or --help option to display the simple usage help text.::

  $ ./simple_threat_report.py --help

  usage: simple_threat_report.py [-h] -i INPUT [-o OUTPUT] [-b BOGUS] [-c CONFIG]
                               [-k APIKEY] [-a] [-l LOCAL] [-d]

  TIDE reporting tool with simplified CSV output and statistics

  optional arguments:
    -h, --help            show this help message and exit
    -i INPUT, --input INPUT
                          Input filename
    -o OUTPUT, --output OUTPUT
                          CSV Output to <filename>
    -b BOGUS, --bogus BOGUS
                          Output invalid lines to file
    -c CONFIG, --config CONFIG
                          Overide Config file
    -a, --active          Process active only
    -C, --check_domains   Check domain in addition to fqdn (hosts only)
    -w, --webcat          Add Infoblox Web Categorisation Data (hosts only)
    -l LOCAL, --local LOCAL
                          Use local database <filename>
    -d, --debug           Enable debug messages


Configuring the API Key
========================

:mod:`simple_threat_report` supports the use of a config.ini file to store the API Key.

By default :mod:`simple_threat_report` will look for a ``config.ini`` file in the
current working directory. The default config.ini file can be overridden with
the --config/-c option. This allows you to call the script with alternative ini
files as needed without using the --apikey option.


ini File Format
---------------

A sample config.ini file is included with this package, however, the simple
format is shown below::

  [BloxOne]
  url = 'https://csp.infoblox.com'
  api_version = 'v1'
  api_key = '<you API Key here>'


Add you API Key from the BloxOne Portal to the :data:`api_key` property and save the
file. 


A Simple Example
================

Using the simple sample input file from the :doc:`Input File Format <input_format>` section below::

  www.google.com
  eicar.co
  http://t7rminal.space/
  1.1.1.1
  info.spiritsoft.cn

Which can be found in the file :file:`examples/example1.txt`

Action Field
============

The output file includes an additonal Action field to simplify reporting or
understanding of the output. Actions include::

  Active
    IOC belongs to a currently active Threat
  
  Not Active
    Historical data was found, however, it is not considered currently active
  
  Category Block (--webcat)
    No threat intel found but a policy block based on web category should be considered
  
  Country Block 
    A policy based on country blocks could be considered


The *Category Block* and *Country Block* actions are based on the contents 
of the *block_categories* and *country_codes* configuration files.

The field is not populated in the event that no match was found.


block_categories and country_codes
----------------------------------

The *block_categories* file contains a list of keywords that are used when
matching the web category to determine the Category Block recommendation when
there is no threat intel for the IOC.

The *country_codes* file contains a list of ccTLDs used to match when there is
no threat data or web categorisation match.

Sample versions of these files are included for example purposes only and do
not represent a policy or recommendation. The contents should be adapted as 
required by your security policies.
