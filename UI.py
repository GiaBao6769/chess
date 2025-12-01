import tkinter
import time
import chessAlgorithm as cA

cA.standard_generate()

board_size: int = cA.board_size

fonts: dict[str, str] = {"title": "Garamond",
                         "notation_title": "none",
                         "notation": "inherit"}

piece_symbols: list[dict[str, str]] = [{cA.king: "♔", cA.queen: "♕", cA.rook: "♖",
                 cA.bishop: "♗", cA.knight: "♘", cA.pawn: "♙"},

                                       {cA.king: "♚", cA.queen: "♛", cA.rook: "♜",
                 cA.bishop: "♝", cA.knight: "♞", cA.pawn: "♟"}, {"place_holder": ""}]

tkinterBoard: list[list[tkinter]] = [[None] * (board_size + 2) for _ in range(board_size + 2)]

debugMode: bool = True
loadDelayTime: float = 0.5


st_pos: tuple[int, int] = (-1, -1)

lightColor: int = 0
darkColor: int = 1
stPosColor: int = 2
movableCellColor: int = 3
lastStPosColor: int = 4
lastEdPosColor: int = 5
checkCellColor: int = 6
pieceColor: int = 7

themeIndex: int = 0

themeIndexDict: dict[str, int] = {"livid": 0}
themesList: list[list[str]] = [["white", "gray", "#f9e076", "light yellow", "#FFF5EE", "#FFF5EE", "#ff7474", "black"]]

noneTuple: tuple[int, int] = (-1, -1)

colored_move_cell_lst: list[tuple[int, int]] = []
colored_cell_lst: list[tuple[int, int]] = []

essential_colored_cell: list[tuple[int, int]] = [noneTuple, noneTuple, noneTuple] # last st_pos, last et_pos, check_pos

notationCnt: int = 0


def cellParity(row: int, file: int) -> int:
    global lightColor, darkColor
    if (row+file) % 2:
        return darkColor
    return lightColor


def colorCellWithIndex(row: int, file: int, color_index: int):
    global themeIndex, themesList
    tkinterBoard[row][file].config(bg=themesList[themeIndex][color_index])

def colorCellWithStr():
    raise NotImplementedError


def colorCells(row: int, file: int, color_index: int, colored_lst: list[tuple[int, int]]) -> None:
    colorCellWithIndex(row, file, color_index)
    colored_lst.append((row, file))


def colorEssentialCells():
    global essential_colored_cell, noneTuple, tkinterBoard
    if essential_colored_cell[0] != noneTuple:
        colorCellWithIndex(essential_colored_cell[0][0], essential_colored_cell[0][1], lastStPosColor)
    if essential_colored_cell[1] != noneTuple:
        colorCellWithIndex(essential_colored_cell[1][0], essential_colored_cell[1][1], lastEdPosColor)
    if essential_colored_cell[2] != noneTuple:
        colorCellWithIndex(essential_colored_cell[2][0], essential_colored_cell[2][1], checkCellColor)
        # tkinterBoard[essential_colored_cell[2][0]][essential_colored_cell[2][1]].config(font=("inherit", 20, "italic"))


def deColorCells(colored_lst) -> None:
    for pos in colored_lst:
        if pos == noneTuple:
            continue
        colorCellWithIndex(pos[0], pos[1], cellParity(pos[0], pos[1]))
    colored_lst.clear()


def deColorEssentialCells() -> None:
    global essential_colored_cell, noneTuple

    # if essential_colored_cell[2] != noneTuple:
    #     tkinterBoard[essential_colored_cell[2][0]][essential_colored_cell[2][1]].config(font=("inherit", 20))
    for index in range(len(essential_colored_cell)):
        if essential_colored_cell[index] == noneTuple:
            continue
        colorCellWithIndex(essential_colored_cell[index][0],
                           essential_colored_cell[index][1],
                           cellParity(essential_colored_cell[index][0], essential_colored_cell[index][1]))
        essential_colored_cell[index] = noneTuple



