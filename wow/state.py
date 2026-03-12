from dataclasses import dataclass, field
from typing import List, Optional

from wow.config import GAME_IDLE

@dataclass
class RuntimeState:
    finish_dialogue: bool = False
    query: str = ""
    listening_enabled: bool = True

    game_state: str = GAME_IDLE
    state_just_entered: bool = True

    current_word: str = ""
    taboo_words: List[str] = field(default_factory=list)
    current_role: Optional[str] = None

    round_timer_active: bool = False
    round_timer_call = None
    shutting_down: bool = False
    listening_loop = None

    session_id: Optional[str] = None
    session_start_t: Optional[float] = None
    session_end_t: Optional[float] = None

    last_face_t: Optional[float] = None
    last_user_speech_t: Optional[float] = None

    disengaged: bool = False
    disengage_start_t: Optional[float] = None
    disengagement_frequency_count: int = 0
    disengagement_event_index: int = 0
    reengagement_latencies_s: List[float] = field(default_factory=list)

    event_rows: List[dict] = field(default_factory=list)