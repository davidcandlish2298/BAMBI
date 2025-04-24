import time
import math # needed for flight time calculation
from datetime import datetime, timedelta # also needed for flight time calculation
import os # needed to interact with os files
import logging # essential for proper logging
import sys
import db_get # all database operations for getting data
import db_set # all database operations for any data modifications
import utils
import db_initialisation

# BAMBI
# Bath Airline Management & Booking Interface
# Technically it's not "booking" anything yet but I wanted a good acronym!

# Original plan was to present user with an option to chose CLI mode or
# If they had flask installed, a flask-based web app mode as another option but I ran out of time for the flask option so everything redirects to CLI

# I wanted to provide a pre-populated database but also
# demonstrate the code used to create it in the first instance and so it can be setup from scratch if the user requires
# therefore both the cli and webapp route both check for an existing bambi.db and if one is not found, create using sample data
# this setup is done in db_initialisation

# setup loggign
# recently refactored a number of scripts on a work project to use proper logging instead of print statements
# it may be overkill here but I want to do it properly and want to keep up with good practice!
LOGFILE_NAME = 'bambi.log'
DB_FILE = "bambi.db"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=LOGFILE_NAME, filemode='w')
logger = logging.getLogger(__name__)
logger.info("Started logging")
LOG_LEVEL = logging.getLogger().getEffectiveLevel()
if LOG_LEVEL == 10:
    LOG_LEVEL = "DEBUG"
elif LOG_LEVEL == 20:
    LOG_LEVEL = "INFO"
else:
    LOG_LEVEL = "Unknown log level detected"
# included this check above - someone accidentally entered DEBUG instead of info and filled a disk with verbose logs
# so this else statement is good practice for handling that edge case and printing the plain english log level on the first line

logger.info(f"Starting BAMBI - Log level: {LOG_LEVEL}")
logger.info(f"Database file used - {DB_FILE}")

# start_journey is the basic entrypoint to the application once we have setup/checked the DB
# this script covers the core CLI interface approach requested - I will tackle the web based approach in a separate script
def start_journey():
    if(utils.check_flask()):
        print("Flask installation detected, but web mode disabled")

        print("Choose an option:")
        print("1. Run in CLI mode")
        #print("2. Run in Web mode")

        user_choice = input("Select mode (1 or 2)\n")
        if user_choice == "1":
            logger.info("User selected CLI mode")
            cli_mode_init()
        #elif user_choice == "2":
        #    logger.info("User selected web mode")
        #    web_mode()
        else:
            print("Invalid choice, please start again")
    else:
        print("Flask not installed, running at command line only.")
        #print("Install Flask to enable web app option")
        print("Starting CLI mode instead\n\n")
        cli_mode_init()

def cli_mode_init():
    os.system('cls')
    logger.info("Started CLI mode")
    print(r"""
    Welcome to -
    .______        ___      .___  ___. .______    __
    |   _  \      /   \     |   \/   | |   _  \  |  |
    |  |_)  |    /  ^  \    |  \  /  | |  |_)  | |  |
    |   _  <    /  /_\  \   |  |\/|  | |   _  <  |  |
    |  |_)  |  /  _____  \  |  |  |  | |  |_)  | |  |
    |______/  /__/     \__\ |__|  |__| |______/  |__|

    Bath Airline Management & Booking Interface
    """)
    if LOG_LEVEL == "DEBUG":
        print("** Debug mode detected **")
        print("To reset the system with seed data please delete the bambi.db file\n")

    input("\n    Press Enter To Continue")
    # ASCII Art generated here - https://patorjk.com/software/taag/ - and 1 second timer
    # is used to provide a visually clear delineation between initialisation tasks and activation of CLI mode
    cli_mainmenu()

def cli_mainmenu():
    utils.log_active_function()
    while True: # added this to handle invalid user inputs
        os.system('cls')
        print("Enter a letter to view or manage data\n\n")

        print("(F)light Management\n")
        print("(C)ity, Route & Airport Management")
        print("(S)chedule Viewer")
        print("(P)ilot Management")
        print("(A)ircraft Management\n\n")

        print("(Q) to quit")
        user_input = input().lower()
        logger.info(f"User selected input {user_input}")
        if user_input == "c":
            cli_view_cityairport()
        elif user_input == "s":
            cli_view_schedules()
        elif user_input == "p":
            cli_view_pilots()
        elif user_input == "a":
            cli_view_aircraft()
        elif user_input == "f":
            cli_view_flights()
        elif user_input == "q":
            logging.info("User quit application")
            print("Thank you for using BAMBI!")
            sys.exit()
        else:
            print("Invalid option, please select a valid menu option or (Q) to quit")

# def cli_view_routes():
#     utils.log_active_function()
#     os.system('cls')
#     route_rows = db_get.get_routes(DB_FILE)
#     print("\nAll current routes are shown below\n")
#
#     route_headers = ["Route ID", "Origin City", "Origin Airport", "Origin Code", "Dest. City", "Dest. Airport", "Dest. Code", "Distance (km)"]
#     print(f"{route_headers[0]:<8}   {route_headers[1]:<11}   {route_headers[2]:<14}   {route_headers[3]:<11}   {route_headers[4]:<10}   {route_headers[5]:<14}   {route_headers[6]:<10}   {route_headers[7]:<5}")
#     print("-" * 110)
#
#     for route_row in route_rows:
#         print(f"{route_row[0]:<8}   {route_row[1]:<11}   {route_row[2]:<14}   {route_row[3]:<11}   {route_row[4]:<10}   {route_row[5]:<14}   {route_row[6]:<10}   {route_row[7]:<5}")
#
#     print("\n Read Only Route View\n")
#     print("Choose from the options below or press (B) to return to the main menu\n")
#     print("(C) to manage Routes, Cities & Airports\n")
#
#     print("*WARNING* - you CANNOT modify/delete any route that is part of an active flight")
#
#     user_input = input().lower()
#     if user_input == "c":
#         cli_view_cityairport()

