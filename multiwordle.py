import pygame
import sys
import random
import enchant
import subprocess

from word import word_list

pygame.init()

WIDTH, HEIGHT = 600, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordle mutiple Players Turn-Based Single Word")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (106, 170, 100)
YELLOW = (255, 223, 0)
DARKGRAY = (120, 124, 126)
RED = (255, 0, 0)

KEY_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
KEY_SIZE = 40
KEY_GAP = 6
KEY_TOP = HEIGHT - 3*(KEY_SIZE+KEY_GAP) - 100  # 上移鍵盤

color_map = {'green': GREEN, 'yellow': YELLOW, 'gray': DARKGRAY, 'unused': GRAY}

FONT = pygame.font.SysFont("arial", 45, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 20, bold=True)
NAME_FONT = pygame.font.SysFont("arial", 30, bold=True)
LABEL_FONT = pygame.font.SysFont("arial", 28, bold=True)
TEXT_FONT = pygame.font.SysFont("arial", 24, bold=True)

ROWS = 6
COLS = 5
BOX_SIZE = 60
GAP = 8
TOP_MARGIN = 90
LEFT_MARGIN = (WIDTH - (COLS * BOX_SIZE + (COLS - 1) * GAP)) // 2

BG_IMG = pygame.image.load("image/23671474_m.jpg").convert()
BG_IMG = pygame.transform.scale(BG_IMG, (WIDTH, HEIGHT))

BG_IMG_GAME  = pygame.image.load("image/123.jpg").convert()
BG_IMG_GAME  = pygame.transform.scale(BG_IMG_GAME, (WIDTH, HEIGHT))

d = enchant.Dict("en_US")

def choose_player_count():
    """讓使用者用 1–6 數字鍵選人數，回傳整數"""
    num = ""
    choosing = True
    while choosing:
        WIN.blit(BG_IMG, (0, 0))
        title = FONT.render("How many players (1-6)?", True, BLACK)
        WIN.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 40))

        prompt = LABEL_FONT.render(num or "_", True, BLACK)
        WIN.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 + 20))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.unicode.isdigit() and 1 <= int(event.unicode) <= 6:
                    num = event.unicode
                elif event.key == pygame.K_RETURN and num:
                    choosing = False
    return int(num)

def input_player_names(num_players):
    names = [""] * num_players
    current_idx = 0
    input_active = True

    while input_active:
        WIN.blit(BG_IMG, (0, 0))
        title = FONT.render("Enter Player Names", True, BLACK)
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2 , 20))

        prompt = SMALL_FONT.render("BACKSPACE to edit, ENTER to confirm", True, DARKGRAY)
        WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 80))

        for i in range(num_players):
            color = RED if i == current_idx else BLACK
            label = LABEL_FONT.render(f"Player {i+1}:", True, BLACK )
            WIN.blit(label, (150, 150 + i * 60))
            name_text = NAME_FONT.render(names[i], True, color)
            WIN.blit(name_text, (280, 150 + i * 60))

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    names[current_idx] = names[current_idx][:-1]
                elif event.key == pygame.K_RETURN:
                    if len(names[current_idx]) > 0:
                        current_idx += 1
                        if current_idx >= num_players:
                            input_active = False
                else:
                    if len(names[current_idx]) < 10 and event.unicode.isalpha():
                        names[current_idx] += event.unicode
        
    random.shuffle(names)  # 打亂順序
    return names
    
