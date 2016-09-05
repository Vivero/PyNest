#!/usr/bin/python

import argparse, json, os, psycopg2, signal, sys, yaml

import lib.nest as nest

from lib.nest import Nest

from datetime import datetime
from time import sleep

class PyNest:

    def __init__(self, auth_file, db_info=None):
        self.terminate = False
        signal.signal(signal.SIGTERM, self.stop)

        # get authorization information
        with open(auth_file, 'r') as stream:
            try:
                auth_data = yaml.load(stream)
            except yaml.YAMLError as e:
                raise e

        # create Nest API object
        self.nest = Nest(auth_data)

        # use database?
        self.db_conn = None
        if db_info is not None:
            try:
                self.db_conn = psycopg2.connect(
                    database=db_info['dbname'], 
                    user=db_info['dbuser'], 
                    password=db_info['dbpass'], 
                    host=db_info['dbhost'])
            except psycopg2.Error as e:
                print("Unable to connect to database!\n{:s}".format(str(e)))
                self.db_conn = None


    def start(self):
        while (not self.terminate):
            #dt = datetime.now()
            #print("PyNest! {:s}".format(dt.strftime("%A, %d. %B %Y %I:%M:%S%p")))

            # get Nest API data
            nest_data = self.nest.get_data()
            #print json.dumps(nest_data, indent=4, sort_keys=True)


            # store in database
            if (nest_data is not None) and (self.db_conn is not None):
                creation_date = datetime.now()

                thermostats = nest_data["devices"]["thermostats"].keys()
                thermostat_data = nest_data["devices"]["thermostats"][thermostats[0]]

                cursor = self.db_conn.cursor()
                cursor.execute("INSERT INTO thermostat_readings (device_id, name, has_leaf, target_temperature_f, target_temperature_high_f, target_temperature_low_f, away_temperature_high_f, away_temperature_low_f, hvac_mode, ambient_temperature_f, humidity, hvac_state, raw_data, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())", (
                            thermostat_data['device_id'],
                            thermostat_data['name'],
                            thermostat_data['has_leaf'],
                            thermostat_data['target_temperature_f'],
                            thermostat_data['target_temperature_high_f'],
                            thermostat_data['target_temperature_low_f'],
                            thermostat_data['away_temperature_high_f'],
                            thermostat_data['away_temperature_low_f'],
                            thermostat_data['hvac_mode'],
                            thermostat_data['ambient_temperature_f'],
                            thermostat_data['humidity'],
                            thermostat_data['hvac_state'],
                            json.dumps(nest_data),
                        )
                    )
                self.db_conn.commit()
                cursor.close()

            # wait till next polling period
            sleep(6.0)

        print("Terminating...")

    def stop(self, signum, frame):
        self.terminate = True


if __name__ == '__main__':
    
    # parse command-line arguments
    #===========================================================================
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-a", "--authorize", 
        help="Generate an authorization key file",
        action="store_true")
    arg_parser.add_argument("-d", "--no-db", 
        help="Disables the use of a database store",
        action="store_true")
    args = arg_parser.parse_args()
    
    generate_authorization = args.authorize
    disable_database = args.no_db
    
    
    # start the application
    #===========================================================================
    
    # environment setup
    auth_file = os.environ['PYNEST_AUTH_FILE']

    # authorization tool
    if (generate_authorization):
        nest_id = os.environ['NEST_CLIENT_ID']
        nest_secret = os.environ['NEST_CLIENT_SECRET']

        nest.generate_authorization_file(nest_id, nest_secret, auth_file)

    # data logger service
    else:
        db_info = None
        if not disable_database:
            db_info = {
                'dbname': os.environ['PYNEST_DB_NAME'],
                'dbuser': os.environ['PYNEST_DB_USER'],
                'dbpass': os.environ['PYNEST_DB_PASS'],
                'dbhost': os.environ['PYNEST_DB_HOST'],
            }

        pynest = PyNest(auth_file, db_info)
        pynest.start()
    
    sys.exit(0)
