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
        f.flight_id as assigned_pilot_flight_id
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
def get_schedules(DB_FILE):
    utils.log_active_function()
    logging.info("Getting schedules")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        get_schedules = '''
        SELECT 
        schedule_id,
        departure_time
        
        FROM 
        Schedule
        
        ORDER BY schedule_id
        '''


        logging.debug(get_schedules)
        cursor.execute(get_schedules)

        returned_schedule_rows = cursor.fetchall()
        logging.debug(returned_schedule_rows)

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after getting all schedules")
        connection.close()
    return returned_schedule_rows

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

def get_aircraft(DB_FILE):
    utils.log_active_function()
    logging.info("Getting available aircraft")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        get_aircraft = '''
            SELECT 
            a.aircraft_id,
            a.aircraft_name,
            am.aircraftmodel_id,
            am.aircraftmodel_name,
            f.flight_id as assigned_aircraft_flight_id,
            am.aircraftmodel_range
            FROM 
            Aircraft a
            LEFT JOIN AircraftModel am on a.aircraftmodel_id = am.aircraftmodel_id
            LEFT JOIN Flight f on a.aircraft_id = f.aircraft_id
            ORDER by
            a.aircraft_id, f.flight_id
            '''

        logging.debug(get_aircraft)
        cursor.execute(get_aircraft)

        returned_aircraft = cursor.fetchall()
        logging.debug(returned_aircraft)

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after getting all aircraft")
        connection.close()
    return returned_aircraft

def get_aircraftmodels(DB_FILE):
    utils.log_active_function()
    logging.info("Getting available aircraft")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        get_aircraftmodels = '''
               SELECT 
               am.aircraftmodel_id,
               am.aircraftmodel_name,
               am.aircraftmodel_range,
               am.aircraftmodel_speed
               
               FROM 
               AircraftModel am
               
               ORDER by
               am.aircraftmodel_id
               '''

        logging.debug(get_aircraftmodels)
        cursor.execute(get_aircraftmodels)

        returned_aircraftmodels = cursor.fetchall()
        logging.debug(returned_aircraftmodels)

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after getting all aircraft models")
        connection.close()
    return returned_aircraftmodels

def get_flights(DB_FILE):
    utils.log_active_function()
    logging.info("Getting all flights")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        get_flights = '''
                       SELECT 
                       f.flight_id,
                       f.flight_number,
                       a.aircraft_name,
                       am.aircraftmodel_name,
                       p.pilot_name AS captain,
                       ao.airport_code AS origin_airport,
                       ad.airport_code AS destination_airport,
                       s.departure_time,
                       f.arrival_time

                       FROM 
                       Flight f
                       
                       INNER JOIN Aircraft a on f.aircraft_id = a.aircraft_id
                       INNER JOIN AircraftModel am on a.aircraftmodel_id = am.aircraftmodel_id
                       INNER JOIN Pilot p on f.pilot_id = p.pilot_id
                       INNER JOIN Route r on f.route_id = r.route_id
                       INNER JOIN Schedule s on f.schedule_id = s.schedule_id
                       
                       INNER JOIN CityAirport cao on r.origin_cityairport_id = cao.cityairport_id
                       INNER JOIN Airport ao on cao.airport_id = ao.airport_id

                       INNER JOIN CityAirport cad on r.destination_cityairport_id = cad.cityairport_id
                       INNER JOIN Airport ad on cad.airport_id = ad.airport_id
                                            
                       ORDER by
                       f.flight_id
                       '''
        # I didn't know that cao/ao and cad/ad was "acceptable" practice when setting up table aliases (aliasii?)
        # A colleague at work suggested it's fine to do so if it makes the code more readable, so I used the practice
        # it makes it much clearer for me when i'm doing multiple joins on the same tables!

        # most of the query is straightforward but the origin/destination is as follows
        # Flight has a Route and a Route has an origin + destination airport
        # So we need Flight > Route > CityAirport > Airport
        # repeated for origin/destination

        # flight time is calculated as the route distance/aircraftmodel speed


        logging.debug(get_flights)
        cursor.execute(get_flights)

        returned_flights = cursor.fetchall()
        logging.debug(returned_flights)

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after getting all flights")
        connection.close()
    return returned_flights

