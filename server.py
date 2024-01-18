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
            max_tokens=400,
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


