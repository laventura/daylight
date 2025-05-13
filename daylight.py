#!/usr/bin/env python3
"""
daylight - A CLI tool to get sunlight hours for a given date and location.
"""

import argparse
import datetime
import json
import sys
import pytz
from typing import Dict, Any, Tuple, Optional
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder

import requests
from astral import LocationInfo
from astral.sun import sun


def get_location_from_ip() -> Tuple[str, float, float, str]:
    """
    Get the user's location based on their IP address.
    Returns a tuple of (location_name, latitude, longitude, timezone)
    """
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        data = response.json()
        
        # Extract location information
        location = data.get("city", "Unknown")
        if "region" in data and data["region"]:
            location += f", {data['region']}"
        elif "country" in data:
            location += f", {data['country']}"
            
        # Extract coordinates
        if "loc" in data and data["loc"]:
            lat_lng = data["loc"].split(",")
            latitude = float(lat_lng[0])
            longitude = float(lat_lng[1])
            
            # Get timezone from coordinates
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
            if not timezone_str:
                timezone_str = "UTC"
                
            return location, latitude, longitude, timezone_str
        
        raise ValueError("Could not determine location from IP")
    except Exception as e:
        print(f"Error determining location from IP: {e}", file=sys.stderr)
        print("Using default location: Mountain View, CA", file=sys.stderr)
        # Default to Mountain View, CA
        return "Mountain View, CA", 37.3861, -122.0839, "America/Los_Angeles"


def get_location_from_zipcode(zipcode: str) -> Tuple[str, float, float, str]:
    """
    Get location information from a ZIP/postal code.
    Returns a tuple of (location_name, latitude, longitude, timezone)
    """
    try:
        response = requests.get(
            f"https://nominatim.openstreetmap.org/search?postalcode={zipcode}&format=json&limit=1",
            headers={"User-Agent": "daylight-cli/1.0"},
            timeout=5
        )
        data = response.json()
        
        if not data:
            raise ValueError(f"Could not find location for ZIP code: {zipcode}")
            
        result = data[0]
        location_name = result.get("display_name", "").split(",")[0]
        location_name += f", {zipcode}"
        latitude = float(result["lat"])
        longitude = float(result["lon"])
        
        # Get timezone from coordinates
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        if not timezone_str:
            timezone_str = "UTC"
            
        return location_name, latitude, longitude, timezone_str
    except Exception as e:
        print(f"Error finding location for ZIP code {zipcode}: {e}", file=sys.stderr)
        raise


def get_location_from_name(location_name: str) -> Tuple[str, float, float, str]:
    """
    Convert a location name to coordinates.
    Returns a tuple of (formatted_location_name, latitude, longitude, timezone)
    """
    try:
        response = requests.get(
            f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1",
            headers={"User-Agent": "daylight-cli/1.0"},
            timeout=5
        )
        data = response.json()
        
        if not data:
            raise ValueError(f"Could not find location: {location_name}")
            
        result = data[0]
        # debug ony
        # print(f"[Debug: Nominatim result: {result}]", file=sys.stderr)
        formatted_name = result.get("display_name", "").split(",")[0]
        if len(formatted_name) < 3:  # If we got a very short name, use input
            formatted_name = location_name
            
        latitude = float(result["lat"])
        longitude = float(result["lon"])
        
        # Get timezone from coordinates
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        if not timezone_str:
            timezone_str = "UTC"
            
        return formatted_name, latitude, longitude, timezone_str
    except Exception as e:
        print(f"Error finding location {location_name}: {e}", file=sys.stderr)
        raise


def get_date_from_string(date_str: Optional[str] = None) -> datetime.date:
    """
    Parse a date string into a datetime.date object.
    Handles special keywords like 'tomorrow', 'yesterday', 'day-after'.
    If date_str is None, returns today's date.
    """
    today = datetime.date.today()
    
    if not date_str:
        return today
        
    date_str = date_str.lower()
    
    if date_str == "today":
        return today
    elif date_str == "tomorrow":
        return today + datetime.timedelta(days=1)
    elif date_str == "yesterday":
        return today - datetime.timedelta(days=1)
    elif date_str == "day-after":
        return today + datetime.timedelta(days=2)
    else:
        try:
            # Try to parse as YYYY-MM-DD
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(
                f"Invalid date format: {date_str}. "
                f"Use YYYY-MM-DD or keywords: today, tomorrow, yesterday, day-after"
            )


def get_sunlight_data(date: datetime.date, 
                      latitude: float, 
                      longitude: float, 
                      timezone_str: str, 
                      location_name: str = "Custom Location") -> Dict[str, Any]:
    """
    Calculate sunlight information for the given date and coordinates.
    Returns a dictionary with sunlight information.
    """
    # Create a location object with the given coordinates
    location = LocationInfo(
        name=location_name,
        region="",
        timezone=timezone_str,
        latitude=latitude,
        longitude=longitude
    )
    
    # Get sun information for the specified date
    s = sun(location.observer, date=date, tzinfo=ZoneInfo(timezone_str))
    
    # Calculate sunlight duration in hours
    sunrise = s["sunrise"]
    sunset = s["sunset"]
    
    # Calculate duration in hours and minutes
    duration = sunset - sunrise
    hours = duration.total_seconds() / 3600
    
    # Format sunrise and sunset times in local timezone
    sunrise_str = sunrise.strftime("%I:%M %p")
    sunset_str = sunset.strftime("%I:%M %p")
    
    # Build result dictionary
    result = {
        "date": date.isoformat(),
        "location": {
            "name": location.name,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_str
        },
        "sunlight": {
            "sunrise": sunrise.isoformat(),
            "sunset": sunset.isoformat(),
            "sunrise_time": sunrise_str,
            "sunset_time": sunset_str,
            "duration_hours": round(hours, 2),
        },
        "astronomical": {
            "dawn": s["dawn"].isoformat(),
            "dusk": s["dusk"].isoformat(),
            "noon": s["noon"].isoformat(),
        }
    }
    
    return result


