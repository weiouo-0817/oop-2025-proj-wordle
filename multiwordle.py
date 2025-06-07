import pygame
import sys
import random
import enchant
import subprocess

from word import word_list

pygame.init()

# ===================== 全域常數 ===================== #
WIDTH, HEIGHT = 600, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordle Multiple Players – Turn‑Based")

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
KEY_TOP = HEIGHT - 3 * (KEY_SIZE + KEY_GAP) - 100  # 上移鍵盤

FONT = pygame.font.SysFont("arial", 45, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 20, bold=True)
NAME_FONT = pygame.font.SysFont("arial", 30, bold=True)
LABEL_FONT = pygame.font.SysFont("arial", 28, bold=True)

ROWS = 6
COLS = 5
BOX_SIZE = 60
GAP = 8
TOP_MARGIN = 90
LEFT_MARGIN = (WIDTH - (COLS * BOX_SIZE + (COLS - 1) * GAP)) // 2

# 背景圖片載入
BG_IMG = pygame.image.load("image/23671474_m.jpg").convert()
BG_IMG = pygame.transform.scale(BG_IMG, (WIDTH, HEIGHT))
BG_IMG_GAME = pygame.image.load("image/123.jpg").convert()
BG_IMG_GAME = pygame.transform.scale(BG_IMG_GAME, (WIDTH, HEIGHT))

dict_en = enchant.Dict("en_US")


# ===================== 資料類別 ===================== #
class Player:
    """紀錄玩家名稱與分數"""

    def __init__(self, name: str):
        self.name = name
        self.score = 0

    def add_score(self, pts: int):
        self.score += pts

    def __repr__(self):
        return f"{self.name}({self.score})"


