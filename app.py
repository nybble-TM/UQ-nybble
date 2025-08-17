#!/usr/bin/env python3
"""
Flask Web Application for UQ Events with Food Detection

This application displays all events (both free and paid) from event_data.json
and shows food indicators for events that have been analyzed by the food detector.

Usage: python app.py
"""

import json
import logging
from flask import Flask, render_template
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def load_events() -> List[Dict[str, Any]]:
    """
    Load events from event_data.json file.
    
    Returns:
        List of event dictionaries from the results array
    """
    try:
        with open('event_data.json', 'r') as f:
            data = json.load(f)
        
        # Extract events from results array
        if isinstance(data, dict) and 'results' in data:
            events = data['results']
            logger.info(f"Loaded {len(events)} events from event_data.json")
            return events
        else:
            logger.error("No 'results' array found in event_data.json")
            return []
            
    except FileNotFoundError:
        logger.error("event_data.json file not found")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading events: {e}")
        return []

@app.route('/')
def index():
    """
    Main route that displays all events with food indicators.
    """
    try:
        # Load all events
        events = load_events()
        
        if not events:
            logger.warning("No events found to display")
            return render_template('events_cards.html', events=[])
        
        # Filter events with food for statistics
        events_with_food = [e for e in events if e.get('free_food') is True]
        
        logger.info(f"Displaying {len(events)} total events")
        logger.info(f"Found {len(events_with_food)} events with free food")
        
        return render_template('events_cards.html', 
                             events=events,
                             events_with_food_count=len(events_with_food))
        
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return f"Error loading events: {e}", 500

@app.route('/food-events')
def food_events():
    """
    Route that displays only events with free food.
    """
    try:
        # Load all events
        all_events = load_events()
        
        # Filter for events with free food
        food_events = [e for e in all_events if e.get('free_food') is True]
        
        logger.info(f"Displaying {len(food_events)} events with free food")
        
        return render_template('events_cards.html', 
                             events=food_events,
                             events_with_food_count=len(food_events),
                             food_only=True)
        
    except Exception as e:
        logger.error(f"Error in food_events route: {e}")
        return f"Error loading food events: {e}", 500

@app.route('/stats')
def stats():
    """
    Route that displays statistics about events and food detection.
    """
    try:
        events = load_events()
        
        if not events:
            return "No events found", 404
        
        # Calculate statistics
        total_events = len(events)
        events_with_food = len([e for e in events if e.get('free_food') is True])
        events_without_food = len([e for e in events if e.get('free_food') is False])
        events_not_analyzed = len([e for e in events if 'free_food' not in e or not isinstance(e.get('free_food'), bool)])
        
        free_events = len([e for e in events if e.get('info', '').lower().startswith('free')])
        paid_events = total_events - free_events
        
        stats_data = {
            'total_events': total_events,
            'events_with_food': events_with_food,
            'events_without_food': events_without_food,
            'events_not_analyzed': events_not_analyzed,
            'free_events': free_events,
            'paid_events': paid_events,
            'food_percentage': round((events_with_food / total_events * 100), 1) if total_events > 0 else 0
        }
        
        return f"""
        <h1>UQ Events Statistics</h1>
        <ul>
            <li><strong>Total Events:</strong> {stats_data['total_events']}</li>
            <li><strong>Events with Free Food:</strong> {stats_data['events_with_food']} ({stats_data['food_percentage']}%)</li>
            <li><strong>Events without Food:</strong> {stats_data['events_without_food']}</li>
            <li><strong>Events Not Analyzed:</strong> {stats_data['events_not_analyzed']}</li>
            <li><strong>Free Events:</strong> {stats_data['free_events']}</li>
            <li><strong>Paid Events:</strong> {stats_data['paid_events']}</li>
        </ul>
        <p><a href="/">← Back to Events</a></p>
        """
        
    except Exception as e:
        logger.error(f"Error in stats route: {e}")
        return f"Error loading statistics: {e}", 500

if __name__ == '__main__':
    logger.info("Starting UQ Events Flask application...")
    logger.info("Available routes:")
    logger.info("  / - All events with food indicators")
    logger.info("  /food-events - Only events with free food")
    logger.info("  /stats - Event statistics")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
