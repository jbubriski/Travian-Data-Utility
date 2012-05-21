# Travian Data Utility

A Python script to download Travian map data, load it into SQLite, and generate images.

## Requirements

- [Python 3.X (32-bit)](http://www.python.org/download/)
- [PyGame](http://pygame.org/download.shtml) 

The script has been tested with Python 3.2.3 and PyGame 1.92, but it should work with other variations of the major version numbers. **The 32-bit version of Python is required in order to be compatible with PyGame.**

## Usage
Just run the script!  It should create the following folder structure:

- data
	- [server name]
		- [server name].sqlite
		- [date].sql.gz
		- [date].sql
		- [date].jpg
- python data utility.py

If the script is successful you should have 4 files in each server folder (3 new files per day).  If the script fails, you may be missing files, depending on where the script failed in its execution.