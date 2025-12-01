import tkinter
import time

place_holder: int = 0

current_color: int = 1
move_restrict: bool = False

in_check: bool = False
notation_cnt: int = 2

fifty_cnt: int = 0

check_board: list[list[int]] = [[place_holder] * 8 for _ in range(8)]
piece_symbol: list[dict[str, str]] = [{"King": "♔", "Queen": "♕", "Rook": "♖",
                 "Bishop": "♗", "Knight": "♘", "Pawn": "♙"},

                {"King": "♚", "Queen": "♛", "Rook": "♜",
                 "Bishop": "♝", "Knight": "♞", "Pawn": "♟"}]

abbrev_piece_name: dict[str, str] = {"King": "K", "Queen": "Q", "Rook": "R",
                 "Bishop": "B", "Knight": "N", "Pawn": ""}

abbrev_to_name: dict[str, str] = {"K": "King", "Q": "Queen", "R": "Rook",
                 "B": "Bishop", "N": "Knight"}

piece_value: dict[str, int] = {"King": 3, "Queen": 9, "Rook": 5,
                 "Bishop": 3, "Knight": 3, "Pawn": 1}

class_board: list[list[int]] = [[place_holder] * 8 for _ in range(8)]

display_chess_cells: list[list[any]] = [[0] * 8 for _ in range(8)]

taken_piece_index: dict[str, int] = {"Pawn": 0, "Knight": 1, "Bishop": 2, "Rook": 3, "Queen": 4}
taken_piece_icons: list = ["Pawn", "Knight", "Bishop", "Rook", "Queen"]
taken_piece_config: list[list[int]] = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
point_config: list[int, int] = [0, 0]

bg_color = [["white", "gray", "#f9e076", "light yellow", "#ff7474", "black", "#FFF5EE"], #Livid
            ["#d8e3cd", "#4d6338", "#66CC66", "#99FF99", "#864e21", "#003300", "#FFF5EE"], #Nature
            ["#fff8dc", "#8b6914", "#a9916b", "#e3d6ab", "#ff6347", "#130f0e", "#FFF5EE"], #Classic
            ["#ADD8E6", "#0077B6", "#99CCFF", "#F0FFFF", "#FF1FCE", "#00254d", "#FFF5EE"], #Ocean
            ["#ffd1dc", "#e75480", "#fc0fc0", "#f987c5", "#ff2800", "#381f33", "#FFF5EE"],
            # ["#f5dfaa", "#433519", "#f9e076", "light yellow", "#ff7474", "black", "#FFF5EE"]
            ]
            # light color, dark color, chosen cell color, movable cell color, check color, piece color, just-moved-cell
bg_color_name = ["Livid", "Nature", "Classic", "Ocean", "Woke"]
theme_color = 0

king_lst: list[any] = []

threefold_repetition_position_lst: dict[str, int] = {}

allowed_moves_lst: list[tuple[tuple[int, int], tuple[int, int]]] = []

colored_cells: list[tuple[int, int]] = []

st_cord: tuple[int, int] = (-1, -1) # the position of the initial piece to move
just_moved_cells: list[tuple[int, int]] = []


def print_board():
    for i in range(8):
        print(*check_board[i])


def print_class_board():
    for i in range(8):
        print(*class_board[i])


def convert_position(pos: str) -> tuple:
    # turn the position of a piece to the coordinate on the board
    return 8 - int(pos[1]), ord(pos[0]) - 97


def convert_coordinate(cord: tuple) -> str:
    # turn the coordinate of a piece on the board to the position
    return chr(cord[1] + 97) + str(8 - cord[0])


def convert_pos_to_file(x: int) -> str:
    return chr(97 + x)


def convert_file_to_pos(char: str) -> int:
    return ord(char) - 97


def convert_pos_and_rank(x: int) -> int:
    return 8 - x

def get_piece(pos: tuple[int, int]):
    return class_board[pos[0]][pos[1]]


def check_unoccupied(pos: tuple[int, int]) -> bool:
    if class_board[pos[0]][pos[1]] == place_holder:
        return True
    return False


class Piece:

    def __init__(self, name: str, color: int, value: int, position: tuple[int, int]):
        # name is the name of the piece declared
        # color is the color of the piece declared with 0 is white and 1 is black
        # value is the value of the piece declared
        # position is the position of the piece declared on the board
        self.name = name
        self.color = color
        self.value = value
        self.position = position

    def __str__(self):
        return f"Name: {self.name}\nColor: {['White', 'Black'][self.color]}\nPoint: {self.value}\nPosition: {self.position}"

    def build_piece(self):
        class_board[self.position[0]][self.position[1]] = self

        check_board[self.position[0]][self.position[1]] = (self.name, self.color)

        config_piece(self.position, piece_symbol[self.color][self.name])

    def destroy_piece(self):
        global threefold_repetition_position_lst, taken_piece_index, taken_piece_config, point_config

        threefold_repetition_position_lst = {}
        class_board[self.position[0]][self.position[1]] = place_holder

        taken_piece_config[self.color][taken_piece_index[self.name]] += 1

        point_config[self.color] += self.value
        config_taken_piece_frame(self.color)

        check_board[self.position[0]][self.position[1]] = place_holder
        config_piece(self.position, "")

        self.position = (-1, -1)

    def move(self, pos: tuple):
        write_notation(self.position, pos, self.name)

        if class_board[pos[0]][pos[1]] != place_holder:
            taken_piece = class_board[pos[0]][pos[1]]
            taken_piece.destroy_piece()

            global fifty_cnt
            fifty_cnt = 0

        class_board[self.position[0]][self.position[1]] = place_holder

        check_board[self.position[0]][self.position[1]] = place_holder

        config_piece(self.position, "")

        self.position = pos
        self.build_piece()


