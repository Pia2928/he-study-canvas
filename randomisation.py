# randomisation.py
"""
Balanced random assignment to the two conditions (canvas_ai, canvas_noai).

Permuted-block randomisation with randomly varying block sizes (4 or 8), from a seeded, pre-generated allocation
sequence stored in the database. A returning participant always gets the original slot back.

Report: "Participants were assigned to conditions by permuted-block randomisation (block sizes 4 and 8, random order)
using a pre-generated, seeded allocation sequence."
"""
import random
import time

CONDITIONS = ["canvas_noai", "canvas_ai"]
BLOCK_SIZES = (4, 8)


def generate_sequence(seed, n_slots):
    rng = random.Random(seed)
    sequence, block = [], 0
    while len(sequence) < n_slots:
        block += 1
        size = rng.choice(BLOCK_SIZES)
        items = CONDITIONS * (size // len(CONDITIONS))
        rng.shuffle(items)
        sequence.extend((block, cond) for cond in items)
    return sequence


def ensure_sequence(db, seed, n_slots):
    """Fill the allocation table once. Never regenerates existing slots."""
    if db.execute("SELECT COUNT(*) FROM allocation").fetchone()[0] >= n_slots:
        return
    db.executemany("INSERT OR IGNORE INTO allocation (slot, block, condition) VALUES (?, ?, ?)",
                   [(i + 1, blk, cond) for i, (blk, cond) in enumerate(generate_sequence(seed, n_slots))])


def assign(db, pid):
    """Atomically take the next free slot (or return the existing one). Returns (condition, slot). Caller commits."""
    if db.in_transaction:
        db.commit()
    db.execute("BEGIN IMMEDIATE")   # write lock first: two simultaneous participants never share a slot
    row = db.execute("SELECT slot, condition FROM allocation WHERE pid = ?", (pid,)).fetchone()
    if row:
        return row["condition"], row["slot"]
    row = db.execute("SELECT slot, condition FROM allocation WHERE pid IS NULL ORDER BY slot LIMIT 1").fetchone()
    if row is None:
        raise RuntimeError("Allocation sequence exhausted; increase ALLOCATION_SLOTS.")
    db.execute("UPDATE allocation SET pid = ?, assigned_at = ? WHERE slot = ?", (pid, time.time(), row["slot"]))
    return row["condition"], row["slot"]
