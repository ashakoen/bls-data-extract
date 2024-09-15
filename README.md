# Average Price Data (AP) Database

## Table of Contents

- [Introduction](#introduction)
- [Database Structure](#database-structure)
  - [Tables and Their Relationships](#tables-and-their-relationships)
  - [Schema Definition](#schema-definition)
- [Data Flow for Query Construction](#data-flow-for-query-construction)
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Installing Dependencies](#installing-dependencies)
  - [Setting Up the Database](#setting-up-the-database)
  - [Downloading Data](#downloading-data)
  - [Fetching CPI Data via API](#fetching-cpi-data-via-api)
- [Usage Examples](#usage-examples)
  - [Sample Query Structure](#sample-query-structure)
- [Important Notes](#important-notes)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

The **Average Price Data (AP)** from the **Bureau of Labor Statistics (BLS)** provides detailed information on average consumer prices for household fuels, motor fuels, and food items. Collected monthly across various urban areas in the United States, this data is crucial for measuring the price levels of specific items over time and across different regions.

This repository contains scripts and a database schema to set up and manage a local SQLite database for storing and querying the AP data. It includes tools for downloading the latest data from the BLS website and fetching Consumer Price Index (CPI) data via the BLS API.

---

## Database Structure

The database comprises several tables that store data about items, areas, periods, series, and the actual price observations. Understanding the schema and relationships between these tables is crucial for constructing accurate SQL queries and extracting meaningful insights.

### Tables and Their Relationships

1. **```ap_item```**

   - **Purpose**: Stores information about the items for which average prices are recorded.
   - **Fields**:
     - `item_code` (TEXT, PRIMARY KEY): Unique identifier for each item.
     - `item_name` (TEXT): Descriptive name of the item.
   - **Example Entries**:
     - `701111`: Flour, white, all purpose, per lb. (453.6 gm)
     - `702111`: Sugar, white, all sizes, per lb. (453.6 gm)

2. **```ap_area```**

   - **Purpose**: Contains information about the geographic areas covered in the survey.
   - **Fields**:
     - `area_code` (TEXT, PRIMARY KEY): Unique identifier for each area.
     - `area_name` (TEXT): Descriptive name of the area.
   - **Example Entries**:
     - `0000`: U.S. city average
     - `A100`: Northeast Urban
     - `S200`: South Urban

3. **```ap_period```**

   - **Purpose**: Defines the periods (months) for which data is collected.
   - **Fields**:
     - `period` (TEXT, PRIMARY KEY): Code representing the period (e.g., M01 for January).
     - `period_abbr` (TEXT): Abbreviation of the period name (e.g., JAN).
     - `period_name` (TEXT): Full name of the period (e.g., January).
   - **Example Entries**:
     - `M01`: JAN, January
     - `M02`: FEB, February

4. **```ap_series```**

   - **Purpose**: Provides metadata about each time series, linking items and areas.
   - **Fields**:
     - `series_id` (TEXT, PRIMARY KEY): Unique identifier for each time series.
     - `area_code` (TEXT): References `ap_area.area_code`.
     - `item_code` (TEXT): References `ap_item.item_code`.
     - `series_title` (TEXT): Title describing the series.
     - `footnote_codes` (TEXT): Any associated footnotes.
     - `begin_year` (INTEGER): First year of data availability.
     - `begin_period` (TEXT): First period of data availability.
     - `end_year` (INTEGER): Last year of data availability.
     - `end_period` (TEXT): Last period of data availability.
   - **Relationships**:
     - `ap_series.area_code` → `ap_area.area_code`
     - `ap_series.item_code` → `ap_item.item_code`

5. **```ap_data_current```**

   - **Purpose**: Holds current year-to-date average price data.
   - **Fields**:
     - `series_id` (TEXT): References `ap_series.series_id`.
     - `year` (INTEGER): Year of the observation.
     - `period` (TEXT): References `ap_period.period`.
     - `value` (REAL): Observed average price.
     - `footnote_codes` (TEXT): Any associated footnotes.
   - **Primary Key**: `(series_id, year, period)`
   - **Relationships**:
     - `ap_data_current.series_id` → `ap_series.series_id`
     - `ap_data_current.period` → `ap_period.period`

6. **```ap_data_food```**

   - **Purpose**: Contains average price data for food items.
   - **Fields and Relationships**: Same as `ap_data_current`.

7. **```ap_data_gasoline```**

   - **Purpose**: Contains average price data for gasoline.
   - **Fields and Relationships**: Same as `ap_data_current`.

8. **```ap_data_householdfuels```**

   - **Purpose**: Contains average price data for household fuels.
   - **Fields and Relationships**: Same as `ap_data_current`.

9. **```ap_seasonal```**

   - **Purpose**: Stores information about seasonal adjustment codes.
   - **Fields**:
     - `seasonal_code` (TEXT, PRIMARY KEY): Code indicating seasonal adjustment.
     - `seasonal_text` (TEXT): Description of the seasonal code.

### Schema Definition

Below is the SQL schema used to create the tables:

```sql
CREATE TABLE ap_item (
    item_code TEXT PRIMARY KEY,
    item_name TEXT
);

CREATE TABLE ap_area (
    area_code TEXT PRIMARY KEY,
    area_name TEXT
);

CREATE TABLE ap_period (
    period TEXT PRIMARY KEY,
    period_abbr TEXT,
    period_name TEXT
);

CREATE TABLE ap_seasonal (
    seasonal_code TEXT PRIMARY KEY,
    seasonal_text TEXT
);

CREATE TABLE ap_series (
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

CREATE TABLE ap_data_current (
    series_id TEXT,
    year INTEGER,
    period TEXT,
    value REAL,
    footnote_codes TEXT,
    PRIMARY KEY(series_id, year, period)
);

CREATE TABLE ap_data_food (
    series_id TEXT,
    year INTEGER,
    period TEXT,
    value REAL,
    footnote_codes TEXT,
    PRIMARY KEY(series_id, year, period)
);

CREATE TABLE ap_data_gasoline (
    series_id TEXT,
    year INTEGER,
    period TEXT,
    value REAL,
    footnote_codes TEXT,
    PRIMARY KEY(series_id, year, period)
);

CREATE TABLE ap_data_householdfuels (
    series_id TEXT,
    year INTEGER,
    period TEXT,
    value REAL,
    footnote_codes TEXT,
    PRIMARY KEY(series_id, year, period)
);

CREATE TABLE cpi_info (
    series_id TEXT,
    year INTEGER,
    period TEXT,
    value REAL,
    footnote_codes TEXT,
    PRIMARY KEY(series_id, year, period)
);
```

---

## Data Flow for Query Construction

To construct a query that retrieves specific average price data, follow these steps:

1. **Identify the Item**:
   - Use `ap_item` to find the `item_code` corresponding to the desired `item_name`.

2. **Identify the Area**:
   - Use `ap_area` to find the `area_code` corresponding to the desired `area_name`.

3. **Find the Series ID**:
   - Use `ap_series` to find the `series_id` matching both the `item_code` and `area_code`.

4. **Retrieve Data Observations**:
   - Use the `series_id` to query the appropriate `ap_data_*` table (`ap_data_food`, `ap_data_gasoline`, etc.) for the desired `year` and `period`.

5. **Join Period Information**:
   - Use `ap_period` to translate `period` codes into readable `period_name` values.

---

## Setup Instructions

### Prerequisites

- **Python 3.6+**
- **SQLite3**
- **pip** (Python package installer)
- **Virtual Environment** (recommended)

### Installing Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/ap-database.git
cd ap-database

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

# Install required Python packages
pip install -r requirements.txt
```

### Setting Up the Database

Run the `seed_data.py` script to initialize the database:

```bash
python seed_data.py
```

This script will:

- Create the SQLite database named `average_price_data.db`.
- Create all the tables as per the schema.
- Load data from local CSV files into the database.

### Downloading Data

Use the `get_http.py` script to download the necessary data files from the BLS website:

```bash
python get_http.py
```

This script will:

- Download specified files from the BLS FTP site.
- Save them in the `downloads` directory.

**Note**: Ensure that the `downloads` directory exists or will be created by the script.

### Fetching CPI Data via API

Use the `get_api.py` script to fetch Consumer Price Index (CPI) data via the BLS API:

1. **Obtain a BLS API Key**:

   - Register at the [BLS website](https://data.bls.gov/registrationEngine/) to obtain an API key.
   - Store the API key in a `.env` file in the project root:

     ```
     BLS_API_KEY=your_api_key_here
     ```

2. **Run the Script**:

   ```bash
   python get_api.py
   ```

   This script will:

   - Fetch CPI data for specified `series_id`, `start_year`, and `end_year`.
   - Save the data into text files and insert it into the `cpi_info` table in the database.

---

## Usage Examples

### Sample Query Structure

To retrieve specific average price data, you can use the following SQL query structure:

```sql
SELECT
  d.year,
  p.period_name,
  i.item_name,
  a.area_name,
  d.value
FROM
  ap_data_food AS d
JOIN
  ap_series AS s ON d.series_id = s.series_id
JOIN
  ap_item AS i ON s.item_code = i.item_code
JOIN
  ap_area AS a ON s.area_code = a.area_code
JOIN
  ap_period AS p ON d.period = p.period
WHERE
  i.item_name = 'Sugar, white, all sizes, per lb. (453.6 gm)'
  AND a.area_name = 'U.S. city average'
ORDER BY
  d.year, p.period_name;
```

This query will:

- Retrieve the average price of sugar per pound in U.S. city averages.
- Display the data ordered by year and month.

---

## Important Notes

- **Primary Keys**:
  - Ensure uniqueness and efficient data retrieval.

- **Foreign Keys**:
  - Maintain referential integrity between tables.

- **Data Partitioning**:
  - Data is divided into specific tables based on item categories for optimized access.

- **Understanding Period Codes**:
  - Monthly Periods:
    - `M01` to `M12` represent January to December.
  - Annual Averages:
    - `M13` may be used to represent annual average data.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

---

## License

This project is licensed under the [MIT License](LICENSE).

---