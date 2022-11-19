from flask import Flask, render_template, request, redirect, flash
import pickle
import pandas as pd
import joblib
import numpy as np
import sqlite3


app = Flask(__name__)
app.secret_key="21433253"
conn = sqlite3.connect("database1.db")
conn.execute("CREATE TABLE IF NOT EXISTS login(email TEXT PRIMARY KEY,password TEXT)")
conn.close()

@app.route('/')
def main():
    return render_template('login.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        try:
            print("request1")
            fv = [x for x in request.form.values()]
            print(fv)
            print([x for x in request.form.values()])
            print(request.form["email"])
            email = request.form["email"]
            pswd = request.form["pswd"]
            print("request2")
            conn = sqlite3.connect("database1.db")
            cur = conn.cursor()
            print(email, pswd)
            cur.execute("SELECT password FROM login WHERE email=?;", (str(email),))
            print("select")

            result = cur.fetchone()
            cur.execute("SELECT * FROM login")
            print(cur.fetchall())
            print("fetch")
            if result:
                print("You've have been logged in")
                print(result)
                if result[0] == pswd:
                    flash("Login successfully", 'success')
                    return redirect('/home')
                else:
                    return render_template("login.html", error="Please enter correct password")

            else:
                print("register")
                flash("Please Register first to access", 'danger')

                return redirect('/reg')

        except Exception as e:
            print(e)
            print('danger-----------------------------------------------------------------')
            return "hello error"


@app.route('/reg')
def reg():
    return render_template("register.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        try:
            print("request1")
            fv = [x for x in request.form.values()]
            print(fv)
            print([x for x in request.form.values()])
            print(request.form["email"])
            email = request.form["email"]
            print(request.form["pswd"])
            pswd = request.form["pswd"]
            conn = sqlite3.connect("database1.db")
            print("database")
            cur = conn.cursor()
            print("cursor")
            cur.execute("SELECT * FROM login WHERE email=?;", (str(email),))
            print("fetch")
            result = cur.fetchone()
            if result:
                print("already")
                flash("User already exists,please login", 'danger')
                return redirect('/')
            else:
                print("insert")
                cur.execute("INSERT INTO  login(email,password)values(?,?)", (str(email), str(pswd)))
                conn.commit()
                cur.execute("SELECT * FROM login")
                print(cur.fetchall())
                flash("Registered successfully", 'success')
                return render_template('login.html')

        except Exception as e:
            print(e)
            # flash(e,'danger')
            return "hello error1"

            # return redirect('/')
# return render_template('login.html')


@app.route('/home')
def home():
    return render_template('Flightdelay.html')


@app.route('/result', methods=['POST'])
def predict():
    fl_num = int(request.form.get('fno'))
    month = int(request.form.get('month'))
    dayofmonth = int(request.form.get('daym'))
    dayofweek = int(request.form.get('dayw'))
    sdeptime = request.form.get('sdt')
    adeptime = request.form.get('adt')
    arrtime = int(request.form.get('sat'))
    depdelay = int(adeptime) - int(sdeptime)
    inputs = list()
    inputs.append(fl_num)
    inputs.append(month)
    inputs.append(dayofmonth)
    inputs.append(dayofweek)
    if (depdelay < 15):
        inputs.append(0)
    else:
        inputs.append(1)
    inputs.append(arrtime)
    origin = str(request.form.get("org"))
    dest = str(request.form.get("dest"))
    if (origin == "ATL"):
        a = [1, 0, 0, 0, 0]
        inputs.extend(a)
    elif (origin == "DTW"):
        a = [0, 1, 0, 0, 0]
        inputs.extend(a)
    elif (origin == "JFK"):
        a = [0, 0, 1, 0, 0]
        inputs.extend(a)
    elif (origin == "MSP"):
        a = [0, 0, 0, 1, 0]
        inputs.extend(a)
    elif (origin == "SEA"):
        a = [0, 0, 0, 0, 1]
        inputs.extend(a)

    if (dest == "ATL"):
        b = [1, 0, 0, 0, 0]
        inputs.extend(b)
    elif (dest == "DTW"):
        b = [0, 1, 0, 0, 0]
        inputs.extend(b)
    elif (dest == "JFK"):
        b = [0, 0, 1, 0, 0]
        inputs.extend(b)
    elif (dest == "MSP"):
        b = [0, 0, 0, 1, 0]
        inputs.extend(b)
    elif (dest == "SEA"):
        b = [0, 0, 0, 0, 1]
        inputs.extend(b)

    prediction = preprocessAndPredict(inputs)
    # Pass prediction to prediction template
    print(inputs)
    return render_template('/result.html', prediction=prediction)


def preprocessAndPredict(inputs):
    test_data = np.array(inputs).reshape((1, 16))
    model_file = open('model.pkl', 'rb')


    trained_model = joblib.load(model_file)

    crs_sc = pickle.load(open('crs_scale.pkl', 'rb'))
    flnum_sc = pickle.load(open('flnum_scale.pkl', 'rb'))

    df = pd.DataFrame(data=test_data[0:, 0:],
                      columns=['FL_NUM', 'MONTH', 'DAY_OF_MONTH', 'DAY_OF_WEEK', 'DEP_DEL15', 'CRS_ARR_TIME',
                               'ORIGIN_ATL', 'ORIGIN_DTW', 'ORIGIN_JFK', 'ORIGIN_MSP', 'ORIGIN_SEA', 'DEST_ATL',
                               'DEST_DTW', 'DEST_JFK', 'DEST_MSP', 'DEST_SEA'])
    df[['FL_NUM']] = flnum_sc.transform(df[['FL_NUM']])
    df[['CRS_ARR_TIME']] = crs_sc.transform(df[['CRS_ARR_TIME']])

    data = df.values

    result = trained_model.predict(data)

    print(result)
    return result


if __name__ == '__main__':
    app.run(debug=True)



