import random

class BoardOutException(Exception):
    pass


class CellOccupiedException(Exception):
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
    def __init__(self, length, bow, horizontal):
        self.length = length  #длина корабля
        self.bow = bow  #точка носа корабля (объект Dot)
        self.horizontal = horizontal  #True, если горизонтальный; False, если вертикальный
        self.health = length  #количество оставшегося здоровья

    def dots(self):
        ship_dots = []  #список для точек корабля
        for i in range(self.length):
            if self.horizontal:  #горизонтальный корабль
                ship_dots.append(Dot(self.bow.x, self.bow.y + i))
            else:  #вертикальный корабль
                ship_dots.append(Dot(self.bow.x + i, self.bow.y))
        return ship_dots


class Board:
    def __init__(self, size=6, hid=False):
        self.size = size  #размер доски
        self.board = [['O'] * size for _ in range(size)]  #создание доски (6x6 клеток)
        self.ships = []  #список кораблей на доске
        self.hid = hid  #скрывать корабли или нет
        self.alive_ships = 0  #количество живых кораблей

    def __str__(self):
        board_str = "  | 1 | 2 | 3 | 4 | 5 | 6 |\n"
        for i, row in enumerate(self.board):
            board_str += f"{i + 1} |" + " | ".join(row) + " |\n"
        return board_str

    def out(self, dot):
        return not (0 <= dot.x < self.size and 0 <= dot.y < self.size) #проверка, выходит ли точка за пределы доски

    def contour(self, ship):
        contour_cells = []  #список для хранения клеток контура
        offsets = [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),           (0, 1),
                   (1, -1), (1, 0), (1, 1)]

        #для каждой точки корабля проверяем клетки вокруг
        for dot in ship.dots():
            for dx, dy in offsets:
                adj_dot = Dot(dot.x + dx, dot.y + dy)
                if not self.out(adj_dot) and self.board[adj_dot.x][adj_dot.y] == 'O':  #если клетка в пределах доски и свободна
                    contour_cells.append(adj_dot)

        return contour_cells

    def add_ship(self, ship):
        #проверяем, можно ли разместить корабль
        for dot in ship.dots():
            if self.out(dot):
                raise ValueError("Корабль выходит за пределы доски")
            if self.board[dot.x][dot.y] != 'O':
                raise ValueError("На этой клетке уже есть корабль")

        #получаем клетки контура и помечаем их как занятые
        contour_cells = self.contour(ship)
        for cell in contour_cells:
            self.board[cell.x][cell.y] = "~"  #обозначаем клетки вокруг как запрещенные для кораблей

        #размещаем сам корабль на доске
        for dot in ship.dots():
            self.board[dot.x][dot.y] = '■'

        #добавляем корабль в список
        self.ships.append(ship)
        self.alive_ships += 1

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException("Выстрел за пределы доски")
        if self.board[dot.x][dot.y] in ['X', 'T']:
            raise CellOccupiedException("В эту клетку уже стрелялось")

        #если в клетке есть корабль, помечаем его как подбитый
        for ship in self.ships:
            if dot in ship.dots():
                ship.health -= 1  #уменьшаем здоровье корабля
                self.board[dot.x][dot.y] = 'X'  #помечаем как подбитый
                if ship.health == 0:  #если у корабля не осталось здоровья
                    self.alive_ships -= 1  #уменьшаем количество живых кораблей
                return "Попал!"

        #если в клетке нет корабля, помечаем клетку как промах
        self.board[dot.x][dot.y] = 'T'
        return "Промах!"

    def print_board(self):
        print("  | 1 | 2 | 3 | 4 | 5 | 6 |")
        for i, row in enumerate(self.board):
            print(f"{i + 1} |", end=" ")
            for cell in row:
                if self.hid:
                    #если нужно скрывать корабли и их контуры
                    if cell == '■' or cell == '~':  #заменяем все, что связано с кораблями и их контурами
                        print('О', end=" | ")  #печатаем как пустую клетку
                    else:
                        print(cell, end=" | ")
                else:
                    print(cell, end=" | ")
            print()


class Player:
    def __init__(self, board, enemy_board):
        self.board = board  #собственная доска игрока
        self.enemy_board = enemy_board  #доска противника

    def ask(self):
        raise NotImplementedError()

    def move(self):
        try:
            target = self.ask()  #получаем точку для выстрела
            result = self.enemy_board.shot(target)  #делаем выстрел по доске противника
            print(result)
            return result == "Попал!"
        except BoardOutException as e:
            print(e)
        except CellOccupiedException as e:
            print(e)
        return False


class User(Player):
    def ask(self):
        while True:
            try:
                x, y = map(int, input("Введите координаты выстрела (через пробел): ").split())
                return Dot(x - 1, y - 1)  #преобразуем координаты в индекс массива
            except ValueError:
                print("Введите два числа через пробел!")


class AI(Player):
    def ask(self):
        dot = Dot(random.randint(0, self.enemy_board.size - 1),
                  random.randint(0, self.enemy_board.size - 1))
        print(f"Компьютер стреляет в: {dot.x + 1} {dot.y + 1}")
        return dot

class Game:
    def __init__(self, size=6):
        self.size = size
        self.user_board = self.random_board()
        self.ai_board = self.random_board(hid=True)
        if not self.user_board or not self.ai_board:
            print("Не удалось создать доски для игры.")
            exit()
        self.user = User(self.user_board, self.ai_board)
        self.ai = AI(self.ai_board, self.user_board)

    def random_board(self, hid=False):
        board = Board(size=self.size, hid=hid)
        attempts = 0
        for length in [3, 2, 2, 1, 1, 1, 1]:  #устанавливаем корабли разных размеров
            while True:
                attempts += 1
                if attempts > 4000:  #ограничение попыток
                    print(f"Не удалось разместить все корабли за {attempts} попыток.")
                    return None  #если не удалось разместить, возвращаем None
                ship = Ship(length, Dot(random.randint(0, self.size - 1),
                                        random.randint(0, self.size - 1)),
                            random.choice([True, False]))  #выбор горизонтального или вертикального корабля
                try:
                    board.add_ship(ship)  #пробуем добавить корабль на доску
                    break  #если все хорошо, выходим из цикла
                except ValueError:  #если корабль не помещается, пробуем снова
                    pass
        return board  #если доска создана успешно, возвращаем ее



    def greet(self):
        print("-------------------")
        print("  Добро пожаловать  ")
        print("      в игру        ")
        print("   Морской бой!     ")
        print("-------------------")
        print(" Формат ввода: x y ")
        print(" x - номер строки   ")
        print(" y - номер столбца  ")

    def loop(self):
        turn = 0
        while True:
            print("-" * 20)
            print("Доска игрока:")
            self.user_board.print_board()  #показываем доску игрока
            print("Доска компьютера:")
            self.ai_board.print_board()  #показываем доску компьютера
            if turn % 2 == 0:
                print("Ходит игрок!")
                repeat = self.user.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                turn -= 1
            if self.ai_board.alive_ships == 0:
                print("Игрок победил!")
                break
            if self.user_board.alive_ships == 0:
                print("Компьютер победил!")
                break
            turn += 1

    def start(self):
        self.greet()
        self.loop()


if __name__ == "__main__":
    game = Game()
    game.start()

