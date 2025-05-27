import pygame
import sys
import random
import enchant
import subprocess
from word import word_list  # 你的五字母單字列表

pygame.init()

WIDTH, HEIGHT = 600, 850
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordle - Pygame GUI")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (106, 170, 100)
YELLOW = (255, 223, 0)
DARKGRAY = (120, 124, 126)
RED = (255, 0, 0)

KEY_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]       # 鍵盤排列
KEY_SIZE = 40                                           # 每顆鍵寬高
KEY_GAP  = 6
KEY_TOP  = HEIGHT - 3*(KEY_SIZE+KEY_GAP) - 40           # 離底部 40px
letter_state = {c: 'unused' for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}  # 綠 / 黃 / 灰 / 未用
color_map = {'green': GREEN, 'yellow': YELLOW, 'gray': DARKGRAY, 'unused': GRAY}

FONT = pygame.font.SysFont("arial", 48, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 24)
TEXT_FONT = pygame.font.SysFont("arial", 24, bold=True)

ROWS = 6
COLS = 5
BOX_SIZE = 80
GAP = 10
TOP_MARGIN = 100
LEFT_MARGIN = (WIDTH - (COLS * BOX_SIZE + (COLS - 1) * GAP)) // 2

BG_IMG = pygame.image.load("image/8623_m.JPG").convert()
BG_IMG = pygame.transform.scale(BG_IMG, (WIDTH, HEIGHT))


BG_IMG_GAME  = pygame.image.load("image/123.jpg").convert()
BG_IMG_GAME  = pygame.transform.scale(BG_IMG_GAME, (WIDTH, HEIGHT))


d = enchant.Dict("en_US")
chosen_word = random.choice(word_list).lower()

