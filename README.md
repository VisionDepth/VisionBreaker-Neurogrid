# VisionBreaker: Neurogrid Terminal

VisionBreaker: Neurogrid Terminal is a cyberpunk terminal toy and logic puzzle game built with Pygame.

You boot into a simulated grid, watch cascading code rain, and jack into a hidden puzzle layer. Solve terminal riddles to neutralize the TRACE system and unlock new visual themes as the Neurogrid bends to your will.

> Part ambient code rain visualizer, part minimal puzzle game.

---
<p align="center">
  <img
    src="https://github.com/user-attachments/assets/9f2fd6b4-f085-444a-ac15-3ab9f8d46ecf"
    width="450"
    alt="VisionBreaker: Neurogrid Terminal – boot sequence"
  />
</p>


## Features

- **Dynamic code rain renderer**
  - High density character streams that scale with your screen resolution
  - Glowing trails, random glitches, binary mode, and camera shake events

- **Neurogrid boot sequence**
  - Diegetic boot screen where you type your choice
  - Type a specific word to break into the simulation or abandon the connection

- **Hack console**
  - Press `H` to open the `HACK>` prompt
  - Type anything and press Enter to rain that phrase down the screen
  - Satisfying confirm sound for successful terminal injections

- **Puzzle mode with TRACE system**
  - Press `P` to enter puzzle mode
  - Answer eight original terminal puzzles through the `HACK>` console
  - A TRACE bar climbs as you stall or answer wrong
  - Wrong answer or full TRACE triggers a critical system failure
  - Solve puzzles to neutralize TRACE and unlock cosmetic rewards

- **Theme unlock progression**
  - Start with 1 theme unlocked
  - Each solved puzzle unlocks an additional color theme
  - Work your way to the full set as you crack the Neurogrid

- **Critical error events**
  - Red tint overlays, glitch bars, camera shake, and a giant SYSTEM FAILURE banner
  - Audio cue for failure and a hard drop back into free mode

- **Plays nice with your hardware**
  - Starts in fullscreen using your current display resolution
  - Can be toggled between fullscreen and windowed mode at run time
  - Fails gracefully if audio assets are missing

---

## Color Themes

You start with **Emerald Stream** and unlock more as you solve puzzles.

- `Emerald Stream`  
  Classic green-on-black cascading code

- `Red Alert`  
  Aggressive red palette with warning vibes

- `Synthwave`  
  Purple and magenta for retro neon energy

- `Neon Circuit`  
  Cyan and teal grid glow

- `Amber Warning`  
  Warm amber tones with hazard feel

- `Glacial Scan`  
  Icy blue scanner aesthetic

- `Violet Static`  
  High contrast purple glitch

- `Ghost Signal`  
  Soft mint and spectral green

- `Solar Flare`  
  Hot orange blast with dark red background

---

## Controls

**General**

- `Esc`  
  Quit the game, or exit hack console if it is open

- `F11`  
  Toggle fullscreen and windowed mode

- `Space`  
  Pause or resume the rain animation  
  (Critical error overlay and shake still animate while paused)

---

**Rain and visual controls**

- `C`  
  Cycle through unlocked color themes

- `Up / Down Arrow`  
  Increase or decrease global rain speed

- `B`  
  Toggle slow motion

- `N`  
  Toggle binary mode  
  In binary mode the rain switches to only `0` and `1`

- `S`  
  Trigger a short manual camera shake event

- `E`  
  Trigger a critical error event on demand

---

**Hack console**

- `H`  
  Open the `HACK>` input at the bottom of the screen

- `Enter` (while the console is open)  
  - In free mode:  
    - Spawn a vertical word rain of what you typed  
    - Play a confirm sound if available  
    - Close the console
  - In puzzle mode:  
    - Submit your answer for the current puzzle

- `Backspace`  
  Delete the last character while typing into the console

- `Esc` (while console is open)  
  Cancel hack input and close the console

---

**Puzzle mode and TRACE**

- `P`  
  Enter puzzle mode from free mode

In puzzle mode:

- A **TRACE bar** appears on the top right
- A **puzzle prompt** appears near the bottom of the screen
- You answer only via the `HACK>` console

If the TRACE bar fills before you solve the current puzzle, or you type a wrong answer, a **critical error** is triggered.

Solving puzzles:

- Correct answers:
  - Show `ACCESS GRANTED` as word rain
  - Advance you to the next puzzle
  - Unlock new themes as you go
- After the last puzzle:
  - TRACE is neutralized
  - You drop back into free mode with all unlocked themes

---

## Boot Screen

On launch you see a green boot sequence for the Neurogrid terminal.

- Wait for the boot lines to fully reveal
- The bottom of the screen will prompt you with a choice
- Type the required word and press Enter to jack in
- Or type the alternative word to close the program instead

This sequence is entirely text driven and fits the in universe lore for VisionBreaker.

---

## Requirements

- Python 3.9 or newer
- Pygame

## Installation

You can run VisionBreaker: Neurogrid Terminal in a Conda environment (recommended) or with plain Python and `pip`.

### Option 1: Using Conda (recommended)

1. **Create a new environment**

   ```bash
   conda create -n VisionBreaker python=3.11
   ```

2. **Activate the environment**

   ```bash
   conda activate VisionBreaker
   ```

3. **Download the game**

   - Either clone the repo:

     ```bash
     git clone https://github.com/your-name/VisionBreaker-Neurogrid-Terminal-main.git
     ```

   - Or download the ZIP from GitHub and extract it somewhere on your drive.

4. **Change into the project folder**

   ```bash
   cd path/to/VisionBreaker-Neurogrid-Terminal-main
   ```

5. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

6. **Run the game**

   ```bash
   python VisionBreaker.py
   ```

---

### Option 2: Plain Python and pip

1. Make sure you have **Python 3.10+** installed and on your PATH.
2. Download or clone the repository and extract it.
3. Open a terminal in the project folder:

   ```bash
   cd path/to/VisionBreaker-Neurogrid-Terminal-main
   ```

4. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run the game:

   ```bash
   python VisionBreaker.py
   ```