def show_final_scores(players, scores):
    WIN.blit(BG_IMG_GAME, (0, 0))  # 使用遊戲背景圖片
    title = FONT.render("Final Scores", True, BLACK)
    WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

    sorted_scores = sorted(zip(players, scores), key=lambda x: -x[1])

    for i, (player, score) in enumerate(sorted_scores):
        score_text = SMALL_FONT.render(f"{i+1}. {player}: {score} points", True, BLACK)
        WIN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 120 + i * 40))

    exit_btn = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 80, 120, 40)
    pygame.draw.rect(WIN, DARKGRAY, exit_btn, border_radius=10)
    exit_text = SMALL_FONT.render("Exit", True, WHITE)
    WIN.blit(exit_text, (exit_btn.x + 60 - exit_text.get_width() // 2,
                         exit_btn.y + 20 - exit_text.get_height() // 2))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if exit_btn.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()

def draw_board(guesses, colors, current_guess, error_msg, letter_state, players, current_player, scores):
    
    global home_btn_rect # 用於回到主選單
    
    WIN.blit(BG_IMG_GAME, (0, 0))  # 使用遊戲背景圖片
    title_text = FONT.render("Wordle", True, BLACK)
    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 10))

    for i, player in enumerate(players):
        color = GREEN if i == current_player else BLACK
        info = f"{player} ({scores[i]})"
        player_text = SMALL_FONT.render(info, True, color)
        WIN.blit(player_text, (10, 60 + i * 25))

    start_row = max(0, len(guesses) - ROWS)
    visible_guesses = guesses[start_row:]
    visible_colors = colors[start_row:]

    for row in range(ROWS):
        for col in range(COLS):
            x = LEFT_MARGIN + col * (BOX_SIZE + GAP)
            y = TOP_MARGIN + row * (BOX_SIZE + GAP)
            rect = pygame.Rect(x, y, BOX_SIZE, BOX_SIZE)

            if row < len(visible_guesses):
                color = visible_colors[row][col]
                letter = visible_guesses[row][col].upper()
            elif row == len(visible_guesses):
                color = GRAY
                letter = current_guess[col].upper() if col < len(current_guess) else ""
            else:
                color = DARKGRAY
                letter = ""

            pygame.draw.rect(WIN, color, rect)
            pygame.draw.rect(WIN, BLACK, rect, 2)

            if letter:
                letter_text = FONT.render(letter, True, BLACK)
                WIN.blit(letter_text, (x + BOX_SIZE//2 - letter_text.get_width()//2,
                                       y + BOX_SIZE//2 - letter_text.get_height()//2))

    if error_msg:
        error_surface = SMALL_FONT.render(error_msg, True, RED)
        WIN.blit(error_surface, (WIDTH // 2 - error_surface.get_width() // 2, HEIGHT - 60))

    for r, row in enumerate(KEY_ROWS):
        for c, ch in enumerate(row):
            x = (WIDTH - len(row)*(KEY_SIZE+KEY_GAP))//2 + c*(KEY_SIZE+KEY_GAP)
            y = KEY_TOP + r*(KEY_SIZE+KEY_GAP)
            rect = pygame.Rect(x, y, KEY_SIZE, KEY_SIZE)
            clr = color_map[letter_state[ch]]
            pygame.draw.rect(WIN, clr, rect, border_radius=4)
            pygame.draw.rect(WIN, BLACK, rect, 2, border_radius=4)

            txt = SMALL_FONT.render(ch, True, BLACK)
            WIN.blit(txt, (x + KEY_SIZE//2 - txt.get_width()//2,
                           y + KEY_SIZE//2 - txt.get_height()//2))

    # End Game button
    end_btn_rect = pygame.Rect(WIDTH - 140, HEIGHT - 45, 120, 35)
    pygame.draw.rect(WIN, RED, end_btn_rect, border_radius=8)
    end_txt = SMALL_FONT.render("End Game", True, WHITE)
    WIN.blit(end_txt, (end_btn_rect.x + 60 - end_txt.get_width() // 2,
                       end_btn_rect.y + 18 - end_txt.get_height() // 2))
    
    # ---------- 新增 Home 按鈕（右下，靠 End 的左邊一點） ----------
    home_btn_rect = pygame.Rect(WIDTH-270, HEIGHT-45, 110, 35)
    pygame.draw.rect(WIN, DARKGRAY, home_btn_rect, border_radius=8)
    home_txt = SMALL_FONT.render("Home", True, WHITE)
    WIN.blit(home_txt,
             (home_btn_rect.x + 55 - home_txt.get_width()//2,
              home_btn_rect.y + 18 - home_txt.get_height()//2))   

    pygame.display.update()

def check_guess(guess, chosen, letter_state):
    result = [0]*COLS
    alpha = [0]*26
    for c in chosen:
        alpha[ord(c)-97] += 1

    for i in range(COLS):
        if guess[i] == chosen[i]:
            result[i] = 1
            alpha[ord(guess[i])-97] -= 1

    for i in range(COLS):
        if result[i] == 0 and alpha[ord(guess[i])-97] > 0:
            result[i] = 2
            alpha[ord(guess[i])-97] -= 1

    for i, ch in enumerate(guess):
        if result[i] == 1:
            letter_state[ch.upper()] = 'green'
        elif result[i] == 2 and letter_state[ch.upper()] != 'green':
            letter_state[ch.upper()] = 'yellow'
        elif letter_state[ch.upper()] not in ('green', 'yellow'):
            letter_state[ch.upper()] = 'gray'

    return result

def main():
    MAX_ROUNDS = 5     # ← 想玩幾局就改這裡
    round_count = 1      # 目前是第幾局（第一局從 1 開始）
    
    num_players = choose_player_count()      # ① 先決定幾人
    players = input_player_names(num_players)   # ② 輸入相應個名字
    scores  = [0] * num_players                # ③ 分數陣列同長
    chosen_word = random.choice(word_list).lower()
    letter_state = {c: 'unused' for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}

    guesses = []
    colors = []
    current_guess = ""
    current_player = 0
    round_attempts = 0
    max_attempts = 2 * num_players
    error_msg = ""

    clock = pygame.time.Clock()

    while True:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if WIDTH - 140 <= mx <= WIDTH - 20 and HEIGHT - 45 <= my <= HEIGHT - 10:
                    show_final_scores(players, scores)

                # --- 點 Home：回到主選單 (main.py) ---
                if home_btn_rect.collidepoint(mx, my):
                    subprocess.Popen([sys.executable, "main.py"])
                    pygame.quit()      # 關閉目前視窗
                    sys.exit()

                # --- 點 End Game：照舊顯示總分 ---
                if WIDTH-140 <= mx <= WIDTH-20 and HEIGHT-45 <= my <= HEIGHT-10:
                    show_final_scores(players, scores)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    current_guess = current_guess[:-1]
                    error_msg = ""
                elif event.key == pygame.K_RETURN:
                    if len(current_guess) == COLS:
                        if not d.check(current_guess):
                            error_msg = "Not a valid word. Please continue typing."
                        else:
                            error_msg = ""
                            result = check_guess(current_guess, chosen_word, letter_state)
                            guess_color = [
                                GREEN if r == 1 else YELLOW if r == 2 else GRAY for r in result
                            ]

                            for res in result:
                                if res == 1:
                                    scores[current_player] += 3
                                elif res == 2:
                                    scores[current_player] += 2

                            guesses.append(current_guess)
                            colors.append(guess_color)
                            round_attempts += 1
                            if all(r == 1 for r in result):
                                draw_board(guesses, colors, "", "", letter_state, players, current_player, scores)
                                pygame.time.wait(1000)
                                
                                # ---------- 新增 ----------
                                if round_count >= MAX_ROUNDS:          # 已經玩完最後一局
                                    show_final_scores(players, scores)
                                    pygame.quit()
                                    sys.exit()
                                round_count += 1                       # 還沒達上限，就進入下一局
                                # --------------------------
                                
                                chosen_word = random.choice(word_list).lower()
                                guesses.clear()
                                colors.clear()
                                letter_state = {c: 'unused' for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
                                round_attempts = 0

                            elif round_attempts % num_players == 0:
                                pygame.time.wait(500)
                                guesses.clear()
                                colors.clear()

                            if round_attempts >= max_attempts:
                                draw_board(guesses, colors, "", f"Answer: {chosen_word.upper()}", letter_state, players, current_player, scores)
                                pygame.time.wait(2000)
                                # ---------- 新增 ----------
                                if round_count >= MAX_ROUNDS:
                                    show_final_scores(players, scores)
                                    pygame.quit()
                                    sys.exit()
                                round_count += 1
                                # --------------------------
                                chosen_word = random.choice(word_list).lower()
                                guesses.clear()
                                colors.clear()
                                letter_state = {c: 'unused' for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
                                round_attempts = 0

                            current_guess = ""
                            current_player = (current_player + 1) % num_players

                elif len(current_guess) < COLS and event.unicode.isalpha():
                    current_guess += event.unicode.lower()
                    error_msg = ""

        draw_board(guesses, colors, current_guess, error_msg, letter_state, players, current_player, scores)

if __name__ == "__main__":
    main()