def format_output(data: Dict[str, Any], output_format: str) -> str:
    """
    Format the sunlight data according to the specified output format.
    """
    date = datetime.date.fromisoformat(data["date"])
    date_str = date.strftime("%A, %B %d, %Y")
    location_name = data["location"]["name"]
    hours = data["sunlight"]["duration_hours"]
    sunrise = data["sunlight"]["sunrise_time"]
    sunset = data["sunlight"]["sunset_time"]
    lat = data["location"]["latitude"]
    lon = data["location"]["longitude"]
    timezone = data["location"]["timezone"]
    
    if output_format == "json":
        return json.dumps(data, indent=2)
    elif output_format == "brief":
        return f"{hours}"
    elif output_format == "verbose":
        # Add more astronomical information in verbose mode
        result = (
            f"Sunlight information for {date_str} at {location_name}:\n"
            f"  Sunrise: {sunrise}\n"
            f"  Sunset:  {sunset}\n"
            f"  Daylight duration: {hours} hours\n"
            f"  Lat/Lon:  {lat}, {lon}\n"
            f"  Timezone: {timezone}\n"
            f"\nAstronomical information:\n"
            f"  Dawn: {data['astronomical']['dawn']}\n"
            f"  Noon: {data['astronomical']['noon']}\n"
            f"  Dusk: {data['astronomical']['dusk']}\n"
        )
        return result
    else:  # default
        day_type = "Today's" if date == datetime.date.today() else f"{date_str}'s"
        return f"{day_type} sunlight in {location_name}: {hours} hours ({sunrise} to {sunset})"


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Get sunlight hours for a given date and location."
    )
    
    # Date options
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        "--date", "-d", 
        help="Specific date in YYYY-MM-DD format"
    )
    date_group.add_argument(
        "--today", 
        action="store_true", 
        help="Use today's date (default)"
    )
    date_group.add_argument(
        "--tomorrow", "-t", 
        action="store_true", 
        help="Use tomorrow's date"
    )
    date_group.add_argument(
        "--yesterday", "-y", 
        action="store_true", 
        help="Use yesterday's date"
    )
    date_group.add_argument(
        "--day-after", 
        action="store_true", 
        help="Use the day after tomorrow"
    )
    
    # Location options
    location_group = parser.add_mutually_exclusive_group()
    location_group.add_argument(
        "--location", "-l", 
        help="Location as 'City, Country' or 'City, State'"
    )
    location_group.add_argument(
        "--zipcode", "-z", 
        help="Location by ZIP/postal code"
    )
    location_group.add_argument(
        "--latitude", 
        type=float, 
        help="Latitude coordinate"
    )
    location_group.add_argument(
        "--longitude", 
        type=float, 
        help="Longitude coordinate"
    )
    
    # Output format options
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--json", "-j", 
        action="store_true", 
        help="Output in JSON format"
    )
    output_group.add_argument(
        "--brief", "-b", 
        action="store_true", 
        help="Output only the hours as a number"
    )
    output_group.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Output detailed information"
    )
    
    return parser.parse_args()


def main():
    """
    Main function for the daylight CLI.
    """
    args = parse_args()
    
    # Determine the date
    if args.today:
        date = get_date_from_string("today")
    elif args.tomorrow:
        date = get_date_from_string("tomorrow")
    elif args.yesterday:
        date = get_date_from_string("yesterday")
    elif args.day_after:
        date = get_date_from_string("day-after")
    elif args.date:
        date = get_date_from_string(args.date)
    else:
        date = get_date_from_string("today")  # Default to today
    
    # Determine the location
    try:
        if args.location:
            location_name, latitude, longitude, timezone_str = get_location_from_name(args.location)
        elif args.zipcode:
            location_name, latitude, longitude, timezone_str = get_location_from_zipcode(args.zipcode)
        elif args.latitude is not None and args.longitude is not None:
            latitude = args.latitude
            longitude = args.longitude
            
            # Get timezone from coordinates
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
            if not timezone_str:
                timezone_str = "UTC"
                
            location_name = f"Custom Location ({latitude}, {longitude})"
        else:
            # Default to IP-based location
            location_name, latitude, longitude, timezone_str = get_location_from_ip()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Get sunlight data
    try:
        data = get_sunlight_data(date, latitude, longitude, timezone_str, location_name)
        data["location"]["name"] = location_name
    except Exception as e:
        print(f"Error calculating sunlight data: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output format
    if args.json:
        output_format = "json"
    elif args.brief:
        output_format = "brief"
    elif args.verbose:
        output_format = "verbose"
    else:
        output_format = "default"
    
    # Print the formatted output
    print(format_output(data, output_format))


if __name__ == "__main__":
    main()