def check_valid_flight(DB_FILE, flight_id):
    utils.log_active_function()
    logging.info("Getting list of valid flight IDs")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_flight_ids = '''
               SELECT 
               f.flight_id        
           FROM 
               Flight f
           
           '''

        cursor.execute(get_flight_ids)

        returned_flight_ids = cursor.fetchall()
        logging.debug(f"Returned flight id list  {returned_flight_ids}")


        valid_flight_ids = [returned_flight_id[0] for returned_flight_id in returned_flight_ids]
        logging.debug(f"ID returned = {valid_flight_ids}")
        logging.debug(f"flightID = {flight_id}")
        if flight_id in valid_flight_ids:
            logging.info(f"Flight id {flight_id} found in list of valid flights")
            return True
        else:
            logging.info(f"Flight id {flight_id} NOT found in list of valid flights")
            return False
        logging.debug(returned_flight_ids)

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking flight ids")
        connection.close()

def check_valid_pilot_id(DB_FILE, pilot_id):
    utils.log_active_function()
    logging.info("Getting list of valid pilot IDs")
    pilot_id = int(pilot_id)
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

def check_valid_airport(DB_FILE, airport_id):
    utils.log_active_function()
    logging.info(f"Checking if {airport_id} is a valid airportID")

    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_airport_ids = '''
                           SELECT airport_id
                           FROM Airport 
                           '''

        logging.debug(get_airport_ids)
        cursor.execute(get_airport_ids)

        existing_airport_ids = cursor.fetchall()  # list of tuples here, needs converting
        logging.debug(f"returned airport id tuples: {existing_airport_ids}")
        existing_airport_ids_list = [airport[0] for airport in existing_airport_ids]
        logging.debug(f"list of airport ids: {existing_airport_ids_list}")

        if airport_id in existing_airport_ids_list:
            logging.info(f"Matched airport ID {airport_id} to existing airport")
            return True
        else:
            logging.info(f"airport {airport_id} not found ")
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

def check_city_has_airport(DB_FILE, city_id):
    utils.log_active_function()
    logging.info(f"Checking if {city_id} has a mapped airport")

    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_city_ids = '''
                           SELECT city_id
                           FROM CityAirport 
                           '''

        logging.debug(get_city_ids)
        cursor.execute(get_city_ids)

        existing_city_ids = cursor.fetchall()  # list of tuples here, needs converting
        logging.debug(f"returned city id tuples: {existing_city_ids}")
        existing_city_ids_list = [city[0] for city in existing_city_ids]
        logging.debug(f"list of city ids: {existing_city_ids_list}")

        if city_id in existing_city_ids_list:
            logging.info(f"Matched city ID {city_id} to existing cityairport mapping")
            return True
        else:
            logging.info(f"city {city_id} not found in cityairport ")
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

def check_valid_aircraft(DB_FILE, aircraft_id):
    utils.log_active_function()
    logging.info(f"Checking if {aircraft_id} is a valid aircraft")
    aircraft_id = int(aircraft_id)
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_aircraft_ids = '''
                               SELECT aircraft_id
                               FROM Aircraft
                               '''

        logging.debug(get_aircraft_ids)
        cursor.execute(get_aircraft_ids)

        existing_aircraft_ids = cursor.fetchall()  # list of tuples here, needs converting
        logging.debug(f"returned aircraft id tuples: {existing_aircraft_ids}")
        existing_aircraft_ids_list = [aircraft[0] for aircraft in existing_aircraft_ids]
        logging.debug(f"list of aircraft ids: {existing_aircraft_ids_list}")

        if aircraft_id in existing_aircraft_ids_list:
            logging.info(f"Matched aircraft ID {aircraft_id} to existing aircraft")
            return True
        else:
            logging.info(f"aircraft {aircraft_id} not found ")
            return False

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking aircraft ID")
        connection.close()

