import time
from numpy import pi, cos, sin, dot, matrix, transpose, cross, hstack, linalg
import numpy as np
from math import sqrt


class Kinematyka:
    def __init__(self):
        self.Theta = {1: 0, 2: 0, 3: 0, 4: 0}
        self.a = {1: 6, 2: 10.5, 3: 9.5, 4: 3.5, 5: -1.7}
        self.alfa = {1: 90, 2: 0, 3: 0, 4: -90, 5:0}
        a = self.a
        self.r = {1: 0, 2: a[2], 3: a[3], 4: a[4], 5: 0}
        self.d = {1: a[1], 2: 0, 3: 0, 4: 0, 5: a[5]}

    def mnozenie(self,H):
        H0_1 = matrix(H["01"])
        H0_2 = dot(H["01"], H["12"])
        H0_3 = dot(H0_2,    H["23"])
        H0_4 = dot(H0_3,    H["34"])
        H0_5 = dot(H0_4,    H["45"])
        H_mult = {1:H0_1, 2:H0_2, 3:H0_3, 4:H0_4, 5:H0_5}
        return H_mult

    def macierze_DH(self,T,alfa):
        r = self.r
        d = self.d

        H = {} #zmienna do przechowywania macierzy przekształceń w postaci
               #słownika, gdzie kluczem jest "01", "12", "23" itd.
        T[5] = 0 #dodanie 5 miejsca w tabeli dla theta
        for n in range (1,6): #macierze H
            numer = str(n-1)+ str(n)
            #wn - wiersze do wprowadzenia do macierzy H
            w1 = [cos(T[n]), -sin(T[n])*cos(alfa[n]), sin(T[n])*sin(alfa[n]), r[n]*cos(T[n])]
            w2 = [sin(T[n]), cos(T[n])*cos(alfa[n]), -cos(T[n])*sin(alfa[n]), r[n]*sin(T[n])]
            w3 = [0, sin(alfa[n]), cos(alfa[n]), d[n]]
            w4 = [0, 0, 0, 1]
            H[numer] = [w1, w2, w3, w4]
        return H

    def stopnie_na_rad(self,alfa,theta):
        T = {} #słownik dla kątów theta
        for x in range (1,6): #zamiana kątów alfa na radiany
            alfa[x] = (alfa[x]/180)*pi
        for x in range (4):
            theta[x] = (theta[x]/180)*pi #zamiana kątów theta na radiany
        for x in range(1,5): #zamiana listy na słownik
            T[x] = theta[x-1] #kąty theta są teraz w słowniku od 1 do 4
        return alfa, T

class Prosta(Kinematyka):

    def oblicz(self,theta):
        theta = list(theta) #zamiana krotki na liste aby mozna bylo przeksztalcac
        alfa = self.alfa
        alfa, T = self.stopnie_na_rad(alfa,theta)
        H = self.macierze_DH(T,alfa) #funkcja DH
        H_mult = self.mnozenie(H)
        H0_5 = H_mult[3]
        x = round(H0_5[0,-1], 1)
        y = round(H0_5[1,-1], 1)
        z = round(H0_5[2,-1], 1)
        polozenie = (x,y,z)
        return polozenie

class Odwrotna(Kinematyka):

    def zaleznosci_x(self,polozenie):
        x,y,z = polozenie
        Theta = {} #słownik kątów Theta
        R = {}

        if x == 0.0:
            Theta[1] = pi/2
            R[1] = y
        if x < 0:
            Theta[1] = pi/2 + np.arctan(y/x) + pi/2
            R[1] = sqrt( pow(x,2) + pow(y,2) )
        if x > 0:
            Theta[1] = np.arctan(y/x)
            R[1] = sqrt( pow(x,2) + pow(y,2) )
        return Theta, R

    def zaleznosci_z(self,z,a,R,Fi,T):
        if z == 0.0:
            T[2] = np.arccos( ( pow(R[1],2) + pow(a[2],2) - pow(a[3],2) ) / (2*R[1]*a[2]) )
        if z >0:
            T[2] = Fi[2] + Fi[1]
        if z <0:
            T[2] = Fi[2] - abs(Fi[1])
        return T

    def oblicz(self,polozenie):
        x, y, z = polozenie
        T, R = self.zaleznosci_x(polozenie)
        a = self.a
        z = z-a[1]
        Fi = {}
        R[2] = sqrt(pow(z,2) + pow(R[1],2))
        Fi[1] = np.arctan(z/R[1])
        Fi[2] = np.arccos( ( pow(a[2],2) + pow(R[2],2) - pow(a[3],2) ) / ( 2*a[2]*R[2] ))
        Fi[3] = np.arccos((pow(a[2],2) + pow(a[3],2) - pow(R[2],2))  / ( 2*a[2]*a[3]) )
        T = self.zaleznosci_z(z,a,R,Fi,T)
        T[3] = -(pi-Fi[3])
        T[4] = -T[3]-T[2]

        for x in range(1,5): #zamiana kątów Theta na stopnie
            T[x] = (T[x]/pi)*180
        T = (T[1],T[2],T[3],T[4]) #zamiana słownika na krotkę
        return T

