import face_recognition
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_mysqldb import MySQL
import io
import dropbox
import cv2
import threading

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dbms'
app.config['MYSQL_DB'] = 'deepali'

mysql = MySQL(app)

# Routes for user authentication
DROPBOX_ACCESS_TOKEN ='sl.BxzFKT08aAmnNtz0kX7vBgxNLi8sHdu8ZxluD2utnjhA1r2DT0A3Loyf1EU7p6v-EZMVqFUHHIf0eV-IUvoSQ2OqD7xp1WdtaEwRMVapXnXREHT6HMTqOjWSzItLYCuckWARQrAISLag'
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# Secret key for session
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

# Landing page
@app.route('/landing')
def landing():
    if 'username' in session:
        return render_template('landing.html')
    else:
        return redirect(url_for('login'))
    

# Face-based Access
@app.route('/documents-face', methods=['GET', 'POST'])
def documents_face():
    if request.method == 'POST':
        # Assuming you have face recognition logic here to authenticate the user
        # You can use any face recognition library like OpenCV or face_recognition
        # For simplicity, let's assume authentication succeeds

        
        authenticated = False

        def auth():
            image_of_person1 = face_recognition.load_image_file("tp.jpg")
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
                        if name == "Person 1":
                            return True

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

        authenticated = auth()
        
        if authenticated:
            # Fetch images from Dropbox and pass them to template
            username = session.get('username')
            if username:
                folder_path = '/{}'.format(username)
                return redirect('https://www.dropbox.com/home' + folder_path)
            else:
                return 'User not logged in'
        else:
            return 'Face not recognized. Access denied.'
    return render_template('documents.html')  # Using the same template for both key-based and face-based access

@app.route('/face', methods=['GET', 'POST'])
def face():
    image_of_person1 = face_recognition.load_image_file("tp.jpg")
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
                if name == "Person 1":
                    return render_template('upload_form.html')

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

    
@app.route('/user-dropbox-folder')
def user_dropbox_folder():
    username = session.get('username')
    if username:
        folder_path = '/{}'.format(username)
        dropbox_folder_link = "https://www.dropbox.com/home{}".format(folder_path)
        return redirect(dropbox_folder_link)
    else:
        return 'User not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username and password are valid
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cur.fetchone()
        cur.close()
        
        if user:
            # Login successful, set up session and redirect to homepage
            session['username'] = username
            return redirect(url_for('landing'))
        else:
            # Login failed
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        secret_key = request.form['key']
        
        # Store username, password, and secret key in the session
        session['username'] = username
        session['secret_key'] = secret_key

        # Store username and password in the database
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO users (username, password, `key`) VALUES (%s, %s, %s)', (username, password, secret_key))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/documents', methods=['GET', 'POST'])   
def documents():
    if request.method == 'POST':
        entered_key = request.form.get('key')
        stored_key = session.get('secret_key')
        
        if entered_key == stored_key:  
            # Fetch images from Dropbox and pass them to template
            username = session.get('username')
            if username:
                folder_path = '/{}'.format(username)
                return redirect('https://www.dropbox.com/home' + folder_path)
            else:
                return 'User not logged in'
        else:
            return 'Invalid key. Access denied.'
    return render_template('documents.html')

@app.route('/normal-access', methods=['GET', 'POST'])
def normal_access():
    if request.method == 'POST':
        entered_key = request.form.get('key')
        if entered_key == session.get('secret_key'):  # You need to store the secret key in session upon login/signup
            # Render the upload form directly if the entered key matches the stored key
            return render_template('upload_form.html')
        else:
            # Deny access and display an error message if the entered key is incorrect
            return 'Invalid key. Access denied.'
    return render_template('normal-access.html')


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


@app.route('/display')
def display_image():
    # Download the image file from Dropbox
    _, response = dbx.files_download('/your_image.jpg')

    # Return the image file as a response
    return send_file(io.BytesIO(response.content), mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)

# https://www.dropbox.com/developers/apps?_tk=pilot_lp&_ad=topbar4&_camp=myapps