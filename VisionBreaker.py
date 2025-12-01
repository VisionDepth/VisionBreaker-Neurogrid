import pygame
import random
import os
import sys

# ================== INIT ==================
pygame.init()
pygame.mixer.init()

# ---- Audio setup ----
ASSET_DIR = "assets"
MUSIC_FILE = os.path.join(ASSET_DIR, "codefall_ambience.ogg")
SFX_HACK_FILE = os.path.join(ASSET_DIR, "hack_confirm.wav")
SFX_BINARY_FILE = os.path.join(ASSET_DIR, "binary_toggle.wav")
SFX_ERROR_FILE = os.path.join(ASSET_DIR, "critical_error.wav")

music_loaded = False
sfx_hack = None
sfx_binary = None
sfx_error = None


def init_audio():
    """Try to load music and SFX; fail gracefully if files aren't there."""
    global music_loaded, sfx_hack, sfx_binary, sfx_error

    # Background music
    try:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)  # loop forever
        music_loaded = True
    except Exception:
        music_loaded = False

    # Hack confirm SFX
    try:
        sfx_hack = pygame.mixer.Sound(SFX_HACK_FILE)
        sfx_hack.set_volume(0.6)
    except Exception:
        sfx_hack = None

    # Binary toggle SFX
    try:
        sfx_binary = pygame.mixer.Sound(SFX_BINARY_FILE)
        sfx_binary.set_volume(0.5)
    except Exception:
        sfx_binary = None

    # Critical error SFX
    try:
        sfx_error = pygame.mixer.Sound(SFX_ERROR_FILE)
        sfx_error.set_volume(0.7)
    except Exception:
        sfx_error = None


# ---- Dynamic screen + fullscreen handling ----
DEFAULT_WINDOW_SIZE = (800, 600)
info = pygame.display.Info()
FULLSCREEN_SIZE = (info.current_w, info.current_h)

# Start in fullscreen
fullscreen = True
WIDTH, HEIGHT = FULLSCREEN_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("VisionBreaker: Neurogrid Terminal |  mode={game_mode}  hack={hack_input_mode}")

# Font Settings
FONT_SIZE = 28
font = pygame.font.Font(pygame.font.match_font("monospace"), FONT_SIZE)
big_font = pygame.font.Font(pygame.font.match_font("monospace"), 48)

# Character Pool (English + Katakana)
char_pool = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*カタカナ"

# Special words that occasionally rain down as vertical strings
SPECIAL_WORDS = [
    # Core identity
    "VISIONBREAKER",
    "NEUROGRID TERMINAL",
    "GRID ONLINE",
    "GRID BREACH",
    "NEURAL LINK",

    # Theme-flavored
    "EMERALD STREAM",
    "RED ALERT",
    "SYNTHWAVE CASCADE",

    # Trace / security vibe
    "TRACE RISING",
    "TRACE SUPPRESSED",
    "TRACE NEUTRALIZED",
    "INTRUSION DETECTED",
    "ACCESS GRANTED",
    "ACCESS DENIED",
    "OVERRIDE ACCEPTED",

    # Signal / data flavor
    "SIGNAL BREACH",
    "GHOST SIGNAL",
    "PACKET STORM",
    "LINK ESTABLISHED",
    "CONNECTION LOST",
    "NODE COMPROMISED",

    # Glitchy system stuff
    "CORE GLITCH",
    "SYSTEM FAULT",
    "KERNEL PANIC",
]


