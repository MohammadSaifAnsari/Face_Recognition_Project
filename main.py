import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendencerealtime-58240-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendencerealtime-58240.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# print(len(imgModeList))


# Load the encoding file
print("Loading Encode file")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithId = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithId
# print(studentIds)
print("Encode file loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgSize = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgSize = cv2.cvtColor(imgSize, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgSize)
    encodeCurFrame = face_recognition.face_encodings(imgSize, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[144:144 + 512, 857:857 + 330] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            # print("match Index", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendence", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # Get  the data
                studentsInfo = db.reference(f'Students/{id}').get()
                print(studentsInfo)

                # Get the image from storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # Update data of attendence
                datetimeObject = datetime.strptime(studentsInfo['last_attendence_time'], "%Y-%m-%d %H:%M:%S")
                secondsElasped = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElasped)
                if secondsElasped > 30:
                    ref = db.reference(f'Students/{id}')
                    studentsInfo['total_attendence'] += 1
                    ref.child('total_attendence').set(studentsInfo['total_attendence'])
                    ref.child('last_attendence_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[144:144 + 512, 857:857 + 330] = imgModeList[modeType]

            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 2

                imgBackground[144:144 + 512, 857:857 + 330] = imgModeList[modeType]

                if counter <= 10:
                    (w, h), _ = cv2.getTextSize(str(studentsInfo['total_attendence']), cv2.FONT_HERSHEY_COMPLEX, 1.1, 1)
                    offset = (250 - w) // 2
                    cv2.putText(imgBackground, str(studentsInfo['total_attendence']), (900 + offset, 485),
                                cv2.FONT_HERSHEY_COMPLEX, 1.1, (25, 255, 255), 1)

                    # cv2.putText(imgBackground, str(studentsInfo['standing']), (910, 625),
                    #             cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    # cv2.putText(imgBackground, str(id), (900 + offset, 540),
                    #             cv2.FONT_HERSHEY_COMPLEX, 0.5, (25, 255, 255), 1)

                    (w, h), _ = cv2.getTextSize(studentsInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 0.6, 1)
                    offset = (250 - w) // 2
                    cv2.putText(imgBackground, str(studentsInfo['name']), (900 + offset, 515),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (25, 255, 255), 1)

                    (w, h), _ = cv2.getTextSize( str(studentsInfo['enrollment_number']), cv2.FONT_HERSHEY_COMPLEX, 0.6, 1)
                    offset = (250 - w) // 2
                    cv2.putText(imgBackground, str(studentsInfo['enrollment_number']), (900 + offset, 540),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (25, 255, 255), 1)

                    (w, h), _ = cv2.getTextSize(studentsInfo['major'], cv2.FONT_HERSHEY_COMPLEX, 0.5, 1)
                    offset = (250 - w) // 2
                    cv2.putText(imgBackground, str(studentsInfo['major']), (900 + offset, 560),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (25, 255, 255), 1)

                    (w, h), _ = cv2.getTextSize(str(studentsInfo['starting_year']), cv2.FONT_HERSHEY_COMPLEX, 0.6, 1)
                    offset = (250 - w) // 2
                    cv2.putText(imgBackground, str(studentsInfo['starting_year']), (900 + offset, 582),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (25, 255, 255), 1)

                    imgBackground[219:219 + 130, 957:957 + 130] = imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentsInfo = []
                    imgStudent = []
                    imgBackground[144:144 + 512, 857:857 + 330] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendence", imgBackground)
    cv2.waitKey(1)
