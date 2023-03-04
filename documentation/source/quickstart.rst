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