# Color themes
COLOR_THEMES = [
    {
        "name": "Emerald Stream",
        "bg": (0, 0, 0),
        "main": (0, 255, 0),
        "trail": (0, 100, 0),
        "bright": (180, 255, 180),
        "flash": (255, 255, 255),
    },
    {  
        "name": "Red Alert",
        "bg": (5, 0, 0),
        "main": (255, 40, 40),
        "trail": (120, 0, 0),
        "bright": (255, 150, 150),
        "flash": (255, 255, 255),
    },
    {  
        "name": "Synthwave",
        "bg": (5, 0, 20),
        "main": (255, 0, 255),
        "trail": (80, 0, 120),
        "bright": (255, 150, 255),
        "flash": (255, 255, 255),
    },

    # 4) Neon cyan grid
    {
        "name": "Neon Circuit",
        "bg": (0, 4, 12),
        "main": (0, 255, 200),
        "trail": (0, 120, 100),
        "bright": (180, 255, 240),
        "flash": (255, 255, 255),
    },

    # 5) Amber warning tones
    {
        "name": "Amber Warning",
        "bg": (10, 3, 0),
        "main": (255, 180, 0),
        "trail": (150, 80, 0),
        "bright": (255, 230, 150),
        "flash": (255, 255, 255),
    },

    # 6) Icy scan blue
    {
        "name": "Glacial Scan",
        "bg": (0, 8, 20),
        "main": (120, 200, 255),
        "trail": (40, 90, 140),
        "bright": (200, 240, 255),
        "flash": (255, 255, 255),
    },

    # 7) Purple glitch
    {
        "name": "Violet Static",
        "bg": (8, 0, 16),
        "main": (200, 120, 255),
        "trail": (90, 40, 140),
        "bright": (235, 190, 255),
        "flash": (255, 255, 255),
    },

    # 8) Soft ghostly green
    {
        "name": "Ghost Signal",
        "bg": (0, 0, 0),
        "main": (120, 255, 200),
        "trail": (40, 120, 90),
        "bright": (210, 255, 230),
        "flash": (255, 255, 255),
    },

    # 9) Solar orange blast
    {
        "name": "Solar Flare",
        "bg": (10, 0, 0),
        "main": (255, 120, 0),
        "trail": (140, 40, 0),
        "bright": (255, 210, 150),
        "flash": (255, 255, 255),
    },
]

theme_index = 0
current_theme = COLOR_THEMES[theme_index]
unlocked_themes = 1


# These will be initialized in init_surfaces()
columns = 0
raindrops = []
x_positions = []
speeds = []
trail_length = 10
trail_surface = None
scene_surface = None
error_overlay = None

# Camera shake
shake_intensity = 0
shake_timer = 0

# Global speed multiplier
base_speed_factor = 1.0
slow_mo = False  # bullet-time toggle
binary_mode = False  # all 0/1 mode

# ==== PUZZLE MODE STATE ====
game_mode = "free"  # "free" or "puzzle"

puzzles = [
    {
        "prompt": "ACCESS PHRASE: SEE BEYOND THE SURFACE (ONE WORD, THINK 'DEEP UNDERSTANDING')",
        "answer": "INSIGHT",
    },
    {
        "prompt": "ACCESS CODE SEQUENCE: 2 4 8 16 ? (PATTERN: EACH VALUE DOUBLES)",
        "answer": "32",
    },
    {
        "prompt": "DECRYPT: OPPOSITE OF 'NOISE' (ONE WORD, THINK SIGNAL PROCESSING)",
        "answer": "SIGNAL",
    },
    {
        "prompt": "CORE OVERRIDE KEYWORD (THE MAIN TITLE WORD IN ALL CAPS)",
        "answer": "VISIONBREAKER",
    },
    {
        "prompt": "LOGIC SEQUENCE: 1 3 6 10 15 ? (ADD 2,3,4,5,6...)",
        "answer": "21",
    },
    {
        "prompt": "SYSTEM MODEL: INPUT -> PROCESS -> ______",
        "answer": "OUTPUT",
    },
    {
        "prompt": "CONVERT: BINARY 1010 = ? (DECIMAL)",
        "answer": "10",
    },
    {
        "prompt": "IDENT VERIFY: NAME THE TERMINAL (ONE WORD FROM TITLE, COLORFUL ONE)",
        "answer": "SPECTRAL",
    },
]


current_puzzle_index = 0
puzzle_message = ""  # text shown for current puzzle / status

# TRACE system
trace_level = 0.0
trace_max = 100.0
trace_active = False

# Game state
running = True
paused = False
clock = pygame.time.Clock()

# Smaller control overlay font so it does not crowd the screen
ui_font = pygame.font.SysFont("consolas", 12)
# Bigger, more prominent font just for the HACK> console
hack_font = pygame.font.SysFont("consolas", 28)

