import os
import time
import requests
from pathlib import Path
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

# Set API keys
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
PIKALABS_API_KEY = os.getenv("PIKALABS_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = os.getenv("SMTP_PORT", 587)

# Database setup
Base = declarative_base()


class Content(Base):
    __tablename__ = "content"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    video_paths = Column(Text)
    image_paths = Column(Text)
    status = Column(String, default="Processing")
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)


DATABASE_URL = "sqlite:///content.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Helper functions


def create_user_directory(user_id):
    """Creates a directory to store generated content for a user."""
    directory = Path(f"generated_content/{user_id}")
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def notify_user(email, message):
    """Send an email notification to the user."""
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
            print(
                f"Failed to generate video {i + 1}: {response.status_code} - {response.text}")

    return video_paths


# Main execution
if __name__ == "__main__":
    # User input
    user_id = input("Enter your user ID: ")
    email = input("Enter your email: ")
    prompt = input("Enter a text prompt: ")

    # Create a new record in the database
    content = Content(user_id=user_id, prompt=prompt)
    session.add(content)
    session.commit()

    try:
        # Generate images
        print("\nGenerating images...")
        image_paths = generate_images(prompt, user_id)
        content.image_paths = ",".join(image_paths)

        # Generate videos
        print("\nGenerating videos...")
        video_paths = generate_videos(prompt, user_id)
        content.video_paths = ",".join(video_paths)

        # Update content status
        content.status = "Completed"
        session.commit()

        # Notify the user
        notify_user(
            email, f"Your content is ready! Check it out in the 'generated_content/{user_id}/' directory.")

    except Exception as e:
        content.status = "Failed"
        session.commit()
        print(f"An error occurred: {e}")

    print("\nAll tasks completed.")
