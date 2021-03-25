#!/usr/bin/python

import os
import sys
import logging
import ConfigParser # python2 version
#import configparser # python3 version


def main():
    # Make sure the user passed a config file
    try:
        config_file = sys.argv[1]
    except:
        print('usage: redrop.py <config_file>')
        sys.exit(2)

    parser = ConfigParser.SafeConfigParser() # python2 version
    #parser = configparser.ConfigParser() #python3 version
    parser.read(config_file)

    # Read the default section of the config file
    if parser.has_section('default'):
        base_path = parser.get('default', 'basepath')
        log_file = parser.get('default', 'logfile')
        threshold = int(parser.get('default', 'threshold'))
    else:
        log_file = '/var/log/cvpredrop.log'
        threshold = 10

    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s %(message)s')

    # Read skip file if it exists
    skip_file = os.path.splitext(log_file)[0] + '.skip'
    if os.path.isfile(skip_file):
        with open(skip_file, 'r') as f:
            skip_list = f.read().splitlines()
    else:
        skip_list = []

    # Check each route to see if there are files waiting to be moved
    for section_name in parser.sections():
        if section_name.startswith('route'):
            from_folder = base_path + parser.get(section_name, 'from')
            to_folder = base_path + parser.get(section_name, 'to')

            # Skip route if path does not exist
            if not os.path.isdir(from_folder) or not os.path.isdir(to_folder):
                continue 

            # Get folder contents
            file_list = os.listdir(from_folder)
            file_count = len(file_list)

            # Only log if there are files present
            if file_count > threshold:
                logging.info('Too many DLQ files in %s. Only %s are allowed. There are %s',
                             from_folder, threshold, file_count)
            elif file_count > 0:
                for file_name in file_list:
                    # Skip file if already redropped
                    if file_name in skip_list:
                        logging.info('Already redropped. Skipping %s', file_name)
                        continue

                    # Read file contents
                    with open(from_folder + file_name, 'r') as f:
                        contents = f.read()

                    # Check to see if file has an error
                    if 'java.lang.NullPointerException' in contents:
                        os.remove(from_folder + file_name)
                        logging.info('DLQ file contained java.lang.NullPointerException. Deleted %s', file_name)
                        logging.info(contents)
                    else:
                        # Check file for bad characters
                        ascii_contents = contents.decode('ascii','ignore') #python2 version
                        #ascii_contents = contents.encode().decode('ascii','ignore') #python3 version
                        if len(contents) != len(ascii_contents): 
                            os.remove(from_folder + file_name)
                            with open(to_folder + file_name, 'w') as f:
                                f.write(ascii_contents)
                            logging.info('DLQ file contained non ASCII characters. Fixed %s', file_name)
                            logging.info(contents)
                        else:
                            os.rename(from_folder + file_name,
                                    to_folder + file_name)
                        logging.info('Moved %s from %s to %s',
                                     file_name, from_folder, to_folder)
                        
                        # Remember the files that were redropped
                        with open(skip_file, 'a') as f:
                            f.write(file_name + '\n')


if __name__ == '__main__':
    main()
