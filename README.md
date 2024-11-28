# SentinelCam

**SentinelCam** *is a web-based security application that captures and sends images when an unauthorized login attempt is detected on a device. The app is built using Flask, Python, and integrates with a camera to capture images, sending them via email to the user for monitoring purposes.*

# Features

**User Authentication**: Secure login and registration system with password hashing using Flask-Bcrypt.
**Image Capture**: Uses OpenCV to capture an image from the device's webcam.
**Email Notifications**: Sends the captured image to the user's email using Gmail's SMTP server.
**Image Logs**: Captures images and stores metadata in a database for future reference.
**Delete Logs**: Users can delete their image logs from the database and the file system.
**User Dashboard**: Provides a user-friendly interface for accessing captured images and logs.

# Prerequisites

Before running **SentinelCam**, make sure you have the following installed:

*Python 3.x*
*Flask*
*Flask-SQLAlchemy*
*Flask-Login*
*Flask-Bcrypt*
*Flask-WTF*
*OpenCV*
*smtplib (Standard Library)*

# You can install the necessary Python libraries using `pip`:

```bash```
*pip install flask flask-sqlalchemy flask-login flask-bcrypt flask-wtf opencv-python*

# How it Works
1. *Login/Registration*: Users can register and log in using their email and password. The system supports user authentication with password hashing.
2. *Image Capture:* Once logged in, the user can capture an image using their webcam. The image is saved with a timestamp and stored in the static/images/ folder.
3. *Email Notification:* After capturing the image, the app sends it to the user's registered email address using Gmail's SMTP server.
4. *Logs Management:* The captured images are logged in the database. The user can view their image logs on their dashboard. Users can delete individual logs, which will remove both the log from the database and the image from the file system.

# Endpoints
- */ : Home page.*
- */capture:* Captures an image and sends it via email.
- */userdata:* Displays a list of the user's image logs.
- */delete_log/<int:log_id>:* Deletes a specific image log and removes the associated image file.
- */login:* User login page.
- */register:* User registration page.
- */dashboard:* User dashboard displaying their image logs.

# Security Considerations
1. *The app uses Flask-Bcrypt to hash and verify user passwords securely.*
2. *Sensitive credentials such as email passwords should not be hardcoded. Use environment variables for storing sensitive information.*
3. *Ensure that the "Less Secure Apps" option is enabled or use an App Password if using Gmail's SMTP server.*

# Troubleshooting
1. *Failed to send email:* Ensure that the Gmail credentials are correct, and if you have 2-step verification enabled, use an app-specific password.
Check if Gmail is blocking the login attempt. Visit Google Account Recovery to resolve any account lockouts.
2. *No image captured:* Ensure that your device has a working webcam and OpenCV is correctly installed.


# Acknowledgments
- *Flask:* A lightweight web framework for Python.
- *OpenCV:* A library for computer vision tasks such as capturing images from a webcam.
- *Flask-SQLAlchemy:* An extension for Flask that adds support for SQLAlchemy.
- *Flask-Login:* A Flask extension that manages user sessions and login authentication.