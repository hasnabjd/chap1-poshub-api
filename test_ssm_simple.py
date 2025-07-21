#!/usr/bin/env python3
"""
Simple test to verify SSM functionality and see logs.
"""

import sys
import structlog
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from shared.config.settings import get_settings
from shared.utils.ssm_utils import get_api_key_from_ssm


def main():
    """Simple test of SSM functionality."""
    
    # Configure basic logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),  # Use JSON renderer for better visibility
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    logger = structlog.get_logger(__name__)
    
    print("🧪 Testing SSM Utility - Simple Version")
    print("=" * 50)
    
    try:
        # Get settings
        settings = get_settings()
        print(f"📋 Configuration:")
        print(f"   STAGE: {settings.STAGE}")
        print(f"   LOG_LEVEL: {settings.LOG_LEVEL}")
        print(f"   API_KEY_PARAM: {settings.API_KEY_PARAM}")
        
        # Test SSM
        print(f"\n🔍 Testing SSM parameter retrieval...")
        api_key = get_api_key_from_ssm(settings.API_KEY_PARAM)
        
        print(f"✅ SUCCESS!")
        print(f"   Parameter: {settings.API_KEY_PARAM}")
        print(f"   Value: {api_key}")
        
        # Also log with structlog
        logger.info("SSM test successful", 
                   parameter=settings.API_KEY_PARAM, 
                   value=api_key)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.error("SSM test failed", error=str(e))
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1) 