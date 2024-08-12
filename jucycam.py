
from flask import Flask, render_template, Response, url_for, redirect
from PIL import ImageFont, ImageDraw, Image
import datetime
import cv2
import numpy as np


ip = "192.168.212.192"
app = Flask(__name__)
global is_capture, is_record, start_record           
capture = cv2.VideoCapture(-1)                      
fourcc = cv2.VideoWriter_fourcc(*'XVID')           
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
font = ImageFont.truetype('project/fonts/SCDream6.otf', 20)
is_record = False
is_capture = False
start_record = False  
on_record = False                                 
cnt_record = 0     
max_cnt_record = 5
face_cascade = cv2.CascadeClassifier('project/haarcascade/haarcascade_frontalface_default.xml')

def gen_frames():  
    global is_record, start_record, is_capture, video, video_name, on_record, cnt_record, max_cnt_record
    while True:                                    
        now = datetime.datetime.now()                     
        nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S') 
        nowDatetime_path = now.strftime('%Y-%m-%d %H_%M_%S')
        ref, frame = capture.read()  
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor= 1.5, minNeighbors=3, minSize=(20,20))

        if len(faces) :
            is_record = True    
            if on_record == False:
                video = cv2.VideoWriter("project/cctv_data/얼굴인식" + nowDatetime_path + ".avi", fourcc, 1, (frame.shape[1], frame.shape[0]))
            cnt_record = max_cnt_record

        if is_record == True:  
            video.write(frame)   
            cnt_record -= 1     
            on_record = True    
        if cnt_record == 0:     
            is_record = False   
            on_record = False


        if not ref:                     
            break                      
        else:
            frame = Image.fromarray(frame)    
            draw = ImageDraw.Draw(frame)    
             
            draw.text(xy=(10, 15),  text="주시캠"+nowDatetime, font=font, fill=(255, 255, 255))
            frame = np.array(frame)
            ref, buffer = cv2.imencode('.jpg', frame)            
            frame1 = frame              
            frame = buffer.tobytes()
            
            if start_record == True and is_record == False: 
                is_record = True           
                start_record = False      
               
                video_name = "project/cctv_data/녹화" + nowDatetime_path + ".mp4"
                video = cv2.VideoWriter(video_name, fourcc, 15, (frame1.shape[1], frame1.shape[0]))
            elif start_record and is_record == True: 
                is_record = False       
                start_record = False
                video.release()        
            elif is_capture:      
               
                is_capture = False
                cv2.imwrite("project/cctv_data/capture" + nowDatetime_path + ".png", frame1)  
            if is_record == True:                 
                
                video.write(frame1)
    
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 

@app.route('/')
def index():
    global is_record
    return render_template('index4#6.html', is_record=is_record)           

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/push_record')
def push_record():                   
    global start_record                 
    start_record = not start_record   
    return redirect(url_for('index'))

@app.route('/push_capture')
def push_capture():                   
    global is_capture                 
    is_capture = True                  
    return redirect(url_for('index'))

if __name__ == "__main__":  
    app.run(host=ip, port = "8080")
   
