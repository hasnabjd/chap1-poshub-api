#!/usr/bin/env python3
"""
Script to create SSM parameters for testing.
This script creates the required SSM parameters for testing the SSM utility.
"""

import boto3
import sys
from botocore.exceptions import ClientError


def create_ssm_parameter(parameter_name: str, parameter_value: str, parameter_type: str = "String"):
    """Create an SSM parameter."""
    try:
        ssm_client = boto3.client('ssm')
        
        response = ssm_client.put_parameter(
            Name=parameter_name,
            Value=parameter_value,
            Type=parameter_type,
            Overwrite=True  # Overwrite if parameter already exists
        )
        
        print(f"✅ SUCCESS: Created SSM parameter '{parameter_name}'")
        print(f"   Version: {response['Version']}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            print(f"❌ ERROR: Access denied. Make sure you have permissions to create SSM parameters.")
        else:
            print(f"❌ ERROR: Failed to create parameter '{parameter_name}': {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {e}")
        return False


def main():
    """Main function to create test SSM parameters."""
    print("🔧 Creating SSM Parameters for Testing")
    print("=" * 50)
    
    # Parameters to create
    parameters = [
        {
            "name": "/pos-h/api-key",
            "value": "test-api-key-value-12345",
            "type": "String"
        },
        {
            "name": "/pos-h/test-api-key", 
            "value": "test-custom-api-key-67890",
            "type": "String"
        }
    ]
    
    success_count = 0
    
    for param in parameters:
        print(f"\n📋 Creating parameter: {param['name']}")
        success = create_ssm_parameter(
            param['name'], 
            param['value'], 
            param['type']
        )
        if success:
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {success_count}/{len(parameters)} parameters created successfully")
    
    if success_count == len(parameters):
        print("✅ All parameters created successfully!")
        print("\n🎯 Next steps:")
        print("   1. Run: python scripts/test_ssm_util.py")
        print("   2. Check the logs to see the parameter values")
    else:
        print("❌ Some parameters failed to create!")
        sys.exit(1)


if __name__ == "__main__":
    main() 