def draw_board(guesses, colors, current_guess, error_msg, game_over, win):
    global home_btn_rect 
    
    WIN.blit(BG_IMG_GAME, (0, 0))  # 使用遊戲背景圖片
    title_text = FONT.render("Wordle", True, BLACK)
    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))
    
    for row in range(ROWS):
        for col in range(COLS):
            x = LEFT_MARGIN + col * (BOX_SIZE + GAP)
            y = TOP_MARGIN + row * (BOX_SIZE + GAP)
            rect = pygame.Rect(x, y, BOX_SIZE, BOX_SIZE)
            
            if row < len(guesses):
                color = colors[row][col]
            elif row == len(guesses):
                color = GRAY
            else:
                color = DARKGRAY
            
            pygame.draw.rect(WIN, color, rect)
            pygame.draw.rect(WIN, BLACK, rect, 2)
            
            if row < len(guesses):
                letter = guesses[row][col].upper()
            elif row == len(guesses) and col < len(current_guess):
                letter = current_guess[col].upper()
            else:
                letter = ""
            
            if letter != "":
                letter_text = FONT.render(letter, True, BLACK)
                WIN.blit(letter_text, (x + BOX_SIZE//2 - letter_text.get_width()//2,
                                       y + BOX_SIZE//2 - letter_text.get_height()//2))
    
    if error_msg != "":
        error_surface = SMALL_FONT.render(error_msg, True, RED)
        WIN.blit(error_surface, (WIDTH // 2 - error_surface.get_width() // 2, HEIGHT - 80))
    
    if game_over:
        msg_text = "You Win! :)" if win else f"You Lose! Word: {chosen_word.upper()}"
        msg_surface = TEXT_FONT.render(msg_text, True, BLACK)
        WIN.blit(msg_surface, (WIDTH // 2 - msg_surface.get_width()-5 // 2, HEIGHT - 30))
        
    for r, row in enumerate(KEY_ROWS):
        for c, ch in enumerate(row):
            x = (WIDTH - len(row)*(KEY_SIZE+KEY_GAP))//2 + c*(KEY_SIZE+KEY_GAP)
            y = KEY_TOP + r*(KEY_SIZE+KEY_GAP)
            rect = pygame.Rect(x, y, KEY_SIZE, KEY_SIZE)
            clr  = color_map[letter_state[ch]]
            pygame.draw.rect(WIN, clr, rect, border_radius=4)
            pygame.draw.rect(WIN, BLACK, rect, 2, border_radius=4)

            txt = SMALL_FONT.render(ch, True, BLACK)
            WIN.blit(txt, (x+KEY_SIZE//2-txt.get_width()//2 ,
                           y+KEY_SIZE//2-txt.get_height()//2))    

    # ---------- 新增 Home 按鈕（右下，靠 End 的左邊一點） ----------
    home_btn_rect = pygame.Rect(WIDTH-150, HEIGHT-45, 110, 35)
    pygame.draw.rect(WIN, DARKGRAY, home_btn_rect, border_radius=8)
    home_txt = SMALL_FONT.render("Home", True, WHITE)
    WIN.blit(home_txt,
             (home_btn_rect.x + 50 - home_txt.get_width()//2 +10,
              home_btn_rect.y + 18 - home_txt.get_height()//2))      
                
    pygame.display.update()

def check_guess(guess, chosen):
    """回傳 [0/1/2] 清單；並同步更新 letter_state"""
    result = [0]*COLS
    alpha = [0]*26
    for c in chosen:
        alpha[ord(c)-97] += 1

    # ① 先標出正確位置
    for i in range(COLS):
        if guess[i] == chosen[i]:
            result[i] = 1
            alpha[ord(guess[i])-97] -= 1

    # ② 再標出存在但位置錯
    for i in range(COLS):
        if result[i] == 0 and alpha[ord(guess[i])-97] > 0:
            result[i] = 2
            alpha[ord(guess[i])-97] -= 1

    # ③ 更新鍵盤顏色（綠 > 黃 > 灰）
    for i, ch in enumerate(guess):
        if result[i] == 1:
            letter_state[ch.upper()] = 'green'
        elif result[i] == 2 and letter_state[ch.upper()] != 'green':
            letter_state[ch.upper()] = 'yellow'
        elif letter_state[ch.upper()] not in ('green', 'yellow'):
            letter_state[ch.upper()] = 'gray'

    return result

def show_start_screen():
    WIN.blit(BG_IMG, (0, 0))
    title = FONT.render("Welcome to Wordle!", True, BLACK)
    prompt = SMALL_FONT.render("Press any key to start", True, DARKGRAY)

    WIN.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
    WIN.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
                
def main():
    
    show_start_screen()
    guesses = []
    colors = []
    current_guess = ""
    game_over = False
    win = False
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

                # --- 點 Home：回到主選單 (main.py) ---
                if home_btn_rect.collidepoint(mx, my):
                    subprocess.Popen([sys.executable, "main.py"])
                    pygame.quit()      # 關閉目前視窗
                    sys.exit()

                # --- 點 End Game：照舊顯示總分 ---
                if WIDTH-140 <= mx <= WIDTH-20 and HEIGHT-45 <= my <= HEIGHT-10:
                    show_final_scores(players, scores)

            if game_over:
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    current_guess = current_guess[:-1]
                    error_msg = ""
                elif event.key == pygame.K_RETURN:
                    if len(current_guess) == COLS:
                        if not d.check(current_guess):
                            error_msg = "Not a valid word. Please continue typing."
                            # 不清空 current_guess，玩家繼續編輯同一行
                        else:
                            error_msg = ""
                            guess_colors = check_guess(current_guess, chosen_word)
                            guesses.append(current_guess)
                            colors.append([
                                GREEN if c == 1 else
                                YELLOW if c == 2 else
                                GRAY for c in guess_colors])
                            if all(c == 1 for c in guess_colors):
                                game_over = True
                                win = True
                            elif len(guesses) == ROWS:
                                game_over = True
                            current_guess = ""
                else:
                    if len(current_guess) < COLS and event.unicode.isalpha():
                        current_guess += event.unicode.lower()
                        error_msg = ""
        
        draw_board(guesses, colors, current_guess, error_msg, game_over, win)

if __name__ == "__main__":
        main() 