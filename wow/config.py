import os

API_KEY = os.getenv("GEMINI_API_KEY", "")

FACE_TIMEOUT = 3.5
SPEECH_TIMEOUT = 10.0
MONITOR_PERIOD = 0.3

OUTPUT_DIR = os.getenv("WOW_LOG_DIR", "logs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ROUND_TIMER = 180
EXIT_CONDITIONS = (":q", "quit", "exit", "stop")

GAME_IDLE = "idle"
GAME_CHOOSE_ROLE = "choose_role"
GAME_DIRECTOR = "director"
GAME_MATCHER = "matcher"
GAME_PLAY_AGAIN = "play_again"

delta_t = 2