# Initially all menu screens were rendered and setup via the cli_* functions
# However when it came to adding flights it was difficult for users to remember the IDs they needed
# So I split the function into cli_* for the operations
# and render* for drawing the table, allowing me to "refresh user memories" whenever needed
def cli_view_cityairport():
    # This function is responsible for rendering the cities & airports served and allowing users to add/edit/remove cities/airports
    utils.log_active_function()
    os.system('cls')
    print("All served cities, their airport(s) and routing codes are shown below\n")
    render_cityairport()
    print("\nAll current routes are shown below\n")
    render_routes()

    print("\nChoose from the options below, (F) to access Flight Management or press (B) to return to the main menu\n")
    print("Airport Management")
    print("(A) to add a new airport (requires city)         (E) to modify an existing airport     (D) to delete an airport")
    print("(R) to change airport-city mapping\n")
    print("City Management")
    print("(C) to add a new city                            (M) to modify an existing city        (X) to delete an city\n")
    print("Route Management")
    print("(T) to add a new route                            (L) to delete a route\n")

    print("\nWARNING - Cannot delete a city/airport assigned to an active route or flight")

    user_input = input().lower()
    if user_input == "a":
        new_airport = input("Enter name for new airport\n")
        logging.info(f"New airport name = {new_airport}")

        new_airport_existing_city_id = input("Enter ID of existing city\n")
        logging.info(f"User has chosen city {new_airport_existing_city_id} for {new_airport}")
        if db_get.check_valid_city(DB_FILE, int(new_airport_existing_city_id)):
            logging.info("Valid city check TRUE")
            new_airport_code = input("Enter code for new airport or CANCEL to restart\n")
            logging.info(f"User has chosen code {new_airport_code}")
            if db_get.check_airport_code(DB_FILE, new_airport_code):
                logging.info(f"Airport code check OK for {new_airport_code}")
                print("Airport code is valid")
                db_set.add_airport(DB_FILE, new_airport,new_airport_code, int(new_airport_existing_city_id))
                os.system('cls')
                print("Airport added successfully successfully")
                time.sleep(1)
                cli_view_cityairport()
            elif new_airport_code == "CANCEL":
                cli_mainmenu()
            else:
                print(f"Airport code {new_airport_code} invalid, please enter a valid, unique airport code")
        else:
            os.system('cls')
            print("\nWARNING\n")
            print("Invalid city chosen - please choose an existing city")
            time.sleep(1)
            cli_view_cityairport()

    elif user_input == "e":
        logging.info("User modifying an existing airport")
        print("This allows you to modify airport names & code only")
        airport_id = input("Please choose the airport ID you wish to modify\n")

        try:
            airport_id = int(airport_id)
            logging.info(f"Checking {airport_id} is an integer")

            if db_get.check_valid_airport(DB_FILE,airport_id):
                # city names can be duplicated so down to the user to not enter nonsense, but we do limit the lengths
                new_airport_name = input(f"Enter new name for airport {airport_id} - limit 25 characters\n")[:25]
                new_airport_code = input(f"Enter new code for airport {airport_id} - limit 3 characters\n")[:3]
                if db_set.update_airport(DB_FILE, airport_id, new_airport_name,new_airport_code):
                    os.system('cls')
                    print("Airport name & code updated successfully")
                    time.sleep(1)
                    cli_view_cityairport()
                else:
                    print("Operation failed, please check the log")
            else:
                logging.info("User did not enter integer airport_id")
                os.system('cls')
                print("Invalid entry, please choose an existing airport ID")
                time.sleep(1)
                cli_view_cityairport()

        except ValueError:
            logging.info("User did not enter integer airport_id")
            print("Invalid entry, please choose an existing airport ID")

    elif user_input == "d":
        # this process will delete both the cityairport mapping and airport
        airport_id_to_delete = input("Select ID for the airport you wish to delete\n")
        logging.info(f"Airport to delete = {airport_id_to_delete}")
        try:
            airport_id_to_delete = int(airport_id_to_delete)
            logging.info(f"Checking {airport_id_to_delete} is an integer")

            # now check the ID actually exists
            if db_get.check_valid_airport(DB_FILE, airport_id_to_delete):
                # now we know it exists, check if the associated airport is in a route
                # we check this here and not on city deletion because to delete a city it must not
                # have an airport
                if not db_get.check_airport_in_route(DB_FILE, airport_id_to_delete):
                    logging.info("Airport exists and not in route, deleting")
                    db_set.delete_airport(DB_FILE,airport_id_to_delete)
                    os.system('cls')
                    print("Airport deleted successfully")
                    time.sleep(1)
                    cli_view_cityairport()
                else:
                    logging.info("Airport exists in a route, NOT deleted")
                    os.system('cls')
                    print("Airport exists as part of a route, cannot delete")
                    time.sleep(1.5)
                    cli_view_cityairport()
            else:
                logging.info("User did not enter valid integer airport_id")
                os.system('cls')
                print("Invalid entry, please choose an existing airport ID")
                time.sleep(1)
                cli_view_cityairport()

        except ValueError:
            logging.info("User did not enter integer airport_id")
            print("Invalid entry, please choose an existing airport ID")

    elif user_input == "c":
        # will check if new city name matches existing city name
        new_city = input("Enter name for new city\n")
        logging.info(f"New city name = {new_city}")
        logging.info(f"Checking if {new_city} name already exists")
        if db_get.check_valid_city(DB_FILE, new_city):
            os.system('cls')
            print("\n WARNING\n")
            print(f"City - {new_city} - already exists, please review available cities and try again")
            logging.info(f"City creation failed - {new_city} - user tried to create pre-existing city")
            cli_view_cityairport()
        else:
            logging.info(f"Creating new city with name - {new_city}")
            db_set.add_city(DB_FILE, new_city)
            os.system('cls')
            print(f"\nNew city {new_city} created successfully")
            time.sleep(1)
            cli_view_cityairport()

    elif user_input == "m":
        existing_city_id = input("Select ID for the city you wish to rename\n")
        logging.info(f"City to modify = {existing_city_id}")
        try:
            existing_city_id = int(existing_city_id)
            logging.info(f"Checking {existing_city_id} is an integer")


            if db_get.check_valid_city(DB_FILE,existing_city_id):
                # city names can be duplicated so down to the user to not enter nonsense
                new_city_name = input(f"Enter new name for city {existing_city_id} - limit 25 characters\n")[:25]
                if db_set.update_city(DB_FILE, existing_city_id, new_city_name):
                    os.system('cls')
                    print("City renamed successfully")
                    time.sleep(1)
                    cli_view_cityairport()
                else:
                    print("Operation failed, please check the log")
            else:
                logging.info("User did not enter integer city_id")
                os.system('cls')
                print("Invalid entry, please choose an existing city ID")
                time.sleep(1)
                cli_view_cityairport()

        except ValueError:
            logging.info("User did not enter integer city_id")
            print("Invalid entry, please choose an existing city ID")

    elif user_input == "x":
        # given time I'd probably have made this a "soft" delete since cities are the kind of thing you'd potentially want to re-enable in the future
        # and there's no GDPR risk keeping a city soft deleted via an "IsActive" flag in the DB (or similar)
        city_id_to_delete = input("Select ID for the city you wish to delete\n")
        logging.info(f"City to delete = {city_id_to_delete}")
        try:
            city_id_to_delete = int(city_id_to_delete)
            logging.info(f"Checking {city_id_to_delete} is an integer")

            # now check the ID actually exists
            if db_get.check_valid_city(DB_FILE, city_id_to_delete):
                logging.info("City exists, checking for assigned airport")
                # if it exists, check we aren't mapped to an airport
                if not db_get.check_city_has_airport(DB_FILE, city_id_to_delete):
                    logging.info("Trying city deletion")
                    # we don't check if the city is in a route before deletion because we can't
                    # delete a city UNLESS it has no airports (and by definition no cityairport entry)
                    # so we do the route check on AIRPORT deletion.

                    db_set.delete_city(DB_FILE, city_id_to_delete)
                    os.system('cls')
                    print("City deleted successfully")
                    time.sleep(2)
                    cli_view_cityairport()

                else:
                    logging.info("User tried to delete city mapped to an airport")
                    os.system('cls')
                    print("Please delete ALL airports mapped to a city before deleting a city.")
                    time.sleep(1)
                    cli_view_cityairport()
            else:
                logging.info("User did not enter valid integer city_id")
                os.system('cls')
                print("Invalid entry, please choose an existing city ID")
                time.sleep(1)
                cli_view_cityairport()

        except ValueError:
            logging.info("User did not enter integer city_id")
            print("Invalid entry, please choose an existing city ID")

    elif user_input == "r":
        logging.info("User modifying an existing airport mapping")
        print("This allows you to change the city an airport is mapped to")
        airport_remap_id = input("Please choose the airport ID you wish to modify\n")
        city_remap_id = input("Please choose the new city to map the airport to\n")

        try:
            airport_remap_id = int(airport_remap_id)
            logging.info(f"Checking {airport_remap_id} is an integer")
            city_remap_id = int(city_remap_id)
            logging.info(f"Checking {city_remap_id} is an integer")

            if db_get.check_valid_airport(DB_FILE,airport_remap_id):
                logging.info("Valid airport ID selected")
                if db_get.check_valid_city(DB_FILE, city_remap_id):
                    logging.info("Valid city ID selected")
                    if db_set.remap_airport(DB_FILE, airport_remap_id, city_remap_id):
                        os.system('cls')
                        print("Airport-City mapping updated successfully")
                        time.sleep(1)
                        cli_view_cityairport()
                    else:
                        os.system('cls')
                        print("Operation failed, please check the log")
                        time.sleep(1)
                        cli_view_cityairport()
                else:
                    logging.info("User did not enter valid city_id")
                    os.system('cls')
                    print("Invalid entry, please choose an existing city ID")
                    time.sleep(1)
                    cli_view_cityairport()
            else:
                logging.info("User did not enter integer airport_id")
                os.system('cls')
                print("Invalid entry, please choose an existing airport ID")
                time.sleep(1)
                cli_view_cityairport()


        except ValueError:
            logging.info("User did not enter integer airport_id")
            print("Invalid entry, please choose an existing airport ID")

    elif user_input == "t":
        # origin
        origin_airport = input("Enter ID for route origin airport\n")
        origin_airport = int(origin_airport)

        if not db_get.check_valid_airport(DB_FILE, origin_airport):
            os.system('cls')
            print("Airport does not exist, please try again")
            time.sleep(1)
            cli_view_cityairport()
            return

        logging.info(f"New origin airport ID = {origin_airport}")

        # destination
        destination_airport = input("Enter ID for route destination airport\n")
        destination_airport = int(destination_airport)
        if not db_get.check_valid_airport(DB_FILE, destination_airport):
            os.system('cls')
            print("Airport does not exist, please try again")
            time.sleep(1)
            cli_view_cityairport()
            return
        logging.info(f"New destination airport ID = {destination_airport}")

        # check if this route already exists
        if db_get.check_existing_route(DB_FILE, origin_airport, destination_airport):
            os.system('cls')
            print("The proposed route already exists - not creating duplicate")
            time.sleep(1)
            cli_view_cityairport()
            return

        # Get the distance and add the route
        route_distance = input("Please enter the route distance in km\n")
        route_distance = int(route_distance)
        if not route_distance > 0:
            print("Please only enter positive values")
            cli_view_cityairport()
            return

        # now we try to add the route
        origin_cityairport_id = db_get.get_cityairport_for_airport(DB_FILE, origin_airport)[0]
        destination_cityairport_id = db_get.get_cityairport_for_airport(DB_FILE, destination_airport)[0]
        if db_set.add_route(DB_FILE, origin_cityairport_id, destination_cityairport_id, route_distance):
            os.system('cls')
            print("New route added successfully")
            time.sleep(2)
            cli_view_cityairport()
        else:
            print("Error adding route, please check log file")
    elif user_input == "f":
        cli_view_flights()

    elif user_input == "l":

        route_to_delete = input("Select ID for the route you wish to delete\n")

        try:
            route_to_delete = int(route_to_delete)
            logging.info(f"route to delete = {route_to_delete}")
            logging.info(f"Checked {route_to_delete} is an integer")

            # now check the ID actually exists
            if db_get.check_valid_route(DB_FILE, route_to_delete):
                logging.info("Route exists")
                if not db_get.check_attribute_in_flight(DB_FILE, "route_id", int(route_to_delete)):
                    os.system('cls')
                    db_set.delete_route(DB_FILE, route_to_delete)
                    print("Route deleted!")
                    time.sleep(1)
                    cli_view_cityairport()

                else:
                    os.system('cls')
                    print("Selected route is mapped to a flight - cannot delete")
                    time.sleep(1)
                    cli_view_cityairport()

            else:
                os.system('cls')
                print("Selected route does not exist")
                time.sleep(1)
                cli_view_cityairport()



        except ValueError:
            logging.info("User did not enter integer route_to_delete")
            print("Invalid entry, please choose an existing route_to_delete ID")

    elif user_input == "b":
        cli_mainmenu()
    else:
        print("Invalid choice")
        cli_view_cityairport()
