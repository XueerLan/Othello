import pygame
import sys
import traceback
import copy
import random

# 棋盘大小
BOARD_SIZE = 8
# 棋盘格子大小
CELL_SIZE = 100
# 颜色定义（黑棋和白棋）
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# 创建一个二维数组代表棋盘，初始值都是0，表示棋盘上的这个位置没有棋子
# 对于数组board，board[i][j] == 0 表示空格，board[i][j] == 1 表示黑子，board[i][j] == -1 表示白子
board = [[0] * 8 for i in range(8)]

# 设置初始的四颗棋子的位置
board[3][3] = board[4][4] = -1  # 白棋
board[3][4] = board[4][3] = 1  # 黑棋

PIECE_RADIUS = CELL_SIZE // 2 - 5

#画棋盘
def draw_board(screen, board, current_player):
    for row in range(BOARD_SIZE):
        for column in range(BOARD_SIZE):
            pygame.draw.rect(screen, WHITE, pygame.Rect(column*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            if board[row][column] == -1:  # 如果该位置是白棋
                pygame.draw.circle(screen, WHITE, ((column * CELL_SIZE) + (CELL_SIZE // 2),
                                                   (row * CELL_SIZE) + (CELL_SIZE // 2)), CELL_SIZE // 2 - 5)
            elif board[row][column] == 1:  # 如果该位置是黑棋
                pygame.draw.circle(screen, BLACK, ((column * CELL_SIZE) + (CELL_SIZE // 2),
                                                   (row * CELL_SIZE) + (CELL_SIZE // 2)), CELL_SIZE // 2 - 5)
            elif current_player == 1:  # 只在玩家的回合显示合法落子的位置
                if is_valid_move(board, row, column, current_player):
                    pygame.draw.circle(screen, GREEN,
                                       (column * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2),
                                       PIECE_RADIUS // 2)



#判断是否有合法的落子
def is_valid_move(board, x, y, color):
    # 判断落子点是否在棋盘内
    if x < 0 or x > 7 or y < 0 or y > 7:
        return False
    if board[x][y] != 0:
        return False
    # 判断是否可以翻转对方的棋子
    for d in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
        nx, ny = x + d[0], y + d[1]
        if nx < 0 or nx > 7 or ny < 0 or ny > 7 or board[nx][ny] != -color:
            continue
        while 0 <= nx < 8 and 0 <= ny < 8:
            if board[nx][ny] == color:
                return True
            if board[nx][ny] == 0:
                break
            nx += d[0]
            ny += d[1]
    return False



#翻转相应的棋子
def flip(board, x, y, color):
    board[x][y] = color
    for d in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
        nx, ny = x + d[0], y + d[1]
        if nx < 0 or nx > 7 or ny < 0 or ny > 7 or board[nx][ny] != -color:
            continue
        nx += d[0]
        ny += d[1]
        while 0 <= nx < 8 and 0 <= ny < 8:
            if board[nx][ny] == color:
                nx, ny = x + d[0], y + d[1]
                while board[nx][ny] == -color:
                    board[nx][ny] = color
                    nx += d[0]
                    ny += d[1]
                break
            if board[nx][ny] == 0:
                break
            nx += d[0]
            ny += d[1]



#处理事件（鼠标点击 + 关闭窗口）
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            row, col = y // CELL_SIZE, x // CELL_SIZE
            return (row, col)
    return False



def has_valid_move(board, color):
    for i in range(8):
        for j in range(8):
            if is_valid_move(board, i, j, color):
                return True
    return False



#检查游戏是否结束
def game_over(board):
    if not has_valid_move(board, -1) and not has_valid_move(board, 1):
        return True
    for row in board:
        for cell in row:
            if cell == 0:
                return False
    return True



#统计结果
def display_result(screen, board):
    white = 0
    black = 0
    for row in board:
        for cell in row:
            if cell == -1:  # -1 代表白棋
                white += 1
            elif cell == 1:  # 1 代表黑棋
                black += 1
    if white > black:
        result = 'White wins!'
    elif black > white:
        result = 'Black wins!'
    else:
        result = 'The game is a draw!'
    print(result)

    font = pygame.font.Font(None, 36)  # 创建字体对象
    text = font.render(result, True, (0, 0, 0))  # 渲染文本，参数是文本，抗锯齿和颜色

    # 创建一个矩形的表面，并将其填充为白色
    result_surface = pygame.Surface((300, 100))  # 300x100是矩形的尺寸，你可以根据需要调整
    result_surface.fill((255, 255, 255))  # 填充为白色

    # 把文本渲染到矩形表面的中心
    text_rect = text.get_rect()
    text_rect.center = result_surface.get_rect().center  # 文本的中心位置是矩形表面的中心
    result_surface.blit(text, text_rect)

    # 将矩形表面绘制到屏幕的中心
    surface_rect = result_surface.get_rect()
    surface_rect.center = screen.get_rect().center  # 矩形表面的中心位置是屏幕的中心
    screen.blit(result_surface, surface_rect)

    pygame.display.flip()  # 更新整个待显示的 Surface 对象到屏幕上



def evaluate(board, color):
    white_score, black_score = count_pieces(board)
    if color == -1:  # AI是白棋
        return white_score - black_score
    else:
        return black_score - white_score



def count_pieces(board):
    white_score = sum([row.count(-1) for row in board])
    black_score = sum([row.count(1) for row in board])
    return white_score, black_score



def minimax(board, depth, color):
    if depth == 0 or game_over(board):
        return evaluate(board, color), None
    if color == -1:  # AI (Maximizer)
        best_score = float('-inf')
        best_move = None
        for i in range(8):
            for j in range(8):
                if is_valid_move(board, i, j, color):
                    temp_board = copy.deepcopy(board)
                    flip(temp_board, i, j, color)
                    current_score, _ = minimax(temp_board, depth-1, -color)
                    if best_move is None:
                        best_move = (i, j)
                    if current_score > best_score:
                        best_score = current_score
                        best_move = (i, j)
        return best_score, best_move
    else:  # Player (Minimizer)
        best_score = float('inf')
        best_move = None
        for i in range(8):
            for j in range(8):
                if is_valid_move(board, i, j, color):
                    temp_board = copy.deepcopy(board)
                    flip(temp_board, i, j, color)
                    current_score, _ = minimax(temp_board, depth-1, -color)
                    if best_move is None:
                        best_move = (i, j)
                    if current_score < best_score:
                        best_score = current_score
                        best_move = (i, j)
        return best_score, best_move



def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE))
    pygame.display.set_caption('Othello')
    running = True
    current_player = 1

    is_game_over = False
    while running:
        # 判断是否有合法的落子位置，如果没有，判断游戏结束
        if not any(is_valid_move(board, row, col, current_player) for row in range(BOARD_SIZE) for col in
                   range(BOARD_SIZE)):
            current_player = -current_player  # 切换到另一玩家
            if not any(is_valid_move(board, row, col, current_player) for row in range(BOARD_SIZE) for col in
                       range(BOARD_SIZE)):
                is_game_over = True
                display_result(screen, board)
                break

        pos = handle_events()
        if pos is None:
            running = False
        elif pos and current_player == 1:
            row, col = pos
            if is_valid_move(board, row, col, current_player):
                flip(board, row, col, current_player)
                draw_board(screen, board, current_player)
                pygame.display.flip()
                current_player = -current_player
        elif current_player == -1:
            _, move = minimax(board, 4, current_player)
            if move:
                flip(board, move[0], move[1], current_player)
                draw_board(screen, board, current_player)
                pygame.display.flip()
                current_player = -current_player
        screen.fill((253, 236, 166))
        draw_board(screen, board, current_player)
        pygame.display.flip()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()



if __name__ == '__main__':
    main()