import sqlite3
import csv
import re
import os
import sys

# Database setup
DATABASE_FOLDER = 'database'
DATABASE_NAME = os.path.join(DATABASE_FOLDER, 'average_price_data.db')

# Table definitions, including cpi_info
TABLES = {
    "ap_item": '''
        CREATE TABLE IF NOT EXISTS ap_item (
            item_code TEXT PRIMARY KEY,
            item_name TEXT
        );
    ''',
    "ap_data_current": '''
        CREATE TABLE IF NOT EXISTS ap_data_current (
            series_id TEXT,
            year INTEGER,
            period TEXT,
            value REAL,
            footnote_codes TEXT,
            PRIMARY KEY(series_id, year, period)
        );
    ''',
    "ap_data_food": '''
        CREATE TABLE IF NOT EXISTS ap_data_food (
            series_id TEXT,
            year INTEGER,
            period TEXT,
            value REAL,
            footnote_codes TEXT,
            PRIMARY KEY(series_id, year, period)
        );
    ''',
    "ap_data_gasoline": '''
        CREATE TABLE IF NOT EXISTS ap_data_gasoline (
            series_id TEXT,
            year INTEGER,
            period TEXT,
            value REAL,
            footnote_codes TEXT,
            PRIMARY KEY(series_id, year, period)
        );
    ''',
    "ap_data_householdfuels": '''
        CREATE TABLE IF NOT EXISTS ap_data_householdfuels (
            series_id TEXT,
            year INTEGER,
            period TEXT,
            value REAL,
            footnote_codes TEXT,
            PRIMARY KEY(series_id, year, period)
        );
    ''',
    "ap_period": '''
        CREATE TABLE IF NOT EXISTS ap_period (
            period TEXT PRIMARY KEY,
            period_abbr TEXT,
            period_name TEXT
        );
    ''',
    "ap_area": '''
        CREATE TABLE IF NOT EXISTS ap_area (
            area_code TEXT PRIMARY KEY,
            area_name TEXT
        );
    ''',
    "ap_seasonal": '''
        CREATE TABLE IF NOT EXISTS ap_seasonal (
            seasonal_code TEXT PRIMARY KEY,
            seasonal_text TEXT
        );
    ''',
    "ap_series": '''
        CREATE TABLE IF NOT EXISTS ap_series (
            series_id TEXT PRIMARY KEY,
            area_code TEXT,
            item_code TEXT,
            series_title TEXT,
            footnote_codes TEXT,
            begin_year INTEGER,
            begin_period TEXT,
            end_year INTEGER,
            end_period TEXT
        );
    ''',
    "cpi_info": '''
        CREATE TABLE IF NOT EXISTS cpi_info (
            series_id TEXT,
            year INTEGER,
            period TEXT,
            value REAL,
            footnote_codes TEXT,
            PRIMARY KEY(series_id, year, period)
        );
    '''
}

# CSV to table mapping with CPI file
CSV_TO_TABLE_MAPPING = {
    'ap.item': 'ap_item',
    'ap.data.0.Current': 'ap_data_current',
    'ap.data.3.Food': 'ap_data_food',
    'ap.data.2.Gasoline': 'ap_data_gasoline',
    'ap.data.1.HouseholdFuels': 'ap_data_householdfuels',
    'ap.period': 'ap_period',
    'ap.area': 'ap_area',
    'ap.seasonal': 'ap_seasonal',
    'ap.series': 'ap_series',
    'CUUR0000SA0.txt': 'cpi_info',  # CPI file mapped to cpi_info table
}

def create_tables(conn):
    """Creates all the necessary tables."""
    cursor = conn.cursor()
    for table_name, create_stmt in TABLES.items():
        cursor.execute(create_stmt)
    conn.commit()

def process_file(file_path, conn):
    """Processes each file and inserts its data into the corresponding table."""
    cursor = conn.cursor()
    file_name = os.path.basename(file_path)  # Extract the file name from the full path
    table_name = CSV_TO_TABLE_MAPPING.get(file_name)
    if not table_name:
        print(f"File not mapped to a table: {file_name}")
        return

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            # Cleaning up, parsing the CPI file, which has pipe-delineated data and extra symbols
            lines = file.readlines()

            # Regex to match actual data rows (ignore lines with only pipes or dashes)
            data_pattern = re.compile(r'^\|\s+([^|]+)\s+\|\s+(\d{4})\s+\|\s+([A-Z0-9]+)\s+\|\s+([\d\.]+)\s+\|\s*([^|]*)\s+\|')

            for line in lines:
                match = data_pattern.match(line)
                if match:
                    # Extract the matching parts of the regex
                    series_id, year, period, value, footnote_codes = match.groups()

                    # Build the final query and insert into database
                    query = '''INSERT OR REPLACE INTO cpi_info (series_id, year, period, value, footnote_codes)
                               VALUES (?, ?, ?, ?, ?)'''
                    cursor.execute(query, (series_id.strip(), int(year), period.strip(), float(value), footnote_codes.strip() or None))

        conn.commit()
    except Exception as e:
        print(f"Error while processing file {file_name}: {e}")

def update_database(file_names):
    """Loads new data into the database from the specified files."""
    try:
        # Ensure the database directory exists
        if not os.path.exists(DATABASE_FOLDER):
            os.makedirs(DATABASE_FOLDER)

        conn = sqlite3.connect(DATABASE_NAME)
        create_tables(conn)
        for file_name in file_names:
            process_file(file_name, conn)
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def initialize_database():
    """Initializes the database by processing all files for the first time."""
    downloads_folder = 'downloads'
    if not os.path.exists(downloads_folder):
        print(f"Error: The downloads folder '{downloads_folder}' does not exist.")
        sys.exit(1)

    files_to_process = list(CSV_TO_TABLE_MAPPING.keys())
    missing_files = [file for file in files_to_process if not os.path.exists(os.path.join(downloads_folder, file))]

    if missing_files:
        print(f"Error: The following required files are missing in the downloads folder: {', '.join(missing_files)}")
        sys.exit(1)

    file_paths = [os.path.join(downloads_folder, file) for file in files_to_process]
    update_database(file_paths)

if __name__ == "__main__":
    # Initialize the database
    initialize_database()

    # After new files are published, use update_database with new file names
    # update_database(['downloads/CUUR0000SA0_1.txt'])