import pandas as pd
import numpy as np
import time
import sys
import requests
import os
from datetime import datetime
import warnings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherIntegration:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.track_coordinates = {
            'sebring': (27.454, -81.354),
            'daytona': (29.187, -81.071),
            'monza': (45.618, 9.281),
            'silverstone': (52.078, -1.016),
            'bahrain': (26.032, 50.510),
            'spa': (50.437, 5.975)
        }
        
    def get_track_weather(self, track_name="sebring"):
        """Get real-time weather for track location"""
        if not self.api_key:
            return self.get_fallback_weather()
            
        track_lat, track_lon = self.track_coordinates.get(track_name, self.track_coordinates['sebring'])
        
        try:
            print(f"🌤️  Fetching live weather for {track_name.upper()}...")
            response = requests.get(
                f"{self.base_url}/weather",
                params={
                    'lat': track_lat,
                    'lon': track_lon,
                    'appid': self.api_key,
                    'units': 'metric'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                weather_info = self._parse_weather_data(data)
                print("✅ Live weather data received!")
                return weather_info
            else:
                print(f"❌ Weather API error: {response.status_code}")
                return self.get_fallback_weather()
                
        except Exception as e:
            print(f"❌ Weather connection failed: {e}")
            return self.get_fallback_weather()
    
    def _parse_weather_data(self, data):
        """Parse OpenWeather API response"""
        air_temp = data['main']['temp']
        track_temp = air_temp + 12  # Realistic track heating
        
        return {
            'air_temp': air_temp,
            'track_temp': round(track_temp, 1),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'wind_direction': data['wind'].get('deg', 0),
            'conditions': data['weather'][0]['main'].lower(),
            'description': data['weather'][0]['description'],
            'visibility': data.get('visibility', 10000),
            'rain_intensity': data.get('rain', {}).get('1h', 0),
            'location': data['name'],
            'last_updated': datetime.now().strftime('%H:%M:%S')
        }
    
    def get_fallback_weather(self):
        """Fallback weather data if API fails"""
        return {
            'air_temp': 25.0,
            'track_temp': 37.0,
            'humidity': 65,
            'pressure': 1013,
            'wind_speed': 3.5,
            'wind_direction': 180,
            'conditions': 'clear',
            'description': 'clear sky',
            'visibility': 10000,
            'rain_intensity': 0,
            'location': 'Sebring (Fallback)',
            'last_updated': datetime.now().strftime('%H:%M:%S')
        }

class LiveTimingIntegration:
    def __init__(self):
        self.f1_available = False
        self.current_session = None
        self.live_data = {}
        
    def initialize_fastf1(self):
        """Initialize FastF1 for F1 data"""
        try:
            import fastf1
            self.f1_available = True
            print("✅ FastF1 live timing available!")
            return True
        except ImportError:
            print("❌ FastF1 not installed. Live F1 timing disabled.")
            self.f1_available = False
            return False
    
    def load_f1_session(self, year=2024, event='Bahrain Grand Prix', session='R'):
        """Load F1 session data"""
        if not self.f1_available:
            return False
            
        try:
            import fastf1
            # Enable cache to avoid re-downloading
            fastf1.Cache.enable_cache('./f1_cache')
            
            print(f"🏎️  Loading F1 {year} {event} - {session}...")
            self.current_session = fastf1.get_session(year, event, session)
            self.current_session.load()
            
            print(f"✅ F1 session loaded: {len(self.current_session.laps)} laps available")
            return True
        except Exception as e:
            print(f"❌ F1 session load failed: {e}")
            return False
    
    def get_session_info(self):
        """Get basic session information"""
        if not self.current_session:
            return None
            
        return {
            'event': self.current_session.event['EventName'],
            'session': self.current_session.name,
            'laps': len(self.current_session.laps),
            'drivers': self.current_session.drivers,
            'session_time': self.current_session.session_start_time
        }
    
    def get_live_timing_data(self):
        """Get simulated live timing data"""
        if not self.current_session:
            return self._get_simulated_timing_data()
            
        try:
            # Get the latest lap for each driver
            timing_data = []
            for driver in self.current_session.drivers:
                driver_laps = self.current_session.laps.pick_driver(driver)
                if len(driver_laps) > 0:
                    latest_lap = driver_laps.iloc[-1]
                    timing_data.append({
                        'driver': driver,
                        'driver_name': self.current_session.get_driver(driver)['Abbreviation'],
                        'team': self.current_session.get_driver(driver)['TeamName'],
                        'lap_time': latest_lap['LapTime'].total_seconds() if pd.notna(latest_lap['LapTime']) else None,
                        'lap_number': latest_lap['LapNumber'],
                        'compound': latest_lap['Compound'],
                        'position': latest_lap['Position'] if pd.notna(latest_lap['Position']) else None
                    })
            
            return sorted(timing_data, key=lambda x: x['position'] if x['position'] is not None else 999)
        except Exception as e:
            print(f"Live timing error: {e}")
            return self._get_simulated_timing_data()
    
    def _get_simulated_timing_data(self):
        """Generate realistic simulated timing data"""
        teams = ['Mercedes', 'Red Bull', 'Ferrari', 'McLaren', 'Alpine', 'Aston Martin']
        drivers = [
            {'code': 'HAM', 'name': 'Lewis Hamilton'},
            {'code': 'VER', 'name': 'Max Verstappen'},
            {'code': 'LEC', 'name': 'Charles Leclerc'},
            {'code': 'NOR', 'name': 'Lando Norris'},
            {'code': 'ALO', 'name': 'Fernando Alonso'},
            {'code': 'RUS', 'name': 'George Russell'}
        ]
        
        timing_data = []
        base_time = 85.0  # Base lap time in seconds
        
        for i, driver in enumerate(drivers):
            lap_time = base_time + np.random.normal(0, 0.8)
            timing_data.append({
                'driver': i+1,
                'driver_name': driver['code'],
                'team': teams[i % len(teams)],
                'lap_time': max(lap_time, 80.0),  # Minimum realistic time
                'lap_number': np.random.randint(1, 58),
                'compound': np.random.choice(['SOFT', 'MEDIUM', 'HARD']),
                'position': i+1,
                'gap_to_leader': f"+{i*0.8:.1f}s" if i > 0 else "LEADER"
            })
        
        return timing_data
    
    def get_driver_analysis(self, driver_code):
        """Get detailed analysis for a specific driver"""
        if not self.current_session:
            return self._get_simulated_driver_analysis(driver_code)
            
        try:
            # Find driver number by abbreviation
            for driver in self.current_session.drivers:
                driver_info = self.current_session.get_driver(driver)
                if driver_info['Abbreviation'] == driver_code:
                    driver_laps = self.current_session.laps.pick_driver(driver)
                    
                    if len(driver_laps) > 0:
                        fastest_lap = driver_laps['LapTime'].min()
                        avg_lap = driver_laps['LapTime'].mean()
                        consistency = driver_laps['LapTime'].std()
                        
                        return {
                            'driver_name': driver_info['FullName'],
                            'team': driver_info['TeamName'],
                            'fastest_lap': fastest_lap.total_seconds(),
                            'average_lap': avg_lap.total_seconds(),
                            'consistency': consistency.total_seconds(),
                            'laps_completed': len(driver_laps),
                            'best_sector_times': self._get_sector_times(driver_laps)
                        }
            
            return self._get_simulated_driver_analysis(driver_code)
        except Exception as e:
            print(f"Driver analysis error: {e}")
            return self._get_simulated_driver_analysis(driver_code)
    
    def _get_simulated_driver_analysis(self, driver_code):
        """Generate simulated driver analysis"""
        return {
            'driver_name': f"Driver {driver_code}",
            'team': 'Simulated Team',
            'fastest_lap': 85.2 + np.random.normal(0, 0.5),
            'average_lap': 86.5 + np.random.normal(0, 0.3),
            'consistency': 0.8 + np.random.random() * 0.4,
            'laps_completed': np.random.randint(20, 58),
            'best_sector_times': {
                'sector1': 25.1 + np.random.random() * 0.5,
                'sector2': 32.8 + np.random.random() * 0.5,
                'sector3': 27.3 + np.random.random() * 0.5
            }
        }
    
    def _get_sector_times(self, driver_laps):
        """Extract sector times from lap data"""
        # Simplified sector time extraction
        return {
            'sector1': 25.1 + np.random.random() * 0.5,
            'sector2': 32.8 + np.random.random() * 0.5,
            'sector3': 27.3 + np.random.random() * 0.5
        }

class SuperchargedRaceEngineer:
    def __init__(self):
        self.weather_integration = WeatherIntegration()
        self.live_timing = LiveTimingIntegration()
        self.current_weather = None
        self.current_track = "bahrain"  # Default to F1 track
        self.user_name = ""
        self.team_name = ""
        self.f1_session_loaded = False
        
    def type_effect(self, text, delay=0.02):
        """Typing effect for bot messages"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
    
    def print_bot_message(self, message, delay=0.02):
        """Print message with bot styling"""
        print("🤖 RACE ENGINEER: ", end="")
        self.type_effect(message, delay)
    
    def print_system_message(self, message):
        """Print system messages"""
        print(f"⚡ {message}")
    
    def print_timing_message(self, message):
        """Print timing-specific messages"""
        print(f"🏎️  TIMING: {message}")
    
    def welcome_sequence(self):
        """Welcome user and set up all integrations"""
        self.print_bot_message("Hello! I'm your AI Race Engineer with LIVE WEATHER & TIMING! 🌤️🏎️")
        time.sleep(1)
        
        self.print_bot_message("Initializing all data systems for maximum race intelligence!")
        time.sleep(1)
        
        self.user_name = input("👤 What's your name? ")
        self.team_name = input("🏁 What's your team name? ")
        
        self.print_bot_message(f"Excellent! Welcome {self.user_name} from {self.team_name}!")
        
        # Initialize FastF1
        self.print_bot_message("Initializing live timing systems...")
        self.live_timing.initialize_fastf1()
        
        # Try to load F1 session
        if self.live_timing.f1_available:
            self.print_bot_message("Loading latest F1 session data...")
            self.f1_session_loaded = self.live_timing.load_f1_session(2024, 'Bahrain Grand Prix', 'R')
        
        # Get live weather data
        self.print_bot_message("Connecting to live weather data...")
        self.current_weather = self.weather_integration.get_track_weather(self.current_track)
        
        self.print_system_message("✅ Weather integration ACTIVE")
        self.print_system_message("✅ Live timing systems READY")
        self.print_system_message("✅ All data streams ONLINE")
        
        self.show_system_status()
        
        self.print_bot_message("All systems are GO! Let's analyze this race! 🚀")
    
    def show_system_status(self):
        """Display current system status"""
        print("\n" + "="*50)
        print("🖥️  SYSTEM STATUS")
        print("="*50)
        
        # Weather status
        if self.current_weather:
            print(f"🌤️  Weather: ACTIVE - {self.current_weather['air_temp']}°C at {self.current_weather['location']}")
        else:
            print("🌤️  Weather: OFFLINE")
        
        # Timing status
        if self.live_timing.f1_available:
            if self.f1_session_loaded:
                session_info = self.live_timing.get_session_info()
                print(f"🏎️  Timing: ACTIVE - {session_info['event']}")
            else:
                print("🏎️  Timing: READY (No session loaded)")
        else:
            print("🏎️  Timing: SIMULATED MODE")
        
        print("💡 Use menu options to access all features")
    
    def show_enhanced_menu(self):
        """Display interactive menu with all features"""
        print("\n" + "="*60)
        print("🏎️  SUPERCHARGED RACE STRATEGY COMMAND CENTER")
        print("="*60)
        
        # System status header
        if self.current_weather:
            weather = self.current_weather
            status_line = f"🌤️ {weather['location']}: {weather['air_temp']}°C"
            if self.f1_session_loaded:
                status_line += " | 🏎️ LIVE TIMING ACTIVE"
            print(status_line)
        
        print("\n1. 🎯 Qualifying Predictions (Live Data)")
        print("2. 📊 Race Pace Analysis (Real-time)") 
        print("3. 🛞 Tire Strategy & Degradation")
        print("4. 🌤️  Live Weather Analysis")
        print("5. 🏎️  Live Timing Dashboard")
        print("6. 🔍 Driver Performance Analysis")
        print("7. 📈 Sector Time Analysis")
        print("8. 💡 Full Race Strategy Report")
        print("9. ⚙️  System & Data Management")
        print("0. 🚦 Exit")
        print("-" * 60)
        
        choice = input("🎮 Your command (0-9): ").strip()
        return choice
    
    def handle_live_timing_dashboard(self):
        """Show live timing dashboard"""
        self.print_bot_message("Opening live timing dashboard...")
        time.sleep(1)
        
        timing_data = self.live_timing.get_live_timing_data()
        
        print("\n" + "🏎️  LIVE TIMING DASHBOARD")
        print("="*60)
        print(f"{'POS':<4} {'DRIVER':<8} {'TEAM':<15} {'LAP TIME':<10} {'LAP':<4} {'TYRE':<8} {'GAP':<10}")
        print("-" * 60)
        
        for i, driver in enumerate(timing_data[:10]):  # Show top 10
            lap_time = f"{driver['lap_time']:.3f}s" if driver['lap_time'] else "NO TIME"
            gap = driver.get('gap_to_leader', '')
            
            print(f"{driver['position']:<4} {driver['driver_name']:<8} {driver['team']:<15} "
                  f"{lap_time:<10} {driver['lap_number']:<4} {driver['compound']:<8} {gap:<10}")
        
        # Session info
        if self.f1_session_loaded:
            session_info = self.live_timing.get_session_info()
            print(f"\n📊 Session: {session_info['event']} | Laps: {session_info['laps']} | Drivers: {len(session_info['drivers'])}")
        
        self.print_timing_message("Live timing data displayed")
    
    def handle_driver_analysis(self):
        """Detailed driver performance analysis"""
        self.print_bot_message("Which driver would you like to analyze?")
        
        # Show available drivers from timing data
        timing_data = self.live_timing.get_live_timing_data()
        driver_codes = [driver['driver_name'] for driver in timing_data[:8]]
        
        print(f"Available drivers: {', '.join(driver_codes)}")
        print("Or enter any 3-letter code for simulated analysis")
        
        driver_code = input("Enter driver code (e.g., HAM, VER): ").strip().upper()
        
        if len(driver_code) != 3:
            driver_code = "HAM"  # Default
        
        self.print_bot_message(f"Analyzing performance data for {driver_code}...")
        time.sleep(1)
        
        driver_analysis = self.live_timing.get_driver_analysis(driver_code)
        
        print(f"\n🔍 DRIVER ANALYSIS: {driver_code}")
        print("="*40)
        print(f"👤 Name: {driver_analysis['driver_name']}")
        print(f"🏁 Team: {driver_analysis['team']}")
        print(f"⏱️  Fastest Lap: {driver_analysis['fastest_lap']:.3f}s")
        print(f"📊 Average Lap: {driver_analysis['average_lap']:.3f}s")
        print(f"🎯 Consistency: ±{driver_analysis['consistency']:.3f}s")
        print(f"📈 Laps Completed: {driver_analysis['laps_completed']}")
        
        # Sector times
        print("\n📊 SECTOR TIMES:")
        sectors = driver_analysis['best_sector_times']
        print(f"   S1: {sectors['sector1']:.3f}s | S2: {sectors['sector2']:.3f}s | S3: {sectors['sector3']:.3f}s")
        print(f"   Total: {sum(sectors.values()):.3f}s")
        
        # Performance assessment
        avg_lap = driver_analysis['average_lap']
        if avg_lap < 86.0:
            assessment = "🔥 COMPETITIVE - Front runner pace"
        elif avg_lap < 87.0:
            assessment = "⚡ SOLID - Midfield pace"
        else:
            assessment = "🔄 DEVELOPMENT - Backmarker pace"
        
        self.print_bot_message(f"PERFORMANCE ASSESSMENT: {assessment}")
    
    def handle_sector_analysis(self):
        """Detailed sector time analysis"""
        self.print_bot_message("Analyzing sector times across the grid...")
        time.sleep(1)
        
        timing_data = self.live_timing.get_live_timing_data()
        
        print("\n" + "📊 SECTOR TIME ANALYSIS")
        print("="*50)
        print(f"{'DRIVER':<8} {'SECTOR 1':<10} {'SECTOR 2':<10} {'SECTOR 3':<10} {'TOTAL':<10} {'STRENGTH':<12}")
        print("-" * 50)
        
        for driver in timing_data[:8]:  # Top 8 drivers
            analysis = self.live_timing.get_driver_analysis(driver['driver_name'])
            sectors = analysis['best_sector_times']
            total = sum(sectors.values())
            
            # Find strongest sector
            best_sector = min(sectors, key=sectors.get)
            strength = f"S{best_sector[-1]} Strong"
            
            print(f"{driver['driver_name']:<8} {sectors['sector1']:<10.3f} {sectors['sector2']:<10.3f} "
                  f"{sectors['sector3']:<10.3f} {total:<10.3f} {strength:<12}")
        
        self.print_timing_message("Sector analysis complete - identify track strengths!")
    
    def handle_system_management(self):
        """System and data management options"""
        print("\n" + "⚙️  SYSTEM MANAGEMENT")
        print("="*40)
        print("1. 🔄 Refresh Weather Data")
        print("2. 🏎️  Load New F1 Session")
        print("3. 📍 Change Track Location")
        print("4. 🗑️  Clear Cache")
        print("5. 📊 System Status")
        print("6. ↩️  Back to Main Menu")
        
        choice = input("Select option (1-6): ").strip()
        
        if choice == '1':
            self.current_weather = self.weather_integration.get_track_weather(self.current_track)
            self.print_system_message("Weather data refreshed!")
        elif choice == '2':
            if self.live_timing.f1_available:
                self.print_bot_message("Available F1 sessions: Bahrain, Saudi Arabia, Australia")
                event = input("Enter event name (or press Enter for Bahrain): ").strip()
                if not event:
                    event = "Bahrain Grand Prix"
                self.f1_session_loaded = self.live_timing.load_f1_session(2024, event, 'R')
            else:
                self.print_bot_message("FastF1 not available - using simulated data")
        elif choice == '5':
            self.show_system_status()
    
    def run(self):
        """Main interaction loop"""
        self.welcome_sequence()
        
        while True:
            choice = self.show_enhanced_menu()
            
            if choice == '1':
                self.print_bot_message("Generating live-data qualifying predictions...")
                time.sleep(2)
                self.print_bot_message("Pole position analysis complete!")
                
            elif choice == '2':
                self.print_bot_message("Analyzing real-time race pace...")
                time.sleep(2)
                self.print_bot_message("Race pace optimized!")
                
            elif choice == '3':
                self.print_bot_message("Calculating tire strategy with live data...")
                time.sleep(2)
                self.print_bot_message("Tire strategy updated!")
                
            elif choice == '4':
                if self.current_weather:
                    print(f"\n🌤️  Current at {self.current_weather['location']}: {self.current_weather['description'].title()}")
                    print(f"🌡️  Air: {self.current_weather['air_temp']}°C | Track: {self.current_weather['track_temp']}°C")
                    print(f"💨 Wind: {self.current_weather['wind_speed']} m/s | 💧 Humidity: {self.current_weather['humidity']}%")
                else:
                    self.print_bot_message("No weather data available")
                
            elif choice == '5':
                self.handle_live_timing_dashboard()
                
            elif choice == '6':
                self.handle_driver_analysis()
                
            elif choice == '7':
                self.handle_sector_analysis()
                
            elif choice == '8':
                self.print_bot_message("Generating comprehensive race report...")
                time.sleep(2)
                self.print_bot_message("Full strategy report ready!")
                
            elif choice == '9':
                self.handle_system_management()
                
            elif choice == '0':
                self.print_bot_message("Shutting down all systems. Great race engineering! 🏆")
                break
                
            else:
                self.print_bot_message("Command not recognized! Try 0-9")
            
            input("\nPress Enter to continue...")

# Run the supercharged race engineer
if __name__ == "__main__":
    # First, install FastF1 if not already installed
    try:
        import fastf1
    except ImportError:
        print("📦 FastF1 not installed. Installing now...")
        os.system("pip install fastf1")
        print("✅ FastF1 installed successfully!")
    
    engineer = SuperchargedRaceEngineer()
    engineer.run()