def check_valid_route(DB_FILE, route_id):
    utils.log_active_function()
    logging.info(f"Checking if {route_id} is valid")

    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_route_id = '''
                                   SELECT route_id
                                   FROM Route
                                   '''

        logging.debug(get_route_id)
        cursor.execute(get_route_id)

        existing_route_ids = cursor.fetchall()  # list of tuples here, needs converting
        logging.debug(f"returned id tuples: {existing_route_ids}")
        existing_route_ids_list = [aircraft[0] for aircraft in existing_route_ids]
        logging.debug(f"list of ids: {existing_route_ids_list}")

        if route_id in existing_route_ids_list:
            logging.info(f"Matched ID {route_id} to existing entry")
            return True
        else:
            logging.info(f"Entry for route {route_id} not found ")
            return False

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking route ID")
        connection.close()
def check_valid_schedule(DB_FILE, schedule_id):
    utils.log_active_function()
    logging.info(f"Checking if {schedule_id} is valid")

    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_schedule_id = '''
                                      SELECT schedule_id
                                      FROM Schedule
                                      '''

        logging.debug(get_schedule_id)
        cursor.execute(get_schedule_id)

        existing_schedule_ids = cursor.fetchall()  # list of tuples here, needs converting
        logging.debug(f"returned id tuples: {existing_schedule_ids}")
        existing_schedule_ids_list = [aircraft[0] for aircraft in existing_schedule_ids]
        logging.debug(f"list of ids: {existing_schedule_ids_list}")

        if schedule_id in existing_schedule_ids_list:
            logging.info(f"Matched ID {schedule_id} to existing entry")
            return True
        else:
            logging.info(f"Entry for scedheule {schedule_id} not found ")
            return False

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking schedule ID")
        connection.close()

def check_valid_aircraftmodel(DB_FILE, aircraftmodel_id):
    utils.log_active_function()
    logging.info(f"Checking if {aircraftmodel_id} is a valid aircraftmodel")

    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_aircraftmodel_ids = '''
                                   SELECT aircraftmodel_id
                                   FROM AircraftModel
                                   '''

        logging.debug(get_aircraftmodel_ids)
        cursor.execute(get_aircraftmodel_ids)

        existing_aircraftmodel_ids = cursor.fetchall()  # list of tuples here, needs converting
        logging.debug(f"returned aircraftmodel id tuples: {existing_aircraftmodel_ids}")
        existing_aircraftmodel_ids_list = [aircraftmodel[0] for aircraftmodel in existing_aircraftmodel_ids]
        logging.debug(f"list of aircraftmodel ids: {existing_aircraftmodel_ids_list}")

        if aircraftmodel_id in existing_aircraftmodel_ids_list:
            logging.info(f"Matched aircraftmodel ID {aircraftmodel_id} to existing aircraftmodel")
            return True
        else:
            logging.info(f"aircraftmodel {aircraftmodel_id} not found ")
            return False

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking aircraftmodel ID")
        connection.close()

def check_aircraftmodel_in_use(DB_FILE, aircraftmodel_id):
    utils.log_active_function()
    logging.info(f"Checking if {aircraftmodel_id} is assigned to a live aircraft")

    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_aircraftmodel_ids_in_aircraft = '''
                                       SELECT aircraftmodel_id
                                       FROM Aircraft
                                       '''

        logging.debug(get_aircraftmodel_ids_in_aircraft)
        cursor.execute(get_aircraftmodel_ids_in_aircraft)

        existing_aircraftmodel_ids_in_aircraft = cursor.fetchall()  # list of tuples here, needs converting
        logging.debug(f"returned aircraftmodel id tuples: {existing_aircraftmodel_ids_in_aircraft}")
        existing_aircraftmodel_ids_in_aircraft_list = [aircraftmodel[0] for aircraftmodel in existing_aircraftmodel_ids_in_aircraft]
        logging.debug(f"list of aircraftmodel ids: {existing_aircraftmodel_ids_in_aircraft_list}")

        if aircraftmodel_id in existing_aircraftmodel_ids_in_aircraft_list:
            logging.info(f"Matched aircraftmodel ID {aircraftmodel_id} to existing aircraftmodel in aircraft table")
            return True
        else:
            logging.info(f"aircraftmodel {aircraftmodel_id} not found in aircraft table")
            return False

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking aircraftmodel ID")
        connection.close()