# ===================== 遊戲主體 ===================== #
class WordleGame:
    MAX_ROUNDS = 5  # 預設最多局數

    def __init__(self):
        """初始化所有狀態與資源"""
        self.clock = pygame.time.Clock()
        self.players: list[Player] = []
        self.current_player_idx = 0
        self.round_count = 1

        # 本局狀態
        self.chosen_word = random.choice(word_list).lower()
        self.letter_state = {c: "unused" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        self.guesses: list[str] = []
        self.colors: list[list[tuple[int, int, int]]] = []
        self.current_guess = ""
        self.round_attempts = 0
        self.max_attempts = 0  # 依人數決定
        self.error_msg = ""
        self.home_btn_rect = pygame.Rect(0, 0, 0, 0)  # 先給預設值

    # ---------- 前置輸入 ---------- #
    def choose_player_count(self) -> int:
        num = ""
        choosing = True
        while choosing:
            WIN.blit(BG_IMG, (0, 0))
            title = FONT.render("How many players (1-6)?", True, BLACK)
            WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 40))
            prompt = LABEL_FONT.render(num or "_", True, BLACK)
            WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 20))
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

    def input_player_names(self, n: int):
        names = [""] * n
        idx = 0
        active = True
        while active:
            WIN.blit(BG_IMG, (0, 0))
            title = FONT.render("Enter Player Names", True, BLACK)
            WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
            prompt = SMALL_FONT.render("BACKSPACE to edit, ENTER to confirm", True, DARKGRAY)
            WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 80))

            for i in range(n):
                color = RED if i == idx else BLACK
                label = LABEL_FONT.render(f"Player {i + 1}:", True, BLACK)
                WIN.blit(label, (150, 150 + i * 60))
                name_text = NAME_FONT.render(names[i], True, color)
                WIN.blit(name_text, (280, 150 + i * 60))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        names[idx] = names[idx][:-1]
                    elif event.key == pygame.K_RETURN and names[idx]:
                        idx += 1
                        if idx >= n:
                            active = False
                    elif event.unicode.isalpha() and len(names[idx]) < 10:
                        names[idx] += event.unicode
        random.shuffle(names)
        self.players = [Player(name) for name in names]
        self.max_attempts = 3 * len(self.players)

    # ---------- 核心邏輯 ---------- #
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

        # 更新鍵盤顏色狀態 & 加分
        for i, ch in enumerate(guess):
            if result[i] == 1:
                self.letter_state[ch.upper()] = "green"
                self.players[self.current_player_idx].add_score(3)
            elif result[i] == 2 and self.letter_state[ch.upper()] != "green":
                self.letter_state[ch.upper()] = "yellow"
                self.players[self.current_player_idx].add_score(2)
            elif self.letter_state[ch.upper()] not in ("green", "yellow"):
                self.letter_state[ch.upper()] = "gray"
        return result

    # ---------- 畫面渲染 ---------- #
    def draw_board(self):
        WIN.blit(BG_IMG_GAME, (0, 0))
        title_text = FONT.render("Wordle", True, BLACK)
        WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 10))

        # 玩家清單
        for i, p in enumerate(self.players):
            color = GREEN if i == self.current_player_idx else BLACK
            info = f"{p.name} ({p.score})"
            txt = SMALL_FONT.render(info, True, color)
            WIN.blit(txt, (10, 60 + i * 25))

        start_row = max(0, len(self.guesses) - ROWS)
        vis_guesses = self.guesses[start_row:]
        vis_colors = self.colors[start_row:]

        for row in range(ROWS):
            for col in range(COLS):
                x = LEFT_MARGIN + col * (BOX_SIZE + GAP)
                y = TOP_MARGIN + row * (BOX_SIZE + GAP)
                rect = pygame.Rect(x, y, BOX_SIZE, BOX_SIZE)

                if row < len(vis_guesses):
                    color = vis_colors[row][col]
                    letter = vis_guesses[row][col].upper()
                elif row == len(vis_guesses):
                    color = GRAY
                    letter = self.current_guess[col].upper() if col < len(self.current_guess) else ""
                else:
                    color = DARKGRAY
                    letter = ""

                pygame.draw.rect(WIN, color, rect)
                pygame.draw.rect(WIN, BLACK, rect, 2)
                if letter:
                    lt = FONT.render(letter, True, BLACK)
                    WIN.blit(lt, (x + BOX_SIZE // 2 - lt.get_width() // 2,
                                  y + BOX_SIZE // 2 - lt.get_height() // 2))

        # 錯誤訊息
        if self.error_msg:
            err = SMALL_FONT.render(self.error_msg, True, RED)
            WIN.blit(err, (WIDTH // 2 - err.get_width() // 2, HEIGHT - 70))

        # 鍵盤
        color_map = {"green": GREEN, "yellow": YELLOW, "gray": DARKGRAY, "unused": GRAY}
        for r, row_key in enumerate(KEY_ROWS):
            for c, ch in enumerate(row_key):
                x = (WIDTH - len(row_key) * (KEY_SIZE + KEY_GAP)) // 2 + c * (KEY_SIZE + KEY_GAP)
                y = KEY_TOP + r * (KEY_SIZE + KEY_GAP)
                rect = pygame.Rect(x, y, KEY_SIZE, KEY_SIZE)
                clr = color_map[self.letter_state[ch]]
                pygame.draw.rect(WIN, clr, rect, border_radius=4)
                pygame.draw.rect(WIN, BLACK, rect, 2, border_radius=4)
                t = SMALL_FONT.render(ch, True, BLACK)
                WIN.blit(t, (x + KEY_SIZE // 2 - t.get_width() // 2,
                             y + KEY_SIZE // 2 - t.get_height() // 2))

        # End Game 按鈕
        end_rect = pygame.Rect(WIDTH - 140, HEIGHT - 45, 120, 35)
        pygame.draw.rect(WIN, RED, end_rect, border_radius=8)
        etxt = SMALL_FONT.render("End Game", True, WHITE)
        WIN.blit(etxt, (end_rect.x + 60 - etxt.get_width() // 2,
                        end_rect.y + 18 - etxt.get_height() // 2))

        # Home 按鈕
        self.home_btn_rect = pygame.Rect(WIDTH - 270, HEIGHT - 45, 110, 35)
        pygame.draw.rect(WIN, DARKGRAY, self.home_btn_rect, border_radius=8)
        htxt = SMALL_FONT.render("Home", True, WHITE)
        WIN.blit(htxt, (self.home_btn_rect.x + 55 - htxt.get_width() // 2,
                        self.home_btn_rect.y + 18 - htxt.get_height() // 2))

        pygame.display.update()

    # ---------- 輔助 ---------- #
    def show_final_scores(self):
        WIN.blit(BG_IMG_GAME, (0, 0))
        title = FONT.render("Final Scores", True, BLACK)
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        sorted_scores = sorted(self.players, key=lambda p: -p.score)
        for i, p in enumerate(sorted_scores):
            txt = SMALL_FONT.render(f"{i + 1}. {p.name}: {p.score} points", True, BLACK)
            WIN.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 120 + i * 40))
        exit_btn = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 80, 120, 40)
        pygame.draw.rect(WIN, DARKGRAY, exit_btn, border_radius=10)
        etxt = SMALL_FONT.render("Exit", True, WHITE)
        WIN.blit(etxt, (exit_btn.x + 60 - etxt.get_width() // 2,
                        exit_btn.y + 20 - etxt.get_height() // 2))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and exit_btn.collidepoint(event.pos):
                    pygame.quit(); sys.exit()

    def reset_round(self):
        """準備下一局"""
        self.round_count += 1
        self.chosen_word = random.choice(word_list).lower()
        self.letter_state = {c: "unused" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        self.guesses.clear()
        self.colors.clear()
        self.current_guess = ""
        self.round_attempts = 0
        self.error_msg = ""
        self.current_player_idx = 0

    # ---------- 遊戲主迴圈 ---------- #
    def run(self):
        # 前置輸入
        cnt = self.choose_player_count()
        self.input_player_names(cnt)

        while True:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if WIDTH - 140 <= mx <= WIDTH - 20 and HEIGHT - 45 <= my <= HEIGHT - 10:
                        self.show_final_scores()
                    elif self.home_btn_rect.collidepoint(mx, my):
                        subprocess.Popen([sys.executable, "main.py"])
                        pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.current_guess = self.current_guess[:-1]
                        self.error_msg = ""
                    elif event.key == pygame.K_RETURN:
                        if len(self.current_guess) == COLS:
                            if not dict_en.check(self.current_guess):
                                self.error_msg = "Not a valid word. Please continue typing."
                            else:
                                result = self.check_guess(self.current_guess)
                                guess_color = [GREEN if r == 1 else YELLOW if r == 2 else GRAY for r in result]
                                self.guesses.append(self.current_guess)
                                self.colors.append(guess_color)
                                self.round_attempts += 1
                                self.current_guess = ""

                                # 是否全部正確？
                                if all(r == 1 for r in result):
                                    self.draw_board()
                                    pygame.time.wait(1000)
                                    if self.round_count >= self.MAX_ROUNDS:
                                        self.show_final_scores()
                                    self.reset_round()

                                elif self.round_attempts >= self.max_attempts:
                                    self.draw_board()
                                        # ① 把答案印到畫面底端
                                    ans_txt = SMALL_FONT.render(
                                        f"Answer: {self.chosen_word.upper()}", True, RED)
                                    WIN.blit(ans_txt, (WIDTH // 2 - ans_txt.get_width() // 2,
                                                    HEIGHT - 90))
                                    pygame.display.update()    # ② 強制刷新，玩家能看到答案
                                    pygame.time.wait(1500)
                                    if self.round_count >= self.MAX_ROUNDS:
                                        self.show_final_scores()
                                    self.reset_round()

                                else:
                                    # 換下一位
                                    self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
                                    if self.round_attempts % len(self.players) == 0:
                                        # 每回合結束暫停一下並清盤
                                        pygame.time.wait(500)
                                        self.guesses.clear()
                                        self.colors.clear()
                                self.current_guess = ""
                    elif len(self.current_guess) < COLS and event.unicode.isalpha():
                        self.current_guess += event.unicode.lower()
                        self.error_msg = ""
            self.draw_board()


# -------------------- 入口 -------------------- #
if __name__ == "__main__":
    WordleGame().run()
