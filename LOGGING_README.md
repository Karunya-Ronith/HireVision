# HireVision Logging System

This document describes the comprehensive logging system implemented throughout the HireVision application.

## Overview

The logging system provides detailed tracking of all application activities, including:
- User actions and authentication
- API calls and responses
- File operations
- Performance metrics
- Error tracking and debugging
- Function execution flow

## Architecture

### Core Components

1. **`logging_config.py`** - Central logging configuration and utilities
2. **Module-specific loggers** - Individual loggers for each major component
3. **Django logging integration** - Django-specific logging configuration
4. **Rotating file handlers** - Automatic log file rotation and management

### Log Levels

- **DEBUG** - Detailed information for debugging
- **INFO** - General information about application flow
- **WARNING** - Warning messages for potential issues
- **ERROR** - Error messages for failed operations
- **CRITICAL** - Critical errors that may cause application failure

## Log Files Structure

```
logs/
├── django.log                    # Django framework logs
├── hirevision.log               # Main application logs
├── resume_analyzer.log          # Resume analysis module logs
├── resume_analyzer_errors.log   # Resume analysis errors
├── learning_path_analyzer.log   # Learning path module logs
├── learning_path_analyzer_errors.log # Learning path errors
├── resume_builder.log           # Resume builder module logs
├── resume_builder_errors.log    # Resume builder errors
├── pdf_generator.log            # PDF generation logs
├── pdf_generator_errors.log     # PDF generation errors
├── utils.log                    # Utility functions logs
├── utils_errors.log             # Utility function errors
├── views.log                    # Django views logs
├── views_errors.log             # Django views errors
├── tasks.log                    # Background task logs
├── tasks_errors.log             # Background task errors
├── api_calls.log                # API call logs
├── user_actions.log             # User action audit logs
├── file_operations.log          # File operation logs
└── performance.log              # Performance metrics logs
```

## Key Features

### 1. Function Call Logging

Automatically log function entry, parameters, and exit with the `@log_function_call` decorator:

```python
from logging_config import log_function_call

@log_function_call
def my_function(param1, param2):
    # Function logic here
    return result
```

### 2. API Call Logging

Track API calls with request/response data (sensitive data automatically filtered):

```python
from logging_config import log_api_call

log_api_call(
    api_name="OpenAI Chat Completions",
    request_data={"model": "gpt-4", "temperature": 0.3},
    response_data={"response_length": 1500},
    success=True
)
```

### 3. User Action Logging

Audit trail for user actions:

```python
from logging_config import log_user_action

log_user_action(
    user_id="123",
    action="upload_resume",
    details="Uploaded resume.pdf",
    success=True
)
```

### 4. File Operation Logging

Track file operations with size and error information:

```python
from logging_config import log_file_operation

log_file_operation(
    operation="upload",
    file_path="resumes/user_resume.pdf",
    success=True,
    file_size=1024000
)
```

### 5. Performance Logging

Monitor operation performance:

```python
from logging_config import log_performance

log_performance(
    operation="resume_analysis",
    duration=2.5,
    details="Processed 1500 characters"
)
```

## Module-Specific Logging

### Resume Analyzer (`resume_analyzer.py`)

- PDF text extraction process
- OpenAI API calls and responses
- Analysis result processing
- Error handling and fallbacks

### Learning Path Analyzer (`learning_path_analyzer.py`)

- Learning path generation
- Skills gap analysis
- Resource recommendation tracking
- API call monitoring

### Resume Builder (`resume_builder.py`)

- LaTeX generation process
- PDF creation tracking
- Data validation logging
- Error handling

### PDF Generator (`pdf_generator.py`)

- PDF compilation process
- Alternative generation methods
- File system operations
- Performance metrics

### Utils (`utils.py`)

- Input validation
- JSON extraction
- Error handling
- Performance tracking

### Django Views (`views.py`)

- User authentication
- Form processing
- Permission checks
- Page rendering

### Background Tasks (`tasks.py`)

- Task execution flow
- Status updates
- Error handling
- Performance monitoring

## Configuration

### Log Level Configuration

Set the log level in `logging_config.py`:

```python
LOG_LEVEL = logging.INFO  # Change to DEBUG for more detailed logs
```

### File Rotation

Log files automatically rotate when they reach 10MB and keep 5 backup files:

```python
file_handler = logging.handlers.RotatingFileHandler(
    file_path,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
```

### Django Integration

Django logging is configured in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024*1024*10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## Usage Examples

### Basic Logger Usage

```python
from logging_config import get_logger

logger = get_logger(__name__)

logger.info("Application started")
logger.debug("Processing user input")
logger.warning("API rate limit approaching")
logger.error("Failed to process request", exc_info=True)
```

### Performance Monitoring

```python
import time
from logging_config import log_performance

start_time = time.time()
# ... perform operation ...
duration = time.time() - start_time
log_performance("operation_name", duration, "Additional details")
```

### Error Tracking

```python
from logging_config import get_logger

logger = get_logger(__name__)

try:
    # ... risky operation ...
    pass
except Exception as e:
    logger.error(f"Operation failed: {str(e)}", exc_info=True)
    # Handle error appropriately
```

## Testing

Run the logging test script to verify all components:

```bash
python test_logging.py
```

This will test:
- Logger creation
- Function call logging
- API call logging
- User action logging
- File operation logging
- Performance logging
- Module-specific loggers

## Monitoring and Maintenance

### Log Analysis

Use standard Unix tools to analyze logs:

```bash
# View recent errors
grep "ERROR" logs/*.log | tail -20

# Monitor API calls
tail -f logs/api_calls.log

# Check performance
grep "Performance" logs/performance.log

# User activity
tail -f logs/user_actions.log
```

### Log Rotation

Log files automatically rotate when they reach 10MB. Old logs are kept for reference but don't consume excessive disk space.

### Disk Space Monitoring

Monitor the `logs/` directory size:

```bash
du -sh logs/
```

### Log Cleanup

To clean old logs (optional):

```bash
# Remove logs older than 30 days
find logs/ -name "*.log*" -mtime +30 -delete
```

## Security Considerations

### Sensitive Data Filtering

The logging system automatically filters sensitive information:
- API keys
- Passwords
- Tokens
- Secrets

### Audit Trail

User actions are logged for security auditing:
- Login/logout events
- File uploads/downloads
- Data access attempts
- Permission violations

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure the `logs/` directory is writable
2. **Disk Space**: Monitor log file sizes and implement cleanup
3. **Performance Impact**: Adjust log levels for production environments

### Debug Mode

Enable debug logging for troubleshooting:

```python
LOG_LEVEL = logging.DEBUG
```

### Log File Locations

All log files are stored in the `logs/` directory relative to the project root.

## Best Practices

1. **Use appropriate log levels** - Don't log everything as INFO
2. **Include context** - Add relevant details to log messages
3. **Handle exceptions properly** - Use `exc_info=True` for error logging
4. **Monitor log sizes** - Implement log rotation and cleanup
5. **Secure sensitive data** - Never log passwords or API keys
6. **Use structured logging** - Include relevant metadata in log messages

## Integration with Monitoring Tools

The logging system can be integrated with external monitoring tools:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Datadog**
- **New Relic**
- **AWS CloudWatch**

Configure your monitoring tool to read from the `logs/` directory for centralized log management. 