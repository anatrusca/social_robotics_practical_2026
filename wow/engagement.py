from twisted.internet.defer import inlineCallbacks
from alpha_mini_rug import perform_movement

from wow.config import FACE_TIMEOUT, SPEECH_TIMEOUT
from wow.logging_utils import log_event

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

def face_engaged_now(state, now_fn):
    if state.last_face_t is None:
        return False
    return (now_fn() - state.last_face_t) <= FACE_TIMEOUT

def speech_engaged_now(state, now_fn):
    if not state.listening_enabled:
        return True
    if state.last_user_speech_t is None:
        return False
    return (now_fn() - state.last_user_speech_t) <= SPEECH_TIMEOUT

@inlineCallbacks
def poll_face_read(session, state, now_fn):
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
        state.last_face_t = now_fn()

    return faces_n

@inlineCallbacks
def repair_behavior(session, frames):
    try:
        yield perform_movement(session, frames=frames, force=True)
    except Exception:
        pass

@inlineCallbacks
def engagement_tick(session, state, condition, now_fn, robot_say_fn, repair_frames):
    if not state.listening_enabled:
        return

    yield poll_face_read(session, state, now_fn)
    engaged_now = face_engaged_now(state, now_fn)

    if (not engaged_now) and (not state.disengaged):
        state.disengaged = True
        state.disengage_start_t = now_fn()
        state.disengagement_frequency_count += 1
        state.disengagement_event_index += 1

        log_event(
            state,
            now_fn,
            event_type="disengagement_start",
            disengagement_event_index_val=state.disengagement_event_index,
        )

        if condition == "control":
            robot_say_fn("Hey, are you there?", auto_speaking_gestures=False)
        elif condition == "experimental":
            yield session.call("rom.optional.behavior.play", name="BlocklyStand")
            yield repair_behavior(session, repair_frames)
            yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    if engaged_now and state.disengaged:
        state.disengaged = False
        latency = (now_fn() - state.disengage_start_t) if state.disengage_start_t else 0.0
        state.reengagement_latencies_s.append(latency)

        log_event(
            state,
            now_fn,
            event_type="reengagement",
            disengagement_event_index_val=state.disengagement_event_index,
            reengagement_latency_s=latency,
        )