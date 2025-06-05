import pygame
import sys
import random
import enchant
import subprocess
import time
import json
import os
from word import word_list  # 自備 5 字母單字表

pygame.init()

WIDTH, HEIGHT = 600, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordle – Time Trial Mode")

FONT = pygame.font.SysFont("arial", 48, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 24)
TEXT_FONT = pygame.font.SysFont("arial", 24, bold=True)

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
KEY_TOP = HEIGHT - 3 * (KEY_SIZE + KEY_GAP) - 40

ROWS, COLS = 6, 5
BOX_SIZE = 80
GAP = 10
TOP_MARGIN = 100
LEFT_MARGIN = (WIDTH - (COLS * BOX_SIZE + (COLS - 1) * GAP)) // 2

BG_IMG_MENU = pygame.transform.scale(pygame.image.load("image/8623_m.JPG").convert(), (WIDTH, HEIGHT))
BG_IMG_GAME = pygame.transform.scale(pygame.image.load("image/123.jpg").convert(), (WIDTH, HEIGHT))

dict_en = enchant.Dict("en_US")
RANKING_FILE = "time_trial_rankings.json"

class WordleGame:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.letter_state = {c: "unused" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        self.color_map = {"green": GREEN, "yellow": YELLOW, "gray": DARKGRAY, "unused": GRAY}
        self.reset_game()
        self.home_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.rank_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.start_time = None
        self.end_time = None
        self.player_name = ""

    def reset_game(self):
        self.chosen_word = random.choice(word_list).lower()
        self.guesses = []
        self.colors = []
        self.current_guess = ""
        self.game_over = False
        self.win = False
        self.error_msg = ""
        self.letter_state = {c: "unused" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}

    def input_player_name(self):
        name = ""
        entering = True
        while entering:
            WIN.fill(WHITE)
            prompt = FONT.render("Enter your name:", True, BLACK)
            WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 250))
            name_display = TEXT_FONT.render(name, True, BLACK)
            pygame.draw.rect(WIN, GRAY, (WIDTH//2 - 150, 350, 300, 50))
            WIN.blit(name_display, (WIDTH // 2 - name_display.get_width() // 2, 360))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name.strip():
                        entering = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif len(name) < 12 and event.unicode.isprintable():
                        name += event.unicode
        self.player_name = name.strip()

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
        self.start_time = time.time()

    def check_guess(self, guess):
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
        for i, ch in enumerate(guess):
            if result[i] == 1:
                self.letter_state[ch.upper()] = "green"
            elif result[i] == 2 and self.letter_state[ch.upper()] != "green":
                self.letter_state[ch.upper()] = "yellow"
            elif self.letter_state[ch.upper()] not in ("green", "yellow"):
                self.letter_state[ch.upper()] = "gray"
        return result

    def draw_board(self):
        WIN.blit(BG_IMG_GAME, (0, 0))
        title_text = FONT.render("Wordle", True, BLACK)
        WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))

        # 計時器
        if self.start_time and not self.end_time:
            elapsed = round(time.time() - self.start_time, 1)
            timer_text = TEXT_FONT.render(f"Time: {elapsed:.1f}s", True, BLACK)
            WIN.blit(timer_text, (WIDTH - 180, 20))
        elif self.end_time:
            elapsed = round(self.end_time - self.start_time, 1)
            timer_text = TEXT_FONT.render(f"Time: {elapsed:.1f}s", True, BLACK)
            WIN.blit(timer_text, (WIDTH - 180, 20))

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

        if self.error_msg:
            err = SMALL_FONT.render(self.error_msg, True, RED)
            WIN.blit(err, (WIDTH // 2 - err.get_width() // 2, HEIGHT - 80))

        if self.game_over:
            msg = ("You Win! :)" if self.win else f"You Lose! Word: {self.chosen_word.upper()}")
            mtxt = TEXT_FONT.render(msg, True, BLACK)
            WIN.blit(mtxt, (WIDTH // 2 - mtxt.get_width() // 2, HEIGHT - 40))

            self.rank_btn_rect = pygame.Rect(WIDTH - 160, HEIGHT - 50, 140, 40)
            pygame.draw.rect(WIN, GREEN, self.rank_btn_rect, border_radius=10)
            rtxt = SMALL_FONT.render("View Ranking", True, WHITE)
            WIN.blit(rtxt, (self.rank_btn_rect.x + 70 - rtxt.get_width() // 2,
                            self.rank_btn_rect.y + 20 - rtxt.get_height() // 2))

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

        pygame.display.update()

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
                    self.current_guess = ""
                    if all(x == 1 for x in res):
                        self.game_over = True
                        self.win = True
                        self.end_time = time.time()
                        self.save_ranking()
                        pygame.time.set_timer(pygame.USEREVENT, 5000)
                    elif len(self.guesses) == ROWS:
                        self.game_over = True
                        self.end_time = time.time()
        else:
            if len(self.current_guess) < COLS and event.unicode.isalpha():
                self.current_guess += event.unicode.lower()
                self.error_msg = ""

    def save_ranking(self):
        elapsed = round(self.end_time - self.start_time, 2)
        if not self.win:
            return
        data = []
        if os.path.exists(RANKING_FILE):
            with open(RANKING_FILE, "r") as f:
                data = json.load(f)
        data.append({"name": self.player_name, "time": elapsed})
        data.sort(key=lambda x: x["time"])
        with open(RANKING_FILE, "w") as f:
            json.dump(data[:10], f)

    def load_rank_data(self):
        if os.path.exists(RANKING_FILE):
            with open(RANKING_FILE, "r") as f:
                return json.load(f)
        return []

    def show_ranking(self, top_list):
        WIN.fill(WHITE)
        title = FONT.render("Top 10 Time Trial Winners", True, BLACK)
        WIN.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        for idx, entry in enumerate(top_list):
            line = f"{idx+1}. {entry['name']} - {entry['time']}s"
            text = TEXT_FONT.render(line, True, BLACK)
            WIN.blit(text, (WIDTH//2 - text.get_width()//2, 150 + idx * 50))

        back_btn = pygame.Rect(WIDTH - 180, HEIGHT - 60, 160, 40)
        pygame.draw.rect(WIN, DARKGRAY, back_btn, border_radius=10)
        btxt = SMALL_FONT.render("Back to Menu", True, WHITE)
        WIN.blit(btxt, (back_btn.x + 80 - btxt.get_width()//2, back_btn.y + 20 - btxt.get_height()//2))
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_btn.collidepoint(event.pos):
                        subprocess.Popen([sys.executable, "main.py"])
                        pygame.quit(); sys.exit()

    def run(self):
        self.input_player_name()
        self.show_start_screen()
        while True:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.USEREVENT and self.win:
                    self.show_ranking(self.load_rank_data())
                elif event.type == pygame.KEYDOWN and not self.game_over:
                    self.handle_keydown(event)
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                    if self.rank_btn_rect.collidepoint(event.pos):
                        self.show_ranking(self.load_rank_data())
            self.draw_board()

if __name__ == "__main__":
    WordleGame().run()
