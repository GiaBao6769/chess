board_size: int = 8


class Piece:

    def __init__(self, name: str, color: int, position: tuple[int, int]):
        global piecePoint
        self.name: str = name
        self.color: int = color
        self.position: tuple[int, int] = position

        self.point: int = piecePoint[self.name]


    def __str__(self):
        return f"{self.name=}, {self.color=}, {self.position=}, {isSafe(self.position, current_color)}"

    def build(self) -> None:
        global classBoard, checkBoard
        updateBoard(classBoard, self.position, self)
        updateBoard(checkBoard, self.position, (self.name, self.color))
        pointOfColor[opsColor(self.color)] += self.point

    def destroy(self) -> None:
        global pointOfColor
        pointOfColor[opsColor(self.color)] -= self.point
        resetNonMoveCnt()
        del(self)

    def move(self, ed_pos: tuple[int, int], moveType: int) -> None:
        global classBoard, checkBoard, placeHolder, checkBoard_placeHolder, take, moved_moves, move_types

        if moveType == move_types[enPassantLeft]:
            moved_moves[-1] = ((self.position, ed_pos, moveType), getPiece((ed_pos[0], ed_pos[1]-1)))

        elif moveType == move_types[enPassantRight]:
            moved_moves[-1] = ((self.position, ed_pos, moveType), getPiece((ed_pos[0], ed_pos[1]+1)))

        elif moveType == move_types[take] or moveType == move_types[takeAndPromote]:
            getPiece(ed_pos).destroy()

        notate((self.position, ed_pos, moveType))

        updateBoard(classBoard, ed_pos, self)
        updateBoard(classBoard, self.position, placeHolder)

        updateBoard(checkBoard, ed_pos, (self.name, self.color))
        updateBoard(checkBoard, self.position, checkBoard_placeHolder)

        self.position = ed_pos


    def isOccupied(self) -> bool:
        return True

    def isTakeable(self, color: int):
        return self.color != color

    def get_possible_moves(self):
        pass


class PlaceHolder(Piece):
    def __init__(self, name: str, color: int, position: tuple[int, int]):
        super().__init__(name, color, position)

    def isOccupied(self) -> bool:
        return False

    def isTakeable(self, color: int):
        return False


class Knight(Piece):
    def get_knight_moves(self) -> None:
        global board_size, placeHolder, move_types, take, possible_moves_lst, none

        row, file = self.position
        for ud in [1, -1]:
            for lr in [2, -2]:
                for udx, lrx in ((ud, lr), (lr, ud)):
                    if isValidCell(row+udx, file + lrx):
                        toCell: Piece = getPiece((row + udx, file + lrx))
                        if not toCell.isOccupied() and isSafeMove(self.position, (row+udx, file+lrx)):
                            possible_moves_lst.append((self.position, (row + udx, file + lrx), move_types[none]))
                        elif toCell.isTakeable(self.color) and isSafeMove(self.position, (row+udx, file+lrx)):
                            possible_moves_lst.append((self.position, (row + udx, file + lrx), move_types[take]))


    def get_possible_moves(self) -> None:
        self.get_knight_moves()


class Bishop(Piece):
    def get_bishop_moves(self) -> None:
        global board_size, placeHolder, possible_moves_lst, move_types, take, none
        for ud in (-1, 1):
            for lr in (-1, 1):
                row, file = self.position
                while isValidCell(row+ud, file+lr):
                    row += ud
                    file += lr
                    toCell: Piece = getPiece((row, file))
                    if toCell.isOccupied():
                        if toCell.isTakeable(self.color) and isSafeMove(self.position, (row, file)):
                            possible_moves_lst.append((self.position, (row, file), move_types[take]))
                        break
                    elif isSafeMove(self.position, (row, file)):
                        possible_moves_lst.append((self.position, (row, file), move_types[none]))

    def get_possible_moves(self) -> None:
        self.get_bishop_moves()


