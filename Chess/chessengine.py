#---CHESS BY GUM---
'''
responsible for storing all of the information of the current state of the chess game
also responsible for determining the valid moves at the current state
responsible to keep the move log --> undo move, etc
'''
#chessEngine for the behavior of the chess game 

class GameState():
    def __init__(self):
        #board is 8x8 2d list, each element of the list has 2 characters
        #first character = color of piece (b/w)
        #second character = type of the piece (K = King, Q = Queen, etc)
        # '--' represents an empty space 
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        self.moveFunctions = {'P':self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'Q':self.getQueenMoves, 'K':self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.pins = []
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        self.inCheck = False
        self.enpassantPossible = () #coordinates for the square when en passant capture is possible 

    #takes a move as a parameter and execute it
    #this will not work forr castling, pawn protomiton and en-paassant

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it 
        self.whiteToMove = not self.whiteToMove #swap players

        #update king location 
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #en passant 
        if move.isEnpassantMove:
            #the pawn after the blank squares must be removed
            self.board[move.startRow][move.endCol] = '--' #capturing the pawn

        #generate the possible en passant moves (update enPassantPossibe var)
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2: #if a pawn move twice
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.endCol)
        else:
            self.enpassantPossible = ()

    #undo the last move
    def undoMoves(self):
        if len(self.moveLog) != 0: #there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            
            #update king's position 
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            #undo an en passant move 
            if move.isEnpassantMove:
                enemy_piece = 'bP' if self.whiteToMove else 'wP'
                self.board[move.endRow][move.endCol] = '--' #lave landing square blank
                self.board[move.startRow][move.endCol] = enemy_piece
                self.enpassantPossible = (move.endRow, move.endCol)
            
            #undo 2 square pawn advance
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) ==2:
                self.enpassantPossible = ()

    #all moves considering checks
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible #temporary en passant var
        moves_list = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.blackKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks) == 1: #only 1 check, block check or move king
                moves_list = self.getAllPossibleMoves()

                #to block a check we must move a piece into one of the squares between the enemy and king
                check_info = self.checks[0] #check information
                checkRow = check_info[0]
                checkCol = check_info[1]
                pieceChecking = self.board[checkRow][checkCol] #enemy piece causing the check
                validSquares = [] #squares that pieces can move to 

                #if knight, must capture knight or move king, other pieces can be blocked 
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:

                    for i in range(1, 8):
                        sq_iter = (kingRow + check_info[2]*i, kingCol + check_info[3]*i) #check_info[3] and check_info[2] is the directions
                        validSquares.append(sq_iter)

                        if sq_iter[0] == checkRow and sq_iter[1] == checkCol: #once we get to the piece and checks
                            break

                #get rid of any moves that don't block check or move king 
                for i in range(len(moves_list)-1, -1, -1):
                    if moves_list[i].pieceMoved[1] != 'K': #move doesn't move king so it must block or capture
                        if not (moves_list[i].endRow, moves_list[i].endCol) in validSquares: #moves doesn't block check or capture piece
                            moves_list.remove(moves_list[i])
            
            else: #double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves_list)

        else: #no checks, all moves are allowed 
            moves_list = self.getAllPossibleMoves()

        self.enpassantPossible = tempEnpassantPossible #en passant variable doesn't change
            
        return moves_list


    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False

        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        #check outward from king's perspective for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #reset possible pin 

            for i in range(1,8):
                endRow = startRow + d[0]*i
                endCol = startCol + d[1]*i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]

                    if endPiece[0] == allyColor and endPiece[1] != 'K':

                        if possiblePin == (): #1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break

                    elif endPiece[0] == enemyColor:
                        the_type = endPiece[1]
                        #5 possibilities here in this complex conditional 
                        #1) orthogonally away from king and the piece is a rook 
                        #2) diagonally away from king and the piece is a bishop 
                        #3) 1 square away diagonally from king and the piece is a pawn 
                        #4) any direction and the piece is a queen 
                        #5) any direction 1 square away and the piece is a king 

                        if (0 <= j <= 3 and the_type == 'R') or\
                            (4 <= j <= 7 and the_type == 'B') or\
                                (i == 1 and the_type == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or\
                                    (the_type == 'Q') or (i == 1 and the_type == 'K'):

                                    if possiblePin == (): #no piece are blocking, so check
                                        inCheck = True
                                        checks.append((endRow, endCol, d[0], d[1]))
                                        break
                                    else: #there is (are) piece(s), so pin
                                        pins.append(possiblePin)
                                        break
                        else: #enemy piece not applying check: 
                            #for example hitting the rook diagonally during the iteration, the piece isn't able to attack 
                            break 
                else:
                    break
        
        #check for knight 
        knightDirections = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))

        for m in knightDirections: 
            endRow = startRow + m[0]
            endCol = startCol + m[1]

            if 0<= endRow < 8 and 0<= endCol < 8:
                endPiece = self.board[endRow][endCol]

                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True 
                    checks.append((endRow, endCol, m[0], m[1] ))

        return inCheck, pins, checks



    #all moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of cols in given row 
                turn = self.board[r][c][0] #the first letter of the piece, whether it is 'w' or 'b' 
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove): #if it is a white piece
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #call the appropiate func
        
        return moves
    
    #get all the pawn moves for the pawn located at row, col and add these moves to the list 
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True 
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove: #white pawn moves
            if 0 < r < 7:
                if self.board[r-1][c] == '--': #one square pawn advance
                    if not piecePinned or pinDirection == (-1, 0):
                        moves.append(Move((r, c), (r-1, c), self.board))
                        if r == 6 and self.board[r-2][c] == '--': #2 square pawn advance
                            moves.append(Move((r, c), (r-2, c), self.board))
        
                if c-1 >= 0: #capture to the left 
                    if self.board[r-1][c-1][0] == 'b': #enemy piece to capture
                        if not piecePinned or pinDirection == (-1, -1):
                            moves.append(Move((r, c), (r-1, c-1), self.board))
                    elif (r-1, c-1) == self.enpassantPossible: #capturing a black space, en passant move
                        moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove = True))
                
                if c + 1 <= 7: #capture to the right
                    if self.board[r-1][c+1][0] == 'b': #enemy to capture
                        if not piecePinned or pinDirection == (-1, 1):
                            moves.append(Move((r, c), (r-1, c+1), self.board))
                    elif (r-1, c+1) == self.enpassantPossible: #capturing a black space, en passant move
                        moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove = True))
        
        else: #black pawn moves
            if 0 < r < 7: 
                if self.board[r+1][c] == '--':
                    if not piecePinned or pinDirection == (1, 0):
                        moves.append(Move((r, c), (r+1, c), self.board))
                        if r == 1 and self.board[r+2][c] == '--':
                            moves.append(Move((r,c), (r+2, c), self.board))
            
                if c-1 >=0:
                    if self.board[r+1][c-1][0] == 'w':
                        if not piecePinned or pinDirection == (1, -1):
                            moves.append(Move((r,c), (r+1, c-1), self.board))
                    elif (r+1, c-1) == self.enpassantPossible: #capturing a black space, en passant move
                            moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove = True))
                if c+1 <=7:
                    if self.board[r+1][c+1][0] == 'w':
                        if not piecePinned or pinDirection == (1, 1):
                            moves.append(Move((r,c), (r+1, c+1), self.board)) 
                    elif (r+1, c+1) == self.enpassantPossible: #capturing a black space, en passant move
                            moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove = True))


    def getRookMoves(self, r, c, moves):

        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True 
                pinDirection = (self.pins[i][2], self.pins[i][3])
                
                if self.board[r][c][1] != 'Q': #we cant remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        direction = ((-1, 0), (1, 0), (0, 1), (0, -1)) #up, down, right, left 
        enemy = 'b' if self.whiteToMove else 'w'

        for d in direction:
            for i in range(1, 8):
                row = r + d[0]*i
                col = c + d[1]*i

                if 0 <= row < 8 and 0 <= col < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]): #for moving away or towards the king
                        if self.board[row][col] == '--':
                            #print('CLEAR!!')
                            moves.append(Move((r, c), (row, col), self.board))
                        elif self.board[row][col][0] == enemy:
                            #print('ENEMY DETECTED!!')
                            moves.append(Move((r, c), (row, col), self.board))
                            break
                        else:
                            break
                else:
                    break

        
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True 
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break


        directions = ((2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2))
        enemy = 'b' if self.whiteToMove else 'w'

        for d in directions:
            row = r + d[0]
            col = c + d[1]

            if 0 <= row < 8 and 0 <= col < 8:
                if not piecePinned:
                    if self.board[row][col] == '--': #right, up
                        moves.append(Move((r, c), (row, col), self.board))
                    elif self.board[row][col][0] == enemy:
                        moves.append(Move((r, c), (row, col), self.board))


    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1]==c:
                piecePinned = True 
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])


        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1)) #diagonal right up, diagonal left up, diagonal right down, diagonal left down
        enemy = 'b' if self.whiteToMove else 'w'

        for dir in directions:
            for i in range(1, 8):
                row = r + dir[0]*i 
                col = c + dir[1]*i

                if 0 <= row < 8 and 0 <= col < 8:
                    if not piecePinned or pinDirection == dir or pinDirection == (-dir[0], -dir[1]):
                        if self.board[row][col] == '--':
                            moves.append(Move((r,c), (row, col), self.board))
                        elif self.board[row][col][0] == enemy:
                            moves.append(Move((r,c), (row, col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (-1, -1), (1, 1), (1, -1))
        enemy = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                row = r + d[0]*i
                col = c + d[1]*i

                if 0 <= row < 8 and 0 <= col < 8:
                    if self.board[row][col] == '--':
                        moves.append(Move((r,c), (row, col), self.board))
                    elif self.board[row][col][0] == enemy:
                        moves.append(Move((r,c), (row, col), self.board))
                        break
                    else:
                        break
                else:
                    break


    def getKingMoves(self, r, c, moves):
        direction = ((-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (-1, -1), (1, 1), (1, -1))
        ally = 'w' if self.whiteToMove else 'b'

        for d in direction:
            row = r + d[0]
            col = c + d[1]

            if 0 <= row < 8 and 0 <= col < 8:
                if self.board[row][col][0] != ally:
                    #place king on end square and check for checks 
                    if ally == 'w':
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)
                    
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    
                    if not inCheck:
                        moves.append(Move((r, c), (row, col), self.board))

                    #place king back on original location
                    if ally == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
                  



class Move():
    #maps keys to values
    #key : value

    ranksToRows = {'1':7, '2':6, '3':5, '4':4, '5':3, '6':2, '7':1, '8':0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
    colsToFiles = {v:k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        #pawn promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7):
            self.isPawnPromotion = True

        #en passant 
        self.isEnpassantMove = isEnpassantMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        print (self.moveID)
        
    #overriding the equals method
    def __eq__(self, other): #comparing one object to another object
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + ' to ' + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]   