import pygame
import sys
import random
import enchant
import subprocess
from word import word_list  # 自備 5 字母單字表

pygame.init()

# ==================== 視窗與字型 ==================== #
WIDTH, HEIGHT = 600, 850
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordle – Pygame GUI (OOP)")

FONT = pygame.font.SysFont("arial", 48, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 24)
TEXT_FONT = pygame.font.SysFont("arial", 24, bold=True)

# ==================== 顏色常數 ==================== #
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (106, 170, 100)
YELLOW = (255, 223, 0)
DARKGRAY = (120, 124, 126)
RED = (255, 0, 0)

# ==================== UI 參數 ==================== #
KEY_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
KEY_SIZE = 40
KEY_GAP = 6
KEY_TOP = HEIGHT - 3 * (KEY_SIZE + KEY_GAP) - 40

ROWS, COLS = 6, 5
BOX_SIZE = 80
GAP = 10
TOP_MARGIN = 100
LEFT_MARGIN = (WIDTH - (COLS * BOX_SIZE + (COLS - 1) * GAP)) // 2

# ==================== 資源讀取 ==================== #
BG_IMG_MENU = pygame.transform.scale(pygame.image.load("image/8623_m.JPG").convert(), (WIDTH, HEIGHT))
BG_IMG_GAME = pygame.transform.scale(pygame.image.load("image/123.jpg").convert(), (WIDTH, HEIGHT))

dict_en = enchant.Dict("en_US")