class King(Piece):

    def __init__(self, name, color, value, position):
        super().__init__(name, color, value, position)
        self.first_move = True

    def possible_king_move(self) -> list[tuple]:
        move_list: list[tuple] = []
        for ud in [-1, 0, 1]:
            for lr in [-1, 0, 1]:
                if ud == 0 and lr == 0:
                    continue
                row, col = self.position
                if (0 <= row + ud < 8) and (0 <= col + lr < 8):
                    if class_board[row + ud][col + lr] == place_holder:
                        move_list.append((row + ud, col + lr))
                    else:
                        obstacle = class_board[row + ud][col + lr]
                        if obstacle.color != self.color:
                            move_list.append((row + ud, col + lr))
        return move_list

    def possible_castle_moves(self) -> list[tuple]:
        global in_check

        move_castle: list[tuple] = []

        if self.first_move is True and in_check is False:
            if self.color == 0:
                current_piece_fst = get_piece(convert_position("h1"))
                current_piece_snd = get_piece(convert_position("a1"))

                if (current_piece_fst != place_holder and current_piece_fst.name == "Rook" and current_piece_fst.first_move is True) and\
                        (check_unoccupied(convert_position("f1")) and check_unoccupied(convert_position("g1"))) and \
                        (check_king(convert_position("f1")) is True and check_king(convert_position("g1")) is True):
                    move_castle.append((7, 6))

                if current_piece_snd != place_holder and current_piece_snd.name == "Rook" and current_piece_snd.first_move is True and\
                        (check_unoccupied(convert_position("d1")) and check_unoccupied(convert_position("c1")) and check_unoccupied(convert_position("b1"))) and\
                        check_king(convert_position("d1")) is True and check_king(convert_position("c1")) is True:
                    move_castle.append((7, 2))

            else:
                current_piece_fst = get_piece(convert_position("h8"))
                current_piece_snd = get_piece(convert_position("a8"))

                if current_piece_fst != place_holder and current_piece_fst.name == "Rook" and current_piece_fst.first_move is True and\
                        (check_unoccupied(convert_position("f8")) and check_unoccupied(convert_position("g8"))) and\
                        check_king(convert_position("f8")) is True and check_king(convert_position("g8")) is True:
                    move_castle.append((0, 6))

                if current_piece_snd != place_holder and current_piece_snd.name == "Rook" and current_piece_snd.first_move is True and\
                        (check_unoccupied(convert_position("d8")) and check_unoccupied(convert_position("c8")) and check_unoccupied(convert_position("b8"))) and\
                        check_king(convert_position("d8")) is True and check_king(convert_position("c8")) is True:
                    move_castle.append((0, 2))
        return move_castle

    def possible_move(self) -> list[tuple]:
        # if self.color != current_color:
        #     return self.possible_king_move()
        return self.possible_king_move() + self.possible_castle_moves()

    def move(self, pos: tuple):
        global threefold_repetition_position_lst
        check_castle: bool = False

        if self.first_move is True:
            if self.color == 0:
                if pos == (7, 6):
                    current_piece = get_piece(convert_position("h1"))
                    current_piece.move(convert_position("f1"), 1)
                    write_notation_castle(0)
                    check_castle = True
                elif pos == (7, 2):
                    current_piece = get_piece(convert_position("a1"))
                    current_piece.move(convert_position("d1"), 1)
                    write_notation_castle(1)
                    check_castle = True
            else:
                if pos == (0, 6):
                    current_piece = get_piece(convert_position("h8"))
                    current_piece.move(convert_position("f8"), 1)
                    write_notation_castle(0)
                    check_castle = True
                elif pos == (0, 2):
                    current_piece = get_piece(convert_position("a8"))
                    current_piece.move(convert_position("d8"), 1)
                    write_notation_castle(1)
                    check_castle = True

            self.first_move = False

            threefold_repetition_position_lst = {}

        if check_castle is False:
            write_notation(self.position, pos, self.name)

        if class_board[pos[0]][pos[1]] != place_holder:
            taken_piece = class_board[pos[0]][pos[1]]
            taken_piece.destroy_piece()

            global fifty_cnt
            fifty_cnt = 0

        class_board[self.position[0]][self.position[1]] = place_holder

        check_board[self.position[0]][self.position[1]] = place_holder

        config_piece(self.position, "")

        self.position = pos
        self.build_piece()


class Rook(Piece):
    first_move = True

    def __init__(self, name, color, value, position):
        super().__init__(name, color, value, position)

    def possible_rook_move(self) -> list[tuple]:
        move_list = []
        for ud, lr in [[0, 1], [1, 0], [0, -1], [-1, 0]]:
            row, col = self.position
            while (0 <= row + ud < 8) and (0 <= col + lr < 8) and (class_board[row + ud][col + lr] == place_holder):
                row += ud
                col += lr
                move_list.append((row, col))
            if (0 <= row + ud < 8) and (0 <= col + lr < 8) and (class_board[row + ud][col + lr] != place_holder):
                obstacle = class_board[row + ud][col + lr]
                if obstacle.color != self.color:
                    move_list.append((row + ud, col + lr))
        return move_list

    def possible_move(self) -> list[tuple]:
        return self.possible_rook_move()

    def move(self, pos: tuple, *args):
        global threefold_repetition_position_lst, king_lst
        if self.first_move is True:
            self.first_move = False

            if king_lst[self.color].first_move is True:
                threefold_repetition_position_lst = {}

        if args == ():
            write_notation(self.position, pos, self.name)

        if class_board[pos[0]][pos[1]] != place_holder:
            taken_piece = class_board[pos[0]][pos[1]]
            taken_piece.destroy_piece()

            global fifty_cnt
            fifty_cnt = 0

        class_board[self.position[0]][self.position[1]] = place_holder

        check_board[self.position[0]][self.position[1]] = place_holder

        config_piece(self.position, "")

        self.position = pos
        self.build_piece()


class Bishop(Piece):
    def __init__(self, name, color, value, position):
        super().__init__(name, color, value, position)

    def possible_bishop_move(self) -> list[tuple]:
        move_list = []
        for ud in [1, -1]:
            for lr in [1, -1]:
                row, col = self.position
                while (0 <= row + ud < 8) and (0 <= col + lr < 8) and (class_board[row + ud][col + lr] == place_holder):
                    row += ud
                    col += lr
                    move_list.append((row, col))
                if (0 <= row + ud < 8) and (0 <= col + lr < 8) and (class_board[row + ud][col + lr] != place_holder):
                    obstacle = class_board[row + ud][col + lr]
                    if obstacle.color != self.color:
                        move_list.append((row + ud, col + lr))
        return move_list

    def possible_move(self) -> list[tuple]:
        return self.possible_bishop_move()


class Queen(Bishop, Rook):
    def __init__(self, name, color, value, position):
        super().__init__(name, color, value, position)

    def possible_move(self) -> list[tuple]:
        return self.possible_bishop_move() + self.possible_rook_move()


class Knight(Piece):
    def __init__(self, name, color, value, position):
        super().__init__(name, color, value, position)

    def possible_move(self) -> list[tuple]:
        move_list = []
        row, col = self.position
        for ud in [1, -1]:
            for lr in [2, -2]:
                for udx, lrx in [[ud, lr], [lr, ud]]:
                    if (0 <= row + udx < 8) and (0 <= col + lrx < 8):
                        if class_board[row + udx][col + lrx] == place_holder:
                            move_list.append((row + udx, col + lrx))
                        else:
                            obstacle = class_board[row + udx][col + lrx]
                            if obstacle.color != self.color:
                                move_list.append((row + udx, col + lrx))

        return move_list


