from flask import Flask, request, jsonify, url_for
from openai import OpenAI
from dotenv import load_dotenv
import os
import sendgrid
from sendgrid.helpers.mail import Mail
from firebase_admin import auth

app = Flask(__name__)
load_dotenv()

client = OpenAI(                                                                      
    api_key=os.environ.get("OPENAI_KEY"),
)


SENDGRID_API_KEY = api_key=os.environ.get("SENDGRID_KEY"),

@app.route('/send_verification_email', methods=['POST'])
def send_verification_email():
    email = request.json.get('email')
    user = auth.get_user_by_email(email)
    
    verification_link = auth.generate_email_verification_link(email)
    sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
    message = Mail(
        from_email='your-email@example.com',
        to_emails=email,
        subject='Verify your email',
        html_content=f'Please verify your email by clicking the following link: <a href="{verification_link}">Verify Email</a>'
    )
    try:
        response = sg.send(message)
        return jsonify({'message': 'Verification email sent!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify_email', methods=['GET'])
def verify_email():
    try:
        oob_code = request.args.get('oob_code')
        auth.apply_action_code(oob_code)
        return 'Email verified successfully!'
    except Exception as e:
        return str(e), 400

@app.route('/gpt3', methods=['POST'])
def gpt3():
    try:
        data = request.json
        text = data.get('text')
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ],
            max_tokens=100,
            model="gpt-3.5-turbo",
        )


        # Extracting relevant data from the response
        formatted_response = {
            "id": response.id,
            "created": response.created,
            "model": response.model,
            "choices": [{"content": choice.message.content, "role": choice.message.role} for choice in response.choices],
            "max_tokens": response.usage.total_tokens,
        }

        # Returning the formatted response as JSON
        return jsonify(formatted_response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

