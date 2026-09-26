# Operation Phoneback

### A 3D Investigation, Parkour, and Chase Game

A crowded street. People move between shops, traffic, market stalls, and narrow alleys. Everything looks normal. Then the player checks their pocket.

The phone is gone.

A witness remembers a blue shirt. CCTV shows someone entering an alley. The phone signal grows stronger as the player approaches a suspect. The chase begins, then suddenly the signal becomes weaker.

The thief has passed the phone to someone else. The person being chased may no longer be carrying the phone. The player must investigate, adapt, and answer the question: **Who has my phone now?**

## Play the Game

[Download or view Operation Phoneback](https://github.com/Neloy23201333/Operation-Phoneback/blob/main/Operation_Phoneback_Marked_All_Changes.py)

This is a desktop Python/OpenGL game, not a browser game. Install the requirements and run it using the instructions below.

## Project Overview

Operation Phoneback is a 3D investigation-and-chase game set in a fictional Dhaka-inspired urban area with streets, markets, alleys, shops, traffic, barriers, rooftops, and multiple escape routes.

At the beginning of each round, one NPC is secretly selected as the thief. The thief approaches through the moving crowd and steals the phone when close enough. The game does not directly reveal the thief.

The player investigates witnesses, checks CCTV cameras, collects clues, and follows a distance-based phone tracker to identify a suspect. Finding the suspect starts a chase involving running, jumping, shortcuts, obstacles, and tactical stun projectiles.

The thief may secretly pass the phone to an accomplice. Catching the original thief does not guarantee success: the player must capture whoever currently has the phone.

**Gameplay flow:**

Phone stolen → Gather clues → Check CCTV → Track signal → Identify suspect → Chase → Intercept → Verify phone holder → Recover phone

## Main Objective

Recover the phone before its current holder reaches an escape point or the mission timer runs out.

Capturing a random NPC does not win the game. Wrong captures cost score and time while the real phone holder continues escaping. Investigation, deduction, NPC behavior, 3D movement, parkour, projectiles, timing, and chase strategy all contribute to the mission.

## Major Features

### 1. Dynamic Crowd and Hidden NPC Roles

The environment contains moving NPCs. At the beginning of each round, NPCs receive roles such as civilian, witness, thief, or accomplice.

Each NPC has information such as position, movement direction, destination, role, appearance, and state. Roles can change between rounds, so the player cannot rely on memorizing the thief.

### 2. Phone Theft and Changing Ownership

The thief must approach the player and enter stealing range before taking the phone.

`PLAYER → THIEF → ACCOMPLICE`

The tracker and capture system follow the current phone holder. The original thief may no longer be the correct target.

### 3. Thief Behavior States

The thief uses multiple behavior states instead of following one repeated movement pattern.

Example: `BLEND → APPROACH → STEAL → WALK AWAY → ESCAPE → HIDE → RUN`

When the player gets close, the thief may become more desperate, move faster, choose another route, jump obstacles, or attempt a handoff. If the thief creates enough distance, they may blend into the crowd again.

### 4. Witnesses, Clues, and Suspects

NPCs near the theft may become witnesses. Interacting with them can reveal clues about the thief, such as:

- Clothing color
- Direction of travel
- Approximate body size
- Last known location
- Whether another suspicious person was nearby

The player combines clues to narrow down the suspects. The game does not simply reveal the thief.

### 5. CCTV Investigation

CCTV cameras cover important areas such as streets, markets, alleys, and escape routes. At a terminal, the player can switch between camera views to investigate.

### 6. Phone Tracker and Remote Pulse

The tracker calculates the distance between the player and the phone's current holder. Its signal ranges from very weak to very strong.

The player can remotely activate the phone. When nearby, the current holder briefly flashes or pulses, helping the player locate them. A cooldown prevents repeated use.

### 7. Escape Routes and Crowd Blending

The map includes routes through roads, alleys, markets, stairs, and rooftops. The thief can choose routes based on the player's position, for example:

- Market → Alley → Main Road
- Market → Stairs → Rooftop → Side Exit

If the thief gets far enough away, they may stop running and act like a normal pedestrian. The player may need to return to clues, CCTV, or tracking.

### 8. Secret Accomplice Handoff

During the chase, the thief may meet a secretly selected accomplice. If they get close enough, the phone changes hands:

`THIEF A → ACCOMPLICE B`

The original thief may continue running as a distraction while the accomplice escapes in another direction. The tracker follows the new phone holder.

### 9. Character Selection

Before starting, the player chooses one of three specialists:

- **Investigator:** Receives more useful investigation information and improved CCTV support.
- **Runner:** Moves faster and jumps higher, helping with parkour and pursuit.
- **Tracker:** Receives more accurate signal information and has a shorter pulse cooldown.

### 10. Jumping, Gravity, and Parkour

The player and thief encounter barriers, boxes, low walls, gaps, and raised platforms. Jumping uses vertical movement and gravity:

`Upward velocity → Gravity → Falling → Landing`

Missing an obstacle can slow the player or cause a time penalty rather than immediately ending the game.

### 11. Shortcuts, Interception, and Stun Projectiles

The player can use alleys, stairs, rooftops, and alternative paths to predict the thief's movement and intercept them.

The player also has a limited supply of non-lethal stun projectiles. A successful hit slows the target:

`RUN → STUNNED / SLOWED`

Limited ammunition encourages careful timing and aim.

### 12. Verified Capture and Scoring

When the player captures an NPC, the game checks whether that NPC currently has the phone.

- **Correct capture:** The phone is recovered and the mission is completed.
- **Wrong capture:** Score decreases, time is lost, and the real phone holder continues escaping.

Points can be earned for useful clues, detecting a handoff, successful interception, accurate stun hits, and recovering the phone quickly. Wrong captures and wasted projectiles create penalties.

## Win and Failure Conditions

The player wins only by capturing the current phone holder.

The mission fails if:

- The current holder reaches an escape point.
- The recovery timer reaches zero.
- The player makes too many wrong captures.

## Controls

| Key | Action |
| --- | --- |
| `W` / `S` | Move forward / backward |
| `A` / `D` | Turn left / right |
| `Space` | Jump |
| `E` | Interact with witnesses, CCTV, or nearby NPCs |
| `Q` | Switch CCTV camera while viewing CCTV |
| `R` | Activate the remote phone pulse |
| `F` | Fire a stun projectile |
| `P` | Pause or resume |
| `1` / `2` / `3` | Choose Investigator, Runner, or Tracker |
| `Enter` | Start a case or play again |
| `Esc` | Return to character selection |

## Run the Python Game

Operation Phoneback is a desktop Python game built with PyOpenGL, GLU, and GLUT. A working OpenGL environment and GLUT/freeglut runtime are required.

1. Install Python 3.
2. Install the Python OpenGL packages:

   ```bash
   python -m pip install PyOpenGL PyOpenGL_accelerate
