# todo revisit all "add" statements and add character caps

import time
import sqlite3 # needed for, well, the entire assignment
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

# User will be presented with an option to chose CLI mode or
# If they have flask installed, a flask-based web app mode is another option
# Same functionality for both, slightly richer interaction with the web-app

# I wanted to provide a pre-populated database but also
# demonstrate the code used to create it in the first instance and so it can be setup from scratch if the user requires
# therefore both the cli and webapp route both check for an existing bambi.db and if one is not found, create using sample data
# this setup is done in db_initialisation

# setup loggign
# recently refactored a number of scripts on a work project to use proper logging instead of print statements
# it may be overkill here but I want to do it properly and want to keep up with good practice!
LOGFILE_NAME = 'bambi.log'
DB_FILE = "bambi.db"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename=LOGFILE_NAME, filemode='w')
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
        print("Flask installation detected, allowing user to run in CLI mode or Web mode")
        print("Choose an option:")
        print("1. Run in CLI mode")
        print("2. Run in Web mode")

        user_choice = input("Select mode (1 or 2)\n")
        if user_choice == "1":
            logger.info("User selected CLI mode")
            cli_mode_init()
        elif user_choice == "2":
            logger.info("User selected web mode")
            web_mode()
        else:
            print("Invalid choice, please start again")
    else:
        print("Flask not installed, running at command line only.")
        print("Install Flask to enable web app option")
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
    input("    Press Enter To Continue")
    # ASCII Art generated here - https://patorjk.com/software/taag/ - and 1 second timer
    # is used to provide a visually clear delineation between initialisation tasks and activation of CLI mode
    cli_mainmenu()

def cli_mainmenu():
    utils.log_active_function()
    while True: # added this to handle invalid user inputs
        os.system('cls')
        print("Enter a letter to view or manage data\n")

        print("(R)outes - includes City & Airport Management")
        print("(S)chedules")
        print("(P)ilots")
        print("(A)ircraft")
        print("(F)light Management\n\n")
        print("(Q) to quit")
        user_input = input().lower()
        logger.info(f"User selected input {user_input}")
        if user_input == "r":
            cli_view_routes()
        elif user_input == "s":
            view_schedules()
        elif user_input == "p":
            cli_view_pilots()
        elif user_input == "a":
            view_aircraft()
        elif user_input == "f":
            view_flights()
        elif user_input == "q":
            logging.info("User quit application")
            print("Thank you for using BAMBI!")
            sys.exit()
        else:
            print("Invalid option, please select a valid menu option or (Q) to quit")

def cli_view_routes():
    utils.log_active_function()
    os.system('cls')
    route_rows = db_get.get_routes(DB_FILE)
    print("\nAll current routes are shown below\n")

    route_headers = ["Route ID", "Origin City", "Origin Airport", "Origin Code", "Dest. City", "Dest. Airport", "Dest. Code", "Distance (km)"]
    print(f"{route_headers[0]:<8}   {route_headers[1]:<11}   {route_headers[2]:<14}   {route_headers[3]:<11}   {route_headers[4]:<10}   {route_headers[5]:<14}   {route_headers[6]:<10}   {route_headers[7]:<5}")
    print("-" * 110)

    for route_row in route_rows:
        print(f"{route_row[0]:<8}   {route_row[1]:<11}   {route_row[2]:<14}   {route_row[3]:<11}   {route_row[4]:<10}   {route_row[5]:<14}   {route_row[6]:<10}   {route_row[7]:<5}")

    print("\nChoose from the options below or press (B) to go back to the main menu\n")
    print("(C) to manage cities & airports")
    print("(A) to add a new route       (M) to modify a route")
    print("(X) to delete a route\n")
    print("*WARNING* - you CANNOT modify/delete any city/airport/route that is part of an active flight")

    user_input = input().lower()
    if user_input == "c":
        cli_view_cityairport()

