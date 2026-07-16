#!/usr/bin/env python3
"""One-keystroke human review of every pair in qa.jsonl.

Shows one pair at a time (all fields, in file order); one keystroke decides:

    a      Accept the question as is
    f      Fix the question wording (marked for later editing)
    l      Lose the question
    space  Defer — take some space, consider it later
    u      Undo the previous keystroke
    q      Quit (progress is saved after every keystroke)

Decisions append to review.jsonl ({key, locus, question, decision, ts});
the latest decision per pair wins. Re-running resumes with the undecided
and deferred pairs, in qa.jsonl order.  `review.py --stats` prints the tally.
"""
import datetime
import hashlib
import json
import os
import shutil
import sys
import termios
import textwrap
import time
import tty

HERE = os.path.dirname(os.path.abspath(__file__))
QA_PATH = os.path.join(HERE, "qa.jsonl")
REVIEW_PATH = os.path.join(HERE, "review.jsonl")

DECISIONS = {"a": "accept", "f": "fix", "l": "lose", " ": "defer"}

BOLD, DIM, CYAN, GREEN, YELLOW, RESET = (
    "\033[1m", "\033[2m", "\033[36m", "\033[32m", "\033[33m", "\033[0m")


def pair_key(pair):
    raw = pair["locus"] + "\x1f" + pair["question"]
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


def load_pairs():
    with open(QA_PATH) as f:
        return [json.loads(line) for line in f]


def load_decisions():
    if not os.path.exists(REVIEW_PATH):
        return []
    with open(REVIEW_PATH) as f:
        return [json.loads(line) for line in f]


def latest_by_key(decisions):
    latest = {}
    for d in decisions:
        latest[d["key"]] = d["decision"]
    return latest


def save_all(decisions):
    tmp = REVIEW_PATH + ".tmp"
    with open(tmp, "w") as f:
        for d in decisions:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    os.replace(tmp, REVIEW_PATH)


def append_one(decision):
    with open(REVIEW_PATH, "a") as f:
        f.write(json.dumps(decision, ensure_ascii=False) + "\n")


def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    if ch in ("\x03", "\x04"):  # Ctrl-C / Ctrl-D
        raise KeyboardInterrupt
    return ch.lower()


def tally(decisions):
    counts = {"accept": 0, "fix": 0, "lose": 0, "defer": 0}
    for decision in latest_by_key(decisions).values():
        counts[decision] += 1
    return counts


def fmt_time(seconds):
    seconds = int(seconds)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"


def progress_bar(done, total, session_n, elapsed, remaining, width):
    frac = done / total if total else 1.0
    pct = f"{frac * 100:5.1f}%"
    if session_n and elapsed > 0:
        rate = session_n / elapsed
        eta = fmt_time(remaining / rate)
        rate_s = f"{rate:.2f}it/s" if rate >= 1 else f"{1 / rate:.2f}s/it"
    else:
        eta, rate_s = "?", "?it/s"
    stats = f" {done}/{total} [{fmt_time(elapsed)}<{eta}, {rate_s}]"
    bar_w = max(10, width - len(pct) - len(stats) - 2)
    filled = frac * bar_w
    bar = "█" * int(filled)
    if int(filled) < bar_w:
        bar += " ▏▎▍▌▋▊▉"[int((filled - int(filled)) * 8)]
    return f"{pct}|{bar.ljust(bar_w)}|{stats}"


def render(pair, done, total, counts, session_n, session_t0, remaining):
    width = min(shutil.get_terminal_size().columns, 100)
    out = ["\033[2J\033[H"]  # clear screen, cursor home
    out.append(progress_bar(
        done, total, session_n, time.monotonic() - session_t0, remaining, width))
    out.append(
        f"{DIM}pair {done + 1} of {total} undecided · "
        f"{GREEN}{counts['accept']} accepted{RESET}{DIM} · "
        f"{YELLOW}{counts['fix']} to fix{RESET}{DIM} · "
        f"{counts['lose']} lost · {counts['defer']} deferred{RESET}")
    out.append(DIM + "─" * width + RESET)
    for field, value in pair.items():
        label = f"{CYAN}{field:>12}{RESET}  "
        emphasis = BOLD if field in ("question", "answer") else ""
        wrapped = textwrap.fill(
            str(value), width=width,
            initial_indent=" " * 14, subsequent_indent=" " * 14)
        out.append(label + emphasis + wrapped[14:] + (RESET if emphasis else ""))
    out.append(DIM + "─" * width + RESET)
    out.append(
        f"{BOLD}[a]{RESET}ccept  {BOLD}[f]{RESET}ix wording  "
        f"{BOLD}[l]{RESET}ose  {BOLD}[space]{RESET} later  "
        f"{DIM}[u]ndo  [q]uit{RESET}")
    print("\n".join(out), flush=True)


def main():
    pairs = load_pairs()
    decisions = load_decisions()

    if "--stats" in sys.argv:
        counts = tally(decisions)
        undecided = sum(
            1 for p in pairs
            if latest_by_key(decisions).get(pair_key(p), "defer") == "defer")
        print(f"{len(pairs)} pairs: {counts['accept']} accepted, "
              f"{counts['fix']} to fix, {counts['lose']} lost, "
              f"{counts['defer']} deferred, {undecided} to review")
        return

    if not sys.stdin.isatty():
        sys.exit("review.py needs an interactive terminal (or use --stats)")

    latest = latest_by_key(decisions)
    queue = [p for p in pairs if latest.get(pair_key(p), "defer") == "defer"]
    if not queue:
        print("Nothing left to review — every pair has a decision.")
        return

    done_before = len(pairs) - len(queue)
    undo_stack = []  # (queue index, decision dict) from this session
    session_t0 = time.monotonic()
    i = 0
    while i < len(queue):
        render(queue[i], done_before + i, len(pairs), tally(decisions),
               len(undo_stack), session_t0, len(queue) - i)
        ch = getch()
        if ch == "q":
            break
        if ch == "u":
            if undo_stack:
                i, undone = undo_stack.pop()
                decisions.remove(undone)
                save_all(decisions)
            continue
        if ch in DECISIONS:
            pair = queue[i]
            decision = {
                "key": pair_key(pair),
                "locus": pair["locus"],
                "question": pair["question"],
                "decision": DECISIONS[ch],
                "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            }
            decisions.append(decision)
            append_one(decision)
            undo_stack.append((i, decision))
            i += 1
        # any other key: ignore, re-render

    counts = tally(decisions)
    remaining = len(queue) - i
    print(f"\nSaved to {os.path.basename(REVIEW_PATH)}. "
          f"{counts['accept']} accepted, {counts['fix']} to fix, "
          f"{counts['lose']} lost, {counts['defer']} deferred; "
          f"{remaining} still to review this pass.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted — progress is saved.")
