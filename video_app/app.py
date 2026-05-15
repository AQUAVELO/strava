import logging
import os
import tempfile
import threading
import uuid
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from higgsfield_scraper import HiggsFieldScraper

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
HIGGSFIELD_EMAIL = os.getenv("HIGGSFIELD_EMAIL")
HIGGSFIELD_PASSWORD = os.getenv("HIGGSFIELD_PASSWORD")
HIGGSFIELD_COOKIES = os.getenv("HIGGSFIELD_COOKIES")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

# In-memory job store: job_id → {status, enhanced_prompt, video_url, error}
jobs: dict[str, dict] = {}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def build_video_prompt(user_request: str, has_image: bool) -> str:
    """Use Claude Sonnet to transform a user request into a cinematic video prompt."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    image_ctx = (
        "A reference image is provided — animate it naturally while respecting its content."
        if has_image
        else ""
    )
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        system=(
            "You are an expert AI video director. Rewrite user requests into precise, "
            "cinematic video generation prompts. Be specific about camera movement, "
            "lighting, mood, motion, and visual style. "
            "Output ONLY the prompt text — no explanations, no formatting."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"{image_ctx}\n\nUser request: {user_request}\n\n"
                    "Write a detailed cinematic video prompt (2-4 sentences)."
                ),
            }
        ],
    )
    return response.content[0].text.strip()


def run_generation(job_id: str, prompt: str, image_path: str | None) -> None:
    """Background thread: run Playwright scraper and update job status."""
    scraper = HiggsFieldScraper(
        email=HIGGSFIELD_EMAIL,
        password=HIGGSFIELD_PASSWORD,
        cookies_json=HIGGSFIELD_COOKIES,
    )
    try:
        jobs[job_id]["status"] = "generating"
        video_url = scraper.generate(prompt, image_path)
        jobs[job_id].update({"status": "completed", "video_url": video_url})
        logger.info("Job %s completed: %s", job_id, video_url)
    except Exception as exc:
        logger.error("Job %s failed: %s", job_id, exc)
        jobs[job_id].update({"status": "failed", "error": str(exc)})
    finally:
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    user_request = request.form.get("request", "").strip()
    if not user_request:
        return jsonify({"error": "A description is required."}), 400

    # Save uploaded image to a temp file
    image_path = None
    image_file = request.files.get("image")
    if image_file and image_file.filename and allowed_file(image_file.filename):
        ext = image_file.filename.rsplit(".", 1)[1].lower()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
        image_file.save(tmp.name)
        image_path = tmp.name

    # Enhance prompt with Claude
    try:
        enhanced_prompt = build_video_prompt(
            user_request, has_image=image_path is not None
        )
    except Exception as exc:
        if image_path:
            os.unlink(image_path)
        return jsonify({"error": f"Prompt generation failed: {exc}"}), 502

    # Create job and spawn background thread
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "queued",
        "enhanced_prompt": enhanced_prompt,
        "video_url": None,
        "error": None,
    }
    threading.Thread(
        target=run_generation,
        args=(job_id, enhanced_prompt, image_path),
        daemon=True,
    ).start()

    return jsonify(
        {
            "job_id": job_id,
            "enhanced_prompt": enhanced_prompt,
            "status": "queued",
        }
    )


@app.route("/api/status/<job_id>", methods=["GET"])
def status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found."}), 404
    return jsonify(job)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        port=port,
        host="0.0.0.0",
    )
