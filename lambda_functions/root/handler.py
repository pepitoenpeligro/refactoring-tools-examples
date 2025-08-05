import json
import datetime
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Root endpoint Lambda function - provides API information and status.

    Args:
        event: Lambda event data
        context: Lambda context object

    Returns:
        API Gateway response with service information
    """
    try:
        print("Root endpoint called - processing API info request")

        # Get current timestamp
        current_time = datetime.datetime.utcnow().isoformat() + 'Z'

        # API information
        api_info = {
            "service": "Multi-Lambda Hello & Mortgage Service",
            "version": "2.0.0",
            "description": "A comprehensive service with greeting and mortgage calculation endpoints",
            "timestamp": current_time,
            "endpoints": [
                {"path": "/", "method": "GET", "description": "API information and service status"},
                {"path": "/hello", "method": "GET", "description": "Random greetings with motivational quotes"},
                {"path": "/hello/{name}", "method": "GET", "description": "Personalized greetings with name analysis"},
                {"path": "/mortgage/payment", "method": "POST", "description": "Calculate monthly mortgage payments"},
                {"path": "/mortgage/breakdown", "method": "POST", "description": "Detailed amortization schedules and payment breakdowns"}
            ],
            "services": {
                "greeting_service": {
                    "description": "Multi-language greeting service with personality analysis",
                    "features": ["random_greetings", "name_analysis", "multi_language_support"]
                },
                "mortgage_service": {
                    "description": "Financial mortgage calculation service with precise decimal arithmetic",
                    "features": ["monthly_payment_calculation", "amortization_schedules", "loan_analysis"],
                    "architecture": "hexagonal_architecture",
                    "precision": "decimal_based"
                }
            },
            "status": "healthy",
            "uptime": "running",
            "environment": "AWS Lambda"
        }

        print(f"Generated API info with {len(api_info['endpoints'])} endpoints and {len(api_info['services'])} services")

        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,GET',
                'X-API-Version': '1.0.0'
            },
            'body': json.dumps(api_info, indent=2)
        }

        print("Root endpoint response generated successfully")
        return response

    except Exception as e:
        print(f"Error in root endpoint: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'Failed to retrieve API information',
                'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
            })
        }
