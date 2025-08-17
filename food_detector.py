#!/usr/bin/env python3
"""
Food Detection Script for UQ Events

This script analyzes event titles and descriptions to detect if food/drinks are provided.
It reads events from free_events.json, uses OpenAI API to analyze each event,
and updates the JSON file with a "has_food" boolean field.

Usage: python food_detector.py
"""

import json
import os
import yaml
import logging
from openai import OpenAI
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FoodDetector:
    def __init__(self, config_path: str = "uqlink.yml", events_path: str = "event_data.json"):
        """
        Initialize the FoodDetector with configuration and events file paths.
        
        Args:
            config_path: Path to YAML config file containing OpenAI API key
            events_path: Path to JSON file containing events data
        """
        self.config_path = config_path
        self.events_path = events_path
        self.client = None
        self._load_config()
        
    def _load_config(self):
        """Load configuration from YAML file and initialize OpenAI client."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            api_key = config.get('ai_api')
            if not api_key:
                raise ValueError("No 'ai_api' key found in config file")
            
                
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
            
        except FileNotFoundError:
            logger.error(f"Config file {self.config_path} not found")
            raise
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def _analyze_event_for_food(self, event: Dict[str, Any]) -> bool:
        """
        Analyze a single event to determine if it offers food/drinks.
        
        Args:
            event: Event dictionary containing title and other details
            
        Returns:
            bool: True if event likely offers food/drinks, False otherwise
        """
        # Extract relevant text from event
        title = event.get('title', '')
        subtitle = event.get('subtitle', '')
        society_name = event.get('societyname', '')
        
        # Combine text for analysis
        event_text = f"{title} {subtitle} {society_name}".strip()
        
        if not event_text:
            logger.warning("Empty event text, defaulting to False")
            return False
        
        # Create concise prompt for OpenAI
        prompt = f"Does this event offer free food or drinks to attendees? Event: {event_text[:200]}. Answer only 'true' or 'false'."
        
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that determines if events offer food or drinks. Answer only 'true' or 'false'."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0
            )
            
            answer = response.choices[0].message.content.strip().lower()
            
            # Parse response strictly
            if answer == 'true':
                return True
            elif answer == 'false':
                return False
            else:
                logger.warning(f"Unexpected OpenAI response: {answer}, defaulting to False")
                return False
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return False
    
    def load_events(self) -> tuple:
        """
        Load events from JSON file.
        
        Returns:
            Tuple of (full_data_dict, events_list)
        """
        try:
            with open(self.events_path, 'r') as f:
                full_data = json.load(f)
            
            # Extract events from results array
            if isinstance(full_data, dict) and 'results' in full_data:
                events = full_data['results']
            else:
                logger.error("Events data does not contain 'results' array")
                return {}, []
                
            logger.info(f"Loaded {len(events)} events from {self.events_path}")
            return full_data, events
            
        except FileNotFoundError:
            logger.error(f"Events file {self.events_path} not found")
            return {}, []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from {self.events_path}: {e}")
            return {}, []
        except Exception as e:
            logger.error(f"Error loading events: {e}")
            return {}, []
    
    def save_events(self, full_data: Dict[str, Any], events: List[Dict[str, Any]]):
        """
        Save events back to JSON file, preserving the full data structure.
        
        Args:
            full_data: Complete data dictionary containing all metadata
            events: List of updated event dictionaries
        """
        try:
            # Create backup
            backup_path = f"{self.events_path}.backup"
            if os.path.exists(self.events_path):
                with open(self.events_path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
                logger.info(f"Created backup at {backup_path}")
            
            # Update the results array in the full data structure
            full_data['results'] = events
            
            # Save updated full data
            with open(self.events_path, 'w') as f:
                json.dump(full_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(events)} events to {self.events_path}")
            
        except Exception as e:
            logger.error(f"Error saving events: {e}")
            raise
    
    def process_events(self):
        """
        Main processing function: load events, analyze for food, and save results.
        """
        logger.info("Starting food detection process...")
        
        # Load events
        full_data, events = self.load_events()
        if not events:
            logger.error("No events to process")
            return
        
        # Process each event
        food_count = 0
        processed_count = 0
        
        for i, event in enumerate(events):
            try:
                # Check if already processed with boolean free_food field
                if 'free_food' in event and isinstance(event['free_food'], bool):
                    print("working")
                    logger.debug(f"Event {i+1} already processed, skipping")
                    if event['free_food']:
                        food_count += 1
                    processed_count += 1
                    continue
                
                # Analyze event for food
                has_food = self._analyze_event_for_food(event)
                event['free_food'] = has_food  # Use boolean instead of string
                
                if has_food:
                    food_count += 1
                    logger.info(f"Event {i+1}/{len(events)}: '{event.get('title', 'Unknown')}' - HAS FOOD")
                else:
                    logger.debug(f"Event {i+1}/{len(events)}: '{event.get('title', 'Unknown')}' - no food")
                
                processed_count += 1
                
                # Progress update every 10 events
                if processed_count % 10 == 0:
                    logger.info(f"Processed {processed_count}/{len(events)} events...")
                    
            except Exception as e:
                logger.error(f"Error processing event {i+1}: {e}")
                # Set default value on error
                event['free_food'] = False
                processed_count += 1
        
        # Save results
        self.save_events(full_data, events)
        
        # Summary
        logger.info(f"Food detection complete!")
        logger.info(f"Total events: {len(events)}")
        logger.info(f"Events with food: {food_count}")
        logger.info(f"Events without food: {len(events) - food_count}")


def main():
    """Main entry point for the script."""
    try:
        # Initialize detector
        detector = FoodDetector()
        
        # Process events
        detector.process_events()
        
        print("Food detection completed successfully!")
        print("Check the logs above for detailed results.")
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
