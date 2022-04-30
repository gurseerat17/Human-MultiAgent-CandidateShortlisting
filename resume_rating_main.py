from glob import glob
import os
from flask import Flask, flash, request, redirect, render_template,url_for
from constants import file_constants as cnst
from processing import resume_matcher
from utils import file_utils
from PersonalityPrediction import main 

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','docx'])
app = Flask(__name__)
app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = cnst.UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getA(x, y, B):
   return 1 if ( w1*x + w2*y > threshold ) else B

def human_model(result_jobfit,result_personality):
   
   global conf_jobfit
   global conf_personalityfit
   global w1, w2, threshold, l

   conf_jobfit = 1.0
   conf_personalityfit = 1.0

   h_jobfit =  result_jobfit*conf_jobfit
   h_personality =  result_personality*conf_personalityfit

   B = -1
   w1 =  0.75
   w2 = 0.25
   #TODO
   threshold = 0.5
   l = 0.8
   
   print("\n\n----", (h_jobfit*h_personality) , h_jobfit*(1-h_personality)*getA(h_jobfit, 1-h_personality,B) , h_personality*(1-h_jobfit)*getA( 1-h_jobfit, h_personality, B) , (1-h_jobfit)*(1-h_personality)*B ,"\n",getA(h_jobfit, 1-h_personality,B) ,getA( 1-h_jobfit, h_personality, B), "\n\n\n\n----------")

   E_accept = (h_jobfit*h_personality) + h_jobfit*(1-h_personality)*getA(h_jobfit, 1-h_personality,B) + h_personality*(1-h_jobfit)*getA( 1-h_jobfit, h_personality, B) + (1-h_jobfit)*(1-h_personality)*B

   #TODO : accuracy of human taken as 1
   E_solve = 1 - l 

   return E_accept, E_solve

@app.route('/')
def upload_form():
    return render_template('resume_loader.html')

@app.route('/failure')
def failure():
   return 'No files were selected'

@app.route('/success/<name>')
def success(name):
   return 'Files %s has been selecte3d' %name

@app.route('/', methods=['POST', 'GET'])
def check_for_file():
   
   if request.method == 'POST':
        # check if the post request has the file part
        if 'reqFile' not in request.files:
           flash('Requirements document can not be empty')
           return redirect(request.url)
        if 'resume_file' not in request.files:
           flash('Select at least one resume File to proceed further')
           return redirect(request.url)
        file = request.files['reqFile']
        if file.filename == '':
           flash('Requirement document has not been selected')
           return redirect(request.url)
        resume_file = request.files['resume_file']
        if ((file and allowed_file(file.filename)) and resume_file):
           #filename = secure_filename(file.filename)
           abs_paths = []
           filename = file.filename
        #    req_document = os.path.join(app.config['UPLOAD_FOLDER'], filename)
           req_document = cnst.UPLOAD_FOLDER+'\\'+filename
           file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
           filename = resume_file.filename
           abs_paths.append(cnst.UPLOAD_FOLDER + '\\' + filename)
           resume_file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
           result_jobfit = resume_matcher.process_files(req_document,abs_paths)
           
           name=request.form['name']
           age=request.form['age']
           gender=request.form['gender']
           openness=request.form['openness']
           neuroticism=request.form['neuroticism']
           conscientiousness=request.form['conscientiousness']
           agreeableness=request.form['agreeableness']
           extraversion=request.form['extraversion']
         
           result_trait,result_personalityconf= main.prediction_result(name,abs_paths,(gender,age,openness,neuroticism,conscientiousness,agreeableness,extraversion))
        #    for file_path in abs_paths:
            #    file_utils.delete_file(file_path)
           
           E_accept, E_solve = human_model(result_jobfit[0][1], result_personalityconf)
           

           return render_template("resume_results.html", result_jobfit=result_jobfit, result_personality=[result_trait,result_personalityconf], E_accept = E_accept, E_solve = E_solve)
        else:
           flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
           return redirect(request.url)

if __name__ == "__main__":
    app.run(debug = True)