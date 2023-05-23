from flask import Flask, render_template,redirect, request, url_for
import asyncio
import io
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
# To install this module, run:
# python -m pip install Pillow
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, QualityForRecognition
from PIL import Image, ImageDraw, ImageFont
import urllib.request
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
connection_string = 'DefaultEndpointsProtocol=https;AccountName=whatsapp123url;AccountKey=aUAaGuT3173N35X9DRoNaSk7S67mOTnEFyf33aUmqpO/mYXz/pkoRnfbRCUMycyNGHruu2FKWRUVsxtdJDPgsQ==;EndpointSuffix=core.windows.net'

# Create a container name
container_name = 'faceapipoc'

# Create an instance of the BlobServiceClient class
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)
# Function to upload an image to Azure Blob Storage
def upload_image_to_blob(image_path, blob_name):
    # Create a BlobClient for the container
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Upload the image file to the blob
    with open(image_path, "rb") as data:
        blob_client.upload_blob(data)

# Function to get the URL of an image in Azure Blob Storage
def get_image_url(blob_name):
    # Get the BlobClient for the container
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Get the URL of the image
    url = blob_client.url
    return url

# Function to delete an image from Azure Blob Storage
def delete_image_from_blob(blob_name):
    # Delete the blob
    container_client.delete_blob(blob_name)
# This key will serve all examples in this document.
API_KEY = '2bf3fa20e6d94740af639c24f5c8c3ff'

# This endpoint will be used in all examples in this quickstart.
ENDPOINT = 'https://facial-recognition-poc.cognitiveservices.azure.com/'

# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(API_KEY))
app = Flask(__name__)


@app.route('/',methods=['GET'])
def startPage():
    return render_template('index.html')
    # return 'Hello, World!'

@app.route('/home',methods=['GET'])
def homePage():
    return render_template('index.html')
    # return 'Hello, World!'

@app.route('/personID',methods=['GET'])
def personID():
    return render_template('personGroupID.html')
    # return 'Hello, World!'

@app.route('/personGroupID',methods=['GET', 'POST'])
def personGroupID():
    if request.method == 'POST':
        PERSON_GROUP_ID = request.form.get('PERSON_GROUP_ID')
        print(PERSON_GROUP_ID)
        if not PERSON_GROUP_ID:
            return redirect(url_for('personGroupID', error='please enter details'))
        try:
            face_client.person_group.create(person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID, recognition_model='recognition_04')
            return redirect(url_for('personGroupID', error='created successfully!!!'))
        except:
            return redirect(url_for('personGroupID', error='name or target already taken please use other'))
    return render_template('personGroupID.html', error=request.args.get('error'))
    # return 'Hello, World!'

@app.route('/CrPerson',methods=['GET'])
def crPerson():
    return render_template('createPerson.html')
    # return 'Hello, World!'

@app.route('/createPerson',methods=['GET', 'POST'])
def createPerson():
    if request.method == 'POST':
        PERSON_GROUP_ID = request.form.get('PERSON_GROUP_ID')
        PERSON_NAME = request.form.get('UNIQUE_PERSON_NAME')
        # IMAGE_URL = request.form.get('IMAGE_URL')
        print(PERSON_GROUP_ID)
        if not PERSON_GROUP_ID or not PERSON_NAME:
            return redirect(url_for('createPerson', error='please enter details'))
        try:
            add_person  = face_client.person_group_person.create(PERSON_GROUP_ID, name=PERSON_NAME)
            # # Check if the image is of sufficent quality for recognition.
            # sufficientQuality = True
            # detected_faces = face_client.face.detect_with_url(url='https://whatsapp123url.blob.core.windows.net/faceapipoc/singleperson.JPG' , detection_model='detection_03', recognition_model='recognition_04', return_face_attributes=['qualityForRecognition'])
            # if not detected_faces:
            #     raise Exception('No face detected')
            # for face in detected_faces:
            #     if face.face_attributes.quality_for_recognition != QualityForRecognition.high:
            #         sufficientQuality = False
            #         break
            #     face_client.person_group_person.add_face_from_url(PERSON_GROUP_ID, add_person.person_id, 'https://whatsapp123url.blob.core.windows.net/faceapipoc/singleperson.JPG')
            #     print("face {} added to person {}".format(face.face_id, add_person.person_id))
            return redirect(url_for('createPerson', error='Please find the person id to add person face to name - ' + str(add_person.person_id)))
        except:
            return redirect(url_for('createPerson', error='please give valid name or person group ID'))
    return render_template('createPerson.html', error=request.args.get('error'))

