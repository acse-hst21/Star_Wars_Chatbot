import random
from functools import wraps
from flask import Flask, request, jsonify, abort
from sqlalchemy import create_engine, Column, Integer, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import openai
from openai.error import AuthenticationError

from src import config

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    prompt = Column(Text, nullable=False)
    weight = Column(Float, nullable=False)

def initialize_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        count = session.query(Prompt).count()
        if count == 0:
            default_prompts = [Prompt(prompt=dp["prompt"], name=dp["name"], weight=dp["weight"]) for dp in config.DEFAULT_PROMPTS]
            session.add_all(default_prompts)
            session.commit()
            print("Database initialized with default prompts.")
    except Exception as e:
        print("Error initializing database:", e)
    finally:
        session.close()

app = Flask(__name__)

def validate_openai_key():
    """Validate OpenAI API key by making a minimal API call"""
    try:
        openai.ChatCompletion.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1  # Keep token request as minimum value
        )
    except AuthenticationError:
        abort(403, description="Invalid API key")
    except Exception:
        # Any error outside of authentication set to 500
        abort(500, description="Error validating API key")

def authenticate(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            abort(403, description="Bearer token required")
        
        token = auth_header.split("Bearer ")[1]
        if not token:
            abort(403, description="Token cannot be empty")
            
        openai.api_key = token
        validate_openai_key()
        return func(*args, **kwargs)
    return decorated_function

def select_weighted_prompt(session):
    prompts = session.query(Prompt).all()
    if not prompts:
        default_prompt = config.DEFAULT_PROMPTS[0]
        return default_prompt["prompt"], default_prompt["name"], default_prompt["weight"]
    
    total_weight = sum(p.weight for p in prompts)
    rand_val = random.uniform(0, total_weight)
    cumulative = 0.0
    
    for p in prompts:
        cumulative += p.weight
        if rand_val <= cumulative:
            return p.prompt, p.name, p.weight
    
    chosen = prompts[-1]
    return chosen.prompt, chosen.name, chosen.weight

@app.route("/chat", methods=["POST"])
@authenticate
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    user_message = data["message"]

    session = SessionLocal()
    try:
        system_prompt, prompt_version, prompt_weight = select_weighted_prompt(session)
    finally:
        session.close()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    try:
        response = openai.ChatCompletion.create(
            model=config.OPENAI_MODEL,
            messages=messages
        )
        chat_content = response.choices[0].message["content"].strip()
    except Exception:
        abort(500, description="Internal server error")

    return jsonify({
        "content": chat_content,
        "prompt_version": prompt_version,
        "prompt_weight": prompt_weight
    })

@app.route("/insert_prompt", methods=["POST"])
@authenticate
def insert_prompt():
    data = request.get_json()
    if not data or "prompt" not in data or "weight" not in data:
        return jsonify({"error": "Request must contain 'prompt' and 'weight'"}), 400

    prompt_text = data["prompt"]
    prompt_name = data["name"]
    try:
        weight = float(data["weight"])
    except ValueError:
        return jsonify({"error": "'weight' must be a numeric value"}), 400

    session = SessionLocal()
    try:
        new_prompt = Prompt(prompt=prompt_text,name=prompt_name, weight=weight)
        session.add(new_prompt)
        session.commit()
        session.refresh(new_prompt)
        return jsonify({
            "name": new_prompt.name,
            "prompt": new_prompt.prompt,
            "weight": new_prompt.weight
        })
    except Exception:
        abort(500, description="Error saving prompt to database")
    finally:
        session.close()

if __name__ == "__main__":
    initialize_db()
