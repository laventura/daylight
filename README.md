# Daylight CLI

A command-line tool to get sunlight hours for any date at any location.

## Overview

`daylight` is a Python CLI tool that returns the number of hours of sunlight for a specified date and location. It automatically detects your current location by default and provides information about sunrise, sunset, and daylight duration.

## Features

- Get sunlight information for **any location** worldwide
- Query for **any date** (past, present, or future)
- Automatically detect your **current location** via IP address
- View results in multiple **output formats** (human-readable, JSON, brief, verbose)
- Support for special date shortcuts (`tomorrow`, `yesterday`, `day-after`)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/laventura/daylight.git
   cd daylight
   ```

2. Install required dependencies:
   ```bash
   pip install requests astral timezonefinder pytz
   ```

3. Make the script executable (optional, Unix/Linux/MacOS):
   ```bash
   chmod +x daylight.py
   ```

## Usage

### Basic Usage

```bash
python daylight.py
```
This returns sunlight hours for today at your current location.

### Date Options

```bash
# Specific date (YYYY-MM-DD format)
python daylight.py --date 2025-06-21

# Tomorrow
python daylight.py --tomorrow
python daylight.py -t

# Yesterday
python daylight.py --yesterday
python daylight.py -y

# Day after tomorrow
python daylight.py --day-after
```

### Location Options

```bash
# Specific location by name
python daylight.py --location "Paris, France"
python daylight.py -l "Tokyo, Japan"

# Location by ZIP/postal code
python daylight.py --zipcode 90210
python daylight.py -z 94043

# Exact coordinates
python daylight.py --latitude 37.7749 --longitude -122.4194
```

### Output Formats

```bash
# JSON format (for programmatic use)
python daylight.py --json
python daylight.py -j

# Brief output (hours only)
python daylight.py --brief
python daylight.py -b

# Verbose output (with additional astronomical details)
python daylight.py --verbose
python daylight.py -v
```

### Examples

```bash
# Get tomorrow's sunlight hours in London
python daylight.py --location "London, UK" --tomorrow

# Get sunlight hours for winter solstice in Sydney
python daylight.py --location "Sydney, Australia" --date 2025-12-21

# Get verbose output for summer solstice in Reykjavik
python daylight.py -l "Reykjavik, Iceland" -d 2025-06-21 -v
```

## Testing

Run the automated test suite:
```bash
python test_daylight.py
```

Run manual tests:
```bash
python manual_test_daylight.py
```

## How It Works

1. Determines the requested date and location
2. Gets the correct time zone for the location
3. Calculates sunrise, sunset, and daylight duration using astronomical formulas
4. Formats and displays the results based on the requested output type

## Dependencies

- `requests`: For API calls to IP geolocation and location services
- `astral`: For astronomical calculations
- `timezonefinder`: For determining time zones from coordinates
- `pytz` and `zoneinfo`: For time zone handling

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.