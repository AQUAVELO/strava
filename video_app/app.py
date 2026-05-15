import os
import base64
import time
import uuid
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify
import anthropic
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB max upload

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
HIGGSFIELD_API_KEY = os.getenv("HIGGSFIELD_API_KEY")
HIGGSFIELD_BASE_URL = "https://api.higgsfield.ai/v1"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def build_video_prompt(user_request: str, has_image: bool) -> str:
    """Transform a user request into an optimized cinematic video prompt via Claude."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    image_context = (
        "A reference image is provided — animate it naturally while respecting its content."
        if has_image
        else ""
    )

    system = (
        "You are an expert AI video director. Your job is to rewrite user requests "
        "into precise, cinematic video generation prompts. Be specific about camera "
        "movement, lighting, mood, motion, and style. Output ONLY the prompt text, "
        "no explanations or extra formatting."
    )

    user_message = (
        f"{image_context}\n\nUser request: {user_request}\n\n"
        "Write a detailed, cinematic video generation prompt (2-4 sentences max)."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text.strip()


def image_to_data_uri(file_bytes: bytes, mime_type: str) -> str:
    encoded = base64.b64encode(file_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def submit_generation(prompt: str, image_data_uri: str | None) -> dict:
    """Submit a video generation request to Higgsfield and return the job info."""
    headers = {
        "Authorization": f"Bearer {HIGGSFIELD_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "task": "image-to-video" if image_data_uri else "text-to-video",
        "prompt": prompt,
        "duration": 5,
        "fps": 24,
        "motion_intensity": "medium",
        "enhance_prompt": False,  # We already enhanced with Claude
    }

    if image_data_uri:
        payload["input_image"] = image_data_uri

    response = requests.post(
        f"{HIGGSFIELD_BASE_URL}/generations",
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_generation_status(generation_id: str) -> dict:
    """Poll Higgsfield for the status of a generation job."""
    headers = {"Authorization": f"Bearer {HIGGSFIELD_API_KEY}"}
    response = requests.get(
        f"{HIGGSFIELD_BASE_URL}/generations/{generation_id}",
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    user_request = request.form.get("request", "").strip()
    if not user_request:
        return jsonify({"error": "A description is required."}), 400

    image_data_uri = None
    image_file = request.files.get("image")
    if image_file and image_file.filename:
        if not allowed_file(image_file.filename):
            return jsonify({"error": "Unsupported image format. Use PNG, JPG, WEBP or GIF."}), 400
        file_bytes = image_file.read()
        mime_type = image_file.content_type or "image/jpeg"
        image_data_uri = image_to_data_uri(file_bytes, mime_type)

    try:
        enhanced_prompt = build_video_prompt(user_request, has_image=image_data_uri is not None)
    except Exception as exc:
        logger.error("Claude prompt enhancement failed: %s", exc)
        return jsonify({"error": f"Prompt generation failed: {exc}"}), 502

    try:
        job = submit_generation(enhanced_prompt, image_data_uri)
    except requests.HTTPError as exc:
        logger.error("Higgsfield submission failed: %s", exc.response.text if exc.response else exc)
        return jsonify({"error": f"Higgsfield API error: {exc}"}), 502
    except Exception as exc:
        logger.error("Unexpected error during submission: %s", exc)
        return jsonify({"error": str(exc)}), 500

    generation_id = job.get("id") or job.get("generation_id")
    return jsonify(
        {
            "generation_id": generation_id,
            "enhanced_prompt": enhanced_prompt,
            "status": job.get("status", "queued"),
        }
    )


@app.route("/api/status/<generation_id>", methods=["GET"])
def status(generation_id: str):
    try:
        data = get_generation_status(generation_id)
        return jsonify(data)
    except requests.HTTPError as exc:
        return jsonify({"error": str(exc)}), 502
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true", port=port, host="0.0.0.0")