def cli_view_cityairport():
    # This function is responsible for rendering the cities & airports served and allowing users to add/edit/remove cities/airports
    utils.log_active_function()

    os.system('cls')
    cityairport_rows = db_get.get_cities_airports(DB_FILE) # calls the select query to view city/airport/cityairport mapping
    logging.debug(f"cityairport_rows = {cityairport_rows}")
    print("All served cities, their airport(s) and routing codes are shown below\n")
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
        # todo tidy this up if time permits
        print(f"{cityairport_row[0]:<8}   {cityairport_row[1]:<25}   {airport_id:<10}   {airport:<36}   {code:<3}")

    print("\nChoose from the options below or press (B) to go back to the main menu\n")
    print("(A) to add a new airport (requires city)         (E) to modify an existing airport     (D) to delete an airport")
    print("(C) to add a new city                            (M) to modify an existing city        (X) to delete an city")
    print("(B) to return to main menu")
    print("\n WARNING - Cannot delete a city/airport assigned to an active flight")

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
        db_set.update_airport()
    elif user_input == "d":
        db_set.delete_airport()
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

    elif user_input == "m":
        existing_city_id = input("Select ID for the city you wish to rename\n")
        logging.info(f"City to modify = {existing_city_id}")
        try:
            existing_city_id = int(existing_city_id)
            logging.info(f"Checking {existing_city_id} is an integer")
            # city names can be duplicated so down to the user to not enter nonsense
            new_city_name = input(f"Enter new name for city {existing_city_id} - limit 25 characters\n")[:25]
            if db_set.update_city(DB_FILE, existing_city_id, new_city_name):
                os.system('cls')
                print("City renamed successfully")
                time.sleep(1)
                cli_view_cityairport()
            else:
                print("Operation failed, please check the log")

        except ValueError:
            logging.info("User did not enter integer city_id")
            print("Invalid entry, please choose an existing city ID")



    elif user_input == "x":
        db_set.delete_city()
    elif user_input == "b":
        cli_mainmenu()
    else:
        print("Invalid choice")
        cli_view_cityairport()

def cli_view_schedules():
    utils.log_active_function()

def cli_view_pilots():
    utils.log_active_function()
    # This function allows users to view pilot data and leads to add/update/removal

    os.system('cls')
    while True:
        pilot_rows = db_get.get_pilots(DB_FILE)  # calls the select query for pilots

        print("All registered pilots are shown below\n")
        pilot_headers = ["Pilot ID", "Pilot Name", "Assigned Flight ID"]
        print(f"{pilot_headers[0]:<8}   {pilot_headers[1]:<25}   {pilot_headers[2]:<12}")
        print("-" * 60)

        for pilot_row in pilot_rows:
            assigned_flight_id = pilot_row[2] if pilot_row[2] is not None else 'Not Assigned'
            print(
                f"{pilot_row[0]:<8}   {pilot_row[1]:<25}   {assigned_flight_id:<12}")

        print("\nChoose from the options below or press (B) to go back to the main menu\n")
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

            if db_get.check_pilot_assigned_flight(DB_FILE, int(user_delete_pilot_id)):
                logging.info(f"Pilot id {user_delete_pilot_id} already assigned to flight - cannot delete")
                os.system('cls')
                print("\n WARNING ")
                print(f"Pilot {user_delete_pilot_id} is assigned to a flight - cannot delete an assigned pilot")
                time.sleep(2)
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

# deprecated this in favour of cityairport - todo delete this
# def cli_view_cities():
#     utils.log_active_function()
#     os.system('cls')
#
#     while True:
#         city_rows = db_get.get_cities(DB_FILE)
#
#         print("All currently served cities are shown below\n")
#         city_headers = ["City ID", "City Name"]
#         print(f"{city_headers[0]:<3}   {city_headers[1]:<25} ")
#         print("-" * 40)
#
#         for city_row in city_rows:
#             print(
#                 f"{city_row[0]:<3}   {city_row[1]:<25}")
#
#         print("\nChoose from the options below or press (B) to go back to the main menu\n")
#         print("(A) to add a new city\n(E) to edit an existing city name\n(D) to delete a city")
#         print("Cities with assigned airports or allocated to routes cannot be deleted")
#
#
#
#         user_input = input().lower()
#         # add new pilot
#         if user_input == "a":
#             print("A city cannot be added to a route unless it also has at least one airport")
#             print("Please assign an airport after creating a new city")
#         elif user_input == "e":
#             print("To de-link an airport from a city, please modify the airport itself")
#         elif user_input == "d":
#             print("Cities cannot be deleted if they are assigned to a route or have airport(s)")
#         elif user_input == "b":
#             cli_mainmenu()
#         else:
#             print("Please choose a valid option")

def cli_view_airports():
    utils.log_active_function()
def cli_view_aircraft():
    utils.log_active_function()
def cli_view_flights():
    utils.log_active_function()


if __name__ == "__main__":
    db_initialisation.init(DB_FILE)
    start_journey()