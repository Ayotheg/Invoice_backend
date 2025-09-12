from flask import Flask, request, Response
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Flask backend is running!"

app = Flask(__name__)
CORS(app) 

@app.route("/api/invoice", methods=["POST"])
def generate_invoice():
    try:
        # Forward request to Invoice Generator API
        resp = requests.post(
            "https://invoice-generator.com",
            headers={"Content-Type": "application/json"},
            json=request.json
        )

        if resp.status_code != 200:
            return {"error": f"Invoice API failed: {resp.text}"}, resp.status_code

        # Return PDF file to frontend
        return Response(
            resp.content,
            content_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=invoice.pdf"
            }
        )

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
