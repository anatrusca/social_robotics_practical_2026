from wow.config import DELTA_T

NEUTRAL = [{
    "time": 0.0,
    "data": {
        "body.head.pitch": 0.0,
        "body.head.yaw": 0.0,
        "body.head.roll": 0.0,
        "body.arms.left.upper.pitch": 0.0,
        "body.arms.right.upper.pitch": 0.0,
        "body.arms.left.lower.roll": 0.0,
        "body.arms.right.lower.roll": 0.0,
    }
}]

SPEAK_CYCLES = [
    [
        {"time": 0.0, "data": {"body.head.pitch": -0.05}},
        {"time": 0.5, "data": {"body.head.pitch": 0.05}},
        {"time": 1.0, "data": {"body.head.pitch": -0.03}},
        {"time": 1.5, "data": {"body.head.pitch": 0.0}},
    ],
    [
        {"time": 0.0, "data": {"body.head.roll": 0.08}},
        {"time": 0.5, "data": {"body.head.roll": -0.08}},
        {"time": 1.0, "data": {"body.head.roll": 0.04}},
        {"time": 1.5, "data": {"body.head.roll": 0.0}},
    ],
]

LISTEN_CYCLES = [
    [
        {"time": 0.0, "data": {"body.head.roll": 0.12, "body.head.pitch": -0.04}},
        {"time": 0.7, "data": {"body.head.roll": 0.12, "body.head.pitch": 0.02}},
        {"time": 1.4, "data": {"body.head.roll": 0.0, "body.head.pitch": 0.0}},
    ],
    [
        {"time": 0.0, "data": {"body.head.pitch": 0.04}},
        {"time": 0.7, "data": {"body.head.pitch": -0.03}},
        {"time": 1.4, "data": {"body.head.pitch": 0.0}},
    ],
]

def correct_frames():
    return [
        {"time": 0.0 * DELTA_T, "data": {"body.head.pitch": 0.05, "body.arms.right.upper.pitch": -0.4}},
        {"time": 0.4 * DELTA_T, "data": {"body.arms.right.upper.pitch": -1.5, "body.arms.right.lower.roll": -0.2}},
        {"time": 0.8 * DELTA_T, "data": {"body.arms.right.upper.pitch": -1.5}},
        {"time": 1.2 * DELTA_T, "data": {
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.right.lower.roll": 0.0,
            "body.head.pitch": 0.0
        }},
    ]

def wrong_frames():
    return [
        {"time": 0.1 * DELTA_T, "data": {
            "body.head.yaw": 0.0,
            "body.arms.left.upper.pitch": -0.20,
            "body.arms.right.upper.pitch": -0.20,
            "body.arms.left.lower.roll": 0.0,
            "body.arms.right.lower.roll": 0.0
        }},
        {"time": 0.5 * DELTA_T, "data": {"body.head.yaw": 0.18}},
        {"time": 0.9 * DELTA_T, "data": {"body.head.yaw": -0.18}},
        {"time": 1.3 * DELTA_T, "data": {"body.head.yaw": 0.12}},
        {"time": 1.7 * DELTA_T, "data": {"body.head.yaw": 0.0}},
        {"time": 2.1 * DELTA_T, "data": {
            "body.head.yaw": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.lower.roll": 0.0,
            "body.arms.right.lower.roll": 0.0
        }},
    ]

def thinking_frames():
    return [
        {"time": 0.1, "data": {
            "body.head.pitch": -0.03,
            "body.head.roll": 0.0,
            "body.arms.left.upper.pitch": -1.0,
            "body.arms.left.lower.roll": 0.0,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.right.lower.roll": 0.0,
        }},
        {"time": 1.2, "data": {
            "body.head.pitch": -0.03,
            "body.head.roll": 0.10,
            "body.arms.left.upper.pitch": -0.75,
            "body.arms.left.lower.roll": 0.12,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.right.lower.roll": 0.0,
        }},
        {"time": 2.4, "data": {
            "body.head.pitch": -0.03,
            "body.head.roll": -0.10,
            "body.arms.left.upper.pitch": -0.5,
            "body.arms.left.lower.roll": -0.12,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.right.lower.roll": 0.0,
        }},
        {"time": 3.6, "data": {
            "body.head.pitch": 0.02,
            "body.head.roll": 0.0,
            "body.arms.left.upper.pitch": -0.25,
            "body.arms.left.lower.roll": -0.08,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.right.lower.roll": 0.0,
        }},
        {"time": 5.0, "data": {
            "body.head.pitch": 0.0,
            "body.head.roll": 0.0,
            "body.arms.left.upper.pitch": 0.0,
            "body.arms.left.lower.roll": 0.0,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.right.lower.roll": 0.0,
        }},
    ]

def applause_frames():
    return [
        {"time": 0.5 * DELTA_T, "data": {"body.arms.left.upper.pitch": -1.5, "body.arms.right.upper.pitch": -1.5}},
        {"time": 1.0 * DELTA_T, "data": {"body.arms.left.lower.roll": 0.8, "body.arms.right.lower.roll": -0.8}},
        {"time": 1.5 * DELTA_T, "data": {"body.arms.left.lower.roll": -0.8, "body.arms.right.lower.roll": 0.8}},
        {"time": 2.0 * DELTA_T, "data": {"body.arms.left.lower.roll": 0.8, "body.arms.right.lower.roll": -0.8}},
        {"time": 2.5 * DELTA_T, "data": {"body.arms.left.upper.pitch": 0.0, "body.arms.right.upper.pitch": 0.0}},
    ]

def repair_frames():
    return [
        {"time": 0.0, "data": {
            "body.head.pitch": -0.05,
            "body.arms.left.upper.pitch": -0.5,
            "body.arms.right.upper.pitch": -0.5,
            "body.arms.left.lower.roll": 0.0,
            "body.arms.right.lower.roll": 0.0
        }},
        {"time": 0.2, "data": {
            "body.arms.left.lower.roll": 0.5,
            "body.arms.right.lower.roll": -0.5,
            "body.head.pitch": -0.05,
            "body.arms.left.upper.pitch": -0.5,
            "body.arms.right.upper.pitch": -0.5
        }},
        {"time": 0.4, "data": {
            "body.arms.left.lower.roll": -0.5,
            "body.arms.right.lower.roll": 0.5,
            "body.head.pitch": -0.05,
            "body.arms.left.upper.pitch": -0.5,
            "body.arms.right.upper.pitch": -0.5
        }},
        {"time": 0.6, "data": {
            "body.arms.left.lower.roll": 0.5,
            "body.arms.right.lower.roll": -0.5,
            "body.head.pitch": -0.05,
            "body.arms.left.upper.pitch": -0.5,
            "body.arms.right.upper.pitch": -0.5
        }},
        {"time": 0.8, "data": {
            "body.arms.left.upper.pitch": 0.0,
            "body.arms.right.upper.pitch": 0.0,
            "body.arms.left.lower.roll": 0.0,
            "body.arms.right.lower.roll": 0.0,
            "body.head.pitch": 0.0
        }},
    ]