from random import randrange, randint
from termcolor import colored, cprint

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за границами поля!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Повторный выстрел"

class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

class Ship:
    def __init__(self, ship_length, bow_of_the_ship, ship_direction):
        self.ship_length = ship_length
        self.bow_of_the_ship = bow_of_the_ship
        self.ship_direction = ship_direction
        self.number_of_lives = ship_length

    @property
    def dots(self):
        coordinate_points = []
        for i in range(self.ship_length):
            new_x = self.bow_of_the_ship.x
            new_y = self.bow_of_the_ship.y
            if self.ship_direction == 0:
                new_x += i
            elif self.ship_direction == 1:
                new_y += i
            coordinate_points.append(Dot(new_x, new_y))
        return coordinate_points

    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid=False):
        self.cell_state = [['O' for i in range(6)] for i in range(6)]
        self.hid = hid
        self.ship_list = []
        self.occupied_cells = []
        self.number_of_live_ships = 0

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.occupied_cells:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.cell_state[d.x][d.y] = '■'
            self.occupied_cells.append(d)

        self.ship_list.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        pledge = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for d in ship.dots:
            for dx, dy in pledge:
                a = Dot(d.x + dx, d.y + dy)
                if not(self.out(a)) and a not in self.occupied_cells:
                    if verb:
                        self.cell_state[a.x][a.y] = '.'
                    self.occupied_cells.append(a)

    def __str__(self):
        field = ''
        field += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        field += ''.join([f"\n{i + 1} | " + " | ".join(row) + " |" for i, row in enumerate(self.cell_state)])
        if self.hid:
            field = field.replace("■", 'O')
        return field

    def out(self, d):
        return not ((0 <= d.x < 6) and (0 <= d.y < 6))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.occupied_cells:
            raise BoardUsedException

        self.occupied_cells.append(d)

        for ship in self.ship_list:
            if d in ship.dots:
                ship.number_of_lives -= 1
                self.cell_state[d.x][d.y] = colored('X', 'red')
                if ship.number_of_lives == 0:
                    self.number_of_live_ships += 1
                    self.contour(ship, verb=True)
                    print(colored('Корабль убит!', 'red'))
                    return False
                else:
                    print(colored("Корабль ранен!", 'grey'))
                    return True

        self.cell_state[d.x][d.y] = colored('.', 'yellow')
        print('Мимо!')
        return False

    def begin(self):
        self.occupied_cells = []

class Player:
    def __init__(self, board, board_enemy):
        self.board = board
        self.board_enemy = board_enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.board_enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randrange(6), randrange(6))
        print(f'Ход противника: {d.x+1} {d.y+1}')
        return d

class User(Player):
    def ask(self):
        while True:
            coordinates = input('Сделайте Ваш ход ').split()

            if len(coordinates) != 2:
                print('Введите 2 координаты!')
                continue

            x, y = coordinates

            if not(x.isdigit()) or not (y.isdigit()):
                print('Вы ввели не число!')
                continue

            return Dot(int(x)-1, int(y)-1)

class Game:
    def board_creation(self):
        length = [3, 2, 2, 1, 1, 1, 1]
        board = Board()
        count = 0
        for i in length:
            while True:
                count += 1
                if count > 1000:
                    return None
                ship = Ship(i, Dot(randrange(6), randrange(6)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass

        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.board_creation()
        return board

    def __init__(self):
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def greet(self):
        z = '*'*20
        print(f'{colored(z, "red")} Игра "Морской бой!!!" {colored(z, "red")}')
        print(colored(f'Формат ввода подразумевает введение сначала точки по оси абсцисс, потом по оси ординат.', "yellow"))

    def loop(self):
        n = 0
        while True:
            print(colored("Ваша доска:", 'magenta'))
            print(self.us.board)
            print(colored("Доска противника:", 'cyan'))
            print(self.ai.board)
            if n % 2 == 0:
                print(colored("Ваш ход!", 'magenta'))
                repeat = self.us.move()
            else:
                print("Ход противника")
                repeat = self.ai.move()
            if repeat:
                n -= 1

            if self.ai.board.number_of_live_ships == 7:
                print(colored("Вы выиграли!", 'yellow'))
                break

            if self.us.board.number_of_live_ships == 7:
                print(colored("Вы проиграли!", 'black'))
                break
            n += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()


