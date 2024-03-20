import face_recognition
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_mysqldb import MySQL
import io
import dropbox
import cv2
import threading

app = Flask(__name__)

# Load the known images and encodings
image_of_person1 = face_recognition.load_image_file("deepali.jpg")
person1_face_encoding = face_recognition.face_encodings(image_of_person1)[0]

image_of_person2 = face_recognition.load_image_file("manasa.jpg")
person2_face_encoding = face_recognition.face_encodings(image_of_person2)[0]

# Create arrays of known face encodings and their corresponding names
known_face_encodings = [
    person1_face_encoding,
    person2_face_encoding
]
known_face_names = [
    "Person 1",
    "Person 2"
]

from flask import redirect, url_for

@app.route('/face-recognition')
def face_recognise():
    # Load the known images and encodings
    image_of_person1 = face_recognition.load_image_file("deepali.jpg")
    person1_face_encoding = face_recognition.face_encodings(image_of_person1)[0]

    image_of_person2 = face_recognition.load_image_file("manasa.jpg")
    person2_face_encoding = face_recognition.face_encodings(image_of_person2)[0]

    # Create arrays of known face encodings and their corresponding names
    known_face_encodings = [
        person1_face_encoding,
        person2_face_encoding
    ]
    known_face_names = [
        "manu",
        "Person 2"
    ]

    # Initialize webcam
    video_capture = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        # Find all the faces in the frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Initialize an array for storing names of recognized faces
        recognized_face_names = []

        # Loop through each face found in the frame
        for face_encoding in face_encodings:
            # See if the face matches any known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # If a match is found, use the name of the known face
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

                # If the recognized face is Person 1, redirect to documents.html
                if name == "Person 2":
                    return redirect(url_for('http://127.0.0.1:5000/normal-access'))

            recognized_face_names.append(name)

        # Display the recognized face names
        for (top, right, bottom, left), name in zip(face_locations, recognized_face_names):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam
    video_capture.release()
    cv2.destroyAllWindows()


@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'No file part'

        file = request.files['image']

        if file.filename == '':
            return 'No selected file'

        username = session.get('username')
        if username:
            # Create folder if it doesn't exist
            folder_path = '/{}'.format(username)
            try:
                dbx.files_create_folder(folder_path)
            except dropbox.exceptions.ApiError as e:
                if e.error.is_path() and e.error.get_path().is_conflict():
                    pass  # Folder already exists

            # Read the file contents from the FileStorage object
            file_contents = file.read()

            try:
                cur = mysql.connection.cursor()

                # Insert image details into MySQL table without id
                cur.execute("INSERT INTO images (filename) VALUES (%s)", (file.filename,))
                mysql.connection.commit()
                cur.close()

                # Upload the image file to the user's folder in Dropbox
                file_path = '{}/{}'.format(folder_path, file.filename)
                dbx.files_upload(file_contents, file_path)

                return 'File uploaded successfully to {}'.format(username)

            except Exception as e:
                return 'Error: {}'.format(e)

        else:
            return 'User not logged in'

    return render_template('upload_form.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
