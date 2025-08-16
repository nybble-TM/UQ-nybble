#!/usr/bin/env python3
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
        self.config_path = config_path
        self.events_path = events_path
        self.client = None
        self._load_config()
        
    def _load_config(self):
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
        
        title = event.get('title', '')
        subtitle = event.get('subtitle', '')
        society_name = event.get('societyname', '')
        
       
        event_text = f"{title} {subtitle} {society_name}".strip()
        
        if not event_text:
            logger.warning("Empty event text, defaulting to False")
            return False
        
        
        prompt = f"Does this event offer free food or drinks to attendees? Event: {event_text[:200]}. Answer only 'true' or 'false'."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
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
        try:
            # Create backup
            backup_path = f"{self.events_path}.backup"
            if os.path.exists(self.events_path):
                with open(self.events_path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
                logger.info(f"Created backup at {backup_path}")
            
            
            full_data['results'] = events
            
            # Save updated full data
            with open(self.events_path, 'w') as f:
                json.dump(full_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(events)} events to {self.events_path}")
            
        except Exception as e:
            logger.error(f"Error saving events: {e}")
            raise
    
    def process_events(self):
        logger.info("Starting food detection process...")
        
       
        full_data, events = self.load_events()
        if not events:
            logger.error("No events to process")
            return
        
        # Process each event
        food_count = 0
        processed_count = 0
        
        for i, event in enumerate(events):
            try:
            
                if 'free_food' in event and isinstance(event['free_food'], bool):
                    logger.debug(f"Event {i+1} already processed, skipping")
                    if event['free_food']:
                        food_count += 1
                    processed_count += 1
                    continue
                
                
                has_food = self._analyze_event_for_food(event)
                event['free_food'] = has_food  # Use boolean instead of string
                
                if has_food:
                    food_count += 1
                    logger.info(f"Event {i+1}/{len(events)}: '{event.get('title', 'Unknown')}' - HAS FOOD")
                else:
                    logger.debug(f"Event {i+1}/{len(events)}: '{event.get('title', 'Unknown')}' - no food")
                
                processed_count += 1
                
            
                if processed_count % 10 == 0:
                    logger.info(f"Processed {processed_count}/{len(events)} events...")
                    
            except Exception as e:
                logger.error(f"Error processing event {i+1}: {e}")
                
                event['free_food'] = False
                processed_count += 1
        
        # Savethose fricking results
        self.save_events(full_data, events)
        
        # Summary
        logger.info(f"Food detection complete!")
        logger.info(f"Total events: {len(events)}")
        logger.info(f"Events with food: {food_count}")
        logger.info(f"Events without food: {len(events) - food_count}")


def main():
    """Main entry point for the script."""
    try:
        detector = FoodDetector()
    
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
