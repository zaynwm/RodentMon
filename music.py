"""
music.py - Chiptune music engine for RodentMon
Synthesises 8-bit style audio entirely in memory using square waves
(melody/harmony), triangle waves (bass), and noise bursts (percussion).
No external audio files required.
"""

import numpy as np
import pygame

SAMPLE_RATE = 22050

# ---------------------------------------------------------------------------
# Note → frequency
# ---------------------------------------------------------------------------
_SEMIS = {
    'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,
    'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11,
}

def _freq(name: str) -> float:
    if name == 'REST':
        return 0.0
    if len(name) == 3:          # e.g. 'C#5', 'F#4'
        pc, octave = name[:2], int(name[2])
    else:                        # e.g. 'C5', 'A4'
        pc, octave = name[0],   int(name[1])
    midi = (octave + 1) * 12 + _SEMIS[pc]
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)

# ---------------------------------------------------------------------------
# Waveform generators
# ---------------------------------------------------------------------------

def _env(n: int, atk=0.005, rel=0.018) -> np.ndarray:
    e = np.ones(n, np.float32)
    a = min(int(atk * SAMPLE_RATE), n // 4)
    r = min(int(rel * SAMPLE_RATE), n // 4)
    if a: e[:a]  = np.linspace(0.0, 1.0, a, dtype=np.float32)
    if r: e[-r:] = np.linspace(1.0, 0.0, r, dtype=np.float32)
    return e

def _square(freq: float, dur: float, vol=0.28, duty=0.50) -> np.ndarray:
    n = max(1, int(SAMPLE_RATE * dur))
    if freq == 0.0:
        return np.zeros(n, np.float32)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    w = np.where(t * freq % 1.0 < duty, 1.0, -1.0).astype(np.float32)
    return w * _env(n) * vol

def _triangle(freq: float, dur: float, vol=0.20) -> np.ndarray:
    n = max(1, int(SAMPLE_RATE * dur))
    if freq == 0.0:
        return np.zeros(n, np.float32)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    w = (2.0 * np.abs(2.0 * (t * freq % 1.0) - 1.0) - 1.0).astype(np.float32)
    return w * _env(n) * vol

def _noise(dur: float, vol=0.14) -> np.ndarray:
    n = max(1, int(SAMPLE_RATE * dur))
    rng = np.random.default_rng()
    w = rng.uniform(-1.0, 1.0, n).astype(np.float32)
    r = min(int(0.06 * SAMPLE_RATE), n)
    if r:
        w[-r:] *= np.linspace(1.0, 0.0, r, dtype=np.float32)
    return w * vol

# ---------------------------------------------------------------------------
# Channel renderer
# ---------------------------------------------------------------------------

def _render_melodic(seq, bpm: float, wave_fn) -> np.ndarray:
    """Render a list of (note_name, beats) with a melodic wave function."""
    beat = 60.0 / bpm
    parts = []
    for note, beats in seq:
        dur      = beat * beats
        note_dur = dur * 0.87
        gap_dur  = dur * 0.13
        parts.append(wave_fn(_freq(note), note_dur))
        parts.append(np.zeros(max(1, int(SAMPLE_RATE * gap_dur)), np.float32))
    return np.concatenate(parts)

def _render_drums(seq, bpm: float) -> np.ndarray:
    """Render a list of ('kick'|'snare'|'REST', beats) as noise bursts."""
    beat = 60.0 / bpm
    kick_vol,  snare_vol  = 0.18, 0.12
    parts = []
    for kind, beats in seq:
        dur = beat * beats
        if kind == 'kick':
            # Low-pass'd noise burst for kick feel
            b = _noise(min(dur, 0.08), kick_vol)
            pad = np.zeros(max(1, int(SAMPLE_RATE * dur) - len(b)), np.float32)
            parts.append(np.concatenate([b, pad]))
        elif kind == 'snare':
            b = _noise(min(dur, 0.06), snare_vol)
            pad = np.zeros(max(1, int(SAMPLE_RATE * dur) - len(b)), np.float32)
            parts.append(np.concatenate([b, pad]))
        else:
            parts.append(np.zeros(max(1, int(SAMPLE_RATE * dur)), np.float32))
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

def _to_sound(arr: np.ndarray) -> pygame.mixer.Sound:
    s16 = (arr * 32767.0).clip(-32768, 32767).astype(np.int16)
    # pygame.mixer may be mono or stereo; duplicate channel if needed
    if pygame.mixer.get_init()[2] == 2:          # stereo
        s16 = np.column_stack([s16, s16])
    return pygame.sndarray.make_sound(s16)

# ---------------------------------------------------------------------------
# Song data  (note, beats)  —  one beat = one quarter note
# ---------------------------------------------------------------------------

# ── TITLE  ·  C major  ·  112 BPM  ·  triumphant fanfare ──────────────────

_TITLE_MEL = [
    # ---- phrase A: bright ascending opening ----
    ('C5',1),  ('E5',1),  ('G5',1),  ('E5',1),
    ('D5',1),  ('F5',1),  ('A5',1),  ('F5',1),
    ('E5',1),  ('G5',1),  ('C6',0.5),('B5',0.5),('A5',1),
    ('G5',2),                         ('E5',2),
    # ---- phrase B: soaring answer ----
    ('A5',1),  ('C6',1),  ('E6',1),  ('C6',1),
    ('B5',1),  ('G5',1),  ('E5',1),  ('D5',1),
    ('C5',0.5),('E5',0.5),('G5',0.5),('C6',0.5),
    ('B5',0.5),('G5',0.5),('E5',0.5),('D5',0.5),
    ('C5',4),
]
_TITLE_HAR = [
    ('E5',1),  ('G5',1),  ('B5',1),  ('G5',1),
    ('F5',1),  ('A5',1),  ('C6',1),  ('A5',1),
    ('G5',1),  ('B5',1),  ('E6',0.5),('D6',0.5),('C6',1),
    ('B5',2),                         ('G5',2),
    ('C6',1),  ('E6',1),  ('G6',1),  ('E6',1),
    ('D6',1),  ('B5',1),  ('G5',1),  ('F5',1),
    ('E5',0.5),('G5',0.5),('B5',0.5),('E6',0.5),
    ('D6',0.5),('B5',0.5),('G5',0.5),('F5',0.5),
    ('E5',4),
]
_TITLE_BASS = [
    ('C3',4), ('D3',4), ('E3',4), ('G3',4),
    ('F3',4), ('C3',4), ('G3',4), ('C3',4),
    ('C3',4),
]

# ── TOWN  ·  G major  ·  90 BPM  ·  warm and welcoming ───────────────────

_TOWN_MEL = [
    # phrase A
    ('G5',1),  ('A5',1),  ('B5',2),
    ('A5',1),  ('G5',1),  ('E5',2),
    ('D5',1),  ('E5',0.5),('F#5',0.5),('G5',2),
    ('A5',3),                           ('REST',1),
    # phrase B
    ('C6',1),  ('B5',1),  ('A5',2),
    ('G5',1),  ('A5',1),  ('B5',2),
    ('D6',1),  ('C6',1),  ('A5',1),    ('G5',1),
    ('G5',4),
]
_TOWN_HAR = [
    ('B5',1),  ('C6',1),  ('D6',2),
    ('C6',1),  ('B5',1),  ('G5',2),
    ('F#5',1), ('G5',0.5),('A5',0.5),  ('B5',2),
    ('C6',3),                           ('REST',1),
    ('E6',1),  ('D6',1),  ('C6',2),
    ('B5',1),  ('C6',1),  ('D6',2),
    ('F#6',1), ('E6',1),  ('C6',1),    ('B5',1),
    ('B5',4),
]
_TOWN_BASS = [
    ('G3',4), ('C4',4), ('D3',4), ('G3',4),
    ('C4',4), ('G3',4), ('A3',4), ('D3',4),
]

# ── ROUTE  ·  D major  ·  130 BPM  ·  adventurous and energetic ──────────

_ROUTE_MEL = [
    # phrase A: ascending arpeggio runs
    ('D5',0.5),('F#5',0.5),('A5',0.5),('D6',0.5),
    ('C#6',0.5),('A5',0.5),('F#5',0.5),('D5',0.5),
    ('E5',0.5),('G5',0.5),('B5',0.5),('E6',0.5),
    ('D6',0.5),('B5',0.5),('G5',0.5),('E5',0.5),
    # phrase B: lyrical melody
    ('F#5',1),('A5',1),('D6',2),
    ('C#6',1),('A5',1),('F#5',1),('D5',1),
    ('G5',1),('B5',1),('D6',1),('G6',1),
    ('A5',2),                   ('D5',2),
    # phrase C: step-wise build
    ('A5',0.5),('G5',0.5),('F#5',0.5),('E5',0.5),
    ('D5',0.5),('E5',0.5),('F#5',0.5),('A5',0.5),
    ('B5',0.5),('C#6',0.5),('D6',0.5),('E6',0.5),
    ('F#6',1),              ('D6',1),   ('A5',2),
    # phrase D: triumphant resolution
    ('G5',1),('F#5',1),('E5',1),('D5',1),
    ('E5',0.5),('F#5',0.5),('G5',0.5),('A5',0.5),('B5',1),('A5',1),
    ('F#5',0.5),('G5',0.5),('A5',0.5),('B5',0.5),('C#6',1),('B5',1),
    ('D5',4),
]
_ROUTE_BASS = [
    ('D3',4), ('A3',4), ('E3',4), ('B3',4),
    ('D3',4), ('A3',4), ('G3',4), ('D3',4),
    ('D3',4), ('A3',4), ('G3',4), ('D3',4),
    ('G3',4), ('D3',4), ('A3',4), ('D3',4),
]

# ── BATTLE  ·  A minor  ·  152 BPM  ·  intense and driving ───────────────

_BATTLE_MEL = [
    # phrase A: aggressive opening
    ('A5',0.5),('C6',0.5),('E6',0.5),('A5',0.5),
    ('G#5',0.5),('B5',0.5),('D6',0.5),('G#5',0.5),
    ('F5',0.5),('A5',0.5),('C6',0.5),('E6',0.5),
    ('E6',1),              ('D6',0.5),('C6',0.5),
    # phrase B: tension spiral
    ('B5',0.5),('C6',0.5),('D6',0.5),('E6',0.5),
    ('F6',0.5),('E6',0.5),('D6',0.5),('C6',0.5),
    ('B5',0.5),('A5',0.5),('G#5',0.5),('A5',0.5),
    ('A5',2),              ('REST',2),
    # phrase C: climax peak
    ('C6',0.5),('E6',0.5),('A6',0.5),('G#6',0.5),
    ('F6',0.5),('E6',0.5),('D6',0.5),('C6',0.5),
    ('B5',0.5),('D6',0.5),('F6',0.5),('E6',0.5),
    ('E6',1),              ('C6',1),   ('A5',2),
    # phrase D: driving descent
    ('G5',0.5),('A5',0.5),('B5',0.5),('C6',0.5),
    ('D6',0.5),('C6',0.5),('B5',0.5),('A5',0.5),
    ('G#5',0.5),('B5',0.5),('D6',0.5),('F6',0.5),
    ('A5',4),
]
_BATTLE_BASS = [
    ('A3',1),('A3',0.5),('E4',0.5),('A3',1),('E4',1),
    ('G#3',1),('G#3',0.5),('D#4',0.5),('G#3',1),('D#4',1),
    ('F3',1),('F3',0.5),('C4',0.5),('F3',1),('C4',1),
    ('E3',4),
    ('A3',1),('C4',1),('A3',1),('C4',1),
    ('G3',1),('G3',1),('G#3',1),('G#3',1),
    ('F3',1),('F3',1),('E3',1),('E3',1),
    ('A3',2),          ('A2',2),
    ('A3',1),('A3',0.5),('C4',0.5),('A3',1),('C4',1),
    ('F3',1),('F3',0.5),('A3',0.5),('F3',1),('A3',1),
    ('G3',1),('G3',0.5),('B3',0.5),('G3',1),('B3',1),
    ('E3',2),          ('C3',2),
    ('G3',1),('A3',1),('G3',1),('A3',1),
    ('D3',1),('D3',1),('F3',1),('F3',1),
    ('E3',1),('G3',1),('B3',1),('E4',1),
    ('A3',4),
]
_BATTLE_DRUMS = [
    # 16-bar kick/snare pattern (each beat listed individually)
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
    ('kick',0.5),('REST',0.5),('snare',0.5),('REST',0.5),
]

# ── GYM  ·  D minor  ·  138 BPM  ·  dramatic and menacing ────────────────

_GYM_MEL = [
    # phrase A: descending motif
    ('D6',0.5),('C6',0.5),('A#5',0.5),('A5',0.5),
    ('G5',0.5),('A5',0.5),('A#5',0.5),('C6',0.5),
    ('D6',1),('A5',1),('D6',0.5),('F6',0.5),('E6',0.5),('D6',0.5),
    ('D6',2),                                  ('REST',2),
    # phrase B: rising tension
    ('F6',0.5),('E6',0.5),('D6',0.5),('C6',0.5),
    ('A#5',0.5),('A5',0.5),('G5',0.5),('F5',0.5),
    ('A5',0.5),('A#5',0.5),('C6',0.5),('D6',0.5),
    ('F6',3),                                  ('REST',1),
    # phrase C: powerful peak
    ('A5',0.5),('A#5',0.5),('C6',0.5),('D6',0.5),
    ('F6',0.5),('E6',0.5),('D6',0.5),('C6',0.5),
    ('A#5',1),('A5',1),('G5',1),('F5',1),
    ('G5',0.5),('A5',0.5),('A#5',0.5),('C6',0.5),('D6',1),('F6',1),
    # phrase D: resolution
    ('E6',0.5),('D6',0.5),('C6',0.5),('A#5',0.5),
    ('A5',0.5),('G5',0.5),('F5',0.5),('D5',0.5),
    ('F5',0.5),('A5',0.5),('C6',0.5),('F6',0.5),
    ('D5',4),
]
_GYM_BASS = [
    ('D3',4), ('D3',4), ('F3',4), ('G3',4),
    ('D3',4), ('C3',4), ('A#2',4),('D3',4),
    ('D3',4), ('D3',4), ('F3',4), ('C3',4),
    ('D3',4), ('A#2',4),('A2',4), ('D3',4),
]

# ---------------------------------------------------------------------------
# Song compilation
# ---------------------------------------------------------------------------
# Each entry: (channels_fn_list, bpm)
# channels_fn_list: list of (seq, render_fn_or_'drums')

_SONGS = {
    'title': (
        [
            (_TITLE_MEL,  lambda f, d: _square(f, d, vol=0.28, duty=0.50)),
            (_TITLE_HAR,  lambda f, d: _square(f, d, vol=0.16, duty=0.25)),
            (_TITLE_BASS, _triangle),
        ],
        112,
    ),
    'town': (
        [
            (_TOWN_MEL,  lambda f, d: _square(f, d, vol=0.28, duty=0.50)),
            (_TOWN_HAR,  lambda f, d: _square(f, d, vol=0.14, duty=0.25)),
            (_TOWN_BASS, _triangle),
        ],
        90,
    ),
    'route': (
        [
            (_ROUTE_MEL,  lambda f, d: _square(f, d, vol=0.26, duty=0.50)),
            (_ROUTE_BASS, _triangle),
        ],
        130,
    ),
    'battle': (
        [
            (_BATTLE_MEL,   lambda f, d: _square(f, d, vol=0.28, duty=0.50)),
            (_BATTLE_BASS,  _triangle),
            (_BATTLE_DRUMS, 'drums'),
        ],
        152,
    ),
    'gym': (
        [
            (_GYM_MEL,  lambda f, d: _square(f, d, vol=0.28, duty=0.50)),
            (_GYM_BASS, _triangle),
        ],
        138,
    ),
}

def _compile_song(channels_spec, bpm):
    rendered = []
    for seq, wave_fn in channels_spec:
        if wave_fn == 'drums':
            rendered.append(_render_drums(seq, bpm))
        else:
            rendered.append(_render_melodic(seq, bpm, wave_fn))
    return _to_sound(_mix(*rendered))

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class MusicPlayer:
    """Manages chiptune background music for RodentMon."""

    # Map name prefixes → track key
    _MAP_MUSIC = {
        'route':   'route',
        'gym':     'gym',
        'interior_gym': 'gym',
    }
    _DEFAULT_OVERWORLD = 'town'

    def __init__(self):
        # Initialise mixer only if not already done by the host game
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=1024)
        pygame.mixer.set_num_channels(max(pygame.mixer.get_num_channels(), 2))

        self._sounds   = {}          # track_name -> pygame.mixer.Sound
        self._channel  = pygame.mixer.Channel(0)
        self._current  = None
        self.volume    = 1.0
        self.enabled   = True

        print("[music] Synthesising chiptune tracks …", flush=True)
        for name, (spec, bpm) in _SONGS.items():
            print(f"[music]   • {name}", flush=True)
            self._sounds[name] = _compile_song(spec, bpm)
        print("[music] Ready.", flush=True)

    # ------------------------------------------------------------------ #
    def play(self, track: str):
        """Start a named track (loops forever).  No-op if already playing."""
        if track == self._current:
            return
        sound = self._sounds.get(track)
        if sound is None:
            return
        self._channel.stop()
        self._channel.play(sound, loops=-1)
        self._current = track

    def stop(self):
        self._channel.stop()
        self._current = None

    def set_volume(self, vol: float):
        """Set music volume (0.0–1.0). Persists across enable/disable."""
        self.volume = max(0.0, min(1.0, vol))
        self._apply_volume()

    def set_enabled(self, enabled: bool):
        """Mute/unmute music without forgetting the current track or volume."""
        self.enabled = enabled
        self._apply_volume()

    def _apply_volume(self):
        self._channel.set_volume(self.volume if self.enabled else 0.0)

    # ------------------------------------------------------------------ #
    def track_for_map(self, map_name: str) -> str:
        """Return the appropriate track key for a given map name."""
        for prefix, track in self._MAP_MUSIC.items():
            if map_name.startswith(prefix):
                return track
        return self._DEFAULT_OVERWORLD

    def play_for_map(self, map_name: str):
        self.play(self.track_for_map(map_name))
