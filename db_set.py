import os
import time
import utils
import logging
import sqlite3

# Rather than have a single generic "db query" style function where I pass in the sql to be executed, I'm doing the SQL
# operations in individual functions - it'd be more maintenance in real life but this is a small/one-off project so a deliberate design choice

# Initially I had all code in bambi.py but it became far too annoying to traverse to update/add new features
# so I refactored anything "setter" in db_set.py
# this script is primarily concerned with UPDATE/INSERT/DELETE statements necessary to render the different menus

logger = logging.getLogger(__name__)
logger.info("Started logging in db_set.py")


def add_pilot(DB_FILE, new_pilot_name):
    utils.log_active_function()
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        insert_new_pilot = '''
                INSERT INTO Pilot (pilot_name)
                VALUES (?)
            '''
        values = (new_pilot_name,)
        # This caused me numerous problems.  When passing in "David" I would get
        # ERROR - Database error Incorrect number of bindings supplied. The current statement uses 1, and there are 5 supplied.
        # it was treating every character in my name as a value to insert
        # It took a while to find the right search query but eventuall found this
        # https://stackoverflow.com/questions/16856647/sqlite3-programmingerror-incorrect-number-of-bindings-supplied-the-current-sta
        # Answered Martijn Peters May 31 2013, checked April 5th
        # Adding , after the value makes it a tuple not a list of characters

        logging.debug(f"{insert_new_pilot}")
        cursor.execute(insert_new_pilot, values)
        connection.commit()
        logging.info(f"New pilot inserted {new_pilot_name}")
        return True
    except sqlite3.DatabaseError as dbe:
        logger.error(f"Database error {dbe}")
    except Exception as exc:
        logger.error(f"Unknown error {exc}")
    finally:
        connection.close()

def update_pilot(DB_FILE, updated_pilot_name, pilot_id):
    utils.log_active_function()
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        update_pilot = '''
                UPDATE Pilot
                SET pilot_name = ?
                WHERE pilot_id = ?;
            '''
        values = (updated_pilot_name,pilot_id)

        logging.debug(f"{update_pilot}")
        cursor.execute(update_pilot, values)
        connection.commit()
        logging.info(f"Pilot {pilot_id} updated, new name {updated_pilot_name}")
        return True
    except sqlite3.DatabaseError as dbe:
        logger.error(f"Database error {dbe}")
    except Exception as exc:
        logger.error(f"Unknown error {exc}")
    finally:
        connection.close()
        logging.info("Connection closed for pilot update")

def delete_pilot(DB_FILE, pilot_id):
    # I'm doing actual deletes in the pilot scenario - I'm imagining this would be something like a "pilot leaving the company"
    # situation so the professional/ethical considerations are such that I should not "soft delete" such a record
    # instead hard deleting

    utils.log_active_function()
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        delete_pilot = '''
                      DELETE FROM Pilot 
                      WHERE pilot_id = ?
                  '''
        values = (pilot_id,)

        logging.debug(f"{delete_pilot}")
        cursor.execute(delete_pilot, values)
        connection.commit()
        logging.info(f"pilot deleted {pilot_id}")
        return True
    except sqlite3.DatabaseError as dbe:
        logger.error(f"Database error {dbe}")
    except Exception as exc:
        logger.error(f"Unknown error {exc}")
    finally:
        connection.close()

# Airport logic
# An airport cannot exist without a city - to create an airport, it must be assigned to a city immediately
# An airport must also have a valid airport code
# input validation is done in bambi.py so when these functions are called we don't need to repeatthe "check" steps

def add_airport(DB_FILE, airport_name, airport_code, city_id):
    utils.log_active_function()
    logging.info("INCOMPLETE LOGIC")
    logging.info(f"Attempting to add new airport {airport_name} with code {airport_code} to city {city_id}")
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    try:
        logging.info("Commencing dual insert into airport, cityairport")
        insert_new_airport = '''
                INSERT INTO Airport (airport_name, airport_code)
                VALUES (?, ?)
            '''
        # normally I'd use values here but had some trouble so broke it out explicitly
        cursor.execute(insert_new_airport, (airport_name, airport_code))

        # Wasn't sure how to get the last auto-inceremented ID from the airport table to pass into the cityairport mapping
        # googled, found this and tried it
        # https://stackoverflow.com/questions/41368687/lastrowid-returning-none-in-sqlite3-in-python-3

        airport_id = cursor.lastrowid
        logging.info(f"New airportID is {airport_id}")
        insert_new_cityairport = '''
                INSERT INTO CityAirport (city_id, airport_id)
                VALUES (?, ?)
        '''
        logging.info(f"Final values for cityairport mapping are city - {city_id} - airport {airport_id}")
        cursor.execute(insert_new_cityairport,(city_id, airport_id))

        connection.commit()

        logging.info(f"New airport inserted {airport_name}")
        #return True
    except sqlite3.DatabaseError as dbe:
        logger.error(f"Database error {dbe}")
    except Exception as exc:
        logger.error(f"Unknown error {exc}")
    finally:
        connection.close()

    # validation of code and city are done outside this step, we can just insert now

def update_airport(DB_FILE, airport_id, new_airport_name, new_airport_code):
    utils.log_active_function()
    logging.info("INCOMPLETE LOGIC")

def delete_airport(DB_FILE, airport_id):
    utils.log_active_function()
    logging.info("INCOMPLETE LOGIC")


def add_city(DB_FILE, city_name):
    utils.log_active_function()
    logging.info(f"Attempting to add new city  {city_name}")

    # checks to avoid duplicate cities are done before this stage so we can simply insert
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        insert_new_city = '''
                INSERT INTO City (city_name)
                VALUES (?)
            '''
        values = (city_name,)

        logging.debug(f"{insert_new_city}")
        cursor.execute(insert_new_city, values)
        connection.commit()
        logging.info(f"New city inserted {city_name}")
        os.system('cls')
        print(f"\nNew city {city_name} created successfully")
        time.sleep(1)
        return True
    except sqlite3.DatabaseError as dbe:
        logger.error(f"Database error {dbe}")
    except Exception as exc:
        logger.error(f"Unknown error {exc}")
    finally:
        connection.close()
    utils.log_active_function()
    logging.info("INCOMPLETE LOGIC")

def update_city(DB_FILE, existing_city_id, new_city_name):
    utils.log_active_function()
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        update_city = '''
                UPDATE City
                SET city_name = ?
                WHERE city_id = ?;
            '''
        values = (new_city_name, existing_city_id)

        logging.debug(f"{update_city}")
        cursor.execute(update_city, values)
        connection.commit()
        logging.info(f"City {existing_city_id} updated, new name {new_city_name}")
        return True
    except sqlite3.DatabaseError as dbe:
        logger.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logger.error(f"Unknown error {exc}")
        return False
    finally:
        connection.close()
        logging.info("Connection closed for city update")

def delete_city(DB_FILE, city_id):
    utils.log_active_function()
    logging.info("INCOMPLETE LOGIC")