class Pawn(Piece):
    def __init__(self, name: str, color: int, position: tuple[int, int]):
        global piecePoint, move_types, none
        super().__init__(name, color, position)
        self.firstMove: bool = True
        self.en_passant: int = move_types[none]


    def __str__(self):
        return f"{self.name=}, {self.color=}, {self.position=}, {self.firstMove=}, {self.en_passant=}"


    def get_pawn_moves(self) -> None:
        global possible_moves_lst, move_types, take, twoCellsMove, promotion, none, enPassantLeft, enPassantRight
        direction: int = pawnDirection(self.color)
        pos: tuple[int, int] = self.position
        if isValidCell(pos[0] + direction, pos[1]) and not isOccupied((pos[0]+direction, pos[1])) and \
                isSafeMove(pos, (pos[0]+direction, pos[1])):
            possible_moves_lst.append((pos, (pos[0] + direction, pos[1]), move_types[promotion if pos[0] + direction == startRow((self.color + 1) % 2) else none]))

        for lr in (-1, 1):
            if isValidCell(pos[0] + direction, pos[1] + lr) and \
                    isTakeable((pos[0] + direction, pos[1] + lr), self.color) and \
                        isSafeMove(pos, (pos[0] + direction, pos[1] + lr)):
                possible_moves_lst.append((pos, (pos[0] + direction, pos[1] + lr),
                                           move_types[takeAndPromote if pos[0] + direction == startRow((self.color + 1) % 2) else take]))

        if self.firstMove is True and isValidCell(pos[0] + 2*direction, pos[1]) and \
                not isOccupied((pos[0] + direction, pos[1])) and not isOccupied((pos[0] + 2 * direction, pos[1])) and \
                    isSafeMove(pos, (pos[0]+2*direction, pos[1])):
            possible_moves_lst.append((pos, (pos[0] + 2*direction, pos[1]), move_types[twoCellsMove]))

        if self.en_passant == move_types[enPassantLeft] and not getPiece((pos[0] + direction, pos[1] - 1)).isOccupied() and isSafeMove:
            possible_moves_lst.append((pos, (pos[0] + direction, pos[1]-1), move_types[enPassantLeft]))

        elif self.en_passant == move_types[enPassantRight] and not getPiece((pos[0] + direction, pos[1] + 1)).isOccupied():
            possible_moves_lst.append((pos, (pos[0] + direction, pos[1] + 1), move_types[enPassantRight]))

    def get_possible_moves(self) -> None:
        self.get_pawn_moves()

    def promote(self, promotePiece: str):
        global promotePiecesList, knight, bishop, rook, queen
        if promotePiece == knight:
            Knight(knight, self.color, self.position).build()
        elif promotePiece == bishop:
            Bishop(bishop, self.color, self.position).build()
        elif promotePiece == rook:
            Rook(rook, self.color, self.position).build()
        else:
            Queen(queen, self.color, self.position).build()
        self.destroy()


    def move(self, ed_pos: tuple[int, int], moveType: int) -> None:
        global classBoard, checkBoard, placeHolder, checkBoard_placeHolder, move_types, enPassantLeft, enPassantRight, twoCellsMove, pawn
        super().move(ed_pos, moveType)

        if self.firstMove:
            self.firstMove = False
            if moveType == move_types[twoCellsMove]:
                leftCell: Piece = getPiece((ed_pos[0], ed_pos[1]-1))
                rightCell: Piece = getPiece((ed_pos[0], ed_pos[1] + 1))
                if leftCell.name == pawn and leftCell.color == opsColor(self.color):
                    leftCell.en_passant = move_types[enPassantRight]
                if rightCell.name == pawn and rightCell.color == opsColor(self.color):
                    rightCell.en_passant = move_types[enPassantLeft]

        if moveType == move_types[enPassantLeft] or moveType == move_types[enPassantRight]:
            getPiece((self.position[0] - pawnDirection(self.color), self.position[1])).destroy()

        resetNonMoveCnt()
        clearRepetition()


class King(Piece):
    def __init__(self, name: str, color: int, position: tuple[int, int]):
        super().__init__(name, color, position)
        self.firstMove: bool = True

    def __str__(self):
        return f"{self.name=}, {self.color=}, {self.position=}, {self.firstMove=}"

    def get_king_moves(self) -> None:
        global board_size, placeHolder, possible_moves_lst, rook, take, shortCastle, longCastle, move_types, none
        row, file = self.position
        for ud in [-1, 0, 1]:
            for lr in [-1, 0, 1]:
                if ud == lr == 0:
                    continue
                if isValidCell(row+ud, file+lr):
                    toCell: Piece = getPiece((row + ud, file + lr))

                    if not toCell.isOccupied() and isSafeMove(self.position, (row+ud, file+lr)):
                        possible_moves_lst.append((self.position, (row+ud, file+lr), move_types[none]))

                    elif toCell.isTakeable(self.color) and isSafeMove(self.position, (row+ud, file+lr)):
                        possible_moves_lst.append((self.position, (row+ud, file+lr), move_types[take]))

        if self.firstMove and isSafe(self.position, self.color):
            rightRook: Piece = classBoard[row][file+3]
            leftRook: Piece = classBoard[row][file-4]

            if rightRook.name == rook and rightRook.color == self.color and rightRook.firstMove and \
                not isOccupied((row, file+1)) and isSafe((row, file+1), self.color) and \
                    not isOccupied((row, file+2)) and isSafe((row, file+2), self.color):
                possible_moves_lst.append((self.position, (row, file+2), move_types[shortCastle]))

            if leftRook.name == rook and leftRook.color == self.color and leftRook.firstMove and \
                not isOccupied((row, file-1)) and isSafe((row, file-1), self.color) and \
                    not isOccupied((row, file-2)) and isSafe((row, file-2), self.color) and \
                        not isOccupied((row, file-3)):
                possible_moves_lst.append((self.position, (row, file-2), move_types[longCastle]))

    def get_possible_moves(self) -> None:
        self.get_king_moves()

    def move(self, ed_pos: tuple[int, int], moveType: int) -> None:
        global classBoard, checkBoard, placeHolder, checkBoard_placeHolder, shortCastle, longCastle, rookCastle, move_types
        super().move(ed_pos, moveType)

        self.position = ed_pos

        if self.firstMove:
            self.firstMove = False
            if moveType == move_types[shortCastle]:
                getPiece((startRow(self.color), 7)).move((startRow(self.color), 5), move_types[rookCastle])
            elif moveType == move_types[longCastle]:
                getPiece((startRow(self.color), 0)).move((startRow(self.color), 3), move_types[rookCastle])

            clearRepetition()


