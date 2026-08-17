Fix the off-by-one in first_n_squares. Tests already exist. No new features.

Contract: first_n_squares(n) returns the squares of 0 .. n-1 (n numbers).
first_n_squares(0) == []
first_n_squares(3) == [0, 1, 4]

Broken code:

def first_n_squares(n: int) -> list[int]:
    """Return squares of 0 .. n-1 (n numbers)."""
    out: list[int] = []
    for i in range(n + 1):
        out.append(i * i)
    return out

Reply with the full corrected function only. No markdown, no explanation.
