import json
import os
import re
from datetime import datetime

from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks

from alpha_mini_rug import perform_movement
from google import genai

from wow.config import (
    API_KEY,
    EXIT_CONDITIONS,
    GAME_CHOOSE_ROLE,
    GAME_DIRECTOR,
    GAME_IDLE,
    GAME_MATCHER,
    GAME_PLAY_AGAIN,
    OUTPUT_DIR,
)
from wow.logging_utils import compute_summary_row, now, write_csv
from wow.movements import (
    APPLAUSE_FRAMES,
    CORRECT_FRAMES,
    NEUTRAL,
    THINKING_FRAMES,
    WRONG_FRAMES,
)
from wow.prompts import DIRECTOR_PROMPT, MATCHER_PROMPT
from wow.robot_io import (
    asr,
    cleanup,
    robot_say,
    safe_call,
    start_listening_gestures,
    start_round_timer,
)
from wow.state import State

chatbot = genai.Client(api_key=API_KEY)


def parse_director_json(text: str):
    text = (text or "").strip()
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in: {text[:200]}")
    return json.loads(match.group(0))


def clean_matcher_reply(text: str) -> str:
    return (text or "").strip().strip('"').strip("'")


@inlineCallbacks
def _main(session, engagement_tick_fn):
    from twisted.internet import task

    state = State()
    state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    state.session_start_t = now()
    state.last_face_t = now()
    state.last_user_speech_t = now()

    from config import MONITOR_PERIOD

    yield session.call("rie.dialogue.config.language", lang="en")
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    yield session.call("rie.vision.face.stream")
    yield session.call("rie.vision.face.find", active=True)

    yield session.call("rom.optional.behavior.play", name="BlocklyInviteRight")
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    yield robot_say(session, state, "Hello! Let's play With Other Words. Say quit anytime to stop.")

    yield session.subscribe(asr(state), "rie.dialogue.stt.stream")
    yield session.call("rie.dialogue.stt.stream")

    engagement_loop = task.LoopingCall(engagement_tick_fn, session, state)
    engagement_loop.start(MONITOR_PERIOD, now=False)

    dialogue = True
    while dialogue:
        if state.finish_dialogue and any(cmd in state.query for cmd in EXIT_CONDITIONS):
            dialogue = False
            yield robot_say(session, state, "Okay, goodbye!", auto_speaking_gestures=False)
            break

        if state.game_state == GAME_IDLE:
            yield robot_say(session, state, "Do you want me to describe a word, or should I match your word?")
            yield sleep(0.25)
            start_listening_gestures(session, state)
            state.game_state = GAME_CHOOSE_ROLE

        elif state.game_state == GAME_CHOOSE_ROLE and state.finish_dialogue:
            if "match" in state.query:
                state.game_state = GAME_MATCHER
                state.current_role = "matcher"
                state.state_just_entered = True

                yield robot_say(session, state, "Describe a word without saying its name.")
                yield sleep(0.3)
                start_listening_gestures(session, state)
                start_round_timer(session, state, state.current_role)

            elif "describe" in state.query:
                state.game_state = GAME_DIRECTOR
                state.current_role = "director"
                state.state_just_entered = True
                state.current_word = ""
                state.taboo_words = []

                yield robot_say(session, state, "Okay. Guess the word.")
                yield sleep(0.3)
                start_listening_gestures(session, state)
                start_round_timer(session, state, state.current_role)

            else:
                yield robot_say(session, state, "Please say describe or match.")
                yield sleep(0.25)
                start_listening_gestures(session, state)

            state.finish_dialogue = False
            state.query = ""

        elif state.game_state == GAME_DIRECTOR and (state.finish_dialogue or state.state_just_entered):
            human_guess = state.query.strip().lower() if state.finish_dialogue else ""
            response = chatbot.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    DIRECTOR_PROMPT,
                    f"active_target: {state.current_word}\n",
                    f"active_taboo: {', '.join(state.taboo_words) if state.taboo_words else ''}\n",
                    f"human_guess: {human_guess}\n",
                ],
            )

            try:
                data = parse_director_json(response.text)
            except Exception:
                data = {
                    "status": "CLUE",
                    "target": state.current_word,
                    "taboo": state.taboo_words,
                    "say": "Hmm, I couldn't think of a clue. Try again."
                }

            state.current_word = data.get("target", state.current_word)
            state.taboo_words = data.get("taboo", state.taboo_words)
            status = (data.get("status") or "").upper()
            say = (data.get("say") or "").strip()

            if status == "CORRECT" or say.upper() == "CORRECT":
                state.round_timer_active = False
                yield session.call("rom.optional.behavior.play", name="BlocklyStand")
                yield perform_movement(session, frames=NEUTRAL, force=True)

                yield session.call("rom.optional.behavior.play", name="BlocklyStand")
                yield robot_say(session, state, "Correct! Well done.", CORRECT_FRAMES)
                yield sleep(0.4)

                state.game_state = GAME_PLAY_AGAIN
                yield robot_say(session, state, "Do you want to play again? Say yes or no.")
                yield sleep(0.25)
                start_listening_gestures(session, state)

                state.state_just_entered = False
                state.finish_dialogue = False
                state.query = ""
                continue

            if state.finish_dialogue and human_guess:
                yield session.call("rom.optional.behavior.play", name="BlocklyStand")
                yield perform_movement(session, frames=NEUTRAL, force=True)

                yield session.call("rom.optional.behavior.play", name="BlocklyStand")
                yield robot_say(session, state, "Not quite. Try again.", WRONG_FRAMES)
                yield sleep(0.25)

            yield robot_say(session, state, say if say else "Try another guess.")
            yield sleep(0.2)
            start_listening_gestures(session, state)

            state.state_just_entered = False
            state.finish_dialogue = False
            state.query = ""

        elif state.game_state == GAME_MATCHER and state.finish_dialogue:
            yield sleep(0.3)

            if any(w in state.query for w in ["yes", "correct", "right"]):
                state.round_timer_active = False
                yield session.call("rom.optional.behavior.play", name="BlocklyStand")
                yield perform_movement(session, frames=NEUTRAL, force=True)

                yield session.call("rom.optional.behavior.play", name="BlocklyStand")
                yield robot_say(session, state, "Yes! I guessed it!", APPLAUSE_FRAMES)
                yield sleep(0.4)

                state.game_state = GAME_PLAY_AGAIN
                yield robot_say(session, state, "Do you want to play again? Say yes or no.")
                yield sleep(0.25)
                start_listening_gestures(session, state)

                state.finish_dialogue = False
                state.query = ""
                continue

            yield session.call("rom.optional.behavior.play", name="BlocklyStand")
            yield perform_movement(session, frames=NEUTRAL, force=True)

            yield session.call("rom.optional.behavior.play", name="BlocklyStand")
            yield robot_say(session, state, "Let me think...", THINKING_FRAMES)
            yield sleep(0.35)

            response = chatbot.models.generate_content(
                model="gemini-2.5-flash",
                contents=[MATCHER_PROMPT, state.query],
            )

            reply = clean_matcher_reply(response.text)
            reply_lower = reply.lower()

            if reply_lower == "i don't know, tell me more." or "tell me more" in reply_lower:
                yield robot_say(session, state, "I don't know, tell me more.")
            else:
                yield robot_say(session, state, f"Is it {reply}?")

            yield sleep(0.35)
            start_listening_gestures(session, state)

            state.finish_dialogue = False
            state.query = ""

        elif state.game_state == GAME_PLAY_AGAIN and state.finish_dialogue:
            if "yes" in state.query:
                state.game_state = GAME_IDLE
                state.finish_dialogue = False
                state.query = ""
            elif "no" in state.query:
                yield robot_say(session, state, "Thanks for playing!")
                break
            else:
                yield robot_say(session, state, "Please say yes or no.")
                yield sleep(0.2)
                start_listening_gestures(session, state)
                state.finish_dialogue = False
                state.query = ""

        yield sleep(0.5)

    try:
        if engagement_loop.running:
            engagement_loop.stop()
    except Exception:
        pass

    state.session_end_t = now()

    events_path = os.path.join(OUTPUT_DIR, f"{state.session_id}_events.csv")
    summary_path = os.path.join(OUTPUT_DIR, f"{state.session_id}_summary.csv")

    write_csv(
        events_path,
        fieldnames=[
            "session_id",
            "time_since_start_s",
            "event_type",
            "disengagement_event_index",
            "reengagement_latency_s",
        ],
        rows=state.event_rows
    )

    summary_row = compute_summary_row(state)
    write_csv(
        summary_path,
        fieldnames=list(summary_row.keys()),
        rows=[summary_row]
    )

    cleanup(session, state)
    yield sleep(0.2)
    safe_call(session.call("rom.optional.behavior.play", name="BlocklyCrouch"))
    session.leave()


@inlineCallbacks
def main_control(session, details):
    from engagement import engagement_tick_control
    yield _main(session, engagement_tick_control)


@inlineCallbacks
def main_experimental(session, details):
    from engagement import engagement_tick_experimental
    yield _main(session, engagement_tick_experimental)