def render_cityairport():
    cityairport_rows = db_get.get_cities_airports(DB_FILE)  # calls the select query to view city/airport/cityairport mapping
    logging.debug(f"cityairport_rows = {cityairport_rows}")

    cityairport_headers = ["City ID", "City Name", "Airport ID", "Airport Name", "Airport Code"]
    logging.debug("Rendering headers")
    print(f"{cityairport_headers[0]:<8}   {cityairport_headers[1]:<25}   {cityairport_headers[2]:<10}   {cityairport_headers[3]:<36}   {cityairport_headers[4]:<3}")
    print("-" * 100)
    # had to add lots more logging, here I made the decision to add the city id and airport id later in development
    # and it was a nightmare handling all the nulls coming through when city does not have a mapped airport
    for cityairport_row in cityairport_rows:
        # city = cityairport_row[1]
        # logging.debug(f"city is: {city}")
        airport_id = cityairport_row[2] if cityairport_row[2] is not None else "N/A"
        logging.debug(f"cityairport_row[2] is: {airport_id}")
        airport = cityairport_row[3] if cityairport_row[3] is not None else "--UNASSIGNED--"
        logging.debug(f"airport is {airport}")
        code = cityairport_row[4] if cityairport_row[4] is not None else "XXX"
        # assignments above are visual only, unaffecting the DB
        # this was tricky to sort out all the rendering logic with unassigned

        print(f"{cityairport_row[0]:<8}   {cityairport_row[1]:<25}   {airport_id:<10}   {airport:<36}   {code:<3}")