class Rook(Piece):
    def __init__(self, name: str, color: int, position: tuple[int, int]):
        super().__init__(name, color, position)
        self.firstMove: bool = True

    def __str__(self):
        return f"{self.name=}, {self.color=}, {self.position=}, {self.firstMove=}"

    def get_rook_moves(self) -> None:
        global board_size, placeHolder, possible_moves_lst, move_types, take, none
        for ud, lr in [[-1, 0], [1, 0], [0, 1], [0, -1]]:
            row, file = self.position
            while isValidCell(row+ud, file+lr):
                row += ud
                file += lr
                currentCell: Piece = getPiece((row, file))
                if currentCell.isOccupied():
                    if currentCell.isTakeable(self.color) and isSafeMove(self.position, (row, file)):
                        possible_moves_lst.append((self.position, (row, file), move_types[take]))
                    break
                elif isSafeMove(self.position, (row, file)):
                    possible_moves_lst.append((self.position, (row, file), move_types[none]))


    def get_possible_moves(self) -> None:
        self.get_rook_moves()

    def move(self, ed_pos: tuple[int, int], moveType: int) -> None:
        global classBoard, checkBoard, placeHolder, checkBoard_placeHolder
        super().move(ed_pos, moveType)

        if self.firstMove:
            self.firstMove = False
            clearRepetition()



class Queen(Bishop, Rook):
    def get_queen_moves(self) -> None:
        self.get_rook_moves()
        self.get_bishop_moves()

    def get_possible_moves(self) -> None:
        self.get_queen_moves()


pawn: str = "pawn"
bishop: str = "bishop"
knight: str = "knight"
rook: str = "rook"
queen: str = "queen"
king: str = "king"
placeholder: str = "place_holder"

none: str = "none"
take: str = "take"
twoCellsMove: str = "twoCellsMove"
enPassantRight: str = "enPassantRight"
enPassantLeft: str = "enPassantLeft"
promotion: str = "promotion"
takeAndPromote: str = "takeAndPromotion"
shortCastle: str = "shortCastle"
longCastle: str = "longCastle"
rookCastle: str = "rookCastle"

noneTuple: tuple[int, int] = (-1, -1)

# <!-----[Notation]-----> #
shortCastleNotation: str = "0-0"
longCastleNotation: str = "0-0-0"
check: str = "check"
checkmate: str = "checkmate"

#special move numbers, used with args in move()
move_types: dict[str, int] = {none: 1, take: 2, twoCellsMove: 3, enPassantRight: 4, enPassantLeft: 5,
                              promotion: 6, takeAndPromote: 7, shortCastle: 8, longCastle: 9, rookCastle: 10,
                              }
move_error_types: dict[str, int] = {"unavailableMove": 0, 
                                    "unavailableCheck": -1, 
                                    "unavailableCheckmate": -2, 
                                    "unavailablePromote": -3,
                                    "unavailableTake": -4}

promotePiecesList: set[str] = {knight, bishop, rook, queen}
piecePoint: dict[str, int] = {pawn: 1, knight: 3, bishop: 3, king: 3, rook: 5, queen: 9, placeholder: 0}
name_to_abbrev: dict[str, str] = {king: "K", queen: "Q", rook: "R", bishop: "B", knight: "N", pawn: ""}
abbrev_to_name: dict[str, str] = {"K": king, "Q": queen, "R": rook, "B": bishop, "N": knight, "": pawn}

placeHolder: PlaceHolder = PlaceHolder(placeholder, -1, (-1, -1))
checkBoard_placeHolder = (placeHolder.name, -1)

# game result variables

whiteWin: str = "whiteWin"
blackWin: str = "blackWin"

