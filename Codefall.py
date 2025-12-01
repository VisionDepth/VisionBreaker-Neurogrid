import pygame
import random

# Initialize Pygame
pygame.init()

# Screen Settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Matrix Code Rain - More Drops")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
BRIGHT_GREEN = (180, 255, 180)
WHITE = (255, 255, 255)

# Font Settings
FONT_SIZE = 28  # Keep it cinematic and bold
font = pygame.font.Font(pygame.font.match_font('monospace'), FONT_SIZE)

# Increase Rain Density
columns = (WIDTH // FONT_SIZE) * 2  # Double the amount of columns (more rain)
raindrops = [random.randint(-HEIGHT // FONT_SIZE, 0) for _ in range(columns)]  # Start at random heights
x_positions = [i * (FONT_SIZE // 2) for i in range(columns)]  # Reduce spacing slightly to fit more drops
speeds = [random.uniform(0.4, 1.2) for _ in range(columns)]  # Same slow cinematic movement
trail_length = 10  # Length of each rain trail

# Character Pool (English + Katakana)
char_pool = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*カタカナ"

# Transparent Surface for Trails & Effects
trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Camera Shake Variables
shake_intensity = 0
shake_duration = 0

# Function for subtle camera shake effect
def apply_camera_shake():
    global shake_intensity, shake_duration
    if shake_duration > 0:
        shake_x = random.randint(-shake_intensity, shake_intensity)
        shake_y = random.randint(-shake_intensity, shake_intensity)
        screen.scroll(shake_x, shake_y)
        shake_duration -= 1

# Main Loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)  # Clear screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    # Apply subtle camera shake effect
    apply_camera_shake()

    # Draw fading trail effect
    trail_surface.fill((0, 0, 0, 30))  # Stronger fade effect for glowing trails
    screen.blit(trail_surface, (0, 0))

    for i, x in enumerate(x_positions):
        y = int(raindrops[i] * FONT_SIZE)

        # Generate a random character
        char = random.choice(char_pool)

        # Leading character with glitch flicker effect
        if random.random() > 0.97:  # 3% chance of glitch flicker
            text_color = WHITE  # Bright flash effect
        elif random.random() > 0.98:  # Neo's Awakening (morph effect)
            char = random.choice("101010101010")  # Transform into binary briefly
            text_color = BRIGHT_GREEN
        else:
            text_color = BRIGHT_GREEN if random.random() > 0.98 else GREEN

        text = font.render(char, True, text_color)
        screen.blit(text, (x, y))

        # Add trailing effect (streaks of dark green)
        for t in range(trail_length):
            trail_y = y - (t * FONT_SIZE)
            if trail_y > 0:
                trail_char = random.choice(char_pool) if random.random() > 0.5 else char
                trail_text = font.render(trail_char, True, DARK_GREEN)
                trail_surface.blit(trail_text, (x, trail_y))

        # Move character down with varied slower speed
        raindrops[i] += speeds[i]

        # Randomly trigger camera shake effect
        if random.random() > 0.995:  # 0.5% chance of triggering shake
            shake_intensity = random.randint(1, 3)
            shake_duration = random.randint(10, 20)

        # Reset drop randomly at different heights
        if y > HEIGHT and random.random() > 0.90:
            raindrops[i] = random.randint(-10, 0)
            speeds[i] = random.uniform(0.4, 1.2)

    pygame.display.flip()
    clock.tick(30)  # Control frame rate

pygame.quit()

