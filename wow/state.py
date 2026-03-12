from wow.config import GAME_IDLE


class State:
    def __init__(self):
        self.finish_dialogue = False
        self.query = ""
        self.listening_enabled = True

        self.game_state = GAME_IDLE
        self.state_just_entered = True

        self.current_word = ""
        self.taboo_words = []
        self.current_role = None

        self.round_timer_active = False
        self.round_timer_call = None
        self.shutting_down = False
        self.listening_loop = None

        self.session_id = None
        self.session_start_t = None
        self.session_end_t = None

        self.last_face_t = None
        self.last_user_speech_t = None

        self.disengaged = False
        self.disengage_start_t = None
        self.disengagement_frequency_count = 0
        self.disengagement_event_index = 0
        self.reengagement_latencies_s = []

        self.event_rows = []