class Pawn(Piece):

    def __init__(self, name: str, color: int, value: int, position: tuple[int, int]):
        # first_move checks if the pawn can make a two-square move
        # en_passant checks if the pawn can make an en passant move
        super().__init__(name, color, value, position)

        self.first_move = True
        self.en_passant = 0

        # 0 equivalent to no en_passant move available
        # 1 to en_passant to right
        # -1 to en_passant to left

    def possible_move(self):
        move_list: list[tuple] = []
        direction: int = 2 * self.color - 1

        if class_board[self.position[0] + direction][self.position[1]] == place_holder:
            move_list.append((self.position[0] + direction, self.position[1]))

            if self.first_move is True and class_board[self.position[0] + 2 * direction][self.position[1]] == place_holder:
                move_list.append((self.position[0] + 2 * direction, self.position[1]))

        if self.position[1] > 0 and class_board[self.position[0] + direction][self.position[1] - 1] != place_holder:
            taken_piece = class_board[self.position[0] + direction][self.position[1] - 1]
            if taken_piece.color != self.color:
                move_list.append((self.position[0] + direction, self.position[1] - 1))

        if self.position[1] < 7 and class_board[self.position[0] + direction][self.position[1] + 1] != place_holder:
            taken_piece = class_board[self.position[0] + direction][self.position[1] + 1]
            if taken_piece.color != self.color:
                move_list.append((self.position[0] + direction, self.position[1] + 1))

        # 1 to en_passant to right
        # -1 to en_passant to left
        if self.en_passant == 1:
            move_list.append((self.position[0] + direction, self.position[1] + 1, 1))

        elif self.en_passant == -1:
            move_list.append((self.position[0] + direction, self.position[1] - 1, -1))

        return move_list

    def move(self, pos: tuple):
        global fifty_cnt, threefold_repetition_position_lst
        fifty_cnt = 0

        if self.first_move is True:
            self.first_move = False

            # Make adjacent pawn able to en passant
            if (self.color == 0 and pos[0] == 4) or (self.color == 1 and pos[0] == 3):
                left_piece = place_holder
                right_piece = place_holder

                if pos[1] > 0:
                    left_piece = get_piece((pos[0], pos[1] - 1))
                if pos[1] < 7:
                    right_piece = get_piece((pos[0], pos[1] + 1))

                if (left_piece != place_holder) and (left_piece.name == "Pawn" and left_piece.color != self.color):
                    left_piece.en_passant = 1

                if (right_piece != place_holder) and (right_piece.name == "Pawn" and right_piece.color != self.color):
                    right_piece.en_passant = -1

                # 1 to en_passant to right
                # -1 to en_passant to left

        if class_board[pos[0]][pos[1]] == place_holder and abs(pos[1] - self.position[1]) == 1:
            if self.en_passant == 1:
                taken_piece = class_board[self.position[0]][self.position[1] + 1]
                taken_piece.destroy_piece()
            else:
                taken_piece = class_board[self.position[0]][self.position[1] - 1]
                taken_piece.destroy_piece()
            write_notation(self.position, pos, self.name, 1)

        else:
            write_notation(self.position, pos, self.name)

        if class_board[pos[0]][pos[1]] != place_holder:
            taken_piece = class_board[pos[0]][pos[1]]

            taken_piece.destroy_piece()

        class_board[self.position[0]][self.position[1]] = place_holder

        config_piece(self.position, "")

        check_board[self.position[0]][self.position[1]] = place_holder

        threefold_repetition_position_lst = {}

        self.position = pos

        self.build_piece()
        self.promote()

    def promote(self):
        global move_restrict, point_config
        if (self.color == 0 and self.position[0] == 0) or (self.color == 1 and self.position[0] == 7):
            move_restrict = True

            new_piece: str = "Queen"
            new_piece = promote_display()

            if new_piece == "Queen":
                self.__class__ = Queen
            elif new_piece == "Rook":
                self.__class__ = Rook
            elif new_piece == "Bishop":
                self.__class__ = Bishop
            elif new_piece == "Knight":
                self.__class__ = Knight

            move_restrict = False

            self.name = new_piece
            self.point = piece_value[new_piece]
            self.build_piece()

            write_notation_promote(abbrev_piece_name[new_piece])

            point_config[(self.color + 1) % 2] += self.point - 1
            config_point_frame()


def standard_pieces_generate():
    global king_lst
    W_pawn1 = Pawn("Pawn", 0, 1, convert_position('a2'))
    W_pawn2 = Pawn("Pawn", 0, 1, convert_position('b2'))
    W_pawn3 = Pawn("Pawn", 0, 1, convert_position('c2'))
    W_pawn4 = Pawn("Pawn", 0, 1, convert_position('d2'))
    W_pawn5 = Pawn("Pawn", 0, 1, convert_position('e2'))
    W_pawn6 = Pawn("Pawn", 0, 1, convert_position('f2'))
    W_pawn7 = Pawn("Pawn", 0, 1, convert_position('g2'))
    W_pawn8 = Pawn("Pawn", 0, 1, convert_position('h2'))

    W_pawn1.build_piece()
    W_pawn2.build_piece()
    W_pawn3.build_piece()
    W_pawn4.build_piece()
    W_pawn5.build_piece()
    W_pawn6.build_piece()
    W_pawn7.build_piece()
    W_pawn8.build_piece()

    W_king = King("King", 0, 3, convert_position("e1"))
    W_queen = Queen("Queen", 0, 9, convert_position("d1"))
    W_rook1 = Rook("Rook", 0, 5, convert_position("a1"))
    W_rook2 = Rook("Rook", 0, 5, convert_position("h1"))
    W_bishop1 = Bishop("Bishop", 0, 3, convert_position("c1"))
    W_bishop2 = Bishop("Bishop", 0, 3, convert_position("f1"))
    W_knight1 = Knight("Knight", 0, 3, convert_position("b1"))
    W_knight2 = Knight("Knight", 0, 3, convert_position("g1"))

    W_king.build_piece()
    W_queen.build_piece()
    W_rook1.build_piece()
    W_rook2.build_piece()
    W_bishop1.build_piece()
    W_bishop2.build_piece()
    W_knight1.build_piece()
    W_knight2.build_piece()

    B_pawn1 = Pawn("Pawn", 1, 1, convert_position('a7'))
    B_pawn2 = Pawn("Pawn", 1, 1, convert_position('b7'))
    B_pawn3 = Pawn("Pawn", 1, 1, convert_position('c7'))
    B_pawn4 = Pawn("Pawn", 1, 1, convert_position('d7'))
    B_pawn5 = Pawn("Pawn", 1, 1, convert_position('e7'))
    B_pawn6 = Pawn("Pawn", 1, 1, convert_position('f7'))
    B_pawn7 = Pawn("Pawn", 1, 1, convert_position('g7'))
    B_pawn8 = Pawn("Pawn", 1, 1, convert_position('h7'))

    B_pawn1.build_piece()
    B_pawn2.build_piece()
    B_pawn3.build_piece()
    B_pawn4.build_piece()
    B_pawn5.build_piece()
    B_pawn6.build_piece()
    B_pawn7.build_piece()
    B_pawn8.build_piece()

    B_king = King("King", 1, 3, convert_position("e8"))
    B_queen = Queen("Queen", 1, 9, convert_position("d8"))
    B_rook1 = Rook("Rook", 1, 5, convert_position("a8"))
    B_rook2 = Rook("Rook", 1, 5, convert_position("h8"))
    B_bishop1 = Bishop("Bishop", 1, 3, convert_position("c8"))
    B_bishop2 = Bishop("Bishop", 1, 3, convert_position("f8"))
    B_knight1 = Knight("Knight", 1, 3, convert_position("b8"))
    B_knight2 = Knight("Knight", 1, 3, convert_position("g8"))

    B_king.build_piece()
    B_queen.build_piece()
    B_rook1.build_piece()
    B_rook2.build_piece()
    B_bishop1.build_piece()
    B_bishop2.build_piece()
    B_knight1.build_piece()
    B_knight2.build_piece()

    king_lst = [W_king, B_king]