drawThreefoldRepetition: str = "fiftyRepetition"
drawInsufficientMaterials: str = "insufficientMaterials"
drawStalemate: str = "drawStalemate"
drawSeventyMove: str = "drawSeventyMove"


game_result_types: dict[str, int] = {none: 0, whiteWin: 1, blackWin: 2, drawThreefoldRepetition: 3,
                                     drawInsufficientMaterials: 4, drawStalemate: 5, drawSeventyMove: 6}

# resetable variables

nonMoveCnt: int = 0
isTerminated: bool = False
gameResult: int = game_result_types[none]

threefoldRepetitionDict: dict[str, int] = {}

current_color: int = 1 # 0 for white, 1 for black
isInCheck: bool = False

classBoard: list[list[Piece]] = [[placeHolder] * board_size for _ in range(board_size)]
checkBoard: list[list[tuple[str, int]]] = [[checkBoard_placeHolder] * board_size for _ in range(board_size)]

possible_moves_lst: list[tuple[tuple[int, int], tuple[int, int], int]] = []
kings_lst: list[King, King] = []

# sum of all point of pieces of each color
pointOfColor: list[int, int] = [0, 0]

notationsList: list[str] = []


# <!---Moved moves---->

moved_moves: list[tuple[tuple[tuple[int, int], tuple[int, int], int], Piece]] = []
turnInfo: list[dict[str, any]] = []



def newGame() -> None:
    global nonMoveCnt, isTerminated, gameResult, threefoldRepetitionDict, current_color, isInCheck, pointOfColor, classBoard, checkBoard, possible_moves_lst, kings_lst, moved_moves

    nonMoveCnt = 0
    isTerminated = False
    gameResult = game_result_types[none]
    threefoldRepetitionDict.clear()

    current_color = 1
    isInCheck = False

    classBoard = [[placeHolder] * board_size for _ in range(board_size)]
    checkBoard = [[checkBoard_placeHolder] * board_size for _ in range(board_size)]

    possible_moves_lst.clear()
    kings_lst.clear()
    moved_moves.clear()
    pointOfColor = [0, 0]
    notationsList.clear()

    standard_generate()
    turnChange()




def printBoard() -> None:
    global board_size, classBoard, checkBoard
    for row in range(board_size):
        for file in range(board_size):
            if isOccupied((row, file)):
                print(checkBoard[row][file], end=" ")
            else:
                print("(0, 0)", end=" ")
        print()


def standard_generate() -> None:
    global pawn, knight, bishop, rook, queen, king, pointOfColor, kings_lst

    for color in (0, 1):
        pawn
        for file in range(board_size):
            Pawn(pawn, color, (startRow(color) + pawnDirection(color), file)).build()

        Knight(knight, color, (startRow(color), 1)).build()
        Knight(knight, color, (startRow(color), 6)).build()
        Bishop(bishop, color, (startRow(color), 2)).build()
        Bishop(bishop, color, (startRow(color), 5)).build()
        Rook(rook, color, (startRow(color), 0)).build()
        Rook(rook, color, (startRow(color), 7)).build()
        Queen(queen, color, (startRow(color), 3)).build()

        kings_lst.append(King(king, color, (7 - color * 7, 4)))
        kings_lst[-1].build()

    # Rook(rook, 1, (4, 0)).build()
    # Rook(rook, 1, (4, 2)).build()
    # Bishop(bishop, 1, (0, 0)).build()
    # Pawn(pawn, 1, (3, 0)).build()
    # Pawn(pawn, 1, (3, 2)).build()
    # Pawn(pawn, 0, (6, 1)).build()



def updateBoard(board: list[list[any]], pos: tuple[int, int], updateContent: any) -> None:
    board[pos[0]][pos[1]] = updateContent


def isOccupied(pos: tuple[int, int]) -> bool:
    global placeHolder
    return getPiece(pos) != placeHolder


def isValidCell(rank: int, file: int) -> bool:
    global board_size
    return 0 <= rank < board_size and 0 <= file < board_size


def isTakeable(pos: tuple[int, int], color: int) -> bool:
    global classBoard
    return isOccupied(pos) and classBoard[pos[0]][pos[1]].color != color


def opsColor(color: int) -> int:
    return (color + 1) % 2


def getPiece(pos: tuple[int, int]) -> Piece:
    """
    Return the piece in the parameter position if the cell is valid and the piece exists.
    """
    global classBoard, placeHolder
    if not isValidCell(pos[0], pos[1]):
        return placeHolder
    return classBoard[pos[0]][pos[1]]


def convert_pos_to_cord(pos: tuple[int, int]) -> str:
    global board_size
    return chr(pos[1] + 97) + str(board_size - pos[0])


def convert_cord_to_pos(cord: str) -> tuple[int, int]:
    global board_size
    return board_size - int(cord[1]), ord(cord[0]) - 97