def getInfo(r: int, f: int) -> None:
    if debugMode:
        print(f"tkinter_position={r, f}, board_position={cA.convert_pos_to_cord((r, f))},", cA.getPiece((r-1, f-1)))


def displayPromoteWindow() -> str:
    rt_piece: str = cA.queen

    def return_queen():
        nonlocal rt_piece
        rt_piece = cA.queen
        promote_window.destroy()

    def return_rook():
        nonlocal rt_piece
        rt_piece = cA.rook
        promote_window.destroy()

    def return_bishop():
        nonlocal rt_piece
        rt_piece = cA.bishop
        promote_window.destroy()

    def return_knight():
        nonlocal rt_piece
        rt_piece = cA.knight
        promote_window.destroy()

    promote_window = tkinter.Toplevel()
    promote_window.grab_set()

    promote_frame = tkinter.Frame(promote_window)


    queen_button = tkinter.Button(promote_frame, text=piece_symbols[cA.current_color]["queen"],
                                  font=("Inherit", 15), command=return_queen)
    rook_button = tkinter.Button(promote_frame, text=piece_symbols[cA.current_color]["rook"],
                                 font=("Inherit", 15), command=return_rook)
    bishop_button = tkinter.Button(promote_frame, text=piece_symbols[cA.current_color]["bishop"],
                                   font=("Inherit", 15), command=return_bishop)
    knight_button = tkinter.Button(promote_frame, text=piece_symbols[cA.current_color]["knight"],
                                   font=("Inherit", 15), command=return_knight)

    queen_button.grid(row=0, column=0)
    rook_button.grid(row=0, column=1)
    bishop_button.grid(row=0, column=2)
    knight_button.grid(row=0, column=3)

    promote_frame.pack()
    promote_window.wait_window()

    return rt_piece


def configMove(st_pos, ed_pos, moveType, *args):
    crank, cfile = ed_pos
    rank, file = crank+1, cfile+1

    tkinterBoard[rank][file].config(text=tkinterBoard[st_pos[0] + 1][st_pos[1] + 1]["text"])
    tkinterBoard[st_pos[0] + 1][st_pos[1] + 1].config(text="")

    if moveType == cA.move_types[cA.shortCastle]:
        tkinterBoard[rank][file - 1].config(text=tkinterBoard[st_pos[0] + 1][st_pos[1] + 4]["text"])
        tkinterBoard[st_pos[0] + 1][st_pos[1] + 4].config(text="")

    elif moveType == cA.move_types[cA.longCastle]:
        tkinterBoard[rank][file + 1].config(text=tkinterBoard[st_pos[0] + 1][st_pos[1] - 3]["text"])
        tkinterBoard[st_pos[0] + 1][st_pos[1] - 3].config(text="")

    elif moveType == cA.move_types[cA.enPassantLeft] or moveType == cA.move_types[cA.enPassantRight]:
        tkinterBoard[rank - cA.pawnDirection((cA.current_color + 1) % 2)][file].config(text="")

    elif moveType == cA.move_types[cA.promotion] or moveType == cA.move_types[cA.takeAndPromote]:
        if args == ():
            promotePiece: str = displayPromoteWindow()
            tkinterBoard[rank][file].config(text=piece_symbols[cA.current_color][promotePiece])
            cA.toPromote((crank, cfile), promotePiece)
        else:
            tkinterBoard[rank][file].config(text=piece_symbols[cA.opsColor(cA.current_color)][cA.getPiece(ed_pos).name])


