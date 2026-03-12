from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks

from alpha_mini_rug import perform_movement
from logging_utils import log_event, now
from wow.movements import NEUTRAL, REPAIR_FRAMES
from wow.robot_io import (
    face_engaged_now,
    poll_face_read,
    repair_behavior,
    robot_say,
    safe_call,
    speech_engaged_now,
)


@inlineCallbacks
def repair_behavior(session, state):
    print("NOT PAYING ATTENTION")
    try:
        yield perform_movement(session, frames=REPAIR_FRAMES, force=True)
    except Exception:
        pass


@inlineCallbacks
def engagement_tick_control(session, state):
    if not state.listening_enabled:
        return

    yield poll_face_read(session, state)
    f_ok = face_engaged_now(state)
    s_ok = speech_engaged_now(state)
    engaged_now = f_ok or s_ok

    if (not engaged_now) and (not state.disengaged):
        state.disengaged = True
        state.disengage_start_t = now()
        state.disengagement_frequency_count += 1
        state.disengagement_event_index += 1

        log_event(
            state,
            event_type="disengagement_start",
            disengagement_event_index_val=state.disengagement_event_index,
        )

        safe_call(robot_say(session, state, "Hey, are you there?", auto_speaking_gestures=False))

    if engaged_now and state.disengaged:
        state.disengaged = False
        latency = (now() - state.disengage_start_t) if state.disengage_start_t else 0.0
        state.reengagement_latencies_s.append(latency)

        log_event(
            state,
            event_type="reengagement",
            disengagement_event_index_val=state.disengagement_event_index,
            reengagement_latency_s=latency,
        )


@inlineCallbacks
def engagement_tick_experimental(session, state):
    if not state.listening_enabled:
        return

    yield poll_face_read(session, state)
    f_ok = face_engaged_now(state)
    s_ok = speech_engaged_now(state)
    engaged_now = f_ok or s_ok

    if (not engaged_now) and (not state.disengaged):
        state.disengaged = True
        state.disengage_start_t = now()
        state.disengagement_frequency_count += 1
        state.disengagement_event_index += 1

        log_event(
            state,
            event_type="disengagement_start",
            disengagement_event_index_val=state.disengagement_event_index,
        )

        yield session.call("rom.optional.behavior.play", name="BlocklyStand")
        yield perform_movement(session, frames=NEUTRAL, force=True)
        yield repair_behavior(session, state)
        yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    if engaged_now and state.disengaged:
        state.disengaged = False
        latency = (now() - state.disengage_start_t) if state.disengage_start_t else 0.0
        state.reengagement_latencies_s.append(latency)

        log_event(
            state,
            event_type="reengagement",
            disengagement_event_index_val=state.disengagement_event_index,
            reengagement_latency_s=latency,
        )