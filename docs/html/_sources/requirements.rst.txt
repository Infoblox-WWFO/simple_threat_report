============
Requirements
============

.. important::
  :mod:`simple_tide_report` requires Python 3.x and was developed under Python 3.6. As such they are unlikely to work with Python 2.x.

Special Libraries
-----------------

:mod:`simple_tide_report` makes use of the following 'homegrown' modules:

 * :mod:`ibtidelib`

A version of this has been included as part of the package.


Additional Modules
------------------

In addition to the standard Python 3.6 Modules :mod:`simple_tide_report` makes use of
the following packages:

 * :mod:`requests`
 * :mod:`tqdm`


Complete List Of Modules
------------------------

::

  import sys
  import os
  import shutil
  import datetime
  import argparse
  import collections
  import requests
  import json
  import logging
  import tqdm
  import ibtidelib

Modules used by ibtidelib ::

  import logging
  import os
  import re
  import ipaddress
  import requests
  import datetime
  import sqlite3