def render_routes():
    route_rows = db_get.get_routes(DB_FILE)


    route_headers = ["Route ID", "Origin City", "Origin Airport", "Origin Code", "Dest. City", "Dest. Airport",
                     "Dest. Code", "Distance (km)"]
    print(
        f"{route_headers[0]:<8}   {route_headers[1]:<11}   {route_headers[2]:<14}   {route_headers[3]:<11}   {route_headers[4]:<10}   {route_headers[5]:<15}   {route_headers[6]:<10}   {route_headers[7]:<5}")
    print("-" * 110)

    for route_row in route_rows:
        print(
            f"{route_row[0]:<8}   {route_row[1]:<11}   {route_row[2]:<14}   {route_row[3]:<11}   {route_row[4]:<10}   {route_row[5]:<15}   {route_row[6]:<10}   {route_row[7]:<5}")

def cli_view_schedules():
    utils.log_active_function()
    os.system('cls')
    print("All active schedules can be seen below")
    print("These departure times are mandated by Air Traffic Control and cannot be changed\n")
    print("This data is READ ONLY\n")

    while True:
        render_schedules()
        user_input = input("\nPress (B) to return to the main menu\n")

        if user_input == "b":
            cli_mainmenu()
    # I confess I ran out of time to add full add/edit/delete features to schedules so
    # instead assumed that air traffic control only lets us take off on the hour
    # and hence it's a schedule "Viewer"!
def render_schedules():
    utils.log_active_function()
    schedule_rows = db_get.get_schedules(DB_FILE)


    schedule_headers = ["Schedule ID", "Departure Time"]
    print(f"{schedule_headers[0]:<11}   {schedule_headers[1]:<14}")
    print("-" * 25)

    for schedule_row in schedule_rows:
        print(f"{schedule_row[0]:<11}   {schedule_row[1]:<14}")
