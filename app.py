from flask import Flask, request, Response, jsonify
import requests
import os
from dotenv import load_dotenv

# Try importing CORS, fallback if not available
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("Warning: flask-cors not available, CORS may not work properly")

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS if available
if CORS_AVAILABLE:
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Accept"],
            "expose_headers": ["Content-Disposition"]
        }
    })

@app.route("/", methods=["GET"])
def home():
    return "✅ Flask backend is running!"

@app.route("/api/test", methods=["GET"])
def test_api_key():
    """Test endpoint to verify API key is loaded"""
    api_key = os.getenv('INVOICE_GENERATOR_API_KEY')
    return jsonify({
        "api_key_loaded": bool(api_key),
        "api_key_length": len(api_key) if api_key else 0,
        "api_key_preview": api_key[:10] + "..." if api_key and len(api_key) > 10 else api_key
    })

@app.route("/api/invoice", methods=["POST"])
def generate_invoice():
    try:
        # Get API key from environment variables
        api_key = os.getenv('INVOICE_GENERATOR_API_KEY')
        print(f"API Key loaded: {'Yes' if api_key else 'No'}")
        
        if not api_key:
            return jsonify({"error": "Invoice Generator API key not configured"}), 500
        
        print(f"Request data: {request.json}")
        
        # Forward request to Invoice Generator API WITH AUTHENTICATION
        resp = requests.post(
            "https://invoice-generator.com",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"  # THIS WAS MISSING!
            },
            json=request.json
        )
        
        print(f"Invoice API response status: {resp.status_code}")
        print(f"Invoice API response headers: {dict(resp.headers)}")

        if resp.status_code != 200:
            print(f"Invoice API error: {resp.text}")
            return jsonify({"error": f"Invoice API failed: {resp.text}"}), resp.status_code

        # Return PDF file to frontend
        return Response(
            resp.content,
            content_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=invoice.pdf"
            }
        )

    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Manual CORS handling if flask-cors is not available
if not CORS_AVAILABLE:
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

if __name__ == "__main__":
    app.run(port=5000, debug=True)
