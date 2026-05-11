# VisionBreaker: Neurogrid Terminal

**VisionBreaker: Neurogrid Terminal** is a cyber-hacking typing arcade game built around dense codefall visuals, command-based terminal gameplay, cipher puzzles, pressure systems, score progression, unlockable themes, and fast reaction typing.

Step into the Neurogrid, open the terminal, and breach your way through a hostile mainframe before the system traces you.

What starts as a calm Matrix-style codefall experience becomes a full multi-stage hacking run where every command matters.

**Break in. Steal the data. Defend the escape. Survive the Neurogrid.**

---

<p align="center">
  <img
    src="https://github.com/user-attachments/assets/0b3dd9c6-eb3e-4637-b3d4-361f9fc636c9"
    width="450"
    alt="VisionBreaker: Neurogrid Terminal"
  />
</p>


[![Downloads](https://img.shields.io/github/downloads/VisionDepth/VisionBreaker-Neurogrid/total?color=brightgreen)](https://github.com/VisionDepth/VisionBreaker-Neurogrid/releases)

---

## About

VisionBreaker blends the feel of old-school typing games with a cyberpunk mainframe fantasy.

It is part typing trainer, part arcade survival game, and part interactive hacking terminal. Players type commands, solve cipher locks, manage danger meters, extract data, and defend their escape stream from falling countertrace packets.

The game begins in ambient free-hack mode where players can type words into the codefall. When ready, type `SCAN` to engage the mainframe and begin the real breach.

---

## Gameplay Overview

VisionBreaker v3.0 introduces a complete 3-level gameplay run.

### Level 1: Main Breach

Reveal and attack the mainframe core.

Type `SCAN` to reveal the firewall core, then use terminal commands to damage it, manage TRACE, solve cipher locks, and extract root access.

Core commands:

- `SCAN` reveals the mainframe core
- `BREACH` damages the firewall core
- `INJECT` deals heavier damage but increases TRACE risk
- `SUPPRESS` lowers TRACE
- `DECRYPT` opens a cipher puzzle
- `EXTRACT` begins root access extraction once the core is weak

The mainframe reacts with particles, cracks, flashing, warning pulses, system messages, screen shake, and TRACE pressure.

### Level 2: Data Vault Infiltration

Steal data from the vault before lockdown reaches 100%.

After completing the main breach, the player enters the Data Vault. The goal is to extract 5 valid data fragments while avoiding corrupt packets and decoy nodes.

Vault commands:

- `PING` reveals vault nodes
- `LOCK A-G` selects a node
- `DECRYPT` opens a fragment cipher
- `DOWNLOAD` extracts decrypted data
- `PURGE` removes corrupt or decoy nodes
- `MASK` slows vault lockdown

Level 2 uses a separate **Vault Lockdown** pressure system.

### Level 3: Countertrace Defense

Defend your escape stream in a typing-shooter style final level.

Falling threat packets move toward the escape stream. Type the displayed word to destroy each packet before it hits.

Math packets also appear. For math packets, type the answer instead of the equation.

Example:

```text
8+7
```

Type:

```text
15
```

Survive until the escape stream reaches 100%.

---

## Features

- Full cyber-hacking typing arcade gameplay
- Complete 3-level gameplay run
- Dense Matrix-style codefall visuals
- Ambient free-hack mode before the breach starts
- Command-based terminal controls
- Reactive mainframe core
- TRACE pressure system
- Data vault infiltration mode
- Vault lockdown system
- Falling threat packet typing mode
- Math packet challenges
- Randomized cipher puzzles
- Expanded puzzle pool
- Built-in Operator Reference Card
- Score, combo, and high score system
- Expanded achievement system
- Unlockable visual themes
- Theme unlock progression
- Particle bursts, screen shake, warning overlays, and system messages
- Music and sound effect support
- Fullscreen and windowed mode support
- Graceful handling for missing audio files

---

## Cipher Puzzles

Cipher puzzles are part of both the Main Breach and Data Vault stages.

When a cipher opens:

- TRACE pauses while the puzzle is active
- A large readable cipher panel appears
- Type the answer directly into the `HACK>` console
- Type `HINT` for help
- Wrong answers do not add TRACE
- Puzzles are randomized to keep runs from feeling identical

Puzzle types include:

- Binary
- Hexadecimal
- Logic
- Sequences
- Quick math
- VisionBreaker command knowledge
- Cybersecurity-themed word prompts
- System flow questions

---

## Operator Reference Card

Press `F1` during gameplay to open the built-in Operator Card.

The Operator Card includes:

- Level 1 command reference
- Level 2 command reference
- Level 3 typing rules
- Binary quick help
- Hex quick help
- Logic quick help
- Common cipher words
- Sequence examples
- Quick gameplay tips

This is meant to feel like an old-school in-game reference manual for players who want help during ciphers or commands.

---

## Achievements

VisionBreaker v3.0 includes an expanded achievement system.

Achievement examples include:

- First Hack
- Scanner Online
- First Breach
- Cipher Breaker
- Code Breaker
- Combo Starter
- Combo Master
- Combo Overdrive
- Packet Runner
- Firewall Breaker
- Neurogrid Operator
- Digital Phantom
- Trace Survivor
- Clean Breach
- Root Access
- Vault Ping
- Data Thief
- Vault Runner
- Ghost in the Vault
- Math Packet Smasher
- Virus Hunter
- Perfect Escape
- Countertrace Defender
- Neurogrid Escaped
- Theme Collector

---

## Unlockable Themes

VisionBreaker includes multiple unlockable visual themes.

Themes can unlock through score milestones, level progress, and full-run completion.

Theme examples:

- Cyber Ice
- Toxic Lime
- Deep Matrix
- Blue Firewall
- Crimson Trace
- Golden Core
- Void Purple
- Pink Glitch
- White Terminal
- Blood Moon
- Quantum Teal
- Root Phantom
- Countertrace Red
- Vault Gold
- Neurogrid Whiteout

---

## Controls

### General Controls

| Key | Action |
| --- | --- |
| `Enter` | Continue from boot, start next level, submit terminal input |
| `Esc` | Pause, close console, or exit cipher mode |
| `F11` | Toggle fullscreen or windowed mode |
| `F1` | Open or close Operator Card |
| `TAB` | Toggle UI |
| `C` | Cycle unlocked themes |
| `Up Arrow` | Increase code rain speed |
| `Down Arrow` | Decrease code rain speed |
| `B` | Toggle slow-motion mode |
| `N` | Toggle binary mode |
| `H` | Open or clear the hack console |
| `P` | Manually open or exit cipher mode |
| `F12` | Save screenshot |

### Hack Console

Use the `HACK>` console to type commands, puzzle answers, and Level 3 targets.

Before `SCAN`, typed words are sent into the codefall as ambient free-hack echoes.

After `SCAN`, the terminal becomes the main command input for the game.

### Level 1 Commands

```text
SCAN
BREACH
INJECT
SUPPRESS
DECRYPT
EXTRACT
STATUS
HELP
```

### Level 2 Commands

```text
PING
LOCK A-G
DECRYPT
DOWNLOAD
PURGE
MASK
STATUS
HELP
```

### Level 3 Input

Type falling threat words exactly as shown.

For math packets, type the answer.

Examples:

```text
FIREWALL
TRACE
VIRUS
15
24
```

---

## Installation

### Option 1: Windows EXE Release

If you want to play without using command prompts:

1. Go to the latest GitHub release.
2. Download the release ZIP.
3. Extract the ZIP somewhere on your hard drive.
4. Run the `.exe`.

### Option 2: Using Conda

1. Create a new environment:

   ```bash
   conda create -n VisionBreaker python=3.11
   ```

2. Activate the environment:

   ```bash
   conda activate VisionBreaker
   ```

3. Clone the repository:

   ```bash
   git clone https://github.com/your-name/VisionBreaker-Neurogrid-main.git
   ```

4. Open the project folder:

   ```bash
   cd VisionBreaker-Neurogrid-main
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Run the game:

   ```bash
   python VisionBreaker.py
   ```

### Option 3: Plain Python and pip

1. Install Python 3.10 or newer.
2. Download or clone the repository.
3. Open a terminal in the project folder.
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run the game:

   ```bash
   python VisionBreaker.py
   ```

---

## Requirements

- Python 3.10 or newer
- Pygame
- Windows recommended for the packaged `.exe`

Audio files are optional. Missing audio assets are handled gracefully.

---

## License

VisionBreaker: Neurogrid Terminal is proprietary software.

Unless otherwise stated in a separate license file:

- Personal play/use is allowed
- Redistribution is not allowed
- Reuploading is not allowed
- Reselling is not allowed
- Modifying or repackaging the game for release is not allowed
- The VisionBreaker name, logo, artwork, branding, and related materials may not be reused without permission

Gameplay videos, screenshots, reviews, and non-commercial streams are allowed as long as they do not redistribute the game files or claim ownership of the project.

For permission requests, contact the project owner.

---

## Photosensitivity Warning

This project contains:

- Rapidly changing visuals
- Flashing and strobing effects
- Screen shake and glitch effects
- High contrast color themes

These effects may trigger discomfort or seizures in people with photosensitive epilepsy or other light sensitivities.

If you experience dizziness, blurred vision, headache, nausea, or any discomfort while playing, stop using the program immediately and rest. If symptoms persist, seek medical advice.

---

## Summary

VisionBreaker is no longer just codefall.

It is now a full mainframe breach typing arcade game.

Type commands.  
Break the firewall.  
Manage TRACE.  
Decrypt the vault.  
Defend the escape stream.  
Survive the Neurogrid.
