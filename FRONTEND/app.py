from flask import Flask, url_for, redirect, render_template, request,session
import mysql.connector, os, re
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib


app = Flask(__name__)
app.secret_key = 'admin'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306",
    database='transaction_db'
)

mycursor = mydb.cursor()

def executionquery(query,values):
    mycursor.execute(query,values)
    mydb.commit()
    return

def retrivequery1(query,values):
    mycursor.execute(query,values)
    data = mycursor.fetchall()
    return data

def retrivequery2(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        c_password = request.form['c_password']
        if password == c_password:
            query = "SELECT UPPER(email) FROM users"
            email_data = retrivequery2(query)
            email_data_list = []
            for i in email_data:
                email_data_list.append(i[0])
            if email.upper() not in email_data_list:
                query = "INSERT INTO users (email, password) VALUES (%s, %s)"
                values = (email, password)
                executionquery(query, values)
                return render_template('login.html', message="Successfully Registered!")
            return render_template('register.html', message="This email ID is already exists!")
        return render_template('register.html', message="Conform password is not match!")
    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = []
        for i in email_data:
            email_data_list.append(i[0])

        if email.upper() in email_data_list:
            query = "SELECT UPPER(password) FROM users WHERE email = %s"
            values = (email,)
            password__data = retrivequery1(query, values)
            if password.upper() == password__data[0][0]:
                global user_email
                user_email = email
                name = password__data[0][0]
                session['name'] = name
                return render_template('home.html',message= f"Welcome to Home page {name}")
            return render_template('login.html', message= "Invalid Password!!")
        return render_template('login.html', message= "This email ID does not exist!")
    return render_template('login.html')


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/upload',methods = ["GET","POST"])
def upload():
    if request.method == "POST":
        file = request.files['file']
        df = pd.read_csv(file)
        df = df.head(500)
        df = df.to_html()
        return render_template('upload.html', df = df)
    return render_template('upload.html')


@app.route('/model',methods =["GET","POST"])
def model():
    if request.method == "POST":
        algorithams = request.form["algo"]
        if algorithams == "1":
            accuracy = 72
            msg = 'Accuracy  for  DNN - deep neural network is ' + str(accuracy) + str('%')
        elif algorithams == "2":
            accuracy = 91
            msg = 'Accuracy  for Recurrent Neural Network RNN  is ' + str(accuracy) + str('%')
        elif algorithams == "3":
            accuracy = 91
            msg = 'Accuracy  for SGDClassifier (Stochastic Gradient Descent) is ' + str(accuracy) + str('%')
        elif algorithams == "4":
            accuracy = 99
            msg = 'Accuracy  for DecisionTreeClassifier is ' + str(accuracy) + str('%')
        elif algorithams == "5":
            accuracy = 99
            msg = 'Accuracy  for RandomForestClassifier is ' + str(accuracy) + str('%')
        elif algorithams == "6":
            accuracy = 99
            msg = 'Accuracy  for XGBClassifier is ' + str(accuracy) + str('%')
        elif algorithams == "7":
            accuracy = 98
            msg = 'Accuracy  for GradientBoostingClassifier is ' + str(accuracy) + str('%')
        elif algorithams == "8":
            accuracy = 99
            msg = 'Accuracy  for Fedrated with Randomforest is ' + str(accuracy) + str('%')
        return render_template('model.html',msg=msg,accuracy = accuracy)
    return render_template('model.html')


@app.route('/prediction', methods=["GET", "POST"])
def prediction():
    result = None
    if request.method == "POST":
             
        type = int(request.form['type'])
        amount = float(request.form['amount'])
        oldbalanceOrg = float(request.form['oldbalanceOrg'])
        newbalanceOrig = float(request.form['newbalanceOrig'])
        oldbalanceDest = float(request.form['oldbalanceDest'])
        newbalanceDest = float(request.form['newbalanceDest'])
        
        # Load the saved models
        model = joblib.load('random_forest_model.joblib')

        def prediction_function(inputs):
            classes = {0 : "No Fraud Transaction", 1 : "Fraud Transaction"}
            prediction = model.predict(inputs)
            result = classes[prediction[0]]
            return result

        inputs =[[type, amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest]]

        result = prediction_function(inputs)

    return render_template('prediction.html', prediction = result)




if __name__ == '__main__':
    app.run(debug = True)