# Special vertical word rain effects
# list of dicts: {"x", "y", "letters", "speed"}
word_rains = []

# Hack console input
hack_input_mode = False
hack_buffer = ""

# Critical error state
critical_error_timer = 0
critical_glitch_intensity = 0


def init_surfaces():
    """Initialize / rebuild surfaces and rain columns when screen size changes."""
    global trail_surface, scene_surface, error_overlay
    global columns, raindrops, x_positions, speeds, word_rains

    trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    scene_surface = pygame.Surface((WIDTH, HEIGHT))
    error_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # Rebuild rain columns to fill the new resolution
    columns = (WIDTH // FONT_SIZE) * 2
    raindrops = [random.randint(-HEIGHT // FONT_SIZE, 0) for _ in range(columns)]
    x_positions = [i * (FONT_SIZE // 2) for i in range(columns)]
    speeds = [random.uniform(0.4, 1.2) for _ in range(columns)]

    # Clear word rains when resizing so they do not get weird positions
    word_rains.clear()


def trigger_shake(intensity=3, duration=20):
    """Start a camera shake."""
    global shake_intensity, shake_timer
    shake_intensity = intensity
    shake_timer = duration


def get_shake_offset():
    """Return current shake offset."""
    global shake_timer
    if shake_timer > 0:
        shake_timer -= 1
        return (
            random.randint(-shake_intensity, shake_intensity),
            random.randint(-shake_intensity, shake_intensity),
        )
    return 0, 0


def next_theme():
    """Cycle to the next unlocked color theme."""
    global theme_index, current_theme
    if unlocked_themes <= 0:
        return
    theme_index = (theme_index + 1) % unlocked_themes
    current_theme = COLOR_THEMES[theme_index]


def toggle_fullscreen():
    """Toggle between fullscreen and windowed 800x600."""
    global fullscreen, screen, WIDTH, HEIGHT
    fullscreen = not fullscreen
    if fullscreen:
        WIDTH, HEIGHT = FULLSCREEN_SIZE
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        WIDTH, HEIGHT = DEFAULT_WINDOW_SIZE
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    init_surfaces()


def spawn_word_rain():
    """Spawn a vertical word cascade in a random column from SPECIAL_WORDS."""
    word = random.choice(SPECIAL_WORDS)
    spawn_word_rain_from_text(word)


def spawn_word_rain_from_text(text):
    """Spawn a vertical word cascade using the given text."""
    text = text.strip()
    if not text:
        return
    letters = list(text.upper())
    col_index = random.randrange(len(x_positions))
    x = x_positions[col_index]
    start_y = -len(letters) * FONT_SIZE
    word_rains.append(
        {
            "x": x,
            "y": start_y,
            "letters": letters,
            "speed": random.uniform(1.5, 3.0),
        }
    )


def draw_word_rains(surface, effective_speed):
    """Draw and update special vertical word rains."""
    to_remove = []
    for i, wr in enumerate(word_rains):
        x = wr["x"]
        y_top = wr["y"]
        letters = wr["letters"]

        # Draw each letter top to bottom
        for idx, ch in enumerate(letters):
            y = y_top + idx * FONT_SIZE
            if y > HEIGHT:
                continue

            # skip rendering spaces but keep vertical spacing
            if ch == " ":
                continue

            # Make word rains pop: bright or flash color
            if random.random() > 0.9:
                color = current_theme["flash"]
            else:
                color = current_theme["bright"]

            text = font.render(ch, True, color)
            surface.blit(text, (x, y))

        # Move the whole word rain down
        wr["y"] += wr["speed"] * effective_speed

        # Remove once it fully moved past bottom
        if wr["y"] - len(letters) * FONT_SIZE > HEIGHT:
            to_remove.append(i)

    # Remove in reverse so indices stay valid
    for i in reversed(to_remove):
        del word_rains[i]


def trigger_critical_error():
    """Start a critical error event with red glitch and system failure text."""
    global critical_error_timer, critical_glitch_intensity
    global game_mode, puzzle_message, hack_input_mode, hack_buffer
    global trace_level, trace_active

    critical_error_timer = 180  # ~6 seconds at 30fps
    critical_glitch_intensity = 6
    trigger_shake(intensity=critical_glitch_intensity, duration=critical_error_timer)

    # Leave puzzle mode on failure
    if game_mode == "puzzle":
        game_mode = "free"
        puzzle_message = "TRACE FAILED"
        hack_input_mode = False
        hack_buffer = ""

    # Reset trace when error hits
    trace_level = 0.0
    trace_active = False

    # Play critical error SFX if available
    if sfx_error is not None:
        sfx_error.play()


def apply_critical_error_overlay(surface):
    """Apply red tint plus glitch lines plus SYSTEM FAILURE while timer is active."""
    global critical_error_timer
    if critical_error_timer <= 0:
        return

    critical_error_timer -= 1

    # Red tint overlay
    error_overlay.fill((255, 0, 0, 80))
    surface.blit(error_overlay, (0, 0))

    # Random horizontal glitch lines
    for _ in range(8):
        y = random.randint(0, HEIGHT)
        width = random.randint(WIDTH // 4, WIDTH)
        x = random.randint(-WIDTH // 4, WIDTH)
        pygame.draw.rect(surface, (255, 0, 0), (x, y, width, 2))

    # Big SYSTEM FAILURE text
    text = big_font.render("SYSTEM FAILURE", True, current_theme["flash"])
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    surface.blit(text, rect)


# ==== PUZZLE MODE LOGIC ====
def start_puzzle_mode():
    """Enter puzzle mode and prepare the first puzzle."""
    global game_mode, current_puzzle_index, puzzle_message, hack_input_mode, hack_buffer
    global trace_level, trace_active

    game_mode = "puzzle"
    current_puzzle_index = 0
    puzzle_message = puzzles[current_puzzle_index]["prompt"]
    hack_input_mode = True
    hack_buffer = ""

    # start trace bar
    trace_level = 0.0
    trace_active = True


def give_puzzle_hint():
    """Show a hint for the current puzzle and increase trace."""
    global puzzle_message, trace_level

    hint = puzzles[current_puzzle_index].get("hint")
    if not hint:
        return

    puzzle_message = f"{puzzles[current_puzzle_index]['prompt']}  // HINT: {hint}"
    trace_level = min(trace_max, trace_level + 25.0)


def handle_puzzle_answer(answer_str):
    """Check the player's answer for the current puzzle."""
    global current_puzzle_index, game_mode, puzzle_message, hack_input_mode, hack_buffer
    global trace_level, trace_active, unlocked_themes

    answer = answer_str.strip().upper()
    current = puzzles[current_puzzle_index]
    correct = current["answer"].upper()

    if answer == correct:
        # Correct answer
        spawn_word_rain_from_text("ACCESS GRANTED")
        if sfx_hack is not None:
            sfx_hack.play()

        # Move to next puzzle index (number solved so far)
        current_puzzle_index += 1

        # ---------- THEME UNLOCK LOGIC ----------
        # You start with 1 theme unlocked (index 0).
        # After solving N puzzles, you should have 1 + N themes unlocked,
        # up to the total number of COLOR_THEMES.
        solved = current_puzzle_index
        desired_unlocked = min(1 + solved, len(COLOR_THEMES))

        if desired_unlocked > unlocked_themes:
            # Unlock each new theme between old and new counts
            for theme_idx in range(unlocked_themes, desired_unlocked):
                theme_name = COLOR_THEMES[theme_idx]["name"].upper()
                spawn_word_rain_from_text(f"THEME UNLOCKED: {theme_name}")
            unlocked_themes = desired_unlocked
        # ---------- END THEME UNLOCK LOGIC ----------

        # All puzzles solved?
        if current_puzzle_index >= len(puzzles):
            spawn_word_rain_from_text("TRACE NEUTRALIZED")
            puzzle_message = "TRACE NEUTRALIZED"
            game_mode = "free"
            hack_input_mode = False
            hack_buffer = ""
            trace_level = 0.0
            trace_active = False
        else:
            # Next puzzle: reset trace for new round
            puzzle_message = puzzles[current_puzzle_index]["prompt"]
            hack_input_mode = True
            hack_buffer = ""
            trace_level = 0.0
            trace_active = True

    else:
        # Wrong answer -> critical failure
        spawn_word_rain_from_text("ACCESS DENIED")
        trigger_critical_error()



def draw_ui_overlay(surface):
    """Draw small text with controls and theme name plus hack console."""
    speed_label = f"{base_speed_factor:.1f}x"
    mode_flags = []
    if slow_mo:
        mode_flags.append("Slow-mo")
    if binary_mode:
        mode_flags.append("Binary")
    if game_mode == "puzzle":
        mode_flags.append("Puzzle")
    if hack_input_mode:
        mode_flags.append("Hack")

    flag_str = f" ({' / '.join(mode_flags)})" if mode_flags else ""

    # Window caption reflects mode
    pygame.display.set_caption(
        f"Neurogrid: Codefall  |  mode={game_mode}  hack={hack_input_mode}"
    )


    lines = [
        f"Theme: {current_theme['name']}  (Unlocked {unlocked_themes}/{len(COLOR_THEMES)})",
        f"Speed: {speed_label}{flag_str}",
        "C - Theme   Space - Pause",
        "Up/Down - Speed   B - Slow-mo   N - Binary",
        "H - Hack console   P - Puzzle mode",
        "E - Critical error   S - Shake   F11 - Fullscreen",
        "Esc - Quit / Exit hack",
    ]
    y = 6
    for line in lines:
        text_surf = ui_font.render(line, True, (200, 200, 200))
        surface.blit(text_surf, (8, y))
        y += 14

    # Optional extra line about hints while in puzzle mode
    if game_mode == "puzzle":
        hint_line = "Puzzle mode: type HINT in the console for a clue (costs trace)"
        text_surf = ui_font.render(hint_line, True, (200, 200, 200))
        surface.blit(text_surf, (8, y))
        y += 14

    # Show puzzle prompt if in puzzle mode
    if game_mode == "puzzle" and puzzle_message:
        puzzle_surf = ui_font.render(
            f"PUZZLE {current_puzzle_index + 1}/{len(puzzles)}: {puzzle_message}",
            True,
            current_theme["bright"],
        )
        rect = puzzle_surf.get_rect()
        rect.midbottom = (WIDTH // 2, HEIGHT - 60)
        surface.blit(puzzle_surf, rect)

    # TRACE bar (top right) only in puzzle mode
    if game_mode == "puzzle":
        bar_width = WIDTH // 4
        bar_height = 12
        margin = 10
        bar_x = WIDTH - bar_width - margin
        bar_y = margin + 8

        # background
        pygame.draw.rect(surface, (30, 30, 30), (bar_x, bar_y, bar_width, bar_height))

        # filled portion
        fill_ratio = max(0.0, min(1.0, trace_level / trace_max))
        fill_w = int(bar_width * fill_ratio)
        if fill_w > 0:
            pygame.draw.rect(surface, (255, 80, 40), (bar_x, bar_y, fill_w, bar_height))

        # border
        pygame.draw.rect(
            surface, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1
        )

        # label just above bar
        label = ui_font.render(
            f"TRACE {int(trace_level):03d}/{int(trace_max):03d}",
            True,
            (200, 200, 200),
        )
        label_rect = label.get_rect()
        label_rect.bottomright = (bar_x + bar_width, bar_y - 2)
        surface.blit(label, label_rect)

    # Hack console input shown at bottom when active
    if hack_input_mode:
        prompt = f"HACK> {hack_buffer}_"
        text_surf = hack_font.render(prompt, True, current_theme["bright"])
        rect = text_surf.get_rect()
        rect.topleft = (8, HEIGHT - rect.height - 12)

        # Semi-transparent bar behind the console so it stands out
        console_bg = pygame.Surface((rect.width + 16, rect.height + 8), pygame.SRCALPHA)
        console_bg.fill((0, 0, 0, 160))
        surface.blit(console_bg, (rect.x - 8, rect.y - 4))

        surface.blit(text_surf, rect)


# ==== BOOT SCREEN WITH RED / BLUE PILL ====
def show_boot_screen():
    boot_font = pygame.font.SysFont("consolas", 24)
    small_font = pygame.font.SysFont("consolas", 18)

    boot_lines = [
        "BOOT SEQUENCE - NEUROGRID TERMINAL",
        "SCANNING UPLINK...",
        "HANDSHAKE ESTABLISHED",
        "LOADING CODEFALL ENGINE...",
        "TRACE SUPPRESSION ONLINE",
    ]


    boot_buffer = ""
    revealed_lines = 0
    last_reveal_time = 0
    reveal_interval = 550  # ms per line

    boot_running = True
    local_clock = pygame.time.Clock()

    while boot_running:
        dt = local_clock.tick(60)
        last_reveal_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_RETURN:
                    norm = " ".join(boot_buffer.strip().lower().split())
                    if norm in ("awaken",):
                        boot_running = False   # enter the game
                    elif norm in ("sleep",):
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_BACKSPACE:
                    boot_buffer = boot_buffer[:-1]
                else:
                    if event.unicode and event.unicode.isprintable():
                        boot_buffer += event.unicode

        if revealed_lines < len(boot_lines) and last_reveal_time >= reveal_interval:
            revealed_lines += 1
            last_reveal_time = 0

        screen.fill((0, 0, 0))

        # Draw boot lines
        y = HEIGHT // 3
        for i in range(revealed_lines):
            text_surf = boot_font.render(boot_lines[i], True, (0, 255, 0))
            rect = text_surf.get_rect(center=(WIDTH // 2, y))
            screen.blit(text_surf, rect)
            y += 32

        if revealed_lines == len(boot_lines):
            # Choice text
            prompt1 = "TYPE 'AWAKEN' TO JACK INTO THE NEUROGRID"
            prompt2 = "TYPE 'SLEEP' TO ABORT CONNECTION"
            p1_surf = small_font.render(prompt1, True, (0, 255, 0))
            p2_surf = small_font.render(prompt2, True, (0, 255, 0))
            p1_rect = p1_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            p2_rect = p2_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 90))
            screen.blit(p1_surf, p1_rect)
            screen.blit(p2_surf, p2_rect)

            # Input line
            label_surf = small_font.render("CHOICE>", True, (0, 255, 0))
            screen.blit(label_surf, (WIDTH // 2 - 220, HEIGHT // 2 + 130))

            choice_surf = small_font.render(boot_buffer + "_", True, (0, 255, 0))
            screen.blit(choice_surf, (WIDTH // 2 - 120, HEIGHT // 2 + 130))

        pygame.display.flip()


# ============= BOOTSTRAP =============
init_surfaces()
init_audio()
show_boot_screen()

while running:
    # One tick per frame
    dt_ms = clock.tick(30)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # While in hack console mode, intercept most keys for typing
            if hack_input_mode and event.key not in (pygame.K_ESCAPE,):
                if event.key == pygame.K_RETURN:
                    cleaned = hack_buffer.strip()

                    if game_mode == "puzzle":
                        upper = cleaned.upper()
                        if upper == "HINT":
                            give_puzzle_hint()
                            hack_buffer = ""
                        else:
                            handle_puzzle_answer(cleaned)
                            hack_buffer = ""
                    else:
                        if cleaned:
                            spawn_word_rain_from_text(cleaned)
                            if sfx_hack is not None:
                                sfx_hack.play()
                        hack_buffer = ""
                        hack_input_mode = False

                elif event.key == pygame.K_BACKSPACE:
                    hack_buffer = hack_buffer[:-1]
                else:
                    if event.unicode and event.unicode.isprintable():
                        hack_buffer += event.unicode
                continue  # skip normal controls while typing

            if event.key == pygame.K_ESCAPE:
                if hack_input_mode:
                    hack_input_mode = False
                    hack_buffer = ""
                else:
                    running = False

            elif event.key == pygame.K_SPACE:
                paused = not paused

            elif event.key == pygame.K_c:
                next_theme()

            elif event.key == pygame.K_UP:
                base_speed_factor = min(base_speed_factor + 0.1, 3.0)

            elif event.key == pygame.K_DOWN:
                base_speed_factor = max(base_speed_factor - 0.1, 0.2)

            elif event.key == pygame.K_b:
                slow_mo = not slow_mo

            elif event.key == pygame.K_n:
                binary_mode = not binary_mode
                if sfx_binary is not None:
                    sfx_binary.play()

            elif event.key == pygame.K_h:
                hack_input_mode = True
                hack_buffer = ""

            elif event.key == pygame.K_p:
                if game_mode == "free":
                    start_puzzle_mode()

            elif event.key == pygame.K_e:
                trigger_critical_error()

            elif event.key == pygame.K_s:
                trigger_shake(
                    intensity=random.randint(2, 5),
                    duration=random.randint(15, 30),
                )

            elif event.key == pygame.K_F11:
                toggle_fullscreen()

    # Effective speed (base * slow-mo multiplier)
    effective_speed = base_speed_factor * (0.3 if slow_mo else 1.0)

    # TRACE progression while in puzzle mode
    if (
        game_mode == "puzzle"
        and not paused
        and trace_active
        and critical_error_timer <= 0
    ):
        trace_level += 0.06 * (dt_ms / 16.0)
        if trace_level >= trace_max:
            trace_level = trace_max
            trace_active = False
            trigger_critical_error()

    if paused:
        apply_critical_error_overlay(scene_surface)
        offset_x, offset_y = get_shake_offset()
        screen.fill(current_theme["bg"])
        screen.blit(scene_surface, (offset_x, offset_y))
        draw_ui_overlay(screen)

        pygame.display.flip()
        continue

    # Clear scene and apply background
    scene_surface.fill(current_theme["bg"])

    # Fading trail effect
    trail_surface.fill((0, 0, 0, 80))
    scene_surface.blit(trail_surface, (0, 0))

    # Draw main rain
    for i, x in enumerate(x_positions):
        y = int(raindrops[i] * FONT_SIZE)

        # Random glyph
        if binary_mode:
            char = random.choice("01")
        else:
            char = random.choice(char_pool)

        # Glitch / bright effects
        r = random.random()
        if r > 0.985:
            color = current_theme["flash"]
        elif r > 0.95 and not binary_mode:
            char = random.choice("01")
            color = current_theme["bright"]
        else:
            color = (
                current_theme["bright"]
                if random.random() > 0.95
                else current_theme["main"]
            )

        text = font.render(char, True, color)
        scene_surface.blit(text, (x, y))

        # Trails
        for t in range(trail_length):
            trail_y = y - t * FONT_SIZE
            if trail_y > 0:
                if random.random() > 0.5 and not binary_mode:
                    trail_char = random.choice(char_pool)
                else:
                    trail_char = char
                trail_text = font.render(trail_char, True, current_theme["trail"])
                trail_surface.blit(trail_text, (x, trail_y))

        # Move drop
        raindrops[i] += speeds[i] * effective_speed

        # Random shake trigger
        if random.random() > 0.997:
            trigger_shake(
                intensity=random.randint(1, 3),
                duration=random.randint(10, 25),
            )

        # Reset drop randomly after leaving screen
        if y > HEIGHT and random.random() > 0.9:
            raindrops[i] = random.randint(-10, 0)
            speeds[i] = random.uniform(0.4, 1.2)

    # Occasionally spawn a special word rain
    if random.random() > 0.998:
        spawn_word_rain()

    # Draw and update word rains on top of normal rain
    draw_word_rains(scene_surface, effective_speed)

    # Apply critical error overlay (if active)
    apply_critical_error_overlay(scene_surface)

    # Camera shake on the rain scene only
    offset_x, offset_y = get_shake_offset()
    screen.fill(current_theme["bg"])
    screen.blit(scene_surface, (offset_x, offset_y))

    # Draw UI overlay after shake so it stays fixed
    draw_ui_overlay(screen)

    pygame.display.flip()

pygame.quit()
