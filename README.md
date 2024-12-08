# AI Image and Video Generation Web App

This project is an AI-powered image and video generation system. It leverages Hugging Face's Stable Diffusion model for generating images based on text prompts and the Pika API for generating videos. The system also allows users to track their generated content and receive notifications upon completion.

## Features:
- **Generate Images**: Create images using a text prompt via Hugging Face’s Stable Diffusion model.
- **Generate Videos**: Generate short videos based on a text prompt using the Pika API.
- **Track Content**: Users can track the history of generated content.
- **Email Notification**: Once content is generated, users are notified via email.
- **Database Integration**: SQLite database to store user-generated content and its status.

## Requirements:

### **1. Install Dependencies:**

You can install the necessary dependencies by creating a virtual environment and using `pip` to install the packages listed in `requirements.txt` (or manually install the required packages).

```bash
# Create a virtual environment (if you don't have one)
python -m venv venv

# Activate the virtual environment
# For Windows:
.\venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

If `requirements.txt` is not available, you need to manually install the dependencies:

```bash
pip install flask flask_sqlalchemy flask_migrate requests smtplib python-dotenv
```

### **2. Set Up Environment Variables:**

Before running the application, create a `.env` file in the root directory and add your API keys and email credentials.

Example `.env` file:

```env
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
PIKALABS_API_KEY=your_pikalabs_api_key_here
EMAIL_SENDER=your_email_here
EMAIL_PASSWORD=your_email_app_password_here
SECRET_KEY=your_secret_key_here
```

**Note**: You will need to create an App Password for Gmail if using Gmail for SMTP authentication (this is recommended for security).

---

## Setup and Running the App:

### **1. Run the Flask App:**

After setting up the environment variables, run the Flask application.

```bash
python main.py
```

This will start a development server at `http://127.0.0.1:5000`.

### **2. Open the Web App:**

- Navigate to `http://127.0.0.1:5000` in your web browser.
- Enter your **User ID**, **Email**, and a **Text Prompt**.
- Click **Submit** to generate images and videos based on your text prompt.

### **3. Track Generated Content:**

The web app also keeps track of the content you generate. You can view the content history through the **History** page. The **content.db** file stores the metadata for the generated content, including image and video paths, user info, and status.

---

## Functionality:

### **1. Image Generation**:
- Images are generated using **Hugging Face's Stable Diffusion model**.
- The user provides a text prompt, and the app will make a request to the Hugging Face API to generate images based on that prompt.
- If the model is loading or if rate limits are reached, the app will wait and retry.

### **2. Video Generation**:
- Videos are generated using the **Pika API**.
- Like images, the user provides a text prompt, and the app requests video generation.
- The generated video is saved in the `generated_content` folder and associated with the user’s ID.

### **3. Email Notification**:
- After the content is successfully generated, an email notification is sent to the user.
- The email contains a message indicating that the content is ready and where to find it.

### **4. SQLite Database**:
- The **content.db** SQLite database stores user-related information, including:
  - **user_id**: The unique ID provided by the user.
  - **prompt**: The text prompt entered by the user.
  - **video_paths**: Paths to the generated videos.
  - **image_paths**: Paths to the generated images.
  - **status**: The current status of the generation (e.g., "Processing", "Completed", "Failed").
  - **generated_at**: Timestamp of when the content was generated.

---

## Troubleshooting:

### **1. Missing `content` Table**:
If the `content` table is not created, make sure to run the migration process to create the table:

```bash
# Run Flask-Migrate commands
flask db init
flask db migrate -m "Create content table"
flask db upgrade
```

This will create the necessary table in the database.

### **2. Email Authentication Issues**:
If you are having issues sending email notifications, make sure:
- You are using **App Passwords** for Gmail (not your main Gmail password).
- **Less secure app access** is enabled (or use App Passwords instead).

### **3. Rate Limiting & Model Loading Errors**:
- If you encounter **503 errors** or rate limiting from Hugging Face, try again later.
- If **GPU memory issues** (CUDA out of memory) occur, consider reducing the request size or retrying later, as this is typically an API-side issue.

---

## Additional Features (Future Work):
- **User Authentication**: Add user authentication to manage sessions and history.
- **Progress Indicators**: Show progress indicators for image and video generation.
- **Multiple File Formats**: Support additional video formats and larger image resolutions.
- **Advanced Content Settings**: Allow users to customize settings like video length, image resolution, etc.

---

## License:
This project is open-source and available under the MIT License.

---

### **Conclusion:**
This app demonstrates a basic AI-powered content generation system that can generate images and videos based on text prompts. It uses Hugging Face's Stable Diffusion for images, Pika for video generation, and Flask for the web framework, with email notifications to alert users when their content is ready. The project also integrates an SQLite database to track content history.

---
