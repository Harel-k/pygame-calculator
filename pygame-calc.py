import pygame
import sys
import time
import os
print("Current folder:", os.getcwd())
print("Files in folder:", os.listdir())


pygame.init()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # used when running from PyInstaller bundle
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

icon = pygame.image.load(resource_path("calc_icon.png"))

pygame.display.set_icon(icon)
WIDTH, HEIGHT = 430, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Calculator")
FONT = pygame.font.SysFont("segoeui", 30)
MEDIUM = pygame.font.SysFont("segoeui", 22)
SMALL = pygame.font.SysFont("segoeui", 15)
BIG = pygame.font.SysFont("segoeui", 34)

# Colors
WHITE = (255, 255, 255)
BG = (245, 247, 251)
BLACK = (32, 34, 42)
GRAY = (220, 224, 230)
DARKGRAY = (120, 125, 140)
BLUE = (66, 140, 255)
SOFTBLUE = (240, 248, 255)
GREEN = (50, 220, 180)
RED = (242, 94, 94)
SHADOW = (224, 230, 242)
ANSWER_BG = (250, 252, 255)
HIGHLIGHT = (235, 244, 255)
YELLOW = (255, 220, 50)

def draw_shadow(surface, rect, radius=12):
    shadow_rect = rect.inflate(8, 8)
    shadow_rect.topleft = (rect.left + 2, rect.top + 4)
    pygame.draw.rect(surface, SHADOW, shadow_rect, border_radius=radius)

def draw_rounded_rect(surface, color, rect, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

class InputBox:
    def __init__(self, x, y, w, h, hint):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = ''
        self.active = False
        self.hint = hint

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif (
                event.unicode.isdigit()
                or (event.unicode == '-' and self.text == '')
                or (event.unicode == '.' and '.' not in self.text)
            ):
                self.text += event.unicode

    def draw(self, screen):
        color = BLUE if self.active else GRAY
        draw_shadow(screen, self.rect, 16)
        draw_rounded_rect(screen, WHITE, self.rect, 16)
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=16)
        if self.text:
            txt = FONT.render(self.text, True, BLACK)
            screen.blit(txt, (self.rect.x+14, self.rect.y+9))
        else:
            hint = SMALL.render(self.hint, True, DARKGRAY)
            screen.blit(hint, (self.rect.x+14, self.rect.y+14))

    def get_value(self):
        try:
            return float(self.text)
        except:
            return None

def draw_spinner(screen, cx, cy, angle):
    length = 32
    for i in range(12):
        a = angle + i * 30
        fade = 180 - i*15
        color = (SOFTBLUE[0], SOFTBLUE[1], SOFTBLUE[2], fade)
        vec = pygame.math.Vector2(1,0).rotate(a)
        x = cx + length * vec.x
        y = cy + length * vec.y
        pygame.draw.line(screen, SOFTBLUE if i<9 else BLUE, (cx,cy), (x,y), 5)

def draw_button(rect, text, enabled, hovered, selected=False):
    if selected:
        color = GREEN
        textcolor = BLUE
        border_color = YELLOW
    else:
        color = BLUE if enabled else GRAY
        textcolor = WHITE if enabled else DARKGRAY
        border_color = color
    draw_shadow(screen, rect, 16)
    draw_rounded_rect(screen, color if not hovered else GREEN, rect, 16)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=16)
    txt = MEDIUM.render(text, True, textcolor)
    screen.blit(txt, (rect.x + rect.w//2 - txt.get_width()//2, rect.y + rect.h//2 - txt.get_height()//2))

def main():
    box1 = InputBox(32, 70, 120, 54, "Number 1")
    box2 = InputBox(278, 70, 120, 54, "Number 2")
    operations = ["+", "-", "×", "÷"]
    op_rects = [pygame.Rect(70 + i*80, 150, 60, 50) for i in range(4)]
    selected_op = 0
    calc_button = pygame.Rect(120, 230, 190, 58)
    answer = ""
    answer_bg_rect = pygame.Rect(38, 312, 355, 70)
    loading = False
    spinner_angle = 0
    loading_start = 0
    error_msg = ""
    btn_hovered = False
    clock = pygame.time.Clock()

    while True:
        mx, my = pygame.mouse.get_pos()
        btn_hovered = calc_button.collidepoint(mx, my)
        op_hovered = [r.collidepoint(mx, my) for r in op_rects]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if not loading:
                box1.handle_event(event)
                box2.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(op_rects):
                        if rect.collidepoint(event.pos):
                            selected_op = i
                    if calc_button.collidepoint(event.pos) and btn_hovered:
                        n1 = box1.get_value()
                        n2 = box2.get_value()
                        op = operations[selected_op]
                        error_msg = ""
                        if n1 is None or n2 is None:
                            error_msg = "Enter both numbers!"
                            answer = ""
                        else:
                            loading = True
                            loading_start = time.time()
                            answer = ""
        # BG
        screen.fill(BG)
        # Title
        title = BIG.render("Calculator", True, BLUE)
        screen.blit(title, (WIDTH//2-title.get_width()//2, 16))
        # Input boxes
        box1.draw(screen)
        box2.draw(screen)
        # Operation buttons
        for i, rect in enumerate(op_rects):
            draw_button(rect, operations[i], True, op_hovered[i], selected=(i==selected_op))
        # Button
        draw_button(calc_button, "CALCULATE", not loading, btn_hovered)
        # Spinner or answer
        if loading:
            draw_rounded_rect(screen, ANSWER_BG, answer_bg_rect, 18)
            spinner_angle = (spinner_angle + 12) % 360
            draw_spinner(screen, WIDTH//2, 346, spinner_angle)
            if time.time() - loading_start > 1.2:
                n1 = box1.get_value()
                n2 = box2.get_value()
                op = operations[selected_op]
                try:
                    if op == "+":
                        result = n1 + n2
                    elif op == "-":
                        result = n1 - n2
                    elif op == "×":
                        result = n1 * n2
                    elif op == "÷":
                        if n2 == 0:
                            raise ZeroDivisionError
                        result = round(n1 / n2, 6)
                    answer = f"{n1} {op} {n2} = {result}"
                    error_msg = ""
                except ZeroDivisionError:
                    answer = ""
                    error_msg = "Can't divide by zero!"
                except:
                    answer = ""
                    error_msg = "Math error!"
                loading = False
        else:
            if answer:
                draw_rounded_rect(screen, ANSWER_BG, answer_bg_rect, 18)
                txt = FONT.render(answer, True, BLUE)
                screen.blit(txt, (WIDTH//2-txt.get_width()//2, 332))
            if error_msg:
                draw_rounded_rect(screen, ANSWER_BG, answer_bg_rect, 18)
                txt = FONT.render(error_msg, True, RED)
                screen.blit(txt, (WIDTH//2-txt.get_width()//2, 332))
        pygame.display.flip()
        clock.tick(60)

main()
