from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_KEY"),
)

@app.route('/gpt3', methods=['POST'])
def gpt3():
    try:
        # Extracting data from the request
        # data = request.json
        # prompt = data.get('prompt')
        # max_tokens = data.get('max_tokens', 150)

        # Making a request to OpenAI API
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
        )


        # Returning the response
        return jsonify(response.choices[0].text.strip())

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
