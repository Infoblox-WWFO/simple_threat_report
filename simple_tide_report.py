#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
------------------------------------------------------------------------

 Description:
  Lookup query against TIDE active state and historic data
  producing basic report on whether there is active/historical
  data with simplified report output.

  For more extensive output for a specific IOC use tide-lookup.py

 Requirements:
  Requires ibtidelib, requests, tqdm

 Usage:
    simple_tide_report.py [options] <query>
        -h  help
        -i  <file> Input file (one IOC per line)
        -o  <file> CSV Output file for results
        -b  <file> File for reporting of bogus lines
        -k  <key> TIDE apikey
        -a  active threats only
        -l  local database (activeonly)
        -d  debug output

 Author: Chris Marrison

 Date Last Updated: 20190510

 .. todo::
    * Config file
    * Option to treat URLs as hostnames i.e. parse URL to extract host
    * Considering adding option to do DNS lookup on hosts and TIDE lookups
      on returned CNAMEs and IPs, however, may need different data structure

Copyright 2019 Chris Marrison / Infoblox

Redistribution and use in source and binary forms,
with or without modification, are permitted provided
that the following conditions are met:

1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

------------------------------------------------------------------------
"""
__version__ = '2.5'
__author__ = 'Chris Marrison'

import sys
import os
import shutil
import datetime
import configparser
import argparse
import collections
import requests
import json
import logging
import tqdm

# Add '.' to path if ios (Pythonista) to find ibtidelib
if sys.platform == 'ios':
    sys.path.append('.')

import ibtidelib

# ** Global Variables **
# apikey = ''
log = logging.getLogger(__name__)

# ** Functions **

def read_config(cfg_filename):
    '''
    Open and parse ini file

    Parameters:
        cfg_filename (str): name of inifile

    Returns:
        api_key (str): API Key for authentication

    '''
    cfg = configparser.ConfigParser()

    # Attempt to read api_key from ini file
    try:
        cfg.read(cfg_filename)
    except configparser.Error as err:
        log.error(err)

    # Look for TIDE section
    if 'TIDE' in cfg:
        # Check for api_key in TIDE section
        if 'api_key' in cfg['TIDE']:
            api_key = cfg['TIDE']['api_key'].strip("'\"")
            log.debug('API Key Found in {}: {}'.format(cfg_filename, api_key))
        else:
            log.warn('No API key (api_key) variable in section TIDE.')
            api_key = ''
    else:
        log.warn('No TIDE Section in config file: {}'.format(cfg_filename))
        api_key = ''

    return api_key

def parseargs():
    '''
    Parse Arguments Using argparse

    Parameters:
        None

    Returns:
        Returns parsed arguments
    '''
    parse = argparse.ArgumentParser(description='TIDE reporting tool with '
                                    'simplified CSV output and statistics')
    parse.add_argument('-i', '--input', type=str, required=True,
                       help="Input filename")
    parse.add_argument('-o', '--output', type=str,
                       help="CSV Output to <filename>")
    parse.add_argument('-b', '--bogus', type=str,
                       help="Output invalid lines to file")
    parse.add_argument('-c', '--config', type=str, default='config.ini',
                       help="Overide Config file")
    parse.add_argument('-k', '--apikey', type=str,
                       help="Overide API Key")
    parse.add_argument('-a', '--active', action='store_true',
                       help="Process active only")
    parse.add_argument('-l', '--local', type=str,
                       help="Use local database <filename>")
    parse.add_argument('-d', '--debug', action='store_true',
                       help="Enable debug messages")

    return parse.parse_args()


def setup_logging(debug):
    '''
     Set up logging

     Parameters:
        debug (bool): True or False.

     Returns:
        None.

    '''
    # Set debug level
    if debug:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s: %(message)s')

    # Create logger and add Console handler
    # log = logging.getLogger(__name__)
    # log.addHandler(fileh)
    # log.addHandler(console)
    return


def open_file(filename):
    '''
     Attempt to open output file

     Parameters:
        filename (str): Name of file to open.

     Returns:
        file handler object.

    '''
    if os.path.isfile(filename):
        backup = filename+".bak"
        try:
            shutil.move(filename, backup)
            log.info("Outfile exists moved to {}".format(backup))
            try:
                handler = open(filename, mode='w')
                log.info("Successfully opened output file {}."
                         .format(filename))
            except IOError as err:
                log.error("{}".format(err))
                handler = False
        except IOError:
            log.warning("Could not backup existing file {}."
                        .format(filename))
            handler = False
    else:
        try:
            handler = open(filename, mode='w')
            log.info("Successfully opened output file {}.".format(filename))
        except IOError as err:
            log.error("{}".format(err))
            handler = False

    return handler


def output_bogus(data, file, line_number):
    '''
    Write invalid data to file

    Parameters:
        data (str): data to Write
        file (filehandle): file handler
        line_number (int): bogus line number

    Returns:
        no data.

    '''
    file.write(str(line_number)+":   "+data+"\n")
    return


def output_counter(cc):
    '''
    Output all entries in a counter by value

    Parameters:
        cc is a collection.Counter() obj.

    Returns:
        No data.

    '''
    for key in cc.items():
        print('  {}: {}'.format(key[0], key[1]))
    return


def getkeys(cc):
    '''
    Get keys from collections.Counter object

    Parameters:
        cc: collection.counter object

    Returns:
        keys: List of keys in counter

    '''
    keys = []
    for item in cc.items():
        keys.append(item[0])

    return keys


def most_recent(t1, t2):
    '''
    Compare two datetime stamps and return most recent

    Parameters:
        t1: timestamp
        t2: timestamp

    Returns:
        mostrecent: most recent timestamp from t1,t2.

    '''
    if t1 > t2:
        mostrecent = t1
    else:
        mostrecent = t2
    return mostrecent


def checkactive(query, qtype, apikey):
    '''
    Check for active threat intel, parse and output results

    Parameters:
        query (str): hostname, ip, or url
        qtype (str): query type (host, ip, url)
        apikey (str): TIDE API key

    Returns:
        totalthreats (int): number of active threats Found
        profiles (list): TIDE Profiles
        tclasses (list): List of threat classes

    '''
    # Set up local counters
    totalthreats = 0
    profile_stats = collections.Counter()
    class_stats = collections.Counter()
    # threat_types = collections.Counter()
    # property_stats = collections.Counter()
    profiles = []
    tclasses = []

    # Query active TIDE data
    rcode, rtext = ibtidelib.querytidestate(qtype, query, apikey)
    # Process Response
    if rcode == requests.codes.ok:
        # Parse json
        parsed_json = json.loads(rtext)

        log.debug('Quey: {}, Query type: {}'.format(query, qtype))
        log.debug('Raw response: {}'.format(rtext))

        # Parse Results
        # Check for threat construct
        if "threat" in parsed_json.keys():
            for threat in parsed_json['threat']:
                # Collect stats
                totalthreats += 1
                profile_stats[threat['profile']] += 1
                class_stats[threat['class']] += 1
                # threat_types[threat['type']] += 1
                # property_stats[threat['property']] += 1

            # Generate basic output
            profiles = getkeys(profile_stats)
            tclasses = getkeys(class_stats)
            log.debug('{}, {} active threat(s) {}'.format(query, totalthreats,
                                                          profiles))
        else:
            log.debug('{}, No active threats found'.format(query))

    else:
        log.error("Query Failed with response: {}".format(rcode))
        log.error("Body response: {}".format(rtext))
        totalthreats = -1
        profiles = "API Exception Occurred"

    return totalthreats, profiles, tclasses


def checktide(query, qtype, apikey):
    '''
    Check against all threat intel data, parse and output results

    Parameters:
        query (str): hostname, ip, or url
        qtype (str): query type (host, ip, url)
        apikey (str): TIDE API key

    Returns:
        totalthreats (int): number of active threats Found
        profiles (list): TIDE Profiles
        tclasses (list): List of threat classes
        last_available (datetime): Most recent 'available' date if available
        last_expiration (datetime): Most recent 'expiration' date if available

    '''
    # Set up local counters
    totalthreats = 0
    profile_stats = collections.Counter()
    class_stats = collections.Counter()
    last_available = datetime.datetime.fromtimestamp(0)
    last_expiration = datetime.datetime.fromtimestamp(0)
    # threat_types = collections.Counter()
    # property_stats = collections.Counter()
    profiles = []
    tclasses = []

    # Query TIDE (complete)
    rcode, rtext = ibtidelib.querytide(qtype, query, apikey)

    # Process response
    if rcode == requests.codes.ok:

        # Parse json
        parsed_json = json.loads(rtext)

        log.debug('Quey: {}, Query type: {}'.format(query, qtype))
        log.debug('Raw response: {}'.format(rtext))

        # Check for threat construct
        if "threat" in parsed_json.keys():
            for threat in parsed_json['threat']:
                # Collect stats
                totalthreats += 1
                profile_stats[threat['profile']] += 1
                class_stats[threat['class']] += 1
                # threat_types[threat['type']] += 1
                # property_stats[threat['property']] += 1

                # Collect available/expiration dates, determine most recent
                available = datetime.datetime.strptime(threat['imported'],
                                                       '%Y-%m-%dT%H:%M:%S.%fZ')
                last_available = most_recent(last_available, available)
                if "expiration" in threat.keys():
                    expiration = datetime.datetime.strptime(
                        threat['expiration'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    last_expiration = most_recent(last_expiration, expiration)

            # Add basic output
            profiles = getkeys(profile_stats)
            tclasses = getkeys(class_stats)
            log.debug('{}, {} total item(s) of threat intel {}, {}'
                      .format(query, totalthreats, profiles, tclasses))
        else:
            log.debug('{}, No threat intel found'.format(query))

    else:
        log.error("Query Failed with response: {}".format(rcode))
        log.error("Body response: {}".format(rtext))
        totalthreats = -1
        profiles = "API Exception Occurred"

    # Check whether dates were updated
    if last_available == datetime.datetime.fromtimestamp(0):
        last_available = ''
    if last_expiration == datetime.datetime.fromtimestamp(0):
        last_expiration = ''

    return totalthreats, profiles, tclasses, last_available, last_expiration


def checkoffline(query, qtype, db_cursor, db_table):
    '''
     Check for active threat intel using local database

     Parameters:
        query (str): hostname, ip, or url
        qtype (str): query type (host, ip, url)
        db_cursor (db.cursor): database cursor
        db_table (db.table): database table

     Returns:
        totalthreats (int): number of active threats Found
        profiles (list): TIDE Profiles
        tclasses (list): List of threat classes

    '''
    # Set up local counters
    totalthreats = 0
    profile_stats = collections.Counter()
    class_stats = collections.Counter()
    # threat_types = collections.Counter()
    # property_stats = collections.Counter()
    profiles = []
    tclasses = []

    # Query active TIDE data
    rows = ibtidelib.db_query(db_cursor, db_table, qtype, query)
    # Process Response

    log.debug('Quey: {}, Query type: {}'.format(query, qtype))
    log.debug('Raw response: {}'.format(rows))

    # Parse Results
    # Check for threat construct
    if rows:
        for row in rows:
            # Collect stats
            totalthreats += 1
            profile_stats[row['profile']] += 1
            class_stats[row['class']] += 1

        # Generate basic output
        profiles = getkeys(profile_stats)
        tclasses = getkeys(class_stats)
        log.debug('{}, {} active threat(s) {}'.format(query, totalthreats,
                                                      profiles))
    else:
        log.debug('{}, No active threats found'.format(query))

    return totalthreats, profiles, tclasses


def gen_report(activethreats, totalthreats, filehandle):
    '''
    Generate Threat Report

    Parameters:
        activethreats (dict): Dictionary of active threat query data
        totalthreats (dict): Dictionary of all threat query data
        filehandle (fh or None): file handler or None

    Returns:
        Report to STDOUT and/or file
        No return data

    '''
    # Local Variables
    total_hosts = len(activethreats)
    with_active = 0
    with_threats = 0

    # Parse items and output
    if len(totalthreats) == 0:
        # Assert Active Only
        # Check for CSV output
        if filehandle:
            # Write Header
            print('Host,Active Threats,Active Profiles,Active Classes',
                  file=filehandle)
        for item in activethreats:
            # Summarise Info
            # total_hosts += 1
            if activethreats[item][0] > 0:
                with_active += 1

            # Human Output
            print('Host: {}, Active threats: {}, Active profiles: {}, '
                  'Classes: {}' .format(item, activethreats[item][0],
                                        activethreats[item][1],
                                        activethreats[item][2]))

            # File output
            if filehandle:
                print('{},{},"{}","{}"'.format(item, activethreats[item][0],
                                               activethreats[item][1],
                                               activethreats[item][2]),
                      file=filehandle)

        # Add Summary
        # Human
        print('Summary: Total = {}, Active = {}, Not active = {}'
              .format(total_hosts, with_active, total_hosts - with_active))
        # File
        if filehandle:
            print('Summary: Total = {}, Active = {}, Not active = {}'
                  .format(total_hosts, with_active, total_hosts - with_active),
                  file=filehandle)

    else:
        # Assert active and total threats
        # Check for CSV output
        if filehandle:
            # Write Header
            print('Host,Active Threats,Active Profiles,Total Indicators, '
                  'Indicator Profiles, Threat Classes,Last Seen,Last Expiry',
                  file=filehandle)
        for item in activethreats:
            # Summarise Info
            # total_hosts += 1
            if activethreats[item][0] > 0:
                with_active += 1
            if totalthreats[item][0] > 0:
                with_threats += 1

            # Human Output
            print('Host: {}, Active threats: {}, Active profiles: {}, '
                  'Total threats: {}, Profiles: {}, Classes: {}, '
                  'Last seen: {}, Last Expiry: {}'
                  .format(item, activethreats[item][0], activethreats[item][1],
                          totalthreats[item][0], totalthreats[item][1],
                          totalthreats[item][2], totalthreats[item][3],
                          totalthreats[item][4]))
            # File output
            if filehandle:
                print('{},{},"{}",{},"{}","{}",{},{}'
                      .format(item, activethreats[item][0],
                              activethreats[item][1], totalthreats[item][0],
                              totalthreats[item][1], totalthreats[item][2],
                              totalthreats[item][3], totalthreats[item][4]),
                      file=filehandle)
        # Add Summary
        # Human
        print('Summary: Total = {}, Active = {}, Threats = {}, No info = {}'
              .format(total_hosts, with_active, with_threats,
                      total_hosts - with_threats))
        # File
        if filehandle:
            print('Summary: Total = {}, Active = {}, Threats = {}, '
                  'No info = {}'.format(total_hosts, with_active, with_threats,
                                        total_hosts - with_threats),
                  file=filehandle)

    if filehandle:
        print('CSV output written to {}'.format(filehandle.name))

    return


def main():
    '''
    * Main *

    Core logic when running as script

    '''
    #global apikey

    # Local Variables
    exitcode = 0
    activethreats = {}
    totalthreats = {}
    # threats = 0
    linecount = 0
    total_lines = 0
    bogus_lines = 0
    # profiles = ''

    # Parse Arguments and configure
    args = parseargs()

    # Set up logging
    debug = args.debug
    setup_logging(debug)

    # File Options
    bogusfilename = args.bogus
    inputfile = args.input
    outputfile = args.output
    if args.config:
        configfile = args.config
    else:
        configfile = 'config.ini'

    # Set API Key
    if args.apikey:
        apikey = args.apikey
    else:
        apikey = read_config(configfile)
    if apikey == '':
        log.error('API Key not set.')

    # General Options
    activeonly = args.active

    # Local database option
    if args.local:
        database = args.local
        # Force activeonly
        log.debug('Forcing check for active threats only.')
        activeonly = True
        log.debug('Opening local database {}'.format(database))
        db_cursor = ibtidelib.opendb(database)
        if db_cursor:
            db_table = ibtidelib.get_table(db_cursor)
            if not db_table:
                log.error('Local database table error, exiting.')
                sys.exit(1)
            else:
                log.info('Using local database for active lookups.')
                log.debug('Database opened successfully.')
        else:
            log.error('Local database error, exiting.')
            sys.exit(1)
    else:
        database = None

    # Set up output file for bogus lines
    if bogusfilename:
        bogus_out = open_file(bogusfilename)
        if not bogus_out:
            log.error('Failed to open output file for bogus lines.')
            exit(1)
    else:
        bogus_out = False

    # Set up output file for CSV
    if outputfile:
        outfile = open_file(outputfile)
        if not outfile:
            log.warning('Failed to open output file for CSV. Outputting to stdout only.')
    else:
        outfile = False

    # Build regexes for data_type checking
    host_regex, url_regex = ibtidelib.buildregex()

    # Check for input file and attempt to read
    log.debug('Attempting to open input file: {}'.format(inputfile))
    try:
        # Open input file
        with open(inputfile) as file:
            # Determine number of lines
            for line in file:
                total_lines += 1
            # Return to start of file
            file.seek(0)
            log.debug('File {} opened, with {} lines'
                      .format(inputfile, total_lines))

            # Process file
            with tqdm.tqdm(total=total_lines) as pbar:
                for line in file:
                    query = str(line.rstrip())
                    linecount += 1
                    # Update progress bar
                    pbar.update(1)

                    # Get data type for query
                    qtype = ibtidelib.data_type(query, host_regex, url_regex)

                    # Check qtype and log bogus lines
                    log.debug("Query: {}".format(query))
                    log.debug("Data type of query: {}".format(qtype))

                    if qtype != "invalid":
                        # Determine TIDE or Local db
                        if database:
                            # Use local database
                            log.debug("Querying local database.")
                            activethreats[query] = checkoffline(query,
                                                                qtype,
                                                                db_cursor,
                                                                db_table)
                        else:
                            # Call checkactive
                            log.debug("Querying TIDE Active State Table...")
                            activethreats[query] = checkactive(query,
                                                               qtype,
                                                               apikey)

                        # Call checktide
                        if not activeonly:
                            log.debug("Querying TIDE for all data...")
                            totalthreats[query] = checktide(query,
                                                            qtype,
                                                            apikey)
                    else:
                        # ASSERT: qtype == "invalid"
                        bogus_lines += 1
                        if bogus_out:
                            output_bogus(query, bogus_out, linecount)

        # Output Report
        gen_report(activethreats, totalthreats, outfile)

    except IOError as error:
        log.error(error)
        exitcode = 1

    finally:
        # Close files
        if outfile:
            outfile.close()
        if bogus_out:
            bogus_out.close()

        log.debug("Processing complete.")

    return exitcode


# ** Main **
if __name__ == '__main__':
    exitcode = main()
    raise SystemExit(exitcode)

# ** End Main **