def getPos(rank: int, file: int) -> None:
    crank, cfile = rank-1, file-1
    global st_pos
    if st_pos == (-1, -1):
        if cA.classBoard[crank][cfile].color == cA.current_color:
            st_pos = (crank, cfile)
            colorCells(rank, file, stPosColor, colored_move_cell_lst)

            for moves in cA.possible_moves_lst:
                if moves[0] == st_pos:
                    colorCells(moves[1][0]+1, moves[1][1]+1, movableCellColor, colored_move_cell_lst)

    elif st_pos == (crank, cfile):
        deColorCells(colored_move_cell_lst)
        st_pos = (-1, -1)

    else:
        moveType: int = cA.toMove(st_pos, (crank, cfile))

        if moveType:
            configMove(st_pos, (rank-1, file-1), moveType)
            beginningPhase()
            essential_colored_cell[0] = (st_pos[0] + 1, st_pos[1] + 1)
            essential_colored_cell[1] = (rank, file)

        deColorCells(colored_move_cell_lst)
        colorEssentialCells()
        st_pos = (-1, -1)
        getPos(rank, file)


def loadNotation():
    global loadDelayTime
    newGame()
    with open("Chess_Notation", "r") as notation_file:
        for line in notation_file:
            notationList = list(line.split())

            for id in range(1, len(notationList)):
                move: tuple[tuple[int, int], tuple[int, int], int] = cA.toMoveWithNotation(notationList[id])
                if move == (noneTuple, noneTuple, 0):
                    print(f"Invalid move {move}")
                    return
                configMove(move[0], move[1], move[2], 1)
                beginningPhase()

                essential_colored_cell[0] = (move[0][0] + 1, move[0][1] + 1)
                essential_colored_cell[1] = (move[1][0] + 1, move[1][1] + 1)
                colorEssentialCells()

                window.update()
                time.sleep(loadDelayTime)


def beginningPhase() -> None:
    global notationCnt
    deColorEssentialCells()
    if cA.isInCheck:
        essential_colored_cell[2] = [cA.kings_lst[cA.current_color].position[0] +1,
                                     cA.kings_lst[cA.current_color].position[1] + 1]

    # <-----[Write Notation]----->
    length: int = len(cA.notationsList)


    for index in range(notationCnt, len(cA.notationsList)):
        notationTxt: str = ""
        if cA.notationsList[index] in ("1-0", "0-1", "1/2-1/2"):
            pass
        elif index % 2:
            notationTxt = notationListbox.get(tkinter.END) + " "
            notationListbox.delete(tkinter.END)
        else:
            notationTxt = f"{(length + 1) // 2}. "

        notationTxt += cA.notationsList[index]
        notationListbox.insert(tkinter.END, notationTxt)

    notationCnt = len(cA.notationsList)


def saveNotation():
    if len(cA.notationsList):
        with open("Chess_Notation", "w") as notation_file:
            notation_file.flush()
            index: int = 0
            length: int = len(cA.notationsList)
            if cA.notationsList[-1] in ("1-0", "0-1", "1/2-1/2"):
                length -= 1
            while index < length:
                if index < length - 1:
                    notation_file.write(f"{index // 2 + 1}. {cA.notationsList[index]} {cA.notationsList[index + 1]}")
                    index += 2
                else:
                    notation_file.write(f"{index // 2 + 1}. {cA.notationsList[index]}")
                    index += 1
                notation_file.write("\n")
            if cA.notationsList[-1] in ("1-0", "0-1", "1/2-1/2"):
                notation_file.write(cA.notationsList[-1])


def buildBoard() -> None:
    for rank in range(1, board_size+1):
        for file in range(1, board_size+1):
            current_cell = cA.classBoard[rank-1][file-1]
            tkinterBoard[rank][file] = tkinter.Button(boardFrame,
                                                     text=piece_symbols[current_cell.color][current_cell.name],
                                                     fg=themesList[themeIndex][pieceColor],
                                                     font=("inherit", 20),
                                                      height=1, width=3
                                                     )
            colorCellWithIndex(rank, file, cellParity(rank, file))
            tkinterBoard[rank][file].bind('<Button-3>', lambda e, r=rank, f=file: getInfo(r, f), add="+")
            tkinterBoard[rank][file].bind('<Button-1>', lambda e, r=rank, f=file: getPos(r, f), add="+")
            tkinterBoard[rank][file].grid(row=rank, column=file, sticky="nsew")


