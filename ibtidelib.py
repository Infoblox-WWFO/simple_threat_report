#!/usr/local/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
------------------------------------------------------------------------
 Description:
   Library to simplify scripting for Infoblox TIDE

 Requirements:
   Python3 with re, ipaddress, requests and sqlite3 modules

 Author: Chris Marrison

 ChangeLog:
   20190104    v2.1    Changed to Simplified BSD license
   20181122    v2.0    Added functions to get threat classes, properties
                       and stats
   20181112    v1.6    Bug fixes for offline database (import os)
   20181112    v1.5    Switched to logging, removed hard exit()s on exceptions
   20180619    v1.1    Cleaned up comments and self pydoc
   20180614    v1.0    Added requests exception handling
   20180614    v0.9    Moved querytideactive to querytidestate and
                       Created new querytideactive to use expiration field
   20180613    v0.8    Added local database functions (sqllite)
   20180502    v0.7    Added target type for dossier query
   20180501    v0.6    Added basic dossier query function
   20180501    v0.5    Added call for TIDE Active Datafeed
   20180430    v0.3    Added basic tide queries for a specific IOC
   20180424    v0.1    Initial test library collection including data types
 Todo:

 Copyright (c) 2018 Chris Marrison

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
__version__ = '2.1'
__author__ = 'Chris Marrison'

import logging
import os
import re
import ipaddress
import requests
import datetime
import sqlite3

### Global Vars ###
tideurl = "https://platform.activetrust.net:8000/api"
dossierurl = "https://platform.activetrust.net:8000/api/services/intel/lookup/jobs?wait=true"

### TIDE Functions ###

def threat_classes(apikey):
    """
    Query Infoblox TIDE for all available threat classes

        Input:
            apikey = TIDE API Key (string)

        Output:
           response.status_code or zero on exception
           response.txt or "Exception occurred." on exception
    """
    headers = { 'content-type': "application/json" }
    url = tideurl+'/data/threat_classes'

    # Call TIDE API
    try:
        response = requests.request("GET",url, headers=headers, auth=requests.auth.HTTPBasicAuth(apikey,''))
    # Catch exceptions
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return 0, "Exception occured."

    # Return response code and body text
    return response.status_code,response.text


def threat_properties(apikey, threatclass=""):
    """
    Query Infoblox TIDE for threat properties

        Input:
            apikey = TIDE API Key (string)
        Optional input:
            threatclass = threat class

        Output:
           response.status_code or zero on exception
           response.txt or "Exception occurred." on exception
    """
    headers = { 'content-type': "application/json" }
    url = tideurl+'/data/properties'
    if threatclass:
        url = url+'?class='+threatclass

    # Call TIDE API
    try:
        response = requests.request("GET",url, headers=headers, auth=requests.auth.HTTPBasicAuth(apikey,''))
    # Catch exceptions
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return 0, "Exception occured."

    # Return response code and body text
    return response.status_code,response.text


def threat_stats(apikey, period=""):
    """
    Query Infoblox TIDE for threat class stats

        Input:
            apikey = TIDE API Key (string)
        Optional input:
            period = one of ('daily', 'weekly', 'monthly')
            format = data format
            rlimit = record limit

        Output:
           response.status_code or zero on exception
           response.txt or "Exception occurred." on exception
    """
    if not period:
        period = "daily"
    elif period in ('daily', 'weekly', 'monthly'):
        period = "daily"

    headers = { 'content-type': "application/json" }
    url = tideurl+'/data/dashboard/'+period+'_threats_by_class'

    # Call TIDE API
    try:
        response = requests.request("GET",url, headers=headers, auth=requests.auth.HTTPBasicAuth(apikey,''))
    # Catch exceptions
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return 0, "Exception occured."

    # Return response code and body text
    return response.status_code,response.text


def querytide(datatype, query, apikey, format="",rlimit=""):
    """
    Query Infoblox TIDE for all available threat data

        Input:
            datatype = "host", "ip" or "url"
            query = query data
            apikey = TIDE API Key (string)
        Optional input:
            format = data format
            rlimit = record limit

        Output:
           response.status_code or zero on exception
           response.txt or "Exception occurred." on exception
    """
    headers = { 'content-type': "application/json" }
    url = tideurl+"/data/threats/"+datatype+"?"+datatype+"="+query
    if format:
        url = url+"&data_format="+format
    if rlimit:
        url = url+"&rlimit="+rlimit

    # Call TIDE API
    try:
        response = requests.request("GET",url, headers=headers, auth=requests.auth.HTTPBasicAuth(apikey,''))
    # Catch exceptions
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return 0, "Exception occured."

    # Return response code and body text
    return response.status_code,response.text


