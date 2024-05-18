import logging
from flask import Flask, request, jsonify, url_for
import openai
from dotenv import load_dotenv
import os
import sendgrid
from sendgrid.helpers.mail import Mail
import firebase_admin
from firebase_admin import auth, credentials

# Initialize Flask app
app = Flask(__name__)
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.environ.get("OPENAI_KEY")

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
        message = Mail(
            from_email='your-email@example.com',
            to_emails=email,
            subject='Verify your email',
            html_content=f'Please verify your email by clicking the following link: <a href="{verification_link}">Verify Email</a>'
        )
        response = sg.send(message)
        logging.info(f"Verification email sent to {email}")
        return jsonify({'message': 'Verification email sent!'}), 200
    except Exception as e:
        logging.error(f"Failed to send verification email to {email}: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
    try:
        data = request.json
        text = data.get('text')
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=text,
            max_tokens=100
        )

        # Extracting relevant data from the response
        formatted_response = {
            "id": response.get('id'),
            "created": response.get('created'),
            "model": response.get('model'),
            "choices": [{"content": choice['text']} for choice in response.get('choices', [])],
            "usage": response.get('usage', {}).get('total_tokens'),
        }

        # Returning the formatted response as JSON
        return jsonify(formatted_response)

    except Exception as e:
        logging.error(f"GPT-3 request failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
