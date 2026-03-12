import random
import time

from autobahn.twisted.util import sleep
from twisted.internet import reactor, task
from twisted.internet.defer import DeferredList, inlineCallbacks

from alpha_mini_rug import perform_movement
from wow.config import EXIT_CONDITIONS
from wow.movements import SPEAK_CYCLES, LISTEN_CYCLES
from wow.logging_utils import now


def safe_call(d):
    try:
        d.addErrback(lambda f: None)
    except Exception:
        pass
    return d


def stop_listening_gestures(state):
    if state.listening_loop and state.listening_loop.running:
        try:
            state.listening_loop.stop()
        except Exception:
            pass
    state.listening_loop = None


def start_listening_gestures(session, state, period=2.0):
    if state.listening_loop and state.listening_loop.running:
        return

    @inlineCallbacks
    def one_listen_cycle():
        if state.shutting_down or (not state.listening_enabled):
            return
        frames = random.choice(LISTEN_CYCLES)
        try:
            yield perform_movement(session, frames=frames, force=False)
        except Exception:
            pass

    state.listening_loop = task.LoopingCall(one_listen_cycle)
    state.listening_loop.start(period, now=False)


@inlineCallbacks
def speak_with_looping_gestures(session, state, say_deferred):
    done = {"flag": False}

    def _mark_done(result):
        done["flag"] = True
        return result

    say_deferred.addBoth(_mark_done)

    while not done["flag"]:
        if state.shutting_down:
            break
        frames = random.choice(SPEAK_CYCLES)
        try:
            yield perform_movement(session, frames=frames, force=True)
        except Exception:
            pass
        yield sleep(0.05)

    yield say_deferred


def asr(state):
    def _asr(frames):
        if state.shutting_down or (not state.listening_enabled):
            return

        if frames["data"]["body"]["final"]:
            stop_listening_gestures(state)
            state.query = str(frames["data"]["body"]["text"]).strip().lower()
            state.last_user_speech_t = now()
            print("ASR:", state.query)
            state.finish_dialogue = True

    return _asr


@inlineCallbacks
def robot_say(session, state, text, frames=None, auto_speaking_gestures=True):
    if state.shutting_down:
        return

    state.listening_enabled = False
    stop_listening_gestures(state)

    say = session.call("rie.dialogue.say", text=text)

    if frames:
        move = perform_movement(session, frames=frames, force=True)
        yield DeferredList([move, say])
    else:
        if auto_speaking_gestures:
            yield speak_with_looping_gestures(session, state, say)
        else:
            yield say

    yield sleep(0.25)
    state.listening_enabled = True


@inlineCallbacks
def poll_face_read(session, state):
    frame0 = None
    try:
        frames = yield session.call("rie.vision.face.read", time=0)
        if isinstance(frames, list) and len(frames) > 0:
            frame0 = frames[0]
    except Exception:
        frame0 = None

    n = extract_faces_anywhere(frame0)
    faces_n = int(n) if n is not None else 0

    if faces_n > 0:
        state.last_face_t = now()

    return faces_n


def extract_faces_anywhere(obj):
    if obj is None:
        return None
    if isinstance(obj, int):
        return obj
    if isinstance(obj, list):
        return len(obj)
    if not isinstance(obj, dict):
        return None

    for key in ("num_faces", "face_count", "faces_count", "count"):
        if key in obj and isinstance(obj[key], int):
            return obj[key]

    if "faces" in obj:
        value = obj["faces"]
        if isinstance(value, int):
            return value
        if isinstance(value, list):
            return len(value)

    for value in obj.values():
        n = extract_faces_anywhere(value)
        if n is not None:
            return n

    return None


def face_engaged_now(state):
    if state.last_face_t is None:
        return False
    from config import FACE_TIMEOUT
    return (now() - state.last_face_t) <= FACE_TIMEOUT


def speech_engaged_now(state):
    if not state.listening_enabled:
        return True
    if state.last_user_speech_t is None:
        return False
    from config import SPEECH_TIMEOUT
    return (now() - state.last_user_speech_t) <= SPEECH_TIMEOUT


def start_round_timer(session, state, role):
    state.round_timer_active = True

    def timeout_reached():
        if state.shutting_down or (not state.round_timer_active):
            return

        if role == "director":
            safe_call(robot_say(session, state, f"Time's up! You couldn't guess the word '{state.current_word}'."))
            safe_call(session.call("rom.optional.behavior.play", name="BlocklyShrug"))
        elif role == "matcher":
            safe_call(robot_say(session, state, "Time's up! I couldn't guess your word in time."))
            safe_call(session.call("rom.optional.behavior.play", name="BlocklyShrug"))

        from config import GAME_PLAY_AGAIN
        state.game_state = GAME_PLAY_AGAIN
        state.round_timer_active = False

    if state.round_timer_call and state.round_timer_call.active():
        try:
            state.round_timer_call.cancel()
        except Exception:
            pass

    from config import ROUND_TIMER
    state.round_timer_call = reactor.callLater(ROUND_TIMER, timeout_reached)


def cleanup(session, state):
    state.shutting_down = True
    state.listening_enabled = False
    stop_listening_gestures(state)

    state.round_timer_active = False
    if state.round_timer_call and state.round_timer_call.active():
        try:
            state.round_timer_call.cancel()
        except Exception:
            pass
    state.round_timer_call = None

    safe_call(session.call("rie.dialogue.stt.close"))