def check_airport_in_route(DB_FILE, airport_id,):
    # thius is more complex than usual as we need to check if the airport is in cityairport and where it is,
    # is that cityairport_id in route
    # it feels kind of clunky

    utils.log_active_function()
    logging.info(f"Checking if {airport_id} is assigned to a route")

    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        #get the cityairport_ids should they exist
        get_cityairport_ids = '''
               SELECT cityairport_id
               FROM CityAirport
               WHERE airport_id = ?
               '''

        cityairport_values = (airport_id, )

        logging.debug(f"Executing query: {get_cityairport_ids} with params: {cityairport_values}")
        cursor.execute(get_cityairport_ids, cityairport_values)
        # so far so normal.  now we want to use a list of cityairport_ids that match our query
        # should they exist
        # iterating over the ca ids
        cityairport_ids = [ca_id[0] for ca_id in cursor.fetchall()]
        logging.debug(f"found these cityairport_ids {cityairport_ids}")

        # stop immediately if airport not in cityairport
        if not cityairport_ids:
            logging.info(f"No cityairport IDs found for airport_id {airport_id}.")
            return False

        # now to check if our new cityairport_ids are in any route
        for cityairport_id in cityairport_ids:
            get_airport_in_route = '''
                SELECT route_id
                FROM Route
                WHERE origin_cityairport_id = ? 
               OR destination_cityairport_id = ?
            '''
            logging.debug(f"query {get_airport_in_route}")
            # it feels like there must be a more efficient or at least elegant way of doing this
            cursor.execute(get_airport_in_route, (cityairport_id, cityairport_id))

            if cursor.fetchall():  # If any rows at all are returned, yay
                logging.info(f"Airport ID {airport_id} is assigned to a route (either as origin or destination).")
                return True
            else:
                logging.info(f"Airport ID {airport_id} is not assigned to any route.")
                return False

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after the ugly check for airports in a route")
        connection.close()

def check_attribute_in_flight(DB_FILE, attribute, attribute_value):
    # I wrote the logic to check if something was assigned to a flight at the end
    # in hindsight I could have created more generalised get/add/update/delete functions like this
    # this means when I do the check for whether something is assigned to a flight (usually deletions or updates)
    # I can pass in what I want to check and the value I'm looking for dynamically instead of having millions of
    # "check_if_attribute_A in flight", "check_if_attribute_b_in_flight" and so on
    utils.log_active_function()
    logging.info(f"Checking if {attribute} with value {attribute_value} is assigned to a flight")

    # converting to an int to make sure it can find the IDs I'm looking for
    # this seems a bit hacky and would need more defenseive coding that I don't have time for
    attribute_value = int(attribute_value)
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_flight_content = f'''
                                     SELECT {attribute}
                                     FROM Flight
                                     WHERE {attribute} = ?
                                     '''
        values = (attribute_value,)
        logging.debug(f"{get_flight_content} with values {values}")
        cursor.execute(get_flight_content, values)

        flight_contents = cursor.fetchall()  # list of tuples here, needs converting
        logging.debug(f"returned tuples: {flight_contents} for {attribute}")
        flight_content_list = [flight_content[0] for flight_content in flight_contents]
        logging.debug(f"list of ids: {flight_content_list}")

        if attribute_value in flight_content_list:
            logging.info(f"Matched attribute {attribute} with value {attribute_value} to existing flight ")
            return True
        else:
            logging.info(f"Attribute {attribute} with value {attribute_value} not found assigned to flight")
            return False

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking flight contents")
        connection.close()

