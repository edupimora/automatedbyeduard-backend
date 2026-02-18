# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for the entire Flask application

# --- Database Configuration ---
# Get database URI from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable tracking modifications for performance

db = SQLAlchemy(app) # Initialize SQLAlchemy with the Flask app

# --- Database Model for Contact Messages ---
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages' # Link to the table created in Supabase

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, server_default=db.text("gen_random_uuid()")) # UUID as string
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now()) # Timestamp with timezone

    def __repr__(self):
        return f'<ContactMessage {self.name} - {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# --- Routes ---
@app.route('/')
def home():
    return "Willkommen im Backend von Eduard Morales!"

@app.route('/api/saludo')
def saludo():
    return jsonify(message="Hallo vom Python-API!")

@app.route('/api/contacto', methods=['POST'])
def contacto():
    data = request.get_json()
    name = data.get('nombre')
    email = data.get('email')
    message = data.get('mensaje')

    if not name or not email or not message:
        return jsonify(message="Bitte füllen Sie alle Felder aus.", status="error"), 400

    try:
        # Create a new ContactMessage object
        new_message = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_message) # Add to the session
        db.session.commit() # Commit to the database

        print(f"Empfangene Formulardaten und in DB gespeichert: Name={name}, Email={email}, Nachricht={message}")
        return jsonify(message="Kontaktdaten erfolgreich empfangen und gespeichert", status="success"), 200
    except Exception as e:
        db.session.rollback() # Rollback in case of error
        print(f"Fehler beim Speichern der Kontaktdaten: {e}")
        return jsonify(message=f"Fehler beim Speichern der Kontaktdaten: {str(e)}", status="error"), 500

# --- Optional: Route to fetch all contact messages (for testing/admin) ---
@app.route('/api/mensajes', methods=['GET'])
def get_messages():
    try:
        messages = ContactMessage.query.all()
        return jsonify([msg.to_dict() for msg in messages]), 200
    except Exception as e:
        print(f"Fehler beim Abrufen der Nachrichten: {e}")
        return jsonify(message=f"Fehler beim Abrufen der Nachrichten: {str(e)}", status="error"), 500


if __name__ == '__main__':
    # This block will create tables if they don't exist.
    # It's good for initial setup but for production, use migrations.
    with app.app_context():
        db.create_all() # This will create tables based on models if they don't exist

    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)