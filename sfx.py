"""
sfx.py - Sound-effect engine for RodentMon.
Synthesises all effects in memory using square/triangle waves,
noise bursts, and frequency chirps.  No audio files required.
"""

import numpy as np
import pygame

SAMPLE_RATE = 22050   # must match the mixer frequency

# ---------------------------------------------------------------------------
# Primitives (duplicated from music.py so sfx.py is self-contained)
# ---------------------------------------------------------------------------

_SEMIS = {
    'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,
    'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11,
}

def _freq(name: str) -> float:
    if len(name) == 3:
        pc, octave = name[:2], int(name[2])
    else:
        pc, octave = name[0], int(name[1])
    midi = (octave + 1) * 12 + _SEMIS[pc]
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)

def _env(n, atk=0.004, rel=0.020):
    e = np.ones(n, np.float32)
    a = min(int(atk * SAMPLE_RATE), n // 4)
    r = min(int(rel * SAMPLE_RATE), n // 4)
    if a: e[:a]  = np.linspace(0, 1, a, dtype=np.float32)
    if r: e[-r:] = np.linspace(1, 0, r, dtype=np.float32)
    return e

def _square(freq: float, dur: float, vol=0.25, duty=0.50) -> np.ndarray:
    n = max(1, int(SAMPLE_RATE * dur))
    if freq == 0:
        return np.zeros(n, np.float32)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    w = np.where(t * freq % 1.0 < duty, 1.0, -1.0).astype(np.float32)
    return w * _env(n) * vol

def _triangle(freq: float, dur: float, vol=0.20) -> np.ndarray:
    n = max(1, int(SAMPLE_RATE * dur))
    if freq == 0:
        return np.zeros(n, np.float32)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    w = (2 * np.abs(2 * (t * freq % 1.0) - 1) - 1).astype(np.float32)
    return w * _env(n) * vol

def _noise(dur: float, vol=0.18) -> np.ndarray:
    n = max(1, int(SAMPLE_RATE * dur))
    rng = np.random.default_rng()
    w = rng.uniform(-1, 1, n).astype(np.float32)
    r = min(int(0.06 * SAMPLE_RATE), n)
    if r: w[-r:] *= np.linspace(1, 0, r, dtype=np.float32)
    return w * vol

def _chirp(f0: float, f1: float, dur: float, vol=0.22, duty=0.50) -> np.ndarray:
    """Square-wave frequency sweep from f0 to f1 over dur seconds."""
    n = max(1, int(SAMPLE_RATE * dur))
    freqs = np.linspace(f0, f1, n, dtype=np.float32)
    phase = np.cumsum(freqs) / SAMPLE_RATE
    w = np.where(phase % 1.0 < duty, 1.0, -1.0).astype(np.float32)
    return w * _env(n) * vol

def _seq(*parts) -> np.ndarray:
    """Concatenate an arbitrary number of sample arrays."""
    return np.concatenate(parts)

def _mix(*channels) -> np.ndarray:
    maxlen = max(len(c) for c in channels)
    out = np.zeros(maxlen, np.float32)
    for c in channels:
        out[:len(c)] += c
    peak = float(np.max(np.abs(out)))
    if peak > 0.92:
        out *= 0.92 / peak
    return out

def _gap(dur: float) -> np.ndarray:
    return np.zeros(max(1, int(SAMPLE_RATE * dur)), np.float32)

def _to_sound(arr: np.ndarray) -> pygame.mixer.Sound:
    s16 = (arr * 32767.0).clip(-32768, 32767).astype(np.int16)
    if pygame.mixer.get_init()[2] == 2:     # stereo mixer
        s16 = np.column_stack([s16, s16])
    return pygame.sndarray.make_sound(s16)

# ---------------------------------------------------------------------------
# Sound recipes
# ---------------------------------------------------------------------------

def _make_cursor():
    """Short high blip — UI cursor movement."""
    return _square(_freq('A5'), 0.035, vol=0.18)

def _make_confirm():
    """Two-note ascending chime — menu confirm."""
    return _seq(
        _square(_freq('C6'), 0.045, vol=0.22),
        _gap(0.010),
        _square(_freq('E6'), 0.060, vol=0.22),
    )

def _make_back():
    """Single descending note — cancel/back."""
    return _square(_freq('G4'), 0.070, vol=0.16, duty=0.30)

def _make_text():
    """Ultra-short blip — text box advance."""
    return _square(_freq('G5'), 0.028, vol=0.12)

def _make_step():
    """Quiet soft tick — player footstep."""
    return _mix(
        _noise(0.022, vol=0.08),
        _triangle(_freq('C3'), 0.022, vol=0.06),
    )

def _make_attack():
    """Impact thud — physical move lands."""
    return _mix(
        _noise(0.055, vol=0.22),
        _chirp(300, 80, 0.090, vol=0.14),
    )

def _make_hit():
    """Sharp crack — taking damage."""
    return _mix(
        _noise(0.045, vol=0.28),
        _square(_freq('A3'), 0.040, vol=0.14),
    )

def _make_super_effective():
    """Two sharp high notes — super-effective hit."""
    return _seq(
        _square(_freq('B6'), 0.040, vol=0.24),
        _gap(0.008),
        _square(_freq('E7'), 0.055, vol=0.24),
    )

def _make_not_effective():
    """Muffled low thud — not very effective."""
    return _square(_freq('D4'), 0.085, vol=0.16, duty=0.25)

def _make_faint():
    """Descending 4-note sequence — rodent faints."""
    notes = [('G5', 0.095), ('E5', 0.095), ('C5', 0.095), ('A4', 0.130)]
    parts = []
    for n, d in notes:
        parts.append(_square(_freq(n), d, vol=0.22))
        parts.append(_gap(0.012))
    return _seq(*parts)

def _make_catch_throw():
    """Rising frequency sweep — Rodent Ball thrown."""
    return _chirp(280, 1100, 0.190, vol=0.22)

def _make_catch_success():
    """5-note ascending fanfare — catch successful."""
    notes = ['C5', 'E5', 'G5', 'C6', 'E6']
    parts = []
    for n in notes:
        parts.append(_square(_freq(n), 0.068, vol=0.24))
        parts.append(_gap(0.010))
    return _seq(*parts)

def _make_catch_fail():
    """2-note descending drop — catch failed."""
    return _seq(
        _square(_freq('E5'), 0.090, vol=0.20),
        _gap(0.012),
        _square(_freq('B4'), 0.110, vol=0.20),
    )

def _make_level_up():
    """6-note ascending fanfare — level up."""
    notes = ['C5', 'E5', 'G5', 'C6', 'E6', 'G6']
    parts = []
    for n in notes:
        parts.append(_square(_freq(n), 0.065, vol=0.26))
        parts.append(_gap(0.010))
    # Hold last note
    parts.append(_square(_freq('G6'), 0.120, vol=0.20))
    return _seq(*parts)

def _make_evolve():
    """Long majestic ascending arpeggio — evolution."""
    notes = ['C4', 'E4', 'G4', 'C5', 'E5', 'G5', 'C6']
    parts = []
    for n in notes:
        parts.append(_square(_freq(n), 0.082, vol=0.26))
        parts.append(_gap(0.012))
    parts.append(_square(_freq('C6'), 0.200, vol=0.22))
    return _seq(*parts)

def _make_xp():
    """Short ascending chirp — XP gained."""
    return _chirp(380, 720, 0.065, vol=0.16)

def _make_save():
    """3-note pleasant arp — game saved."""
    notes = ['C5', 'E5', 'G5']
    parts = []
    for n in notes:
        parts.append(_square(_freq(n), 0.060, vol=0.20))
        parts.append(_gap(0.010))
    return _seq(*parts)

def _make_run():
    """Descending chirp — fleeing battle."""
    return _chirp(700, 120, 0.160, vol=0.20)

def _make_win():
    """Short upbeat jingle — battle victory."""
    notes = [('C6', 0.070), ('E6', 0.070), ('G6', 0.070),
             ('REST', 0.040), ('G6', 0.100), ('C7', 0.180)]
    parts = []
    for n, d in notes:
        if n == 'REST':
            parts.append(_gap(d))
        else:
            parts.append(_square(_freq(n), d, vol=0.26))
            parts.append(_gap(0.008))
    return _seq(*parts)

# ---------------------------------------------------------------------------
# Public SoundFX class
# ---------------------------------------------------------------------------

_RECIPES = {
    'cursor':          _make_cursor,
    'confirm':         _make_confirm,
    'back':            _make_back,
    'text':            _make_text,
    'step':            _make_step,
    'attack':          _make_attack,
    'hit':             _make_hit,
    'super_effective': _make_super_effective,
    'not_effective':   _make_not_effective,
    'faint':           _make_faint,
    'catch_throw':     _make_catch_throw,
    'catch_success':   _make_catch_success,
    'catch_fail':      _make_catch_fail,
    'level_up':        _make_level_up,
    'evolve':          _make_evolve,
    'xp':              _make_xp,
    'save':            _make_save,
    'run':             _make_run,
    'win':             _make_win,
}


class SoundFX:
    """Pre-synthesised sound effects, played on demand."""

    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
        # Reserve enough channels: channel 0 = music, 1+ = sfx
        pygame.mixer.set_num_channels(max(pygame.mixer.get_num_channels(), 16))

        self._sounds: dict = {}
        for name, fn in _RECIPES.items():
            self._sounds[name] = _to_sound(fn())
        self.enabled = True

    def play(self, name: str):
        """Play a named sound effect on any free channel (no-op if disabled)."""
        if not self.enabled:
            return
        s = self._sounds.get(name)
        if s:
            # find_channel(True) forces a channel even if all busy
            ch = pygame.mixer.find_channel(True)
            if ch:
                ch.play(s)

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