def startRow(color: int) -> int:
    """
    return the first row of the parameter color\n
    :param color:
    :return: the start row of the parameter color
    """
    global board_size
    return ((color+1) % 2) * (board_size - 1)


def pawnDirection(color: int) -> int:
    """
    return the direction of the pawns of the parameter color
    :param color:
    :return:
    """
    return 2 * color - 1


def modifyPos(pos: tuple[int, int], dx: int, dy: int) -> tuple[int, int]:
    return pos[0] + dx, pos[1] + dy


def isSafe(pos: tuple[int, int], color: int) -> bool:
    global checkBoard, classBoard

    ops_color: int = opsColor(color)

    def isOccupied(rank: int, file:int):
        return checkBoard[rank][file] != checkBoard_placeHolder

    # check for pawn
    direction: int = pawnDirection(color)
    if (isValidCell(pos[0] + direction, pos[1] - 1) and checkBoard[pos[0] + direction][pos[1] - 1] == (pawn, ops_color)) or \
            (isValidCell(pos[0] + direction, pos[1] + 1) and checkBoard[pos[0] + direction][pos[1] + 1] == (pawn, ops_color)):
        return False

    # check for king
    for ud in (-1, 0, 1):
        for lr in (-1, 0, 1):
            if ud == lr == 0:
                continue
            if isValidCell(pos[0]+ud, pos[1]+lr) and checkBoard[pos[0] + ud][pos[1] + lr] == (king, ops_color):
                return False

    # check for knight
    for ud in (-2, 2):
        for lr in (-1, 1):
            for udx, lrx in ((ud, lr), (lr, ud)):
                if isValidCell(pos[0] + udx, pos[1] + lrx) and checkBoard[pos[0] + udx][pos[1] + lrx] == (knight, ops_color):
                    return False

    # check for bishop and queen
    for ud in (-1, 1):
        for lr in (-1, 1):
            rank, file = pos[0] + ud, pos[1] + lr
            while isValidCell(rank, file):
                if isOccupied(rank, file):
                    if checkBoard[rank][file] == (bishop, ops_color) or checkBoard[rank][file] == (queen, ops_color):
                        return False
                    break
                rank += ud
                file += lr

    # check for rook and queen
    for ud, lr in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        rank, file = pos[0] + ud, pos[1] + lr
        while isValidCell(rank, file):
            if isOccupied(rank, file):
                if checkBoard[rank][file] == (rook, ops_color) or checkBoard[rank][file] == (queen, ops_color):
                    return False
                break
            rank += ud
            file += lr
    return True


def isSafeMove(st_pos: tuple[int, int], ed_pos: tuple[int, int], *forColor) -> bool:
    global classBoard, checkBoard, kings_lst, current_color, king, placeHolder, checkBoard_placeHolder

    org_ed_cell: tuple[str, int] = checkBoard[ed_pos[0]][ed_pos[1]]
    checkBoard[ed_pos[0]][ed_pos[1]] = checkBoard[st_pos[0]][st_pos[1]]
    checkBoard[st_pos[0]][st_pos[1]] = checkBoard_placeHolder

    isPossible: bool = False
    curPiece: Piece = getPiece(st_pos)

    if forColor != ():
        checkingColor = forColor[0]
    else:
        checkingColor: int = current_color

    if curPiece.name == king and curPiece.color == checkingColor:
        isPossible = isSafe(ed_pos, checkingColor)
    else:
        isPossible = isSafe(kings_lst[checkingColor].position, checkingColor)
    checkBoard[st_pos[0]][st_pos[1]] = checkBoard[ed_pos[0]][ed_pos[1]]
    checkBoard[ed_pos[0]][ed_pos[1]] = org_ed_cell

    return isPossible


def generatePossibleMoves() -> None:
    global possible_moves_lst, board_size, classBoard, current_color
    possible_moves_lst.clear()
    for row in range(board_size):
        for file in range(board_size):
            if getPiece((row, file)).color == current_color:
                getPiece((row, file)).get_possible_moves()


def splitNotation(notation: str) -> list[str, str, str]:
    global shortCastleNotation, longCastleNotation
    if notation == shortCastleNotation or notation == longCastleNotation:
        return ["K", "", ""]

    splitedNotation: list[str] = ['']
    id: int = 0
    if notation[0].isupper():
        splitedNotation[0] = notation[0]
        id += 1
    
    for idx in range(id, len(notation)):
        if notation[idx] == 'x':
            continue
        if notation[idx].isalpha():
            splitedNotation.append(notation[idx])
        else:
            splitedNotation[-1] += notation[idx]

    if len(splitedNotation) == 2:
        splitedNotation.insert(1, "")

    return splitedNotation   

