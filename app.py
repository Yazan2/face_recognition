#!/usr/bin/env python
from flask import Flask, request, redirect, url_for, send_from_directory
from PIL import Image
from datetime import datetime

import os
import face_recognition
import random

UPLOAD_FOLDER = "uploads"
PHOTOS_FOLDER = "photos"
ALLOWED_FILE_TYPES = ["image/png", "image/jpeg", "image/gif", "image/bmp"]

known_faces = []
known_faces_name = []

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PHOTOS_FOLDER"] = PHOTOS_FOLDER


def allowed_file(file):
    return file.content_type.lower() in ALLOWED_FILE_TYPES


def get_extension(file):
    # print(file.content_type)
    if file.content_type == "image/jpeg":
        return ".jpg"
    else:
        return "." + file.content_type.lower()[-3:]


def get_known_faces():
    print("Getting known faces...")
    for root, dirs, files in os.walk(app.config["UPLOAD_FOLDER"]):
        for filename in files:
            # print(filename)

            # Load the jpg files into numpy arrays
            image = face_recognition.load_image_file(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            add_known_face(image, filename)


def add_known_face(image, filename):
    # Get the face encodings for each face in each image file
    # Since there could be more than one face in each image, it returns a list of encordings.
    # But since I know each image only has one face, I only care about the first encoding in each image, so I grab index 0.
    known_faces.append(face_recognition.face_encodings(image)[0])
    known_faces_name.append(filename[:-4])


@app.route("/recognition", methods=["GET", "POST"])
def recognition():
    # print(request.files)

    if request.method == "POST":
        file = request.files["file"]

        if True:
            unknown_image = face_recognition.load_image_file(file)
            pil_image = Image.fromarray(unknown_image)

            now = datetime.now()
            filename = now.strftime("%Y%m%d%H%M%S") + "_" + str(random.randint(1, 999999999999)) + get_extension(file)
            pil_image.save(os.path.join(app.config["PHOTOS_FOLDER"], filename))

            # Find all the faces in the image
            face_locations = face_recognition.face_locations(unknown_image)

            if len(face_locations) == 0:
                return "I did not find face(s) in this photograph."

            person = []
            for unknown_face_encoding in face_recognition.face_encodings(unknown_image):
                # results is an array of True/False telling if the unknown face matched anyone in the known_faces array
                results = face_recognition.compare_faces(known_faces, unknown_face_encoding)

                if not True in results:
                    person.append("unknown")

                else:
                    for idx, result in enumerate(results):
                        if result:
                            person.append(known_faces_name[idx])
                            break

            print("I found {} face(s) in this photograph. {}".format(len(face_locations), person.__str__()))
            return "I found {} face(s) in this photograph. {}".format(len(face_locations), person.__str__())

    return '''
        <!doctype html>
        <title>RECOGNIZE</title>
        <h1>Upload new File</h1>
        <h2>Allowed extensions: 'png', 'jpg', 'gif', 'bmp'</h2>
        <form action="" method="post" enctype="multipart/form-data">
            <p><input type="file" name="file"></p>
            <input type="submit" value="Upload">
        </form>
        '''


@app.route("/", methods=["GET", "POST"])
def upload_file():
    # print(request.files)
    # print(request.form)

    if request.method == "POST":
        file = request.files["file"]

        if True:
            # Load the jpg file into a numpy array
            image = face_recognition.load_image_file(file)

            # Find all the faces in the image
            face_locations = face_recognition.face_locations(image)
            print("I found {} face(s) in this photograph.".format(len(face_locations)))

            for face_location in face_locations:
                # Print the location of each face in this image
                top, right, bottom, left = face_location

                # You can access the actual face itself like this:
                face_image = image[top:bottom, left:right]
                pil_image = Image.fromarray(face_image)

                now = datetime.now()
                filename = request.form["name"].lower() + "_" + now.strftime("%Y%m%d%H%M%S") + get_extension(file)
                pil_image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

                add_known_face(image, filename)

                # for browser, add 'redirect' function on top of 'url_for'
                return url_for("uploaded_file", filename=file.filename)

    return '''
        <!doctype html>
        <title>INSERT</title>
        <h1>Upload new File</h1>
        <h2>Allowed extensions: 'png', 'jpg', 'gif', 'bmp'</h2>
        <form action="" method="post" enctype="multipart/form-data">
            <p><input type="file" name="file"></p>
            <p><input name="name"></p>
            <input type="submit" value="Upload">
        </form>
        '''


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    get_known_faces()
    # app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