def test_pieces_generate():
    global king_lst
    W_king = King("King", 0, 3, convert_position("e1"))
    # W_rook1 = Rook("Rook", 0, 5, convert_position("a1"))
    # W_rook2 = Rook("Rook", 0, 5, convert_position("h1"))
    #
    W_king.build_piece()
    # W_rook1.build_piece()
    # W_rook2.build_piece()
    #
    B_king = King("King", 1, 3, convert_position("e8"))
    # B_rook1 = Rook("Rook", 1, 5, convert_position("a8"))
    # B_rook2 = Rook("Rook", 1, 5, convert_position("h8"))
    # B_rook3 = Rook("Rook", 1, 5, convert_position("a8"))
    # B_rook44 = Rook("Rook", 1, 5, convert_position("h8"))
    #
    B_king.build_piece()
    # B_rook1.build_piece()
    # B_rook2.build_piece()
    # W_pawn1 = Pawn("Pawn", 0, 1, convert_position('a2'))
    # W_pawn1.build_piece()

    # B_pawn8 = Pawn("Pawn", 1, 1, convert_position('h7'))
    # B_pawn8.build_piece()

    # B_bishop1 = Bishop("Bishop", 1, 3, convert_position("c4"))
    # B_bishop2 = Bishop("Bishop", 1, 3, convert_position("e4"))
    # B_bishop3 = Bishop("Bishop", 1, 3, convert_position("c6"))
    # B_bishop4 = Bishop("Bishop", 1, 3, convert_position("e6"))

    # B_bishop1.build_piece()
    # B_bishop2.build_piece()
    # B_bishop3.build_piece()
    # B_bishop4.build_piece()
    # Pawn("Pawn", 0, 1, convert_position("c4")).build_piece()
    Pawn("Pawn", 0, 1, convert_position("c5")).build_piece()
    Pawn("Pawn", 0, 1, convert_position("e4")).build_piece()
    Pawn("Pawn", 0, 1, convert_position("e5")).build_piece()

    Pawn("Pawn", 1, 1, convert_position("d7")).build_piece()
    king_lst = [W_king, B_king]


def check_king(king_pos: tuple[int, int], *args) -> bool:
    # True for no threat, otherwise False
    global current_color

    # check for Pawn
    direction: int = 2 * current_color - 1
    if 0 <= king_pos[0] + direction < 8:
        if king_pos[1] > 0 and check_board[king_pos[0] + direction][king_pos[1] - 1] == ("Pawn", (current_color + 1) % 2):
            return False
        if king_pos[1] < 7 and check_board[king_pos[0] + direction][king_pos[1] + 1] == ("Pawn", (current_color + 1) % 2):
            return False

    # check for Knight
    for ud in [2, -2]:
        for lr in [1, -1]:
            if (0 <= king_pos[0] + ud < 8 and 0 <= king_pos[1] + lr < 8) and (check_board[king_pos[0] + ud][king_pos[1] + lr] == ("Knight", (current_color + 1) % 2)) or \
                    (0 <= king_pos[0] + lr < 8 and 0 <= king_pos[1] + ud < 8) and (check_board[king_pos[0] + lr][king_pos[1] + ud] == ("Knight", (current_color + 1) % 2)):
                return False

    # check for King
    if args != ():
        for ud in [-1, 0, 1]:
            for lr in [-1, 0, 1]:
                if (ud == 0 and lr == 0) or (ud + king_pos[0] < 0 or ud + king_pos[0] >= 8) or (lr + king_pos[1] < 0 or lr + king_pos[1] >= 8):
                    continue

                if check_board[king_pos[0] + ud][king_pos[1] + lr] == ("King", (current_color + 1) % 2):
                    return False

    # check for Rook or Queen
    for ud, lr in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        pos_x: int = king_pos[0] + ud
        pos_y: int = king_pos[1] + lr

        while 0 <= pos_x < 8 and 0 <= pos_y < 8:
            if check_board[pos_x][pos_y] != place_holder:
                if (check_board[pos_x][pos_y] == ("Rook", (current_color + 1) % 2)) or (check_board[pos_x][pos_y] == ("Queen", (current_color + 1) % 2)):
                    return False
                break
            pos_x += ud
            pos_y += lr

    # check for Bishop or Queen
    for ud in [-1, 1]:
        for lr in [-1, 1]:
            pos_x: int = king_pos[0] + ud
            pos_y: int = king_pos[1] + lr

            while 0 <= pos_x < 8 and 0 <= pos_y < 8:
                if check_board[pos_x][pos_y] != place_holder:
                    if (check_board[pos_x][pos_y] == ("Bishop", (current_color + 1) % 2)) or (check_board[pos_x][pos_y] == ("Queen", (current_color + 1) % 2)):
                        return False
                    break
                pos_x += ud
                pos_y += lr
    return True


def generate_allowed_moves():
    global current_color, allowed_moves_lst
    allowed_moves_lst.clear()

    def check_allowed_move(st_pos: tuple[int, int], ed_pos: tuple[int, int]):

        org_cell = check_board[ed_pos[0]][ed_pos[1]]

        check_board[ed_pos[0]][ed_pos[1]] = check_board[st_pos[0]][st_pos[1]]
        check_board[st_pos[0]][st_pos[1]] = place_holder

        rt: bool = True

        if check_board[ed_pos[0]][ed_pos[1]][0] == "King":
            rt = check_king(ed_pos, 1)
        else:
            rt = check_king(king_lst[current_color].position)

        check_board[st_pos[0]][st_pos[1]] = check_board[ed_pos[0]][ed_pos[1]]
        check_board[ed_pos[0]][ed_pos[1]] = org_cell

        return rt

    for row in range(8):
        for col in range(8):
            if class_board[row][col] != place_holder and class_board[row][col].color == current_color:

                current_piece = class_board[row][col]
                current_pos: tuple[int, int] = current_piece.position

                for move in current_piece.possible_move():
                    if check_allowed_move(current_pos, move) is True:
                        allowed_moves_lst.append((current_pos, move))


def color_move_cells(st_cord: tuple[int, int]):
    global allowed_moves_lst, theme_color
    for move in allowed_moves_lst:
        if move[0] == st_cord:
            colored_cells.append(move[1])

            config_cell_color(move[1], 3)


def remove_colored_cells():
    global current_color, in_check, colored_cells, theme_color
    for pos in colored_cells:
        config_cell_color(pos)

    colored_cells.clear()

    if in_check is True:
        king_pos = king_lst[current_color].position
        config_cell_color(king_pos, 4)