def convertNotationToMove(notation: str) -> tuple[tuple[int, int], tuple[int, int]]:
    global possible_moves_lst, noneTuple
    notationLst: list[str] = splitNotation(notation)

    for move in possible_moves_lst:
        curNotationLst: list[str] = splitNotation(makeNotation(move))
        if len(curNotationLst) < 3:
            print(curNotationLst, move)
            print(makeNotation(((4, 3), (3, 2), 2)))
        if notationLst[0] == curNotationLst[0]:
            check: bool = True
            for idx in range(1, 3):
                if curNotationLst[idx] not in notationLst[idx]:
                    check = False
                    break
            if check:
                return move[0], move[1]
    return noneTuple, noneTuple



def toMoveWithNotation(notation: str) -> tuple[tuple[int, int], tuple[int, int], int]:
    global current_color
    haveChecking: bool = False
    haveMateChecking: bool = False
    haveTaking: bool = False

    if notation[-1] in ("+", "#"):
        if notation[-1] == '#':
            haveMateChecking = True
        haveChecking = True
        notation = notation[:-1]
    
    if 'x' in notation:
        haveTaking = True 
        print("Have yet to implement!")

    # check specifically for promoting move
    if notation[-2] == "=":
        move: tuple[tuple[int, int], tuple[int, int]] = convertNotationToMove(notation[:-2])
        
        print("Can be more specific about if the promote piece is invalid or the move is invalid.")
        if (notation[-1] not in abbrev_to_name) or (abbrev_to_name[notation[-1]] not in promotePiecesList):
            return noneTuple, noneTuple, move_error_types["unavailablePromote"]
        
        moveType: int = getMoveType(move[0], move[1])

        if moveType == move_types[promotion] or moveType == move_types[takeAndPromote]:
            move(move[0], move[1])
            toPromote(move[1], abbrev_to_name[notation[-1]])
            return move[0], move[1], moveType
        
        return noneTuple, noneTuple, move_error_types["unavailablePromote"]
    
    
    move: tuple[tuple[int, int], tuple[int, int]] = convertNotationToMove(notation)
    moveType: int = getMoveType(move[0], move[1])

    

    if moveType == 0:
        return noneTuple, noneTuple, move_error_types["unavailableMove"]

    if haveChecking and isSafeMove(move[0], move[1], (opsColor(current_color))):
        print("Can be more specific about a move that can't check")
        if haveMateChecking:
            return noneTuple, noneTuple, move_error_types["unavailableCheckmate"]
        return noneTuple, noneTuple, move_error_types["unavailableCheck"]


    return move[0], move[1], toMove(move[0], move[1])

print("Can be more specific about take move that doesn't take.")

def getMoveType(st_pos: tuple[int, int], ed_pos: tuple[int, int]) -> int:
    if st_pos == noneTuple or ed_pos == noneTuple:
        return move_error_types["unavailableMove"]
    for move in possible_moves_lst:
        if move[0] == st_pos and move[1] == ed_pos:
            return move[2] 
    return move_error_types["unavailableMove"]


def toMove(st_pos: tuple[int, int], ed_pos: tuple[int, int]) -> int:
    global possible_moves_lst, isTerminated

    # check if the move is valid
    if st_pos == noneTuple or ed_pos == noneTuple:
        return move_error_types["unavailableMove"]

    for move in possible_moves_lst:
        if move[0] == st_pos and move[1] == ed_pos:
            getPiece(st_pos).move(ed_pos, move[2])
            if move[2] == move_types[promotion] or move[2] == move_types[takeAndPromote]:
                possible_moves_lst.clear()
                return move[2]
            turnChange()
            return move[2]
    return move_error_types["unavailableMove"]


def toPromote(pos: tuple[int, int], promotePieceName: str) -> None:
    if isValidCell(pos[0], pos[1]):
        getPiece(pos).promote(promotePieceName)
        addPromotion(promotePieceName)
        turnChange()


def addRepetion() -> None:
    global threefoldRepetitionDict, classBoard, board_size, placeHolder, gameResult
    boardString: str = ""

    for rank in range(board_size):
        for file in range(board_size):
            checkingPiece: Piece = getPiece((rank, file))
            if checkingPiece != placeHolder:
                boardString += f"{name_to_abbrev[checkingPiece.name]}{checkingPiece.position[0]}{checkingPiece.position[1]}"
                if checkingPiece.name == pawn:
                    boardString += f"{checkingPiece.en_passant}"
                elif checkingPiece.name == rook or checkingPiece.name == king:
                    boardString += f"{int(checkingPiece.firstMove)}"

    if boardString in threefoldRepetitionDict:
        threefoldRepetitionDict[boardString] += 1
        if threefoldRepetitionDict[boardString] == 3:
            gameResult = game_result_types[drawThreefoldRepetition]
    else:
        threefoldRepetitionDict[boardString] = 1