def cli_view_pilots():
    utils.log_active_function()
    # This function allows users to view pilot data and leads to add/update/removal

    os.system('cls')
    while True:
        print("All registered pilots are shown below\n")
        render_pilots()

        print("\nChoose from the options below or press (B) to return to the main menu\n")
        print("(A) to add a new pilot\n(E) to edit an existing pilot's name\n(D) to delete a pilot (must not be assigned to a flight)\n")

        user_input = input().lower()
        # add new pilot
        if user_input == "a":
            user_new_pilot = input("Enter new pilot name - limit 25 chars\n")[:25]
            # I wasnt sure how to limit the length of an input but found this
            # https://www.digitalocean.com/community/tutorials/how-to-receive-user-input-python
            # April 5th 2025
            # Section 3 - limit input length had [:20]
            # so I applied that directly to the input() command so it doesn't blow out my table widths
            print(f"New pilot name - {user_new_pilot}")
            logger.info(f"Adding pilot {user_new_pilot}")
            if db_set.add_pilot(DB_FILE, user_new_pilot):
                print("New pilot added successfully")
                time.sleep(0.5) # long enough for user to see it
                os.system('cls')

        # edit existing pilot name
        elif user_input == "e":
            user_update_pilot_id = input("Select a pilot ID to modify their name\n")
            logging.info(f"pilot id to be updated is {user_update_pilot_id}")

            if db_get.check_valid_pilot_id(DB_FILE, int(user_update_pilot_id)):
                logging.info("Check valid pilot OK")
                update_pilot_name = input(f"Input new name for pilot ID {user_update_pilot_id}\n")[:25]
                logging.info(f"New pilot name is {update_pilot_name}")
                db_set.update_pilot(DB_FILE,update_pilot_name,user_update_pilot_id)
                logging.info("Exiting successful pilot name change")
            else:
                print("Invalid pilot ID specified")
                logging.info("Invalid pilot ID specified")
                cli_view_pilots()

        # delete existing pilot NOT assigned to a flight
        elif user_input == "d":
            # found a bug where people don't enter interger pilot_id
            while True:
                logging.info("Checking if user has input integer ID")
                user_delete_pilot_id = input("Select a pilot ID to be deleted\n")
                try:
                    user_delete_pilot_id = int(user_delete_pilot_id)
                    logging.info("user input was an integer ID")
                    break
                except ValueError:
                    print("Invalid pilot ID entered")

            if  db_get.check_attribute_in_flight(DB_FILE, "pilot_id", user_delete_pilot_id):
                logging.info(f"Pilot id {user_delete_pilot_id} already assigned to flight - cannot delete")
                os.system('cls')
                print("\n WARNING ")
                print(f"Pilot {user_delete_pilot_id} is assigned to a flight - cannot delete an assigned pilot")
                time.sleep(3)
                cli_view_pilots()

            else:
                logging.info(f"pilot id to be deleted is {user_delete_pilot_id}")
                deletion_check = input(f"Are you sure you want to delete pilot ID {user_delete_pilot_id} - Y or N?\n").lower()
                if deletion_check == 'y':
                    logging.info("User confirmed pilot deletion")
                    db_set.delete_pilot(DB_FILE, int(user_delete_pilot_id))
                    print(f"Pilot deleted with ID {user_delete_pilot_id}")
                    os.system('cls')
                    cli_view_pilots()
                else:
                    logging.info("User cancelled pilot deletion")
                    print("Pilot not deleted")
        elif user_input == "b":
            cli_mainmenu()
        else:
            print("Please choose a valid option")

def render_pilots():
    pilot_rows = db_get.get_pilots(DB_FILE)  # calls the select query for pilots
    pilot_headers = ["Pilot ID", "Pilot Name", "Assigned Flight ID"]
    print(f"{pilot_headers[0]:<8}   {pilot_headers[1]:<25}   {pilot_headers[2]:<12}")
    print("-" * 60)

    for pilot_row in pilot_rows:
        assigned_pilot_flight_id = pilot_row[2] if pilot_row[2] is not None else 'Not Assigned'
        print(
            f"{pilot_row[0]:<8}   {pilot_row[1]:<25}   {assigned_pilot_flight_id:<12}")