def add_repetition():
    global threefold_repetition_position_lst, abbrev_piece_name, king_lst
    chk: bool = True
    for file in range(8):
        fst_cell = get_piece((3, file))
        if fst_cell != place_holder and fst_cell.name == "Pawn" and fst_cell.en_passant != 0:
            chk = False
            break
        snd_cell = get_piece((4, file))
        if snd_cell != place_holder and snd_cell.name == "Pawn" and snd_cell.en_passant != 0:
            chk = False
            break

    if chk is True:
        repetition_position: str = ""
        for rank in range(8):
            for file in range(8):
                current_cell = get_piece((rank, file))
                if current_cell != place_holder and current_cell.name != "King":
                    repetition_position += abbrev_piece_name[current_cell.name] + str(current_cell.color) + convert_coordinate(current_cell.position)

        def king_pos_repetition(color: int) -> None:
            nonlocal repetition_position

            king_pos = king_lst[color].position
            repetition_position += "K" + convert_coordinate(king_pos) + str(color)
            if king_lst[color].first_move is True:
                current_cell = get_piece((king_pos[0], king_pos[1] + 3))

                if current_cell != place_holder and current_cell.name == "Rook" and current_cell.first_move is True:
                    repetition_position += "S"
                current_cell = get_piece((king_pos[0], king_pos[1] - 4))
                if current_cell != place_holder and current_cell.name == "Rook" and current_cell.first_move is True:
                    repetition_position += "L"
        king_pos_repetition(0)
        king_pos_repetition(1)

        # if repetition_position in threefold_repetition_position_lst:
        #     threefold_repetition_position_lst[repetition_position] += 1
        # else:
        update_repetition = threefold_repetition_position_lst.get(repetition_position, 0)
        if update_repetition == 2:
            return True
        if update_repetition == 1:
            threefold_repetition_position_lst[repetition_position] += 1
        else:
            threefold_repetition_position_lst[repetition_position] = 1

    return False


def restart_game():
    global current_color, move_restrict, in_check, notation_cnt, fifty_cnt, check_board, class_board, display_chess_cells, \
        taken_piece_config, point_config, king_lst, threefold_repetition_position_lst, allowed_moves_lst, colored_cells, \
        st_cord, piece_label_fst, piece_label_snd, point_label_fst, point_label_snd, notation_listbox, chess_label, just_moved_cells

    current_color = 1
    move_restrict = False
    in_check = False
    notation_cnt = 2
    fifty_cnt = 0
    check_board = [[place_holder] * 8 for _ in range(8)]
    class_board = [[place_holder] * 8 for _ in range(8)]
    display_chess_cells = [[0] * 8 for _ in range(8)]
    taken_piece_config = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
    point_config = [0, 0]
    king_lst = []
    threefold_repetition_position_lst = {}
    allowed_moves_lst = []
    colored_cells = []
    st_cord = (-1, -1)
    just_moved_cells = []

    for rank in range(8):
        for file in range(8):

            current_cell = class_board[rank][file]
            cell_text: str

            if current_cell == place_holder:
                cell_text = ""
            else:
                cell_text = piece_symbol[current_cell.color][current_cell.name]

            display_chess_cells[rank][file] = tkinter.Button(board_frame, text=cell_text, font=("Inherit", 35),
                                                             height=1, width=3, bg=bg_color[theme_color][(rank + file) % 2],
                                                             activebackground=bg_color[theme_color][(rank + file) % 2],
                                                             fg=bg_color[theme_color][5],
                                                             command=lambda r=rank, c=file: return_cell_cord(r, c))
            display_chess_cells[rank][file].grid(row=rank + 1, column=file + 1)

    standard_pieces_generate()

    piece_label_fst.config(text="")
    piece_label_snd.config(text="")
    point_label_fst.config(text="")
    point_label_snd.config(text="")
    chess_label.config(text="CHESS")
    notation_listbox.delete(2, tkinter.END)

    turn_change()


def turn_change():
    global current_color, display_chess_cells, in_check, move_restrict, fifty_cnt, colored_cells, threefold_repetition_position_lst, theme_color, just_moved_cells

    king_pos = king_lst[current_color].position

    config_cell_color(king_pos)
    
    in_check = False

    current_color = (current_color + 1) % 2

    # turn all en_passant variables of opponent to False
    for col in range(8):
        if class_board[4 - current_color][col] != place_holder:
            current_piece = class_board[4 - current_color][col]
            if current_piece.color != current_color and current_piece.name == "Pawn":
                current_piece.en_passant = 0

    # check for check
    king_pos = king_lst[current_color].position

    if check_king(king_pos) is False:
        in_check = True
        write_notation_for_check()

        config_cell_color(king_pos, 4)

    generate_allowed_moves()

    # END GAME CHECK

    if len(allowed_moves_lst) == 0:
        if in_check is True:
            chess_label.config(text=f"{['WHITE', 'BLACK'][(current_color + 1) % 2]} WON!")
            write_notation_for_check(1)

            write_notation_end_game(0)
        else:
            chess_label.config(text="STALEMATE!")
            write_notation_end_game(1)
        move_restrict = True

    else:
        # insufficient material
        knight_cnt: int = 0
        bishop_lst: list[tuple[int, int]] = [] #color, cell color
        insufficient_chk: bool = True
        end_game_insufficient: bool = False

        for rank in range(8):
            for file in range(8):
                chk_cell = get_piece((rank, file))
                if chk_cell == place_holder or chk_cell.name == "King":
                    continue
                if chk_cell.name == "Knight":
                    knight_cnt += 1
                    if knight_cnt == 2:
                        insufficient_chk = False
                        break
                elif chk_cell.name == "Bishop":
                    bishop_lst.append((chk_cell.color, (rank + file) % 2))
                    if len(bishop_lst) == 3:
                        insufficient_chk = False
                        break
                else:
                    insufficient_chk = False
                    break
        if insufficient_chk is True:
            if len(bishop_lst) == 0 and knight_cnt < 2:
                end_game_insufficient = True
            elif (knight_cnt == 0 and (len(bishop_lst) < 2) or
                    (len(bishop_lst) == 2 and bishop_lst[0][0] != bishop_lst[1][0] and bishop_lst[0][1] == bishop_lst[1][1])):
                end_game_insufficient = True

        if end_game_insufficient is True:
            chess_label.config(text="DRAW (insufficient material).")
            write_notation_end_game(1)
            move_restrict = True

        # threefold_repetition
        if add_repetition() is True:
            chess_label.config(text="DRAW (threefold repetition).")
            write_notation_end_game(1)
            move_restrict = True

        # fifty_move rule
        if current_color == 0:
            fifty_cnt += 1
            if fifty_cnt == 50:
                chess_label.config(text="DRAW (fifty-move rule).")
                write_notation_end_game(1)
                move_restrict = True

    # print(threefold_repetition_position_lst)


def return_cell_cord(row: int, col: int):
    global current_color, st_cord, display_chess_cells, move_restrict, in_check, allowed_moves_lst, colored_cells, theme_color, just_moved_cells

    if move_restrict is True:
        return

    current_piece = class_board[row][col]

    # Check if the move is possible
    ed_cord = (row, col)
    if (current_piece == place_holder or current_piece.color != current_color) and st_cord != (-1, -1):
        if (st_cord, ed_cord) in allowed_moves_lst:
            movePiece = class_board[st_cord[0]][st_cord[1]]

            movePiece.move(ed_cord)

            if len(just_moved_cells):
                config_cell_color(just_moved_cells[0])
                config_cell_color(just_moved_cells[1])
            just_moved_cells = [st_cord, ed_cord]

            turn_change()

        config_cell_color(st_cord)
        remove_colored_cells()
        if len(just_moved_cells) > 0:
            config_cell_color(just_moved_cells[0], 6)
            config_cell_color(just_moved_cells[1], 6)

        st_cord = (-1, -1)



    # Choose the intial piece to move
    elif current_piece != place_holder and current_piece.color == current_color:
        if st_cord != (-1, -1):
            config_cell_color(st_cord)

            remove_colored_cells()

            if len(just_moved_cells) > 0:
                config_cell_color(just_moved_cells[0], 6)
                config_cell_color(just_moved_cells[1], 6)

        st_cord = (row, col)

        config_cell_color(st_cord, 2)

        color_move_cells(st_cord)


