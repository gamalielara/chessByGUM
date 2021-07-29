#CHESS BY GUM
'''
the driver file
responsible for handling user input and displayingthe current GameState object
'''

import pygame as p
from Chess import chessengine, smartMovesFinder

width = height = 512
dimension = 8 #dimension of chess board 8x8
sq_size = height // dimension
max_fps = 15 #for animations
images = {}

'''
Initial a global dictionary of images, this will be called exactly once in the main 
'''

def loadImages(): #bad python syntax
    piece = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    
    for pic in piece:
        obj = p.transform.scale(p.image.load('Chess/images/' + pic + '.png'), (sq_size, sq_size))
        images[pic] = obj
        #Note : we can access the image by saying 'images['wP'] = wP.png'

'''
The main driver for the code, this will handle user input and updating the graphics
'''

def main():
    p.init()
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = chessengine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    animate = False #flag variable for when we shoudl animate a move 
    loadImages() #only do this once, before the while loop
    running = True 
    sqSelected = () #no square is selected, keep track of the ast click of the user 
    #tuple : (row, coloumn)
    playerClicks = [] #consists of 2 elements, keep track of the player clicks (two tuples): [(6, 4), (4, 4)]
    playerOne = False #if human is playing white, then this will be true, if AI, the thsi will be false
    playerTwo = True #if human is playing black, then this will be true, otherwise this will be false

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            #mouse landler
            elif e.type == p.MOUSEBUTTONDOWN:
                if humanTurn:
                    location = p.mouse.get_pos() #(x, y) location of the mouse
                    col = location[0]//sq_size
                    row = location[1]//sq_size

                    if sqSelected == (row, col): #the user clicked the same square twice, the undo 
                        sqSelected = () #disselect
                        playerClicks = [] #clear 
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) #append for the 1st and 2nd clicks
                    
                    if len(playerClicks) == 2: #after the second click
                        #move the piece to the 2nd square
                        #make a Move class in chessengine 
                        move = chessengine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True 
                                sqSelected = () #reset user clicks
                                playerClicks = []
                            
                        if not moveMade:
                            playerClicks = [sqSelected]

            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #call undo when 'z' is pressed
                    gs.undoMoves()
                    moveMade = True 
                    animate = False

                if e.key == p.K_r: #when r is pressed 
                    gs = chessengine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        #AI move finder logic 
        if not humanTurn:
            AIMove = smartMovesFinder.findBestMove(gs, validMoves)

            if AIMove is None:
                AIMove = smartMovesFinder.findRandomMove(validMoves)

            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(max_fps)
        p.display.flip() 
        
'''
highlight sqyare selected and moves for the piece selected
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved
            #highlight selected square 
            s = p.Surface((sq_size, sq_size))
            s.set_alpha(100) #transparancy value, 0 = transparent; 255 = opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*sq_size, r*sq_size))
            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*sq_size, move.endRow*sq_size))


'''
to draw all of the graphics:
'''
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) #draw the squares on the board
    #add in piece highlighting or move suggestions (later!!)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) #draw the pieces on top of those quares


#to draw the squares, first
def drawBoard(screen):
    global colors 
    colors = [p.Color('white'), p.Color('gray')]

    for r in range(dimension): #rows
        for c in range(dimension): #colomns
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))
            #c = column, the horizontal (x axis); r = row, the vertical (y axis)
            #the last two sq_size, sq_size denotes the dimensions


def drawPieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]

            if piece != '--': #not an empty square
                screen.blit(images[piece], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))

'''
animating a move
'''
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 #frames to move one square
    frameCount = (abs(dR) + abs(dC))*framesPerSquare

    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        #erase the piece move from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*sq_size, move.endRow*sq_size, sq_size, sq_size)
        p.draw.rect(screen, color, endSquare)

        #draw captured piece onto the rectangle 
        if move.pieceCaptured != '--':
            screen.blit(images[move.pieceCaptured], endSquare)
        
        #draw the moving piece 
        screen.blit(images[move.pieceMoved], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))
        p.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()