import json
import random
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Hello endpoint Lambda function - provides random greetings and motivational messages.

    Args:
        event: Lambda event data
        context: Lambda context object

    Returns:
        API Gateway response with random greeting
    """
    try:
        print("Hello endpoint called - generating random greeting")

        # List of random greetings
        greetings = [
            "Hello, wonderful person!",
            "Greetings, friend!",
            "Hey there, awesome human!",
            "Salutations!",
            "What's up, world?",
            "Howdy, partner!",
            "Good day to you!",
            "Welcome, traveler!"
        ]

        # List of motivational quotes
        quotes = [
            "Every day is a new beginning.",
            "You are capable of amazing things.",
            "Today is your day to shine.",
            "Believe in yourself and magic happens.",
            "Small steps lead to big changes.",
            "You've got this!",
            "Dream big, start small.",
            "Progress, not perfection."
        ]

        # Select random greeting and quote
        selected_greeting = random.choice(greetings)
        selected_quote = random.choice(quotes)

        print(f"Selected greeting: {selected_greeting}")
        print(f"Selected quote: {selected_quote}")

        # Get query parameters for additional customization
        query_params = event.get('queryStringParameters') or {}
        include_quote = query_params.get('quote', 'true').lower() == 'true'
        mood = query_params.get('mood', 'happy')

        # Adjust response based on mood
        if mood == 'excited':
            selected_greeting = selected_greeting.upper() + " 🎉"
        elif mood == 'calm':
            selected_greeting = selected_greeting.lower()

        # Build response data
        response_data = {
            "greeting": selected_greeting,
            "timestamp": context.aws_request_id,
            "function": "hello-endpoint",
            "mood": mood
        }

        if include_quote:
            response_data["daily_motivation"] = selected_quote

        print(f"Response prepared with mood: {mood}, quote included: {include_quote}")

        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,GET',
                'X-Greeting-Count': str(len(greetings)),
                'X-Quote-Count': str(len(quotes))
            },
            'body': json.dumps(response_data, indent=2)
        }

        print("Hello endpoint response generated successfully")
        return response

    except Exception as e:
        print(f"Error in hello endpoint: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'Failed to generate greeting',
                'endpoint': 'hello'
            })
        }