def deleteNotation():
    global notationListbox
    notationListbox.delete(2, tkinter.END)


def newGame() -> None:
    global notationListbox, notationCnt
    cA.newGame()
    buildBoard()
    deColorCells(colored_move_cell_lst)
    deColorCells(colored_cell_lst)
    deColorEssentialCells()


    deleteNotation()
    notationCnt = 0

window = tkinter.Tk()
window.title("Chess UI")

chessLabel = tkinter.Label(window, text="CHESS", font=("Garamond", 25))

centerFrame = tkinter.Frame(window)


boardFrame = tkinter.Frame(centerFrame)

cordColorList: list[str] = ["#E5E4E2", "#D3D3D3", "#C0C0C0"]

tkinter.Label(boardFrame, bg=cordColorList[2]).grid(row=0, column=0, sticky='nsew')
tkinter.Label(boardFrame, bg=cordColorList[2]).grid(row=board_size+1, column=0, sticky='nsew')
tkinter.Label(boardFrame, bg=cordColorList[2]).grid(row=0, column=board_size+1, sticky='nsew')
tkinter.Label(boardFrame, bg=cordColorList[2]).grid(row=board_size+1, column=board_size+1, sticky='nsew')

for index in range(1, board_size+1):
    tkinter.Label(boardFrame,
                  text=chr(96 + index),
                  bg=cordColorList[cellParity(index, 0)]).grid(row=0, column=index, sticky='nsew')

    tkinter.Label(boardFrame,
                  text=chr(96 + index),
                  bg=cordColorList[cellParity(index, 1)]).grid(row=board_size+1, column=index, sticky='nsew')

    tkinter.Label(boardFrame,
                  text=index, width=2,
                  bg=cordColorList[cellParity(index, 1)]).grid(row=9-index, column=0, sticky='nsew')

    tkinter.Label(boardFrame,
                  text=index, width=2,
                  bg=cordColorList[cellParity(index, 0)]).grid(row=9-index, column=board_size+1, sticky='nsew')


# boardFrame.rowconfigure((0, 9), minsize=10, weight=10)
# boardFrame.columnconfigure((0, 9), minsize=10, weight=10)

functionFrame = tkinter.Frame(window)

resetButton = tkinter.Button(functionFrame, text="Reset", font=("inherit", 10),
                             command=newGame)
resetButton.grid(row=0, column=0)

notationButton = tkinter.Button(functionFrame, text="Notate", font=("inherit", 10),
                                command=cA.printNotations)
notationButton.grid(row=0, column=1)

loadNotationButton = tkinter.Button(functionFrame, text="Load Notation", font=("inherit", 10),
                                command=loadNotation)
loadNotationButton.grid(row=0, column=2)

saveNotationButton = tkinter.Button(functionFrame, text="Save Notation", font=("inherit", 10),
                                command=saveNotation)
saveNotationButton.grid(row=0, column=3)

# <-----[Notation Listbox]----->
notationListbox = tkinter.Listbox(window)
notationLabel = tkinter.Label(notationListbox, text="Notation", font=("inherit", 15, "bold"), bg="white")
notationListbox.insert(0, "")
notationListbox.insert(1, "")

chessLabel.grid(row=0, column=0)

centerFrame.grid(row=1, column=0)
boardFrame.grid(row=1, column=1)


notationLabel.grid(row=0, column=1, rowspan=2)
notationListbox.grid(row=0, column=1, rowspan=2, sticky='nsew')
functionFrame.grid(row=2, column=0, columnspan=2, sticky='nsew')


if __name__ == "__main__":
    newGame()
    window.mainloop()


