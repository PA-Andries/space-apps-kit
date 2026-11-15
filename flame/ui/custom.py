"""Two helpers for the sliders of page 1.

- When the sliders leave the range of the chosen place, the place is no longer selected: the environment
  is the user's own ("Personnalisé" in the contract, "Custom" on screen).
- When the two handles of a slider sit on the same point, only one number is shown above them.
"""

import streamlit as st

from flame.ui.environment import conditions

TOLERANCE = 1e-9


def within(handles: tuple, allowed: tuple | None, scale: tuple) -> bool:
    """True when the two slider `handles` stay inside the range `allowed` (None = no bound on that side).

    A missing bound is the end of the slider's `scale`: "30 % or more" allows every handle from 30 up.
    """
    low, high = handles
    floor, ceiling = allowed or (None, None)
    floor = scale[0] if floor is None else float(floor)
    ceiling = scale[1] if ceiling is None else float(ceiling)
    return low >= floor - TOLERANCE and high <= ceiling + TOLERANCE


def left_the_place(place: str, sliders: dict[str, tuple[str, tuple]]) -> bool:
    """True when a slider now sits outside the range that `place` gives for its condition.

    `sliders`: {condition of the place: (session key of its slider, scale)}, for example
    {"oxygene_pct": ("ui_oxygen", (0.0, 100.0))}. A slider that is not on screen yet is not counted.
    """
    known = conditions(place)
    for condition, (key, scale) in sliders.items():
        handles = st.session_state.get(key)
        if handles is not None and not within(handles, known.get(condition), scale):
            return True
    return False


def single_value_style(keys: list[str]) -> None:
    """Show one number instead of two above each range slider of `keys` whose handles sit on the same point."""
    # Each handle carries its own number: the first handle is the one followed by another handle.
    value = '[data-testid="stSliderThumbValue"]'
    rules = [
        f".st-key-{key} div:has(> {value}):has(+ div > {value}) > {value} {{ visibility: hidden; }}"
        for key in keys
        if isinstance(st.session_state.get(key), (tuple, list))
        and abs(st.session_state[key][0] - st.session_state[key][1]) < TOLERANCE
    ]
    if rules:
        st.html("<style>" + "\n".join(rules) + "</style>")
