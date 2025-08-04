from django.apps import AppConfig
from logging_config import get_logger

# Initialize logger for app config
logger = get_logger('apps')


class HirevisionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hirevision"
    
    def ready(self):
        """Called when the app is ready"""
        logger.info("HireVision app is ready and initialized")
        logger.debug(f"App name: {self.name}")
        logger.debug(f"Default auto field: {self.default_auto_field}")
        
        # Log app configuration details
        logger.info("HireVision app configuration:")
        logger.info("- Resume Analysis functionality")
        logger.info("- Learning Path Analysis functionality") 
        logger.info("- Resume Builder functionality")
        logger.info("- Thread and Comment system")
        logger.info("- Messaging system")
        logger.info("- User management and authentication")
        
        logger.info("HireVision app ready for use")
