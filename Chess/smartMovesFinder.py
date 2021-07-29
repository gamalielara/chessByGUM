import random 

pieceScore = {'K':0, 'Q':10, 'R':5, 'B':3, 'N':3, 'P':1}
CheckMate = 1000 #white checkmate will be 1000, black checkmate will be -1000
StallMate = 0


def findRandomMove (validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1 
    opponentMinMaxScore = CheckMate #the opponent's minimum max score 
    bestPlayerMove = None
    random.shuffle(validMoves)

    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        opponentMaxScore = -CheckMate #opponent's very low value

        for opponentsMove in opponentsMoves:
            gs.makeMove(opponentsMove)
            if gs.checkMate: #if the opponent has started a move and it results a checkmate:
                score = -turnMultiplier * CheckMate
            elif gs.staleMate:
                score = StallMate
            else:
                score = -turnMultiplier* scoreMaterial(gs.board)

            if score > opponentMaxScore: #finding each moves and if it's greater than the max score, that move is the max move
                opponentMaxScore = score
            gs.undoMoves()

        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove

        gs.undoMoves()

    return bestPlayerMove

#to score the board based on the material
def scoreMaterial(board):
    score = 0

    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    
    return score