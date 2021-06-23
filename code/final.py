from PIL import Image, ImageTk
import tkinter as tk
import cv2
import numpy as np
from keras.models import model_from_json
import operator
import matplotlib.pyplot as plt
import hunspell
from string import ascii_uppercase

class Application:
    def __init__(self):
        self.hs = hunspell.HunSpell('/home/brajesh/Documents/hunspell/en_US.dic', '/home/brajesh/Documents/hunspell/en_US.aff')
        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.current_image2 = None
        
        self.json_file = open("model-bw.json", "r")
        self.model_json = self.json_file.read()
        self.json_file.close()
        self.loaded_model = model_from_json(self.model_json)
        self.loaded_model.load_weights("model-bw.h5")

        self.json_file_dru = open("model-bw_dru.json" , "r")
        self.model_json_dru = self.json_file_dru.read()
        self.json_file_dru.close()
        self.loaded_model_dru = model_from_json(self.model_json_dru)
        self.loaded_model_dru.load_weights("model-bw_dru.h5")

        self.json_file_tkdi = open("model-bw_tkdi.json" , "r")
        self.model_json_tkdi = self.json_file_tkdi.read()
        self.json_file_tkdi.close()
        self.loaded_model_tkdi = model_from_json(self.model_json_tkdi)
        self.loaded_model_tkdi.load_weights("model-bw_tkdi.h5")

        self.json_file_smn = open("model-bw_smn.json" , "r")
        self.model_json_smn = self.json_file_smn.read()
        self.json_file_smn.close()
        self.loaded_model_smn = model_from_json(self.model_json_smn)
        self.loaded_model_smn.load_weights("model-bw_smn.h5")
        
        # GUI Formation
        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0
        for i in ascii_uppercase:
          self.ct[i] = 0
        print("Loaded model from disk")
        self.root = tk.Tk()
        self.root.title("User Interface")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.geometry("900x1100")

        self.panel = tk.Label(self.root) # Main window
        self.panel.place(x = 135, y = 10, width = 640, height = 640)

        self.panel2 = tk.Label(self.root) # initialize image panel
        self.panel2.place(x = 460, y = 95, width = 310, height = 310)
        
        self.T = tk.Label(self.root) 
        self.T.place(x=31,y = 17)
        self.T.config(text = "Sign Language Recognition",font=("courier",40,"bold"))

        self.panel3 = tk.Label(self.root) # Current Character
        self.panel3.place(x = 500,y=640)

        self.T1 = tk.Label(self.root) # Character
        self.T1.place(x = 10,y = 640)
        self.T1.config(text="Character :",font=("Courier",40,"bold"))

        self.panel4 = tk.Label(self.root) # Current Word
        self.panel4.place(x = 220,y=700)

        self.T2 = tk.Label(self.root) # Word
        self.T2.place(x = 10,y = 700)
        self.T2.config(text ="Word :",font=("Courier",40,"bold"))
        self.panel5 = tk.Label(self.root)
        
        self.T4 = tk.Label(self.root) # Sugesstions
        self.T4.place(x = 250,y = 820)
        self.T4.config(text = "Suggestions",fg="red",font = ("Courier",40,"bold"))

        self.bt1=tk.Button(self.root, command=self.action1,height = 0,width = 0)
        self.bt1.place(x = 26,y=890)

        self.bt2=tk.Button(self.root, command=self.action2,height = 0,width = 0)
        self.bt2.place(x = 325,y=890)
        
        self.bt3=tk.Button(self.root, command=self.action3,height = 0,width = 0)
        self.bt3.place(x = 625,y=890)
        
        self.bt4=tk.Button(self.root, command=self.action4,height = 0,width = 0)
        self.bt4.place(x = 125,y=950)
        
        self.bt5=tk.Button(self.root, command=self.action5,height = 0,width = 0)
        self.bt5.place(x = 425,y=950)
        
        self.str=""
        self.word=""
        self.current_symbol="Empty"
        self.photo="Empty"
        self.video_loop()

    def video_loop(self):
        ok, frame = self.vs.read()
        if ok:
            cv2image = cv2.flip(frame, 1)
            # ROI Coordinates
            x1 = int(0.5*frame.shape[1])
            y1 = 10
            x2 = frame.shape[1]-10
            y2 = int(0.5*frame.shape[1])
            cv2.rectangle(frame, (x1-1, y1-1), (x2+1, y2+1), (255,0,0) ,1)
            cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGBA)
            self.current_image = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)
            cv2image = cv2image[y1:y2, x1:x2]
            gray = cv2.cvtColor(cv2image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray,(5,5),2)
            th3 = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
            ret, res = cv2.threshold(th3, 70, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

            self.predict(res)    # predict is the function defined below
            self.current_image2 = Image.fromarray(res)
            imgtk = ImageTk.PhotoImage(image=self.current_image2)
            self.panel2.imgtk = imgtk
            self.panel2.config(image=imgtk)
            self.panel3.config(text=self.current_symbol,font=("Courier",50))
            self.panel4.config(text=self.word,font=("Courier",40))
            self.panel5.config(text=self.str,font=("Courier",40))
            predicts=self.hs.suggest(self.word)    # predicts will store the predicted suggestion by hunspell

            if(len(predicts) > 0):
                self.bt1.config(text=predicts[0],font = ("Courier",20))
            else:
                self.bt1.config(text="")
            if(len(predicts) > 1):
                self.bt2.config(text=predicts[1],font = ("Courier",20))
            else:
                self.bt2.config(text="")
            if(len(predicts) > 2):
                self.bt3.config(text=predicts[2],font = ("Courier",20))
            else:
                self.bt3.config(text="")
            if(len(predicts) > 3):
                self.bt4.config(text=predicts[3],font = ("Courier",20))
            else:
                self.bt4.config(text="")
            if(len(predicts) > 4):
                self.bt4.config(text=predicts[4],font = ("Courier",20))
            else:
                self.bt4.config(text="")                
        self.root.after(30, self.video_loop)

    def predict(self,test_image):
        test_image = cv2.resize(test_image, (128,128))
        result = self.loaded_model.predict(test_image.reshape(1, 128, 128, 1))
        result_dru = self.loaded_model_dru.predict(test_image.reshape(1 , 128 , 128 , 1))
        result_tkdi = self.loaded_model_tkdi.predict(test_image.reshape(1 , 128 , 128 , 1))
        result_smn = self.loaded_model_smn.predict(test_image.reshape(1 , 128 , 128 , 1))
        prediction={}
        prediction['blank'] = result[0][0]
        inde = 1     # inde is variable
        for i in ascii_uppercase:
            prediction[i] = result[0][inde]
            inde += 1

        #LAYER 1
        prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        self.current_symbol = prediction[0][0]
        
        #LAYER 2
        if(self.current_symbol == 'D' or self.current_symbol == 'R' or self.current_symbol == 'U'):
        	prediction = {}
        	prediction['D'] = result_dru[0][0]
        	prediction['R'] = result_dru[0][1]
        	prediction['U'] = result_dru[0][2]
        	prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        	self.current_symbol = prediction[0][0]

        if(self.current_symbol == 'D' or self.current_symbol == 'I' or self.current_symbol == 'K' or self.current_symbol == 'T'):
        	prediction = {}
        	prediction['D'] = result_tkdi[0][0]
        	prediction['I'] = result_tkdi[0][1]
        	prediction['K'] = result_tkdi[0][2]
        	prediction['T'] = result_tkdi[0][3]
        	prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        	self.current_symbol = prediction[0][0]

        if(self.current_symbol == 'M' or self.current_symbol == 'N' or self.current_symbol == 'S'):
        	prediction1 = {}
        	prediction1['M'] = result_smn[0][0]
        	prediction1['N'] = result_smn[0][1]
        	prediction1['S'] = result_smn[0][2]
        	prediction1 = sorted(prediction1.items(), key=operator.itemgetter(1), reverse=True)
        	if(prediction1[0][0] == 'S'):     ###############
        		self.current_symbol = prediction1[0][0] ################
        	else: #################
        		self.current_symbol = prediction[0][0] #############
        if(self.current_symbol == 'blank'):
            for i in ascii_uppercase:
                self.ct[i] = 0
        self.ct[self.current_symbol] += 1
        if(self.ct[self.current_symbol] > 20):
            for i in ascii_uppercase:
                if i == self.current_symbol:
                    continue
                tmp = self.ct[self.current_symbol] - self.ct[i]
                if tmp < 0:
                    tmp *= -1
                if tmp <= 10:
                    self.ct['blank'] = 0
                    for i in ascii_uppercase:
                        self.ct[i] = 0
                    return
            self.ct['blank'] = 0
            for i in ascii_uppercase:
                self.ct[i] = 0
            if self.current_symbol == 'blank':
                if self.blank_flag == 0:
                    self.blank_flag = 1
                    if len(self.str) > 0:
                        self.str += " "
                    self.str += self.word
                    self.word = ""
            else:
                if(len(self.str) > 10):
                    self.str = ""
                self.blank_flag = 0
                self.word += self.current_symbol

    def action1(self):
    	predicts=self.hs.suggest(self.word)
    	if(len(predicts) > 0):
            self.word=""
            self.str+=" "
            self.str+=predicts[0]
    def action2(self):
    	predicts=self.hs.suggest(self.word)
    	if(len(predicts) > 1):
            self.word=""
            self.str+=" "
            self.str+=predicts[1]
    def action3(self):
    	predicts=self.hs.suggest(self.word)
    	if(len(predicts) > 2):
            self.word=""
            self.str+=" "
            self.str+=predicts[2]
    def action4(self):
    	predicts=self.hs.suggest(self.word)
    	if(len(predicts) > 3):
            self.word=""
            self.str+=" "
            self.str+=predicts[3]
    def action5(self):
    	predicts=self.hs.suggest(self.word)
    	if(len(predicts) > 4):
            self.word=""
            self.str+=" "
            self.str+=predicts[4]
    def destructor(self):
        print("Closing Application...")
        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()
    

print("Starting Application...")
pba = Application()
pba.root.mainloop()