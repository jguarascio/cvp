#!/usr/bin/python

from ConfigParser import SafeConfigParser
import os
import sys
import logging

# Make sure the user passed a config file
try:
        config_file = sys.argv[1]
except:
        print 'usage: redrop.py <config_file>'
        sys.exit(2)

parser = SafeConfigParser()
parser.read(config_file)

# Read the default section of the config file
if parser.has_section('default'):
        logfile = parser.get('default', 'logfile')
        threshold = int(parser.get('default', 'threshold'))
else:
        logfile = '/var/log/cvpredrop.log'
        threshold = 10

logging.basicConfig(filename=logfile, level=logging.INFO,format='%(asctime)s %(message)s')

# Check each route to see if there are files waiting to be moved
for section_name in parser.sections():
        if section_name != 'default':
                from_folder = parser.get(section_name, 'from')
                to_folder = parser.get(section_name, 'to')
                list = os.listdir(from_folder)
                file_count = len(list)

                # Only log if there are files present
                if file_count > threshold:
                        logging.info('Too many DLQ files in %s. Only %s are allowed. There are %s', from_folder, threshold, file_count)
                elif file_count > 0:
                        for file in list:
                                # Check to see if file has an error
                                f = open(from_folder + file, 'r')
                                contents = f.read()
                                f.close()
                                if 'java.lang.NullPointerException' in contents:
                                        os.remove(from_folder + file)
                                        logging.info('DLQ contained java.lang.NullPointerException. Deleted %s', file)
                                        logging.info(contents)
                                else:
                                        os.rename(from_folder + file, to_folder + file)
                                        logging.info('Moved %s from %s to %s', file, from_folder, to_folder)