def cli_view_aircraft():
    utils.log_active_function()
    os.system('cls')
    while True:
        print("All active aircraft are shown below\n")
        render_aircraft()

        print("\nChoose from the options below or press (B) to return to the main menu\n")
        print("(A) to add a new aircraft\n(R) to rename an existing aircraft\n(D) to delete an aircraft\n(M) to view aircraft models\n")
        print("You cannot delete an aircraft assigned to a flight\n")
        print("Aircraft flight assignments are managed on the (F)lights screen")


        user_input = input().lower()

        if user_input == "a":
            new_aircraft_name = input("Enter new aircraft name - limit 25 chars\n")[:25]
            render_aircraftmodels()
            new_aircraft_model_id = input("\nEnter new aircraft's model ID\n")


            logger.info(f"Adding new aircraft {new_aircraft_name} of model {new_aircraft_model_id}")
            if db_set.add_aircraft(DB_FILE, new_aircraft_name, new_aircraft_model_id):
                logging.info(f"Added new aircraft {new_aircraft_name} of model {new_aircraft_model_id} OK")
                os.system('cls')
                print(f"New aircraft {new_aircraft_name} added successfully successfully")
                time.sleep(1)
                cli_view_aircraft()


        elif user_input == "r":

            while True:
                logging.info("Checking if user has input integer ID")
                user_rename_aircraft_id = input("Select an aircraft ID to rename\n")

                try:
                    user_rename_aircraft_id = int(user_rename_aircraft_id)
                    logging.info("user input was an integer ID")


                    if db_get.check_valid_aircraft(DB_FILE, user_rename_aircraft_id):
                        logging.info(f"Valid aircraft ID - renaming {user_rename_aircraft_id}")
                        new_aircraft_name = input("Please enter an aircraft name - limit 25 chars\n")[:25]
                        db_set.rename_aircraft(DB_FILE, user_rename_aircraft_id, new_aircraft_name)
                        os.system('cls')
                        print("Aircraft renamed successfully")
                        time.sleep(1)
                        cli_view_aircraft()
                        break
                    else:
                        os.system('cls')
                        print("Invalid aircraft ID selected")
                        time.sleep(1)
                        cli_view_aircraft()

                except ValueError:
                    os.system('cls')
                    print("Invalid aircraft ID entered")
                    time.sleep(1)
                    cli_view_aircraft()


        elif user_input == "d":

            while True:
                logging.info("Checking if user has input integer ID")
                user_delete_aircraft_id = input("Select an aircraft ID to be deleted\n")

                try:
                    user_delete_aircraft_id = int(user_delete_aircraft_id)
                    logging.info("user input was an integer ID")

                    if not db_get.check_attribute_in_flight(DB_FILE, "aircraft_id", user_delete_aircraft_id):
                        logging.info("Aircraft NOT assigned to a flight, safe to delete")

                        if db_get.check_valid_aircraft(DB_FILE, user_delete_aircraft_id):
                            logging.info(f"Valid aircraft ID - deleting {user_delete_aircraft_id}")
                            db_set.delete_aircraft(DB_FILE, user_delete_aircraft_id)
                            os.system('cls')
                            print("Aircraft deleted successfully")
                            time.sleep(1)
                            cli_view_aircraft()
                            break
                        else:
                            os.system('cls')
                            print("Invalid aircraft ID selected")
                            time.sleep(1)
                            cli_view_aircraft()
                    else:
                        os.system('cls')
                        print("Aircraft is assigned to a flight - unable to delete")
                        time.sleep(1)
                        cli_view_aircraft()

                except ValueError:
                    os.system('cls')
                    print("Invalid aircraft ID entered")
                    time.sleep(1)
                    cli_view_aircraft()



        elif user_input == "m":
            cli_view_aircraftmodels()
        elif user_input == "f":
            cli_view_flights()
        elif user_input == "b":
            cli_mainmenu()
        else:
            print("Please choose a valid option")
def render_aircraft():
    aircraft_rows = db_get.get_aircraft(DB_FILE)  # calls the select query for pilots
    aircraft_headers = ["Aircraft ID", "Aircraft Name", "Model ID", "Model Name", "Assigned Flight ID", "Range"]
    print(
        f"{aircraft_headers[0]:<11}   {aircraft_headers[1]:<25}   {aircraft_headers[2]:<8}   {aircraft_headers[3]:<12}   {aircraft_headers[5]:<6}   {aircraft_headers[4]:<12}")
    print("-" * 120)

    for aircraft_row in aircraft_rows:
        assigned_aircraft_flight_id = aircraft_row[4] if aircraft_row[4] is not None else 'Not Assigned'
        print(
            f"{aircraft_row[0]:<11}   {aircraft_row[1]:<25}   {aircraft_row[2]:<8}   {aircraft_row[3]:<12}   {aircraft_row[5]:<6}   {assigned_aircraft_flight_id:<12}")
def cli_view_aircraftmodels():
    utils.log_active_function()
    os.system('cls')
    while True:
        print("All active aircraft models are shown below\n")
        render_aircraftmodels()

        print("\nChoose from the options below, press (K) to go back to aircraft or press (B) to return to the main menu\n")
        print("(A) to add a new aircraft model\n(D) to delete an aircraft model\n")
        print("You cannot delete an aircraft model assigned to a flight/active aircraft\n")

        user_input = input().lower()

        if user_input == "a":
            new_aircraftmodel_name = input("Enter new aircraft name - limit 12 chars\n")[:12]
            new_aircraftmodel_range = input("Enter new aircraft model range - limit 5 chars\n")[:5]
            new_aircraftmodel_speed = input("Enter new aircraft model speed - limit 5 chars\n")[:5]

            logger.info(f"Adding new aircraft model {new_aircraftmodel_name} with range {new_aircraftmodel_range} and speed {new_aircraftmodel_speed} ")
            if db_set.add_aircraftmodel(DB_FILE, new_aircraftmodel_name, new_aircraftmodel_range, new_aircraftmodel_speed):
                logging.info(f"Added new aircrafmodel {new_aircraftmodel_name} OK")
                os.system('cls')
                print(f"New aircraftmodel {new_aircraftmodel_name} added successfully successfully")
                time.sleep(1)
                cli_view_aircraftmodels()
            else:
                os.system('cls')
                print("An error has occurred please check the logs")
                cli_mainmenu()

        elif user_input == "d":

            while True:
                logging.info("Checking if user has input integer ID")
                user_delete_aircraftmodel_id = input("Select an aircraftmodel ID to be deleted\n")

                try:
                    user_delete_aircraftmodel_id = int(user_delete_aircraftmodel_id)
                    logging.info("user input was an integer ID")

                    # checks if the selected model is valid
                    if db_get.check_valid_aircraftmodel(DB_FILE, user_delete_aircraftmodel_id):
                    # now check if there are linked aircraft - BLOCK deletion if so, which means we also don't need to
                    # check "is aircraftmodel + aircraft in flight-  if the model is in use, disallow deletion
                        if not db_get.check_aircraftmodel_in_use(DB_FILE, user_delete_aircraftmodel_id):
                            logging.info(f"Valid aircraftmodel ID - deleting {user_delete_aircraftmodel_id}")
                            db_set.delete_aircraftmodel(DB_FILE, user_delete_aircraftmodel_id)
                            os.system('cls')
                            print("Aircraft Model deleted successfully")
                            time.sleep(1)
                            cli_view_aircraftmodels()
                            break
                        else:
                            os.system('cls')
                            print("AircraftModel in use for active aircraft - cannot delete")
                            time.sleep(1)
                            cli_view_aircraftmodels()
                    else:
                        os.system('cls')
                        print("Invalid aircraft ID selected")
                        time.sleep(1)
                        cli_view_aircraft()

                except ValueError:
                    os.system('cls')
                    print("Invalid aircraft ID entered")
                    time.sleep(1)
                    cli_view_aircraft()

        elif user_input == "k":
            cli_view_aircraft()

        elif user_input == "b":
            cli_mainmenu()
        else:
            print("Please choose a valid option")