class Predkosc(Kinematyka):

    def jakobian(self, H_mult):
        H0_1 = H_mult[1]
        H0_2 = H_mult[2]
        H0_3 = H_mult[3]

        R0_1 = H0_1[:3,:3]
        R0_2 = H0_2[:3,:3]

        d0_1 = matrix([[H0_1[0,-1]], [H0_1[1,-1]], [H0_1[2,-1]]])
        d0_2 = matrix([[H0_2[0,-1]], [H0_2[1,-1]], [H0_2[2,-1]]])
        d0_3 = matrix([[H0_3[0,-1]], [H0_3[1,-1]], [H0_3[2,-1]]])

        wektor001 = [0,0,1]
        d = transpose(d0_3)
        J1 = transpose(cross(wektor001, d))
        J2 = transpose(cross(dot(R0_1,wektor001),transpose(d0_3-d0_1)))
        J3 = transpose(cross(dot(R0_2,wektor001),transpose(d0_3-d0_2)))
        return J1,J2,J3
    
    def kierunek(self,P1,P2):
        
        P1 = np.array(P1)
        P2 = np.array(P2)
        kierunek = np.subtract(P2,P1)
        x1,y,z = P1
        x2,y,z = P2
        if x1 == 0:
            if x2 >x1:
                x1=0.5
            else:
                x1=-0.5
            P1 = (x1,y,z)   
        for i in range(3):
            if np.any(kierunek[i]) != 0:
                kierunek[i] = 8
                if i == 0:
                    kierunek[i] = 8
        return kierunek
            
    def oblicz(self,Poz_akt,P1,P2):
        P1 = list(P1)
        P2 = list(P2)
        Poz_akt = list(Poz_akt)
        V_3 = self.kierunek(P1,P2)
        
        alfa = self.alfa
        alfa, T = self.stopnie_na_rad(alfa,Poz_akt)
        H = self.macierze_DH(T,alfa)
        H_mult = self.mnozenie(H)

        J1, J2, J3 = self.jakobian(H_mult)
        Jakobian = hstack((J1,J2,J3))
        Jakobian_odw = linalg.inv(Jakobian)
         #Słownik dla prędkości członu 3       

        T_dot1 = round(abs(Jakobian_odw[0,0]*V_3[0]+Jakobian_odw[0,1]*V_3[1]+Jakobian_odw[0,2]*V_3[2]),6)
        T_dot2 = round(abs(Jakobian_odw[1,0]*V_3[0]+Jakobian_odw[1,1]*V_3[1]+Jakobian_odw[1,2]*V_3[2]),6)
        T_dot3 = round(abs(Jakobian_odw[2,0]*V_3[0]+Jakobian_odw[2,1]*V_3[1]+Jakobian_odw[2,2]*V_3[2]),6)
        #T_dot3 = T_dot3 + T_dot2
        T_dot = [T_dot1,T_dot2,T_dot3]
        return T_dot #predkosci serw

if __name__ == '__main__':


    kin = Kinematyka()
    predkosc = Predkosc()
    prosta = Prosta()
    odwrotna = Odwrotna()
    poz = {}
    poz[0] = (90,20,-30,0)

    V = predkosc.oblicz(poz[0],"y")
    print(V)

    x,y,z = prosta.oblicz(poz[0])
    pozycja = (x,y,z)
    print("x,y,z: ",pozycja)

    k = odwrotna.oblicz(pozycja)
    print("kąty: ",k)
