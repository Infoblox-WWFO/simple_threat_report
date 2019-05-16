*****************
Quick Start Guide
*****************

The simplest place to start is to run the :mod:`simple_tide_report` Script
with the -h or --help option to display the simple usage help text.::

  $ ./simple_tide_report.py --help

  usage: simple_tide_report.py [-h] -i INPUT [-o OUTPUT] [-b BOGUS] [-k APIKEY]
                               [-a] [-l LOCAL] [-d]

  TIDE reporting tool with simplified CSV output and statistics

  optional arguments:
    -h, --help            show this help message and exit
    -i INPUT, --input INPUT
                          Input filename
    -o OUTPUT, --output OUTPUT
                          CSV Output to <filename>
    -b BOGUS, --bogus BOGUS
                          Output invalid lines to file
    -k APIKEY, --apikey APIKEY
                          Overide API Key
    -a, --active          Process active only
    -l LOCAL, --local LOCAL
                          Use local database <filename>
    -d, --debug           Enable debug messages


Configuring the API Key
========================

Although the script will accept your API Key as part of the command line using
the --key / -k option, you may wish to configure this within the script itself.
To do this edit the script with a text editor and search for the global variable
:data:`apikey` you will find the following line::

  apikey = ''

Add you API Key from the portal in between the '' and save the file. An example,
using a fictious key is shown::

  apikey = 'c3042afe88ea9a1a24b8fb220e203343a1e4ee08d1c8a00331594c802ad50a4c'

Once this step is complete you will not have to use the --apikey / -k option
unless you specifically want to override the configured key.

A Simple Example
================

Using the simple sample input file from the :doc:`Input File Format <input_format>` section below::

  www.google.com
  eicar.co
  http://t7rminal.space/
  1.1.1.1
  info.spiritsoft.cn

Which can be found in the file :file:`examples/example1.txt`
