import random

from autobahn.twisted.util import sleep
from twisted.internet import reactor, task
from twisted.internet.defer import DeferredList, inlineCallbacks

from alpha_mini_rug import perform_movement
from wow.config import ROUND_TIMER
from wow.movements import LISTEN_CYCLES, SPEAK_CYCLES

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

def make_asr_callback(state, now_fn):
    def asr(frames):
        if state.shutting_down or (not state.listening_enabled):
            return
        if frames["data"]["body"]["final"]:
            stop_listening_gestures(state)
            state.query = str(frames["data"]["body"]["text"]).strip().lower()
            state.last_user_speech_t = now_fn()
            print("ASR:", state.query)
            state.finish_dialogue = True
    return asr

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

        state.game_state = "play_again"
        state.round_timer_active = False

    if state.round_timer_call and state.round_timer_call.active():
        try:
            state.round_timer_call.cancel()
        except Exception:
            pass

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