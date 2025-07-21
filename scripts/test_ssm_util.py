#!/usr/bin/env python3
"""
Test script for SSM utility functionality.
This script tests the SSM parameter reading and logging functionality.
"""

import sys
import os
import structlog
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shared.config.settings import get_settings
from shared.utils.ssm_utils import get_api_key_from_ssm, SSMClient


def test_ssm_utility():
    """Test the SSM utility functionality."""
    
    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    logger = structlog.get_logger(__name__)
    logger.info("Starting SSM utility test")
    
    try:
        # Get settings
        settings = get_settings()
        logger.info(f"Configuration loaded - STAGE: {settings.STAGE}, LOG_LEVEL: {settings.LOG_LEVEL}")
        logger.info(f"API_KEY_PARAM configured as: {settings.API_KEY_PARAM}")
        
        # Test SSM client initialization
        logger.info("Testing SSM client initialization...")
        ssm_client = SSMClient()
        logger.info("SSM client initialized successfully")
        
        # Test parameter retrieval
        logger.info("Testing parameter retrieval...")
        api_key = get_api_key_from_ssm(settings.API_KEY_PARAM)
        logger.info(f"✅ SUCCESS: API key retrieved from SSM parameter: {settings.API_KEY_PARAM}")
        logger.info(f"✅ API key value: {api_key}")  # ⚠️ WARNING: Don't log secrets in production!
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR: Failed to test SSM utility: {e}")
        return False


def test_with_custom_parameter():
    """Test with a custom parameter name."""
    logger = structlog.get_logger(__name__)
    
    try:
        # Test with custom parameter name
        custom_param = "/pos-h/test-api-key"
        logger.info(f"Testing with custom parameter: {custom_param}")
        
        api_key = get_api_key_from_ssm(custom_param)
        logger.info(f"✅ SUCCESS: Custom parameter retrieved: {custom_param}")
        logger.info(f"✅ Custom parameter value: {api_key}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR: Failed to test custom parameter: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing SSM Utility")
    print("=" * 50)
    
    # Test 1: Default parameter
    print("\n📋 Test 1: Default API_KEY_PARAM")
    success1 = test_ssm_utility()
    
    # Test 2: Custom parameter
    print("\n📋 Test 2: Custom parameter")
    success2 = test_with_custom_parameter()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1) 