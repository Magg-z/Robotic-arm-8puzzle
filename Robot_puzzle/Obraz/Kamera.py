#!/usr/bin/python3
import cv2
import time
import numpy as np
from image_slicer import slice
from numpy import cos, sin, pi
import evdev
from evdev import InputDevice, categorize, ecodes
# import random as rng
# import imutils
# from matplotlib import pyplot as plt
# import re
# from keras.models import load_model
# from keras.preprocessing.image import array_to_img, img_to_array,load_img

class Kamera:

    def zdjecie(self,nazwa):
        kamera = cv2.VideoCapture(0)
        x = 0
        while True:
            _, frame = kamera.read()
            key = cv2.waitKey(1)
            if x==20:
                cv2.imwrite( "puzzle_rgb.png", frame )
                break
            x+=1

        kamera.release()
        cv2.destroyAllWindows()
        frame = cv2.imread("puzzle_rgb.png")
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        threshold = cv2.adaptiveThreshold(gray,255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 3)
        cv2.imwrite( nazwa, threshold )
   
    def przycisk(self):
        self.key = 27
        
    def film(self):
        kamera = cv2.VideoCapture(0)
        kam = InputDevice('/dev/input/event5')
        while True:
            check, frame = kamera.read()
            frame = cv2.resize(frame, (200, 200))
            #cv2.imshow("nosiema", frame)
            #key = cv2.waitKey(5)
            for event in kam.read_loop():
                if event.type == ecodes.EV_KEY:
                    if event.value == 1:
                        if event.code == 212:
                            break
            break
        kamera.release()
        cv2.destroyAllWindows()
            #if key == 27:
                #break
        

    def transformacja(self,Poz):
        R180_x = np.matrix([[1,0,0],[0,-1,0],[0,0,-1]])
        R180_z = np.matrix([[-1,0,0],[0,-1,0],[0,0,1]])
        d0_C = np.matrix([[6.5],[10.5],[0]])
        R0_C = np.matrix([[-1,0,0],[0,1,0],[0,0,-1]])
        #R0_C = np.dot(R180_x,R180_z)
        #R0_C = [[1,0,-1],[0,-1,0],[0,0,-1]]

        H0_C = np.concatenate((R0_C,d0_C),1)
        H0_C = np.concatenate((H0_C,[[0,0,0,1]]),0)
        x = Poz[0]
        y = Poz[1]
        Poz_C = [[x],[y],[0],[1]]
        Poz_B = np.dot(H0_C,Poz_C)
        x_B = Poz_B[0]
        y_B = Poz_B[1]
        return(Poz_B)

    def px_cm(self,P):
        przelicznik = 0.02325
        Poz_B = {}
        Poz = {}
        pozycja = {}
        for x in P:
            P[x] = list(P[x])
            Poz[x]  = [y* przelicznik for y in P[x]]
            print(Poz[x],"przed zamiana w cm")
            Poz_B[x] = self.transformacja(Poz[x])
            x_B = int(Poz_B[x][0])
            y_B = int(Poz_B[x][1])
            pozycja[x] = (x_B, y_B-3.4, 8)
        return pozycja

    def pozycje(self,x,y,w,h):
        P = {}
        m0 = 5/6
        m1 = 0.5
        m2 = 1/6 
        P[0] = (x + m0 * w, y + m0 * h)
        P[1] = (x + m1 * w, y + m0 * h)
        P[2] = (x + m2 * w, y + m0 * h)
        P[3] = (x + m0 * w, y + m1 * h)
        P[4] = (x + m1 * w, y + m1 * h)
        P[5] = (x + m2 * w, y + m1 * h)
        P[6] = (x + m0 * w, y + m2 * h)
        P[7] = (x + m1 * w, y + m2 * h)
        P[8] = (x + m2 * w, y + m2 * h)
        print("pozycje puzzli przed zamiana: ")
        print(P[0])
        print(P[1])
        print(P[2])
        print(P[3])
        print(P[4])
        print(P[5])
        print(P[6])
        print(P[7])
        print(P[8])
        return P

    def szukaj(self):
        puzzle_rgb = cv2.imread("puzzle_rgb.png")
        puzzle = cv2.imread("puzzle.png",0)
        puzzle_ROI = cv2.imread("puzzle_rgb.png")
        contours, hierarchy = cv2.findContours(puzzle, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE   )
        Pozycja_B = 0
        for contour in contours:
            [x, y, w, h] = cv2.boundingRect(contour)
            if w<400 or h<400:
                continue
            cv2.rectangle(puzzle_rgb, (x, y), (x + w, y + h), (255, 0, 255), 2)
            P = self.pozycje(x, y, w, h)
            Pozycja_B = self.px_cm(P)
            ROI = puzzle_ROI[y:y+h,x:x+w]
            ROI = cv2.rotate(ROI, cv2.ROTATE_180)
            
            cv2.imwrite( "ROI.png", ROI )
            slice("ROI.png",9)
        # write original image with added contours to disk
        cv2.imwrite( "kontury.png", puzzle_rgb )
        return Pozycja_B

if __name__=='__main__':
    kam = Kamera()
    #kam.film()
    kam.zdjecie("puzzle.png")
# #
    P =kam.szukaj()
    print(P)