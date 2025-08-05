import json
import hashlib
import time
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Personalized hello endpoint Lambda function - provides customized greetings with name analysis.

    Args:
        event: Lambda event data
        context: Lambda context object

    Returns:
        API Gateway response with personalized greeting and name analysis
    """
    try:
        print("Personalized hello endpoint called - processing name-based greeting")

        # Extract path parameters
        path_params = event.get('pathParameters') or {}
        name = path_params.get('name', 'Anonymous')

        # Extract query parameters
        query_params = event.get('queryStringParameters') or {}
        greeting_style = query_params.get('style', 'formal')
        language = query_params.get('lang', 'en')

        print(f"Processing greeting for name: {name}, style: {greeting_style}, language: {language}")

        # Name analysis
        name_length = len(name)
        name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
        name_vowels = sum(1 for char in name.lower() if char in 'aeiou')
        name_consonants = sum(1 for char in name.lower() if char.isalpha() and char not in 'aeiou')

        # Generate greeting based on style
        if greeting_style == 'formal':
            greeting_prefix = f"Good day, {name}"
        elif greeting_style == 'casual':
            greeting_prefix = f"Hey {name}!"
        elif greeting_style == 'enthusiastic':
            greeting_prefix = f"WOW! Hello there, {name}! 🌟"
        elif greeting_style == 'poetic':
            greeting_prefix = f"Greetings, dear {name}, whose name dances upon the wind"
        else:
            greeting_prefix = f"Hello, {name}"

        # Language-specific additions
        language_extras = {
            'es': f"¡Hola {name}! ¿Cómo estás?",
            'fr': f"Bonjour {name}! Comment allez-vous?",
            'de': f"Hallo {name}! Wie geht es Ihnen?",
            'it': f"Ciao {name}! Come stai?",
            'pt': f"Olá {name}! Como você está?"
        }

        final_greeting = language_extras.get(language, greeting_prefix)

        # Generate fun facts about the name
        fun_facts = []

        if name_length <= 3:
            fun_facts.append("Short and sweet names are often memorable!")
        elif name_length >= 10:
            fun_facts.append("Long names often have rich cultural histories!")

        if name_vowels > name_consonants:
            fun_facts.append("Your name has more vowels than consonants - that's melodic!")
        elif name_consonants > name_vowels:
            fun_facts.append("Your name has more consonants than vowels - that's strong!")
        else:
            fun_facts.append("Your name has perfect vowel-consonant balance!")

        # Generate a "lucky number" based on name
        lucky_number = (sum(ord(char) for char in name) % 100) + 1

        print(f"Generated greeting: {final_greeting}")
        print(f"Name analysis complete - vowels: {name_vowels}, consonants: {name_consonants}")

        # Build comprehensive response
        response_data = {
            "greeting": final_greeting,
            "name_analysis": {
                "name": name,
                "length": name_length,
                "vowel_count": name_vowels,
                "consonant_count": name_consonants,
                "name_signature": name_hash,
                "lucky_number": lucky_number
            },
            "fun_facts": fun_facts,
            "processing_info": {
                "style": greeting_style,
                "language": language,
                "timestamp": int(time.time()),
                "function": "personalized-hello"
            },
            "available_styles": ["formal", "casual", "enthusiastic", "poetic"],
            "available_languages": ["en", "es", "fr", "de", "it", "pt"]
        }

        print(f"Personalized response prepared for {name} with {len(fun_facts)} fun facts")

        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,GET',
                'X-Name-Length': str(name_length),
                'X-Lucky-Number': str(lucky_number),
                'X-Greeting-Style': greeting_style
            },
            'body': json.dumps(response_data, indent=2)
        }

        print("Personalized hello endpoint response generated successfully")
        return response

    except Exception as e:
        print(f"Error in personalized hello endpoint: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'Failed to generate personalized greeting',
                'endpoint': 'hello_name'
            })
        }
