import pygame
import random
import os
import sys
import math
import json
from enum import Enum

# ================== INIT ==================
pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works in dev and PyInstaller bundles."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# ================== GAME STATE ==================
class GameState(Enum):
    BOOT = "boot"
    PLAYING = "playing"
    PAUSED = "paused"
    TUTORIAL = "tutorial"


SAVE_FILE = os.path.join(
    os.path.dirname(sys.executable) if getattr(sys, "frozen", False)
    else os.path.dirname(os.path.abspath(__file__)),
    "visionbreaker_save.json",
)


def load_save():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "unlocked_themes": int(data.get("unlocked_themes", 1)),
                "high_score": int(data.get("high_score", 0)),
                "tutorial_done": bool(data.get("tutorial_done", False)),
            }
    except Exception:
        return {"unlocked_themes": 1, "high_score": 0, "tutorial_done": False}


def save_game(data):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def persist_save(**updates):
    global save_data
    save_data.update(updates)
    save_game(save_data)


save_data = load_save()
HIGH_SCORE = save_data.get("high_score", 0)


# ================== AUDIO ==================
ASSET_DIR = resource_path("assets")
MUSIC_FILE = os.path.join(ASSET_DIR, "codefall_ambience.ogg")
SFX_HACK_FILE = os.path.join(ASSET_DIR, "hack_confirm.wav")
SFX_BINARY_FILE = os.path.join(ASSET_DIR, "binary_toggle.wav")
SFX_ERROR_FILE = os.path.join(ASSET_DIR, "critical_error.wav")

music_loaded = False
sfx_hack = None
sfx_binary = None
sfx_error = None


def init_audio():
    """Load audio if assets exist. Missing files fail gracefully."""
    global music_loaded, sfx_hack, sfx_binary, sfx_error

    try:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)
        music_loaded = True
    except Exception:
        music_loaded = False

    try:
        sfx_hack = pygame.mixer.Sound(SFX_HACK_FILE)
        sfx_hack.set_volume(0.6)
    except Exception:
        sfx_hack = None

    try:
        sfx_binary = pygame.mixer.Sound(SFX_BINARY_FILE)
        sfx_binary.set_volume(0.5)
    except Exception:
        sfx_binary = None

    try:
        sfx_error = pygame.mixer.Sound(SFX_ERROR_FILE)
        sfx_error.set_volume(0.18)
    except Exception:
        sfx_error = None


def play_hack_sound():
    if sfx_hack is not None:
        sfx_hack.play()


def play_error_sound():
    if sfx_error is not None:
        sfx_error.play()


# ================== SCREEN ==================
DEFAULT_WINDOW_SIZE = (1300, 600)
info = pygame.display.Info()
FULLSCREEN_SIZE = (info.current_w, info.current_h)
fullscreen = True
WIDTH, HEIGHT = FULLSCREEN_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("VisionBreaker: Neurogrid Terminal")

# ================== FONTS ==================
FONT_SIZE = 28
CODE_COLUMN_SPACING = 6
font = pygame.font.Font(pygame.font.match_font("monospace"), FONT_SIZE)
big_font = pygame.font.Font(pygame.font.match_font("monospace"), 48)
small_font = pygame.font.SysFont("consolas", 12, bold=True)
medium_font = pygame.font.SysFont("consolas", 18, bold=True)
large_font = pygame.font.SysFont("consolas", 30, bold=True)
ui_font = pygame.font.SysFont("consolas", 12)
hack_font = pygame.font.SysFont("consolas", 16)
puzzle_font = pygame.font.SysFont("consolas", 14)

# ================== THEME DATA ==================
char_pool = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*カタカナ"

SPECIAL_WORDS = [
    "VISIONBREAKER", "NEUROGRID TERMINAL", "GRID ONLINE", "GRID BREACH",
    "NEURAL LINK", "EMERALD STREAM", "RED ALERT", "SYNTHWAVE CASCADE",
    "TRACE RISING", "TRACE SUPPRESSED", "TRACE NEUTRALIZED",
    "INTRUSION DETECTED", "ACCESS GRANTED", "ACCESS DENIED",
    "OVERRIDE ACCEPTED", "SIGNAL BREACH", "GHOST SIGNAL", "PACKET STORM",
    "LINK ESTABLISHED", "CONNECTION LOST", "NODE COMPROMISED",
    "CORE GLITCH", "SYSTEM FAULT", "KERNEL PANIC", "FIREWALL ACTIVE",
    "DATA VAULT", "ROOT ACCESS", "CIPHER LOCK", "EXTRACTION WINDOW",
]

COLOR_THEMES = [
    {"name": "Deep Matrix", "bg": (0, 0, 0), "main": (0, 190, 80), "trail": (0, 70, 35), "bright": (120, 255, 170), "flash": (235, 255, 235)},
    {"name": "Cyber Ice", "bg": (0, 6, 14), "main": (80, 255, 255), "trail": (20, 110, 130), "bright": (190, 255, 255), "flash": (255, 255, 255)},
    {"name": "Toxic Lime", "bg": (1, 8, 0), "main": (170, 255, 0), "trail": (70, 130, 0), "bright": (220, 255, 120), "flash": (255, 255, 255)},
    {"name": "Blue Firewall", "bg": (0, 2, 14), "main": (40, 100, 255), "trail": (10, 40, 130), "bright": (150, 190, 255), "flash": (255, 255, 255)},
    {"name": "Crimson Trace", "bg": (12, 0, 2), "main": (255, 20, 90), "trail": (120, 0, 35), "bright": (255, 140, 180), "flash": (255, 255, 255)},
    {"name": "Golden Core", "bg": (8, 5, 0), "main": (255, 210, 60), "trail": (130, 90, 20), "bright": (255, 240, 160), "flash": (255, 255, 255)},
    {"name": "Void Purple", "bg": (3, 0, 12), "main": (150, 60, 255), "trail": (55, 20, 120), "bright": (210, 170, 255), "flash": (255, 255, 255)},
    {"name": "Pink Glitch", "bg": (10, 0, 10), "main": (255, 70, 180), "trail": (120, 25, 90), "bright": (255, 180, 230), "flash": (255, 255, 255)},
    {"name": "White Terminal", "bg": (0, 0, 0), "main": (220, 220, 220), "trail": (90, 90, 90), "bright": (255, 255, 255), "flash": (120, 255, 180)},
    {"name": "Blood Moon", "bg": (8, 0, 0), "main": (190, 0, 0), "trail": (80, 0, 0), "bright": (255, 80, 80), "flash": (255, 255, 255)},
    {"name": "Quantum Teal", "bg": (0, 8, 10), "main": (0, 220, 180), "trail": (0, 90, 85), "bright": (140, 255, 235), "flash": (255, 255, 255)},
    {"name": "Root Phantom", "bg": (0, 0, 0), "main": (180, 255, 120), "trail": (60, 100, 45), "bright": (230, 255, 200), "flash": (255, 255, 255)},
    {"name": "Countertrace Red", "bg": (5, 0, 0), "main": (255, 55, 30), "trail": (120, 20, 10), "bright": (255, 170, 140), "flash": (255, 255, 255)},
    {"name": "Vault Gold", "bg": (8, 6, 0), "main": (255, 190, 40), "trail": (115, 80, 10), "bright": (255, 230, 150), "flash": (255, 255, 255)},
    {"name": "Neurogrid Whiteout", "bg": (2, 4, 6), "main": (200, 255, 240), "trail": (70, 120, 110), "bright": (255, 255, 255), "flash": (0, 255, 160)},
]

theme_index = 0
unlocked_themes = max(1, min(save_data.get("unlocked_themes", 1), len(COLOR_THEMES)))
current_theme = COLOR_THEMES[theme_index]

# ================== SURFACE AND RAIN STATE ==================
columns = 0
raindrops = []
x_positions = []
speeds = []
trail_length = 18
trail_surface = None
scene_surface = None
error_overlay = None
word_rains = []

# ================== GENERAL STATE ==================
game_state = GameState.BOOT
game_mode = "free"
hack_input_mode = False
hack_buffer = ""
running = True
clock = pygame.time.Clock()
last_dt_ms = 0
show_ui = True
operator_card_visible = False
base_speed_factor = 0.5
slow_mo = False
binary_mode = False

shake_intensity = 0
shake_timer = 0
critical_error_timer = 0
critical_glitch_intensity = 0

# ================== SCORE / PARTICLES / ACHIEVEMENTS ==================
class ScoreManager:
    def __init__(self):
        self.current_score = 0
        self.multiplier = 1.0
        self.combo = 0
        self.last_hack_time = 0
        self.score_popups = []

    def add_score(self, points, x, y, label=None):
        global HIGH_SCORE
        earned = int(points * self.multiplier)
        self.current_score += earned
        text = label if label is not None else f"+{earned}"
        self.score_popups.append({
            "x": float(x), "y": float(y), "text": text,
            "timer": 140, "color": current_theme["bright"],
        })
        if self.current_score > HIGH_SCORE:
            HIGH_SCORE = self.current_score
            persist_save(high_score=HIGH_SCORE)
        return earned

    def hack(self):
        self.combo += 1
        self.multiplier = min(10.0, 1.0 + (self.combo * 0.1))
        self.last_hack_time = pygame.time.get_ticks()

    def break_combo(self):
        self.combo = 0
        self.multiplier = 1.0

    def update(self):
        if pygame.time.get_ticks() - self.last_hack_time > 5000:
            self.combo = 0
            self.multiplier = max(1.0, self.multiplier - 0.012)
        for popup in self.score_popups[:]:
            popup["timer"] -= 1
            popup["y"] -= 0.35
            if popup["timer"] <= 0:
                self.score_popups.remove(popup)


score_manager = ScoreManager()


class Particle:
    def __init__(self, x, y, color, velocity=None, size=None, life=None):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.life = life if life is not None else random.randint(24, 54)
        self.max_life = self.life
        if velocity is not None:
            self.vx, self.vy = velocity
        else:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.0, 4.5)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
        self.size = float(size if size is not None else random.randint(2, 5))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.035
        self.life -= 1
        self.size *= 0.985
        return self.life > 0

    def draw(self, surface):
        if self.size <= 0.5:
            return
        ratio = max(0.0, min(1.0, self.life / max(1, self.max_life)))
        alpha = int(255 * ratio)
        radius = max(1, int(self.size * ratio))
        particle_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(
            particle_surf,
            (*self.color[:3], alpha),
            (radius * 2, radius * 2),
            radius,
        )
        surface.blit(particle_surf, (int(self.x) - radius * 2, int(self.y) - radius * 2))


particles = []


def spawn_particles(x, y, count=10, color=None, spread=4.0):
    if color is None:
        color = current_theme["bright"]
    for _ in range(count):
        angle = random.uniform(0.0, math.pi * 2.0)
        speed = random.uniform(0.8, spread)
        velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
        particles.append(Particle(x, y, color, velocity=velocity))


ACHIEVEMENTS = {
    "first_hack": {"name": "First Hack", "desc": "Complete your first command", "unlocked": False},
    "scanner_online": {"name": "Scanner Online", "desc": "Reveal the mainframe core", "unlocked": False},
    "first_breach": {"name": "First Breach", "desc": "Damage the mainframe core for the first time", "unlocked": False},
    "first_cipher": {"name": "Cipher Breaker", "desc": "Solve your first cipher puzzle", "unlocked": False},
    "puzzle_solver": {"name": "Code Breaker", "desc": "Solve 10 cipher puzzles", "unlocked": False},

    "combo_starter": {"name": "Combo Starter", "desc": "Reach a 2x multiplier", "unlocked": False},
    "combo_master": {"name": "Combo Master", "desc": "Reach a 5x multiplier", "unlocked": False},
    "combo_overdrive": {"name": "Combo Overdrive", "desc": "Reach a 10x multiplier", "unlocked": False},

    "score_1k": {"name": "Packet Runner", "desc": "Reach 1,000 points", "unlocked": False},
    "score_5k": {"name": "Firewall Breaker", "desc": "Reach 5,000 points", "unlocked": False},
    "score_10k": {"name": "Neurogrid Operator", "desc": "Reach 10,000 points", "unlocked": False},
    "score_25k": {"name": "Digital Phantom", "desc": "Reach 25,000 points", "unlocked": False},

    "speed_demon": {"name": "Speed Demon", "desc": "Reach max rain speed", "unlocked": False},
    "theme_collector": {"name": "Theme Collector", "desc": "Unlock all visual themes", "unlocked": False},

    "trace_survivor": {"name": "Trace Survivor", "desc": "Recover from dangerous TRACE levels", "unlocked": False},
    "clean_breach": {"name": "Clean Breach", "desc": "Complete Level 1 with TRACE below 35%", "unlocked": False},
    "root_access": {"name": "Root Access", "desc": "Compromise the mainframe", "unlocked": False},

    "vault_ping": {"name": "Vault Ping", "desc": "Reveal the data vault nodes", "unlocked": False},
    "first_download": {"name": "Data Thief", "desc": "Download your first vault fragment", "unlocked": False},
    "vault_runner": {"name": "Vault Runner", "desc": "Clear the data vault", "unlocked": False},
    "clean_vault": {"name": "Ghost in the Vault", "desc": "Clear the vault with lockdown below 35%", "unlocked": False},

    "countertrace_defender": {"name": "Countertrace Defender", "desc": "Survive the final typing defense", "unlocked": False},
    "math_destroyer": {"name": "Math Packet Smasher", "desc": "Destroy a math packet", "unlocked": False},
    "virus_hunter": {"name": "Virus Hunter", "desc": "Destroy a virus or lockout packet", "unlocked": False},
    "perfect_escape": {"name": "Perfect Escape", "desc": "Clear Level 3 with no missed packets", "unlocked": False},

    "full_run": {"name": "Neurogrid Escaped", "desc": "Complete the full 3-level run", "unlocked": False},
}
achievement_notification = None
cipher_solved_total = 0


