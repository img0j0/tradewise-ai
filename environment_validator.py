"""
Environment Variables Validator for TradeWise AI
Validates all required environment variables at startup
"""

import os
import sys
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class EnvironmentVariable:
    name: str
    required: bool
    description: str
    validation_func: Optional[callable] = None
    default_value: Optional[str] = None

class EnvironmentValidator:
    """Validates environment variables and provides startup health checks"""
    
    def __init__(self):
        self.required_vars = self._define_environment_variables()
        self.validation_errors = []
        self.validation_warnings = []
    
    def _define_environment_variables(self) -> List[EnvironmentVariable]:
        """Define all environment variables with validation rules"""
        return [
            # Critical Required Variables
            EnvironmentVariable(
                name="DATABASE_URL",
                required=True,
                description="PostgreSQL database connection URL",
                validation_func=self._validate_database_url
            ),
            EnvironmentVariable(
                name="SESSION_SECRET",
                required=True,
                description="Secret key for session encryption (min 32 chars)",
                validation_func=self._validate_session_secret
            ),
            EnvironmentVariable(
                name="STRIPE_SECRET_KEY",
                required=True,
                description="Stripe API secret key for payment processing",
                validation_func=self._validate_stripe_key
            ),
            
            # Optional but Important Variables
            EnvironmentVariable(
                name="REDIS_URL",
                required=False,
                description="Redis connection URL for async task queue",
                default_value="redis://localhost:6379/0",
                validation_func=self._validate_redis_url
            ),
            EnvironmentVariable(
                name="ENVIRONMENT",
                required=False,
                description="Environment type (development, staging, production)",
                default_value="development",
                validation_func=self._validate_environment_type
            ),
            
            # Notification Variables
            EnvironmentVariable(
                name="ERROR_NOTIFICATIONS_ENABLED",
                required=False,
                description="Enable critical error notifications",
                default_value="false"
            ),
            EnvironmentVariable(
                name="SLACK_ERROR_WEBHOOK",
                required=False,
                description="Slack webhook for error notifications"
            ),
            EnvironmentVariable(
                name="SMTP_SERVER",
                required=False,
                description="SMTP server for email notifications"
            ),
            
            # Performance Configuration
            EnvironmentVariable(
                name="ASYNC_WORKER_COUNT",
                required=False,
                description="Number of async workers",
                default_value="3",
                validation_func=self._validate_worker_count
            ),
            EnvironmentVariable(
                name="LOG_LEVEL",
                required=False,
                description="Logging level (DEBUG, INFO, WARNING, ERROR)",
                default_value="INFO",
                validation_func=self._validate_log_level
            ),
            
            # Feature Flags
            EnvironmentVariable(
                name="PREMIUM_FEATURES_ENABLED",
                required=False,
                description="Enable premium features",
                default_value="true"
            ),
            EnvironmentVariable(
                name="ADVANCED_ANALYTICS_ENABLED",
                required=False,
                description="Enable advanced analytics",
                default_value="true"
            )
        ]
    
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Validate all environment variables"""
        self.validation_errors = []
        self.validation_warnings = []
        
        for env_var in self.required_vars:
            value = os.getenv(env_var.name)
            
            # Check if required variable is missing
            if env_var.required and not value:
                self.validation_errors.append(
                    f"CRITICAL: {env_var.name} is required but not set. {env_var.description}"
                )
                continue
            
            # Set default value if not provided
            if not value and env_var.default_value:
                os.environ[env_var.name] = env_var.default_value
                value = env_var.default_value
                self.validation_warnings.append(
                    f"Using default value for {env_var.name}: {env_var.default_value}"
                )
            
            # Run custom validation if function provided
            if value and env_var.validation_func:
                try:
                    is_valid, error_msg = env_var.validation_func(value)
                    if not is_valid:
                        if env_var.required:
                            self.validation_errors.append(f"INVALID {env_var.name}: {error_msg}")
                        else:
                            self.validation_warnings.append(f"WARNING {env_var.name}: {error_msg}")
                except Exception as e:
                    self.validation_warnings.append(
                        f"Validation error for {env_var.name}: {str(e)}"
                    )
        
        is_valid = len(self.validation_errors) == 0
        return is_valid, self.validation_errors, self.validation_warnings
    
    def _validate_database_url(self, value: str) -> Tuple[bool, str]:
        """Validate database URL format"""
        if not value.startswith(('postgresql://', 'postgres://')):
            return False, "Must be a PostgreSQL URL (postgresql:// or postgres://)"
        if 'localhost' in value and os.getenv('ENVIRONMENT') == 'production':
            return False, "Production should not use localhost database"
        return True, ""
    
    def _validate_session_secret(self, value: str) -> Tuple[bool, str]:
        """Validate session secret strength"""
        if len(value) < 32:
            return False, "Session secret must be at least 32 characters long"
        if value in ['your-secret-session-key-here', 'change-me']:
            return False, "Session secret must be changed from default value"
        return True, ""
    
    def _validate_stripe_key(self, value: str) -> Tuple[bool, str]:
        """Validate Stripe API key format"""
        if not value.startswith(('sk_test_', 'sk_live_')):
            return False, "Must be a valid Stripe secret key (sk_test_ or sk_live_)"
        if 'your_stripe_secret_key' in value:
            return False, "Stripe key must be changed from placeholder value"
        return True, ""
    
    def _validate_redis_url(self, value: str) -> Tuple[bool, str]:
        """Validate Redis URL format"""
        if not value.startswith('redis://'):
            return False, "Must be a valid Redis URL (redis://)"
        return True, ""
    
    def _validate_environment_type(self, value: str) -> Tuple[bool, str]:
        """Validate environment type"""
        valid_environments = ['development', 'staging', 'production']
        if value.lower() not in valid_environments:
            return False, f"Must be one of: {', '.join(valid_environments)}"
        return True, ""
    
    def _validate_worker_count(self, value: str) -> Tuple[bool, str]:
        """Validate async worker count"""
        try:
            count = int(value)
            if count < 1 or count > 20:
                return False, "Worker count must be between 1 and 20"
            return True, ""
        except ValueError:
            return False, "Must be a valid integer"
    
    def _validate_log_level(self, value: str) -> Tuple[bool, str]:
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        if value.upper() not in valid_levels:
            return False, f"Must be one of: {', '.join(valid_levels)}"
        return True, ""
    
    def print_validation_results(self, is_valid: bool, errors: List[str], warnings: List[str]):
        """Print formatted validation results"""
        print("\n" + "=" * 60)
        print("🔍 TradeWise AI Environment Validation")
        print("=" * 60)
        
        if is_valid:
            print("✅ Environment validation PASSED")
        else:
            print("❌ Environment validation FAILED")
        
        if errors:
            print(f"\n🚨 CRITICAL ERRORS ({len(errors)}):")
            for error in errors:
                print(f"  • {error}")
        
        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for warning in warnings:
                print(f"  • {warning}")
        
        if is_valid:
            print(f"\n🎯 Environment Status: READY FOR STARTUP")
        else:
            print(f"\n🛑 Environment Status: STARTUP BLOCKED")
            print("Fix critical errors before proceeding.")
        
        print("=" * 60)

def validate_environment_startup() -> bool:
    """Main function to validate environment at startup"""
    validator = EnvironmentValidator()
    is_valid, errors, warnings = validator.validate_all()
    validator.print_validation_results(is_valid, errors, warnings)
    
    # Log validation results
    if errors:
        for error in errors:
            logger.error(error)
    if warnings:
        for warning in warnings:
            logger.warning(warning)
    
    return is_valid

if __name__ == "__main__":
    # Standalone validation
    is_valid = validate_environment_startup()
    if not is_valid:
        sys.exit(1)
    else:
        print("Environment validation successful!")