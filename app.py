from flask import Flask, request, render_template, redirect, url_for, flash
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import os

# Load the trained model
model = load_model(r"C:\Users\divya\Downloads\iompmalaria\iompmalaria\best_model.keras")

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Define the upload folder
UPLOAD_FOLDER = r"C:\Users\divya\Downloads\iompmalaria\iompmalaria\uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Sample user data for login (replace with real authentication)
USER_DATA = {
    'username': 'testuser',
    'password': 'testpass'  # Use hashed passwords in real applications
}

@app.route('/')
def home():
    return render_template('login2.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Check credentials
    if username == USER_DATA['username'] and password == USER_DATA['password']:
        return redirect(url_for('upload'))  # Redirect to the upload page
    else:
        flash('Invalid credentials. Please try again.')
        return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')  # Provide feedback
            return redirect(url_for('upload'))
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')  # Provide feedback
            return redirect(url_for('upload'))
        
        # Save the uploaded file to the uploads folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Make a prediction
        result = predict_image(file_path)
        
        # Prepare messages based on the result
        if result == 'Uninfected':
            message = "Good news! The cell is uninfected."
        else:
            message = "The cell appears to be parasitized. Please consult a healthcare provider."

        return render_template('result.html', result=result, message=message)

    return render_template('upload.html')  # Render upload page on GET request

def predict_image(image_path):
    IMG_SHAPE = 150
    image = load_img(image_path, target_size=(IMG_SHAPE, IMG_SHAPE))
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = image / 255.0

    prediction = model.predict(image)
    predicted_class = 'Uninfected' if prediction[0][0] > 0.5 else 'Parasitized'

    return predicted_class

if __name__ == '__main__':
    app.run(debug=True)