def querytideactive(datatype, query, apikey, format="",rlimit=""):
    """
    Query Infoblox TIDE for "active" threat data
    i.e. threat data that has not expired at time of call

        Input:
            datatype = "host", "ip" or "url"
            query = query data
            apikey = TIDE API Key (string)
        Optional input:
            format = data format
            rlimit = record limit

        Output:
           response.status_code or zero on exception
           response.txt or "Exception occurred." on exception
    """
    now = datetime.datetime.now()

    headers = { 'content-type': "application/json" }
    url = tideurl+"/data/threats/"+datatype+"?"+datatype+"="+query+"&expiration="+now.strftime('%Y-%m-%dT%H:%M:%SZ')
    if format:
        url = url+"&data_format="+format
    if rlimit:
        url = url+"&rlimit="+rlimit

    # Call TIDE API
    try:
        response = requests.request("GET",url, headers=headers, auth=requests.auth.HTTPBasicAuth(apikey,''))
    # Catch exceptions
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return 0, "Exception occured."

    # Return response code and body text
    return response.status_code,response.text



def querytidestate(datatype, query, apikey, format="",rlimit=""):
    """
    Query Infoblox TIDE State Tables for specific query

        Input:
            datatype = "host", "ip" or "url"
            query = query data
            apikey = TIDE API Key (string)
        Optional input:
            format = data format
            rlimit = record limit

        Output:
           response.status_code or zero on exception
           response.txt or "Exception occurred." on exception
    """
    headers = { 'content-type': "application/json" }
    url = tideurl+"/data/threats/state/"+datatype+"?"+datatype+"="+query
    if format:
        url = url+"&data_format="+format
    if rlimit:
        url = url+"&rlimit="+rlimit
    # Call TIDE API
    try:
        response = requests.request("GET",url, headers=headers, auth=requests.auth.HTTPBasicAuth(apikey,''))
    # Catch exceptions
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return 0, "Exception occured."

    # Return response code and body text
    return response.status_code, response.text



#TODO:
#def sortthreatsbyexpiry(tide_json):
     #Parse and sort threats by expiration
        #Input:
            #tide_json = TIDE threat data in json format
        #Ouput:
#
#def activethreat(tide_json):
    #"""
    #Filter on expiration date
        #Input:
            #tide_json = TIDE threat data in json format
        #Output:
            #listoflists
    #"""
#
    #t1 = datetime.datetime.now()
    #threats = json.loads(tide_json)
    #for threat in threats:
#"""

def tideactivefeed(datatype, apikey, profile="", threatclass="", format="", rlimit=""):
    """
    Bulk "active" threat intel download from Infoblox TIDE state tables
    for specified datatype.

        Required input:
            datatype = "host", "ip" or "url"
            apikey = TIDE API Key (string)
        Optional input:
            profile = Data provider
            threatclass = data class
            format = data format
            rlimit = record limit

        Output:
            response.status_code or zero on exception
            response.txt or "Exception occurred." on exception
    """
    # Build Headers
    headers = { 'content-type': "application/json" }
    # Build URL
    url = tideurl+"/data/threats/state/"+datatype
    if profile or threatclass or format or rlimit:
        url = url+"?"
    if profile:
        url = url+"&profile="+profile
    if threatclass:
        url = url+"&class="+threatclass
    if format:
        url = url+"&data_format="+format
    if rlimit:
        url = url+"&rlimit="+rlimit

    # Call TIDE API
    try:
        response = requests.request("GET",url, headers=headers, auth=requests.auth.HTTPBasicAuth(apikey,''))
    # Catch exceptions
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return 0, "Exception occured."

    # Return response code and body text
    return response.status_code, response.text

### Dossier functions ###

def dossierquery(query,apikey,type="host",sources="all"):
    """
    Simple Dossier Query

        Input:
            query = item to lookup
            apikey = TIDE APIKEY
        Output:
            rcode = response code
            rtext = response text
    """
    # Create RESTful API request
    if sources == "all":
        sources = '"alexa","atp","dns","gcs","geo","gsb","pdns","ptr","rwhois","sdf","virus_total","whois"'
    else:
        sources = '"'+sources+'"'

    payload = '{"target": {"one": {"type": "'+type+'", "target": "' + query + '", "sources": ['+sources+'] }}}'
    headers = { 'content-type': "application/json" }

    # Call Dossier API
    try:
        response = requests.request("post", dossierurl, data=payload, headers=headers, auth=requests.auth.HTTPBasicAuth(apikey,''))
    # Catch exceptions
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return 0, "Exception occured."

    # Return response code and body text
    return response.status_code, response.text


