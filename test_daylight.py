#!/usr/bin/env python3
"""
Test cases for the daylight CLI tool.
This script tests various functionality of the daylight CLI.
"""

import unittest
import subprocess
import json
import datetime
import sys
import os
from unittest.mock import patch

# Ensure we can import from the daylight module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import daylight

class TestDaylightCLI(unittest.TestCase):
    """Test cases for the daylight CLI tool."""

    def test_default_behavior(self):
        """Test the default behavior (today, current location)."""
        # Due to IP geolocation, we can't assert exact values, but we can verify output format
        result = subprocess.run(["python", "daylight.py"], 
                               capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        # Verify it contains expected output parts
        self.assertIn("sunlight in", output)
        self.assertIn("hours", output)
        self.assertRegex(output, r'\d+\.\d+ hours')
        self.assertRegex(output, r'\d+:\d+ [AP]M to \d+:\d+ [AP]M')

    def test_json_output(self):
        """Test JSON output format."""
        result = subprocess.run(["python", "daylight.py", "--json"], 
                               capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        # Try to parse as JSON
        data = json.loads(output)
        
        # Verify expected keys are present
        expected_keys = ["date", "location", "sunlight", "astronomical"]
        for key in expected_keys:
            self.assertIn(key, data)
            
        # Verify sunlight data
        self.assertIn("duration_hours", data["sunlight"])
        self.assertIn("sunrise", data["sunlight"])
        self.assertIn("sunset", data["sunlight"])
        
        # Verify location data
        self.assertIn("name", data["location"])
        self.assertIn("latitude", data["location"])
        self.assertIn("longitude", data["location"])
        self.assertIn("timezone", data["location"])

    def test_brief_output(self):
        """Test brief output format."""
        result = subprocess.run(["python", "daylight.py", "--brief"], 
                               capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        # Should only contain a number
        self.assertRegex(output, r'^\d+\.\d+$')

    def test_verbose_output(self):
        """Test verbose output format."""
        result = subprocess.run(["python", "daylight.py", "--verbose"], 
                               capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        # Verify expected sections
        self.assertIn("Sunlight information for", output)
        self.assertIn("Sunrise:", output)
        self.assertIn("Sunset:", output)
        self.assertIn("Daylight duration:", output)
        self.assertIn("Astronomical information:", output)
        self.assertIn("Dawn:", output)
        self.assertIn("Noon:", output)
        self.assertIn("Dusk:", output)

    def test_specific_date(self):
        """Test specifying a date."""
        # Test with a specific date
        date_str = "2025-06-21"  # Summer solstice
        result = subprocess.run(["python", "daylight.py", "--date", date_str], 
                               capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        # Verify date appears in output
        self.assertRegex(output, r'June 21, 2025|06-21|2025-06-21|6/21/2025')

    def test_tomorrow(self):
        """Test tomorrow option."""
        # Get tomorrow's date for verification
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%B %d, %Y")
        
        result = subprocess.run(["python", "daylight.py", "--tomorrow"], 
                               capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        # Check if date is in the output (may be formatted differently)
        self.assertTrue(
            tomorrow_str in output or 
            tomorrow.strftime("%Y-%m-%d") in output or
            tomorrow.strftime("%m/%d/%Y") in output
        )

    @patch('daylight.get_location_from_name')
    def test_specific_location_timezone(self, mock_get_location):
        """Test specific location with time zone."""
        # Mock the location function to return a known location and timezone
        mock_get_location.return_value = ("Tokyo", 35.6762, 139.6503, "Asia/Tokyo")
        
        result = subprocess.run(["python", "daylight.py", "--location", "Tokyo"], 
                               capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        # Verify location appears in output
        self.assertIn("Tokyo", output)
        
        # Sunrise and sunset should be in a reasonable range and positive daylight hours
        result_json = subprocess.run(["python", "daylight.py", "--location", "Tokyo", "--json"], 
                                   capture_output=True, text=True, check=True)
        data = json.loads(result_json.stdout.strip())
        
        # Daylight hours should be positive
        self.assertGreater(data["sunlight"]["duration_hours"], 0)
        
        # Time zone should be correct
        self.assertEqual(data["location"]["timezone"], "Asia/Tokyo")

    @patch('daylight.get_location_from_name')
    def test_london_timezone(self, mock_get_location):
        """Test London time zone."""
        # Mock the location function to return London
        mock_get_location.return_value = ("London", 51.5074, -0.1278, "Europe/London")
        
        result_json = subprocess.run(["python", "daylight.py", "--location", "London", "--json"], 
                                   capture_output=True, text=True, check=True)
        data = json.loads(result_json.stdout.strip())
        
        # Daylight hours should be positive
        self.assertGreater(data["sunlight"]["duration_hours"], 0)
        
        # Time zone should be correct
        self.assertEqual(data["location"]["timezone"], "Europe/London")
        
        # For London in spring/summer, sunrise should be early morning
        sunrise_time = data["sunlight"]["sunrise_time"]
        # Convert to 24-hour format for easier comparison
        if "AM" in sunrise_time:
            # Should be early morning (before 6 AM in summer)
            hour = int(sunrise_time.split(":")[0])
            if hour == 12:
                hour = 0
            self.assertLess(hour, 6)

    @patch('daylight.get_location_from_name')
    def test_los_angeles_timezone(self, mock_get_location):
        """Test Los Angeles time zone."""
        # Mock the location function to return LA
        mock_get_location.return_value = ("Los Angeles", 34.0522, -118.2437, "America/Los_Angeles")
        
        result_json = subprocess.run(["python", "daylight.py", "--location", "Los Angeles", "--json"], 
                                   capture_output=True, text=True, check=True)
        data = json.loads(result_json.stdout.strip())
        
        # Daylight hours should be positive
        self.assertGreater(data["sunlight"]["duration_hours"], 0)
        
        # Time zone should be correct
        self.assertEqual(data["location"]["timezone"], "America/Los_Angeles")

    def test_direct_function_calls(self):
        """Test the internal functions directly."""
        # Test the date parsing function
        today = datetime.date.today()
        self.assertEqual(daylight.get_date_from_string("today"), today)
        self.assertEqual(daylight.get_date_from_string("tomorrow"), today + datetime.timedelta(days=1))
        self.assertEqual(daylight.get_date_from_string("yesterday"), today - datetime.timedelta(days=1))
        self.assertEqual(daylight.get_date_from_string("day-after"), today + datetime.timedelta(days=2))
        
        # Test with a specific date
        test_date = "2025-12-25"
        parsed_date = daylight.get_date_from_string(test_date)
        self.assertEqual(parsed_date.year, 2025)
        self.assertEqual(parsed_date.month, 12)
        self.assertEqual(parsed_date.day, 25)

    def test_edge_cases(self):
        """Test edge cases that might cause issues."""
        # Test with a date near the international date line
        with patch('daylight.get_location_from_name') as mock_get_location:
            # Mock the location function to return a location near the date line
            mock_get_location.return_value = ("Fiji", -17.7134, 178.0650, "Pacific/Fiji")
            
            result = subprocess.run(["python", "daylight.py", "--location", "Fiji", "--json"], 
                                   capture_output=True, text=True, check=True)
            data = json.loads(result.stdout.strip())
            
            # Ensure daylight hours are positive
            self.assertGreater(data["sunlight"]["duration_hours"], 0)

        # Test with extreme northern latitude (summer/winter extremes)
        with patch('daylight.get_location_from_name') as mock_get_location:
            # Mock the location function to return a far northern location
            mock_get_location.return_value = ("Svalbard", 78.2232, 15.6267, "Arctic/Longyearbyen")
            
            # Test summer solstice (24-hour daylight)
            result = subprocess.run(
                ["python", "daylight.py", "--location", "Svalbard", "--date", "2025-06-21", "--json"], 
                capture_output=True, text=True, check=True
            )
            data = json.loads(result.stdout.strip())
            
            # In summer, should be close to 24 hours of daylight
            hours = data["sunlight"]["duration_hours"]
            # Due to various calculation methods, just check it's more than 20 hours
            self.assertGreater(hours, 20)

            # Test winter solstice (minimal daylight)
            result = subprocess.run(
                ["python", "daylight.py", "--location", "Svalbard", "--date", "2025-12-21", "--json"], 
                capture_output=True, text=True, check=True
            )
            data = json.loads(result.stdout.strip())
            
            # In winter, should be close to 0 hours of daylight
            hours = data["sunlight"]["duration_hours"]
            # Due to various calculation methods, just check it's less than 4 hours
            self.assertLess(hours, 4)

if __name__ == "__main__":
    unittest.main()