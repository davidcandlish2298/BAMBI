import utils
import logging
import sqlite3

# Rather than have a single generic "db query" style function where I pass in the sql to be executed, I'm doing the SQL
# operations in individual functions - it'd be more maintenance in real life but this is a small/one-off project so a deliberate design choice

# Initially I had all code in bambi.py but it became far too annoying to traverse to update/add new features
# so I refactored anything "getter" in db_get.py
# this script is primarily concerned with SELECT statements necessary to render the different menus


def get_routes(DB_FILE):
    utils.log_active_function()
    logging.info("Retrieving existing routes")
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    get_route_query = '''
            SELECT 
        route.route_id AS route_id,
        origin_city.city_name AS origin_city,
        origin_airport.airport_name AS origin_airport,
        origin_airport.airport_code AS origin_airport_code,
        destination_city.city_name AS destination_city,
        destination_airport.airport_name AS destination_airport,
        destination_airport.airport_code AS destination_airport_code,
        route.route_distance
            FROM 
        route
            INNER JOIN 
        cityairport AS origin_cityairport ON route.origin_cityairport_id = origin_cityairport.cityairport_id
            INNER JOIN 
        city AS origin_city ON origin_cityairport.city_id = origin_city.city_id
            INNER JOIN 
        airport AS origin_airport ON origin_cityairport.airport_id = origin_airport.airport_id
            INNER JOIN 
        cityairport AS destination_cityairport ON route.destination_cityairport_id = destination_cityairport.cityairport_id
            INNER JOIN 
        city AS destination_city ON destination_cityairport.city_id = destination_city.city_id
            INNER JOIN 
        airport AS destination_airport ON destination_cityairport.airport_id = destination_airport.airport_id;

            '''
    cursor.execute(get_route_query)


    returned_route_rows = cursor.fetchall()
    connection.close()
    logging.info("Connection closed after retrieving routes")
    return returned_route_rows

def get_cities_airports(DB_FILE):
    utils.log_active_function()
    logging.info("Getting city and airport info")
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    get_cityairport = '''
    SELECT 
    c.city_id,
    c.city_name,
    a.airport_id,
    a.airport_name,
    a.airport_code
FROM 
    City c
LEFT JOIN CityAirport ca ON c.city_id = ca.city_id
LEFT JOIN Airport a ON ca.airport_id = a.airport_id
ORDER BY a.airport_code NULLS LAST, c.city_name, a.airport_name;
'''
# this confused me why the XXX airport codes were not appearing at the bottom of the list
# until I realised they are null in the DB
# I found an explanation on how to render them at the bottom of the list here
# https://www.sqlitetutorial.net/sqlite-order-by/
# Accessed 6th April


    cursor.execute(get_cityairport)

    returned_cityairport_rows = cursor.fetchall()
    connection.close()
    logging.info("Connection closed after retrieving cityairport")
    return returned_cityairport_rows

def get_pilots(DB_FILE):
    utils.log_active_function()
    logging.info("Getting pilots")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        get_pilots = '''
        SELECT 
        p.pilot_id,
        p.pilot_name,
        f.flight_id as assigned_flight_id
        FROM 
        Pilot p
        LEFT JOIN Flight f ON p.pilot_id = f.pilot_id
        ORDER BY p.pilot_name, f.flight_id;
        '''
        # Left join used because I want to return all pilots, not just those assigned to a flight

        logging.debug(get_pilots)
        cursor.execute(get_pilots)

        returned_pilot_rows = cursor.fetchall()
        logging.debug(returned_pilot_rows)

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after getting all pilots")
        connection.close()
    return returned_pilot_rows

def get_pilot(DB_FILE, pilot_name):
    utils.log_active_function()
    # incomplete functionality
    # select using like for pilot name

def get_cities(DB_FILE):
    utils.log_active_function()
    logging.info("Getting available cities")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        get_cities = '''
            SELECT 
            c.city_id,
            c.city_name
            FROM 
            City c
            '''

        logging.debug(get_cities)
        cursor.execute(get_cities)

        returned_cities = cursor.fetchall()
        logging.debug(returned_cities)

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after getting all cities")
        connection.close()
    return returned_cities