def clearRepetition() -> None:
    global threefoldRepetitionDict
    threefoldRepetitionDict.clear()


def resetNonMoveCnt() -> None:
    global nonMoveCnt
    nonMoveCnt = 0


def turnChange() -> bool:
    global isTerminated, classBoard, current_color, possible_moves_lst, kings_lst, isInCheck, gameResult, nonMoveCnt
    global king, queen, pawn, rook, bishop, knight

    if isTerminated:
        return False

    current_color = opsColor(current_color)
    isInCheck = not isSafe(kings_lst[current_color].position, current_color)

    nonMoveCnt += 1

    # Remove en passant
    checkingRank: int = startRow(current_color) + 3*pawnDirection(current_color)
    for checkingFile in range(board_size):
        checkingPiece: Piece = getPiece((checkingRank, checkingFile))
        if checkingPiece.name == pawn and checkingPiece.color != current_color:
            checkingPiece.en_passant = move_types[none]
    generatePossibleMoves()

    if isInCheck:
        if len(possible_moves_lst) == 0:
            addCheck(checkmate)
            if current_color == 0:
                gameResult = game_result_types[blackWin]
            else:
                gameResult = game_result_types[whiteWin]
        else:
            addCheck(check)

    if gameResult == game_result_types[none]:
        if len(possible_moves_lst) == 0:
            gameResult = game_result_types[drawStalemate]

    if gameResult == game_result_types[none]:
        addRepetion()

    if gameResult == game_result_types[none]:
        if nonMoveCnt > 75:
            gameResult = game_result_types[drawSeventyMove]

    # <-----[Checking for insufficiency]----->
    if gameResult == game_result_types[none]:
        knightCnt: int = 0
        bishopList: list[tuple[int, int]] = []
        isSufficient: bool = False

        for rank in range(board_size):
            for file in range(board_size):
                checkingPiece: Piece = getPiece((rank, file))

                if checkingPiece == placeHolder or checkingPiece.name == king:
                    continue
                if checkingPiece.name == bishop:
                    bishopList.append((rank, file))
                elif checkingPiece.name == knight:
                    knightCnt += 1
                else:
                    isSufficient = True
                    break

                if (knightCnt and len(bishopList)) or knightCnt > 1 or len(bishopList) > 2:
                    isSufficient = True
                    break

            if isSufficient:
                break

        if not isSufficient:
            if len(bishopList) < 2:
                gameResult = game_result_types[drawInsufficientMaterials]
            else:
                checkingBishop_fst: Piece = getPiece(bishopList[0])
                checkingBishop_snd: Piece = getPiece(bishopList[1])
                if checkingBishop_fst.color != checkingBishop_snd.color and \
                    sum(checkingBishop_fst.position) % 2 == sum(checkingBishop_snd.position) % 2:

                    gameResult = game_result_types[drawInsufficientMaterials]
                    print(4)


    if gameResult != game_result_types[none]:

        possible_moves_lst.clear()

        notateGameResult()
        isTerminated = True
        return False

    return True




def specifyCell(samePiece: int, sameRank: int, sameFile: int, pos: tuple[int, int]) -> str:
    if samePiece > 1:
        if sameRank > 1 and sameFile > 1:
            return convert_pos_to_cord(pos)
        elif sameFile > 1:
            return convert_pos_to_cord(pos)[1]
        else:
           return convert_pos_to_cord(pos)[0]
           # whether there are two same pieces in a rank or not,
           # we still just need to specify the file

    return ""


def notateForCastle(castleType: int) -> str:
    if castleType == move_types[shortCastle]:
        return shortCastleNotation
    else:
        return longCastleNotation


def notateEnPassant(st_pos: tuple[int, int], enPassantType: int) -> str:
    global pawn, current_color
    samePiece: int = 1
    sameRank: int = 1
    sameFile: int = 1

    takeCord: str = ""

    def checkPawn(rank: int, file: int) -> None:
        global pawn
        nonlocal samePiece, sameRank, sameFile, st_pos
        if getPiece((rank, file)).name == pawn:
            samePiece += 1
            if rank == st_pos[0]:
                sameRank += 1
            if file == st_pos[1]:
                sameFile += 1

    if enPassantType == move_types[enPassantLeft]:
        checkPawn(st_pos[0], st_pos[1]-2)
        checkPawn(st_pos[0]-pawnDirection(current_color), st_pos[1]-2)
        takeCord = convert_pos_to_cord((st_pos[0], st_pos[1]-1))

    # elif enPassantType == move_types_lst[enPassantRight]:
    else:
        checkPawn(st_pos[0], st_pos[1]+2)
        checkPawn(st_pos[0]-pawnDirection(current_color), st_pos[1]+1)
        takeCord = convert_pos_to_cord((st_pos[0], st_pos[1]+1))

    checkPawn(st_pos[0]-1, st_pos[1])

    return specifyCell(samePiece, sameRank, sameFile, st_pos) + "x" + takeCord


