import os

API_KEY = os.getenv("GEMINI_API_KEY", "")
OUTPUT_DIR = os.getenv("WOW_LOG_DIR", "logs")

FACE_TIMEOUT = 3.5
SPEECH_TIMEOUT = 10.0
MONITOR_PERIOD = 0.3

ROUND_TIMER = 180
EXIT_CONDITIONS = (":q", "quit", "exit", "stop")

GAME_IDLE = "idle"
GAME_CHOOSE_ROLE = "choose_role"
GAME_DIRECTOR = "director"
GAME_MATCHER = "matcher"
GAME_PLAY_AGAIN = "play_again"

DELTA_T = 2

REALM = "rie.69b276a4b788cadff345d775"
WAMP_URL = "ws://wamp.robotsindeklas.nl"