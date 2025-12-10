# VisionBreaker: Neurogrid Terminal v2.1  
## Update Changelog

## Core Puzzle System Overhaul
- Added a **typewriter-style text reveal system** for all puzzle prompts  
  - Smooth timed reveal  
  - Pulsing glow effect  
  - Occasional glitch-duplicate overlays for added style  

## Improved Puzzle Flow & Player Experience
- Wrong answers now **increase TRACE** instead of instantly failing the puzzle.
- TRACE penalties rebalanced for smoother gameplay:
  - Wrong answer: **+10 TRACE**
  - Using a hint: **+15 TRACE**
- Correct answers now **reset TRACE**, giving players breathing room before the next challenge.
- Code rain slightly slowed to reduce visual strain  
  - Players can still manually adjust speed using Up/Down keys.

## Fixed Hint System
- Players can type **HINT** during puzzles to receive a clue.
- Hint text now appears **instantly** (no typewriter delay).
- Hints apply a TRACE penalty.
- Hint text integrates cleanly into the existing puzzle line.

## Dynamic Theme Unlocking
- Unlocking triggers animated **“THEME UNLOCKED: [NAME]”** vertical word rains.
- Newly unlocked themes **auto-apply immediately**, creating a dramatic atmospheric shift.

## Escape Behavior Improvements
- ESC now correctly exits:
  - Hack console  
  - Puzzle mode  
  - Puzzle text  
  - TRACE UI  
- Fully prevents leftover puzzle UI from sticking on screen.

## Bug Fixes & Polishing
- Puzzle prompts remain visible after incorrect answers.
- TRACE bar resets properly when moving to the next puzzle.
- Puzzle text fully clears upon exiting puzzle mode.
- General UI cleanup and improved stability.
- Wrong answer feedback now appears **instantly** (no typewriter delay).

---

## Summary
This update brings major improvements to puzzle gameplay, visuals, pacing, and overall user experience.  
VisionBreaker now feels more alive, reactive, and cinematic — delivering the most immersive hacker terminal experience yet.
