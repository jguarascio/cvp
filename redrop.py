#!/usr/bin/python3

import configparser
import os
import sys
import logging


def main():
    # Make sure the user passed a config file
    try:
        config_file = sys.argv[1]
    except:
        print('usage: redrop.py <config_file>')
        sys.exit(2)

    parser = configparser.ConfigParser()
    parser.read(config_file)

    # Read the default section of the config file
    if parser.has_section('default'):
        logfile = parser.get('default', 'logfile')
        threshold = int(parser.get('default', 'threshold'))
    else:
        logfile = '/var/log/cvpredrop.log'
        threshold = 10

    logging.basicConfig(filename=logfile, level=logging.INFO,
                        format='%(asctime)s %(message)s')

    # Check each route to see if there are files waiting to be moved
    for section_name in parser.sections():
        if section_name.startswith('route'):
            from_folder = parser.get(section_name, 'from')
            to_folder = parser.get(section_name, 'to')
            file_list = os.listdir(from_folder)
            file_count = len(file_list)

            # Only log if there are files present
            if file_count > threshold:
                logging.info('Too many DLQ files in %s. Only %s are allowed. There are %s',
                             from_folder, threshold, file_count)
            elif file_count > 0:
                for file_name in file_list:
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
                        encoded_contents = contents.encode()
                        if len(contents) != len(encoded_contents): 
                            os.remove(from_folder + file_name)
                            asciidata = encoded_contents.decode("ascii","ignore")
                            with open(to_folder + file_name, 'w') as f:
                                f.write(asciidata)
                            logging.info('DLQ file contained non ASCII characters. Fixed %s', file_name)
                        else:
                            os.rename(from_folder + file_name,
                                    to_folder + file_name)
                        logging.info('Moved %s from %s to %s',
                                     file_name, from_folder, to_folder)


if __name__ == '__main__':
    main()