def get_aircraftmodeldata_for_aircraftmodel(DB_FILE, aircraftmodel_id):
    utils.log_active_function()
    logging.info(f"Fetching aircraftmodel data for aircraftmodel_id {aircraftmodel_id}")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_aircraftmodel_data = '''
                                       SELECT aircraftmodel_range, aircraftmodel_speed , aircraftmodel_name
                                       FROM AircraftModel
                                       WHERE aircraftmodel_id = ?
                                       '''

        values = (aircraftmodel_id, )
        logging.debug(get_aircraftmodel_data)
        cursor.execute(get_aircraftmodel_data, values)

        aircraftmodel_data = cursor.fetchall()

        if aircraftmodel_data:
            logging.info(f"Fetched data for aircraftmodel {aircraftmodel_id}")
            return aircraftmodel_data
        else:
            logging.info(f"Error getting data for aircraftmodel {aircraftmodel_id}")
            return None

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking aircraftmodel data")
        connection.close()

def get_aircraftmodelid_for_aircraft(DB_FILE, aircraft_id):
    utils.log_active_function()
    logging.info(f"Checking aircraftmodel id for aircraftID {aircraft_id}")

    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_aircraftmodelid = '''
                                       SELECT aircraftmodel_id 
                                       FROM Aircraft
                                       WHERE aircraft_id = ?
                                       '''
        values = (aircraft_id, )
        logging.debug(get_aircraftmodelid)
        cursor.execute(get_aircraftmodelid, values)

        fetched_aircraftmodel_id = cursor.fetchone()
        # convert to an int for use later on
        if fetched_aircraftmodel_id:
            fetched_aircraftmodel_id = int(fetched_aircraftmodel_id[0])

        logging.debug(f"returned aircraftmodel id : {fetched_aircraftmodel_id}")

        if fetched_aircraftmodel_id:
            logging.info(f"Matched aircraftmodel ID {fetched_aircraftmodel_id} to existing aircraft")
            return fetched_aircraftmodel_id
        else:
            logging.info(f"aircraftmodel for {aircraft_id} not found ")
            return False

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking aircraftmodel ID")
        connection.close()

def get_departuretime_for_schedule(DB_FILE, schedule_id):
    utils.log_active_function()
    logging.info(f"Fetching schedule for  {schedule_id}")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_departure_time = '''
                                          SELECT departure_time 
                                          FROM Schedule
                                          WHERE schedule_id = ?
                                          '''
        values = (schedule_id,)
        logging.debug(get_departure_time)
        cursor.execute(get_departure_time, values)

        scheduled_departure_time = cursor.fetchone()  # we'll only get one id here so fetchone rather than fetchall

        if scheduled_departure_time:
            logging.info(f"departure time for schedule {schedule_id} FOUND ok")
            return scheduled_departure_time
        else:
            logging.info(f"departure time for schedule {schedule_id} not found ")
            return None

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking schedule")
        connection.close()

def get_distance_for_route(DB_FILE, route_id):
    utils.log_active_function()
    logging.info(f"Fetching distance for  {route_id}")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_distance = '''
                                          SELECT route_distance 
                                          FROM Route
                                          WHERE route_id = ?
                                          '''
        values = (route_id,)
        logging.debug(get_distance)
        cursor.execute(get_distance, values)

        flight_distance = cursor.fetchone()
        if flight_distance:
            flight_distance = int(flight_distance[0])
            logging.info(f"Route distance {flight_distance} for route {route_id} FOUND ok")
            return flight_distance

        else:
            logging.info(f"Route distance for route {route_id} NOT FOUND")
            return None

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking schedule")
        connection.close()

