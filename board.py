class Board(object):
    def __init__(self) -> None:
        # Create a 8x8 board
        self.empty = '.'
        self._board = [[self.empty for _ in range(8)] for _ in range(8)]
        self._board[3][4], self._board[4][3] = 'X', 'X' # black
        self._board[3][3], self._board[4][4] = 'O', 'O' # white

    def __getitem__(self, index):
        return self._board[index]
    
    def get_board(self):
        return self._board
    
    def display(self, step_time=None, total_time=None):
        board = self._board

        print(' ', ' '.join(list('ABCDEFGH')))
        for i in range(8):
            print(str(i + 1), ' '.join(board[i]))
        
        if (not step_time) or (not total_time):
            step_time = {'X': 0, 'O': 0}
            total_time = {'X': 0, 'O': 0}
        print("Game statistics: total number\ttime/move\ttotal time")
        count = self.count()
        print("Black pieces: \t" + str(count['X']) + ' \t ' + 
              str(step_time['X']) + ' \t ' + str(total_time['X']))
        print("White pieces: \t" + str(count['O']) + ' \t ' + 
              str(step_time['O']) + ' \t ' + str(total_time['O']) + '\n')
    
    def count(self):
        count_X = 0
        count_O = 0
        for x in range(8):
            for y in range(8):
                if self._board[x][y] == 'X':
                    count_X += 1
                elif self._board[x][y] == 'O':
                    count_O += 1

        return {'X': count_X, 'O': count_O}

    def get_winner(self):
        count = self.count()
        black_count, white_count = count['X'], count['O']

        if black_count > white_count:
            # black wins
            return 0, black_count - white_count
        elif white_count > black_count:
            # white wins
            return 1, white_count - black_count
        else:
            # draw
            return 2, 0

    def move(self, action, color):

        if isinstance(action, str):
            action = self._board2num(action=action)
        
        reversed = self._can_reverse(action, color)
        if reversed:
            # Reverse the opponent's chess pieces
            for coord in reversed:
                x, y = coord
                self._board[x][y] = color
            x, y = action
            self._board[x][y] = color   
        return reversed
    
    def _can_reverse(self, action, color):
        if isinstance(action, str):
            action = self._board2num(action=action)
        x_, y_ = action

        if not self._is_on_board(x_, y_) or self._board[x_][y_] != self.empty:
            return False
        
        self._board[x_][y_] = color
        op_color = self._op_color(color)

        reversed_pos = []
        for x_direction, y_direction in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
            x, y = x_ + x_direction, y_ + y_direction
            if self._is_on_board(x,y) and self._board[x][y] == op_color:
                while self._board[x][y] == op_color:
                    x += x_direction
                    y += y_direction
                    if not self._is_on_board(x, y):
                        break
                if not self._is_on_board(x, y):
                    continue

                if self._board[x][y] == color:
                    while True:
                        x -= x_direction
                        y -= y_direction
                        if x == x_ and y == y_:
                            break
                        reversed_pos.append([x, y])
        
        self._board[x_][y_] = self.empty

        return False if len(reversed_pos) == 0 else reversed_pos

    def backpropagation(self, action, reversed_pos, color):
        if isinstance(action, str):
            action = self._board2num(action=action)
        x, y = action
        self._board[x][y] = self.empty
        op_color = self._op_color(color)

        for coor in reversed_pos:
            if isinstance(coor, str):
                coor = self._board2num(coor)
            x, y = coor
            self._board[x][y] = op_color
    
    def get_legal_actions(self, color):
        op_color = self._op_color(color)
        op_color_near_coords = []
        board = self._board
        for x in range(8):
            for y in range(8):
                if board[x][y] == op_color:
                    for x_direction, y_direction in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
                        x_prime, y_prime = x+x_direction, y+y_direction
                        if self._is_on_board(x_prime, y_prime) and board[x_prime][y_prime] == self.empty and \
                            [x_prime, y_prime] not in op_color_near_coords:
                            op_color_near_coords.append([x_prime, y_prime])
        
        legal_actions = []
        for pos in op_color_near_coords:
            if self._can_reverse(pos, color):
                action = self._nun2board(pos)
                legal_actions.append(action)
        return legal_actions
    
    def _board2num(self, action):
        row, col = str(action[1]), str(action[0]).upper()
        return '12345678'.index(row), 'ABCDEFGH'.index(col)
    
    def _nun2board(self, action):
        row, col = action
        return chr(ord('A') + col) + str(row + 1)
    
    def _is_on_board(self, x, y):
        return x >= 0 and x <= 7 and y >=0 and y <= 7
    
    def _op_color(self, color):
        return 'O' if color == 'X' else 'X'
    

# Test
if __name__ == '__main__':
    board = Board()  # Init board
    board.display()
    print("----------------------------------X",list(board.get_legal_actions('X')))
    print("==========",'F1' in list(board.get_legal_actions('X')))