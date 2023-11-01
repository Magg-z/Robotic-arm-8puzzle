from Ruch.Kinematyka import Predkosc, Prosta
from Ruch.PCA9685 import PCA9685
import time
import numpy as np


class Serwo:
    '''
    Klasa zawierająca funkcje związane z ruchem manipulatora.
    '''
    def __init__(self,poz_1,V= [0.3,0.3,0.3,0.3]):
        self.poz_1 = poz_1
        self.W_zakres = { 1: (2440,500), 2: (500,2400), 3: (420,2450), 4: (2420,600) } #kolejność 1. górne 2. dolne
        self.A_180 = (180,0)
        self.A_180_inv = (-180,0)
        self.A_90 = (90, -90)
        self.V = V
        self.V2 = V
        self.pwm_start()

    def pwm_start(self):
        '''
        Inicjalizacja klasy sterownika PCA9685
        '''
        self.pwm = PCA9685(0x40, debug=False)
        self.pwm.setPWMFreq(50)

    def oblicz_wypelnienie(self,A):
        '''
        Funkcja oblicza wartość wypełnienia "W" PWM
        dla podanego kąta alfa "A" w stopniach
        '''
        W = [0,0,0,0]
        W_zakres = self.W_zakres
        for i in range(0,4):
            if i == 0 :
                A_zakres = self.A_180
            elif i == 2:
                A_zakres = self.A_180_inv
            else:
                A_zakres = self.A_90

            A_max = A_zakres[0]
            A_min = A_zakres[1]
            W_max = W_zakres[i+1][0]
            W_min = W_zakres[i+1][1]

            wyp = ((W_max - W_min) / (A_max - A_min)) * (A[i] - A_min) + W_min
            W[i] = wyp
        return W

    def ustaw_predkosc(self,V):
        '''
        Możliwość zmiany domyślnej prędkości serwonapędów
        '''
        self.V = [V,V,V,V]

    def oblicz_predkosc_poz1(self,poz2):
        '''
        Obliczenie i ustawienie prędkości serwonapędów dla poprzedniej pozycji
        za pomocą jakobianu, w celu wykonania ruchu liniowego
        '''
        poz1= self.poz_1
        predkosc = Predkosc()
        prosta = Prosta()
        P1 = prosta.oblicz(poz1)
        prosta = Prosta()
        P2 = prosta.oblicz(poz2)
        V = predkosc.oblicz(poz1,P1,P2)
        self.V = V
        k1,k2,k3,k4 = poz1
        k1 = round(k1,1)
        k2 = round(k2,1)
        k3 = round(k3,1)
        k4 = round(k4,1)
        poz11 = (k1,k2,k3,k4)
        print("POPRZEDNI")
        print("odwrotna", poz11)
        print( "Predkosc: ",V)
        print("-----------------")
        return V

    def ustaw_pwm(self,P):
        '''
        Funkcja ustawiająca pozycje serwonapędów od wypełnienia pozycji P
        '''
        pwm = self.pwm
        P=self.oblicz_wypelnienie(P)
        pwm.setServoPulse(0, P[0])
        pwm.setServoPulse(1, P[1])
        pwm.setServoPulse(2, P[2])
        pwm.setServoPulse(3, P[3])
        time.sleep(0.001)

    def zmiana_wypelnienia(self,P1,P2,V):
        '''
        Funkcja prędkości. Wykonywana jest inkrementacja lub dekrementacja
        stopni o określoną wartość prędkości V, dla każdego z serw.
        '''
        while(1):
            #print("P1",round(P1[0],2),round(P1[1],2),round(P1[2],2),round(P1[3],2),"P2",round(P2[0],2),round(P2[1],2),round(P2[2],2),round(P2[3],2))


            for x in range(3):

                if P1[x] < P2[x]:
                    if x == 2:
                        V[x] += V[x]*0.03
                    elif x == 1:
                        V[x] += V[x]*0.02
#                     elif x == 0:
#                         V[x] -= V[x]*0.005

                    P1[x] += V[x]
                    diff = P2[x] - P1[x]
                    if abs(diff) < abs(V[x]):
                        P1[x] += diff
                if P1[x] > P2[x]:
                    if x == 1:
                        V[x] += V[x]*0.02
                    elif x == 2:
                        V[x] += V[x]*0.01
                    P1[x] -= V[x]
                    diff = P1[x] - P2[x]
                    if abs(diff) < abs(V[x]):
                        P1[x] -= diff
            P1[3] = -P1[2]-P1[1]-1
            self.ustaw_pwm(P1)
            if np.all(P1[:3] == P2[:3]):
                break

    def ustaw_poz(self,pozycje):
        '''
        Funkcja ustawia manipulator na określoną pozycję
        '''
        V = self.V
        P1 = list(self.poz_1)
        P2 = list(pozycje)
        self.zmiana_wypelnienia(P1,P2,V)
        
        # -- Przypisanie ostatniej pozycji jako początkowej -- #
        self.poz_1 = pozycje

class Pozycje:
    '''
    Klasa do przechowywania pozycji manipulatora wraz z funkcjami do ich
    dodawania i kasowania. Pozycje przechowywane są w słowniku "poz".
    '''
    def __init__(self):
        # -- Przechowywane pozycje xyz -- #
        self.poz = {}
        self.poz["start"] = (0.5,6,10)
       
    def dodaj_puzzle(self,puzzle):
        for x in puzzle:
            self.poz[x] = puzzle[x]
            
    def puzzle(self,poz,z):
        poz2 = (poz[0],poz[1],z)
        return poz2
        
    def dodaj(self, nowa_poz):
        # -- Automatyczne przypisanie numeru według długości słownika -- #
        numer = len(self.poz)
        self.poz[numer] = nowa_poz

    def kasuj(self, nr_poz):
        usun = self.poz
        # -- None - Jeżeli nie ma takiej pozycji to nie wyrzuci błędu -- #
        usun.pop(nr_poz, None)


if __name__ == '__main__':
    poz = Pozycje()
    serwo = Serwo(poz.poz["start"])
#     serwo.zmiana_wypelnienia([90,55,-100,65],[90,80,-100,65],[0.5,0.5,0.5,0.5])
#     time.sleep(2)
#     serwo.zmiana_wypelnienia([90,80,-100,65],[90,55,-100,65],[0.5,0.5,0.5,0.5])
# #     time.sleep(2)
# #     serwo.zmiana_wypelnienia([90,55,-100,65],[0,55,-100,65],[0.5,0.5,0.5,0.5])
# #     time.sleep(2)
# #     serwo.zmiana_wypelnienia([0,55,-100,65],[90,55,-100,65],[0.5,0.5,0.5,0.5])
# 