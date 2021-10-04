#!/bin/sh
###############################
# Create threat db from TIDE
# for all threat types
#
# Author: Chris Marrison
# Date: 11th Dec 2017
# Last updated: 16th Jan 2018
###############################

### Global Vars ###
DBONLY=0
FORCE=0
APIKEY="a9a1a24b8c3042a3a1efe88efb220e20d1c8a00333344ee081594c802ad50a4c"
DATE=`date +%Y%m%d`
TYPES="host ip url"
TYPE=""
TABLE="indicators"

###############
# Subroutines #
###############

### Get active threats for type ${TYPE} via TIDE API ###
GETACTIVETHREATS()
{
echo "Retrieving active threats from TIDE for type ${TYPE}..."
curl --request GET --url "https://platform.activetrust.net:8000/api/data/threats/state/${TYPE}?&data_format=csv" \
	-u ${APIKEY}: > ${FILE}
if [ $? -eq 0 ]
then
	echo "CSV data retrieved."
	echo
else
	echo "Failed to retrieve data from TIDE for type ${TYPE}"
	exit 1
fi
}

### Create db with domain index ###

CREATEDB ()
{
echo "Creating database ${DB}..."
HOSTFILE="${DATE}-active-host-threats.csv"
IPFILE="${DATE}-active-ip-threats.csv"
URLFILE="${DATE}-active-url-threats.csv"

sqlite3 --batch ${DB} << EOF
.mode csv
.import ${HOSTFILE} ${TABLE}
.import ${IPFILE} ${TABLE}
.import ${URLFILE} ${TABLE}
CREATE INDEX idx_domain on ${TABLE} (domain);
CREATE INDEX idx_host on ${TABLE} (host);
CREATE INDEX idx_ip on ${TABLE} (ip);
CREATE INDEX idx_url on ${TABLE} (url);
.schema
EOF
echo "${DB} created."
}

USAGE()
{
	echo
	echo "Usage: $0 [db|force] <filename>"
	echo "-db: Create db only"
	echo "-d: Force use of existing CSV files."
	echo
	exit 1
}



############
### Main ###
############

### Check options ###
if [ $# -eq 0 ]
then
	DB="active-threat-intel.db"

elif [ $# -eq 1 ]
then
	if [ $1 == "db" ]
	then
		DBONLY=1
		DB="active-threat-intel.db"
	elif [ $1 == "force" ]
	then
		FORCE=1
		DB="active-threat-intel.db"
	else
		DB=$1
	fi

elif [ $# -eq 2 && $1 == "db"]
then
	DBONLY=1
	DB=$2

elif [ $# -eq 2 && $1 == "force"]
then
	FORCE=1
	DB=$2
else
	USAGE
fi


### Check for file ###
if [ -f ${DB} ]
then
	echo "Database ${DB} already exists."
else

	if [ ${DBONLY} = 0 ]
	then
		for TYPE in ${TYPES}
		do
			FILE="${DATE}-active-${TYPE}-threats.csv"
			if [ -f ${FILE} ]
			then
				if [ ${FORCE} -eq 0 ]
				then
					echo "File ${FILE} already exists."
					exit 1
				else
					echo "Using existing file ${FILE} for type ${TYPE}."
				fi
			else
    				GETACTIVETHREATS
			fi
		done
	fi

	### Create DB files ###
	CREATEDB
fi
exit 0

### End MAIN ###
