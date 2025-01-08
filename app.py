from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import numpy as np
import google.generativeai as genai
from joblib import load
from dotenv import load_dotenv
import os
import json
import zipfile
import ulid
import csv
from collections import defaultdict
from datetime import datetime

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Extracting model 
zip_file = 'Model_Compressed.zip'
extract_to = './data'
os.makedirs(extract_to, exist_ok=True)

session_id = None
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Replace with a random secret key

# Initialize Flask-Bcrypt
bcrypt = Bcrypt(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configure MongoDB
client = MongoClient(MONGO_URI)
db = client['dps']
user_collection = db.dps_collection

# Initialize Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)
model_gem = genai.GenerativeModel("gemini-1.5-flash")
chat = model_gem.start_chat(history=[])

# Load your model
model = load('./data/DRISHTI_DPS.joblib')

symptom_dict={'anxiety and nervousness': 0,
 'depression': 1,
 'shortness of breath': 2,
 'depressive or psychotic symptoms': 3,
 'sharp chest pain': 4,
 'dizziness': 5,
 'insomnia': 6,
 'abnormal involuntary movements': 7,
 'chest tightness': 8,
 'palpitations': 9,
 'irregular heartbeat': 10,
 'breathing fast': 11,
 'hoarse voice': 12,
 'sore throat': 13,
 'difficulty speaking': 14,
 'cough': 15,
 'nasal congestion': 16,
 'throat swelling': 17,
 'diminished hearing': 18,
 'lump in throat': 19,
 'throat feels tight': 20,
 'difficulty in swallowing': 21,
 'skin swelling': 22,
 'retention of urine': 23,
 'groin mass': 24,
 'leg pain': 25,
 'hip pain': 26,
 'suprapubic pain': 27,
 'blood in stool': 28,
 'lack of growth': 29,
 'emotional symptoms': 30,
 'elbow weakness': 31,
 'back weakness': 32,
 'symptoms of the scrotum and testes': 33,
 'swelling of scrotum': 34,
 'pain in testicles': 35,
 'flatulence': 36,
 'pus draining from ear': 37,
 'jaundice': 38,
 'mass in scrotum': 39,
 'white discharge from eye': 40,
 'irritable infant': 41,
 'abusing alcohol': 42,
 'fainting': 43,
 'hostile behavior': 44,
 'drug abuse': 45,
 'sharp abdominal pain': 46,
 'feeling ill': 47,
 'vomiting': 48,
 'headache': 49,
 'nausea': 50,
 'diarrhea': 51,
 'vaginal itching': 52,
 'vaginal dryness': 53,
 'painful urination': 54,
 'involuntary urination': 55,
 'pain during intercourse': 56,
 'frequent urination': 57,
 'lower abdominal pain': 58,
 'vaginal discharge': 59,
 'blood in urine': 60,
 'hot flashes': 61,
 'intermenstrual bleeding': 62,
 'hand or finger pain': 63,
 'wrist pain': 64,
 'hand or finger swelling': 65,
 'arm pain': 66,
 'wrist swelling': 67,
 'arm stiffness or tightness': 68,
 'arm swelling': 69,
 'hand or finger stiffness or tightness': 70,
 'wrist stiffness or tightness': 71,
 'lip swelling': 72,
 'toothache': 73,
 'abnormal appearing skin': 74,
 'skin lesion': 75,
 'acne or pimples': 76,
 'dry lips': 77,
 'facial pain': 78,
 'mouth ulcer': 79,
 'skin growth': 80,
 'eye deviation': 81,
 'diminished vision': 82,
 'double vision': 83,
 'cross-eyed': 84,
 'symptoms of eye': 85,
 'pain in eye': 86,
 'eye moves abnormally': 87,
 'abnormal movement of eyelid': 88,
 'foreign body sensation in eye': 89,
 'irregular appearing scalp': 90,
 'swollen lymph nodes': 91,
 'back pain': 92,
 'neck pain': 93,
 'low back pain': 94,
 'pain of the anus': 95,
 'pain during pregnancy': 96,
 'pelvic pain': 97,
 'impotence': 98,
 'infant spitting up': 99,
 'vomiting blood': 100,
 'regurgitation': 101,
 'burning abdominal pain': 102,
 'restlessness': 103,
 'symptoms of infants': 104,
 'wheezing': 105,
 'peripheral edema': 106,
 'neck mass': 107,
 'ear pain': 108,
 'jaw swelling': 109,
 'mouth dryness': 110,
 'neck swelling': 111,
 'knee pain': 112,
 'foot or toe pain': 113,
 'bowlegged or knock-kneed': 114,
 'ankle pain': 115,
 'bones are painful': 116,
 'knee weakness': 117,
 'elbow pain': 118,
 'knee swelling': 119,
 'skin moles': 120,
 'knee lump or mass': 121,
 'weight gain': 122,
 'problems with movement': 123,
 'knee stiffness or tightness': 124,
 'leg swelling': 125,
 'foot or toe swelling': 126,
 'heartburn': 127,
 'smoking problems': 128,
 'muscle pain': 129,
 'infant feeding problem': 130,
 'recent weight loss': 131,
 'problems with shape or size of breast': 132,
 'difficulty eating': 133,
 'scanty menstrual flow': 134,
 'vaginal pain': 135,
 'vaginal redness': 136,
 'vulvar irritation': 137,
 'weakness': 138,
 'decreased heart rate': 139,
 'increased heart rate': 140,
 'bleeding or discharge from nipple': 141,
 'ringing in ear': 142,
 'plugged feeling in ear': 143,
 'itchy ear(s)': 144,
 'frontal headache': 145,
 'fluid in ear': 146,
 'neck stiffness or tightness': 147,
 'spots or clouds in vision': 148,
 'eye redness': 149,
 'lacrimation': 150,
 'itchiness of eye': 151,
 'blindness': 152,
 'eye burns or stings': 153,
 'itchy eyelid': 154,
 'feeling cold': 155,
 'decreased appetite': 156,
 'excessive appetite': 157,
 'excessive anger': 158,
 'loss of sensation': 159,
 'focal weakness': 160,
 'slurring words': 161,
 'symptoms of the face': 162,
 'disturbance of memory': 163,
 'paresthesia': 164,
 'side pain': 165,
 'fever': 166,
 'shoulder pain': 167,
 'shoulder stiffness or tightness': 168,
 'shoulder weakness': 169,
 'shoulder swelling': 170,
 'tongue lesions': 171,
 'leg cramps or spasms': 172,
 'ache all over': 173,
 'lower body pain': 174,
 'problems during pregnancy': 175,
 'spotting or bleeding during pregnancy': 176,
 'cramps and spasms': 177,
 'upper abdominal pain': 178,
 'stomach bloating': 179,
 'changes in stool appearance': 180,
 'unusual color or odor to urine': 181,
 'kidney mass': 182,
 'swollen abdomen': 183,
 'symptoms of prostate': 184,
 'leg stiffness or tightness': 185,
 'difficulty breathing': 186,
 'rib pain': 187,
 'joint pain': 188,
 'muscle stiffness or tightness': 189,
 'hand or finger lump or mass': 190,
 'chills': 191,
 'groin pain': 192,
 'fatigue': 193,
 'abdominal distention': 194,
 'regurgitation.1': 195,
 'symptoms of the kidneys': 196,
 'melena': 197,
 'flushing': 198,
 'coughing up sputum': 199,
 'seizures': 200,
 'delusions or hallucinations': 201,
 'pain or soreness of breast': 202,
 'excessive urination at night': 203,
 'bleeding from eye': 204,
 'rectal bleeding': 205,
 'constipation': 206,
 'temper problems': 207,
 'coryza': 208,
 'wrist weakness': 209,
 'hemoptysis': 210,
 'lymphedema': 211,
 'skin on leg or foot looks infected': 212,
 'allergic reaction': 213,
 'congestion in chest': 214,
 'muscle swelling': 215,
 'low back weakness': 216,
 'sleepiness': 217,
 'apnea': 218,
 'abnormal breathing sounds': 219,
 'excessive growth': 220,
 'blood clots during menstrual periods': 221,
 'absence of menstruation': 222,
 'pulling at ears': 223,
 'gum pain': 224,
 'redness in ear': 225,
 'fluid retention': 226,
 'flu-like syndrome': 227,
 'sinus congestion': 228,
 'painful sinuses': 229,
 'fears and phobias': 230,
 'recent pregnancy': 231,
 'uterine contractions': 232,
 'burning chest pain': 233,
 'back cramps or spasms': 234,
 'stiffness all over': 235,
 'muscle cramps, contractures, or spasms': 236,
 'low back cramps or spasms': 237,
 'back mass or lump': 238,
 'nosebleed': 239,
 'long menstrual periods': 240,
 'heavy menstrual flow': 241,
 'unpredictable menstruation': 242,
 'painful menstruation': 243,
 'infertility': 244,
 'frequent menstruation': 245,
 'sweating': 246,
 'mass on eyelid': 247,
 'swollen eye': 248,
 'eyelid swelling': 249,
 'eyelid lesion or rash': 250,
 'unwanted hair': 251,
 'symptoms of bladder': 252,
 'irregular appearing nails': 253,
 'itching of skin': 254,
 'hurts to breath': 255,
 'skin dryness, peeling, scaliness, or roughness': 256,
 'skin on arm or hand looks infected': 257,
 'skin irritation': 258,
 'itchy scalp': 259,
 'incontinence of stool': 260,
 'warts': 261,
 'bumps on penis': 262,
 'too little hair': 263,
 'foot or toe lump or mass': 264,
 'skin rash': 265,
 'mass or swelling around the anus': 266,
 'ankle swelling': 267,
 'drainage in throat': 268,
 'dry or flaky scalp': 269,
 'premenstrual tension or irritability': 270,
 'feeling hot': 271,
 'foot or toe stiffness or tightness': 272,
 'pelvic pressure': 273,
 'elbow swelling': 274,
 'early or late onset of menopause': 275,
 'bleeding from ear': 276,
 'hand or finger weakness': 277,
 'low self-esteem': 278,
 'itching of the anus': 279,
 'swollen or red tonsils': 280,
 'irregular belly button': 281,
 'lip sore': 282,
 'vulvar sore': 283,
 'hip stiffness or tightness': 284,
 'mouth pain': 285,
 'arm weakness': 286,
 'leg lump or mass': 287,
 'penis pain': 288,
 'loss of sex drive': 289,
 'obsessions and compulsions': 290,
 'antisocial behavior': 291,
 'neck cramps or spasms': 292,
 'poor circulation': 293,
 'thirst': 294,
 'sneezing': 295,
 'bladder mass': 296,
 'premature ejaculation': 297,
 'leg weakness': 298,
 'penis redness': 299,
 'penile discharge': 300,
 'shoulder lump or mass': 301,
 'cloudy eye': 302,
 'hysterical behavior': 303,
 'arm lump or mass': 304,
 'nightmares': 305,
 'bleeding gums': 306,
 'pain in gums': 307,
 'bedwetting': 308,
 'diaper rash': 309,
 'lump or mass of breast': 310,
 'vaginal bleeding after menopause': 311,
 'itching of scrotum': 312,
 'postpartum problems of the breast': 313,
 'hesitancy': 314,
 'muscle weakness': 315,
 'throat redness': 316,
 'joint swelling': 317,
 'redness in or around nose': 318,
 'wrinkles on skin': 319,
 'foot or toe weakness': 320,
 'hand or finger cramps or spasms': 321,
 'back stiffness or tightness': 322,
 'wrist lump or mass': 323,
 'skin pain': 324,
 'low urine output': 325,
 'sore in nose': 326,
 'ankle weakness': 327}
symptoms_list=symptom_dict.keys()

# Define User class
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Load user callback
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global session_id
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = user_collection.find_one({'email': email})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['user'] = str(user['username'])
            # Generate a new ULID
            ulid_obj = ulid.new()
            session_id = ulid_obj.str
            flash('Login successful!', 'success')
            return redirect('/index')  # Redirect to homepage
        else:
            flash('Incorrect email or password', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        repassword = request.form.get('repassword')

        # Basic validation
        if not (username and email and password and repassword):
            flash('Please fill all fields')
            return render_template('signup.html')

        if password != repassword:
            flash('Passwords do not match')
            return render_template('signup.html')

        existing_user = user_collection.find_one({'username': username})
        if existing_user:
            flash('Username already exists')
            return render_template('signup.html')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_collection.insert_one({'username': username, 'email': email, 'password': hashed_password})
        return redirect('/login')

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect('/login')


def generate_full_prompt(user_input, context):
    system_prompt = f"You are a NER model which will understand a patient's ailments and categorise it into the following symptoms: {list(symptom_dict.keys())}.\n\nMake sure to analyse the entire list instead of assuming anything initially. Only display the observed symptoms with no explanations. Output symptoms should be a single line string separated by commas"
    
    full_prompt = f"{system_prompt}\n\nPatient: {user_input}\nAI:"
    return full_prompt

def get_response(user_input):
    full_prompt = generate_full_prompt(user_input, [])
    
    response_obj = chat.send_message(full_prompt)
    response_text = response_obj.text  # Replace `.text` with the correct attribute or method
    print(response_text)
    
    # history.append(f"Patient: {user_input}")
    # history.append(f"AI: {response_text}")

    return response_text

def get_predicted_value(patient_symptoms, model):
    input_vector = np.zeros(len(symptom_dict.keys()))
    for userSymptom in patient_symptoms:
        cleaned_symptom = userSymptom.lower().strip()
        if cleaned_symptom in symptom_dict:
            input_vector[symptom_dict[cleaned_symptom]] = 1
    predicted_disease = model.predict([input_vector])[0]
    return predicted_disease

import csv

def append_to_csv(user_prompt, model_output, userID):
    
    # Ensure directory exists
    os.makedirs("./data/users", exist_ok=True)

    file_path = f"./data/users/{userID}.csv"

    # Open the CSV file in append mode
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write the header if the file is empty
        file.seek(0, 2)  # Move to the end of the file
        if file.tell() == 0:
            writer.writerow(['Session ID', 'Date', 'User Prompt', 'Model Output'])
        current_date = datetime.now().strftime('%Y-%m-%d')
        # Write the new row
        writer.writerow([str(session_id), current_date, user_prompt, model_output])

def group_entries_by_session(csv_file_path):
    grouped_entries = defaultdict(list)
    
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            session_id = row['Session ID']
            user_prompt = row['User Prompt']
            model_output = row['Model Output']
            date = row['Date']
            
            # Append the entry to the list for the corresponding session ID
            grouped_entries[session_id].append([date, user_prompt, model_output])
    
    # Convert the grouped entries to a list of lists
    grouped_list = list(grouped_entries.values())
    
    return grouped_list

@app.route('/index')
def index():
    print(session)
    if 'user_id' not in session:
        return redirect('/login')
    
    # Fetch user details
    user_id = session['user_id']
    user_name = session['user']
    user = user_collection.find_one({'_id': user_id})

    return render_template('index.html', user_name=user_name)

@app.route('/predict',methods=['POST'])
def predict():
    if 'user_id' not in session:
        return redirect('/login')

    try:
        userID = session['user_id']
        user_input = request.form.get('prompt')
        if not user_input:
            return jsonify({'error': 'No input provided'}), 400
        
        response = get_response(user_input)

        response = response.split("\n")[0]
        userSymptoms = response.split(",")
        
        disease = get_predicted_value(userSymptoms, model)

        output = "You may have " + disease
        append_to_csv(user_input, output, userID)

        # return f"You may have (a) {disease}"
        return output
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_user_data', methods=['GET'])
def get_user_data():
    if 'user_id' in session:
        user_id = session['user_id']
        csv_file_path = f'./data/users/{user_id}.csv'
        
        # Group entries by session ID
        grouped_entries = group_entries_by_session(csv_file_path)
        
        # Return the grouped entries as JSON
        return jsonify(grouped_entries)
    else:
        return jsonify({"error": "User not logged in"}), 401
if __name__ == "__main__":
    app.run(debug=True)
