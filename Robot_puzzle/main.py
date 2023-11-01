#!/usr/bin/python3
import cv2
import evdev
from evdev import InputDevice, categorize, ecodes
from Ruch.Serwo import Serwo, Pozycje
from Ruch.Kinematyka import Prosta, Odwrotna, Predkosc
from Obraz.Kamera import Kamera
import Obraz.Rozpoznawanie as rozpoznawanie
from Puzzle.Puzzle import Puzzle
from time import sleep
import numpy as np

class Start:
    
    def __init__(self,model,startowa="start"):
        self.serwo(startowa)
        self.model = model
        self.oczekiwanie()
        self.kamera()
        self.puzzle()
        
    def serwo(self,startowa):
        '''
        Funkcja inicjuje klasę Serwo od pozycji początkowej
        zapisanej w klasie Pozycje.
        '''
        # ----- Inicjalizacja klas  -----  ##
        pozycje = Pozycje()
        odwrotna = Odwrotna()

        # ----- Obliczenie kątów dla startowej pozycji -----  ##
        T = odwrotna.oblicz(pozycje.poz[startowa])
        p = 0.3 #predkosc
        self.p = p
        self.serwo = Serwo(T,[p,p,p,p])
        
    def oczekiwanie(self):
        kamera = Kamera()
        kamera.film()
        '''
        kam = InputDevice('/dev/input/event5')
        kamera = cv2.VideoCapture(0)
        while True:
            check, frame = kamera.read()
            frame = cv2.resize(frame, (200, 200))
            cv2.imshow("nosiema", frame)
            key = cv2.waitKey(5)
            for event in kam.read_loop():
                if event.type == ecodes.EV_KEY:
                    if event.value == 1:
                        if event.code == 212:
                            break
        kamera.release()
        cv2.destroyAllWindows()
        '''
    def kamera(self):
        '''
        Funkcja inicjuje klasę Kamera, która wykonuje zdjęcie. Następnie
        wykrywa pozycje poszczególnych pól i przekazuje je klasie Pozycje.
        Na koniec uruchamiana jest biblioteka rozpoznawania cyfr i zapisywana
        jest ich sekwencja.
        '''
        # ----- Inicjalizacja klas  -----  ##
        kamera = Kamera()
        pozycje = Pozycje()

        # ----- Wykonanie zdjęcia oraz zapisanie pozycji -----  ##
        kamera.zdjecie("puzzle.png")
        puzzle_pozycje = kamera.szukaj()
        pozycje.dodaj_puzzle(puzzle_pozycje)
        print("Pozycje puzzli: ")
        print(puzzle_pozycje[0])
        print(puzzle_pozycje[1])
        print(puzzle_pozycje[2])
        print(puzzle_pozycje[3])
        print(puzzle_pozycje[4])
        print(puzzle_pozycje[5])
        print(puzzle_pozycje[6])
        print(puzzle_pozycje[7])
        print(puzzle_pozycje[8])
        #print("Pozycje ze slownika: ",pozycje.poz)
        self.pozycje = pozycje

        # ----- Rozpoznanie cyfr i zapisanie sekwencji -----  ##
        model, classes = self.model
        self.kolejnosc = rozpoznawanie.start(model,classes)

    def ruch(self,poz,liniowy=0):
        '''
        Funkcja pobiera informację o położeniu xyz z klasy Pozycje,
        oblicza kąty Theta za pomocą klasy Odwrotna. Umożliwia ruch domyślny
        (Jedna prędkość dla wszystkich złącz) oraz ruch liniowy
        (Prędkości złącz obliczone przez klasę Predkosc).
        '''
        # ----- Inicjalizacja klas  -----  ##
        odwrotna = Odwrotna()
        predkosc = Predkosc()
        prosta = Prosta()
        serwo = self.serwo
        # ----- Obliczenie kątów dla docelowej pozycji -----  ##
        x,y,z = poz
        if x == 0:
            x = 0.1
            poz = (x,y,z)
        T2 = odwrotna.oblicz(poz)
        pozycja = prosta.oblicz(T2)
        k1,k2,k3,k4 = T2
        k1 = round(k1,1)
        k2 = round(k2,1)
        k3 = round(k3,1)
        k4 = round(k4,1)
        T22 = (k1,k2,k3,k4)
        print("DOCELOWY:")
        print("odwrotna: ",T22,"prosta: ",pozycja)

        if liniowy ==0:
            # ----- Ustawienie serw na obliczone kąty, ruch domyślny -----  ##
            serwo.ustaw_predkosc(self.p)
            serwo.ustaw_poz(T2)

        if liniowy == 1:
            # ----- Ustawienie serw na obliczone kąty, ruch liniowy -----  ##
            poz2 = T2
            serwo.oblicz_predkosc_poz1(poz2)
            serwo.ustaw_poz(T2)
            
    def puzzle(self):
        kolejnosc = self.kolejnosc
        pozycje = self.pozycje
        puzzle = Puzzle(kolejnosc)
        zero= kolejnosc.find("0")

        print('Start: ', puzzle.start)
        print('Cel: ', puzzle.cel)
        sciezka = puzzle.search(puzzle.start)
        print("Liczba ruchów= ", (len(sciezka)))
        poz = [0,0,0,0]

        for etap in sciezka:
            kierunek = etap[2]
            x,y,z = pozycje.poz[zero]
            zero = etap[1].find("0")

            if kierunek == "left":
                poz[0] = (x+3,y,8)
                poz[1] = (x+3,y,3.8)
                poz[2] = (x-1,y,3.8)
                poz[3] = (x-1,y,8)
            elif kierunek == "right":
                poz[0] = (x-3,y,8)
                poz[1] = (x-3,y,3.8)
                poz[2] = (x+1,y,3.8)
                poz[3] = (x+1,y,8)
            elif kierunek == "up":
                poz[0] = (x,y-3,8)
                poz[1] = (x,y-3,3.8)
                poz[2] = (x,y+1,3.8)
                poz[3] = (x,y+1,8)
            elif kierunek == "down":
                poz[0] = (x,y+3,8)
                poz[1] = (x,y+3,3.8)
                poz[2] = (x,y-1,3.8)
                poz[3] = (x,y-1,8)
            else: continue
           
            self.ruch(poz[0],liniowy=1)
            sleep(0.5)
            self.ruch(poz[1],liniowy=1)
            sleep(0.5)
            self.ruch(poz[2],liniowy=1)
            sleep(0.5)
            self.ruch(poz[3],liniowy=1)
            sleep(0.5)

        self.ruch(pozycje.poz["start"],liniowy=0)



if __name__ == '__main__':
    model = rozpoznawanie.model()
    while True:
        Start(model)