def render_aircraftmodels():
    aircraftmodel_rows = db_get.get_aircraftmodels(DB_FILE)  # calls the select query for pilots


    aircraftmodel_headers = ["Model ID", "Model Name", "Model Range(km)", "Model Speed(km/h)"]
    print(
        f"{aircraftmodel_headers[0]:<8}   {aircraftmodel_headers[1]:<12}   {aircraftmodel_headers[2]:<15}   {aircraftmodel_headers[3]:<17}")
    print("-" * 70)

    for aircraftmodel_row in aircraftmodel_rows:
        print(
            f"{aircraftmodel_row[0]:<8}   {aircraftmodel_row[1]:<12}   {aircraftmodel_row[2]:<15}   {aircraftmodel_row[3]:<17}")
def render_flights():
    flight_rows = db_get.get_flights(DB_FILE)  # calls the select query for pilots

    # added this after I deleted all flights and it broke the system!
    if not flight_rows:
        os.system('cls')
        print("No flight data found, returning to main menu")
        time.sleep(1)
        cli_mainmenu()

    flight_headers = ["Flight ID", "Flight No.", "Aircraft Name", "Aircraft Model", "Captain", "Orig. Airport",
                      "Dest. Airport", "Dep. Time", "Arr. Time"]
    print(
        f"{flight_headers[0]:<9}   {flight_headers[1]:<10}   {flight_headers[2]:<25}   {flight_headers[3]:<14}   {flight_headers[4]:<25}   {flight_headers[5]:<13}   {flight_headers[6]:<13}   {flight_headers[7]:<9}   {flight_headers[8]:<9}")
    print("-" * 160)

    for flight_row in flight_rows:
        print(
            f"{flight_row[0]:<9}   {flight_row[1] or 'Not Set':<10}   {flight_row[2]:<25}   {flight_row[3]:<14}   {flight_row[4]:<25}   {flight_row[5]:<13}   {flight_row[6]:<13}   {flight_row[7]:<9}   {flight_row[8] or 'Unknown':<9}")