def write_notation_castle(type_castle: int):
    global notation_cnt, current_color
    notation_txt: str = " 0-0"
    if type_castle == 1:
        notation_txt += "-0"

    if current_color == 0:
        notation_listbox.insert(notation_cnt, f"{notation_cnt - 1}." + notation_txt)
    else:
        notation_txt = notation_listbox.get(notation_cnt) + notation_txt
        notation_listbox.delete(notation_cnt)
        notation_listbox.insert(notation_cnt, notation_txt)
        notation_cnt += 1


def write_notation_promote(pieceName: str):
    global current_color
    index = notation_cnt - current_color
    notation_txt = notation_listbox.get(index)

    notation_txt = notation_txt + "=" + pieceName

    notation_listbox.delete(index)
    notation_listbox.insert(index, notation_txt)



def write_notation(st_cord: tuple[int, int], ed_cord: tuple[int, int], pieceName: str, *args) -> None:
    # args == (1) for en passant move
    global notation_cnt, abbrev_piece_name, current_color, allowed_moves_lst, notation_listbox

    notation_txt: str = f" {abbrev_piece_name[pieceName]}"

    if pieceName != "Pawn":
        # chk_lst: list = []
        #
        # if pieceName == "Rook":
        #     for ud, lr in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        #         row, col = ed_cord
        #         while 0 <= row + ud < 8 and 0 <= col + lr < 8:
        #             row += ud
        #             col += lr
        #             current_piece = get_piece((row, col))
        #             if current_piece != place_holder:
        #                 if current_piece.name == pieceName and current_piece.color == current_color:
        #                     chk_lst.append((row, col))
        #                 break
        #
        # elif pieceName == "Knight":
        #     for ud, lr in ((1, 2), (-1, 2), (1, -2), (-1, -2)):
        #         row, col = ed_cord
        #         for x, y in ((ud, lr), (lr, ud)):
        #             row += x
        #             col += y
        #             if 0 <= row < 8 and 0 <= col < 8:
        #                 current_cell = get_piece((row, col))
        #                 if current_cell != place_holder and current_cell.name == pieceName and current_cell.color == current_color:
        #                     chk_lst.append((row, col))
        #
        # elif pieceName == "Bishop":
        #     for ud in (-1, 1):
        #         for lr in (-1, 1):
        #             row, col = ed_cord
        #             while 0 <= row + ud < 8 and 0 <= col + lr < 8:
        #                 row += ud
        #                 col += lr
        #                 current_piece = get_piece((row, col))
        #                 if current_piece != place_holder:
        #                     if current_piece.name == pieceName and current_piece.color == current_color:
        #                         chk_lst.append((row, col))
        #                     break
        #
        # elif pieceName == "Queen":
        #     for ud, lr in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        #         row, col = ed_cord
        #         while 0 <= row + ud < 8 and 0 <= col + lr < 8:
        #             row += ud
        #             col += lr
        #             current_piece = get_piece((row, col))
        #             if current_piece != place_holder:
        #                 if current_piece.name == pieceName and current_piece.color == current_color:
        #                     chk_lst.append((row, col))
        #                 break
        #
        #     for ud in (-1, 1):
        #         for lr in (-1, 1):
        #             row, col = ed_cord
        #             while 0 <= row + ud < 8 and 0 <= col + lr < 8:
        #                 row += ud
        #                 col += lr
        #                 current_piece = get_piece((row, col))
        #                 if current_piece != place_holder:
        #                     if current_piece.name == pieceName and current_piece.color == current_color:
        #                         chk_lst.append((row, col))
        #                     break
        #
        # if len(chk_lst) >= 2:
        #     chk_file: int = 0
        #     chk_rank: int = 0
        #
        #     for chk in chk_lst:
        #         if chk[0] == st_cord[0]:
        #             chk_rank += 1
        #         if chk[1] == st_cord[1]:
        #             chk_file += 1

        chk_cnt: int = 0
        chk_file: int = 0
        chk_rank: int = 0

        for moves in allowed_moves_lst:
            if moves[1] == ed_cord and get_piece(moves[0]).name == pieceName:
                chk_cnt += 1
                if moves[0][0] == st_cord[0]:
                    chk_rank += 1
                if moves[0][1] == st_cord[1]:
                    chk_file += 1
        if chk_cnt >= 2:
            if chk_file > 1 and chk_rank > 1:
                notation_txt += convert_coordinate(st_cord)

            elif chk_file == 1:
                notation_txt += convert_coordinate(st_cord)[0]

            else:
                notation_txt += convert_coordinate(st_cord)[1]

    else:
        if st_cord[1] != ed_cord[1]:
            direction: int = ed_cord[1] - st_cord[1]
            if 0 <= ed_cord[1] + direction < 8:
                current_cell = get_piece((st_cord[0], ed_cord[1] + direction))

                if current_cell != place_holder and current_cell.name == "Pawn" and current_cell.color == current_color:
                    notation_txt += convert_coordinate(st_cord)[0]

            if args != () and args[0] == 1:
                # If there is a Pawn beneath the en passant Pawn
                check_cell = get_piece((st_cord[0] - 2 * current_color + 1, st_cord[1]))
                if check_cell != place_holder and check_cell.name == "Pawn" and check_cell.color == current_color:
                    notation_txt += str(5 - current_color)

            elif st_cord[0] == 4 - current_color:
                # If there is a Pawn which can en passant above the Pawn
                check_cell = get_piece((st_cord[0] + 2 * current_color - 1, st_cord[1]))
                if check_cell != place_holder and check_cell.name == "Pawn" and check_cell.color == current_color and check_cell.en_passant == direction:
                    notation_txt += convert_coordinate(st_cord)[1]

    if args == ():
        if get_piece(ed_cord) != place_holder:
            notation_txt += f"x{convert_coordinate(ed_cord)}"
        else:
            notation_txt += f"{convert_coordinate(ed_cord)}"
    elif args[0] == 1:
        notation_txt += f"x{convert_coordinate((ed_cord[0] - 2 * current_color + 1, ed_cord[1]))}"

    if current_color == 0:
        notation_listbox.insert(notation_cnt, f"{notation_cnt - 1}." + notation_txt)
    else:
        notation_txt = notation_listbox.get(notation_cnt) + notation_txt
        notation_listbox.delete(notation_cnt)
        notation_listbox.insert(notation_cnt, notation_txt)
        notation_cnt += 1


def write_notation_for_check(*args):
    global current_color
    index = notation_cnt + current_color - 1
    notation_txt = notation_listbox.get(index)

    if args == ():
        notation_txt += "+"

    else:
        notation_txt = notation_txt[:-1] + "#"

    notation_listbox.delete(index)
    notation_listbox.insert(index, notation_txt)


