# UQ Events Food Detection System

A comprehensive system for analyzing and displaying University of Queensland events with automatic food detection capabilities. The system processes **all events** (both free and paid) and uses AI to identify which events provide free food or drinks.

## Features

- **Complete Event Coverage**: Analyzes all events from the UQ events database, not just free events
- **AI-Powered Food Detection**: Uses OpenAI GPT-3.5-turbo to intelligently detect food offerings in event descriptions
- **Web Interface**: Clean, responsive web interface to browse all events with food indicators
- **Multiple Views**: 
  - All events with food badges
  - Food-only events filter
  - Statistics dashboard
- **Automatic Processing**: Batch processing of events with progress tracking and error handling

## System Architecture

### Core Components

1. **`food_detector.py`**: AI-powered food detection engine
   - Loads all events from `event_data.json`
   - Analyzes event titles, subtitles, and society names using OpenAI API
   - Adds boolean `free_food` field to each event
   - Preserves original JSON structure and metadata

2. **`app.py`**: Flask web application
   - Displays all events with food indicators
   - Provides filtering and statistics
   - Responsive design with event cards

3. **`templates/events_cards.html`**: Web interface template
   - Modern card-based layout
   - Food badges for events with detected food
   - Navigation between different views

## Data Structure

The system works with `event_data.json` which contains:

```json
{
  "results": [
    {
      "title": "Event Title",
      "subtitle": "Event Type",
      "societyname": "Society Name",
      "info": "Free" or "$X.XX",
      "free_food": true/false,  // Added by food detector
      // ... other event fields
    }
  ],
  // ... other metadata
}
```

## Installation

1. **Install Dependencies**:
   ```bash
   pip install flask openai pyyaml
   ```

2. **Configure OpenAI API**:
   Create `uqlink.yml` with your OpenAI API key:
   ```yaml
   ai_api: "your-openai-api-key-here"
   ```

3. **Ensure Data File**:
   Make sure `event_data.json` exists with the proper structure containing a `results` array.

## Usage

### Food Detection

Run the food detection analysis on all events:

```bash
python food_detector.py
```

This will:
- Load all events from `event_data.json`
- Analyze each event for food offerings using AI
- Add/update the `free_food` boolean field
- Save results back to the same file
- Create a backup file automatically

### Web Application

Start the Flask web server:

```bash
python app.py
```

Then visit:
- `http://localhost:5000/` - All events with food indicators
- `http://localhost:5000/food-events` - Only events with free food
- `http://localhost:5000/stats` - Statistics dashboard

## Food Detection Logic

The AI system analyzes:
- **Event titles**: Looking for food-related keywords
- **Event subtitles**: Checking event types (BBQ, social, etc.)
- **Society names**: Identifying food-focused organizations

Common food indicators detected:
- Pizza nights, BBQ events, coffee meetups
- Social events with catering mentions
- Society events known for providing food
- Workshop/seminar lunch provisions

## Configuration

### OpenAI Settings
- **Model**: GPT-3.5-turbo (cost-effective and reliable)
- **Temperature**: 0 (deterministic responses)
- **Max Tokens**: 10 (simple true/false responses)

### Logging
- Comprehensive logging for debugging and monitoring
- Progress tracking for batch processing
- Error handling with graceful degradation

## File Structure

```
/home/ubuntu/Uploads/
├── food_detector.py      # AI food detection engine
├── app.py               # Flask web application
├── event_data.json      # Main events database
├── uqlink.yml          # Configuration file (API keys)
├── requirements.txt     # Python dependencies
├── templates/
│   └── events_cards.html # Web interface template
└── README.md           # This file
```

## API Usage

The food detection system can be integrated into other applications:

```python
from food_detector import FoodDetector

# Initialize detector
detector = FoodDetector()

# Process all events
detector.process_events()
```

## Statistics

The system provides comprehensive statistics:
- Total events processed
- Events with/without food
- Free vs paid events breakdown
- Processing success rates

## Error Handling

- **Backup Creation**: Automatic backup before processing
- **Graceful Degradation**: Continues processing if individual events fail
- **API Rate Limiting**: Handles OpenAI API limits gracefully
- **Data Validation**: Ensures JSON integrity throughout processing

## Security Notes

- API keys are stored in separate configuration files
- No sensitive data is logged or exposed
- Input validation prevents injection attacks
- Backup system prevents data loss

## Contributing

When modifying the system:

1. **Test thoroughly** with sample data before processing full dataset
2. **Backup data** before making changes
3. **Update documentation** for any new features
4. **Follow logging conventions** for debugging support

## Troubleshooting

### Common Issues

1. **"No events found"**: Check that `event_data.json` exists and has a `results` array
2. **OpenAI API errors**: Verify API key in `uqlink.yml` and check rate limits
3. **Template not found**: Ensure `templates/` directory exists with `events_cards.html`
4. **JSON parsing errors**: Validate JSON structure after manual edits

### Debug Mode

Run Flask in debug mode for detailed error messages:
```bash
python app.py
```

### Logs

Check console output for detailed processing information and error messages.

## License

This project is for educational and research purposes. Not affiliated with University of Queensland.

## Disclaimer

Food information is detected automatically using AI and may not be 100% accurate. Always verify with event organizers before attending events specifically for food offerings.