def get_airportcodes_on_route(DB_FILE, route_id):
    utils.log_active_function()
    logging.info(f"Fetching route data for route_id {route_id}")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_airportcodes_on_route = '''
           SELECT 
           ao.airport_code AS origin_airport,
           ad.airport_code AS destination_airport,
           r.route_distance
           FROM Route r 
                                  
           INNER JOIN CityAirport cao on r.origin_cityairport_id = cao.cityairport_id
           INNER JOIN Airport ao on cao.airport_id = ao.airport_id

           INNER JOIN CityAirport cad on r.destination_cityairport_id = cad.cityairport_id
           INNER JOIN Airport ad on cad.airport_id = ad.airport_id
           
           WHERE r.route_id = ?
           '''

        values = (route_id,)
        logging.debug(get_airportcodes_on_route)
        cursor.execute(get_airportcodes_on_route, values)

        route_code_data = cursor.fetchone()

        if route_code_data:
            logging.info(f"Fetched data for route_code_data {route_code_data}")
            return route_code_data
        else:
            logging.info(f"Error getting data for route_code_data {route_code_data}")
            return None

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking route data")
        connection.close()

def get_pilot_name(DB_FILE, pilot_id):
    utils.log_active_function()
    logging.info(f"Fetching pilot name for id {pilot_id}")
    pilot_id = int(pilot_id)
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_pilot_name = '''
           SELECT 
           pilot_name
           FROM Pilot
           WHERE pilot_id = ?
           '''

        values = (pilot_id,)
        logging.debug(get_pilot_name)
        cursor.execute(get_pilot_name, values)

        pilot_name = cursor.fetchone()

        if pilot_name:
            logging.info(f"Fetched name {pilot_name} for id {pilot_id}")
            return pilot_name
        else:
            logging.info(f"Error getting name for {pilot_id}")
            return None

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking name")
        connection.close()

def get_aircraft_name(DB_FILE, aircraft_id):
    utils.log_active_function()
    logging.info(f"Fetching aircraft name for id {aircraft_id}")
    aircraft_id = int(aircraft_id)
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_aircraft_name = '''
           SELECT 
           aircraft_name
           FROM Aircraft
           WHERE aircraft_id = ?
           '''

        values = (aircraft_id,)
        logging.debug(get_aircraft_name)
        cursor.execute(get_aircraft_name, values)

        aircraft_name = cursor.fetchone()

        if aircraft_name:
            logging.info(f"Fetched name {aircraft_name} for id {aircraft_id}")
            return aircraft_name
        else:
            logging.info(f"Error getting name for {aircraft_id}")
            return None

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking name")
        connection.close()

def check_existing_route(DB_FILE, origin_airport_id, dest_airport_id):
    utils.log_active_function()
    logging.info(f"origin_airport_id {origin_airport_id}, dest_airport_id {dest_airport_id}")

    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        check_route_exists = '''
                SELECT r.route_id
                FROM Route r
                JOIN CityAirport cao ON r.origin_cityairport_id = cao.cityairport_id
                JOIN CityAirport cad ON r.destination_cityairport_id = cad.cityairport_id
                WHERE cao.airport_id = ? AND cad.airport_id = ?
               '''

        values = (origin_airport_id, dest_airport_id)
        logging.debug(check_route_exists)
        cursor.execute(check_route_exists, values)

        route_check = cursor.fetchone()

        if route_check:
            logging.info(f"Route exists")
            return True
        else:
            logging.info(f"Route does not exist")
            return False

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking route")
        connection.close()

def get_cityairport_for_airport(DB_FILE, airport_id):
    utils.log_active_function()
    logging.info(f"Fetching data for  {airport_id}")
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        get_cityairport_id_for_airport = '''
              SELECT 
              ca.cityairport_id
              
              FROM CityAirport ca 

              WHERE ca.airport_id = ?
              '''

        values = (airport_id,)
        logging.debug(get_cityairport_id_for_airport)
        cursor.execute(get_cityairport_id_for_airport, values)

        cityairport_id = cursor.fetchone()

        if cityairport_id:
            logging.info(f"Fetched cityairport_id - {cityairport_id}")
            return cityairport_id
        else:
            logging.info(f"Error getting data for ID airport_id {airport_id}")
            return None

    except sqlite3.DatabaseError as dbe:
        logging.error(f"Database error {dbe}")
        return False
    except Exception as exc:
        logging.error(f"Unknown error {exc}")
        return False
    finally:
        logging.info("Connection closed after checking airport_id")
        connection.close()