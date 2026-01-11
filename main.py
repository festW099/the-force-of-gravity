import pygame
import math
import random

pygame.init()

w, h = 1000, 700
screen = pygame.display.set_mode((w, h))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 22)

G = 6
e = 0.5

planet_radius = 90
ball_radius = planet_radius // 15

planet_x = w // 2
planet_y = h // 2

start_ball_x = 100
start_ball_y = h // 2

ball_x = start_ball_x
ball_y = start_ball_y

inputs = ["", "", "", ""]
labels = ["Масса планеты(тонны)", "Масса спутника(кг)", "Скорость X", "Скорость Y"]
active = 0

started = False
paused = False
ask_restart = False
collided = False
show_vectors = True

vx = vy = 0
ax = ay = 0
m_planet = m_ball = 0

angle_prev = None
orbits = 0
orbit_timer = 0

btn_restart = pygame.Rect(w - 210, 20, 190, 35)
btn_random = pygame.Rect(w - 210, 65, 190, 35)
btn_pause = pygame.Rect(w - 210, 110, 190, 35)
btn_vectors = pygame.Rect(w - 210, 155, 190, 35)

btn_same = pygame.Rect(w // 2 - 220, h // 2, 200, 45)
btn_new = pygame.Rect(w // 2 + 20, h // 2, 200, 45)

def reset_simulation():
    global ball_x, ball_y, angle_prev, orbits, orbit_timer, paused, collided, m_ball, m_planet, vx, vy
    m_planet = float(inputs[0]) * 1000
    m_ball = float(inputs[1])
    vx = float(inputs[2])
    vy = float(inputs[3])
    ball_x = start_ball_x
    ball_y = start_ball_y
    angle_prev = None
    orbits = 0
    orbit_timer = 0
    paused = False
    collided = False

def draw_vector(surface, start_pos, vector, color, scale=1.0):
    if vector[0] == 0 and vector[1] == 0:
        return
        
    end_x = start_pos[0] + vector[0] * scale
    end_y = start_pos[1] + vector[1] * scale
    
    pygame.draw.line(surface, color, start_pos, (end_x, end_y), 2)
    
    angle = math.atan2(vector[1], vector[0])
    arrow_length = 10
    arrow_angle = math.pi / 6
    
    pygame.draw.line(surface, color, 
                     (end_x, end_y),
                     (end_x - arrow_length * math.cos(angle - arrow_angle),
                      end_y - arrow_length * math.sin(angle - arrow_angle)), 2)
    pygame.draw.line(surface, color,
                     (end_x, end_y),
                     (end_x - arrow_length * math.cos(angle + arrow_angle),
                      end_y - arrow_length * math.sin(angle + arrow_angle)), 2)

running = True
while running:
    dt = clock.tick(60) / 60

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if collided or ask_restart:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_same.collidepoint(event.pos):
                    reset_simulation()
                    started = True
                    ask_restart = False
                    collided = False
                if btn_new.collidepoint(event.pos):
                    inputs = ["", "", "", ""]
                    active = 0
                    started = False
                    ask_restart = False
                    collided = False

        elif not started:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if active < 3:
                        active += 1
                    else:
                        m_planet = float(inputs[0]) * 1000
                        m_ball = float(inputs[1])
                        vx = float(inputs[2])
                        vy = float(inputs[3])
                        reset_simulation()
                        started = True
                elif event.key == pygame.K_BACKSPACE:
                    inputs[active] = inputs[active][:-1]
                else:
                    inputs[active] += event.unicode

        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_restart.collidepoint(event.pos):
                    ask_restart = True
                if btn_random.collidepoint(event.pos):
                    m_planet = random.uniform(4, 20) * 1000
                    m_ball = random.uniform(1, 20)
                    vx = random.uniform(0, 15)
                    vy = random.uniform(-15, 15)
                    reset_simulation()
                if btn_pause.collidepoint(event.pos):
                    paused = not paused
                if btn_vectors.collidepoint(event.pos):
                    show_vectors = not show_vectors

    if started and not paused and not ask_restart and not collided:
        dx = planet_x - ball_x
        dy = planet_y - ball_y
        r = math.hypot(dx, dy)

        if r > planet_radius + ball_radius:
            F = G * m_planet * m_ball / (r * r)
            ax = F * dx / r / m_ball
            ay = F * dy / r / m_ball
            vx += ax * dt
            vy += ay * dt
        else:
            if not collided:
                collided = True
            nx = (ball_x - planet_x) / r
            ny = (ball_y - planet_y) / r
            v_n = vx * nx + vy * ny
            vx -= (1 + e) * v_n * nx
            vy -= (1 + e) * v_n * ny
            ball_x = planet_x + nx * (planet_radius + ball_radius + 1)
            ball_y = planet_y + ny * (planet_radius + ball_radius + 1)

        ball_x += vx * dt
        ball_y += vy * dt

        angle = math.atan2(ball_y - planet_y, ball_x - planet_x)
        if angle_prev is not None:
            if angle_prev < -math.pi / 2 and angle > math.pi / 2:
                orbits += 1
        angle_prev = angle
        orbit_timer += dt

    dx = planet_x - ball_x
    dy = planet_y - ball_y
    r = math.hypot(dx, dy)
    
    if r > 0:
        F_grav = G * m_planet * m_ball / (r * r)
    else:
        F_grav = 0

    kinetic = 0.5 * m_ball * (vx * vx + vy * vy)
    potential = -G * m_planet * m_ball / r if r != 0 else 0
    total_energy = kinetic + potential

    screen.fill((0, 0, 0))

    if not started:
        for i in range(4):
            t = font.render(labels[i] + ": " + inputs[i], True, (255, 255, 255))
            if i == active:
                pygame.draw.rect(screen, (120, 120, 120), (45, 45 + i * 40, 300, 30), 2)
            screen.blit(t, (50, 50 + i * 40))
        screen.blit(font.render("Enter - дальше", True, (200, 200, 200)), (50, 230))

    else:
        pygame.draw.circle(screen, (0, 0, 255), (planet_x, planet_y), planet_radius)
        pygame.draw.circle(screen, (255, 0, 0), (int(ball_x), int(ball_y)), ball_radius)

        if show_vectors and not collided:
            draw_vector(screen, (ball_x, ball_y), (vx * 5, 0), (255, 0, 0))
            
            draw_vector(screen, (ball_x, ball_y), (0, vy * 5), (0, 255, 0))
            
            if r > planet_radius + ball_radius:
                F = G * m_planet * m_ball / (r * r)
                force_x = F * dx / r / m_ball * 100
                force_y = F * dy / r / m_ball * 100
                draw_vector(screen, (ball_x, ball_y), (force_x, force_y), (0, 150, 255))
            
            vx_label = font.render(f"Vx: {vx:.1f}", True, (255, 0, 0))
            vy_label = font.render(f"Vy: {vy:.1f}", True, (0, 255, 0))
            screen.blit(vx_label, (int(ball_x + vx * 5 + 5), int(ball_y - 10)))
            screen.blit(vy_label, (int(ball_x + 5), int(ball_y + vy * 5 - 10)))

        info = [
            f"R: {r:.2f}",
            f"Vx: {vx:.2f}",
            f"Vy: {vy:.2f}",
            f"F: {F_grav:.2f}",
            f"Eк: {kinetic:.2f}",
            f"Eп: {potential:.2f}",
            f"E: {total_energy:.2f}",
            f"Обороты: {orbits}",
            f"Время: {orbit_timer:.1f}"
        ]

        for i, t in enumerate(info):
            screen.blit(font.render(t, True, (255, 255, 255)), (10, 10 + i * 18))

        if not collided:
            pygame.draw.rect(screen, (60, 60, 60), btn_restart)
            pygame.draw.rect(screen, (60, 60, 60), btn_random)
            pygame.draw.rect(screen, (60, 60, 60), btn_pause)
            pygame.draw.rect(screen, (60, 60, 60), btn_vectors)

            screen.blit(font.render("Начать заново", True, (255, 255, 255)), (btn_restart.x + 20, btn_restart.y + 8))
            screen.blit(font.render("Случайные (не воркает)", True, (255, 255, 255)), (btn_random.x + 40, btn_random.y + 8)) # не воркает
            screen.blit(font.render("Пауза" if not paused else "Продолжить", True, (255, 255, 255)),
                        (btn_pause.x + 25, btn_pause.y + 8))
            screen.blit(font.render("Скрыть вектора" if show_vectors else "Показать вектора", 
                                   True, (255, 255, 255)), (btn_vectors.x + 25, btn_vectors.y + 8))

        if collided or ask_restart:
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            
            if collided:
                coll_text = font.render("Спутник столкнулся с планетой!", True, (255, 50, 50))
                screen.blit(coll_text, (w//2 - coll_text.get_width()//2, h//2 - 80))
            
            pygame.draw.rect(screen, (80, 80, 80), btn_same)
            pygame.draw.rect(screen, (80, 80, 80), btn_new)
            screen.blit(font.render("Те же параметры", True, (255, 255, 255)),
                        (btn_same.x + 20, btn_same.y + 12))
            screen.blit(font.render("Новые параметры", True, (255, 255, 255)),
                        (btn_new.x + 20, btn_new.y + 12))

    pygame.display.flip()

pygame.quit()