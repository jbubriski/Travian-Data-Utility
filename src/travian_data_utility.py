#!/usr/bin/env python

import os # For working with the file system
import urllib.request # For getting data from web pages
import sqlite3 # for data persistence
import pygame
import pygame.image
import datetime
import gzip

# A dictionary of the server names along with the download URL
# Could be automated for now, but foreign servers have different filenames
server_infos = [
                ("ts1.travian.com", "http://ts1.travian.com/map.sql.gz"),
                ("ts2.travian.com", "http://ts2.travian.com/map.sql.gz"),
                ("ts3.travian.com", "http://ts3.travian.com/map.sql.gz"),
                ("ts4.travian.com", "http://ts4.travian.com/map.sql.gz"),
                ("ts5.travian.com", "http://ts5.travian.com/map.sql.gz"),
                ("ts6.travian.com", "http://ts6.travian.com/map.sql.gz"),
                ("ts7.travian.com", "http://ts7.travian.com/map.sql.gz"),
                ("ts8.travian.com", "http://ts8.travian.com/map.sql.gz")
                ]

today = datetime.date.today()
data_file_name_zipped = "{0}.sql.gz".format(today)
data_file_name = "{0}.sql".format(today)
image_file_name = "{0}.jpg".format(today)
# An extension isn't required but I feel we should have one
database_extension = ".sqlite"
# Size of the grid
size = 800
# Offset so we can draw the map correctly
offset = 400
base_directory = os.getcwd()

def main():
    for server in server_infos:
        # Setup server-specific names and paths
        server_name, url = server
        database_name = server_name + database_extension

        print(server_name)

        full_server_path = os.path.join(base_directory, "data", server_name)

        # Make sure the directory tree exists
        if(not os.path.exists(full_server_path)):
            os.makedirs(full_server_path)

        # Perform all server-specific operations from that directory
        os.chdir(full_server_path)

        print("\tDownloading data file from {0}".format(url))
        download(url, data_file_name_zipped, data_file_name);
        print("\tDone.")

        print("\tCreating table in database " + database_name)
        create_table(database_name)
        print("\tDone.")

        print("\tClearing old data if needed...")
        clear_data(database_name, today)
        print("\tDone.")

        print("\tLoading data file into SQL Lite database " + database_name)
        load_data(database_name, data_file_name, today)
        print("\tDone.")

        print("\tStatistics for {0}:".format(server_name))
        statistics = get_statistics(database_name)
        print("\t\tPopulation of Travian: {0}".format(statistics["population"]))
        print("\t\tNumber of users in Travian: {0}".format(statistics["user_count"]))
        print("\t\tNumber of villages in Travian: {0}".format(statistics["village_count"]))

        print("\tGenerating world map for {0} to file {1}".format(server_name, generate_map_image(database_name, image_file_name, today)))
        print("\tDone.")
        print("\n")

# Originally from http://code.activestate.com/recipes/496685-downloading-a-file-from-the-web/
# Copy the contents of a file from a given URL to a local file.
def download(url, file_name_zipped, file_name):
    if(not os.path.exists(file_name_zipped)):
        try:
            # Download the gzipped file
            urllib.request.urlretrieve(url, file_name_zipped)

            # Open the gzipped file and write the contents to an uncompressed file
            data_file_zipped = gzip.open(file_name_zipped, 'r')
            data_file_unzipped = open(file_name, "wb")
            data = data_file_zipped.read()
            data_file_unzipped.write(data)

            # Close the file handles
            data_file_unzipped.close()
            data_file_zipped.close()

            # You could add code to delete the original gzipped file if you want
        except:
            pass

