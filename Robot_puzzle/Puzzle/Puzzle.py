import queue as Q


class Puzzle:

    def __init__(self,start = "076182453"):
        self.start = start
        self.cel = "123456780"
        self.mozliweRuchy = { # for a 3x3 board
            0: (1,3     ),  # these can slide into square 0
            1: (0,4,2),     # these can slide into square 1
            2: (1,5),       # these can slide into square 2
            3: (0,4,6),     # these can slide into square 3
            4: (1,3,5,7),   # these can slide into square 4
            5: (2,4,8),     # these can slide into square 5
            6: (3,7),       # these can slide into square 6
            7: (4,6,8),     # these can slide into square 7
            8: (5,7)}       # these can slide into square 8

        self.legalneRuchy = { # for a 3x3 board
            0: (1,3     ),  # these can slide into square 0
            1: (-1,3,1),     # these can slide into square 1
            2: (-1,3),       # these can slide into square 2
            3: (-3,1,3),     # these can slide into square 3
            4: (-3,-1,1,3),   # these can slide into square 4
            5: (-3,-1,3),     # these can slide into square 5
            6: (-3,1),       # these can slide into square 6
            7: (-3,-1,1),     # these can slide into square 7
            8: (-3,-1)}       # these can slide into square 8
        self.tabela_odl = self.odleglosc()

    def cel_osiagniety(self, st):
        return st == self.cel

    def znajdz_ruchy(self, st):
        zero = st.find("0")
        return zero, self.legalneRuchy[zero]

    def znajdz_ruchy_robot(self, st):
        zero = st.find("0")
        return self.mozliweRuchy[zero]

    def odleglosc(self):
        tabela_odl = {};
        for aa in range(9):
            for bb in range(9) :
                arow = aa//3; acol=aa%3
                brow = bb//3; bcol=bb%3
                tabela_odl[(aa,bb)] = abs(arow-brow)+abs(acol-bcol)
        return tabela_odl

    def dystans_manhattan(self,st):
        future = 0
        for pole in st:
            if pole != "0":
                shouldbe = self.cel.find(pole)
                teraz = st.find(pole)
                future  += self.tabela_odl[(teraz,shouldbe)]
        return future

    def sprawdz_robot(self,r):
        if r == 1:
            robot = "left"
        if r == -1:
            robot = "right"
        if r == 3:
            robot = "up"
        if r == -3:
            robot = "down"
        return robot

    def wykonaj_ruch(self, st, zero, r):
        stan = list(st)
        stan[zero + r], stan[zero] = stan[zero], stan[zero + r]
        return "".join(stan)

    def search(self, st):
        closed  = {}
        queue   = Q.PriorityQueue()
        ratio = 5
        origCost = self.dystans_manhattan(st)*ratio
        robot= ""
        orig = (origCost,0,st,robot,None) # (cost,nMoves,board,parent)
        print(origCost)
        queue.put(orig)
        closed[orig] = True
        expanded = 0
        solution = None
        while queue and not solution :
            parent = queue.get()
            #print(parent)
            expanded += 1
            (parCost, parMoves, parBoard,robot, ancester) = parent
            zero, ruchy = self.znajdz_ruchy(parBoard)
            #print(zero,ruchy)
            for r in ruchy :
                    childBoard = self.wykonaj_ruch(parBoard,zero,r)
                    #print(childBoard)
                    robot = self.sprawdz_robot(r)
                    if closed.get(childBoard) : continue
                    closed[childBoard] = True
                    childMoves = parMoves+1
                    childCost = self.dystans_manhattan(childBoard)*ratio + childMoves
                    child = (childCost, childMoves,childBoard,robot,parent)
                    #print(childCost)
                    queue.put(child)
                    if childBoard == self.cel:
                        solution = child
        if solution :
            print("%s entries expanded. Queue still has %s" % (expanded, queue.qsize()))
            path = []
            while solution :
                path.append(solution[1:4]) # drop the parent
                solution = solution[4]     # to grandparent
            path.reverse()
            return path
        else :
            return []


if __name__ == '__main__':
    puz = Puzzle()
    print('Start: ', puz.start)
    print('Cel: ', puz.cel)
    path = puz.search(puz.start)
    print("tilesSearch.py: Moves= ", (len(path)))
    for entry in path : print(entry)
