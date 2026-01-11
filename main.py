import pygame
import math

pygame.init()

w, h = 1000, 700
screen = pygame.display.set_mode((w, h))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

G = 6 # 6.67

planet_radius = 90
ball_radius = planet_radius // 15

planet_x = w // 2
planet_y = h // 2

start_ball_x = 100
start_ball_y = h // 2

ball_x = start_ball_x
ball_y = start_ball_y

inputs = ["", "", "", ""]
labels = ["Масса планеты(тонны)", "Масса спутника(кг)", "Скорость по x (пиксели/секунда)", "Скорость по y (пиксели/секунда)"]
active = 0
started = False
ended = False

vx = 0
vy = 0
m_planet = 0
m_ball = 0
F = 0

button_rect = pygame.Rect(w // 2 - 100, h // 2 - 25, 200, 50)

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not started:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if active < 3:
                        active += 1
                    else:
                        m_planet = float(inputs[0]) * 1000
                        m_ball = float(inputs[1])
                        vx = float(inputs[2])
                        vy = float(inputs[3])
                        ball_x = start_ball_x
                        ball_y = start_ball_y
                        started = True
                        ended = False
                elif event.key == pygame.K_BACKSPACE:
                    inputs[active] = inputs[active][:-1]
                else:
                    inputs[active] += event.unicode

        elif ended:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    inputs = ["", "", "", ""]
                    active = 0
                    started = False
                    ended = False
                    vx = vy = 0

    if started and not ended:
        dx = planet_x - ball_x
        dy = planet_y - ball_y
        r = math.sqrt(dx * dx + dy * dy)

        if r <= planet_radius + ball_radius:
            ended = True
        else:
            F = G * m_planet * m_ball / (r * r)
            ax = F * dx / r / m_ball
            ay = F * dy / r / m_ball
            vx += ax
            vy += ay
            ball_x += vx
            ball_y += vy

    screen.fill((0, 0, 0))

    if not started:
        for i in range(4):
            t1 = font.render(labels[i] + ": " + inputs[i], True, (255, 255, 255))
            if i == active:
                pygame.draw.rect(screen, (100, 100, 100), (45, 45 + i * 40, 300, 30), 2)
            screen.blit(t1, (50, 50 + i * 40))
        t2 = font.render("Enter - дальше", True, (200, 200, 200))
        screen.blit(t2, (50, 230))

    else:
        pygame.draw.circle(screen, (0, 0, 255), (planet_x, planet_y), planet_radius)
        pygame.draw.circle(screen, (255, 0, 0), (int(ball_x), int(ball_y)), ball_radius)

        text_vx = font.render(f"Vx: {vx:.2f}", True, (255, 255, 255))
        text_vy = font.render(f"Vy: {vy:.2f}", True, (255, 255, 255))
        text_f = font.render(f"F: {F:.2f}", True, (255, 255, 255))

        screen.blit(text_vx, (10, 10))
        screen.blit(text_vy, (10, 30))
        screen.blit(text_f, (10, 50))

        if ended:
            pygame.draw.rect(screen, (50, 50, 50), button_rect)
            pygame.draw.rect(screen, (200, 200, 200), button_rect, 2)
            text_btn = font.render("Начать заново", True, (255, 255, 255))
            screen.blit(text_btn, (button_rect.x + 40, button_rect.y + 15))

    pygame.display.flip()

pygame.quit()
