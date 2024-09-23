import pygame # type: ignore
import sys
import random

# Initialize PyGame
pygame.init()

# Set up the game window
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Advanced Shooter Game with Enemy Shooting")

# Set the frame rate
clock = pygame.time.Clock()

# Player settings
player_width = 50
player_height = 60
player_x = screen_width // 2 - player_width // 2
player_y = screen_height // 2 - player_height // 2
player_speed = 5

# Bullet settings
bullet_width = 5
bullet_height = 10
bullet_speed = 7
bullets = []

# Bullet cooldown (to avoid spamming bullets)
bullet_cooldown = 500  # milliseconds
last_bullet_time = 0

# Enemy settings
enemy_width = 50
enemy_height = 60
enemy_speed = 2
enemies = []

# Enemy bullet settings
enemy_bullet_width = 5
enemy_bullet_height = 10
enemy_bullet_speed = 5
enemy_bullets = []

# Enemy shooting cooldown
enemy_bullet_cooldown = 1000  # milliseconds

# Enemy spawn time and timer
enemy_timer = 0
enemy_spawn_time = 2000  # milliseconds

# Explosion settings
explosions = []
explosion_duration = 200  # milliseconds

# Score and Health
score = 0
health = 3
font = pygame.font.Font(None, 36)

# Collision detection function
def check_collision(rect1, rect2):
    return pygame.Rect(rect1).colliderect(pygame.Rect(rect2))

# Main game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Handle player movement (in all directions)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
        player_x += player_speed
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < screen_height - player_height:
        player_y += player_speed

    # Handle bullet firing with cooldown
    current_time = pygame.time.get_ticks()
    if keys[pygame.K_SPACE] and current_time - last_bullet_time > bullet_cooldown:
        # Determine bullet direction based on movement
        bullet_dx, bullet_dy = 0, 0
        if keys[pygame.K_LEFT]:
            bullet_dx = -bullet_speed
        elif keys[pygame.K_RIGHT]:
            bullet_dx = bullet_speed
        if keys[pygame.K_UP]:
            bullet_dy = -bullet_speed
        elif keys[pygame.K_DOWN]:
            bullet_dy = bullet_speed
        
        if bullet_dx == 0 and bullet_dy == 0:
            bullet_dy = -bullet_speed  # Default to shooting upwards if no movement
        
        # Create a bullet
        bullet_x = player_x + player_width // 2 - bullet_width // 2
        bullet_y = player_y + player_height // 2 - bullet_height // 2
        bullets.append([bullet_x, bullet_y, bullet_dx, bullet_dy])
        last_bullet_time = current_time

    # Update bullet positions
    for bullet in bullets:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]
    bullets = [bullet for bullet in bullets if 0 < bullet[0] < screen_width and 0 < bullet[1] < screen_height]

    # Update enemy positions and spawn new ones
    if current_time - enemy_timer > enemy_spawn_time:
        enemy_x = random.randint(0, screen_width - enemy_width)
        enemy_y = -enemy_height
        enemies.append([enemy_x, enemy_y, current_time])  # Track spawn time for shooting
        enemy_timer = current_time

    for enemy in enemies:
        enemy[1] += enemy_speed

        # Make enemies shoot bullets periodically
        if current_time - enemy[2] > enemy_bullet_cooldown:
            enemy_bullet_x = enemy[0] + enemy_width // 2 - enemy_bullet_width // 2
            enemy_bullet_y = enemy[1] + enemy_height
            enemy_bullets.append([enemy_bullet_x, enemy_bullet_y])
            enemy[2] = current_time  # Reset enemy shooting timer

    # Update enemy bullet positions
    for enemy_bullet in enemy_bullets:
        enemy_bullet[1] += enemy_bullet_speed
    enemy_bullets = [enemy_bullet for enemy_bullet in enemy_bullets if enemy_bullet[1] < screen_height]

    # Check for player collision with enemy bullets
    for enemy_bullet in enemy_bullets[:]:
        if check_collision((enemy_bullet[0], enemy_bullet[1], enemy_bullet_width, enemy_bullet_height),
                           (player_x, player_y, player_width, player_height)):
            enemy_bullets.remove(enemy_bullet)
            health -= 1
            if health <= 0:
                pygame.quit()
                sys.exit()

    # Check for collisions between player bullets and enemies
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if check_collision((bullet[0], bullet[1], bullet_width, bullet_height),
                               (enemy[0], enemy[1], enemy_width, enemy_height)):
                bullets.remove(bullet)
                enemies.remove(enemy)
                explosions.append((enemy[0], enemy[1], current_time))  # Add explosion at the collision point
                score += 1
                break

    # Remove enemies that are off the screen
    enemies = [enemy for enemy in enemies if enemy[1] < screen_height]

    # Remove explosions after their duration
    explosions = [explosion for explosion in explosions if current_time - explosion[2] < explosion_duration]

    # Fill the screen with black
    screen.fill((0, 0, 0))

    # Draw the player
    pygame.draw.rect(screen, (0, 128, 255), (player_x, player_y, player_width, player_height))

    # Draw the bullets
    for bullet in bullets:
        pygame.draw.rect(screen, (255, 255, 255), (bullet[0], bullet[1], bullet_width, bullet_height))

    # Draw the enemies
    for enemy in enemies:
        pygame.draw.rect(screen, (255, 0, 0), (enemy[0], enemy[1], enemy_width, enemy_height))

    # Draw the enemy bullets
    for enemy_bullet in enemy_bullets:
        pygame.draw.rect(screen, (255, 255, 0), (enemy_bullet[0], enemy_bullet[1], enemy_bullet_width, enemy_bullet_height))

    # Draw the explosions (flame effect)
    for explosion in explosions:
        pygame.draw.circle(screen, (255, 69, 0), (explosion[0] + enemy_width // 2, explosion[1] + enemy_height // 2), 30)

    # Display the score and health
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    
    health_text = font.render(f"Health: {health}", True, (255, 255, 255))
    screen.blit(health_text, (10, 40))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate at 60 FPS
    clock.tick(60)
