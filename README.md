# WOW HRI Experiment

This repository contains the code for a human-robot interaction experiment using the With Other Words game.
The robot plays a spoken word-guessing game with a human participant while monitoring engagement through vision and speech signals.

## Project Goal

The goal of this experiment is to evaluate how different robot behaviors affect user re-engagement during interaction.

When the system detects that the user has disengaged (by looking away from the robot or by taking a long time to respond), the robot attempts to regain attention using one of two strategies.

The experiment compares:
- **Control Condition**
The robot uses a verbal prompt to regain attention: "Hey, are you there?"
- **Experimental Condition**
The robot performs a repair gesture designed to attract the user's attention.

Both conditions use the same game logic, dialogue system, and engagement detection. Only the re-engagement strategy differs.

## Repository Structure

### Main entry files
- `control_condition.py` - Runs the experiment using the control condition (verbal re-engagement).
- `experimental_condition.py`-Runs the experiment using the experimental condition (gesture-based re-engagement).

### Core modules

- `config.py` - Contains global settings such as timeouts, game states, and robot connection settings.
- `prompts.py` - Contains the prompts used by the language model for the Director and Matcher roles.
- `movements.py` - Defines robot movement sequences and gestures used during the interaction.
- `state.py` - Defines a runtime state object that stores all interaction variables.
- `logging_utils.py` - Handles event logging and generation of experiment metrics.
- `engagement.py` - Implements disengagement detection and re-engagement logic.
- `robot_io.py` - Handles robot speech, listening gestures, ASR callbacks, and timers.
- `game_runner.py` - Contains the main WOW game loop and integrates all components.

## Requirements

Install the required Python packages in your robot environment:

```bash
pip install -r requirements.txt
```

## Environment variables

Set your Gemini API key in the script, in `config.py`:

```python
GEMINI_API_KEY="YOUR_API_KEY"
```

## Running the experiment
While working on the assignment, we created a virtual environment, which we activated before running our code.

1. Ensure the robot is connected to the network.
2. Make sure the correct WAMP realm is configured in the script.
3. Run code for control or for experimental condition

### Control Condition

Run the control version of the experiment:
```bash
python control_condition.py
```
In this condition, when disengagement is detected the robot says: "Hey, are you there?"

### Experimental Condition

Run the experimental version of the experiment:
```bash
python experimental_condition.py
```
In this condition, when disengagement is detected the robot performs a repair gesture to regain the participant’s attention.

## Game description
The robot can play in two modes:

* **Director mode**: The robot describes a hidden target word and the user guesses.
* **Matcher mode**: The user describes a word and the robot guesses.

The dialogue engine is powered by Gemini.

### How to Play

* When prompted, say **“describe”** (robot describes) or **“match”** (robot guesses).
* Say **“quit”**, **“stop”**, or **“exit”** to stop the game.
* After each round, say **“yes”** to play again or **“no”** to exit.

## Engagement detection
The robot continuously monitors user engagement using:
* Face detection
* Speech activity timing

A **disengagement event** is detected when:
* No face is detected for a defined period of time, OR
* The user stops responding while the robot is expecting input.

When disengagement is detected, the robot triggers the re-engagement strategy corresponding to the current experimental condition.

## Logged Metrics

During each session the robot automatically records behavioural metrics.

The following metrics are logged:
- **Total Interaction Time** - Total duration of the interaction.
- **Disengagement Frequency** - Number of detected disengagement events.
- **Re-engagement Latency** - Time required for the user to re-engage after disengagement.

Two CSV files are saved after each session:
- **events file** - `<session_id>_events.csv`
- **summary file** - `<session_id>_summary.csv`

These files are stored in the `logs/` directory.