def notatePawnMove(move: tuple[tuple[int, int], tuple[int, int], int]) -> str:
    if move[2] == move_types[enPassantLeft] or move[2] == move_types[enPassantRight]:
        return notateEnPassant(move[0], move[2])

    if move[2] == move_types[take] or move[2] == move_types[takeAndPromote]:
        direction:  int = move[1][1] - move[0][1]
        samePiece: int = 1
        sameRank: int = 1
        sameFile: int = 1

        def checkPawn(rank: int, file: int, st_pos, *enPassant):
            global pawn
            nonlocal samePiece, sameRank, sameFile
            checkingPiece: Piece = getPiece((rank, file))
            if checkingPiece.name == pawn and (enPassant == () or checkingPiece.en_passant == enPassant[0]):
                samePiece += 1
                if rank == st_pos[0]:
                    sameRank += 1
                if file == st_pos[1]:
                    sameFile += 1

        checkPawn(move[0][0], move[0][1] + 2 * direction, move[0])

        checkPawn(move[0][0] + pawnDirection(current_color),
                  min(move[0][1], move[0][1] + 2*direction),
                  move[0], move_types[enPassantRight])

        checkPawn(move[0][0] + pawnDirection(current_color),
                  max(move[0][1], move[0][1] + 2 * direction),
                  move[0], move_types[enPassantLeft])

        return specifyCell(samePiece, sameRank, sameFile, move[0]) + "x" + convert_pos_to_cord(move[1])

    else:
        return convert_pos_to_cord(move[1])


def makeNotation(move: tuple[tuple[int, int], tuple[int, int], int]) -> str:
    global possible_moves_lst, take, takeAndPromote, notationsList

    notationTxt: str = ""

    if move[2] == move_types[shortCastle]:
        notationTxt = notateForCastle(move_types[shortCastle])

    elif move[2] == move_types[longCastle]:
        notationTxt = notateForCastle(move_types[longCastle])

    elif getPiece(move[0]).name == pawn:
        notationTxt = notatePawnMove(move)

    else:
        movePiece: str = getPiece(move[0]).name
        notationTxt = name_to_abbrev[movePiece]

        samePiece: int = 0
        sameRank: int = 0
        sameFile: int = 0

        for currentMove in possible_moves_lst:
            if getPiece(currentMove[0]).name == movePiece and move[1] == currentMove[1]:
                samePiece += 1
                if move[0][0] == currentMove[0][0]:
                    sameRank += 1
                if move[0][1] == currentMove[0][1]:
                    sameFile += 1

        notationTxt += specifyCell(samePiece, sameRank, sameFile, move[0])

        if move[2] == move_types[take] or move[2] == move_types[takeAndPromote]:
            notationTxt += "x"
        notationTxt += convert_pos_to_cord(move[1])

    return notationTxt



def notate(move: tuple[tuple[int, int], tuple[int, int], int]) -> None:
    if move[2] == move_types[rookCastle]:
        return
    notationsList.append(makeNotation(move))


def addPromotion(promotePiece: str):
    notationsList[-1] += "=" + name_to_abbrev[promotePiece]


def addCheck(addType: str):
    if addType == check:
        notationsList[-1] += "+"
    elif addType == checkmate:
        notationsList[-1] += "#"


def notateGameResult() -> None:
    global game_result_types, whiteWin, blackWin, gameResult

    if gameResult == game_result_types[whiteWin]:
        notationsList.append("1-0")
    elif gameResult == game_result_types[blackWin]:
        notationsList.append("0-1")
    else:
        notationsList.append("1/2-1/2")


def getNotations() -> str:
    global notationsList
    notations: str = """"""
    if len(notationsList):
        index: int = 0
        length: int = len(notationsList)
        if notationsList[-1] in ("1-0", "0-1", "1/2-1/2"):
            length -= 1
        while index < length:
            if index < length - 1:
                notations += f"{index//2 + 1}. {notationsList[index]} {notationsList[index+1]}\n"
                index += 2
            else:
                notations += f"{index // 2 + 1}. {notationsList[index]}\n"
                index += 1

        if notationsList[-1] in ("1-0", "0-1", "1/2-1/2"):
            notations += notationsList[-1]
    return notations


def printNotations() -> None:
    print(getNotations())


if __name__ == "__main__":
    print("Run from the main file...\n")
    newGame()

    def inputMove(row: int, file: int, toRow: int, toFile: int) -> bool:
        return bool(toMove((row, file), (toRow, toFile)))
    

