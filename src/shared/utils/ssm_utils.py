import boto3
import structlog
from botocore.exceptions import ClientError, NoCredentialsError

logger = structlog.get_logger(__name__)


class SSMClient:
    """Client for interacting with AWS Systems Manager Parameter Store."""
    
    def __init__(self, region_name: str = None):
        """Initialize the SSM client.
        
        Args:
            region_name: AWS region (optional, uses default region if not specified)
        """
        try:
            self.client = boto3.client('ssm', region_name=region_name)
            logger.info("SSM client initialized successfully")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Make sure you have configured AWS credentials.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize SSM client: {e}")
            raise
    
    def get_parameter(self, parameter_name: str, with_decryption: bool = True) -> str:
        """Retrieve a parameter from SSM Parameter Store.
        
        Args:
            parameter_name: Name of the parameter to retrieve
            with_decryption: If True, automatically decrypts secure parameters
            
        Returns:
            The parameter value
            
        Raises:
            ClientError: If the parameter doesn't exist or in case of AWS error
        """
        try:
            response = self.client.get_parameter(
                Name=parameter_name,
                WithDecryption=with_decryption
            )
            parameter_value = response['Parameter']['Value']
            
            # Log the value (warning: in production, don't log secrets!)
            logger.info(f"Successfully retrieved parameter: {parameter_name}")
            logger.debug(f"Parameter value: {parameter_value}")
            
            return parameter_value
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ParameterNotFound':
                logger.error(f"Parameter not found: {parameter_name}")
                raise
            elif error_code == 'AccessDenied':
                logger.error(f"Access denied to parameter: {parameter_name}")
                raise
            else:
                logger.error(f"AWS SSM error: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving parameter {parameter_name}: {e}")
            raise


def get_api_key_from_ssm(parameter_name: str = None) -> str:
    """Utility function to retrieve API key from SSM.
    
    Args:
        parameter_name: SSM parameter name (default: /pos-h/api-key)
        
    Returns:
        The API key value
    """
    if parameter_name is None:
        parameter_name = "/pos-h/api-key"
    
    try:
        ssm_client = SSMClient()
        api_key = ssm_client.get_parameter(parameter_name)
        logger.info(f"API key retrieved from SSM parameter: {parameter_name}")
        return api_key
    except Exception as e:
        logger.error(f"Failed to retrieve API key from SSM: {e}")
        raise 