from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_KEY"),
)

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
            model="gpt-3.5-turbo",
        )


        # Returning the response
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
