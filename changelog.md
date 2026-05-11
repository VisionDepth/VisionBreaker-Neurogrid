# VisionBreaker: Neurogrid Terminal v3.0

VisionBreaker v3.0 is the biggest update yet, transforming the project from an interactive codefall terminal into a full cyber-hacking typing arcade game.

This update brings a complete goal-based gameplay loop, multiple levels, command-based hacking, typing challenges, cipher puzzles, unlockable themes, achievements, improved UI, and stronger visual feedback.

## What’s New

### Full 3-Level Gameplay Run

VisionBreaker now features a complete hacking run with three different stages:

**Level 1: Main Breach**  
Break into the mainframe, reveal the firewall core, damage it with commands, manage TRACE, solve cipher locks, and extract root access.

**Level 2: Data Vault Infiltration**  
Enter the data vault, scan hidden nodes, lock onto fragments, decrypt cipher puzzles, download valid data, and avoid corrupted or decoy nodes before lockdown hits 100%.

**Level 3: Countertrace Defense**  
Defend the escape stream in a typing-shooter style final level. Type falling threat words or solve math packets before they hit the stream.

## New Gameplay Features

- Goal-based mainframe breach system
- Reactive firewall core
- TRACE pressure system
- Data vault with multiple node types
- Vault lockdown meter
- Falling threat packet typing mode
- Math packet challenges
- Score, combo, and high score system
- Expanded achievements
- More unlockable themes
- Theme unlock progression
- Readable cipher puzzle panels
- Randomized cipher puzzle selection
- Expanded cipher puzzle pool
- Free-hack codefall mode before the breach starts
- Denser Matrix-style codefall
- Particle bursts, screen shake, system messages, and stronger visual feedback

## Level 1: Main Breach

Level 1 now has a clear objective. Start in free codefall mode, then type `SCAN` when you are ready to begin the breach.

Once the system is engaged, the mainframe core appears and becomes the main target.

Commands include:

- `SCAN` to reveal the mainframe core
- `BREACH` to damage the core
- `INJECT` for heavier damage with higher TRACE risk
- `SUPPRESS` to reduce TRACE
- `DECRYPT` to solve cipher locks
- `EXTRACT` to finish the breach when the core is weak

The core now visually reacts to attacks with flashing, particles, cracks, warning pulses, and system feedback.

## Level 2: Data Vault Infiltration

After completing the main breach, the player enters the Data Vault.

The goal is to extract 5 valid data fragments before the vault locks down.

Commands include:

- `PING` to reveal vault nodes
- `LOCK A-G` to select a node
- `DECRYPT` to solve a fragment cipher
- `DOWNLOAD` to extract valid data
- `PURGE` to remove corrupt or decoy nodes
- `MASK` to slow vault lockdown

Level 2 now feels different from Level 1, focusing on selecting targets, avoiding traps, decrypting fragments, and managing the vault lockdown meter.

## Level 3: Countertrace Defense

Level 3 introduces a typing-shooter style final escape mode.

Falling threat packets move toward the escape stream. Type the displayed word to destroy the packet before it hits.

Math packets also appear. For math packets, type the answer instead of the equation.

Example:

```text
8+7
```

Type:

```text
15
```

Level 3 now includes:

- Falling word threats
- Math packets
- Escape stream shield
- Defense progress
- Hit, miss, and accuracy tracking
- Reduced early difficulty curve
- Math difficulty that scales by wave
- Slower early packet spawning
- More manageable threat pacing

## Cipher and Puzzle Updates

Cipher puzzles now feel more like part of the game instead of a fixed sequence.

Changes include:

- Larger readable cipher panel
- TRACE pauses while cipher mode is open
- Wrong cipher answers no longer add TRACE
- Hints can be shown during cipher mode
- Puzzle prompts are randomized
- New expanded puzzle pool
- Binary, hex, logic, command, sequence, math, and system-themed questions
- Cipher questions now feel less repetitive between runs

## Operator Reference Card

Added an in-game Operator Card that can be opened with `F1`.

The Operator Card gives players quick access to:

- Level 1 commands
- Level 2 commands
- Level 3 typing rules
- Binary help
- Hex help
- Logic help
- Common cipher answers
- Sequence examples
- Quick gameplay tips

This gives players a built-in reference sheet without needing to leave the game.

## Achievements Expanded

v3.0 adds a much larger achievement system to reward progress across the full run.

New achievement types include:

- First command completed
- Mainframe core revealed
- First breach completed
- Cipher solved
- Score milestones
- Combo milestones
- TRACE recovery
- Clean Level 1 breach
- Vault ping
- First data download
- Clean vault completion
- Math packet destroyed
- Virus or lockout packet destroyed
- Perfect escape
- Full 3-level run completed

## Theme Expansion

VisionBreaker now includes more unlockable visual themes.

New theme styles include:

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

Themes can unlock through gameplay progress, score milestones, and level completion.

## Codefall Visual Improvements

The codefall effect has been tuned to look denser and more alive.

Changes include:

- Tighter code column spacing
- Longer trails
- Slower fade for a fuller Matrix-style look
- Better ambient free-hack feel before the breach starts

## UI and Flow Improvements

- Top-left HUD stays visible throughout the experience
- Game-specific HUD only appears after `SCAN`
- Free-hack mode no longer punishes random typing before the game starts
- Hack terminal can stay active after gameplay begins
- First typed letter is preserved when entering the terminal
- Cipher panel no longer overlaps level-complete screens
- Level-complete overlays now take priority over active puzzle panels
- Controls text updated to include the Operator Card
- Pause menu shows useful run information

## Core Game Loop

Start in free codefall mode.  
Type `SCAN` when you are ready.  
Breach the mainframe.  
Manage TRACE.  
Decrypt cipher locks.  
Extract root access.  
Enter the data vault.  
Steal the data.  
Defend your escape stream.  
Survive the Neurogrid.

VisionBreaker is no longer just codefall. It is now a full mainframe breach typing arcade game.
