import sqlite3
import json # needed to read seeding data
import os
import logging
import utils

logger = logging.getLogger(__name__)
logger.info("Started logging in db_initialisation.py")

# Initially this was core to bambi.py I refactored and placed in its' own script when bambi.py became too large

def init(DB_FILE):
    # setup the connection and establish if existing db file exists or not

    DB_CHECK = os.path.exists(DB_FILE)
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    SEED_DATA_FILE = "seed_data.json"

    if not DB_CHECK:
        print("No existing database found - creating from baseline data")
        logger.info("No DB found, creating database and populating from seed json files")

        # in my role all database tables start with a capital so I'm extending that here
        # table contents are lower case by our convention
        # As personal preference I always like to have the id column for a table contain the table name, e.g. aircraft.aircraft_id rather than aircraft.id
        # as I have worked with many schemas where too much shorthand made sql query building harder!

        create_aircraft = '''
            CREATE TABLE IF NOT EXISTS Aircraft (
                aircraft_id INTEGER PRIMARY KEY,
                aircraft_name TEXT,
                aircraftmodel_id INTEGER,
                FOREIGN KEY (aircraftmodel_id) REFERENCES AircraftModel(aircraftmodel_id) 
            ) 
        '''
        logger.info("Creating Aircraft table")
        logger.debug(f"{create_aircraft}")
        cursor.execute(create_aircraft)

        create_aircraftmodel = '''
            CREATE TABLE IF NOT EXISTS AircraftModel (
                aircraftmodel_id INTEGER PRIMARY KEY,
                aircraftmodel_name TEXT,
                aircraftmodel_range INTEGER,
                aircraftmodel_speed INTEGER
            )
        '''
        logger.info("Creating AircraftModel table")
        logger.debug(f"{create_aircraftmodel}")
        cursor.execute(create_aircraftmodel)

        create_pilot = '''
            CREATE TABLE IF NOT EXISTS Pilot (
                pilot_id INTEGER PRIMARY KEY,
                pilot_name TEXT
            )
        '''
        logger.info("Creating Pilot table")
        logger.debug(f"{create_pilot}")
        cursor.execute(create_pilot)

        create_schedule = '''
            CREATE TABLE IF NOT EXISTS Schedule (
                schedule_id INTEGER PRIMARY KEY,
                departure_time TEXT
            )
        '''
        logger.info("Creating Schedule table")
        logger.debug(f"{create_schedule}")
        cursor.execute(create_schedule)

    # I learned that SQLLite does not seem to have native functions for handling "Monday 09:00" as a schedule would be
    # rather I would need to store as/parse strings which was added complexity
    # so for this example instead I simply use a departure_time - all my flights run 7 days a week!

        create_city = '''
            CREATE TABLE IF NOT EXISTS City (
                city_id INTEGER PRIMARY KEY,
                city_name TEXT                
            )
        '''
        logger.info("Creating City table")
        logger.debug(f"{create_city}")
        cursor.execute(create_city)

        create_airport = '''
            CREATE TABLE IF NOT EXISTS Airport (
            airport_id INTEGER PRIMARY KEY,
            airport_name TEXT,
            airport_code TEXT
            )
        '''
        logger.info("Create Airport table")
        logger.debug(f"{create_airport}")
        cursor.execute(create_airport)

        create_cityairport = '''
            CREATE TABLE IF NOT EXISTS CityAirport (
            cityairport_id INTEGER PRIMARY KEY,
            airport_id INTEGER,
            city_id INTEGER,
            FOREIGN KEY (airport_id) REFERENCES Airport(airport_id),
            FOREIGN KEY (city_id) REFERENCES City(city_id)
            )
        '''
        logger.info("Create CityAirport table")
        logger.debug(f"{create_cityairport}")
        cursor.execute(create_cityairport)

        create_route = '''
            CREATE TABLE IF NOT EXISTS Route (
                route_id INTEGER PRIMARY KEY,
                origin_cityairport_id INTEGER,
                destination_cityairport_id INTEGER,
                route_distance INTEGER,
                FOREIGN KEY (origin_cityairport_id) REFERENCES CityAirport(cityairport_id),
                FOREIGN KEY (destination_cityairport_id) REFERENCES CityAirport(cityairport_id)
            )
        '''
        logger.info("Create Route table")
        logger.debug(f"{create_route}")
        cursor.execute(create_route)

        create_flight = '''
            CREATE TABLE IF NOT EXISTS Flight (
                flight_id INTEGER PRIMARY KEY,
                flight_number TEXT,
                aircraft_id INTEGER,
                pilot_id INTEGER,
                route_id INTEGER,
                schedule_id INTEGER,
                arrival_time TEXT,
                FOREIGN KEY (aircraft_id) REFERENCES Aircraft(aircraft_id),
                FOREIGN KEY (pilot_id) REFERENCES Pilot(pilot_id),
                FOREIGN KEY (route_id) REFERENCES Route(route_id),
                FOREIGN KEY (schedule_id) REFERENCES Schedule(schedule_id)
            )
        '''
        logger.info("Creating Flight table")
        logger.debug(f"{create_flight}")
        cursor.execute(create_flight)

        print("Database tables created successfully, starting data seeding")
        # saving the departure and arrival times as text is a workaround as strictly
        # speaking I need a "TIME" field that sqllite doesn't have

        #flight_time and arrival_time depend on the aircraft flying the route and are calculated when a flight is defined or first loaded
        #Flight.flight_time is calculated as route.distance/aircraftmodel.speed (for a given aircraft_id)

        # flight_time_trigger = '''
        #     CREATE TRIGGER IF NOT EXISTS calc_flight_time
        #     AFTER INSERT ON Flight
        #     BEGIN
        #         UPDATE Flight
        #         SET flight_time = (
        #               SELECT CAST(CEIL(CAST(Route.distance AS REAL) / Aircraftmodel.aircraftmodel_speed) AS INTEGER)
        # '''

        try:
            with open(SEED_DATA_FILE,"r") as file:
                seed_data = json.load(file)

            logger.info("Successfully loaded seed data file")
            print("Found data seed file - loading data...")
        except FileNotFoundError:
            logger.error("Seed data FILE NOT FOUND!")
            seed_data = {}
        except json.JSONDecodeError as jde:
            logger.error(f"Unknown json error: {jde}")
            seed_data = {}
        except Exception as ex:
            logger.exception(f"Unknown error loading seed data file: {ex}")
            seed_data = {}


        # Database tables should be created
        # JSON file should be found
        # Time to create some sample data

        #cities
        try:
            for city in seed_data.get("cities", []):
                insert_city = '''
                    INSERT INTO City (city_id, city_name)
                    VALUES (?, ?)
                '''
                values = (city['city_id'], city['city_name'])

                logger.info("Inserting city data")
                logger.debug(f"Executing SQL: {insert_city.strip()} | Values: {values}")
                cursor.execute(insert_city, values)

            for airport in seed_data.get("airports", []):
                insert_airport = '''
                    INSERT INTO Airport (airport_id, airport_name, airport_code)
                    VALUES (?, ?, ?)
                '''
                values = (airport['airport_id'], airport['airport_name'], airport['airport_code'])

                logger.info("Inserting airport data")
                logger.debug(f"Executing SQL: {insert_airport.strip()} | Values: {values}")
                cursor.execute(insert_airport, values)

            for cityairport in seed_data.get("cityairports", []):
                insert_cityairport = '''
                           INSERT INTO CityAirport (cityairport_id, city_id, airport_id)
                           VALUES (?, ?, ?)
                       '''
                values = (cityairport['cityairport_id'], cityairport['city_id'], cityairport['airport_id'])

                logger.info("Inserting cityairport data")
                logger.debug(f"Executing SQL: {insert_cityairport.strip()} | Values: {values}")
                cursor.execute(insert_cityairport, values)

            for aircraft in seed_data.get("aircraft", []):
                insert_aircraft = '''
                                     INSERT INTO Aircraft (aircraft_id, aircraft_name, aircraftmodel_id)
                                     VALUES (?, ?, ?)
                                 '''
                values = (aircraft['aircraft_id'], aircraft['aircraft_name'], aircraft['aircraftmodel_id'])

                logger.info("Inserting aircraft data")
                logger.debug(f"Executing SQL: {insert_aircraft.strip()} | Values: {values}")
                cursor.execute(insert_aircraft, values)

            for aircraftmodel in seed_data.get("aircraftmodels", []):
                insert_aircraftmodels = '''
                                             INSERT INTO AircraftModel (aircraftmodel_id, aircraftmodel_name, aircraftmodel_range, aircraftmodel_speed)
                                             VALUES (?, ?, ?, ?)
                                         '''
                values = (aircraftmodel['aircraftmodel_id'], aircraftmodel['aircraftmodel_name'],
                          aircraftmodel['aircraftmodel_range'], aircraftmodel['aircraftmodel_speed'])

                logger.info("Inserting aircraftmodel data")
                logger.debug(f"Executing SQL: {insert_aircraftmodels.strip()} | Values: {values}")
                cursor.execute(insert_aircraftmodels, values)

            for pilot in seed_data.get("pilots", []):
                insert_pilot = '''
                                           INSERT INTO Pilot (pilot_id, pilot_name)
                                           VALUES (?, ?)
                                       '''
                values = (pilot['pilot_id'], pilot['pilot_name'])

                logger.info("Inserting pilot data")
                logger.debug(f"Executing SQL: {insert_pilot.strip()} | Values: {values}")
                cursor.execute(insert_pilot, values)

            for schedule in seed_data.get("schedules", []):
                insert_schedule = '''
                                         INSERT INTO Schedule (schedule_id, departure_time)
                                         VALUES (?, ?)
                                     '''
                values = (schedule['schedule_id'], schedule['departure_time'])

                logger.info("Inserting schedule data")
                logger.debug(f"Executing SQL: {insert_schedule.strip()} | Values: {values}")
                cursor.execute(insert_schedule, values)

            for route in seed_data.get("routes", []):
                insert_route = '''
                                         INSERT INTO Route (route_id, origin_cityairport_id, destination_cityairport_id, route_distance)
                                         VALUES (?, ?, ?, ?)
                                     '''
                values = (route['route_id'], route['origin_cityairport_id'], route['destination_cityairport_id'], route['route_distance'])

                logger.info("Inserting route data")
                logger.debug(f"Executing SQL: {insert_route.strip()} | Values: {values}")
                cursor.execute(insert_route, values)

            for flight in seed_data.get("flights", []):
                insert_flight = '''
                                                INSERT INTO Flight (flight_id, flight_number, pilot_id, route_id, aircraft_id, schedule_id, arrival_time)
                                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                            '''
                values = (flight['flight_id'], flight['flight_number'], flight['pilot_id'], flight['route_id'], flight['aircraft_id'], flight['schedule_id'], flight['arrival_time'])

                logger.info("Inserting flight data")
                logger.debug(f"Executing SQL: {insert_flight.strip()} | Values: {values}")
                cursor.execute(insert_flight, values)

            connection.commit()
            connection.close()
            print("Database seeded successfully")


        except Exception as ex:
            print(f"Error loading data, please check log: {LOGFILE_NAME}")
            logger.exception(f"Error inserting data: {ex}")
            connection.rollback()
            os.remove(DB_FILE)
            print("Deleted db file for fresh start")
            logger.info(f"Deleted {DB_FILE} on terminal exception")


        logger.debug("closed DB connection")

    else:
        print("Existing DB found, skipping creation step")
        logger.info("Existing DB found, skipping creation step")