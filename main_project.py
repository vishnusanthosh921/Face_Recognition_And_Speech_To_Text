
from flask import Flask, jsonify, request, render_template , redirect
import face_recognition
from flask_cors import CORS
import cv2
import os
import numpy as np
import base64
from tree import commands_tree

app = Flask(__name__)
CORS(app)

# Load known face encodings from the 'people' folder
known_image_folder = r'/home/aoopa/Downloads/RECOGNITION/myproject/people'
known_face_encodings = []
known_face_names = []

# Iterate over each file in the folder
for filename in os.listdir(known_image_folder):
    try:
        # Load the image file
        image = face_recognition.load_image_file(os.path.join(known_image_folder, filename))
        # Encode the face
        face_encodings = face_recognition.face_encodings(image)
        if len(face_encodings) > 0:
            encoding = face_encodings[0]
            # Append the encoding and the name to the lists
            known_face_encodings.append(encoding)
            known_face_names.append(os.path.splitext(filename)[0])
        else:
            print(f"No face detected in {filename}")
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hasface', methods=['POST'])
def has_face():
    try:
        image_data = request.form['image']
        # Convert image data to NumPy array
        nparr = np.frombuffer(base64.b64decode(image_data.split(',')[1]), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Find all face locations in the frame
        face_locations = face_recognition.face_locations(frame)
        has_face = len(face_locations) > 0
        
        return jsonify({'hasFace': has_face})
    except Exception as e:
        # Reset current_commands to commands_tree on exception
        global current_commands
        current_commands = commands_tree
        return jsonify({'error': str(e)}), 500

@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        image_data = request.form['image']
        # Convert image data to NumPy array
        nparr = np.frombuffer(base64.b64decode(image_data.split(',')[1]), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Find all face locations in the frame
        face_locations = face_recognition.face_locations(frame)
        # Encode faces in the frame
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        recognized_name = 'Unknown'
        # Loop through each face in the frame
        for face_encoding in face_encodings:
            # Compare face encoding with known encodings
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            if True in matches:
                first_match_index = matches.index(True)
                recognized_name = known_face_names[first_match_index]
                print(f"Recognized face: {recognized_name}")  # Print the recognized name
                break  # Stop processing once a match is found

        return jsonify({'name': recognized_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

current_commands = commands_tree
previous_commands = {}

@app.route('/reset', methods=['GET'])
def reset():
    global current_commands
    current_commands=commands_tree
    return "yeahhhh"

@app.route('/command', methods=['POST'])
def handle_command():
    global current_commands
    global previous_commands
    global command
    try:
        data = request.get_json()
        command = data.get('command')
        print(command)


        if command == "back":
            current_commands = previous_commands
            return jsonify({"message": "Going back."})
        elif command in current_commands:
            previous_commands = current_commands
            current_commands = current_commands[command]
            if isinstance(current_commands, str): # Check if it's a terminating command
                response = current_commands
                current_commands = commands_tree  # Go back to the root node
            
        
            else:
                response = list(current_commands.keys())
        
        elif command =="google":
            response = "google"
        
        else:
            response = "Command not found."
        
        print(response)
        return jsonify({"response": response})
    except Exception as e:
        # Reset current_commands to commands_tree on exception
        current_commands = commands_tree
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
