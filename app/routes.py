from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Content, db  # Relative import for models.py
from .utils import generate_images, generate_videos, notify_user # Relative import for utils.py

import sys
print(sys.path)

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/generate", methods=["POST"])
def generate():
    user_id = request.form.get("user_id")
    email = request.form.get("email")
    prompt = request.form.get("prompt")

    # Add record to database
    content = Content(user_id=user_id, prompt=prompt)
    db.session.add(content)
    db.session.commit()

    try:
        # Generate images and videos
        image_paths = generate_images(prompt, user_id)
        video_paths = generate_videos(prompt, user_id)

        # Update record in database
        content.image_paths = ",".join(image_paths)
        content.video_paths = ",".join(video_paths)
        content.status = "Completed"
        db.session.commit()

        # Notify user via email
        notify_user(
            email,
            f"Your content is ready! Check the generated_content/{
                user_id} directory."
        )
        flash("Content generated successfully!", "success")
    except Exception as e:
        content.status = "Failed"
        db.session.commit()
        flash(f"An error occurred: {e}", "danger")

    return redirect(url_for("main.index"))


@main.route("/history")
def history():
    contents = Content.query.order_by(Content.generated_at.desc()).all()
    return render_template("history.html", contents=contents)
