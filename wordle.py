import pygame
import sys
import random
import enchant
from word import word_list  # 你的五字母單字列表

pygame.init()

WIDTH, HEIGHT = 600, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordle - Pygame GUI")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (106, 170, 100)
YELLOW = (201, 180, 88)
DARKGRAY = (120, 124, 126)
RED = (255, 0, 0)

FONT = pygame.font.SysFont("arial", 48)
SMALL_FONT = pygame.font.SysFont("arial", 24)

ROWS = 6
COLS = 5
BOX_SIZE = 80
GAP = 10
TOP_MARGIN = 100
LEFT_MARGIN = (WIDTH - (COLS * BOX_SIZE + (COLS - 1) * GAP)) // 2

d = enchant.Dict("en_US")
chosen_word = random.choice(word_list).lower()

def draw_board(guesses, colors, current_guess, error_msg, game_over, win):
    WIN.fill(WHITE)
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
        msg_surface = SMALL_FONT.render(msg_text, True, BLACK)
        WIN.blit(msg_surface, (WIDTH // 2 - msg_surface.get_width() // 2, HEIGHT - 50))
    
    pygame.display.update()

def check_guess(guess, chosen_word):
    result = [0]*COLS
    alpha = [0]*26
    for c in chosen_word:
        alpha[ord(c)-ord('a')] += 1
    
    for i in range(COLS):
        if guess[i] == chosen_word[i]:
            result[i] = 1
            alpha[ord(guess[i]) - ord('a')] -= 1
    
    for i in range(COLS):
        if result[i] == 0:
            if alpha[ord(guess[i]) - ord('a')] > 0:
                result[i] = 2
                alpha[ord(guess[i]) - ord('a')] -= 1
            else:
                result[i] = 0
    return result

def main():
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
