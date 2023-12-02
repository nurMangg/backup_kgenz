# Importing required libs
from keras.models import load_model
from keras.utils import img_to_array
import numpy as np
import os
from PIL import Image
from skimage.transform import resize
from flask import Flask

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Loading model
model = load_model(os.path.join(os.path.dirname(__file__), 'models/model2.h5'))
 
 
# Preparing and pre-processing the image
def preprocess_img(img_path):
    op_img = Image.open(img_path)
    # img = op_img.resize((48, 48))
    img = op_img.convert('L')
    img = img.resize((48, 48))
    # img.save(os.path.join(app.config['UPLOAD_FOLDER'], "prep.png"))
    img = np.array(img)
    img = np.expand_dims(img, axis=0)
    img = img.reshape(1,48, 48,1)
    
    return img
 
 
# Predicting function
def predict_result(predict):
    pred = model.predict(predict)
    predicted = np.argmax(pred, axis=-1)
    return predicted
