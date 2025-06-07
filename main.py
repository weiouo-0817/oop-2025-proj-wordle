import pygame
import sys
import subprocess

pygame.init()

WIDTH, HEIGHT = 600, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordle Start Menu")

BG_IMG = pygame.image.load("image/8623_m.JPG").convert()
BG_IMG = pygame.transform.scale(BG_IMG, (WIDTH, HEIGHT))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
GREEN = (106, 170, 100)

TITLE_FONT = pygame.font.SysFont("arial", 48, bold=True)
FONT = pygame.font.SysFont("arial", 36, bold=True)
BUTTON_FONT = pygame.font.SysFont("arial", 28 , bold=True)

def draw_start_menu():
    WIN.blit(BG_IMG, (0, 0))

    title = TITLE_FONT.render("Welcome to Wordle!", True, BLACK)
    WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    single_button = pygame.Rect(WIDTH//2 - 100, 220, 200, 60)
    multi_button = pygame.Rect(WIDTH//2 - 100, 320, 200, 60)
    time_trial_button = pygame.Rect(WIDTH//2 - 100, 420, 200, 60)

    pygame.draw.rect(WIN, GREEN, single_button, border_radius=10)
    pygame.draw.rect(WIN, GREEN, multi_button, border_radius=10)
    pygame.draw.rect(WIN, GREEN, time_trial_button, border_radius=10)

    single_text = BUTTON_FONT.render("Single Player", True, WHITE)
    multi_text = BUTTON_FONT.render("Six Players", True, WHITE)
    time_trial_text = BUTTON_FONT.render("Time Trial", True, WHITE)

    WIN.blit(single_text, (single_button.x + single_button.width//2 - single_text.get_width()//2,
                           single_button.y + single_button.height//2 - single_text.get_height()//2))
    WIN.blit(multi_text, (multi_button.x + multi_button.width//2 - multi_text.get_width()//2,
                          multi_button.y + multi_button.height//2 - multi_text.get_height()//2))
    WIN.blit(time_trial_text, (time_trial_button.x + time_trial_button.width//2 - time_trial_text.get_width()//2,
                               time_trial_button.y + time_trial_button.height//2 - time_trial_text.get_height()//2))

    pygame.display.update()
    return single_button, multi_button, time_trial_button

def start_menu():
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(30)
        single_btn, multi_btn, time_trial_btn = draw_start_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if single_btn.collidepoint(event.pos):
                    subprocess.Popen([sys.executable, "singlewordle.py"])
                    pygame.quit()
                    sys.exit()
                elif multi_btn.collidepoint(event.pos):
                    subprocess.Popen([sys.executable, "multiwordle.py"])
                    pygame.quit()
                    sys.exit()
                elif time_trial_btn.collidepoint(event.pos):
                    subprocess.Popen([sys.executable, "single_time_trial.py"])
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    start_menu()