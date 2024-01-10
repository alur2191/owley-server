from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
openai_api_key = os.getenv('OPENAI_KEY')
# Set your OpenAI API key here. It's recommended to use an environment variable in production.
openai.api_key = openai_api_key

@app.route('/gpt3', methods=['POST'])
def gpt3():
    try:
        # Extracting data from the request
        data = request.json
        prompt = data.get('prompt')
        max_tokens = data.get('max_tokens', 150)

        # Making a request to OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=max_tokens
        )

        # Returning the response
        return jsonify(response.choices[0].text.strip())

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