def unlock_achievement(key):
    global achievement_notification
    if key in ACHIEVEMENTS and not ACHIEVEMENTS[key]["unlocked"]:
        ACHIEVEMENTS[key]["unlocked"] = True
        achievement_notification = {
            "text": f"ACHIEVEMENT: {ACHIEVEMENTS[key]['name']} - {ACHIEVEMENTS[key]['desc']}",
            "timer": 210,
        }
        spawn_particles(WIDTH // 2, HEIGHT // 2, 70, (255, 215, 0), spread=6.0)

def check_general_achievements():
    """Check score, combo, and general progression achievements."""
    if score_manager.multiplier >= 2.0:
        unlock_achievement("combo_starter")

    if score_manager.multiplier >= 5.0:
        unlock_achievement("combo_master")

    if score_manager.multiplier >= 10.0:
        unlock_achievement("combo_overdrive")

    if score_manager.current_score >= 1000:
        unlock_achievement("score_1k")

    if score_manager.current_score >= 5000:
        unlock_achievement("score_5k")

    if score_manager.current_score >= 10000:
        unlock_achievement("score_10k")

    if score_manager.current_score >= 25000:
        unlock_achievement("score_25k")

    unlock_themes_by_score()
    
def register_cipher_solved():
    """Track solved cipher puzzles and unlock cipher achievements."""
    global cipher_solved_total, puzzles_solved_this_run

    cipher_solved_total += 1
    puzzles_solved_this_run += 1

    unlock_achievement("first_cipher")

    if cipher_solved_total >= 10:
        unlock_achievement("puzzle_solver")

# ================== PUZZLES ==================
puzzles = [
    {"prompt": "BINARY 1111 TO DECIMAL.", "answer": "15", "hint": "8 + 4 + 2 + 1."},
    {"prompt": "BINARY 1001 TO DECIMAL.", "answer": "9", "hint": "8 + 1."},
    {"prompt": "BINARY 1100 TO DECIMAL.", "answer": "12", "hint": "8 + 4."},
    {"prompt": "HEX KEY: WHAT COMES AFTER 9 IN HEXADECIMAL?", "answer": "A", "hint": "Hex digits go 0-9, then A-F."},
    {"prompt": "HEX FF TO DECIMAL.", "answer": "255", "hint": "FF is the max value of one byte."},

    {"prompt": "ACCESS CHECK: OPPOSITE OF LOCK.", "answer": "UNLOCK", "hint": "What you do to open access."},
    {"prompt": "TRACE DEFENSE: OPPOSITE OF EXPOSE.", "answer": "HIDE", "hint": "To avoid being seen."},
    {"prompt": "SECURITY TERM: A SECRET WORD USED FOR ACCESS.", "answer": "PASSWORD", "hint": "You type it to log in."},
    {"prompt": "NETWORK NODE: DEVICE THAT ROUTES TRAFFIC.", "answer": "ROUTER", "hint": "Common home network device."},
    {"prompt": "NETWORK PATH: DATA TRAVELS IN A ______.", "answer": "PACKET", "hint": "Small unit of network data."},

    {"prompt": "SYSTEM FLOW: LOGIN -> VERIFY -> ______.", "answer": "ACCESS", "hint": "What you gain after verification."},
    {"prompt": "BREACH FLOW: SCAN -> BREACH -> ______.", "answer": "EXTRACT", "hint": "Final command in Level 1."},
    {"prompt": "VAULT FLOW: PING -> LOCK -> DECRYPT -> ______.", "answer": "DOWNLOAD", "hint": "Command used to take the data."},
    {"prompt": "COUNTERTRACE GOAL: DEFEND THE ESCAPE ______.", "answer": "STREAM", "hint": "Level 3 escape target."},
    {"prompt": "DANGER METER: THE SYSTEM IS TRYING TO ______ YOU.", "answer": "TRACE", "hint": "Main danger system in Level 1."},

    {"prompt": "SEQUENCE KEY: 3 6 12 24 ?", "answer": "48", "hint": "Each value doubles."},
    {"prompt": "SEQUENCE KEY: 5 10 20 40 ?", "answer": "80", "hint": "Each value doubles."},
    {"prompt": "SEQUENCE KEY: 1 2 4 8 16 ?", "answer": "32", "hint": "Powers of two."},
    {"prompt": "SEQUENCE KEY: 2 5 8 11 ?", "answer": "14", "hint": "Add 3 each time."},
    {"prompt": "SEQUENCE KEY: 10 20 30 40 ?", "answer": "50", "hint": "Add 10 each time."},

    {"prompt": "LOGIC KEY: TRUE AND TRUE = ?", "answer": "TRUE", "hint": "Both values are true."},
    {"prompt": "LOGIC KEY: TRUE AND FALSE = ?", "answer": "FALSE", "hint": "AND needs both to be true."},
    {"prompt": "LOGIC KEY: TRUE OR FALSE = ?", "answer": "TRUE", "hint": "OR only needs one true value."},
    {"prompt": "LOGIC KEY: NOT TRUE = ?", "answer": "FALSE", "hint": "NOT flips the value."},
    {"prompt": "LOGIC KEY: NOT FALSE = ?", "answer": "TRUE", "hint": "NOT flips the value."},

    {"prompt": "QUICK MATH: 7 + 8.", "answer": "15", "hint": "Add the two numbers."},
    {"prompt": "QUICK MATH: 12 + 9.", "answer": "21", "hint": "Add the two numbers."},
    {"prompt": "QUICK MATH: 20 - 7.", "answer": "13", "hint": "Subtract 7 from 20."},
    {"prompt": "QUICK MATH: 6 x 4.", "answer": "24", "hint": "Six groups of four."},
    {"prompt": "QUICK MATH: 9 x 3.", "answer": "27", "hint": "Nine groups of three."},

    {"prompt": "CIPHER WORD: SCRAMBLED SIGNAL NEEDS A ______.", "answer": "KEY", "hint": "A cipher is unlocked with this."},
    {"prompt": "CIPHER WORD: HIDDEN DATA IS ______.", "answer": "ENCRYPTED", "hint": "Protected data is usually this."},
    {"prompt": "CIPHER WORD: TO READ ENCRYPTED DATA, YOU ______ IT.", "answer": "DECRYPT", "hint": "The command used to solve cipher locks."},
    {"prompt": "FIREWALL TERM: A WALL THAT BLOCKS NETWORK ______.", "answer": "TRAFFIC", "hint": "Data moving across a network."},
    {"prompt": "SYSTEM TERM: THE MAIN CONTROL PART IS THE ______.", "answer": "CORE", "hint": "VisionBreaker has a mainframe core."},

    {"prompt": "VISIONBREAKER COMMAND: REVEAL THE TARGET.", "answer": "SCAN", "hint": "First command to begin the breach."},
    {"prompt": "VISIONBREAKER COMMAND: DAMAGE THE CORE.", "answer": "BREACH", "hint": "Main attack command."},
    {"prompt": "VISIONBREAKER COMMAND: HEAVY DAMAGE, HIGH RISK.", "answer": "INJECT", "hint": "A stronger attack command."},
    {"prompt": "VISIONBREAKER COMMAND: LOWER TRACE.", "answer": "SUPPRESS", "hint": "Use this when TRACE gets high."},
    {"prompt": "VISIONBREAKER COMMAND: REMOVE BAD VAULT NODES.", "answer": "PURGE", "hint": "Used against corrupt or decoy nodes."},

    {"prompt": "MAINFRAME STATUS: ROOT ACCESS MEANS YOU HAVE ______ CONTROL.", "answer": "FULL", "hint": "Root access is total control."},
    {"prompt": "VAULT STATUS: BAD DATA PACKETS ARE ______.", "answer": "CORRUPT", "hint": "Broken or dangerous data."},
    {"prompt": "VAULT STATUS: FAKE NODES ARE CALLED ______.", "answer": "DECOYS", "hint": "Fake targets meant to trick you."},
    {"prompt": "ESCAPE STATUS: TOO MANY MISSES BREAK THE ______.", "answer": "SHIELD", "hint": "Level 3 protection meter."},
    {"prompt": "FINAL OBJECTIVE: SURVIVE THE ______.", "answer": "NEUROGRID", "hint": "The system watching you."},
]
current_puzzle_index = 0
puzzle_bag = []
puzzles_solved_this_run = 0
puzzle_message = ""
puzzle_full_line = ""
puzzle_visible_chars = 0
puzzle_type_accum = 0.0
PUZZLE_CHARS_PER_SEC = 42.0

# ================== LIVING MAINFRAME SYSTEM ==================
trace_level = 0.0
trace_max = 100.0
trace_active = False

mainframe_integrity = 100.0
mainframe_max_integrity = 100.0
access_level = 1
scan_complete = False
core_revealed = False
core_materialize = 0.0
root_access = False
system_lockout = False

system_status = "AWAITING INTRUSION"
system_objective = "Objective: Type SCAN to locate the mainframe core."
next_command = "SCAN"
system_messages = []
MAX_SYSTEM_MESSAGES = 8
system_chatter_timer = 0
system_event_timer = 0

MAINFRAME_TRACE_DRIFT = 0.018
cipher_lock_active = False
cipher_lock_name = ""
cipher_lock_timer = 0
cipher_lock_thresholds_hit = set()

# Cipher mode is meant to be readable, not panic-hidden.
# TRACE is paused while the cipher panel is open.
cipher_wrong_attempts = 0
cipher_hint_visible = False

extraction_active = False
extraction_progress = 0.0
extraction_stability = 100.0

core_flash_timer = 0
core_damage_timer = 0
core_scan_timer = 0
core_alarm_timer = 0
screen_pulse_timer = 0
command_banner = ""
command_banner_timer = 0
last_command_result = ""


# ================== LEVEL 2: DATA VAULT INFILTRATION ==================
level_stage = 1              # 1 = Main Breach, 2 = Data Vault, 3 = Countertrace Defense
level1_complete = False
vault_active = False
vault_complete = False
vault_nodes = []
vault_locked_index = None
vault_fragments_extracted = 0
vault_fragments_required = 5
vault_lockdown = 0.0
vault_max_lockdown = 100.0
vault_ping_timer = 0
vault_mask_timer = 0
vault_decrypt_pending = False
vault_node_pulse = 0.0
vault_intro_timer = 0

# ================== LEVEL 3: COUNTERTRACE DEFENSE ==================
defense_active = False
defense_complete = False
defense_threats = []
defense_lasers = []
defense_progress = 0.0
defense_progress_max = 100.0
defense_shield = 100.0
defense_max_shield = 100.0
defense_spawn_timer = 0.0
defense_intro_timer = 0
defense_wave = 1
defense_hits = 0
defense_misses = 0
defense_wrong_inputs = 0
defense_typed_commands = 0
defense_math_enabled = True
defense_last_spawn_id = 0

# ================== LEVEL 3 DIFFICULTY TUNING ==================
DEFENSE_START_DELAY = 140.0          # delay before first packet appears
DEFENSE_BASE_SPAWN_FRAMES = 125.0    # higher = slower spawning
DEFENSE_MIN_SPAWN_FRAMES = 42.0      # lower limit for late-game spawn speed
DEFENSE_WAVE_PROGRESS_STEP = 32.0    # higher = waves increase later
DEFENSE_WAVE_SPAWN_STEP = 8.0        # spawn speed increase per wave
DEFENSE_HIT_SPAWN_STEP = 0.08        # spawn speed increase per successful hit
DEFENSE_EXTRA_SPAWN_WAVE = 4         # extra spawns do not happen until this wave
DEFENSE_EXTRA_SPAWN_CHANCE = 0.12    # chance of double spawn in later waves
DEFENSE_THREAT_SPEED_SCALE = 0.78    # lower = falling packets move slower

# ================== BASIC HELPERS ==================
def init_surfaces():
    global trail_surface, scene_surface, error_overlay
    global columns, raindrops, x_positions, speeds, word_rains
    trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    scene_surface = pygame.Surface((WIDTH, HEIGHT))
    error_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    columns = (WIDTH // CODE_COLUMN_SPACING) + 4
    raindrops = [random.randint(-HEIGHT // FONT_SIZE, 0) for _ in range(columns)]
    x_positions = [i * CODE_COLUMN_SPACING for i in range(columns)]
    speeds = [random.uniform(0.4, 1.2) for _ in range(columns)]
    word_rains.clear()


def trigger_shake(intensity=3, duration=20):
    global shake_intensity, shake_timer
    shake_intensity = max(shake_intensity, intensity)
    shake_timer = max(shake_timer, duration)


def get_shake_offset():
    global shake_timer
    if shake_timer > 0:
        shake_timer -= 1
        return (
            random.randint(-shake_intensity, shake_intensity),
            random.randint(-shake_intensity, shake_intensity),
        )
    return 0, 0


def toggle_fullscreen():
    global fullscreen, screen, WIDTH, HEIGHT
    fullscreen = not fullscreen
    if fullscreen:
        WIDTH, HEIGHT = FULLSCREEN_SIZE
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        WIDTH, HEIGHT = DEFAULT_WINDOW_SIZE
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    init_surfaces()


def next_theme():
    global theme_index, current_theme
    if unlocked_themes <= 0:
        return
    theme_index = (theme_index + 1) % unlocked_themes
    current_theme = COLOR_THEMES[theme_index]
    banner(f"THEME: {current_theme['name'].upper()}", current_theme["flash"], 100)


def spawn_word_rain():
    spawn_word_rain_from_text(random.choice(SPECIAL_WORDS))


def spawn_word_rain_from_text(text):
    text = text.strip()
    if not text or not x_positions:
        return
    letters = list(text.upper())
    col_index = random.randrange(len(x_positions))
    x = x_positions[col_index]
    start_y = -len(letters) * FONT_SIZE
    word_rains.append({
        "x": x,
        "y": start_y,
        "letters": letters,
        "speed": random.uniform(1.5, 3.4),
    })


def draw_word_rains(surface, effective_speed):
    to_remove = []
    for i, wr in enumerate(word_rains):
        x = wr["x"]
        y_top = wr["y"]
        letters = wr["letters"]
        for idx, ch in enumerate(letters):
            y = y_top + idx * FONT_SIZE
            if y > HEIGHT or ch == " ":
                continue
            color = current_theme["flash"] if random.random() > 0.88 else current_theme["bright"]
            text = font.render(ch, True, color)
            surface.blit(text, (x, y))
        wr["y"] += wr["speed"] * effective_speed
        if wr["y"] - len(letters) * FONT_SIZE > HEIGHT:
            to_remove.append(i)
    for i in reversed(to_remove):
        del word_rains[i]


def add_system_message(text, color=None, timer=520):
    if color is None:
        color = current_theme["main"]
    system_messages.append({"text": text, "color": color, "timer": timer})
    while len(system_messages) > MAX_SYSTEM_MESSAGES:
        system_messages.pop(0)


def set_objective(text, next_cmd=None):
    global system_objective, next_command
    system_objective = f"Objective: {text}"
    if next_cmd:
        next_command = next_cmd


def banner(text, color=None, timer=95):
    global command_banner, command_banner_timer
    command_banner = text
    command_banner_timer = timer
    if color is not None:
        pass


def clamp_trace():
    global trace_level
    trace_level = max(0.0, min(trace_max, trace_level))


def raise_trace(amount, reason="TRACE RISING"):
    global trace_level, core_alarm_timer, screen_pulse_timer
    if root_access or system_lockout:
        return
    trace_level += amount
    clamp_trace()
    core_alarm_timer = max(core_alarm_timer, 50)
    screen_pulse_timer = max(screen_pulse_timer, 25)
    add_system_message(f"{reason}: TRACE +{int(amount)}", (255, 80, 40), timer=360)
    if trace_level >= trace_max:
        trigger_system_lockout()


def reduce_trace(amount, reason="TRACE SUPPRESSED"):
    global trace_level, core_alarm_timer
    if system_lockout:
        return
    old = trace_level
    trace_level = max(0.0, trace_level - amount)
    reduced = int(old - trace_level)

    if old >= 70 and trace_level < 50:
        unlock_achievement("trace_survivor")
    if reduced > 0:
        add_system_message(f"{reason}: TRACE -{reduced}", current_theme["bright"], timer=360)
        spawn_particles(WIDTH // 2, HEIGHT // 2, 28, current_theme["main"], spread=3.5)
    if trace_level < 50:
        core_alarm_timer = max(0, core_alarm_timer - 20)


def trigger_critical_error():
    global critical_error_timer, critical_glitch_intensity
    global game_mode, puzzle_message, hack_input_mode, hack_buffer
    global trace_level, trace_active
    critical_error_timer = 150
    critical_glitch_intensity = 6
    trigger_shake(critical_glitch_intensity, critical_error_timer)
    if game_mode == "puzzle":
        game_mode = "free"
        puzzle_message = "TRACE FAILED"
        hack_input_mode = False
        hack_buffer = ""
    trace_level = 0.0
    trace_active = False
    play_error_sound()


def apply_critical_error_overlay(surface):
    global critical_error_timer
    if critical_error_timer <= 0:
        return
    critical_error_timer -= 1
    error_overlay.fill((255, 0, 0, 82))
    surface.blit(error_overlay, (0, 0))
    for _ in range(8):
        y = random.randint(0, HEIGHT)
        width = random.randint(WIDTH // 5, WIDTH)
        x = random.randint(-WIDTH // 3, WIDTH)
        pygame.draw.rect(surface, (255, 0, 0), (x, y, width, 2))
    text = big_font.render("SYSTEM FAILURE", True, current_theme["flash"])
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    surface.blit(text, rect)


# ================== MAINFRAME GAMEPLAY ==================
def unlock_theme_count(target_count, reason="THEME UNLOCKED"):
    """Unlock themes up to a specific count."""
    global unlocked_themes, theme_index, current_theme

    target_count = max(1, min(target_count, len(COLOR_THEMES)))

    if target_count > unlocked_themes:
        unlocked_themes = target_count
        theme_index = unlocked_themes - 1
        current_theme = COLOR_THEMES[theme_index]
        persist_save(unlocked_themes=unlocked_themes)

        spawn_word_rain_from_text(f"THEME UNLOCKED {current_theme['name']}")
        spawn_particles(WIDTH // 2, HEIGHT // 2, 80, (255, 215, 0), spread=6.5)
        add_system_message(
            f"VISUAL THEME UNLOCKED: {current_theme['name'].upper()}",
            (255, 215, 0),
            timer=620,
        )

        if unlocked_themes >= len(COLOR_THEMES):
            unlock_achievement("theme_collector")


def unlock_themes_by_score():
    """Unlock extra themes from score milestones."""
    milestones = [
        (500, 2),
        (1200, 3),
        (2500, 4),
        (4000, 5),
        (6500, 6),
        (9000, 7),
        (12000, 8),
        (16000, 9),
        (21000, 10),
        (28000, 11),
        (35000, 12),
    ]

    for score_needed, theme_count in milestones:
        if score_manager.current_score >= score_needed:
            unlock_theme_count(theme_count, "SCORE THEME UNLOCK")


def unlock_next_theme_from_progress():
    """Unlock themes from Level 1 access progress."""
    desired = min(1 + access_level, len(COLOR_THEMES))
    unlock_theme_count(desired, "ACCESS THEME UNLOCK")


def update_access_level():
    global access_level
    old = access_level
    hacked_percent = 100.0 - mainframe_integrity
    access_level = min(5, 1 + int(hacked_percent // 20))
    if access_level > old:
        add_system_message(f"ACCESS LEVEL {access_level} GRANTED", current_theme["flash"], timer=520)
        spawn_word_rain_from_text(f"ACCESS LEVEL {access_level}")
        spawn_particles(WIDTH // 2, HEIGHT // 2, 55, current_theme["bright"], spread=5.0)
        trigger_shake(3, 20)
        unlock_next_theme_from_progress()


def deploy_cipher_lock(lock_name=None):
    global cipher_lock_active, cipher_lock_name, cipher_lock_timer, system_status
    if cipher_lock_active or root_access or system_lockout:
        return
    cipher_lock_active = True
    cipher_lock_name = lock_name or random.choice(["CIPHER LOCK", "FIREWALL HASH", "VAULT ENCRYPTION"])
    cipher_lock_timer = 999999
    system_status = "CIPHER LOCK DEPLOYED"
    add_system_message(f"{cipher_lock_name} DEPLOYED. TYPE DECRYPT.", (255, 180, 0), timer=700)
    set_objective(f"System deployed {cipher_lock_name}. Type DECRYPT to break it.", "DECRYPT")
    spawn_word_rain_from_text(cipher_lock_name)
    spawn_particles(WIDTH // 2, HEIGHT // 2, 70, (255, 180, 0), spread=5.5)
    trigger_shake(4, 28)


def check_cipher_thresholds():
    thresholds = [(75, "OUTER HASH"), (52, "SIGNATURE WALL"), (30, "DATA VAULT LOCK")]
    for threshold, name in thresholds:
        if mainframe_integrity <= threshold and threshold not in cipher_lock_thresholds_hit:
            cipher_lock_thresholds_hit.add(threshold)
            deploy_cipher_lock(name)
            return


def damage_mainframe(amount, reason="BREACH ACCEPTED", allow_through_lock=False):
    global mainframe_integrity, core_flash_timer, core_damage_timer, system_status
    if root_access or system_lockout:
        return 0
    if not scan_complete:
        add_system_message("NO TARGET MAP. TYPE SCAN FIRST.", (255, 180, 0), timer=420)
        return 0

    original_amount = amount
    if cipher_lock_active and not allow_through_lock:
        amount *= 0.28
        add_system_message("CIPHER LOCK ABSORBED MOST OF THE HIT", (255, 180, 0), timer=420)

    mainframe_integrity = max(0.0, mainframe_integrity - amount)
    core_flash_timer = max(core_flash_timer, 18)
    core_damage_timer = max(core_damage_timer, 32)
    system_status = "CORE UNDER ATTACK"
    spawn_particles(WIDTH // 2, HEIGHT // 2, int(24 + original_amount * 2), current_theme["bright"], spread=5.0)
    add_system_message(f"{reason}: CORE -{amount:.1f}%", current_theme["bright"], timer=420)
    update_access_level()
    check_cipher_thresholds()
    unlock_achievement("first_breach")

    if mainframe_integrity <= 0 and not extraction_active:
        set_objective("Core is cracked. Type EXTRACT to pull ROOT ACCESS.", "EXTRACT")
        system_status = "CORE EXPOSED"
        add_system_message("CORE EXPOSED. EXTRACTION AVAILABLE.", current_theme["flash"], timer=620)
    elif mainframe_integrity <= 12 and not extraction_active:
        set_objective("Core weakened. Type EXTRACT to start extraction.", "EXTRACT")
        system_status = "EXTRACTION WINDOW"
    elif not cipher_lock_active and not extraction_active:
        set_objective("Keep attacking. Use BREACH, INJECT, SUPPRESS, or DECRYPT.", "BREACH")
    return amount


def complete_root_access():
    global root_access, system_status, hack_input_mode, hack_buffer, extraction_active, trace_active
    global level1_complete, level_stage
    if root_access:
        return
    clear_cipher_state()
    root_access = True
    level1_complete = True
    level_stage = 1
    extraction_active = False
    trace_active = False
    hack_input_mode = False
    hack_buffer = ""
    system_status = "LEVEL 1 COMPLETE"
    set_objective("Main breach complete. Press ENTER or type VAULT to enter Level 2.", "VAULT")
    banner("LEVEL 1 COMPLETE", current_theme["flash"], 180)
    spawn_word_rain_from_text("ROOT ACCESS GRANTED")
    spawn_word_rain_from_text("DATA VAULT EXPOSED")
    spawn_particles(WIDTH // 2, HEIGHT // 2, 140, current_theme["flash"], spread=8.0)
    trigger_shake(6, 70)
    add_system_message("ROOT ACCESS GRANTED. DATA VAULT EXPOSED.", current_theme["flash"], timer=900)
    add_system_message("PRESS ENTER OR TYPE VAULT TO CONTINUE TO LEVEL 2.", current_theme["bright"], timer=900)
    score_manager.hack()
    score_manager.add_score(1500, WIDTH // 2 - 40, HEIGHT // 2 - 130, label="ROOT +1500")

    if trace_level <= 35:
        unlock_achievement("clean_breach")

    unlock_theme_count(8, "LEVEL 1 COMPLETE")
    unlock_achievement("root_access")

    play_hack_sound()

def trigger_system_lockout():
    global system_lockout, system_status, hack_input_mode, hack_buffer
    global critical_error_timer, critical_glitch_intensity, trace_active, extraction_active
    if system_lockout or root_access:
        return
    clear_cipher_state()
    system_lockout = True
    extraction_active = False
    trace_active = False
    hack_input_mode = False
    hack_buffer = ""
    system_status = "TRACE LOCKOUT"
    critical_error_timer = 190
    critical_glitch_intensity = 8
    trigger_shake(critical_glitch_intensity, critical_error_timer)
    set_objective("TRACE LOCKOUT. Press ENTER to restart the breach.", "RESET")
    banner("TRACE LOCKOUT", (255, 60, 40), 180)
    spawn_word_rain_from_text("TRACE LOCKOUT")
    spawn_word_rain_from_text("ACCESS TERMINATED")
    spawn_particles(WIDTH // 2, HEIGHT // 2, 120, (255, 0, 0), spread=7.0)
    add_system_message("TRACE LOCKOUT. CONNECTION TERMINATED.", (255, 60, 40), timer=900)
    play_error_sound()


def reset_mainframe_run(reset_score=False):
    global mainframe_integrity, access_level, scan_complete, core_revealed, core_materialize
    global root_access, system_lockout, system_status, trace_level, trace_active
    global game_mode, hack_input_mode, hack_buffer, puzzle_message, puzzle_full_line
    global puzzle_visible_chars, puzzle_type_accum, cipher_lock_active, cipher_lock_name
    global cipher_lock_thresholds_hit, extraction_active, extraction_progress, extraction_stability
    global core_flash_timer, core_damage_timer, core_scan_timer, core_alarm_timer
    global level_stage, level1_complete, vault_active, vault_complete, vault_nodes, vault_locked_index
    global vault_fragments_extracted, vault_lockdown, vault_ping_timer, vault_mask_timer
    global vault_decrypt_pending, vault_intro_timer
    global defense_active, defense_complete, defense_threats, defense_lasers
    global defense_progress, defense_shield, defense_spawn_timer, defense_intro_timer
    global defense_wave, defense_hits, defense_misses, defense_wrong_inputs
    global defense_typed_commands, defense_math_enabled, defense_last_spawn_id
    global puzzle_bag, puzzles_solved_this_run

    mainframe_integrity = mainframe_max_integrity
    access_level = 1
    scan_complete = False
    core_revealed = False
    core_materialize = 0.0
    root_access = False
    system_lockout = False
    trace_level = 0.0
    trace_active = False
    game_mode = "free"
    hack_input_mode = True
    hack_buffer = ""
    puzzle_message = ""
    puzzle_full_line = ""
    puzzle_visible_chars = 0
    puzzle_type_accum = 0.0
    puzzle_bag = []
    puzzles_solved_this_run = 0
    cipher_lock_active = False
    cipher_lock_name = ""
    cipher_lock_thresholds_hit.clear()
    extraction_active = False
    extraction_progress = 0.0
    extraction_stability = 100.0
    core_flash_timer = 0
    core_damage_timer = 0
    core_scan_timer = 0
    core_alarm_timer = 0

    level_stage = 1
    level1_complete = False
    vault_active = False
    vault_complete = False
    vault_nodes = []
    vault_locked_index = None
    vault_fragments_extracted = 0
    vault_lockdown = 0.0
    vault_ping_timer = 0
    vault_mask_timer = 0
    vault_decrypt_pending = False
    vault_intro_timer = 0

    defense_active = False
    defense_complete = False
    defense_threats = []
    defense_lasers = []
    defense_progress = 0.0
    defense_shield = defense_max_shield
    defense_spawn_timer = 0.0
    defense_intro_timer = 0
    defense_wave = 1
    defense_hits = 0
    defense_misses = 0
    defense_wrong_inputs = 0
    defense_typed_commands = 0
    defense_math_enabled = True
    defense_last_spawn_id = 0

    system_status = "AWAITING INTRUSION"
    system_messages.clear()
    set_objective("Free codefall mode. Type SCAN when you are ready to engage the mainframe.", "SCAN")
    add_system_message("NEW BREACH SESSION INITIALIZED", current_theme["bright"], timer=520)
    spawn_word_rain_from_text("NEW BREACH SESSION")
    if reset_score:
        score_manager.current_score = 0
        score_manager.break_combo()

def start_scan_sequence():
    global scan_complete, core_revealed, core_materialize, core_scan_timer, system_status, trace_active
    if scan_complete:
        add_system_message("TARGET MAP ALREADY LOADED", current_theme["main"], timer=360)
        set_objective("Attack the firewall core with BREACH or INJECT.", "BREACH")
        return
    scan_complete = True
    core_revealed = True
    core_materialize = 0.0
    core_scan_timer = 130
    system_messages.clear()
    trace_active = True
    system_status = "TARGET LOCKED"
    set_objective("Mainframe core revealed. Type BREACH to damage it.", "BREACH")
    banner("TARGET ACQUIRED", current_theme["flash"], 120)
    add_system_message("SCAN COMPLETE. MAINFRAME CORE FOUND.", current_theme["bright"], timer=700)
    add_system_message("FIREWALL ONLINE. TRACE MONITOR ACTIVE.", (255, 180, 0), timer=700)
    spawn_word_rain_from_text("TARGET ACQUIRED")
    spawn_particles(WIDTH // 2, HEIGHT // 2, 70, current_theme["bright"], spread=6.0)
    trigger_shake(2, 20)
    score_manager.hack()
    score_manager.add_score(80, WIDTH // 2 - 20, HEIGHT // 2 + 150, label="SCAN +80")
    unlock_achievement("scanner_online")
    play_hack_sound()


def start_extraction():
    global extraction_active, extraction_progress, extraction_stability, system_status
    if extraction_active:
        add_system_message("EXTRACTION ALREADY RUNNING", current_theme["main"], timer=360)
        return
    if cipher_lock_active:
        add_system_message("EXTRACTION BLOCKED BY CIPHER LOCK", (255, 180, 0), timer=520)
        set_objective("Type DECRYPT to break the active cipher lock.", "DECRYPT")
        raise_trace(6, "BLOCKED EXTRACTION")
        return
    if mainframe_integrity > 12:
        add_system_message("EXTRACT FAILED. CORE INTEGRITY TOO HIGH.", (255, 180, 0), timer=520)
        add_system_message("LOWER CORE BELOW 12% OR BREAK IT COMPLETELY.", (255, 180, 0), timer=520)
        raise_trace(8, "FAILED EXTRACTION")
        trigger_shake(3, 24)
        return
    extraction_active = True
    extraction_progress = 0.0
    extraction_stability = 100.0
    system_status = "EXTRACTION ACTIVE"
    set_objective("Extraction running. Use SUPPRESS if TRACE spikes.", "SUPPRESS")
    banner("EXTRACTION STARTED", current_theme["flash"], 120)
    add_system_message("ROOT PAYLOAD EXTRACTION STARTED", current_theme["flash"], timer=720)
    spawn_word_rain_from_text("EXTRACTION STARTED")
    spawn_particles(WIDTH // 2, HEIGHT // 2, 100, current_theme["flash"], spread=6.0)
    play_hack_sound()


def break_cipher_lock():
    global cipher_lock_active, cipher_lock_name, system_status
    if not cipher_lock_active:
        add_system_message("NO ACTIVE CIPHER LOCK", current_theme["main"], timer=360)
        return
    name = cipher_lock_name or "CIPHER LOCK"
    cipher_lock_active = False
    cipher_lock_name = ""
    system_status = "CIPHER BROKEN"
    add_system_message(f"{name} BROKEN. FIREWALL PATH OPEN.", current_theme["flash"], timer=720)
    set_objective("Cipher broken. Continue BREACH or INJECT.", "BREACH")
    spawn_word_rain_from_text("CIPHER BROKEN")
    spawn_particles(WIDTH // 2, HEIGHT // 2, 90, current_theme["flash"], spread=7.0)
    trigger_shake(4, 35)
    unlock_achievement("first_cipher")



def ambient_free_hack(text):
    """Old-school free hack mode before SCAN starts the actual breach run.

    This keeps VisionBreaker from punishing players before the objective mode begins.
    Random typed words become codefall echoes. Only SCAN starts the real mainframe run.
    """
    cleaned = text.strip()
    if not cleaned:
        return

    display = cleaned.upper()
    if len(display) > 36:
        display = display[:36] + "..."

    spawn_word_rain_from_text(cleaned)
    spawn_particles(WIDTH // 2, HEIGHT // 2, 18, current_theme["bright"], spread=3.5)
    banner("SIGNAL ECHO", current_theme["bright"], 65)
    add_system_message(f"ECHO STREAM ACCEPTED: {display}", current_theme["main"], timer=420)
    add_system_message("TYPE SCAN WHEN YOU ARE READY TO START THE BREACH.", current_theme["bright"], timer=420)

    # Small ambient reward, but no combo push, no TRACE penalty, and no fail sound.
    ambient_points = min(75, 10 + len(cleaned) * 2)
    score_manager.add_score(ambient_points, WIDTH // 2 - 20, HEIGHT - 110, label=f"ECHO +{ambient_points}")
    play_hack_sound()


def generate_vault_nodes():
    """Create visible Level 2 data fragments and corrupted decoys."""
    global vault_nodes, vault_locked_index, vault_fragments_extracted
    global vault_lockdown, vault_ping_timer, vault_mask_timer, vault_decrypt_pending

    vault_nodes = []
    vault_locked_index = None
    vault_fragments_extracted = 0
    vault_lockdown = 0.0
    vault_ping_timer = 0
    vault_mask_timer = 0
    vault_decrypt_pending = False

    labels = list("ABCDEFG")
    kinds = ["data", "data", "data", "corrupt", "data", "decoy", "data"]
    names = [
        "MEMORY FRAGMENT",
        "IDENTITY CACHE",
        "ROUTING TABLE",
        "CORRUPTED PACKET",
        "ACCESS TOKEN",
        "DECOY MIRROR",
        "ROOT SEED",
    ]

    cx, cy = WIDTH // 2, HEIGHT // 2
    rx = min(470, max(280, WIDTH // 4))
    ry = min(230, max(150, HEIGHT // 4))

    for i, label in enumerate(labels):
        angle = -math.pi / 2 + i * (math.pi * 2 / len(labels))
        x = cx + math.cos(angle) * rx
        y = cy + math.sin(angle) * ry
        vault_nodes.append({
            "label": label,
            "kind": kinds[i],
            "name": names[i],
            "x": float(x),
            "y": float(y),
            "known": False,
            "decrypted": False,
            "downloaded": False,
            "purged": False,
            "pulse": random.random() * 10.0,
        })


def start_vault_level():
    """Start Level 2 after the main breach is cleared."""
    global level_stage, level1_complete, vault_active, vault_complete
    global root_access, system_lockout, system_status, trace_level, trace_active
    global core_revealed, core_materialize, hack_input_mode, hack_buffer
    global game_mode, extraction_active, vault_intro_timer

    level_stage = 2
    level1_complete = True
    vault_active = True
    vault_complete = False
    root_access = False
    system_lockout = False
    trace_level = 0.0
    trace_active = False
    core_revealed = False
    core_materialize = 0.0
    extraction_active = False
    game_mode = "free"
    hack_input_mode = True
    hack_buffer = ""
    vault_intro_timer = 180

    generate_vault_nodes()
    system_messages.clear()
    system_status = "DATA VAULT INFILTRATION"
    set_objective("Level 2: PING the vault, LOCK a fragment, DECRYPT it, then DOWNLOAD it.", "PING")
    banner("LEVEL 2: DATA VAULT", current_theme["flash"], 180)
    spawn_word_rain_from_text("DATA VAULT OPEN")
    spawn_word_rain_from_text("FRAGMENTS DETECTED")
    spawn_particles(WIDTH // 2, HEIGHT // 2, 140, current_theme["flash"], spread=8.0)
    trigger_shake(4, 45)
    add_system_message("DATA VAULT ONLINE. EXTRACT 5 FRAGMENTS BEFORE LOCKDOWN.", current_theme["flash"], timer=900)
    add_system_message("TYPE PING TO IDENTIFY DATA, CORRUPT, AND DECOY NODES.", current_theme["bright"], timer=900)
    play_hack_sound()


def vault_lockdown_color():
    ratio = vault_lockdown / vault_max_lockdown
    if ratio < 0.5:
        return current_theme["bright"]
    if ratio < 0.8:
        return (255, 200, 0)
    return (255, 60, 40)


def raise_vault_lockdown(amount, reason="VAULT LOCKDOWN"):
    """Increase Level 2 pressure."""
    global vault_lockdown, screen_pulse_timer, core_alarm_timer
    if vault_complete or system_lockout:
        return
    vault_lockdown = max(0.0, min(vault_max_lockdown, vault_lockdown + amount))
    screen_pulse_timer = max(screen_pulse_timer, 28)
    core_alarm_timer = max(core_alarm_timer, 45)
    add_system_message(f"{reason}: LOCKDOWN +{int(amount)}", (255, 80, 40), timer=460)
    if vault_lockdown >= vault_max_lockdown:
        trigger_vault_lockdown()


def reduce_vault_lockdown(amount, reason="VAULT MASK"):
    global vault_lockdown
    old = vault_lockdown
    vault_lockdown = max(0.0, vault_lockdown - amount)
    reduced = int(old - vault_lockdown)
    if reduced > 0:
        add_system_message(f"{reason}: LOCKDOWN -{reduced}", current_theme["bright"], timer=420)
        spawn_particles(WIDTH // 2, HEIGHT // 2, 40, current_theme["main"], spread=4.0)


def get_vault_node(label):
    label = label.strip().upper()
    for i, node in enumerate(vault_nodes):
        if node["label"] == label:
            return i, node
    return None, None


def current_vault_node():
    if vault_locked_index is None:
        return None
    if 0 <= vault_locked_index < len(vault_nodes):
        return vault_nodes[vault_locked_index]
    return None


def complete_vault_decryption():
    """Called when a cipher answer is correct during Level 2."""
    global vault_decrypt_pending, game_mode, hack_input_mode, hack_buffer
    global current_puzzle_index, puzzle_message, puzzle_full_line
    node = current_vault_node()
    if node is None:
        vault_decrypt_pending = False
        game_mode = "free"
        hack_input_mode = True
        hack_buffer = ""
        return

    node["decrypted"] = True
    vault_decrypt_pending = False
    game_mode = "free"
    hack_input_mode = True
    hack_buffer = ""
    puzzle_message = ""
    puzzle_full_line = ""

    spawn_word_rain_from_text(f"{node['label']} DECRYPTED")
    spawn_particles(node["x"], node["y"], 90, current_theme["flash"], spread=7.0)
    reduce_vault_lockdown(12, "FRAGMENT DECRYPTED")
    score_manager.hack()
    score_manager.add_score(260, node["x"], node["y"] - 50, label="DECRYPT +260")
    add_system_message(f"FRAGMENT {node['label']} DECRYPTED. TYPE DOWNLOAD.", current_theme["flash"], timer=720)
    set_objective(f"Fragment {node['label']} is decrypted. Type DOWNLOAD to extract it.", "DOWNLOAD")
    banner(f"FRAGMENT {node['label']} DECRYPTED", current_theme["flash"], 110)
    play_hack_sound()

    register_cipher_solved()


def complete_vault_level():
    """Final completion for Level 2."""
    global vault_complete, vault_active, root_access, system_status, hack_input_mode, hack_buffer
    global level_stage
    if vault_complete:
        return
    clear_cipher_state()
    vault_complete = True
    vault_active = False
    root_access = True
    level_stage = 2
    hack_input_mode = False
    hack_buffer = ""
    system_status = "DATA VAULT CLEARED"
    set_objective("Data vault cleared. Press ENTER to start Level 3 Countertrace Defense.", "DEFENSE")
    banner("LEVEL 2 COMPLETE", current_theme["flash"], 200)
    spawn_word_rain_from_text("DATA VAULT CLEARED")
    spawn_word_rain_from_text("COUNTERTRACE INBOUND")
    spawn_particles(WIDTH // 2, HEIGHT // 2, 180, current_theme["flash"], spread=9.0)
    trigger_shake(7, 85)
    score_manager.hack()
    score_manager.add_score(2400, WIDTH // 2 - 50, HEIGHT // 2 - 140, label="VAULT +2400")

    if vault_lockdown <= 35:
        unlock_achievement("clean_vault")

    unlock_theme_count(14, "LEVEL 2 COMPLETE")
    unlock_achievement("vault_runner")

    add_system_message("ALL DATA FRAGMENTS EXTRACTED. COUNTERTRACE SWARM INBOUND.", current_theme["flash"], timer=1000)
    add_system_message("PRESS ENTER OR TYPE DEFENSE TO START LEVEL 3.", current_theme["bright"], timer=1000)
    play_hack_sound()


def trigger_vault_lockdown():
    """Lose state for Level 2."""
    global system_lockout, vault_active, system_status, hack_input_mode, hack_buffer
    global critical_error_timer, critical_glitch_intensity
    if system_lockout or vault_complete:
        return
    clear_cipher_state()
    system_lockout = True
    vault_active = True
    system_status = "VAULT LOCKDOWN"
    hack_input_mode = False
    hack_buffer = ""
    critical_error_timer = 190
    critical_glitch_intensity = 8
    trigger_shake(8, critical_error_timer)
    set_objective("Vault locked down. Press ENTER to restart.", "RESET")
    banner("VAULT LOCKDOWN", (255, 60, 40), 180)
    spawn_word_rain_from_text("VAULT LOCKDOWN")
    spawn_word_rain_from_text("DATA LOST")
    spawn_particles(WIDTH // 2, HEIGHT // 2, 140, (255, 0, 0), spread=8.0)
    add_system_message("VAULT LOCKDOWN. DATA STREAM TERMINATED.", (255, 60, 40), timer=900)
    play_error_sound()



# ================== LEVEL 3: COUNTERTRACE DEFENSE ==================
def make_math_threat():
    """Create a math packet for Level 3. Difficulty scales by defense wave."""

    # Wave 1: addition only, beginner friendly
    if defense_wave <= 1:
        a = random.randint(2, 10)
        b = random.randint(2, 10)
        return f"{a}+{b}", str(a + b)

    # Wave 2: addition and easy subtraction
    if defense_wave == 2:
        op = random.choice(["+", "-"])
        if op == "+":
            a = random.randint(2, 14)
            b = random.randint(2, 14)
            return f"{a}+{b}", str(a + b)

        a = random.randint(8, 20)
        b = random.randint(1, min(9, a - 1))
        return f"{a}-{b}", str(a - b)

    # Wave 3: introduce easy multiplication
    if defense_wave == 3:
        op = random.choice(["+", "-", "x"])
        if op == "x":
            a = random.randint(2, 5)
            b = random.randint(2, 5)
            return f"{a}x{b}", str(a * b)
        if op == "+":
            a = random.randint(5, 18)
            b = random.randint(5, 18)
            return f"{a}+{b}", str(a + b)

        a = random.randint(12, 28)
        b = random.randint(2, min(12, a - 1))
        return f"{a}-{b}", str(a - b)

    # Wave 4+: full mixed math
    op = random.choice(["+", "-", "x"])
    if op == "+":
        a = random.randint(8, 25)
        b = random.randint(8, 25)
        return f"{a}+{b}", str(a + b)

    if op == "-":
        a = random.randint(15, 35)
        b = random.randint(2, min(18, a - 1))
        return f"{a}-{b}", str(a - b)

    a = random.randint(2, 9)
    b = random.randint(2, 9)
    return f"{a}x{b}", str(a * b)


def start_defense_level():
    """Start Level 3, a typing-shooter defense during final escape."""
    global level_stage, defense_active, defense_complete, defense_threats, defense_lasers
    global defense_progress, defense_shield, defense_spawn_timer, defense_intro_timer
    global defense_wave, defense_hits, defense_misses, defense_wrong_inputs, defense_typed_commands
    global root_access, system_lockout, system_status, hack_input_mode, hack_buffer, game_mode

    level_stage = 3
    defense_active = True
    defense_complete = False
    defense_threats = []
    defense_lasers = []
    defense_progress = 0.0
    defense_shield = defense_max_shield
    defense_spawn_timer = DEFENSE_START_DELAY
    defense_intro_timer = 180
    defense_wave = 1
    defense_hits = 0
    defense_misses = 0
    defense_wrong_inputs = 0
    defense_typed_commands = 0

    root_access = False
    system_lockout = False
    system_status = "COUNTERTRACE DEFENSE"
    game_mode = "free"
    hack_input_mode = True
    hack_buffer = ""

    system_messages.clear()
    set_objective("Level 3: type threat words or math answers before packets hit the stream.", "TYPE TARGETS")
    banner("LEVEL 3: COUNTERTRACE DEFENSE", current_theme["flash"], 190)
    spawn_word_rain_from_text("COUNTERTRACE DEFENSE")
    spawn_word_rain_from_text("FINAL ESCAPE STREAM")
    spawn_particles(WIDTH // 2, HEIGHT // 2, 170, current_theme["flash"], spread=9.0)
    trigger_shake(5, 60)
    add_system_message("FINAL ESCAPE STREAM OPEN. DEFEND IT BY TYPING FALLING TARGETS.", current_theme["flash"], timer=1000)
    add_system_message("WORDS DESTROY PACKETS. MATH PACKETS REQUIRE THE ANSWER. EXAMPLE: 8+7 MEANS TYPE 15.", current_theme["bright"], timer=1000)
    play_hack_sound()


def defense_threat_color(kind):
    if kind == "math":
        return (255, 200, 0)
    if kind == "virus":
        return (255, 70, 50)
    if kind == "lockout":
        return (255, 120, 255)
    return current_theme["bright"]


def spawn_defense_threat():
    """Spawn a falling target packet for the typing defense."""
    global defense_last_spawn_id
    defense_last_spawn_id += 1

    word_pool = [
        "TRACE", "VIRUS", "DAEMON", "FIREWALL", "PACKET", "LOCKOUT", "BREACH",
        "CIPHER", "WATCHDOG", "SIGNAL", "OVERRIDE", "KERNEL", "PROXY", "GATEWAY",
        "NEUROGRID", "PAYLOAD", "SUPPRESS", "ROUTER", "TOKEN", "MIRROR",
    ]

    kind_roll = random.random()
    if defense_math_enabled and kind_roll < 0.28:
        text, answer = make_math_threat()
        kind = "math"
    else:
        text = random.choice(word_pool)
        answer = text
        if text in ("VIRUS", "DAEMON", "WATCHDOG"):
            kind = "virus"
        elif text in ("LOCKOUT", "FIREWALL"):
            kind = "lockout"
        else:
            kind = "word"

    margin = 90
    x = random.randint(margin, max(margin, WIDTH - margin))
    y = -random.randint(40, 180)
    base_speed = 1.05 + defense_wave * 0.22

    if kind == "math":
        base_speed *= 0.82

    if kind in ("virus", "lockout"):
        base_speed *= 1.02

    base_speed *= DEFENSE_THREAT_SPEED_SCALE

    defense_threats.append({
        "id": defense_last_spawn_id,
        "text": text,
        "answer": answer.upper(),
        "kind": kind,
        "x": float(x),
        "y": float(y),
        "speed": random.uniform(base_speed, base_speed + 0.75),
        "pulse": random.random() * 10.0,
    })


def add_defense_laser(x, y, color=None):
    if color is None:
        color = current_theme["flash"]
    defense_lasers.append({
        "x1": WIDTH // 2,
        "y1": HEIGHT - 42,
        "x2": float(x),
        "y2": float(y),
        "timer": 14,
        "color": color,
    })


def trigger_defense_failure():
    """Lose state for Level 3."""
    global system_lockout, defense_active, system_status, hack_input_mode, hack_buffer
    global critical_error_timer, critical_glitch_intensity
    if system_lockout or defense_complete:
        return
    clear_cipher_state()
    system_lockout = True
    defense_active = True
    system_status = "ESCAPE STREAM LOST"
    hack_input_mode = False
    hack_buffer = ""
    critical_error_timer = 210
    critical_glitch_intensity = 9
    trigger_shake(9, critical_error_timer)
    set_objective("Countertrace broke the stream. Press ENTER to restart.", "RESET")
    banner("COUNTERTRACE OVERRUN", (255, 60, 40), 200)
    spawn_word_rain_from_text("COUNTERTRACE OVERRUN")
    spawn_word_rain_from_text("ESCAPE STREAM LOST")
    spawn_particles(WIDTH // 2, HEIGHT // 2, 180, (255, 0, 0), spread=9.0)
    add_system_message("ESCAPE STREAM COLLAPSED. COUNTERTRACE WON.", (255, 60, 40), timer=1000)
    play_error_sound()


def complete_defense_level():
    """Final win state after Level 3."""
    global defense_complete, defense_active, root_access, system_status, hack_input_mode, hack_buffer
    if defense_complete:
        return
    clear_cipher_state()
    defense_complete = True
    defense_active = False
    root_access = True
    hack_input_mode = False
    hack_buffer = ""
    system_status = "NEUROGRID ESCAPED"
    set_objective("Final escape complete. Press ENTER to jack in again.", "RESET")
    banner("FINAL ESCAPE COMPLETE", current_theme["flash"], 230)
    spawn_word_rain_from_text("FINAL ESCAPE COMPLETE")
    spawn_word_rain_from_text("NEUROGRID ESCAPED")
    spawn_particles(WIDTH // 2, HEIGHT // 2, 220, current_theme["flash"], spread=10.0)
    trigger_shake(8, 90)
    score_manager.hack()
    score_manager.add_score(3200, WIDTH // 2 - 50, HEIGHT // 2 - 150, label="ESCAPE +3200")

    if defense_misses == 0:
        unlock_achievement("perfect_escape")

    unlock_achievement("countertrace_defender")
    unlock_achievement("full_run")
    unlock_theme_count(len(COLOR_THEMES), "FULL RUN COMPLETE")

    accuracy = int((defense_hits / max(1, defense_hits + defense_wrong_inputs + defense_misses)) * 100)
    add_system_message(f"FINAL ESCAPE COMPLETE. ACCURACY {accuracy}% | HITS {defense_hits} | MISSES {defense_misses}.", current_theme["flash"], timer=1200)
    play_hack_sound()


def process_defense_input(command_text):
    """Level 3 handler. Player types the falling threat word or math answer."""
    global defense_shield, defense_wrong_inputs, defense_typed_commands, defense_hits, defense_progress
    cleaned = command_text.strip().upper()
    if not cleaned:
        return

    if system_lockout or defense_complete:
        if cleaned in ("RESET", "RESTART", "REBOOT", "SCAN"):
            reset_mainframe_run(reset_score=False)
        else:
            add_system_message("SESSION CLOSED. PRESS ENTER OR TYPE RESET.", current_theme["flash"], timer=520)
        return

    if cleaned in ("HELP", "COMMANDS", "?"):
        add_system_message("LEVEL 3: TYPE THE FALLING WORDS TO SHOOT THEM.", current_theme["flash"], timer=900)
        add_system_message("MATH PACKETS SHOW EQUATIONS. TYPE THE ANSWER, NOT THE EQUATION.", current_theme["bright"], timer=900)
        add_system_message("STATUS SHOWS ACCURACY. RESET RESTARTS THE RUN.", current_theme["bright"], timer=900)
        set_objective("Type the falling targets before they hit the escape stream.", "TYPE TARGETS")
        return

    if cleaned == "STATUS":
        accuracy = int((defense_hits / max(1, defense_hits + defense_wrong_inputs + defense_misses)) * 100)
        add_system_message(f"DEFENSE {int(defense_progress)}% | SHIELD {int(defense_shield)}% | WAVE {defense_wave} | ACC {accuracy}%", current_theme["bright"], timer=800)
        return

    defense_typed_commands += 1

    # Choose the matching threat closest to the bottom, so repeated words feel fair.
    matches = [t for t in defense_threats if t["answer"] == cleaned or t["text"].upper() == cleaned]
    if matches:
        target = max(matches, key=lambda t: t["y"])
        color = defense_threat_color(target["kind"])
        defense_threats.remove(target)
        defense_hits += 1
        if target["kind"] == "math":
            unlock_achievement("math_destroyer")

        if target["kind"] in ("virus", "lockout"):
            unlock_achievement("virus_hunter")
        add_defense_laser(target["x"], target["y"], color)
        spawn_particles(target["x"], target["y"], 70 if target["kind"] != "word" else 48, color, spread=6.5)
        spawn_word_rain_from_text(f"{target['text']} NEUTRALIZED")
        defense_progress = min(defense_progress_max, defense_progress + (4.4 if target["kind"] != "word" else 3.2))
        defense_shield = min(defense_max_shield, defense_shield + 1.6)
        score_manager.hack()
        pts = 180 if target["kind"] == "math" else (150 if target["kind"] in ("virus", "lockout") else 110)
        score_manager.add_score(pts, target["x"], target["y"] - 30, label=f"HIT +{int(pts * score_manager.multiplier)}")
        banner("TARGET NEUTRALIZED", current_theme["flash"], 65)
        play_hack_sound()
        if score_manager.multiplier >= 5.0:
            unlock_achievement("combo_master")
        if defense_progress >= defense_progress_max:
            complete_defense_level()
        return

    defense_wrong_inputs += 1
    defense_shield = max(0.0, defense_shield - 5.0)
    score_manager.break_combo()
    banner("MISFIRE", (255, 80, 40), 70)
    add_system_message(f"NO TARGET MATCHED: {cleaned}. SHIELD -5", (255, 80, 40), timer=420)
    spawn_particles(WIDTH // 2, HEIGHT - 60, 25, (255, 0, 0), spread=4.5)
    trigger_shake(2, 14)
    play_error_sound()
    if defense_shield <= 0:
        trigger_defense_failure()


def update_defense_level(dt_scale, dt_sec):
    """Update Level 3 threats, escape progress, and failure checks."""
    global defense_spawn_timer, defense_progress, defense_shield, defense_wave, defense_misses, defense_intro_timer

    if not defense_active or defense_complete or system_lockout:
        return

    defense_intro_timer = max(0, defense_intro_timer - 1 * dt_scale)
    defense_wave = min(5, 1 + int(defense_progress // DEFENSE_WAVE_PROGRESS_STEP))

    # Extraction stream progresses slowly by survival and faster through hits.
    defense_progress = min(defense_progress_max, defense_progress + (1.15 + defense_wave * 0.12) * dt_sec)
    if defense_progress >= defense_progress_max:
        complete_defense_level()
        return

    # Spawn pressure rises with wave, but starts much more manageable.
    defense_spawn_timer -= 1 * dt_scale

    if defense_spawn_timer <= 0:
        threat_cap = 2 + defense_wave  # wave 1 = 3 threats max, wave 5 = 7 threats max

        if len(defense_threats) < threat_cap:
            spawn_defense_threat()

        defense_spawn_timer = max(
            DEFENSE_MIN_SPAWN_FRAMES,
            DEFENSE_BASE_SPAWN_FRAMES
            - defense_wave * DEFENSE_WAVE_SPAWN_STEP
            - min(10.0, defense_hits * DEFENSE_HIT_SPAWN_STEP),
        )

        # Rare double-spawns only later, and only if the screen is not already crowded.
        if (
            defense_wave >= DEFENSE_EXTRA_SPAWN_WAVE
            and len(defense_threats) < threat_cap
            and random.random() < DEFENSE_EXTRA_SPAWN_CHANCE
        ):
            spawn_defense_threat()

    for threat in defense_threats[:]:
        threat["y"] += threat["speed"] * dt_scale
        threat["pulse"] += 0.08 * dt_scale
        if threat["y"] > HEIGHT - 52:
            defense_threats.remove(threat)
            defense_misses += 1
            loss = 16.0 if threat["kind"] in ("virus", "lockout") else 11.0
            defense_shield = max(0.0, defense_shield - loss)
            add_system_message(f"{threat['text']} HIT THE STREAM. SHIELD -{int(loss)}", (255, 80, 40), timer=520)
            spawn_particles(threat["x"], HEIGHT - 52, 55, (255, 0, 0), spread=6.5)
            trigger_shake(3, 20)
            play_error_sound()
            if defense_shield <= 0:
                trigger_defense_failure()
                return

    for laser in defense_lasers[:]:
        laser["timer"] -= 1 * dt_scale
        if laser["timer"] <= 0:
            defense_lasers.remove(laser)


def process_vault_command(command_text):
    """Level 2 command handler. Different loop from Level 1."""
    global vault_locked_index, vault_ping_timer, vault_mask_timer, vault_decrypt_pending, vault_fragments_extracted

    cleaned = command_text.strip()
    if not cleaned:
        return
    parts = cleaned.upper().split()
    command = parts[0]

    if system_lockout or vault_complete:
        if command in ("RESET", "RESTART", "REBOOT", "SCAN"):
            reset_mainframe_run(reset_score=False)
        else:
            add_system_message("SESSION CLOSED. PRESS ENTER OR TYPE RESET.", current_theme["flash"], timer=520)
        return

    if command in ("HELP", "COMMANDS", "?"):
        add_system_message("VAULT COMMANDS: PING, LOCK A-G, DECRYPT, DOWNLOAD, PURGE, MASK, STATUS", current_theme["flash"], timer=900)
        add_system_message("GOAL: EXTRACT 5 REAL DATA FRAGMENTS BEFORE LOCKDOWN HITS 100%.", current_theme["bright"], timer=900)
        set_objective("PING the vault, LOCK a data fragment, DECRYPT it, then DOWNLOAD it.", "PING")
        return

    if command == "STATUS":
        locked = current_vault_node()
        locked_text = locked["label"] if locked else "NONE"
        add_system_message(
            f"FRAGMENTS {vault_fragments_extracted}/{vault_fragments_required} | LOCKDOWN {int(vault_lockdown)}% | LOCKED {locked_text}",
            current_theme["bright"], timer=720,
        )
        return

    if command == "PING":
        vault_ping_timer = 420
        for node in vault_nodes:
            if not node["downloaded"] and not node["purged"]:
                node["known"] = True
        banner("VAULT PING", current_theme["flash"], 95)
        spawn_word_rain_from_text("VAULT PING")
        spawn_particles(WIDTH // 2, HEIGHT // 2, 60, current_theme["bright"], spread=5.0)
        score_manager.hack()
        score_manager.add_score(90, WIDTH // 2 - 30, HEIGHT // 2 + 150, label="PING +90")
        unlock_achievement("vault_ping")
        add_system_message("PING COMPLETE. LOCK A-G TO SELECT A NODE.", current_theme["bright"], timer=760)
        set_objective("Choose a visible data node. Example: LOCK A", "LOCK A")
        play_hack_sound()
        return

    if command == "LOCK":
        if len(parts) < 2:
            add_system_message("LOCK NEEDS A NODE LABEL. EXAMPLE: LOCK A", (255, 180, 0), timer=620)
            set_objective("Type LOCK plus a node letter. Example: LOCK A", "LOCK A")
            return
        idx, node = get_vault_node(parts[1])
        if node is None:
            add_system_message("UNKNOWN NODE. VALID LABELS: A B C D E F G", (255, 180, 0), timer=620)
            raise_vault_lockdown(4, "BAD NODE LOCK")
            return
        if node["downloaded"]:
            add_system_message(f"NODE {node['label']} ALREADY DOWNLOADED", current_theme["main"], timer=460)
            return
        if node["purged"]:
            add_system_message(f"NODE {node['label']} ALREADY PURGED", current_theme["main"], timer=460)
            return
        vault_locked_index = idx
        node["known"] = True
        spawn_particles(node["x"], node["y"], 45, current_theme["bright"], spread=5.0)
        banner(f"LOCKED NODE {node['label']}", current_theme["flash"], 90)
        add_system_message(f"LOCKED NODE {node['label']}: {node['name']}", current_theme["bright"], timer=700)
        if node["kind"] == "corrupt":
            set_objective(f"Node {node['label']} is corrupt. Type PURGE to remove it.", "PURGE")
            add_system_message("CORRUPTED PACKET DETECTED. PURGE RECOMMENDED.", (255, 180, 0), timer=700)
        elif node["kind"] == "decoy":
            set_objective(f"Node {node['label']} looks suspicious. PING again or PURGE it.", "PURGE")
            add_system_message("DECOY MIRROR DETECTED. DOWNLOAD WOULD WASTE TIME.", (255, 180, 0), timer=700)
        elif node["decrypted"]:
            set_objective(f"Node {node['label']} already decrypted. Type DOWNLOAD.", "DOWNLOAD")
        else:
            set_objective(f"Node {node['label']} locked. Type DECRYPT to open its cipher.", "DECRYPT")
        play_hack_sound()
        return

    if command == "DECRYPT":
        node = current_vault_node()
        if node is None:
            add_system_message("NO NODE LOCKED. TYPE PING THEN LOCK A-G.", (255, 180, 0), timer=620)
            set_objective("No vault node locked. Type PING, then LOCK A-G.", "PING")
            return
        if node["kind"] in ("corrupt", "decoy"):
            add_system_message(f"NODE {node['label']} IS NOT VALID DATA. PURGE IT.", (255, 180, 0), timer=620)
            raise_vault_lockdown(8, "BAD DECRYPT TARGET")
            set_objective(f"Node {node['label']} is unsafe. Type PURGE.", "PURGE")
            return
        if node["decrypted"]:
            add_system_message(f"NODE {node['label']} ALREADY DECRYPTED. TYPE DOWNLOAD.", current_theme["bright"], timer=620)
            set_objective(f"Node {node['label']} decrypted. Type DOWNLOAD.", "DOWNLOAD")
            return
        vault_decrypt_pending = True
        add_system_message(f"DECRYPTING FRAGMENT {node['label']}. CIPHER PANEL OPENED.", current_theme["flash"], timer=720)
        set_objective(f"Solve the cipher to decrypt fragment {node['label']}.", "TYPE ANSWER")
        start_puzzle_mode()
        return

    if command == "DOWNLOAD":
        node = current_vault_node()
        if node is None:
            add_system_message("NO NODE LOCKED. TYPE LOCK A-G FIRST.", (255, 180, 0), timer=620)
            return
        if node["kind"] == "corrupt":
            add_system_message("CORRUPTED PACKET CANNOT BE DOWNLOADED. PURGE IT.", (255, 80, 40), timer=620)
            raise_vault_lockdown(12, "CORRUPT DOWNLOAD")
            return
        if node["kind"] == "decoy":
            add_system_message("DECOY DOWNLOAD FAILED. LOCKDOWN SPIKE.", (255, 80, 40), timer=620)
            node["purged"] = True
            raise_vault_lockdown(14, "DECOY TRIGGERED")
            spawn_particles(node["x"], node["y"], 60, (255, 80, 40), spread=6.0)
            return
        if not node["decrypted"]:
            add_system_message(f"NODE {node['label']} STILL ENCRYPTED. TYPE DECRYPT FIRST.", (255, 180, 0), timer=620)
            set_objective(f"Node {node['label']} needs decryption before download.", "DECRYPT")
            return
        if node["downloaded"]:
            add_system_message(f"NODE {node['label']} ALREADY EXTRACTED", current_theme["main"], timer=460)
            return
        node["downloaded"] = True
        vault_fragments_extracted += 1
        unlock_achievement("first_download")
        banner(f"FRAGMENT {node['label']} DOWNLOADED", current_theme["flash"], 115)
        spawn_word_rain_from_text(f"FRAGMENT {node['label']} EXTRACTED")
        spawn_particles(node["x"], node["y"], 110, current_theme["flash"], spread=7.5)
        reduce_vault_lockdown(8, "DATA EXTRACTED")
        score_manager.hack()
        score_manager.add_score(420, node["x"], node["y"] - 50, label="DATA +420")
        add_system_message(f"FRAGMENT {vault_fragments_extracted}/{vault_fragments_required} EXTRACTED.", current_theme["flash"], timer=760)
        play_hack_sound()
        if vault_fragments_extracted >= vault_fragments_required:
            complete_vault_level()
        else:
            set_objective("Extract another fragment. Type PING or LOCK another node.", "PING")
        return

    if command == "PURGE":
        node = current_vault_node()
        if node is None:
            add_system_message("NO NODE LOCKED. TYPE LOCK A-G FIRST.", (255, 180, 0), timer=620)
            return
        if node["downloaded"]:
            add_system_message("NODE ALREADY DOWNLOADED. NO PURGE NEEDED.", current_theme["main"], timer=420)
            return
        if node["kind"] in ("corrupt", "decoy"):
            node["purged"] = True
            banner(f"NODE {node['label']} PURGED", current_theme["bright"], 95)
            spawn_word_rain_from_text(f"NODE {node['label']} PURGED")
            spawn_particles(node["x"], node["y"], 90, current_theme["main"], spread=6.5)
            reduce_vault_lockdown(10, "THREAT PURGED")
            score_manager.hack()
            score_manager.add_score(180, node["x"], node["y"] - 50, label="PURGE +180")
            add_system_message(f"UNSAFE NODE {node['label']} PURGED.", current_theme["bright"], timer=620)
            set_objective("Threat removed. PING or LOCK another data node.", "PING")
            play_hack_sound()
        else:
            add_system_message("PURGE WOULD DESTROY REAL DATA. COMMAND BLOCKED.", (255, 180, 0), timer=620)
            raise_vault_lockdown(5, "PURGE BLOCKED")
            set_objective("Real data needs DECRYPT then DOWNLOAD.", "DECRYPT")
        return

    if command == "MASK":
        vault_mask_timer = 360
        reduce_vault_lockdown(18, "VAULT MASK")
        banner("LOCKDOWN MASKED", current_theme["bright"], 95)
        spawn_word_rain_from_text("VAULT MASK ACTIVE")
        score_manager.hack()
        score_manager.add_score(100, WIDTH // 2 - 20, HEIGHT // 2 + 150, label="MASK +100")
        add_system_message("MASK ACTIVE. LOCKDOWN DRIFT SLOWED TEMPORARILY.", current_theme["bright"], timer=720)
        set_objective("Mask active. Continue extracting fragments.", "PING")
        play_hack_sound()
        return

    # If they type Level 1 commands in Level 2, guide them instead of punishing hard.
    if command in ("SCAN", "BREACH", "INJECT", "SUPPRESS", "EXTRACT"):
        add_system_message("LEVEL 2 USES VAULT COMMANDS: PING, LOCK, DECRYPT, DOWNLOAD, PURGE, MASK.", (255, 180, 0), timer=820)
        raise_vault_lockdown(3, "WRONG TOOL")
        set_objective("This is the Data Vault. Type PING to read the nodes.", "PING")
        return

    add_system_message(f"UNKNOWN VAULT COMMAND: {command}", (255, 60, 40), timer=520)
    add_system_message("TYPE HELP FOR VAULT COMMANDS.", current_theme["bright"], timer=520)
    raise_vault_lockdown(6, "INVALID VAULT INPUT")
    score_manager.break_combo()
    play_error_sound()


def process_mainframe_command(command_text):
    global system_status, core_alarm_timer
    cleaned = command_text.strip()
    if not cleaned:
        return
    command = cleaned.upper().split()[0]

    if defense_active:
        process_defense_input(cleaned)
        return

    if vault_active:
        process_vault_command(cleaned)
        return

    if root_access or system_lockout:
        if root_access and level1_complete and not vault_complete and command in ("VAULT", "NEXT", "CONTINUE", "ENTER", "SCAN"):
            start_vault_level()
        elif root_access and vault_complete and not defense_complete and command in ("DEFENSE", "DEFEND", "NEXT", "CONTINUE", "ENTER", "SCAN"):
            start_defense_level()
        elif command in ("RESET", "RESTART", "REBOOT", "SCAN"):
            reset_mainframe_run(reset_score=False)
        else:
            if root_access and vault_complete and not defense_complete:
                add_system_message("VAULT COMPLETE. TYPE DEFENSE OR PRESS ENTER TO START LEVEL 3.", current_theme["flash"], timer=620)
            else:
                add_system_message("LEVEL COMPLETE. TYPE VAULT TO CONTINUE OR RESET TO RESTART.", current_theme["flash"], timer=620)
        return

    if command in ("HELP", "COMMANDS", "?"):
        add_system_message("LEVEL 1 COMMANDS: SCAN, BREACH, INJECT, DECRYPT, SUPPRESS, STATUS, EXTRACT", current_theme["flash"], timer=820)
        add_system_message("LEVEL 2 COMMANDS: PING, LOCK A-G, DECRYPT, DOWNLOAD, PURGE, MASK", current_theme["bright"], timer=820)
        add_system_message("LEVEL 3: TYPE FALLING WORDS OR MATH ANSWERS TO DEFEND ESCAPE.", current_theme["bright"], timer=820)
        add_system_message("GOAL: BREAK IN, STEAL DATA, THEN DEFEND THE ESCAPE STREAM.", current_theme["bright"], timer=820)
        set_objective("Type SCAN if no target is visible. Then BREACH the core.", next_command)
        return

    if command == "STATUS":
        add_system_message(
            f"CORE {int(mainframe_integrity)}% | TRACE {int(trace_level)}% | ACCESS L{access_level} | NEXT {next_command}",
            current_theme["bright"], timer=620,
        )
        return

    if not scan_complete and command != "SCAN":
        # Before SCAN, the player is still in ambient/free-hack mode.
        # Do NOT punish random codefall typing here.
        ambient_free_hack(cleaned)
        return

    if command == "SCAN":
        start_scan_sequence()
        unlock_achievement("first_hack")
        return

    if command == "BREACH":
        damage = 8.0 + access_level * 1.6
        actual = damage_mainframe(damage, "FIREWALL BREACH")
        raise_trace(4.5 if not cipher_lock_active else 6.5, "COUNTERTRACE")
        banner("BREACH SENT", current_theme["bright"], 80)
        spawn_word_rain_from_text("FIREWALL BREACH")
        score_manager.hack()
        score_manager.add_score(130, WIDTH // 2 - 25, HEIGHT // 2 + 150, label=f"BREACH +{int(130 * score_manager.multiplier)}")
        if actual > 0:
            play_hack_sound()
        if score_manager.multiplier >= 5.0:
            unlock_achievement("combo_master")
        return

    if command == "INJECT":
        damage = 14.0 + access_level * 2.2
        damage_mainframe(damage, "PAYLOAD INJECTED")
        raise_trace(12.0 if not cipher_lock_active else 15.0, "AGGRESSIVE PAYLOAD")
        banner("PAYLOAD INJECTED", current_theme["flash"], 95)
        spawn_word_rain_from_text("PAYLOAD INJECTED")
        trigger_shake(4, 26)
        score_manager.hack()
        score_manager.add_score(210, WIDTH // 2 - 25, HEIGHT // 2 + 150, label=f"INJECT +{int(210 * score_manager.multiplier)}")
        play_hack_sound()
        if score_manager.multiplier >= 5.0:
            unlock_achievement("combo_master")
        return

    if command == "DECRYPT":
        if not cipher_lock_active and mainframe_integrity > 20:
            add_system_message("OPTIONAL DECRYPT OPENED. SOLVE TO DAMAGE CORE AND LOWER TRACE.", current_theme["bright"], timer=620)
        else:
            add_system_message("DECRYPTION CHALLENGE OPENED", current_theme["flash"], timer=620)
        banner("CIPHER CHALLENGE", current_theme["flash"], 95)
        score_manager.hack()
        score_manager.add_score(90, WIDTH // 2 - 20, HEIGHT // 2 + 150, label="DECRYPT +90")
        start_puzzle_mode()
        play_hack_sound()
        return

    if command == "SUPPRESS":
        if trace_level <= 0:
            add_system_message("TRACE ALREADY CLEAR", current_theme["main"], timer=360)
            banner("TRACE CLEAR", current_theme["main"], 70)
        else:
            reduce_trace(22.0, "TRACE MASK RESTORED")
            banner("TRACE SUPPRESSED", current_theme["bright"], 95)
            spawn_word_rain_from_text("TRACE SUPPRESSED")
            score_manager.hack()
            score_manager.add_score(70, WIDTH // 2 - 20, HEIGHT // 2 + 150, label="SUPPRESS +70")
            play_hack_sound()
        if extraction_active:
            set_objective("Extraction running. Keep TRACE under control.", "SUPPRESS")
        elif cipher_lock_active:
            set_objective("TRACE lowered. Type DECRYPT to break the cipher lock.", "DECRYPT")
        else:
            set_objective("Continue attacking with BREACH or INJECT.", "BREACH")
        return

    if command == "EXTRACT":
        start_extraction()
        return

    add_system_message(f"INVALID COMMAND: {command}", (255, 60, 40), timer=420)
    add_system_message("TYPE HELP FOR VALID COMMANDS", current_theme["bright"], timer=420)
    banner("INVALID COMMAND", (255, 60, 40), 90)
    score_manager.break_combo()
    raise_trace(7, "INVALID INPUT")
    spawn_particles(WIDTH // 2, HEIGHT // 2, 25, (255, 0, 0), spread=4.5)
    play_error_sound()


def update_mainframe_system():
    global system_chatter_timer, system_event_timer, trace_level, core_materialize
    global core_flash_timer, core_damage_timer, core_scan_timer, core_alarm_timer
    global screen_pulse_timer, command_banner_timer, extraction_progress, extraction_stability
    global system_status, vault_lockdown, vault_ping_timer, vault_mask_timer, vault_node_pulse, vault_intro_timer

    dt_scale = max(last_dt_ms, 16) / 16.0
    dt_sec = max(last_dt_ms, 16) / 1000.0

    for msg in system_messages[:]:
        msg["timer"] -= 1 * dt_scale
        if msg["timer"] <= 0:
            system_messages.remove(msg)

    core_flash_timer = max(0, core_flash_timer - 1 * dt_scale)
    core_damage_timer = max(0, core_damage_timer - 1 * dt_scale)
    core_scan_timer = max(0, core_scan_timer - 1 * dt_scale)
    core_alarm_timer = max(0, core_alarm_timer - 1 * dt_scale)
    screen_pulse_timer = max(0, screen_pulse_timer - 1 * dt_scale)
    command_banner_timer = max(0, command_banner_timer - 1 * dt_scale)
    vault_ping_timer = max(0, vault_ping_timer - 1 * dt_scale)
    vault_mask_timer = max(0, vault_mask_timer - 1 * dt_scale)
    vault_intro_timer = max(0, vault_intro_timer - 1 * dt_scale)
    vault_node_pulse += 0.045 * dt_scale

    if core_revealed:
        core_materialize = min(1.0, core_materialize + 0.018 * dt_scale)

    if defense_active:
        update_defense_level(dt_scale, dt_sec)
        if system_chatter_timer <= 0 and not system_lockout and not defense_complete:
            pass
        return

    if vault_active and not system_lockout and not vault_complete:
        if game_mode == "puzzle":
            return
        drift = 0.030
        if vault_mask_timer > 0:
            drift *= 0.30
        unsafe_live = sum(1 for n in vault_nodes if n["kind"] in ("corrupt", "decoy") and not n["purged"])
        drift += unsafe_live * 0.003
        vault_lockdown = max(0.0, min(vault_max_lockdown, vault_lockdown + drift * dt_scale))
        if vault_lockdown >= vault_max_lockdown:
            trigger_vault_lockdown()
            return
        system_chatter_timer -= last_dt_ms
        if system_chatter_timer <= 0:
            system_chatter_timer = random.randint(2400, 4800)
            if vault_lockdown >= 75:
                options = ["VAULT LOCKDOWN ESCALATING", "DATA SHUTTERS CLOSING", "DAEMON SWARM APPROACHING"]
            elif vault_fragments_extracted >= 3:
                options = ["VAULT WALLS DESTABILIZING", "ROOT DATA STREAM OPEN", "FINAL FRAGMENTS EXPOSED"]
            else:
                options = ["VAULT DAEMON LISTENING", "FRAGMENTS DRIFTING", "PING RECOMMENDED", "DECOY PACKETS ACTIVE"]
            add_system_message(random.choice(options), current_theme["main"], timer=360)
        return

    if root_access or system_lockout:
        return

    # When a cipher puzzle is open, the game pauses TRACE so the player can
    # actually read the prompt and answer without panic.
    if game_mode == "puzzle":
        return

    if scan_complete:
        drift = MAINFRAME_TRACE_DRIFT
        if cipher_lock_active:
            drift *= 2.4
        if extraction_active:
            drift *= 3.4
        trace_level += drift * dt_scale
        clamp_trace()
        if trace_level >= trace_max:
            trigger_system_lockout()
            return

    if extraction_active:
        extraction_progress += 10.5 * dt_sec
        extraction_stability = max(0.0, 100.0 - trace_level * 0.55)
        if random.random() < 0.04:
            spawn_particles(WIDTH // 2, HEIGHT // 2, 8, current_theme["flash"], spread=3.0)
        if extraction_progress >= 100.0:
            complete_root_access()
            return

    system_chatter_timer -= last_dt_ms
    if system_chatter_timer <= 0:
        system_chatter_timer = random.randint(2600, 5200)
        if not scan_complete:
            options = ["NEUROGRID LISTENING", "NO TARGET MAP LOADED", "AWAITING SCAN COMMAND"]
        elif extraction_active:
            options = ["DATA STREAM OPEN", "ROOT PAYLOAD TRANSFERRING", "TRACE WATCHDOG ACTIVE"]
        elif cipher_lock_active:
            options = [f"{cipher_lock_name} HOLDING", "ENCRYPTED SHIELD ACTIVE", "DECRYPT REQUIRED"]
        elif trace_level >= 75:
            options = ["TRACE VECTOR ESCALATING", "WATCHDOG LOCKING ON", "CONNECTION RISK CRITICAL"]
        elif mainframe_integrity <= 20:
            options = ["CORE WALL UNSTABLE", "EXTRACTION WINDOW NEAR", "ROOT PATH LEAKING"]
        else:
            options = ["WATCHDOG PING", "FIREWALL NODE ACTIVE", "PACKET NOISE DETECTED", "COUNTERMEASURE SWEEP PASSED"]
        add_system_message(random.choice(options), current_theme["main"], timer=300)

    system_event_timer -= last_dt_ms
    if scan_complete and not extraction_active and not cipher_lock_active and system_event_timer <= 0:
        system_event_timer = random.randint(9500, 15000)
        if random.random() < 0.65:
            raise_trace(random.randint(3, 7), "WATCHDOG SWEEP")
            add_system_message("SYSTEM PUSHED BACK. SUPPRESS IF TRACE CLIMBS.", (255, 180, 0), timer=460)


# ================== PUZZLE MODE ==================
def choose_random_puzzle():
    """Pick a random puzzle without repeating until the full bag is used."""
    global current_puzzle_index, puzzle_bag

    if not puzzle_bag:
        puzzle_bag = list(range(len(puzzles)))
        random.shuffle(puzzle_bag)

    current_puzzle_index = puzzle_bag.pop()
    return puzzles[current_puzzle_index]


def load_random_puzzle():
    """Load a fresh random puzzle into the cipher panel."""
    global puzzle_message

    selected = choose_random_puzzle()
    puzzle_message = selected["prompt"]
    reset_puzzle_line()
    
def reset_puzzle_line():
    global puzzle_full_line, puzzle_visible_chars, puzzle_type_accum
    if game_mode == "puzzle" and puzzle_message:
        puzzle_full_line = f"CIPHER {current_puzzle_index + 1}/{len(puzzles)}: {puzzle_message}"
    else:
        puzzle_full_line = ""
    puzzle_visible_chars = 0
    puzzle_type_accum = 0.0


def start_puzzle_mode():
    global game_mode, current_puzzle_index, puzzle_message, hack_input_mode, hack_buffer
    global trace_active, cipher_wrong_attempts, cipher_hint_visible
    
    game_mode = "puzzle"
    load_random_puzzle()
    hack_input_mode = True
    hack_buffer = ""

    # Do not rush the player while reading a cipher.
    # TRACE resumes after the cipher is solved or exited.
    trace_active = False
    cipher_wrong_attempts = 0
    cipher_hint_visible = False

    reset_puzzle_line()
    set_objective("Cipher paused TRACE. Read the big panel and type the puzzle answer.", "TYPE ANSWER")
    add_system_message("CIPHER MODE OPEN. TRACE PAUSED WHILE YOU READ.", current_theme["bright"], timer=760)
    banner("CIPHER MODE - TRACE PAUSED", current_theme["flash"], 120)


def give_puzzle_hint():
    global puzzle_message, puzzle_full_line, puzzle_visible_chars, puzzle_type_accum
    global cipher_hint_visible
    hint = puzzles[current_puzzle_index].get("hint")
    if not hint:
        return

    # Hints are free now because the puzzle needs to be readable and learnable.
    cipher_hint_visible = True
    puzzle_message = f"{puzzles[current_puzzle_index]['prompt']}  // HINT: {hint}"
    add_system_message("HINT SHOWN. TRACE IS STILL PAUSED.", current_theme["bright"], timer=680)
    banner("HINT DISPLAYED", current_theme["flash"], 95)

    puzzle_full_line = f"CIPHER {current_puzzle_index + 1}/{len(puzzles)}: {puzzle_message}"
    puzzle_visible_chars = len(puzzle_full_line)
    puzzle_type_accum = float(puzzle_visible_chars)

def handle_puzzle_answer(answer_str):
    global current_puzzle_index, game_mode, puzzle_message, hack_input_mode, hack_buffer
    global trace_active, unlocked_themes, theme_index, current_theme
    global cipher_wrong_attempts

    raw_answer = answer_str.strip().upper()

    # Do not punish UI-confusion words. Explain the action instead.
    if raw_answer in ("ANSWER", "SUBMIT", "KEY", "CODE"):
        add_system_message("TYPE THE PUZZLE SOLUTION ITSELF. EXAMPLE: INSIGHT", (255, 180, 0), timer=760)
        add_system_message("TRACE IS PAUSED. TAKE YOUR TIME.", current_theme["bright"], timer=760)
        banner("TYPE THE PUZZLE SOLUTION", (255, 180, 0), 115)
        hack_buffer = ""
        return

    answer = raw_answer
    for prefix in ("ANSWER ", "ANSWER:", "SUBMIT ", "SUBMIT:", "KEY ", "KEY:", "CODE ", "CODE:"):
        if answer.startswith(prefix):
            answer = answer[len(prefix):].strip()
            break

    current = puzzles[current_puzzle_index]
    correct = current["answer"].upper()

    if answer == correct:
        if vault_active and vault_decrypt_pending:
            spawn_word_rain_from_text("VAULT CIPHER ACCEPTED")
            complete_vault_decryption()
            return

        spawn_word_rain_from_text("CIPHER ACCEPTED")
        spawn_particles(WIDTH // 2, HEIGHT // 2, 70, (0, 255, 0), spread=5.8)
        score_manager.hack()
        score_manager.add_score(180, WIDTH // 2 - 40, HEIGHT // 2 - 100, label="CIPHER +180")
        reduce_trace(18, "CIPHER ACCEPTED")
        break_cipher_lock()
        damage_mainframe(8.0 + access_level * 1.4, "ENCRYPTION LAYER BROKEN", allow_through_lock=True)
        play_hack_sound()
        register_cipher_solved()

        game_mode = "free"
        hack_input_mode = True
        hack_buffer = ""
        trace_active = scan_complete
        puzzle_message = ""
        puzzle_full_line = ""

        set_objective("Cipher cleared. Continue the breach.", "BREACH")
        add_system_message("CIPHER CLEARED. TRACE RESUMED.", current_theme["bright"], timer=620)
    else:
        cipher_wrong_attempts += 1
        spawn_word_rain_from_text("CIPHER REJECTED")
        spawn_particles(WIDTH // 2, HEIGHT // 2, 22, (255, 180, 0), spread=4.0)
        score_manager.break_combo()

        # Wrong cipher guesses do not raise TRACE anymore. The old behavior made
        # the player feel punished while trying to find the prompt.
        base_prompt = puzzles[current_puzzle_index]["prompt"]
        hint_text = current.get("hint", "")
        if cipher_wrong_attempts >= 2 and hint_text:
            puzzle_message = f"{base_prompt}  // HINT: {hint_text}"
            add_system_message("NOT IT. HINT SHOWN. TRACE IS STILL PAUSED.", (255, 180, 0), timer=760)
        else:
            puzzle_message = f"{base_prompt}  // TRY AGAIN. TRACE PAUSED."
            add_system_message("CIPHER REJECTED. TRY AGAIN. NO TRACE PENALTY.", (255, 180, 0), timer=760)

        puzzle_full_line = f"CIPHER {current_puzzle_index + 1}/{len(puzzles)}: {puzzle_message}"
        puzzle_visible_chars = len(puzzle_full_line)
        puzzle_type_accum = float(puzzle_visible_chars)
        banner("TRY AGAIN - TRACE PAUSED", (255, 180, 0), 95)
        hack_buffer = ""
        play_error_sound()

def clear_cipher_state():
    """Force-close any active cipher/puzzle UI."""
    global game_mode, puzzle_message, puzzle_full_line
    global puzzle_visible_chars, puzzle_type_accum
    global cipher_wrong_attempts, cipher_hint_visible
    global hack_buffer

    game_mode = "free"
    puzzle_message = ""
    puzzle_full_line = ""
    puzzle_visible_chars = 0
    puzzle_type_accum = 0.0
    cipher_wrong_attempts = 0
    cipher_hint_visible = False
    hack_buffer = ""

def exit_puzzle_mode():
    global game_mode, puzzle_message, hack_input_mode, hack_buffer
    global trace_active, puzzle_full_line, puzzle_visible_chars, puzzle_type_accum
    game_mode = "free"
    puzzle_message = ""
    hack_input_mode = True
    hack_buffer = ""
    trace_active = scan_complete
    puzzle_full_line = ""
    puzzle_visible_chars = 0
    puzzle_type_accum = 0.0
    if vault_active:
        set_objective("Returned to Data Vault. Type PING, LOCK, DECRYPT, DOWNLOAD, PURGE, or MASK.", "PING")
    elif cipher_lock_active:
        set_objective("Cipher lock still active. Type DECRYPT to solve it.", "DECRYPT")
    else:
        set_objective("Continue the breach.", "BREACH")


# ================== DRAWING ==================
def draw_boot_screen():
    screen.fill((0, 0, 0))
    t = pygame.time.get_ticks() / 1000.0
    title_color = (0, 255, 0) if int(t * 3) % 2 == 0 else (180, 255, 180)
    title = big_font.render("VISIONBREAKER", True, title_color)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title, title_rect)
    subtitle = medium_font.render("NEUROGRID TERMINAL v3.0", True, (0, 210, 0))
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 60)))
    messages = [
        "BOOT SEQUENCE INITIATED",
        "NEURAL INTERFACE ONLINE",
        "MAINFRAME BREACH MODULE LOADED",
        "TRACE COUNTERMEASURES ACTIVE",
    ]
    y = HEIGHT // 2
    for msg in messages:
        text = small_font.render(msg, True, (0, 255, 0))
        screen.blit(text, text.get_rect(center=(WIDTH // 2, y)))
        y += 25
    instr1 = medium_font.render("PRESS ENTER TO JACK IN", True, (0, 255, 0))
    screen.blit(instr1, instr1.get_rect(center=(WIDTH // 2, HEIGHT * 3 // 4)))
    instr2 = small_font.render("PRESS T FOR TUTORIAL", True, (0, 180, 0))
    screen.blit(instr2, instr2.get_rect(center=(WIDTH // 2, HEIGHT * 3 // 4 + 30)))


def draw_tutorial():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 224))
    screen.blit(overlay, (0, 0))
    lines = [
        ("VISIONBREAKER TUTORIAL", current_theme["bright"], True),
        ("", None, False),
        ("GOAL", current_theme["flash"], True),
        ("Level 1: break the mainframe core before TRACE locks you out.", current_theme["main"], False),
        ("Level 2: steal 5 data fragments before the vault locks down.", current_theme["main"], False),
        ("Level 3: defend the escape stream by typing falling threats.", current_theme["main"], False),
        ("Type commands directly or press H to open the console.", current_theme["main"], False),
        ("", None, False),
        ("LEVEL 1: MAIN BREACH", current_theme["flash"], True),
        ("SCAN reveals the core. BREACH and INJECT damage it.", current_theme["main"], False),
        ("SUPPRESS lowers TRACE. DECRYPT pauses TRACE for cipher locks.", current_theme["main"], False),
        ("EXTRACT clears Level 1 once the core is cracked below 12%.", current_theme["main"], False),
        ("", None, False),
        ("LEVEL 2: DATA VAULT", current_theme["flash"], True),
        ("PING reveals nodes. LOCK A-G selects a fragment.", current_theme["main"], False),
        ("DECRYPT solves the fragment cipher. DOWNLOAD extracts it.", current_theme["main"], False),
        ("PURGE removes corrupt/decoy nodes. MASK slows lockdown.", current_theme["main"], False),
        ("", None, False),
        ("LEVEL 3: COUNTERTRACE DEFENSE", current_theme["flash"], True),
        ("Type falling words to destroy threat packets before they hit.", current_theme["main"], False),
        ("Math packets show equations. Type the answer, like 8+7 -> 15.", current_theme["main"], False),
        ("", None, False),
        ("CONTROLS", current_theme["flash"], True),
        ("ESC Pause | C Theme | UP/DOWN Speed | B Slow motion | N Binary", current_theme["main"], False),
        ("P Manual puzzle mode | TAB Toggle UI | F11 Fullscreen", current_theme["main"], False),
        ("", None, False),
        ("PRESS ENTER TO START", current_theme["flash"], True),
    ]
    y = max(40, HEIGHT // 10)
    for line, color, is_header in lines:
        if color is None:
            y += 10
            continue
        font_to_use = medium_font if is_header else small_font
        text = font_to_use.render(line, True, color)
        screen.blit(text, text.get_rect(center=(WIDTH // 2, y)))
        y += 30 if is_header else 23


def draw_pause_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    screen.blit(overlay, (0, 0))
    title = big_font.render("PAUSED", True, current_theme["bright"])
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
    stats = [
        f"Score: {score_manager.current_score}",
        f"High Score: {HIGH_SCORE}",
        f"Combo: x{score_manager.multiplier:.1f}",
        f"Stage: {'Countertrace Defense' if level_stage == 3 else ('Data Vault' if level_stage == 2 else 'Main Breach')}",
        f"Core Integrity: {int(mainframe_integrity)}%",
        f"Trace/Lockdown: {int(vault_lockdown) if level_stage == 2 else int(trace_level)}%",
        f"Theme: {current_theme['name']}",
    ]
    y = HEIGHT // 2 - 30
    for stat in stats:
        text = medium_font.render(stat, True, current_theme["main"])
        screen.blit(text, text.get_rect(center=(WIDTH // 2, y)))
        y += 30
    options = ["ESC - Resume", "Q - Quit to Desktop", "T - Tutorial"]
    y += 15
    for option in options:
        text = small_font.render(option, True, current_theme["bright"])
        screen.blit(text, text.get_rect(center=(WIDTH // 2, y)))
        y += 24


def draw_bar(surface, x, y, w, h, ratio, fill_color, label, bg=(25, 25, 25)):
    ratio = max(0.0, min(1.0, ratio))
    pygame.draw.rect(surface, bg, (x, y, w, h))
    if ratio > 0:
        pygame.draw.rect(surface, fill_color, (x, y, int(w * ratio), h))
    pygame.draw.rect(surface, (190, 190, 190), (x, y, w, h), 1)
    text = ui_font.render(label, True, (220, 220, 220))
    surface.blit(text, (x, y - 14))


def trace_color():
    ratio = trace_level / trace_max
    if ratio < 0.5:
        return (0, 255, 0)
    if ratio < 0.8:
        return (255, 200, 0)
    return (255, 60, 40)


def draw_reactive_core(surface):
    cx, cy = WIDTH // 2, HEIGHT // 2
    t = pygame.time.get_ticks() / 1000.0

    # Before SCAN, keep the screen as pure codefall/free-hack mode.
    # The target only materializes once the actual breach starts.
    if not core_revealed:
        return

    mat = core_materialize
    integrity_ratio = max(0.0, min(1.0, mainframe_integrity / mainframe_max_integrity))
    trace_ratio = max(0.0, min(1.0, trace_level / trace_max))
    pulse = (math.sin(t * (3.2 + trace_ratio * 5.0)) + 1.0) * 0.5

    base_radius = int((78 + pulse * 8 + trace_ratio * 18) * mat)
    outer_radius = int((130 + pulse * 14 + trace_ratio * 28) * mat)

    if core_scan_timer > 0:
        scan_ratio = 1.0 - (core_scan_timer / 130.0)
        scan_y = int(scan_ratio * HEIGHT)
        scan_surf = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
        scan_surf.fill((*current_theme["bright"], 45))
        surface.blit(scan_surf, (0, scan_y - 20))
        pygame.draw.line(surface, current_theme["flash"], (0, scan_y), (WIDTH, scan_y), 2)

    # warning pulse overlay behind core
    if trace_ratio > 0.55 or core_alarm_timer > 0:
        alarm_alpha = int(35 + trace_ratio * 75 + (math.sin(t * 8) + 1) * 18)
        alarm_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alarm_surf.fill((255, 0, 0, min(110, alarm_alpha)))
        surface.blit(alarm_surf, (0, 0))

    # extraction beam
    if extraction_active:
        beam = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        beam_alpha = int(70 + pulse * 60)
        pygame.draw.line(beam, (*current_theme["flash"], beam_alpha), (cx, cy), (cx, 0), 8)
        pygame.draw.line(beam, (*current_theme["bright"], beam_alpha), (cx - 28, cy), (cx - 72, 0), 3)
        pygame.draw.line(beam, (*current_theme["bright"], beam_alpha), (cx + 28, cy), (cx + 72, 0), 3)
        surface.blit(beam, (0, 0))

    # outer rings
    ring_color = trace_color() if trace_ratio > 0.65 else current_theme["bright"]
    for offset, width in [(0, 2), (34, 1), (68, 1)]:
        radius = max(2, outer_radius + offset)
        pygame.draw.circle(surface, ring_color, (cx, cy), radius, width)

    # rotating arc segments
    for i in range(10):
        ang1 = t * 1.2 + i * (math.pi * 2 / 10)
        ang2 = ang1 + 0.28 + (1.0 - integrity_ratio) * 0.18
        r = outer_radius + 20
        x1 = cx + math.cos(ang1) * r
        y1 = cy + math.sin(ang1) * r
        x2 = cx + math.cos(ang2) * r
        y2 = cy + math.sin(ang2) * r
        color = current_theme["trail"] if i % 2 else ring_color
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), 3)

    # shield if cipher lock is active
    if cipher_lock_active:
        shield_color = (255, 180, 0)
        shield_r = outer_radius + 42 + int(pulse * 8)
        pygame.draw.circle(surface, shield_color, (cx, cy), shield_r, 3)
        shield_text = medium_font.render("CIPHER LOCK", True, shield_color)
        surface.blit(shield_text, shield_text.get_rect(center=(cx, cy - shield_r - 22)))

    # core body
    if core_flash_timer > 0:
        core_color = current_theme["flash"]
    elif core_damage_timer > 0:
        core_color = (255, 80, 60)
    else:
        core_color = current_theme["bright"] if integrity_ratio > 0.3 else (255, 120, 80)

    pygame.draw.circle(surface, core_color, (cx, cy), base_radius, 3)
    pygame.draw.circle(surface, current_theme["main"], (cx, cy), max(4, int(base_radius * 0.62)), 2)
    pygame.draw.circle(surface, current_theme["flash"], (cx, cy), max(2, int(8 + pulse * 7)), 0)

    # cracks grow as integrity drops
    cracks = int((1.0 - integrity_ratio) * 14)
    random.seed(1337)
    for i in range(cracks):
        angle = random.uniform(0, math.pi * 2)
        start_r = random.uniform(base_radius * 0.25, base_radius * 0.75)
        end_r = random.uniform(base_radius * 0.8, base_radius * 1.2)
        x1 = cx + math.cos(angle) * start_r
        y1 = cy + math.sin(angle) * start_r
        x2 = cx + math.cos(angle + random.uniform(-0.25, 0.25)) * end_r
        y2 = cy + math.sin(angle + random.uniform(-0.25, 0.25)) * end_r
        pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 1)
    random.seed()

    # labels
    target_label = large_font.render("FIREWALL CORE", True, current_theme["flash"])
    surface.blit(target_label, target_label.get_rect(center=(cx, cy - outer_radius - 48)))

    integrity_text = medium_font.render(f"CORE INTEGRITY {int(mainframe_integrity)}%", True, core_color)
    surface.blit(integrity_text, integrity_text.get_rect(center=(cx, cy + outer_radius + 44)))

    if extraction_active:
        bar_w = 360
        bar_x = cx - bar_w // 2
        bar_y = cy + outer_radius + 72
        draw_bar(surface, bar_x, bar_y, bar_w, 12, extraction_progress / 100.0, current_theme["flash"], f"EXTRACTION {int(extraction_progress)}%")




def draw_defense_field(surface):
    """Draw Level 3 typing-shooter threats and escape stream."""
    if not defense_active and not defense_complete and not (level_stage == 3 and system_lockout):
        return

    cx = WIDTH // 2
    t = pygame.time.get_ticks() / 1000.0
    shield_ratio = max(0.0, min(1.0, defense_shield / defense_max_shield))

    if defense_intro_timer > 0:
        scan_x = int((1.0 - defense_intro_timer / 180.0) * WIDTH)
        scan_surf = pygame.Surface((48, HEIGHT), pygame.SRCALPHA)
        scan_surf.fill((*current_theme["bright"], 40))
        surface.blit(scan_surf, (scan_x - 24, 0))
        pygame.draw.line(surface, current_theme["flash"], (scan_x, 0), (scan_x, HEIGHT), 2)

    if shield_ratio < 0.35 or system_lockout:
        alarm = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alarm.fill((255, 0, 0, int(55 + (1.0 - shield_ratio) * 80)))
        surface.blit(alarm, (0, 0))

    # Escape stream at bottom and vertical uplink beam.
    beam = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    beam_alpha = int(45 + math.sin(t * 5.0) * 18)
    pygame.draw.line(beam, (*current_theme["flash"], beam_alpha), (cx, HEIGHT), (cx, 0), 5)
    pygame.draw.line(beam, (*current_theme["bright"], 38), (cx - 42, HEIGHT), (cx - 85, 0), 2)
    pygame.draw.line(beam, (*current_theme["bright"], 38), (cx + 42, HEIGHT), (cx + 85, 0), 2)
    surface.blit(beam, (0, 0))

    stream_y = HEIGHT - 48
    pygame.draw.line(surface, current_theme["flash"], (0, stream_y), (WIDTH, stream_y), 2)
    pygame.draw.line(surface, current_theme["trail"], (0, stream_y + 10), (WIDTH, stream_y + 10), 1)

    # Lasers from player stream to threats.
    for laser in defense_lasers:
        alpha = max(0, min(255, int(laser["timer"] * 18)))
        color = laser["color"]
        laser_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(laser_surf, (*color, alpha), (laser["x1"], laser["y1"]), (laser["x2"], laser["y2"]), 4)
        pygame.draw.circle(laser_surf, (*color, alpha), (int(laser["x2"]), int(laser["y2"])), 18, 2)
        surface.blit(laser_surf, (0, 0))

    title = large_font.render("COUNTERTRACE DEFENSE", True, current_theme["flash"])
    surface.blit(title, title.get_rect(center=(cx, 82)))
    subtitle = small_font.render("TYPE FALLING WORDS. FOR MATH PACKETS, TYPE THE ANSWER.", True, current_theme["bright"])
    surface.blit(subtitle, subtitle.get_rect(center=(cx, 112)))

    for threat in defense_threats:
        x, y = int(threat["x"]), int(threat["y"])
        color = defense_threat_color(threat["kind"])
        pulse = (math.sin(threat["pulse"]) + 1.0) * 0.5
        radius = 22 + int(pulse * 5)
        if threat["kind"] in ("virus", "lockout"):
            radius += 4
        pygame.draw.circle(surface, color, (x, y), radius, 2)
        pygame.draw.circle(surface, color, (x, y), max(3, radius // 5), 0)
        pygame.draw.circle(surface, current_theme["trail"], (x, y), radius + 9, 1)
        label = medium_font.render(threat["text"], True, color)
        surface.blit(label, label.get_rect(center=(x, y - radius - 18)))
        if threat["kind"] == "math":
            helper = small_font.render("TYPE ANSWER", True, color)
            surface.blit(helper, helper.get_rect(center=(x, y + radius + 18)))
        elif threat["kind"] in ("virus", "lockout"):
            helper = small_font.render("DANGER", True, color)
            surface.blit(helper, helper.get_rect(center=(x, y + radius + 18)))


def draw_defense_hud(surface):
    hud_w = 390
    x = WIDTH - hud_w - 14
    y = 54
    panel = pygame.Surface((hud_w + 18, 198), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 150))
    surface.blit(panel, (x - 9, y - 22))

    title = small_font.render(f"COUNTERTRACE: {system_status}", True, current_theme["bright"])
    surface.blit(title, (x, y))
    y += 28

    draw_bar(surface, x, y, hud_w, 12, defense_progress / defense_progress_max, current_theme["main"], f"ESCAPE STREAM {int(defense_progress)}%")
    y += 36
    shield_color = current_theme["bright"] if defense_shield >= 50 else ((255, 200, 0) if defense_shield >= 25 else (255, 60, 40))
    draw_bar(surface, x, y, hud_w, 12, defense_shield / defense_max_shield, shield_color, f"STREAM SHIELD {int(defense_shield)}%")
    y += 34

    accuracy = int((defense_hits / max(1, defense_hits + defense_wrong_inputs + defense_misses)) * 100)
    info = ui_font.render(f"WAVE {defense_wave} | TARGETS {len(defense_threats)} | ACC {accuracy}%", True, current_theme["flash"])
    surface.blit(info, (x, y))
    y += 20

    objective = "Objective: Type the falling labels before they hit the stream. Math packets need answers."
    if len(objective) > 58:
        surface.blit(ui_font.render(objective[:58], True, (220, 220, 220)), (x, y))
        surface.blit(ui_font.render(objective[58:116], True, (220, 220, 220)), (x, y + 14))
    else:
        surface.blit(ui_font.render(objective, True, (220, 220, 220)), (x, y))

def draw_vault_map(surface):
    """Draw Level 2 data vault fragments."""
    if not vault_active and not (level_stage == 2 and vault_complete):
        return

    cx, cy = WIDTH // 2, HEIGHT // 2
    t = pygame.time.get_ticks() / 1000.0
    lockdown_ratio = max(0.0, min(1.0, vault_lockdown / vault_max_lockdown))

    if vault_intro_timer > 0:
        scan_y = int((1.0 - vault_intro_timer / 180.0) * HEIGHT)
        scan_surf = pygame.Surface((WIDTH, 52), pygame.SRCALPHA)
        scan_surf.fill((*current_theme["bright"], 42))
        surface.blit(scan_surf, (0, scan_y - 26))
        pygame.draw.line(surface, current_theme["flash"], (0, scan_y), (WIDTH, scan_y), 2)

    if lockdown_ratio > 0.65:
        alarm = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alarm.fill((255, 0, 0, int(35 + lockdown_ratio * 70)))
        surface.blit(alarm, (0, 0))

    # Vault boundary rings
    for r, width in [(210, 1), (280, 1), (350, 2)]:
        color = vault_lockdown_color() if lockdown_ratio > 0.65 else current_theme["trail"]
        pygame.draw.circle(surface, color, (cx, cy), int(r + math.sin(t * 2.0) * 4), width)

    # Connection lines
    active_nodes = [n for n in vault_nodes if not n["downloaded"] and not n["purged"]]
    for i, node in enumerate(active_nodes):
        for other in active_nodes[i+1:i+3]:
            pygame.draw.line(surface, current_theme["trail"], (node["x"], node["y"]), (other["x"], other["y"]), 1)

    title = large_font.render("DATA VAULT", True, current_theme["flash"])
    surface.blit(title, title.get_rect(center=(cx, cy - 32)))
    subtitle = medium_font.render(f"FRAGMENTS {vault_fragments_extracted}/{vault_fragments_required}", True, current_theme["bright"])
    surface.blit(subtitle, subtitle.get_rect(center=(cx, cy + 4)))

    locked = current_vault_node()

    for node in vault_nodes:
        node["pulse"] += 0.05
        pulse = (math.sin(node["pulse"]) + 1.0) * 0.5
        x, y = int(node["x"]), int(node["y"])
        is_locked = locked is node

        if node["downloaded"]:
            color = (90, 90, 90)
            label_extra = "DONE"
        elif node["purged"]:
            color = (80, 60, 60)
            label_extra = "PURGED"
        elif node["known"] or vault_ping_timer > 0:
            if node["kind"] == "data":
                color = current_theme["bright"] if not node["decrypted"] else current_theme["flash"]
                label_extra = "DATA" if not node["decrypted"] else "DECRYPTED"
            elif node["kind"] == "corrupt":
                color = (255, 80, 40)
                label_extra = "CORRUPT"
            else:
                color = (255, 180, 0)
                label_extra = "DECOY"
        else:
            color = current_theme["main"]
            label_extra = "UNKNOWN"

        radius = 26 + int(pulse * 5) + (6 if is_locked else 0)
        if is_locked:
            pygame.draw.circle(surface, current_theme["flash"], (x, y), radius + 12, 2)
        pygame.draw.circle(surface, color, (x, y), radius, 2)
        pygame.draw.circle(surface, color, (x, y), max(3, radius // 5), 0)

        label = medium_font.render(node["label"], True, current_theme["flash"] if is_locked else color)
        surface.blit(label, label.get_rect(center=(x, y)))
        name = small_font.render(label_extra, True, color)
        surface.blit(name, name.get_rect(center=(x, y + radius + 18)))
        if is_locked:
            lock = small_font.render("LOCKED", True, current_theme["flash"])
            surface.blit(lock, lock.get_rect(center=(x, y - radius - 18)))


def draw_vault_hud(surface):
    hud_w = 390
    x = WIDTH - hud_w - 14
    y = 54
    panel = pygame.Surface((hud_w + 18, 196), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 150))
    surface.blit(panel, (x - 9, y - 22))

    title = small_font.render(f"DATA VAULT: {system_status}", True, current_theme["bright"])
    surface.blit(title, (x, y))
    y += 28

    frag_ratio = vault_fragments_extracted / max(1, vault_fragments_required)
    draw_bar(surface, x, y, hud_w, 12, frag_ratio, current_theme["main"], f"FRAGMENTS {vault_fragments_extracted}/{vault_fragments_required}")
    y += 36
    draw_bar(surface, x, y, hud_w, 12, vault_lockdown / vault_max_lockdown, vault_lockdown_color(), f"VAULT LOCKDOWN {int(vault_lockdown)}%")
    y += 34

    locked = current_vault_node()
    locked_label = locked["label"] if locked else "NONE"
    if game_mode == "puzzle":
        command_label = "CIPHER MODE: TYPE THE PUZZLE ANSWER"
    else:
        command_label = f"NEXT COMMAND: {next_command}"
    access_text = ui_font.render(f"LOCKED: {locked_label}    {command_label}", True, current_theme["flash"])
    surface.blit(access_text, (x, y))
    y += 20

    if vault_mask_timer > 0:
        mask_text = ui_font.render(f"MASK ACTIVE: {int(vault_mask_timer / 60) + 1}s", True, current_theme["bright"])
        surface.blit(mask_text, (x, y))
        y += 16

    objective = system_objective
    if len(objective) > 58:
        surface.blit(ui_font.render(objective[:58], True, (220, 220, 220)), (x, y))
        surface.blit(ui_font.render(objective[58:116], True, (220, 220, 220)), (x, y + 14))
    else:
        surface.blit(ui_font.render(objective, True, (220, 220, 220)), (x, y))


def draw_mainframe_hud(surface):
    if defense_active or defense_complete or (level_stage == 3 and system_lockout):
        draw_defense_hud(surface)
        return

    if vault_active or (level_stage == 2 and (vault_complete or system_lockout)):
        draw_vault_hud(surface)
        return

    hud_w = 370
    x = WIDTH - hud_w - 14
    y = 54
    panel = pygame.Surface((hud_w + 18, 180), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 145))
    surface.blit(panel, (x - 9, y - 22))

    title = small_font.render(f"MAINFRAME: {system_status}", True, current_theme["bright"])
    surface.blit(title, (x, y))
    y += 28

    draw_bar(surface, x, y, hud_w, 12, mainframe_integrity / mainframe_max_integrity, current_theme["main"], f"CORE INTEGRITY {int(mainframe_integrity)}%")
    y += 36
    draw_bar(surface, x, y, hud_w, 12, trace_level / trace_max, trace_color(), f"TRACE {int(trace_level)}%")
    y += 34

    if game_mode == "puzzle":
        command_label = "CIPHER MODE: TYPE THE PUZZLE ANSWER"
    else:
        command_label = f"NEXT COMMAND: {next_command}"

    access_text = ui_font.render(f"ACCESS LEVEL: {access_level}    {command_label}", True, current_theme["flash"])
    surface.blit(access_text, (x, y))
    y += 20

    objective = system_objective
    if len(objective) > 58:
        first = objective[:58]
        second = objective[58:116]
        surface.blit(ui_font.render(first, True, (220, 220, 220)), (x, y))
        surface.blit(ui_font.render(second, True, (220, 220, 220)), (x, y + 14))
    else:
        surface.blit(ui_font.render(objective, True, (220, 220, 220)), (x, y))

def draw_system_messages(surface):
    start_x = 8
    start_y = HEIGHT - 188
    panel = pygame.Surface((520, 140), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 135))
    surface.blit(panel, (start_x - 6, start_y - 8))
    title = ui_font.render("SYSTEM FEED", True, current_theme["bright"])
    surface.blit(title, (start_x, start_y))
    y = start_y + 18
    for msg in system_messages[-MAX_SYSTEM_MESSAGES:]:
        text = ui_font.render(f"> {msg['text']}", True, msg["color"])
        surface.blit(text, (start_x, y))
        y += 15


def draw_breach_result_overlay(surface):
    if not root_access and not system_lockout:
        return
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 158))
    surface.blit(overlay, (0, 0))

    if system_lockout and level_stage == 3:
        title_text = "COUNTERTRACE OVERRUN"
        subtitle_text = "ESCAPE STREAM LOST"
        footer_text = "PRESS ENTER OR TYPE RESET TO START A NEW RUN"
        color = (255, 60, 40)
    elif system_lockout and level_stage == 2:
        title_text = "VAULT LOCKDOWN"
        subtitle_text = "DATA STREAM TERMINATED"
        footer_text = "PRESS ENTER OR TYPE RESET TO START A NEW RUN"
        color = (255, 60, 40)
    elif system_lockout:
        title_text = "TRACE LOCKOUT"
        subtitle_text = "CONNECTION TERMINATED"
        footer_text = "PRESS ENTER OR TYPE RESET TO START A NEW BREACH"
        color = (255, 60, 40)
    elif defense_complete:
        title_text = "NEUROGRID ESCAPED"
        subtitle_text = "FINAL COUNTERTRACE DEFENSE CLEARED"
        footer_text = "PRESS ENTER TO JACK IN AGAIN"
        color = current_theme["flash"]
    elif vault_complete and not defense_complete:
        title_text = "LEVEL 2 COMPLETE"
        subtitle_text = "COUNTERTRACE SWARM INBOUND"
        footer_text = "PRESS ENTER OR TYPE DEFENSE TO START LEVEL 3"
        color = current_theme["flash"]
    elif level1_complete and not vault_complete:
        title_text = "LEVEL 1 COMPLETE"
        subtitle_text = "DATA VAULT EXPOSED"
        footer_text = "PRESS ENTER OR TYPE VAULT TO ENTER LEVEL 2"
        color = current_theme["flash"]
    else:
        title_text = "ROOT ACCESS GRANTED"
        subtitle_text = "MAINFRAME COMPROMISED"
        footer_text = "PRESS ENTER OR TYPE RESET TO START A NEW BREACH"
        color = current_theme["flash"]

    title = big_font.render(title_text, True, color)
    surface.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 56)))
    subtitle = medium_font.render(subtitle_text, True, current_theme["bright"])
    surface.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 4)))
    if vault_complete and not defense_complete and not system_lockout:
        commands = small_font.render("LEVEL 3: TYPE FALLING WORDS OR MATH ANSWERS BEFORE THEY HIT THE STREAM", True, (230, 230, 230))
        surface.blit(commands, commands.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 36)))
        footer_y = HEIGHT // 2 + 66
    elif level1_complete and not vault_complete and not system_lockout:
        commands = small_font.render("LEVEL 2 COMMANDS: PING | LOCK A-G | DECRYPT | DOWNLOAD | PURGE | MASK", True, (230, 230, 230))
        surface.blit(commands, commands.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 36)))
        footer_y = HEIGHT // 2 + 66
    else:
        footer_y = HEIGHT // 2 + 46
    restart = small_font.render(footer_text, True, (230, 230, 230))
    surface.blit(restart, restart.get_rect(center=(WIDTH // 2, footer_y)))

def draw_command_banner(surface):
    if command_banner_timer <= 0 or not command_banner:
        return
    alpha = max(0, min(255, int(command_banner_timer * 3)))
    text = large_font.render(command_banner, True, current_theme["flash"])
    text.set_alpha(alpha)
    bg = pygame.Surface((text.get_width() + 32, text.get_height() + 18), pygame.SRCALPHA)
    bg.fill((0, 0, 0, min(180, alpha)))
    rect = bg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 170))
    surface.blit(bg, rect)
    surface.blit(text, text.get_rect(center=rect.center))


def wrap_text_for_font(text, font_obj, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = word if not current else current + " " + word
        if font_obj.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_cipher_panel(surface):
    """Large readable puzzle panel for cipher mode."""
    if game_mode != "puzzle":
        return

    panel_w = min(900, WIDTH - 100)
    panel_h = 300
    x = WIDTH // 2 - panel_w // 2
    y = HEIGHT // 2 - panel_h // 2 - 20

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 220))
    surface.blit(panel, (x, y))

    border_color = current_theme["flash"] if pygame.time.get_ticks() % 700 < 350 else current_theme["bright"]
    pygame.draw.rect(surface, border_color, (x, y, panel_w, panel_h), 2)
    pygame.draw.rect(surface, current_theme["trail"], (x + 8, y + 8, panel_w - 16, panel_h - 16), 1)

    title = large_font.render("CIPHER CHALLENGE", True, current_theme["flash"])
    surface.blit(title, title.get_rect(center=(WIDTH // 2, y + 34)))

    paused = small_font.render("TRACE PAUSED WHILE CIPHER IS OPEN", True, (255, 200, 0))
    surface.blit(paused, paused.get_rect(center=(WIDTH // 2, y + 64)))

    current = puzzles[current_puzzle_index]
    prompt = current.get("prompt", puzzle_message)
    hint = current.get("hint", "")

    prompt_lines = wrap_text_for_font(prompt, medium_font, panel_w - 80)
    text_y = y + 100
    for line in prompt_lines[:4]:
        rendered = medium_font.render(line, True, current_theme["bright"])
        surface.blit(rendered, rendered.get_rect(center=(WIDTH // 2, text_y)))
        text_y += 30

    helper = small_font.render("Type the puzzle solution directly. Press F1 for the Operator Card. Example: INSIGHT", True, (225, 225, 225))
    surface.blit(helper, helper.get_rect(center=(WIDTH // 2, y + panel_h - 70)))

    hint_line = f"Need help? Type HINT.  Hint: {hint if cipher_hint_visible else 'hidden until HINT or 2 wrong tries'}"
    hint_surf = small_font.render(hint_line, True, (255, 200, 0))
    surface.blit(hint_surf, hint_surf.get_rect(center=(WIDTH // 2, y + panel_h - 42)))

    attempts = small_font.render(f"Wrong attempts: {cipher_wrong_attempts}   No TRACE penalty in cipher mode", True, current_theme["main"])
    surface.blit(attempts, attempts.get_rect(center=(WIDTH // 2, y + panel_h - 18)))

def breach_ui_active():
    """Return True once the actual game/breach UI should be visible."""
    return scan_complete or root_access or system_lockout or extraction_active or game_mode == "puzzle" or vault_active or vault_complete or defense_active or defense_complete or level_stage in (2, 3)


def draw_pre_scan_overlay(surface):
    """Minimal overlay before SCAN so the player gets full codefall first."""
    # Keep this intentionally tiny. No target, no mainframe HUD, no TRACE panel.
    if not hack_input_mode:
        hint = ui_font.render("Press H or start typing. Type SCAN when ready to engage the mainframe.", True, current_theme["trail"])
        surface.blit(hint, (8, HEIGHT - 26))

def draw_operator_card(surface):
    """In-game operator reference card / puzzle cheatsheet."""
    if not operator_card_visible:
        return

    panel_w = min(1080, WIDTH - 80)
    panel_h = min(HEIGHT - 60, 620)
    x = WIDTH // 2 - panel_w // 2
    y = HEIGHT // 2 - panel_h // 2

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 232))
    surface.blit(panel, (x, y))

    pygame.draw.rect(surface, current_theme["flash"], (x, y, panel_w, panel_h), 2)
    pygame.draw.rect(surface, current_theme["trail"], (x + 8, y + 8, panel_w - 16, panel_h - 16), 1)

    title = medium_font.render("VISIONBREAKER OPERATOR CARD", True, current_theme["flash"])
    surface.blit(title, title.get_rect(center=(WIDTH // 2, y + 24)))

    subtitle = ui_font.render("Press F1 to close. Quick reference for commands, ciphers, binary, hex, and logic.", True, current_theme["bright"])
    surface.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, y + 44)))

    # Compact layout settings
    col_gap = 28
    col_w = (panel_w - 80 - (col_gap * 2)) // 3
    col1_x = x + 28
    col2_x = col1_x + col_w + col_gap
    col3_x = col2_x + col_w + col_gap
    top_y = y + 70

    line_gap = 13
    section_gap = 16

    def draw_section(col_x, start_y, heading, lines):
        yy = start_y

        heading_surf = small_font.render(heading, True, current_theme["flash"])
        surface.blit(heading_surf, (col_x, yy))
        yy += 18

        for line in lines:
            color = current_theme["bright"] if line.startswith(">") else (215, 215, 215)

            # Trim long lines so they do not leave the box.
            max_chars = 42
            safe_line = line if len(line) <= max_chars else line[:max_chars - 3] + "..."

            text = ui_font.render(safe_line, True, color)
            surface.blit(text, (col_x, yy))
            yy += line_gap

        return yy + section_gap

    # COLUMN 1: Level commands
    y1 = top_y
    y1 = draw_section(
        col1_x,
        y1,
        "LEVEL 1: MAIN BREACH",
        [
            "> SCAN      reveal core",
            "> BREACH    damage core",
            "> INJECT    heavy hit, high TRACE",
            "> SUPPRESS  lower TRACE",
            "> DECRYPT   solve cipher",
            "> EXTRACT   finish weak core",
        ],
    )

    y1 = draw_section(
        col1_x,
        y1,
        "LEVEL 2: DATA VAULT",
        [
            "> PING      reveal nodes",
            "> LOCK A-G  select node",
            "> DECRYPT   solve fragment",
            "> DOWNLOAD  extract data",
            "> PURGE     remove bad nodes",
            "> MASK      slow lockdown",
        ],
    )

    y1 = draw_section(
        col1_x,
        y1,
        "LEVEL 3: COUNTERTRACE",
        [
            "> Type falling words",
            "> Math packets: type answer",
            "> Example: 8+7 means 15",
            "> Misses damage shield",
            "> STATUS shows defense stats",
        ],
    )

    # COLUMN 2: Number / logic help
    y2 = top_y
    y2 = draw_section(
        col2_x,
        y2,
        "BINARY QUICK HELP",
        [
            "> 1001 = 9",
            "> 1010 = 10",
            "> 1100 = 12",
            "> 1111 = 15",
            "> Place values: 8 4 2 1",
        ],
    )

    y2 = draw_section(
        col2_x,
        y2,
        "HEX QUICK HELP",
        [
            "> Hex goes 0-9 then A-F",
            "> After 9 comes A",
            "> FF = 255",
        ],
    )

    y2 = draw_section(
        col2_x,
        y2,
        "LOGIC QUICK HELP",
        [
            "> TRUE AND TRUE = TRUE",
            "> TRUE AND FALSE = FALSE",
            "> TRUE OR FALSE = TRUE",
            "> NOT TRUE = FALSE",
            "> NOT FALSE = TRUE",
        ],
    )

    y2 = draw_section(
        col2_x,
        y2,
        "SEQUENCES",
        [
            "> 2 4 8 16 = 32",
            "> 3 6 12 24 = 48",
            "> 2 5 8 11 = 14",
            "> 10 20 30 40 = 50",
        ],
    )

    # COLUMN 3: Common cipher answers
    y3 = top_y
    y3 = draw_section(
        col3_x,
        y3,
        "COMMON CIPHER WORDS",
        [
            "> Opposite of NOISE = SIGNAL",
            "> Hidden data = ENCRYPTED",
            "> Read encrypted data = DECRYPT",
            "> Main control part = CORE",
            "> Bad data = CORRUPT",
            "> Fake nodes = DECOYS",
            "> Secret access word = PASSWORD",
            "> Network data unit = PACKET",
            "> Route traffic = ROUTER",
        ],
    )

    y3 = draw_section(
        col3_x,
        y3,
        "VISIONBREAKER FLOW",
        [
            "> Break in",
            "> Steal the data",
            "> Defend escape stream",
            "> Survive the Neurogrid",
        ],
    )

    y3 = draw_section(
        col3_x,
        y3,
        "QUICK TIPS",
        [
            "> Use HINT during ciphers",
            "> SUPPRESS before TRACE maxes",
            "> PURGE corrupt vault nodes",
            "> LOCK before DOWNLOAD",
            "> Math packets need answers",
        ],
    )

    footer = ui_font.render("F1 CLOSE  |  ESC PAUSE  |  H TERMINAL", True, current_theme["trail"])
    surface.blit(footer, footer.get_rect(center=(WIDTH // 2, y + panel_h - 18)))

def draw_ui_overlay(surface):
    pygame.display.set_caption(
        f"VisionBreaker: Neurogrid Terminal | state={game_state.value} | mode={game_mode} | hack={hack_input_mode}"
    )

    active = breach_ui_active()

    # Top-left HUD stays visible for the whole experience.
    # Before SCAN it explains ambient/free-hack mode. After SCAN it switches to breach commands.
    score_text = medium_font.render(f"SCORE: {score_manager.current_score}", True, current_theme["bright"])
    surface.blit(score_text, (8, 6))
    hs_text = small_font.render(f"HI: {HIGH_SCORE}", True, current_theme["main"])
    surface.blit(hs_text, (8, 28))

    combo_y = 44
    if score_manager.multiplier > 1.0:
        combo_text = small_font.render(f"COMBO x{score_manager.multiplier:.1f}", True, current_theme["flash"])
        surface.blit(combo_text, (8, combo_y))

    speed_label = f"{base_speed_factor:.1f}x"
    flags = []
    if slow_mo:
        flags.append("Slow-mo")
    if binary_mode:
        flags.append("Binary")
    if game_mode == "puzzle":
        flags.append("Cipher")
    if hack_input_mode:
        flags.append("Hack")
    if not active:
        flags.append("Ambient")
    flag_str = f" ({' / '.join(flags)})" if flags else ""

    if active:
        if defense_active or level_stage == 3:
            command_line = "Defense mode: type falling words, or type math answers"
        elif vault_active or level_stage == 2:
            command_line = "Vault commands: PING, LOCK A-G, DECRYPT, DOWNLOAD, PURGE, MASK"
        else:
            command_line = "Type commands directly: BREACH, INJECT, SUPPRESS, DECRYPT, EXTRACT"
        lines = [
            f"Theme: {current_theme['name']} (Unlocked {unlocked_themes}/{len(COLOR_THEMES)})",
            f"Speed: {speed_label}{flag_str}",
            command_line,
            "C Theme | UP/DOWN Speed | B Slow-mo | N Binary | H Console | P Cipher | F1 Operator Card | TAB UI | F11 Fullscreen",
            "ESC Pause / Exit console",
        ]
    else:
        lines = [
            f"Theme: {current_theme['name']} (Unlocked {unlocked_themes}/{len(COLOR_THEMES)})",
            f"Speed: {speed_label}{flag_str}",
            "Ambient free-hack mode: type any word to echo it into the codefall.",
            "Type SCAN when ready to engage the mainframe breach.",
            "C Theme | UP/DOWN Speed | B Slow-mo | N Binary | H Console | F1 Operator Card | TAB UI | F11 Fullscreen",
            "ESC Pause / Exit console",
        ]

    y = 68
    for line in lines:
        text_surf = ui_font.render(line, True, (205, 205, 205))
        surface.blit(text_surf, (8, y))
        y += 14

    # Score popups stay visible in both ambient and breach modes.
    for popup in score_manager.score_popups:
        r, g, b = popup["color"][:3]
        popup_font = medium_font if popup["timer"] > 70 else small_font
        popup_text = popup_font.render(popup["text"], True, (r, g, b))
        bg = pygame.Surface((popup_text.get_width() + 12, popup_text.get_height() + 8), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        surface.blit(bg, (popup["x"] - 6, popup["y"] - 4))
        surface.blit(popup_text, (popup["x"], popup["y"]))

    if achievement_notification:
        notif_text = medium_font.render(achievement_notification["text"], True, (255, 215, 0))
        notif_rect = notif_text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        surface.blit(notif_text, notif_rect)

    draw_command_banner(surface)

    # Only the actual game/breach UI is hidden until SCAN.
    # This keeps the clean codefall screen before the player engages the system.
    if active:
        draw_mainframe_hud(surface)
        draw_system_messages(surface)
        if not root_access and not system_lockout and not vault_complete and not defense_complete:
            draw_cipher_panel(surface)

        draw_breach_result_overlay(surface)

        # Small backup puzzle line under the readable cipher panel.
        if game_mode == "puzzle" and puzzle_full_line:
            global puzzle_type_accum, puzzle_visible_chars
            dt_sec = last_dt_ms / 1000.0
            puzzle_type_accum += dt_sec * PUZZLE_CHARS_PER_SEC
            target_chars = int(puzzle_type_accum)
            if target_chars > puzzle_visible_chars:
                puzzle_visible_chars = min(target_chars, len(puzzle_full_line))
            visible_text = puzzle_full_line[:puzzle_visible_chars]
            if visible_text:
                t = pygame.time.get_ticks() / 1000.0
                glow = (math.sin(t * 3.0) + 1.0) * 0.5
                br = current_theme["bright"]
                fl = current_theme["flash"]
                color = (
                    int(br[0] + (fl[0] - br[0]) * glow * 0.5),
                    int(br[1] + (fl[1] - br[1]) * glow * 0.5),
                    int(br[2] + (fl[2] - br[2]) * glow * 0.5),
                )
                puzzle_surf = puzzle_font.render(visible_text, True, color)
                rect = puzzle_surf.get_rect(midbottom=(WIDTH // 2, HEIGHT - 58))
                bg = pygame.Surface((rect.width + 24, rect.height + 12), pygame.SRCALPHA)
                bg.fill((0, 0, 0, 170))
                surface.blit(bg, (rect.x - 12, rect.y - 6))
                surface.blit(puzzle_surf, rect)

    # Hack console appears whenever input mode is active, both before and after SCAN.
    if hack_input_mode:
        prompt = f"HACK> {hack_buffer}_"
        text_surf = hack_font.render(prompt, True, current_theme["bright"])
        rect = text_surf.get_rect(topleft=(8, HEIGHT - text_surf.get_height() - 12))
        console_bg = pygame.Surface((max(500, rect.width + 16), rect.height + 10), pygame.SRCALPHA)
        console_bg.fill((0, 0, 0, 190))
        surface.blit(console_bg, (rect.x - 8, rect.y - 5))
        surface.blit(text_surf, rect)
        
    draw_operator_card(surface)

def draw_code_rain(surface, effective_speed):
    trace_ratio = trace_level / trace_max
    for i, x in enumerate(x_positions):
        y = int(raindrops[i] * FONT_SIZE)
        char = random.choice("01") if binary_mode else random.choice(char_pool)
        r = random.random()
        if trace_ratio > 0.7 and r > 0.965:
            color = (255, 60, 40)
        elif r > 0.985:
            color = current_theme["flash"]
        elif r > 0.95 and not binary_mode:
            char = random.choice("01")
            color = current_theme["bright"]
        else:
            color = current_theme["bright"] if random.random() > 0.95 else current_theme["main"]

        text = font.render(char, True, color)
        surface.blit(text, (x, y))

        for tr in range(trail_length):
            trail_y = y - tr * FONT_SIZE
            if trail_y > 0:
                trail_char = random.choice(char_pool) if random.random() > 0.5 and not binary_mode else char
                trail_color = (120, 20, 20) if trace_ratio > 0.75 and random.random() > 0.65 else current_theme["trail"]
                trail_text = font.render(trail_char, True, trail_color)
                trail_surface.blit(trail_text, (x, trail_y))

        speed_boost = 1.0 + trace_ratio * 0.45
        raindrops[i] += speeds[i] * effective_speed * speed_boost
        if y > HEIGHT and random.random() > 0.9:
            raindrops[i] = random.randint(-10, 0)
            speeds[i] = random.uniform(0.4, 1.2)


def draw_scene_background():
    scene_surface.fill(current_theme["bg"])
    fade_alpha = 55 if trace_level < 70 else 42
    trail_surface.fill((0, 0, 0, fade_alpha))
    scene_surface.blit(trail_surface, (0, 0))
    effective_speed = base_speed_factor * (0.3 if slow_mo else 1.0)
    draw_code_rain(scene_surface, effective_speed)
    if random.random() > 0.998:
        spawn_word_rain()
    draw_word_rains(scene_surface, effective_speed)
    if defense_active or defense_complete or (level_stage == 3 and system_lockout):
        draw_defense_field(scene_surface)
    elif vault_active or (level_stage == 2 and vault_complete):
        draw_vault_map(scene_surface)
    else:
        draw_reactive_core(scene_surface)
    apply_critical_error_overlay(scene_surface)


# ================== EVENT HANDLING ==================
def enter_playing_from_menu():
    global game_state, hack_input_mode, hack_buffer
    game_state = GameState.PLAYING
    # Start in ambient view. Press H or simply start typing to open the terminal.
    # The first typed letter is preserved by the direct-typing handler below.
    hack_input_mode = False
    hack_buffer = ""
    persist_save(tutorial_done=True)
    if not system_messages:
        add_system_message("CONNECTION LIVE. PRESS H OR TYPE SCAN TO BEGIN.", current_theme["bright"], timer=680)
        add_system_message("FREE HACK MODE: TYPE ANY WORD TO DROP IT INTO THE CODEFALL.", current_theme["main"], timer=680)
    set_objective("Press H for free hack mode, or type SCAN to start the breach.", "SCAN")


def handle_keydown(event):
    global running, game_state, hack_input_mode, hack_buffer
    global base_speed_factor, slow_mo, binary_mode, show_ui, game_mode
    global achievement_notification, operator_card_visible

    if event.key == pygame.K_F11:
        toggle_fullscreen()
        return
    
    if event.key == pygame.K_F1 and game_state == GameState.PLAYING:
        operator_card_visible = not operator_card_visible
        return

    if game_state == GameState.BOOT:
        if event.key == pygame.K_RETURN:
            enter_playing_from_menu()
        elif event.key == pygame.K_t:
            game_state = GameState.TUTORIAL
        elif event.key == pygame.K_ESCAPE:
            running = False
        return

    if game_state == GameState.TUTORIAL:
        if event.key == pygame.K_RETURN:
            enter_playing_from_menu()
        elif event.key == pygame.K_ESCAPE:
            game_state = GameState.BOOT
        return

    if game_state == GameState.PAUSED:
        if event.key == pygame.K_ESCAPE:
            game_state = GameState.PLAYING
            if not root_access and not system_lockout:
                hack_input_mode = True
        elif event.key == pygame.K_q:
            running = False
        elif event.key == pygame.K_t:
            game_state = GameState.TUTORIAL
        return

    if game_state != GameState.PLAYING:
        return

    if hack_input_mode:
        if event.key == pygame.K_RETURN:
            cleaned = hack_buffer.strip()
            if game_mode == "puzzle":
                if cleaned.upper() == "HINT":
                    give_puzzle_hint()
                else:
                    handle_puzzle_answer(cleaned)
            else:
                if cleaned:
                    process_mainframe_command(cleaned)

            # Keep the terminal hot so the player can immediately type the next command.
            # Root access / lockout screens intentionally close the terminal until Enter resets the run.
            hack_buffer = ""
            hack_input_mode = not (root_access or system_lockout)
        elif event.key == pygame.K_ESCAPE:
            hack_buffer = ""
            hack_input_mode = False
            if game_mode == "puzzle":
                exit_puzzle_mode()
        elif event.key == pygame.K_BACKSPACE:
            hack_buffer = hack_buffer[:-1]
        elif event.unicode and event.unicode.isprintable():
            hack_buffer += event.unicode
        return

    if (root_access or system_lockout) and event.key == pygame.K_RETURN:
        if root_access and level1_complete and not vault_complete and not vault_active and not system_lockout:
            start_vault_level()
        elif root_access and vault_complete and not defense_complete and not defense_active and not system_lockout:
            start_defense_level()
        else:
            reset_mainframe_run(reset_score=False)
        return

    if event.key == pygame.K_ESCAPE:
        game_state = GameState.PAUSED
    elif event.key == pygame.K_c:
        next_theme()
    elif event.key == pygame.K_UP:
        base_speed_factor = min(base_speed_factor + 0.1, 3.0)
        if base_speed_factor >= 3.0:
            unlock_achievement("speed_demon")
    elif event.key == pygame.K_DOWN:
        base_speed_factor = max(base_speed_factor - 0.1, 0.2)
    elif event.key == pygame.K_b:
        slow_mo = not slow_mo
    elif event.key == pygame.K_n:
        binary_mode = not binary_mode
        if sfx_binary is not None:
            sfx_binary.play()
    elif event.key == pygame.K_h:
        # Open/clear the terminal. Before SCAN, this is free-hack mode.
        # After SCAN, it becomes the mainframe command terminal.
        hack_input_mode = True
        hack_buffer = ""
    elif event.key == pygame.K_p:
        if game_mode == "free":
            start_puzzle_mode()
        else:
            exit_puzzle_mode()
    elif event.key == pygame.K_e:
        trigger_critical_error()
    elif event.key == pygame.K_s:
        trigger_shake(random.randint(2, 5), random.randint(15, 30))
    elif event.key == pygame.K_TAB:
        show_ui = not show_ui
    elif event.key == pygame.K_F12:
        pygame.image.save(screen, "codefall_bg.png")
        print("Saved screenshot to codefall_bg.png")
    elif event.unicode and event.unicode.isprintable() and event.unicode.strip():
        hack_input_mode = True
        hack_buffer = event.unicode


# ================== INIT ==================
init_surfaces()
init_audio()

# ================== MAIN LOOP ==================
while running:
    dt_ms = clock.tick(60)
    last_dt_ms = dt_ms

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            handle_keydown(event)

    if game_state == GameState.PLAYING:
        score_manager.update()
        check_general_achievements()
        update_mainframe_system()
        for particle in particles[:]:
            if not particle.update():
                particles.remove(particle)
        if achievement_notification:
            achievement_notification["timer"] -= 1
            if achievement_notification["timer"] <= 0:
                achievement_notification = None

        # Cipher puzzles pause TRACE. The pressure returns once the player exits
        # cipher mode, but the puzzle itself should be readable.
        if False:
            pass

    screen.fill((0, 0, 0))

    if game_state == GameState.BOOT:
        draw_boot_screen()

    elif game_state == GameState.TUTORIAL:
        draw_scene_background()
        offset_x, offset_y = get_shake_offset()
        screen.blit(scene_surface, (offset_x, offset_y))
        draw_tutorial()

    elif game_state in (GameState.PLAYING, GameState.PAUSED):
        draw_scene_background()
        offset_x, offset_y = get_shake_offset()
        screen.blit(scene_surface, (offset_x, offset_y))

        for particle in particles:
            particle.draw(screen)

        if show_ui:
            draw_ui_overlay(screen)

        if game_state == GameState.PAUSED:
            draw_pause_menu()

    pygame.display.flip()

persist_save(high_score=HIGH_SCORE, unlocked_themes=unlocked_themes)
pygame.quit()
sys.exit()