@app.route('/addFaceto',methods=['GET'])
def addfaceto():
    return render_template('addFace.html')
    # return 'Hello, World!'

@app.route('/addFace',methods=['GET', 'POST'])
def addFace():
    if request.method == 'POST':
        PERSON_GROUP_ID = request.form.get('PERSON_GROUP_ID')
        UNIQUE_PERSON_ID_GENERATED = request.form.get('UNIQUE_PERSON_ID_GENERATED')
        # IMAGE_URL = request.form.get('IMAGE_URL')
        image = request.files['image']
        image.save('images/' +str(UNIQUE_PERSON_ID_GENERATED) + str(PERSON_GROUP_ID) + image.filename)
        upload_image_to_blob('images/'+str(UNIQUE_PERSON_ID_GENERATED) + str(PERSON_GROUP_ID) + image.filename, str(UNIQUE_PERSON_ID_GENERATED) + str(PERSON_GROUP_ID) + image.filename)
        IMAGE_URL = get_image_url(str(UNIQUE_PERSON_ID_GENERATED) + str(PERSON_GROUP_ID) + image.filename)
        print(PERSON_GROUP_ID)
        if not PERSON_GROUP_ID or not UNIQUE_PERSON_ID_GENERATED or not IMAGE_URL:
            return redirect(url_for('addFace', error='please enter details'))
        try:
            # Check if the image is of sufficent quality for recognition.
            sufficientQuality = True
            detected_faces = face_client.face.detect_with_url(url=IMAGE_URL , detection_model='detection_03', recognition_model='recognition_04', return_face_attributes=['qualityForRecognition'])
            if not detected_faces:
                raise Exception('No face detected')
            for face in detected_faces:
                if face.face_attributes.quality_for_recognition != QualityForRecognition.high:
                    sufficientQuality = False
                    break
                face_client.person_group_person.add_face_from_url(PERSON_GROUP_ID, UNIQUE_PERSON_ID_GENERATED, IMAGE_URL)
                print("face {} added to person {}".format(face.face_id, UNIQUE_PERSON_ID_GENERATED))
            return redirect(url_for('addFace', error='face is successfully added!!!'))
        except:
            return redirect(url_for('addFace', error='please give valid ID'))
    return render_template('addFace.html', error=request.args.get('error'))

@app.route('/trainto',methods=['GET'])
def trainto():
    return render_template('train.html')
    # return 'Hello, World!'

@app.route('/train',methods=['GET', 'POST'])
def train():
    if request.method == 'POST':
        PERSON_GROUP_ID = request.form.get('PERSON_GROUP_ID')
        print(PERSON_GROUP_ID)
        if not PERSON_GROUP_ID:
            return redirect(url_for('train', error='please enter details'))
        try:
            rawresponse = face_client.person_group.train(PERSON_GROUP_ID, raw= True)
            while (True):
                training_status = face_client.person_group.get_training_status(PERSON_GROUP_ID)
                print("Training status: {}.".format(training_status.status))
                print()
                if (training_status.status is TrainingStatusType.succeeded):
                    return redirect(url_for('train', error='Trained Successfully!!!'))
                elif (training_status.status is TrainingStatusType.failed):
                    face_client.person_group.delete(person_group_id=PERSON_GROUP_ID)
                    # sys.exit('Training the person group has failed.')
                    return redirect(url_for('train', error='Training the person group has failed.!!!'))
                time.sleep(5)
        except:
            return redirect(url_for('train', error='please give valid ID'))
    return render_template('train.html', error=request.args.get('error'))

@app.route('/identifyto',methods=['GET'])
def identifyto():
    return render_template('identify.html')
    # return 'Hello, World!'