def write_notation_end_game(case: int):
    # case = 0: current color won
    # case = 1: draw
    global current_color, notation_cnt
    if current_color == 1:
        notation_cnt += 1

    if case == 0:
        if current_color == 1:
            notation_listbox.insert(notation_cnt, "1-0")
        else:
            notation_listbox.insert(notation_cnt, "0-1")
    else:
        notation_listbox.insert(notation_cnt, "1/2-1/2")


def promote_display() -> str:
    global current_color
    rt_piece: str = "Queen"

    def return_queen():
        nonlocal rt_piece
        rt_piece = "Queen"
        promote_window.destroy()

    def return_rook():
        nonlocal rt_piece
        rt_piece = "Rook"
        promote_window.destroy()

    def return_bishop():
        nonlocal rt_piece
        rt_piece = "Bishop"
        promote_window.destroy()

    def return_knight():
        nonlocal rt_piece
        rt_piece = "Knight"
        promote_window.destroy()

    promote_window = tkinter.Toplevel()
    promote_window.grab_set()

    promote_frame = tkinter.Frame(promote_window)


    queen_button = tkinter.Button(promote_frame, text=piece_symbol[current_color]["Queen"], font=("Inherit", 20), command=return_queen)
    rook_button = tkinter.Button(promote_frame, text=piece_symbol[current_color]["Rook"], font=("Inherit", 20), command=return_rook)
    bishop_button = tkinter.Button(promote_frame, text=piece_symbol[current_color]["Bishop"], font=("Inherit", 20), command=return_bishop)
    knight_button = tkinter.Button(promote_frame, text=piece_symbol[current_color]["Knight"], font=("Inherit", 20), command=return_knight)

    queen_button.grid(row=0, column=0)
    rook_button.grid(row=0, column=1)
    bishop_button.grid(row=0, column=2)
    knight_button.grid(row=0, column=3)

    promote_frame.pack()
    promote_window.wait_window()

    return rt_piece


def config_piece(pos, text):
    global display_chess_cells, theme_color
    display_chess_cells[pos[0]][pos[1]].config(text=text
                                               )


def config_cell_color(pos: tuple, *args):
    global theme_color, display_chess_cells
    color_idx: int = (pos[0] + pos[1]) % 2 if args == () else args[0]

    display_chess_cells[pos[0]][pos[1]].config(bg=bg_color[theme_color][color_idx])


def change_theme(chosen_theme) -> None:
    global theme_color, st_cord, colored_cells, in_check, king_lst, current_color, just_moved_cells
    if theme_color != chosen_theme:
        theme_color = chosen_theme

    for rank in range(8):
        for file in range(8):
            display_chess_cells[rank][file].config(bg=bg_color[theme_color][(rank + file) % 2],
                                                   activebackground=bg_color[theme_color][(rank + file) % 2],
                                                   fg=bg_color[theme_color][5])

    if st_cord != (-1, -1):
        config_cell_color(st_cord, 2)

        for cord in colored_cells:
            config_cell_color(cord, 3)

    if in_check is True:
        king_pos = king_lst[current_color].position
        config_cell_color(king_pos, 4)

    if len(just_moved_cells) > 0:
        config_cell_color(just_moved_cells[0], 6)
        config_cell_color(just_moved_cells[1], 6)


def config_taken_piece_frame(color):
    global point_config, taken_piece_config, taken_piece_icons

    piece_txt = ""
    for index in range(5):
        piece_txt += piece_symbol[color][taken_piece_icons[index]] * taken_piece_config[color][index]

    if color == 0:
        piece_label_fst.config(text=piece_txt)
    else:
        piece_label_snd.config(text=piece_txt)

    config_point_frame()


def config_point_frame():
    if point_config[0] == point_config[1]:
        point_label_fst.config(text="")
        point_label_snd.config(text="")
    elif point_config[0] > point_config[1]:
        point_label_fst.config(text=f"+{point_config[0] - point_config[1]}")
        point_label_snd.config(text="")
    else:
        point_label_fst.config(text="")
        point_label_snd.config(text=f"+{point_config[1] - point_config[0]}")


def save_notation_command():
    global notation_listbox4
    with open("Chess Notation", "w") as wf:
        wf.flush()
        for index in range(2, notation_listbox.index("end")):
            wf.write(notation_listbox.get(index))
            wf.write("\n")


def load_notation_command():
    global abbrev_to_name

    def notation_move(notation: str):
        global current_color, class_board
        if notation[-1] == "+" or notation[-1] == "#":
            notation = notation[:-1]

        # castle
        elif notation[0] == "0":
            if current_color == 0:
                current_cell = class_board[7][4]
            else:
                current_cell = class_board[0][4]

            if notation == "0-0":
                if current_color == 0:
                    current_cell.move(convert_position("g1"))
                else:
                    current_cell.move(convert_position("g8"))
            else:
                if current_color == 0:
                    current_cell.move(convert_position("c1"))
                else:
                    current_cell.move(convert_position("c8"))
            return

        #pawn move
        elif notation[0].islower() is True:
            # promotion
            if notation[-2] == "=":
                pass
            elif 'x' in notation:
                ed_pos: tuple[int, int] = convert_position(notation[-2:])
                st_pos: list[int, int] = [-1, -1]
                if notation[0] != 'x':
                    if notation[0].isalpha():
                        st_pos[1] = convert_file_to_pos(notation[0])
                        if notation[1] != 'x':
                            st_pos[0] = convert_pos_and_rank(int(notation[1]))
                        else:
                            if current_color == 0:
                                st_pos[0] = ed_pos[0] + 1
                            else:
                                st_pos[0] = ed_pos[0] - 1
                    else:
                        st_pos[0] = convert_pos_and_rank(int(notation[0]))
                else:
                    if current_color == 0:
                        if ed_pos[1] - 1 >= 0:
                            left_cell = class_board[ed_pos[0] + 1][ed_pos[1] - 1]
                            if left_cell != place_holder and left_cell.name == "Pawn" and left_cell.color == current_color:
                                st_pos[0] = ed_pos[0] + 1
                                st_pos[1] = ed_pos[1] - 1
                        if ed_pos[1] + 1 < 8:
                            right_cell = class_board[ed_pos[0] + 1][ed_pos[1] + 1]
                            if right_cell != place_holder and right_cell.name == "Pawn" and left_cell.color == current_color:
                                st_pos[0] = ed_pos[0] + 1
                                st_pos[0] = ed_pos[1] + 1
                    else:
                        st_pos[0] = ed_pos[0] - 1
                        if ed_pos[1] - 1 >= 0:
                            left_cell = class_board[ed_pos[0] - 1][ed_pos[1] - 1]
                            if left_cell != place_holder and left_cell.name == "Pawn" and left_cell.color == current_color:
                                st_pos[1] = ed_pos[1] - 1
                        if ed_pos[1] + 1 < 8:
                            right_cell = class_board[ed_pos[0] - 1][ed_pos[1] + 1]
                            if right_cell != place_holder and right_cell.name == "Pawn" and left_cell.color == current_color:
                                st_pos[0] = ed_pos[1] + 1
                current_cell = class_board[st_pos[0]][st_pos[1]]
                current_cell.move(ed_pos)
            else:
                ed_cord: tuple[int, int] = convert_position(notation[-2:])
                if current_color == 0:
                    for rank in range(ed_cord[0], 8, 1):
                        current_cell = class_board[rank][ed_cord[1]]
                        if current_cell != place_holder and current_cell.name == "Pawn" and current_cell.color == current_color:
                            current_cell.move(ed_cord)
                            break
                else:
                    for rank in range(ed_cord[0], -1, -1):
                        current_cell = class_board[rank][ed_cord[1]]
                        if current_cell != place_holder and current_cell.name == "Pawn" and current_cell.color == current_color:
                            current_cell.move(ed_cord)
                            break
            return




        else:
            ed_cord: tuple = convert_position(notation[-2:])
            pieceName: str = abbrev_to_name[notation[0]]
            for rank in range(8):
                for file in range(8):
                    current_cell = class_board[rank][file]
                    if current_cell != place_holder and current_cell.name == pieceName and ed_cord in current_cell.possible_move():
                        current_cell.move(ed_cord)


    restart_game()
    with open("Chess_Notation", "r") as notation_file:
        for line in notation_file:
            line_content = list(line.split())
            if len(line_content) >= 2:
                notation_move(line_content[1])
                turn_change()
                window.update()
                time.sleep(1)
            if len(line_content) > 2:
                notation_move(line_content[2])
                turn_change()
                window.update()
                time.sleep(1)


