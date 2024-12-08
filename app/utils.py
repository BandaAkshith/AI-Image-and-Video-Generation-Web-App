import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
PIKALABS_API_KEY = os.getenv("PIKALABS_API_KEY")


def create_user_directory(user_id):
    """Creates a directory to store generated content for a user."""
    directory = Path(f"generated_content/{user_id}")
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def generate_images(prompt, user_id, count=5):
    output_dir = create_user_directory(user_id)
    image_paths = []

    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"

    for i in range(count):
        print(f"Generating image {i + 1}...")
        payload = {"inputs": prompt}
        retries = 3
        while retries > 0:
            response = requests.post(api_url, headers=headers, json=payload)
            if response.status_code == 200:
                image_path = output_dir / f"image_{i + 1}.jpg"
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                image_paths.append(str(image_path))
                print(f"Image {i + 1} generated successfully.")
                break
            elif response.status_code == 503:  # Model loading error
                print(f"Model is loading. Waiting for {
                      retries * 30} seconds...")
                time.sleep(30)  # Wait before retrying
                retries -= 1
            elif response.status_code == 429:  # Rate limit hit
                print(f"Rate limit hit. Waiting for 60 seconds...")
                time.sleep(60)  # Wait before retrying
                retries -= 1
            else:
                print(f"Failed to generate image {
                      i + 1}: {response.status_code} - {response.text}")
                break
        else:
            print(f"Image {i + 1} failed after retries.")

    return image_paths


def generate_videos(prompt, user_id, count=5):
    """Generate videos using Pika API."""
    output_dir = create_user_directory(user_id)
    video_paths = []

    api_url = "https://api.pika.video/v1/generate"
    headers = {"Authorization": f"Bearer {PIKALABS_API_KEY}"}

    for i in range(count):
        print(f"Generating video {i + 1}...")
        payload = {
            "prompt": prompt,
            "duration": 5  # Customize based on API capability
        }
        response = requests.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            video_path = output_dir / f"video_{i + 1}.mp4"
            with open(video_path, 'wb') as f:
                f.write(response.content)
            video_paths.append(str(video_path))
            print(f"Video {i + 1} generated successfully.")
        else:
            print(f"Failed to generate video {
                  i + 1}: {response.status_code} - {response.text}")

    return video_paths


def notify_user(email, message):
    """Send an email notification to the user."""
    import smtplib
    from email.mime.text import MIMEText
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = os.getenv("SMTP_PORT", 587)
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    try:
        msg = MIMEText(message)
        msg["Subject"] = "Your Generated Content is Ready"
        msg["From"] = EMAIL_SENDER
        msg["To"] = email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Notification sent to {email}.")
    except Exception as e:
        print(f"Failed to send email: {e}")