@app.route('/identify',methods=['GET', 'POST'])
def identify():
    if request.method == 'POST':
        PERSON_GROUP_ID = request.form.get('PERSON_GROUP_ID')
        # IMAGE_URL = request.form.get('IMAGE_URL')
        image = request.files['image']
        image.save('images/' + image.filename)
        try:
            upload_image_to_blob('images/'+image.filename, image.filename)
        except:
            delete_image_from_blob(image.filename)
            upload_image_to_blob('images/'+image.filename, image.filename)
        IMAGE_URL = get_image_url(image.filename)
        print(PERSON_GROUP_ID)
        if not PERSON_GROUP_ID or not IMAGE_URL:
            return redirect(url_for('identify', error='please enter details'))
        try:
            face_ids = []
            # We use detection model 3 to get better performance, recognition model 4 to support quality for recognition attribute.
            faces = face_client.face.detect_with_url(IMAGE_URL, detection_model='detection_01', recognition_model='recognition_04', return_face_attributes=['qualityForRecognition','age', 'emotion'])
            for face in faces:
                # Only take the face if it is of sufficient quality.
                if face.face_attributes.quality_for_recognition == QualityForRecognition.high or face.face_attributes.quality_for_recognition == QualityForRecognition.medium:
                    face_ids.append(face.face_id)
            # Identify faces
            results = face_client.face.identify(face_ids, PERSON_GROUP_ID)
            print(results)
            urllib.request.urlretrieve(IMAGE_URL,"text.png")
            img = Image.open("text.png")
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(r'C:\Windows\Fonts\Arial.ttf', 35)
            print('Identifying faces in image')
            if not results:
                print('No person identified in the person group')
            for identifiedFace in results:
                if len(identifiedFace.candidates) > 0:
                    for face in faces:
                        if face.face_id == identifiedFace.face_id:
                            response_name = face_client.person_group_person.get(PERSON_GROUP_ID,identifiedFace.candidates[0].person_id)
                            print('Person is identified for face ID {} in image, with a confidence of {}.'.format(identifiedFace.face_id, identifiedFace.candidates[0].confidence)) # Get topmost confidence score
                            print(identifiedFace)
                            face_id_project = identifiedFace.face_id
                            age = face.face_attributes.age
                            emotion = face.face_attributes.emotion
                            neutral = '{0:.0f}%'.format(emotion.neutral * 100)
                            happiness = '{0:.0f}%'.format(emotion.happiness * 100)
                            anger = '{0:.0f}%'.format(emotion.anger * 100)
                            sandness = '{0:.0f}%'.format(emotion.sadness * 100)
                            personId = identifiedFace.candidates[0].person_id
                            personName = response_name.name
                            rect = face.face_rectangle
                            left = rect.left
                            top = rect.top
                            right = rect.width + left
                            bottom = rect.height + top
                            draw.rectangle(((left, top), (right, bottom)), outline='green', width=5)
                            draw.text((right + 4, top+70), 'personName: ' + personName, fill="#000", font=font)
                            draw.text((right + 4, top+105), 'Happy: ' + happiness, fill="#000", font=font)
                            draw.text((right + 4, top+140), 'Sad: ' + sandness, fill="#000", font=font)
                            draw.text((right + 4, top+175), 'Angry: ' + anger, fill="#000", font=font)
                            draw.text((right + 4, top+210), 'Neutral: ' + neutral, fill="#000", font=font)
                            img.show()
                            img.save("result.jpg")
                            # return redirect(url_for('identify', error='Person is identified for face ID {} in image, with a confidence of {}.'.format(identifiedFace.face_id, identifiedFace.candidates[0].confidence),user_image = img))
                            return render_template('identify.html', user_image = 'result.jpg',error='Person is identified for face ID {} in image, with a confidence of {}.'.format(identifiedFace.face_id, identifiedFace.candidates[0].confidence))
                    # Verify faces
                    # verify_result = face_client.face.verify_face_to_person(identifiedFace.face_id, identifiedFace.candidates[0].person_id, PERSON_GROUP_ID)
                    # print('verification result: {}. confidence: {}'.format(verify_result.is_identical, verify_result.confidence))
                else:
                    return redirect(url_for('identify', error='No person identified for face ID {} in image.'.format(identifiedFace.face_id)))
        except:
            return redirect(url_for('identify', error='please give valid ID'))
    return render_template('identify.html', error=request.args.get('error'))
# main driver function
if __name__ == '__main__':
    app.run()