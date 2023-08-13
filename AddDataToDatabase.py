import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendencerealtime-58240-default-rtdb.firebaseio.com/"
})


ref = db.reference('Students')

data = {
    "605221183":
        {
            "name": "Mohammad Saif Ansari",
            "major": "Computer Science",
            "starting_year": 2021,
            "total_attendence":6,
            "enrollment_number": "A7605221183",
            "last_attendence_time": "2023-6-20 12:45:00"
       },
    "852741":
        {
            "name": "Zayed",
            "major": "Computer Science",
            "starting_year": 2021,
            "total_attendence":0,
            "enrollment_number": "A7605221196",
            "last_attendence_time": "2023-6-20 12:45:00"
       },
    "963852":
        {
            "name": "Elon Musk",
            "major": "Spacex",
            "starting_year": 2020,
            "total_attendence":6,
            "enrollment_number": "A7605221184",
            "last_attendence_time": "2023-6-20 12:45:00"
       }
}

for key,value in data.items():
    ref.child(key).set(value)