def cli_view_flights():
    utils.log_active_function()
    os.system('cls')
    while True:

        print("All active flights are shown below\n")
        render_flights()

        print("\nChoose from the options below or press (B) to return to the main menu\n")
        print("All arrival/departure times are shown in UTC")
        print("This screen allows you to build a flight from all available aircraft, pilots, routes and schedules\n")
        print("(F) to add a new flight\n(D) to delete a flight\n")



        user_input = input().lower()

        # because it's a command line tool I can't practically show all flights, aircraft, pilots etc. on the same screen so the user needs to know what they are entering
        # the compromise is if they make a mistake I redirect them to the relevant view so they can refresh their memory

        if user_input == "f":
            new_flight_number = input("Enter Flight Number - limit 6 chars\n")[:6]
            # aircraft
            render_aircraft()
            new_flight_aircraft = input("\nEnter Aircraft ID - limit 3 chars\n")[:3]
            # getting this now for later use
            new_flight_aircraftmodel_id = db_get.get_aircraftmodelid_for_aircraft(DB_FILE, new_flight_aircraft)
            new_flight_aircraft_data = db_get.get_aircraftmodeldata_for_aircraftmodel(DB_FILE,
                                                                                      new_flight_aircraftmodel_id)
            print(f"\nAircraft chosen -")
            print(f"Name - {db_get.get_aircraft_name(DB_FILE, new_flight_aircraft)[0]}")
            print(f"Model - {new_flight_aircraft_data[0][2]}, Range - {new_flight_aircraft_data[0][0]}km, Speed - {new_flight_aircraft_data[0][1]}km/h\n")
            # check if the chosen aircraft is already allocated to a flight
            if db_get.check_attribute_in_flight(DB_FILE, "aircraft_id", new_flight_aircraft):
                logging.info("Aircraft already allocated to flight")
                print("Selected aircraft is already allocated to a flight - resetting flight entry")
                time.sleep(3)
                cli_view_flights()
                return

            if not db_get.check_valid_aircraft(DB_FILE, new_flight_aircraft):
                logging.info("Aircraft invalid")
                print("Invalid aircraft chosen, resetting flight entry - showing user available aircraft")
                time.sleep(3)
                cli_view_aircraft()
                return

            # route
            render_routes()
            new_flight_route = input("\nEnter Route ID - limit 3 chars\n")[:3]
            new_flight_route = int(new_flight_route)
            route_distance = db_get.get_distance_for_route(DB_FILE, new_flight_route)
            route_data = db_get.get_airportcodes_on_route(DB_FILE, new_flight_route)
            print(f"Origin Airport - {route_data[0]}, Destination Airport - {route_data[1]}")
            if not db_get.check_valid_route(DB_FILE, new_flight_route):
                    print("Invalid route chosen, resetting flight entry - showing user available routes")
                    time.sleep(3)
                    cli_view_cityairport()
                    return

                # check the range is OK

            aircraft_range = int(new_flight_aircraft_data[0][0])
            logging.debug(f"aircraft range = {aircraft_range}")

            logging.debug(f"route distance = {route_distance}")

            if (aircraft_range >= 1.1*(db_get.get_distance_for_route(DB_FILE, new_flight_route))):
                print(f"Selected aircraft range is {aircraft_range}km")
                print(f"Route distance is {route_distance}km\n")
                print("Aircraft range check OK - please continue adding details\n")
            else:
                print(f"Selected aircraft range is {aircraft_range}km")
                print(f"Route distance is {route_distance}km\n")
                print("Selected aircraft does not have range for this route - range needs to be at least 110% of route distance, please try again")
                time.sleep(2)
                cli_view_flights()
                return

            #pilot
            render_pilots()
            new_flight_pilot = input("\nEnter Pilot ID - limit 3 chars\n")[:3]
            if not db_get.check_valid_pilot_id(DB_FILE, new_flight_pilot):
                print("Invalid pilot chosen, resetting flight entry - showing user available routes")
                time.sleep(2)
                cli_view_pilots()
                return
            print(f"Pilot {db_get.get_pilot_name(DB_FILE, new_flight_pilot)[0]} chosen as captain!\n")

            #schedule
            new_flight_schedule = input("\nEnter Scheduled departure hour from 1 to 24 (01:00 to 00:00)\n")[:3]
            new_flight_schedule = int(new_flight_schedule)
            if not db_get.check_valid_schedule(DB_FILE, new_flight_schedule):
                print("Invalid schedule chosen, resetting flight entry - showing user available schedules")
                time.sleep(2)
                cli_view_schedules()
                return

            flight_departure = db_get.get_departuretime_for_schedule(DB_FILE, new_flight_schedule)[0]
            print(f"Flight departure time set to - {flight_departure}")
            print("Please wait, calculating expected flight arrival time")
            time.sleep(2)  # little artificial sleep to make it look like it's doing hardcore maths
            # calculating arrival time from aircraft details and schedule

            new_flight_aircraft_data = db_get.get_aircraftmodeldata_for_aircraftmodel(DB_FILE,new_flight_aircraftmodel_id)
            flight_route_distance = db_get.get_distance_for_route(DB_FILE, new_flight_route)
            flight_aircraft_speed = int(new_flight_aircraft_data[0][1])

            new_flight_arrival_time = calculate_flight_time(flight_route_distance, flight_aircraft_speed,flight_departure)
            print(f"Flight arrival times calculated to be: {new_flight_arrival_time}")
            time.sleep(3)

            logger.info(f"Adding new flight {new_flight_number}, aircraftID {new_flight_aircraft}, pilotID{new_flight_pilot}, routeID{new_flight_route}, schedule{new_flight_schedule}, new_flight_arrival_time{new_flight_arrival_time}")
            # now to take all this info and do a mega insert
            if db_set.add_flight(DB_FILE,new_flight_number, new_flight_aircraft, new_flight_pilot, new_flight_route, new_flight_schedule, new_flight_arrival_time):
                logging.info(f"Added new flight to database! ")
                os.system('cls')
                print(f"New flight added to database & registered with ATC!")
                time.sleep(1)
                cli_view_flights()
            else:
                os.system('cls')
                print("An error has occurred please check the logs")
                cli_mainmenu()

        elif user_input == "d":

            while True:
                logging.info("Checking if user has input integer ID")
                user_delete_flight_id = input("Select a flight to delete\n")

                try:
                    user_delete_flight_id = int(user_delete_flight_id)
                    logging.info("user input was an integer ID")

                    if db_get.check_valid_flight(DB_FILE, user_delete_flight_id):
                        logging.info(f"Deleting flight ID {user_delete_flight_id}")
                        db_set.delete_flight(DB_FILE, user_delete_flight_id)
                        os.system('cls')
                        print("Flight deleted successfully")
                        time.sleep(1)
                        cli_view_flights()
                        break
                    else:
                        os.system('cls')
                        print("Invalid Flight ID selected")
                        time.sleep(1)
                        cli_view_flights()


                except ValueError:
                    os.system('cls')
                    print("Invalid flight ID entered")
                    time.sleep(1)
                    cli_view_flights()

        elif user_input == "b":
            cli_mainmenu()
        elif user_input == "c":
            cli_view_cityairport()
        else:
            cli_view_flights()
def calculate_flight_time(flight_route_distance, flight_aircraft_speed, flight_departure):
# initially was going to do this as a trigger but it made more sense to break out logic like this into the python code
# my departure times are stored as text in the DB because sqllite doesn't have a pure "time" datatype and I wanted something
# simple so I looked up some suggestions on how to add an integer to text time like 04:00
# seemed to make more sense to convert time datetime in python - do the addition - convert back to text
# https://stackoverflow.com/questions/56101570/add-time-with-integer-number-in-python checked 23rd April 2025

    # this is a very very simple "round it up" approach
    flight_time_hours = math.ceil(flight_route_distance / flight_aircraft_speed)

    #  convert the text dep time to a datetime object
    departure_time_object = datetime.strptime(flight_departure, "%H:%M")

    # now we can use timedelta to make the maths easier
    arrival_time_object = departure_time_object + timedelta(hours=flight_time_hours)

    # does the arrival time loop over into the next day
    day_difference = (arrival_time_object.date() - departure_time_object.date()).days

    # arrival time
    new_flight_arrival_time = arrival_time_object.strftime("%H:%M")

    #final result adding the extra day notification
    if day_difference > 0:
        new_flight_arrival_time += f" +{day_difference}"
    return new_flight_arrival_time

if __name__ == "__main__":
    db_initialisation.init(DB_FILE)
    start_journey()