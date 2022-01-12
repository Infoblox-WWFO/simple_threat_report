*****************
Quick Start Guide
*****************

The simplest place to start is to run the :mod:`simple_tide_report` Script
with the -h or --help option to display the simple usage help text.::

  $ ./simple_tide_report.py --help

  usage: simple_tide_report.py [-h] -i INPUT [-o OUTPUT] [-b BOGUS] [-c CONFIG]
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
    -k APIKEY, --apikey APIKEY
                          Overide API Key
    -a, --active          Process active only
    -l LOCAL, --local LOCAL
                          Use local database <filename>
    -d, --debug           Enable debug messages

Configuring the API Key
========================

Although the script will accept your API Key as part of the command line using
the --apikey / -k option, :mod:`simple_tide_report` supports the use of a config.ini file to store the API Key.

.. note::
  Using the --apikey/-k option overrides any API Key stored in
  the ``config.ini``

By default :mod:`simple_tide_report` will look for a ``config.ini`` file in the
current working directory. The default config.ini file can be overridden with
the --config/-c option. This allows you to call the script with alternative ini
files as needed without using the --apikey option.

ini File Format
---------------

A sample config.ini file is included with this package, however, the simple
format is shown below::

  [TIDE]
  api_key = <your API Key Here>

Add you API Key from the portal to the :data:`apikey` property and save the
file. An example, using a fictious key is shown::

  [TIDE]
  apikey = c3042afe88ea9a1a24b8fb220e203343a1e4ee08d1c8a00331594c802ad50a4c

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
