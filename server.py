import logging
from flask import Flask, request, jsonify, url_for
from openai import OpenAI
from dotenv import load_dotenv
import os
import sendgrid
from sendgrid.helpers.mail import Mail
import firebase_admin
from firebase_admin import auth, credentials

# Initialize Flask app
app = Flask(__name__)
load_dotenv()


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_KEY"),
)

# Initialize SendGrid
SENDGRID_API_KEY = os.environ.get("SENDGRID_KEY")

# Initialize Firebase Admin SDK (assuming credentials are set)
cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred)

# Configure logging
logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s %(message)s')


@app.route('/send_verification_email', methods=['POST'])
def send_verification_email():
    logging.info(">>>>>INCOMING REQUEST<<<<<<")
    email = request.json.get('email')
    try:
        user = auth.get_user_by_email(email)
        verification_link = auth.generate_email_verification_link(email)
        sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
        logging.info("SENDGRID_API_KEY>>>>>>")
        logging.info(SENDGRID_API_KEY)
        message = Mail(
            from_email='info@owley.ai',
            to_emails=email,
            subject='Verify your email',
            html_content=f'Please verify your email by clicking the following link: <a href="{verification_link}">Verify Email</a>'
        )
        response = sg.send(message)
        logging.info(f"Verification email sent to {email}")
        return jsonify({'message': 'Verification email sent!'}), 200
    except Exception as e:
        logging.error(
            f"Failed to send verification email to {email}: {str(e)}")
        return jsonify({'error': str(e)}), 500
from flask import Flask, request, jsonify
import logging
import openai

app = Flask(__name__)


@app.route('/generate_deck', methods=['POST'])
def generate_deck():
    logging.info(">>>>> INCOMING DECK GPT REQUEST <<<<<")
    try:
        data = request.json

        # Extracting additional fields
        deck_name = data.get('deckName', 'Unnamed Deck')
        about_deck = data.get('aboutDeck', '')
        ai_version = data.get('aiVersion', 'gpt-3.5-turbo-0125')  # Default to 'gpt-3.5-turbo-0125'
        length = int(data.get('length', 150))  # Default to 150 if not provided

        # Check if answers are provided correctly
        answers = data.get('answers', [])
        
        if not answers:
            raise ValueError("No answers provided")

        # Instructional text to be added before the list of questions and answers
        instructional_text = (
            "Help generate only a single flashcard deck question. I will provide you with questions and answers that will help you better understand what content I need."
            "In your response I only need you to respond with a question I'm requesting for flashcards."
        )

        # Additional text based on the about deck input
        additional_text = (
            f"{about_deck}\n\n"
            "Here are some questions and answers for determining what type of data I'm seeking help with:"
        )

        # Concatenate instructional text, additional text, and questions and answers into a single prompt text
        text = instructional_text + "\n\n" + additional_text + "\n\n" + "\n".join(
            [f"Q: {answer['question']}\nA: {answer['answer']}" for answer in answers]
        )
        logging.info(f"Received text: {text}")

        # Create a request to the OpenAI API
        response = client.chat.completions.create(
            model=ai_version,
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ],
            max_tokens=length,
        )

        # Extract relevant data from the response
        formatted_response = {
            "id": response['id'],
            "created": respoßnse['created'],
            "model": response['model'],
            "choices": [
                {
                    "content": choice['message']['content'],
                    "role": choice['message']['role'],
                    "finish_reason": choice['finish_reason']
                } 
                for choice in response['choices']
            ],
            "usage": {
                "completion_tokens": response['usage']['completion_tokens'],
                "prompt_tokens": response['usage']['prompt_tokens'],
                "total_tokens": response['usage']['total_tokens']
            }
        }

        logging.info(f"Generated response: {formatted_response}")

        # Return the formatted response as JSON
        return jsonify(formatted_response)

    except Exception as e:
        logging.error(f"Failed to generate response: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/verify_email', methods=['GET'])
def verify_email():
    try:
        oob_code = request.args.get('oob_code')
        auth.apply_action_code(oob_code)
        logging.info(f"Email verified successfully with code {oob_code}")
        return 'Email verified successfully!'
    except Exception as e:
        logging.error(f"Failed to verify email with code {oob_code}: {str(e)}")
        return str(e), 400


@app.route('/gpt3', methods=['POST'])
def gpt3():
    logging.info(">>>>>INCOMING GPT REQUEST<<<<<<")
    try:
        data = request.json
        text = data.get('text')
        logging.info(f"Received text: {text}")

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ],
            max_tokens=150,
            model="gpt-4-turbo",
        )

        # Extracting relevant data from the response
        formatted_response = {
            "id": response.id,
            "created": response.created,
            "model": response.model,
            "choices": [
                {
                    "content": choice.message.content,
                    "role": choice.message.role,
                    "finish_reason": choice.finish_reason
                }
                for choice in response.choices
            ],
            "usage": {
                "completion_tokens": response.usage.completion_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }

        logging.info(f"Generated response: {formatted_response}")

        # Returning the formatted response as JSON
        return jsonify(formatted_response)

    except Exception as e:
        logging.error(f"Failed to generate response: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/deck_answer', methods=['POST'])
def deck_answer():
    logging.info(">>>>>INCOMING DECK ANSWER GPT REQUEST<<<<<<")
    try:
        data = request.json
        text = data.get('text')

        if not text:
            raise ValueError("No text provided")

        logging.info(f"Received text: {text}")

        # Instructional text to be added before the input text
        instructional_text = (
            "Help generate only a single flashcard deck answer."
        )

        # Concatenate instructional text and the provided text
        full_text = instructional_text + "\n\n" + text

        # Create a request to the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": full_text,
                }
            ],
            max_tokens=150,
        )

        # Extracting relevant data from the response
        response_dict = response.to_dict()
        formatted_response = {
            "id": response_dict['id'],
            "created": response_dict['created'],
            "model": response_dict['model'],
            "choices": [
                {
                    "content": choice['message']['content'],
                    "role": choice['message']['role'],
                    "finish_reason": choice['finish_reason']
                }
                for choice in response_dict['choices']
            ],
            "usage": {
                "completion_tokens": response_dict['usage']['completion_tokens'],
                "prompt_tokens": response_dict['usage']['prompt_tokens'],
                "total_tokens": response_dict['usage']['total_tokens']
            }
        }

        logging.info(f"Generated response: {formatted_response}")

        # Returning the formatted response as JSON
        return jsonify(formatted_response)

    except Exception as e:
        logging.error(f"Failed to generate response: {str(e)}")
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