def reverse_display_board():
    pass


if __name__ == "__main__":
    window = tkinter.Tk()
    window.title("Chezz.cum")

    window.columnconfigure(0, weight=10)
    window.columnconfigure(1, weight=50)
    window.columnconfigure(2, weight=10)
    window.rowconfigure(0, weight=10)
    window.rowconfigure(1, weight=10)
    window.rowconfigure(2, weight=50)
    window.rowconfigure(3, weight=10)
    window.rowconfigure(4, weight=10)

    menubar = tkinter.Menu(window)
    window.config(menu=menubar)

    fileMenu = tkinter.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=fileMenu)
    fileMenu.add_command(label="Save Notation", command=save_notation_command)
    fileMenu.add_separator()
    fileMenu.add_command(label="Close")

    openMenu = tkinter.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Open", menu=openMenu)
    openMenu.add_command(label="Load Notation", command=load_notation_command)

    chess_label = tkinter.Label(window, text="CHESS", font=("Garamond", 30))
    board_frame = tkinter.Frame(window)
    notation_listbox = tkinter.Listbox(window)

    board_frame.rowconfigure((0, 9), weight=5)
    board_frame.columnconfigure((0, 9), weight=5)

    # file - rank
    index_color: list[str] = ["#E5E4E2", "#D3D3D3"]
    for row in (0, 9):
        for col in (0, 9):
            tkinter.Label(board_frame, bg="#C0C0C0").grid(row=row, column=col, sticky='nsew')
    for index in range(1, 9):
        tkinter.Label(board_frame, text=chr(96 + index), font=("Inherit", 15), bg=index_color[index % 2], height=1).grid(row=0, column=index, sticky='nsew')
        tkinter.Label(board_frame, text=chr(96 + index), font=("Inherit", 15), bg=index_color[(index + 1) % 2], height=1).grid(row=9, column=index, sticky='nsew')

        tkinter.Label(board_frame, text=str(index), font=("Inherit", 15), bg=index_color[index % 2], width=2).grid(row=9-index, column=0, sticky='nsew')
        tkinter.Label(board_frame, text=str(index), font=("Inherit", 15), bg=index_color[(index + 1) % 2], width=2).grid(row=9-index, column=9, sticky='nsew')

    for row in range(8):
        for col in range(8):

            current_cell = class_board[row][col]
            cell_text: str

            if current_cell == place_holder:
                cell_text = ""
            else:
                cell_text = piece_symbol[current_cell.color][current_cell.name]

            display_chess_cells[row][col] = tkinter.Button(board_frame, text=cell_text, font=("Inherit", 35),
                                                           bg=bg_color[theme_color][(row + col) % 2],
                                                           activebackground=bg_color[theme_color][(row + col) % 2],
                                                           fg=bg_color[theme_color][5],
                                                           command=lambda r=row, c=col: return_cell_cord(r, c))
            display_chess_cells[row][col].grid(row=row + 1, column=col + 1, sticky="nsew")

    theme_frame = tkinter.Frame(window)

    theme_label = tkinter.Label(theme_frame, text="THEME COLOR", font=("Inherit", 20, "bold"))
    theme_label.pack()

    theme_var = tkinter.IntVar()

    taken_frame_color: str = "#DCDCDC"

    taken_piece_frame_fst = tkinter.Frame(window, height=30, bg=taken_frame_color)
    taken_piece_frame_snd = tkinter.Frame(window, height=30, bg=taken_frame_color)

    piece_label_fst = tkinter.Label(taken_piece_frame_fst, font=("Inherit", 20), bg=taken_frame_color)
    piece_label_snd = tkinter.Label(taken_piece_frame_snd, font=("Inherit", 20), bg=taken_frame_color)

    point_label_fst = tkinter.Label(taken_piece_frame_fst, font=("Inherit", 15), bg=taken_frame_color)
    point_label_snd = tkinter.Label(taken_piece_frame_snd, font=("Inherit", 14), bg=taken_frame_color)

    for index in range(len(bg_color)):
        tkinter.Radiobutton(theme_frame,
                            text=bg_color_name[index],
                            font=("Inherit", 15),
                            variable=theme_var,
                            value=index,
                            padx=25,
                            compound="left",
                            command=lambda chosen_theme=index: change_theme(chosen_theme)
                            ).pack(anchor=tkinter.W)

    function_frame = tkinter.Frame(window, bg="cyan")
    restart_button = tkinter.Button(function_frame, text="Restart", font=("Inherit", 15),
                                    # bg="#808080", activebackground="#808080",
                                    command=restart_game)

    reverse_button = tkinter.Button(function_frame, text="Resverse", font=("Inherit", 15),
                                    # bg="#808080", activebackground="#808080",
                                    command=reverse_display_board)

    standard_pieces_generate()
    # test_pieces_generate()
    turn_change()

    notation_listbox.insert(0, "")
    notation_listbox.insert(1, "")



    function_frame.grid(row=4, column=0, columnspan=3)
    reverse_button.pack(side=tkinter.RIGHT)
    restart_button.pack(side=tkinter.RIGHT)

    piece_label_fst.pack(side=tkinter.RIGHT)
    piece_label_snd.pack(side=tkinter.RIGHT)

    point_label_fst.pack(side=tkinter.RIGHT)
    point_label_snd.pack(side=tkinter.RIGHT)

    theme_frame.grid(row=1, column=0, rowspan=3, sticky='nsew')

    taken_piece_frame_fst.grid(row=1, column=1, sticky='nsew')
    taken_piece_frame_snd.grid(row=3, column=1, sticky='nsew')

    chess_label.grid(row=0, column=1)
    board_frame.grid(row=2, column=1)

    tkinter.Label(window, text="Notation", font=("Inherit", 15, "bold"), bg="white").grid(row=1, column=2)
    notation_listbox.grid(row=1, column=2, rowspan=2, sticky='nsew')
    window.mainloop()

    # [0,     title, 0]
    # [theme, point 1, notate title]
    # [theme, board, notation]
    # [theme, point 2, 0]
    # [func, func, func, restart]