def check_valid_pilot_id(DB_FILE, pilot_id):
    utils.log_active_function()
    logging.info("Getting list of valid pilot IDs")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_pilot_ids = '''
            SELECT 
            p.pilot_id        
        FROM 
            Pilot p
        WHERE p.pilot_id = ?
        '''
        values = (pilot_id,)

        cursor.execute(get_pilot_ids, values)

        returned_pilot_ids = cursor.fetchall()
        logging.debug(f"Returned pilot id list of tuples: {returned_pilot_ids}")

        # the select query returns a tuple of pilot_ids, I need to gfrab the list of pilot IDs from the query result
        valid_pilot_ids = [returned_pilot_id[0] for returned_pilot_id in returned_pilot_ids]
        logging.debug(f"ID returned = {valid_pilot_ids}")
        logging.debug(f"pilotID = {pilot_id}")
        if pilot_id in valid_pilot_ids :
            logging.info(f"Pilot id {pilot_id} found in list of valid pilots")
            return True
        else:
            logging.info(f"Pilot id {pilot_id} NOT found in list of valid pilots")
            return False
        logging.debug(returned_pilot_ids)

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking pilot id")
        connection.close()

def check_pilot_assigned_flight(DB_FILE, pilot_id):
    utils.log_active_function()
    logging.info(f"Checking if pilot_id {pilot_id} is assigned to a flight...")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        check_pilot_flight = '''
            SELECT flight_id
            FROM Flight f
            WHERE f.pilot_id = ? '''
        values = (pilot_id,)
        logging.debug(check_pilot_flight)
        cursor.execute(check_pilot_flight, values)

        flight_pilot_ids = cursor.fetchall()
        logging.debug(f"list of ids: {flight_pilot_ids}")

        if len(flight_pilot_ids) == 0:
            logging.info("Pilot not assigned to a flight")
            return False
        else:
            logging.info(f"Pilot assigned to flight {flight_pilot_ids[0]}")
            return True

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking pilot flight mapping")
        connection.close()

def check_airport_code(DB_FILE, airport_code):
    utils.log_active_function()
    logging.info(f"Checking if {airport_code} is a valid, unused airport code")

    if len(airport_code) == 3:
        logging.info(f"{airport_code} is 3 chars - valid format")

        try:
            connection = sqlite3.connect(DB_FILE)
            cursor = connection.cursor()
            get_airport_codes = '''
                        SELECT airport_code
                        FROM Airport 
                        '''

            logging.debug(get_airport_codes)
            cursor.execute(get_airport_codes)

            existing_airport_codes = cursor.fetchall() #list of tuples here, needs converting
            logging.debug(f"list of tuples: {existing_airport_codes}")
            existing_airport_codes_list = [code[0] for code in existing_airport_codes]
            logging.debug(f"list of codes: {existing_airport_codes_list}")

            if airport_code in existing_airport_codes_list:
                logging.info(f"Matched airport code {airport_code} to existing airport - new code invalid")
                return False
            else:
                logging.info(f"Airport code {airport_code} not found - eligible for use")
                return True

        except sqlite3.DatabaseError as dbe:
            logging.error(f"Database error {dbe}")
            return False
        except Exception as exc:
            logging.error(f"Unknown error {exc}")
            return False
        finally:
            logging.info("Connection closed after checking airport code")
            connection.close()
    else:
        logging.info(f"{airport_code} not 3 chars long - invalid code")
        return False

def check_valid_city(DB_FILE, city_id):
    utils.log_active_function()
    logging.info(f"Checking if {city_id} is a valid city")

    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_city_ids = '''
                           SELECT city_id
                           FROM City 
                           '''

        logging.debug(get_city_ids)
        cursor.execute(get_city_ids)

        existing_city_ids = cursor.fetchall()  # list of tuples here, needs converting
        logging.debug(f"returned city id tuples: {existing_city_ids}")
        existing_city_ids_list = [city[0] for city in existing_city_ids]
        logging.debug(f"list of city ids: {existing_city_ids_list}")

        if city_id in existing_city_ids_list:
            logging.info(f"Matched city ID {city_id} to existing city")
            return True
        else:
            logging.info(f"city {city_id} not found ")
            return False

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking city ID")
        connection.close()

def check_cityairport_in_flight(DB_FILE, cityairport_id):
    utils.log_active_function()

def check_route_in_flight(DB_FILE, route_id):
    utils.log_active_function()

def check_pilot_in_flight(DB_FILE, pilot_id):
    utils.log_active_function()

def check_aircraft_in_flight(DB_FILE, aircraft_id):
    utils.log_active_function()

def check_schedule_in_flight(DB_FILE, schedule_id):
    utils.log_active_function()