# ==================== 遊戲主體類 ==================== #
class WordleGame:
    def __init__(self):
        """初始化整個遊戲狀態"""
        self.clock = pygame.time.Clock()
        self.letter_state = {c: "unused" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        self.color_map = {"green": GREEN, "yellow": YELLOW, "gray": DARKGRAY, "unused": GRAY}
        self.reset_game()
        self.home_btn_rect = pygame.Rect(0, 0, 0, 0)  # placeholder

    # ---------- 流程控制 ---------- #
    def reset_game(self):
        self.chosen_word = random.choice(word_list).lower()
        self.guesses: list[str] = []
        self.colors: list[list[tuple[int, int, int]]] = []
        self.current_guess = ""
        self.game_over = False
        self.win = False
        self.error_msg = ""
        self.letter_state = {c: "unused" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}

    def show_start_screen(self):
        WIN.blit(BG_IMG_MENU, (0, 0))
        title = FONT.render("Welcome to Wordle!", True, BLACK)
        prompt = SMALL_FONT.render("Press any key to start", True, DARKGRAY)
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2))
        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    waiting = False

    # ---------- 核心檢查 ---------- #
    def check_guess(self, guess: str):
        result = [0] * COLS
        alpha = [0] * 26
        for c in self.chosen_word:
            alpha[ord(c) - 97] += 1
        for i in range(COLS):
            if guess[i] == self.chosen_word[i]:
                result[i] = 1
                alpha[ord(guess[i]) - 97] -= 1
        for i in range(COLS):
            if result[i] == 0 and alpha[ord(guess[i]) - 97] > 0:
                result[i] = 2
                alpha[ord(guess[i]) - 97] -= 1
        # 更新鍵盤狀態
        for i, ch in enumerate(guess):
            if result[i] == 1:
                self.letter_state[ch.upper()] = "green"
            elif result[i] == 2 and self.letter_state[ch.upper()] != "green":
                self.letter_state[ch.upper()] = "yellow"
            elif self.letter_state[ch.upper()] not in ("green", "yellow"):
                self.letter_state[ch.upper()] = "gray"
        return result

    # ---------- 畫面渲染 ---------- #
    def draw_board(self):
        WIN.blit(BG_IMG_GAME, (0, 0))
        title_text = FONT.render("Wordle", True, BLACK)
        WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))

        # 方格
        for row in range(ROWS):
            for col in range(COLS):
                x = LEFT_MARGIN + col * (BOX_SIZE + GAP)
                y = TOP_MARGIN + row * (BOX_SIZE + GAP)
                rect = pygame.Rect(x, y, BOX_SIZE, BOX_SIZE)

                if row < len(self.guesses):
                    color = self.colors[row][col]
                elif row == len(self.guesses):
                    color = GRAY
                else:
                    color = DARKGRAY

                pygame.draw.rect(WIN, color, rect)
                pygame.draw.rect(WIN, BLACK, rect, 2)

                if row < len(self.guesses):
                    letter = self.guesses[row][col].upper()
                elif row == len(self.guesses) and col < len(self.current_guess):
                    letter = self.current_guess[col].upper()
                else:
                    letter = ""

                if letter:
                    lt = FONT.render(letter, True, BLACK)
                    WIN.blit(lt, (x + BOX_SIZE // 2 - lt.get_width() // 2,
                                  y + BOX_SIZE // 2 - lt.get_height() // 2))
        # 錯誤訊息
        if self.error_msg:
            err = SMALL_FONT.render(self.error_msg, True, RED)
            WIN.blit(err, (WIDTH // 2 - err.get_width() // 2, HEIGHT - 80))

        # 結果訊息
        if self.game_over:
            msg = ("You Win! :)" if self.win else f"You Lose! Word: {self.chosen_word.upper()}")
            mtxt = TEXT_FONT.render(msg, True, BLACK)
            WIN.blit(mtxt, (WIDTH // 2 - mtxt.get_width() // 2, HEIGHT - 40))

        # 畫鍵盤
        for r, row_key in enumerate(KEY_ROWS):
            for c, ch in enumerate(row_key):
                x = (WIDTH - len(row_key) * (KEY_SIZE + KEY_GAP)) // 2 + c * (KEY_SIZE + KEY_GAP)
                y = KEY_TOP + r * (KEY_SIZE + KEY_GAP)
                rect = pygame.Rect(x, y, KEY_SIZE, KEY_SIZE)
                clr = self.color_map[self.letter_state[ch]]
                pygame.draw.rect(WIN, clr, rect, border_radius=4)
                pygame.draw.rect(WIN, BLACK, rect, 2, border_radius=4)
                t = SMALL_FONT.render(ch, True, BLACK)
                WIN.blit(t, (x + KEY_SIZE // 2 - t.get_width() // 2,
                             y + KEY_SIZE // 2 - t.get_height() // 2))

        # Home 按鈕
        self.home_btn_rect = pygame.Rect(WIDTH - 150, HEIGHT - 45, 110, 35)
        pygame.draw.rect(WIN, DARKGRAY, self.home_btn_rect, border_radius=8)
        htxt = SMALL_FONT.render("Home", True, WHITE)
        WIN.blit(htxt, (self.home_btn_rect.x + 55 - htxt.get_width() // 2,
                        self.home_btn_rect.y + 18 - htxt.get_height() // 2))

        pygame.display.update()

    # ---------- 事件處理 ---------- #
    def handle_keydown(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.current_guess = self.current_guess[:-1]
            self.error_msg = ""
        elif event.key == pygame.K_RETURN:
            if len(self.current_guess) == COLS:
                if not dict_en.check(self.current_guess):
                    self.error_msg = "Not a valid word. Please continue typing."
                else:
                    self.error_msg = ""
                    res = self.check_guess(self.current_guess)
                    self.guesses.append(self.current_guess)
                    self.colors.append([GREEN if x == 1 else YELLOW if x == 2 else GRAY for x in res])
                    if all(x == 1 for x in res):
                        self.game_over = True; self.win = True
                    elif len(self.guesses) == ROWS:
                        self.game_over = True
                    self.current_guess = ""
        else:
            if len(self.current_guess) < COLS and event.unicode.isalpha():
                self.current_guess += event.unicode.lower()
                self.error_msg = ""

    # ---------- 主迴圈 ---------- #
    def run(self):
        self.show_start_screen()
        while True:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.home_btn_rect.collidepoint(event.pos):
                        subprocess.Popen([sys.executable, "main.py"])
                        pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN and not self.game_over:
                    self.handle_keydown(event)
            self.draw_board()


# ==================== 入口 ==================== #
if __name__ == "__main__":
    WordleGame().run()
