import webview
import subprocess
import os

# Function to start the Flask app
def start_flask():
    # Set the environment variable to point to your Flask app file
    os.environ["FLASK_APP"] = "./app.py"  # Replace 'app.py' with your Flask app file
    subprocess.run(["flask", "run"])

# Run Flask app in the background
start_flask()

# Create a PyWebView window that loads the Flask app's URL
webview.create_window('SentinelCam', 'http://127.0.0.1:5000')

# Start PyWebView to display the Flask app in a native window
webview.start()