### Data Validation functions ###

def data_type(qdata, host_regex, url_regex):
    """
    Validate and determine data type (host, ip or url)

        Input:
            qdata - data to determine type/validity
            host_regex/url_regex: pre-compiled regexes

        Returns data type of qdata as one of "ip", "host", or "url"
    """
    if validate_ip(qdata):
        dtype = "ip"
    elif validate_url(qdata, url_regex):
        dtype = "url"
    elif validate_fqdn(qdata, host_regex):
        dtype = "host"
    else:
        dtype = "invalid"
    return dtype

def buildregex():
    """
    Pre-compile 'standard' regexes as used by data_type and
    validate_XXX functions

        Returns two compiled regexes for type host and url
    """
    #host_regex=re.compile(r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|')
    # Added _ for support of Microsoft domains
    host_regex = re.compile("(?!-)[A-Z\d\-\_]{1,63}(?<!-)$", re.IGNORECASE)
    url_regex = re.compile(
        #r'^(?:http|ftp)s?://' # http:// or https://
        r'^(?:http)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return host_regex, url_regex


def validate_fqdn(hostname,regex):
    """
    Validate input data is a legitmate fqdn

        Returns True if valid
        Returns False if not valid
    """
    if len(hostname) > 255 or len(hostname) < 1:
        result = False
    if hostname.endswith("."):
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    result = all(regex.match(x) for x in hostname.split("."))

    return result

def validate_ip(ip):
    """
    Validate input data is a valid IP address

        Returns True if valid
        Returns False if not valid
    """
    try:
        ipaddress.ip_address(ip)
        result = True
    except ValueError:
        result = False
    return result

def validate_url(url,regex):
    """
    Validate input data is a valid URL

        Returns True if valid
        Returns False if not valid
    """
    result = regex.match(url)
    return result


### Misc Functions

def reverse_labels(domain):
    """
    Reserve order of domain labels (or any dot separated data, e.g. IP)

        Input:
            domain = domain.labels
        Output:
            rdomain = labels.domain
    """
    rdomain = ""
    labels = domain.split(".")
    for l in reversed(labels):
        if rdomain:
            rdomain = rdomain+"."+l
        else:
            rdomain = l
    return rdomain

### Local db Functions

def opendb(dbfile):
    """
    Open sqlite db and return cursor()

        Input:
            dbfile = path to file
        Returns a db.cursor()
    """
    if os.path.isfile(dbfile):
        db = sqlite3.connect(dbfile)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
    else:
        logging.error("Database "+dbfile+" not found.")
        cursor = None

    return cursor

def get_table(cursor):
    """
    Determine db table and return

        Returns name of single db table
        exits with error if more than one table present
    """
    ### Determine table name ###
    select = 'SELECT name FROM sqlite_master WHERE type="table"'
    cursor.execute(select)
    tables = cursor.fetchall()
    ### Expecting single table ###
    if len(tables) == 1:
        ### Assume table is correct (even if it isn't) ###
        table = tables[0][0]
    else:
        ### Print error and exit ###
        logging.error("DB "+dbfile+" not of correct format - too many tables")
        table = None

    return table

def db_query(db_cursor,table,query_type,query_data,*flags):
    """
    Perform db query and return appropriate rows

        Input:
            db_cursor = db cursor object

        Output:
            All matching db rows
    """
    if query_type == "host":
        ### Form DB Query ###
        select = 'SELECT * FROM '+table+' WHERE host="'+query_data+'" OR domain="'+query_data+'"'
        # Ignore class = "Policy"
        if flags:
            select = select+' AND property!="Policy_UnsolictedBulkEmail"'
    elif query_type == "ip":
        ### Form DB Query ###
        select = 'SELECT * FROM '+table+' WHERE ip="'+query_data+'"'
        # Ignore class = "Policy"
        if flags:
            select = select+' AND property!="Policy_UnsolictedBulkEmail"'
    elif query_type == "url":
        ### Form DB Query ###
        select = 'SELECT * FROM '+table+' WHERE url="'+query_data+'"'
        # Ignore class = "Policy"
        if flags:
            select = select+' AND property!="Policy_UnsolictedBulkEmail"'
    else:
        logging.error("Invalid Type for {} data type for {} - should not be here".format(query_type,query_data))
        return None

    db_cursor.execute(select)
    rows = db_cursor.fetchall()
    return rows
