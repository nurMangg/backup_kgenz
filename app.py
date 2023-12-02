from flask import Flask, render_template, request, redirect, Response, url_for
import os
from PIL import Image
import base64
import io

# import tensorflow
from tensorflow.keras.models import load_model

#Model
from model import preprocess_img, predict_result
from model_chatbot import chatbot_response

# Database
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, and_


class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fullname: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password : Mapped[str] = mapped_column(String, nullable=False)
    
with app.app_context():
    db.create_all()

@app.route("/list")
def list():
    users = db.session.execute(db.select(User).order_by(User.id)).scalars()
    return render_template("user/list.html", users = users)

@app.route("/", methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        
        if db.session.query(User).filter(and_(User.email==request.form['email'], User.password==request.form['password'])).first() is not None:
            return redirect(url_for('beranda'))
        else :
            return render_template('user/index.html')
    
    if request.method == 'GET':
        view = "K-Genz | Login"
        return render_template("user/index.html", active = view)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            fullname = request.form['fullName'],
            email = request.form['email'],
            password = request.form['password'],
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('beranda'))
    
    
    view = "K-Genz | Register"
    return render_template("user/register.html", active = view)

@app.route("/beranda")
def beranda():
    view = "beranda"
    return render_template("user/beranda.html", active = view)
    
@app.route("/artikel")
def artikel(): 
    view = "artikel"
    return render_template("user/artikel.html", active = view)

@app.route("/layanan")
def layanan():
    view = "layanan"
    return render_template("user/layanan.html", active = view)

@app.route("/capture-layanan")
def camera():
    return render_template("user/viewCaptureCamera.html")



@app.route("/chatbot")
def chatbot():
    return render_template("user/chatbot.html")

@app.route("/chatbot_res")
def get_bot_response():
    userText = request.args.get('msg')
    return chatbot_response(userText)

@app.route("/history")
def history():
    return render_template("user/history.html")

@app.route("/profil")
def profil():
    view = "profil"
    return render_template("user/profil.html", active = view)

@app.route('/uploadfile', methods=['POST'])
def upload_file():
    try:
        if request.method == 'POST':
            image = request.files['file']
            if image.filename != '':
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
                sh_img = image.filename
            img = preprocess_img(request.files['file'].stream)
            pred = predict_result(img)
            return render_template("user/resultCapture.html", sh_img=sh_img, predict=str(pred))
    except Exception as e:
        error = f"An error occurred: {str(e)}"
        return render_template("user/viewCaptureCamera.html", message=error)
    
    
@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    if data and 'image' in data:
        img_data = data['image'].split(',')[1]
        image = Image.open(io.BytesIO(base64.b64decode(img_data)))
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], "capture-camera.png"))
        img = preprocess_img(io.BytesIO(base64.b64decode(img_data)))
        pred = predict_result(img)
        return 'success', 200
    return 'Error', 400

@app.route('/predict')
def predict():
    img = preprocess_img(os.path.join(app.config['UPLOAD_FOLDER'], "capture-camera.png"))
    pred = predict_result(img)
    return render_template("user/resultCapture.html", sh_img="capture-camera.png", predict=str(pred))
    
if __name__ == '__main__':
	app.run(debug=True)