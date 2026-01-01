import pygame
import random
import math
import sys

pygame.init()
WIDTH, HEIGHT = 900, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

clock = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 22)

# Colors
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255,255,0)
BLUE = (0,150,255)
BLACK = (0,0,0)

# Gameplay values
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 2
SHOOTER_SPEED = 1.5
BOSS_SPEED = 1
AUTO_FIRE = True

# Player
player_img = pygame.Surface((50,40), pygame.SRCALPHA)
pygame.draw.polygon(player_img, BLUE, [(0,40),(50,20),(0,0)])
player = pygame.Rect(WIDTH//2, HEIGHT//2, 50, 40)
player_health = 100
score = 0
shield_active = False
shield_timer = 0
rapid_fire = False
rapid_timer = 0

bullets = []
enemies = []
enemy_bullets = []
powerups = []
boss = None
boss_health = 400
spawn_boss_score = 150

def draw_health_bar(entity_rect, hp, max_hp, offset= -10):
    ratio = hp / max_hp
    pygame.draw.rect(WIN, RED, (entity_rect.x, entity_rect.y + offset, entity_rect.width, 7))
    pygame.draw.rect(WIN, GREEN, (entity_rect.x, entity_rect.y + offset, entity_rect.width * ratio, 7))

def spawn_enemy():
    t = random.choice(["normal","shooter"])
    x = random.choice([0, WIDTH])
    y = random.randint(50, HEIGHT-50)
    enemies.append({"rect": pygame.Rect(x,y,40,40),"type":t,"health":40 if t=="normal" else 60})

def spawn_powerup():
    p_type = random.choice(["shield","heal","rapid"])
    rect = pygame.Rect(random.randint(50,WIDTH-50), random.randint(50,HEIGHT-50),25,25)
    powerups.append({"rect":rect,"type":p_type})

def spawn_boss():
    global boss, boss_health
    boss_health = 400
    boss = pygame.Rect(WIDTH//2-120, 40, 240, 80)

def shoot():
    mx, my = pygame.mouse.get_pos()
    angle = math.atan2(my - player.centery, mx - player.centerx)
    dx = math.cos(angle) * BULLET_SPEED
    dy = math.sin(angle) * BULLET_SPEED
    bullets.append({"rect":pygame.Rect(player.centerx, player.centery,8,4),"dx":dx,"dy":dy})

def enemy_shoot(enemy):
    angle = math.atan2(player.centery - enemy["rect"].centery, player.centerx - enemy["rect"].centerx)
    dx = math.cos(angle) * 6
    dy = math.sin(angle) * 6
    enemy_bullets.append({"rect":pygame.Rect(enemy["rect"].centerx, enemy["rect"].centery,6,3),"dx":dx,"dy":dy})

shoot_timer = 0
enemy_spawn_timer = 0
enemy_shoot_timer = 0
powerup_timer = 0

run = True
while run:
    dt = clock.tick(60)
    WIN.fill((10,10,25))

    # Input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player.y > 0: player.y -= PLAYER_SPEED
    if keys[pygame.K_s] and player.y < HEIGHT-player.height: player.y += PLAYER_SPEED
    if keys[pygame.K_a] and player.x > 0: player.x -= PLAYER_SPEED
    if keys[pygame.K_d] and player.x < WIDTH-player.width: player.x += PLAYER_SPEED

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                AUTO_FIRE = not AUTO_FIRE
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not AUTO_FIRE:
                shoot()

    # Shooting
    shoot_timer += 1
    if AUTO_FIRE:
        if rapid_fire:
            if shoot_timer > 8:
                shoot()
                shoot_timer = 0
        else:
            if shoot_timer > 18:
                shoot()
                shoot_timer = 0

    # Bullet movement
    for b in bullets[:]:
        b["rect"].x += b["dx"]
        b["rect"].y += b["dy"]
        if not WIN.get_rect().contains(b["rect"]):
            bullets.remove(b)

    # Enemy spawn
    enemy_spawn_timer += 1
    if enemy_spawn_timer > 50:
        spawn_enemy()
        enemy_spawn_timer = 0

    # Powerups spawn
    powerup_timer += 1
    if powerup_timer > 400:
        spawn_powerup()
        powerup_timer = 0

    # Enemy logic
    enemy_shoot_timer += 1
    for e in enemies[:]:
        if e["type"]=="normal":
            direction = pygame.Vector2(player.center) - pygame.Vector2(e["rect"].center)
            if direction.length() != 0:
                direction = direction.normalize() * ENEMY_SPEED
            e["rect"].move_ip(direction)
        else:
            direction = pygame.Vector2(player.center) - pygame.Vector2(e["rect"].center)
            if direction.length()!=0:
                direction=direction.normalize()*SHOOTER_SPEED
            e["rect"].move_ip(direction)
            if enemy_shoot_timer>50:
                enemy_shoot(e)
                enemy_shoot_timer=0

        # Enemy hit by bullet
        for b in bullets[:]:
            if e["rect"].colliderect(b["rect"]):
                e["health"] -= 20
                bullets.remove(b)
                if e["health"]<=0:
                    enemies.remove(e)
                    score += 10
                    break

        # Collision with player
        if e in enemies and e["rect"].colliderect(player):
            if not shield_active:
                player_health -= 10
            enemies.remove(e)

    # Enemy bullets
    for eb in enemy_bullets[:]:
        eb["rect"].x += eb["dx"]
        eb["rect"].y += eb["dy"]
        if eb["rect"].colliderect(player):
            if not shield_active:
                player_health -= 10
            enemy_bullets.remove(eb)
        elif not WIN.get_rect().contains(eb["rect"]):
            enemy_bullets.remove(eb)

    # Boss
    if score >= spawn_boss_score and boss is None:
        spawn_boss()

    if boss:
        boss.x += math.sin(pygame.time.get_ticks()*0.002)*2
        draw_health_bar(boss,boss_health,400, +85)

        for b in bullets[:]:
            if boss.colliderect(b["rect"]):
                boss_health -= 5
                bullets.remove(b)
                if boss_health<=0:
                    boss=None
                    score += 100

        if boss and boss.colliderect(player):
            if not shield_active:
                player_health -= 20

    # Powerups pickup
    for p in powerups[:]:
        if p["rect"].colliderect(player):
            if p["type"]=="shield":
                shield_active=True
                shield_timer=180
            elif p["type"]=="heal":
                player_health=min(100,player_health+30)
            elif p["type"]=="rapid":
                rapid_fire=True
                rapid_timer=300
            powerups.remove(p)

    # Timers
    if shield_active:
        shield_timer-=1
        if shield_timer<=0:
            shield_active=False

    if rapid_fire:
        rapid_timer-=1
        if rapid_timer<=0:
            rapid_fire=False

    # Draw Player
    rotated = player_img.copy()
    mx,my = pygame.mouse.get_pos()
    angle = math.degrees(math.atan2(my-player.centery, mx-player.centerx))
    rotated = pygame.transform.rotate(player_img, -angle)
    WIN.blit(rotated, rotated.get_rect(center=player.center))

    # Visual shield
    if shield_active:
        pygame.draw.circle(WIN, YELLOW, player.center, 45,2)

    # Draw Bullets
    for b in bullets:
        pygame.draw.rect(WIN, WHITE, b["rect"])

    for e in enemies:
        pygame.draw.rect(WIN, RED if e["type"]=="normal" else YELLOW, e["rect"])
        draw_health_bar(e["rect"], e["health"], 60)

    for eb in enemy_bullets:
        pygame.draw.rect(WIN, YELLOW, eb["rect"])

    for p in powerups:
        color = BLUE if p["type"]=="shield" else GREEN if p["type"]=="heal" else YELLOW
        pygame.draw.rect(WIN,color,p["rect"])

    if boss:
        pygame.draw.rect(WIN,(200,0,200),boss)

    # UI
    health_text = FONT.render(f"Health: {player_health}", True, WHITE)
    score_text = FONT.render(f"Score: {score}", True, WHITE)
    mode_text = FONT.render(f"Mode: {'Auto Fire' if AUTO_FIRE else 'Manual'} (SPACE toggle)", True, WHITE)

    WIN.blit(health_text,(10,10))
    WIN.blit(score_text,(10,35))
    WIN.blit(mode_text,(10,60))

    if player_health<=0:
        over = FONT.render("GAME OVER - Close Window to Exit",True,RED)
        WIN.blit(over,(WIDTH//2-120, HEIGHT//2))
    
    pygame.display.update()

pygame.quit()
sys.exit()
