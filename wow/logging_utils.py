import csv
import statistics

def t_rel_s(state, now_fn):
    return (now_fn() - state.session_start_t) if state.session_start_t else 0.0

def log_event(state, now_fn, event_type, disengagement_event_index_val=None, reengagement_latency_s=None):
    state.event_rows.append({
        "session_id": state.session_id,
        "time_since_start_s": round(t_rel_s(state, now_fn), 3),
        "event_type": event_type,
        "disengagement_event_index": disengagement_event_index_val if disengagement_event_index_val is not None else "",
        "reengagement_latency_s": round(reengagement_latency_s, 3) if isinstance(reengagement_latency_s, (int, float)) else "",
    })

def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def compute_summary_row(state):
    total_interaction_time_s = (
        state.session_end_t - state.session_start_t
        if (state.session_start_t and state.session_end_t) else 0.0
    )

    if state.reengagement_latencies_s:
        mean_reengagement_latency_s = statistics.mean(state.reengagement_latencies_s)
        median_reengagement_latency_s = statistics.median(state.reengagement_latencies_s)
    else:
        mean_reengagement_latency_s = 0.0
        median_reengagement_latency_s = 0.0

    return {
        "session_id": state.session_id,
        "total_interaction_time_s": round(total_interaction_time_s, 3),
        "disengagement_frequency_count": state.disengagement_frequency_count,
        "mean_reengagement_latency_s": round(mean_reengagement_latency_s, 3),
        "median_reengagement_latency_s": round(median_reengagement_latency_s, 3),
    }