def create_table(database_name):
    # This SQL originally from http://help.travian.com/index.php?type=faq&mod=230
    # But I made some minor modifications so it works with SQLite
    table_sql = """CREATE TABLE x_world (
    data_id integer PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
    id integer NOT NULL DEFAULT '0',
    x integer NOT NULL default '0',
    y integer NOT NULL default '0',
    tid integer unsigned NOT NULL default '0',
    vid integer unsigned NOT NULL default '0',
    village text NOT NULL default '',
    uid integer NOT NULL default '0',
    player text NOT NULL default '',
    aid integer unsigned NOT NULL default '0',
    alliance text NOT NULL default '',
    population integer unsigned NOT NULL default '0',
    date_created text
    );"""

    # Try and create the table.
    # If it fails it's probably because the table exists
    # We should probably handle this better though
    try:
        sql_connection = sqlite3.connect(database_name)
        sql_cursor = sql_connection.cursor()
        sql_cursor.execute(table_sql)
        sql_connection.commit()
    except:
        pass
    finally:
        sql_connection.close()

def clear_data(database_name, date_to_delete):
    sql_delete_current_data = """DELETE
    FROM x_world
    WHERE date_created = ?"""

    # Delete all the existing data from the given date
    try:
        sql_connection = sqlite3.connect(database_name)
        sql_cursor = sql_connection.cursor()
        sql_cursor.execute(sql_delete_current_data, [date_to_delete])
        sql_connection.commit()
    except:
        print("Warning:", sys.exc_info()[0])
    finally:
        sql_connection.close()

def load_data(database_name, data_file_name, today):
    try:
        # Open the data file
        data_file = open(data_file_name, mode='r', encoding="UTF8")

        try:
            sql_connection = sqlite3.connect(database_name)
            sql_cursor = sql_connection.cursor()

            # string.replace() to make the columns and data match up with our new schema
            # And run each SQL statement from the data file
            for line in data_file:
                line = line.replace("VALUES", "(id, x, y, tid, vid, village, uid, player, aid, alliance, population) VALUES")
                sql_cursor.execute(line)

            # Update all the new data with today's date
            sql_update_todays = """UPDATE x_world
            SET date_created = ?
            WHERE date_created IS NULL"""
            sql_cursor.execute(sql_update_todays, [today])

            sql_connection.commit()
        except:
            pass
        finally:
            sql_connection.close()
    except:
        pass

def get_statistics(database_name):
    try:
        sql_connection = sqlite3.connect(database_name)
        sql_cursor = sql_connection.cursor()

        #Population query
        sql_population = """SELECT SUM(population) FROM x_world"""
        sql_cursor.execute(sql_population)
        population = sql_cursor.fetchone()[0]

        #User count query
        sql_count_users = """SELECT COUNT(DISTINCT(uid)) FROM x_world"""
        sql_cursor.execute(sql_count_users)
        user_count = sql_cursor.fetchone()[0]

        #Village count query
        sql_count_villages = """SELECT COUNT(*) FROM x_world"""
        sql_cursor.execute(sql_count_villages)
        village_count = sql_cursor.fetchone()[0]

        return { "population" : population, "user_count" : user_count, "village_count" : village_count }
    except:
        pass
    finally:
        sql_connection.close()

def generate_map_image(database_name, image_file_name, date):
    try:
        sql_connection = sqlite3.connect(database_name)
        sql_connection.row_factory = sqlite3.Row
        sql_cursor = sql_connection.cursor()

        # Locations query
        sql_all = """SELECT x, y FROM x_world where date_created = ?"""

        #Create a surface (like an image canvas)
        surface = pygame.Surface((size, size))

        #Paint the background white
        back_color = pygame.Color(255, 255, 255, 255)
        surface.fill(back_color)

        #The color red for coloring the villages
        color = pygame.Color(255, 0, 0, 255)

        sql_cursor.execute(sql_all, [date])

        #For each village, set the corresponding pixel to red
        for row in sql_cursor.fetchall():
            surface.set_at((row[0] + offset, row[1] + offset), color)

        #Save the image to disk
        #Will save as a PNG file because of the extension
        pygame.image.save(surface, image_file_name)

        sql_connection.commit()
    except:
        pass
    finally:
        sql_connection.close()

    return image_file_name

#Run the main function
main()
