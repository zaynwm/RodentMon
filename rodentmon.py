#!/usr/bin/env python3
"""
RodentMon - A Pokemon-style RPG with rodents!
Catch, train, and battle with mice, rats, gerbils, squirrels, and bats.
"""

import pygame
import random
import math
import sys
import json
import os
import traceback
import datetime

try:
    from music import MusicPlayer
    _MUSIC_AVAILABLE = True
except ImportError:
    _MUSIC_AVAILABLE = False

try:
    from sfx import SoundFX
    _SFX_AVAILABLE = True
except ImportError:
    _SFX_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TILE = 32
SCREEN_W, SCREEN_H = 640, 480
FPS = 60

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 180, 50)
BLUE = (50, 100, 220)
YELLOW = (240, 200, 40)
GREY = (180, 180, 180)
DARK_GREY = (80, 80, 80)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (34, 100, 34)
BROWN = (139, 90, 43)
SAND = (210, 180, 140)
LIGHT_BLUE = (135, 200, 250)
DARK_BLUE = (30, 60, 120)
ORANGE = (240, 160, 50)
PURPLE = (150, 80, 200)
PINK = (240, 150, 180)
ROOF_RED = (180, 40, 40)
WATER_BLUE = (70, 130, 200)
PATH_COLOR = (200, 180, 140)
FLOOR_TAN = (230, 215, 190)
WALL_CREAM = (240, 230, 210)
COUNTER_BROWN = (160, 110, 60)
ARENA_GREEN = (120, 170, 120)
MAT_RED = (160, 60, 60)

# ---------------------------------------------------------------------------
# Rodent species data
# ---------------------------------------------------------------------------
SPECIES = {
    "Mouse": {
        "base_hp": 30, "base_atk": 8, "base_def": 6, "base_spd": 12,
        "type": "Normal", "color": (180, 160, 140),
        "moves_learn": {1: "Nibble", 5: "Quick Dash", 10: "Tail Whip", 15: "Cheese Bomb"},
        "evolves_to": "Rat", "evolve_level": 16,
        "catch_rate": 200,
        "desc": "A tiny mouse. Quick but fragile.",
    },
    "Rat": {
        "base_hp": 55, "base_atk": 14, "base_def": 12, "base_spd": 15,
        "type": "Normal", "color": (120, 100, 80),
        "moves_learn": {1: "Nibble", 5: "Quick Dash", 10: "Tail Whip", 15: "Cheese Bomb",
                        20: "Sewer Surge", 25: "Plague Bite"},
        "evolves_to": None, "evolve_level": None,
        "catch_rate": 90,
        "desc": "A fierce rat. Powerful and fast.",
    },
    "Gerbil": {
        "base_hp": 35, "base_atk": 10, "base_def": 8, "base_spd": 10,
        "type": "Sand", "color": (220, 190, 130),
        "moves_learn": {1: "Sand Kick", 5: "Burrow", 10: "Dust Cloud", 15: "Desert Storm"},
        "evolves_to": "Desert Gerbil", "evolve_level": 18,
        "catch_rate": 170,
        "desc": "A sandy gerbil. Loves to dig.",
    },
    "Desert Gerbil": {
        "base_hp": 60, "base_atk": 18, "base_def": 15, "base_spd": 13,
        "type": "Sand", "color": (190, 150, 80),
        "moves_learn": {1: "Sand Kick", 5: "Burrow", 10: "Dust Cloud", 15: "Desert Storm",
                        22: "Sandstorm Fury", 28: "Earthquake"},
        "evolves_to": None, "evolve_level": None,
        "catch_rate": 60,
        "desc": "A powerful desert dweller.",
    },
    "Squirrel": {
        "base_hp": 40, "base_atk": 9, "base_def": 10, "base_spd": 11,
        "type": "Forest", "color": (160, 100, 50),
        "moves_learn": {1: "Acorn Toss", 5: "Tree Climb", 10: "Nut Barrage", 15: "Forest Shield"},
        "evolves_to": "Giant Squirrel", "evolve_level": 20,
        "catch_rate": 150,
        "desc": "A bushy-tailed acorn hoarder.",
    },
    "Giant Squirrel": {
        "base_hp": 70, "base_atk": 16, "base_def": 18, "base_spd": 12,
        "type": "Forest", "color": (120, 70, 30),
        "moves_learn": {1: "Acorn Toss", 5: "Tree Climb", 10: "Nut Barrage", 15: "Forest Shield",
                        24: "Oak Slam", 30: "Nature Wrath"},
        "evolves_to": None, "evolve_level": None,
        "catch_rate": 50,
        "desc": "A massive squirrel. Tough as oak.",
    },
    "Bat": {
        "base_hp": 32, "base_atk": 11, "base_def": 5, "base_spd": 14,
        "type": "Dark", "color": (80, 60, 100),
        "moves_learn": {1: "Screech", 5: "Wing Slash", 10: "Echo Pulse", 15: "Night Dive"},
        "evolves_to": "Vampire Bat", "evolve_level": 17,
        "catch_rate": 180,
        "desc": "A nocturnal flyer with sonar.",
    },
    "Vampire Bat": {
        "base_hp": 58, "base_atk": 20, "base_def": 10, "base_spd": 18,
        "type": "Dark", "color": (50, 30, 70),
        "moves_learn": {1: "Screech", 5: "Wing Slash", 10: "Echo Pulse", 15: "Night Dive",
                        21: "Blood Drain", 26: "Shadow Storm"},
        "evolves_to": None, "evolve_level": None,
        "catch_rate": 45,
        "desc": "A terrifying predator of the night.",
    },
}

# Moves database
MOVES = {
    "Nibble":        {"power": 15, "type": "Normal", "acc": 100, "desc": "A small bite."},
    "Quick Dash":    {"power": 20, "type": "Normal", "acc": 95,  "desc": "A speedy charge."},
    "Tail Whip":     {"power": 0,  "type": "Normal", "acc": 100, "desc": "Lowers defense.", "effect": "def_down"},
    "Cheese Bomb":   {"power": 35, "type": "Normal", "acc": 90,  "desc": "Exploding cheese!"},
    "Sewer Surge":   {"power": 45, "type": "Normal", "acc": 85,  "desc": "A filthy tidal wave."},
    "Plague Bite":   {"power": 55, "type": "Dark",   "acc": 80,  "desc": "A toxic bite.", "effect": "poison"},
    "Sand Kick":     {"power": 15, "type": "Sand",   "acc": 100, "desc": "Kicks sand at foe."},
    "Burrow":        {"power": 25, "type": "Sand",   "acc": 95,  "desc": "Digs underground to attack."},
    "Dust Cloud":    {"power": 0,  "type": "Sand",   "acc": 90,  "desc": "Lowers accuracy.", "effect": "acc_down"},
    "Desert Storm":  {"power": 40, "type": "Sand",   "acc": 85,  "desc": "A blinding sandstorm."},
    "Sandstorm Fury":{"power": 55, "type": "Sand",   "acc": 80,  "desc": "Raging sands."},
    "Earthquake":    {"power": 65, "type": "Sand",   "acc": 75,  "desc": "The ground splits!"},
    "Acorn Toss":    {"power": 18, "type": "Forest", "acc": 100, "desc": "Throws an acorn."},
    "Tree Climb":    {"power": 22, "type": "Forest", "acc": 95,  "desc": "Drops from a tree."},
    "Nut Barrage":   {"power": 35, "type": "Forest", "acc": 90,  "desc": "A hail of nuts."},
    "Forest Shield": {"power": 0,  "type": "Forest", "acc": 100, "desc": "Raises defense.", "effect": "def_up"},
    "Oak Slam":      {"power": 50, "type": "Forest", "acc": 85,  "desc": "Slams with oak branch."},
    "Nature Wrath":  {"power": 65, "type": "Forest", "acc": 75,  "desc": "Nature's fury unleashed."},
    "Screech":       {"power": 0,  "type": "Dark",   "acc": 95,  "desc": "Lowers attack.", "effect": "atk_down"},
    "Wing Slash":    {"power": 20, "type": "Dark",   "acc": 100, "desc": "Slashes with wings."},
    "Echo Pulse":    {"power": 30, "type": "Dark",   "acc": 90,  "desc": "Sonic pulse attack."},
    "Night Dive":    {"power": 40, "type": "Dark",   "acc": 85,  "desc": "Dives from darkness."},
    "Blood Drain":   {"power": 45, "type": "Dark",   "acc": 85,  "desc": "Drains HP.", "effect": "drain"},
    "Shadow Storm":  {"power": 60, "type": "Dark",   "acc": 78,  "desc": "A storm of shadows."},
}

# Type effectiveness: attacker_type -> {defender_type: multiplier}
TYPE_CHART = {
    "Normal": {"Normal": 1.0, "Sand": 1.0, "Forest": 1.0, "Dark": 0.5},
    "Sand":   {"Normal": 1.0, "Sand": 0.5, "Forest": 0.5, "Dark": 2.0},
    "Forest": {"Normal": 1.0, "Sand": 2.0, "Forest": 0.5, "Dark": 1.0},
    "Dark":   {"Normal": 2.0, "Sand": 0.5, "Forest": 1.0, "Dark": 0.5},
}

TYPE_COLORS = {
    "Normal": (180, 180, 160),
    "Sand":   (210, 180, 100),
    "Forest": (80, 160, 80),
    "Dark":   (100, 60, 140),
}

# Wild encounter tables per area
ENCOUNTER_TABLES = {
    "route1": [("Mouse", 3, 6, 50), ("Squirrel", 3, 5, 30), ("Bat", 3, 5, 20)],
    "route2": [("Mouse", 6, 10, 30), ("Gerbil", 5, 8, 35), ("Bat", 5, 8, 35)],
    "route3": [("Rat", 10, 15, 25), ("Squirrel", 8, 13, 25), ("Gerbil", 8, 12, 25),
               ("Bat", 10, 14, 25)],
    "route4": [("Rat", 14, 20, 20), ("Desert Gerbil", 18, 22, 15),
               ("Giant Squirrel", 20, 24, 15), ("Vampire Bat", 17, 22, 15),
               ("Mouse", 12, 16, 35)],
}

# ---------------------------------------------------------------------------
# Rodent class
# ---------------------------------------------------------------------------
class Rodent:
    def __init__(self, species_name, level, nickname=None):
        self.species = species_name
        self.nickname = nickname or species_name
        self.level = level
        data = SPECIES[species_name]
        self.type = data["type"]
        self.color = data["color"]

        # Stats
        self.max_hp = data["base_hp"] + level * 2
        self.hp = self.max_hp
        self.atk = data["base_atk"] + level
        self.defense = data["base_def"] + level
        self.spd = data["base_spd"] + level
        self.base_atk = data["base_atk"]
        self.base_def = data["base_def"]
        self.base_spd = data["base_spd"]

        # Stat modifiers (battle only)
        self.atk_mod = 0
        self.def_mod = 0
        self.acc_mod = 0

        # Status
        self.poisoned = False

        # Moves (up to 4)
        self.moves = []
        for req_level, move_name in sorted(data["moves_learn"].items()):
            if req_level <= level:
                if len(self.moves) < 4:
                    self.moves.append(move_name)
                else:
                    self.moves[random.randint(0, 3)] = move_name

        # XP
        self.xp = 0
        self.xp_to_next = self._xp_needed()

    def _xp_needed(self):
        return int(self.level ** 2.5 * 4)

    def gain_xp(self, amount):
        """Returns list of messages (level ups, new moves, evolutions)."""
        self.xp += amount
        messages = []
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            data = SPECIES[self.species]
            self.max_hp = data["base_hp"] + self.level * 2
            self.hp = min(self.hp + 4, self.max_hp)
            self.atk = data["base_atk"] + self.level
            self.defense = data["base_def"] + self.level
            self.spd = data["base_spd"] + self.level
            self.xp_to_next = self._xp_needed()
            messages.append(f"{self.nickname} grew to level {self.level}!")

            # New move?
            if self.level in data["moves_learn"]:
                new_move = data["moves_learn"][self.level]
                if len(self.moves) < 4:
                    self.moves.append(new_move)
                    messages.append(f"{self.nickname} learned {new_move}!")
                else:
                    old = self.moves[0]
                    self.moves[0] = new_move
                    messages.append(f"{self.nickname} learned {new_move} (forgot {old})!")

            # Evolution?
            if data["evolves_to"] and data["evolve_level"] and self.level >= data["evolve_level"]:
                old_name = self.species
                self.species = data["evolves_to"]
                data = SPECIES[self.species]
                self.type = data["type"]
                self.color = data["color"]
                self.max_hp = data["base_hp"] + self.level * 2
                self.hp = self.max_hp
                self.atk = data["base_atk"] + self.level
                self.defense = data["base_def"] + self.level
                self.spd = data["base_spd"] + self.level
                if self.nickname == old_name:
                    self.nickname = self.species
                messages.append(f"{old_name} evolved into {self.species}!")
        return messages

    def reset_battle_mods(self):
        self.atk_mod = 0
        self.def_mod = 0
        self.acc_mod = 0

    def effective_atk(self):
        return max(1, self.atk + self.atk_mod * 3)

    def effective_def(self):
        return max(1, self.defense + self.def_mod * 3)

    def to_dict(self):
        return {
            "species": self.species, "nickname": self.nickname,
            "level": self.level, "hp": self.hp, "xp": self.xp,
            "moves": self.moves, "poisoned": self.poisoned,
        }

    @classmethod
    def from_dict(cls, d):
        r = cls(d["species"], d["level"], d.get("nickname"))
        r.hp = d["hp"]
        r.xp = d.get("xp", 0)
        r.moves = d["moves"]
        r.poisoned = d.get("poisoned", False)
        return r


# ---------------------------------------------------------------------------
# Map data - tile-based maps
# ---------------------------------------------------------------------------
# Legend:
# . = grass (encounters), # = wall/tree, ~ = water, P = path,
# D = door, H = house, R = roof, C = center (heal), S = sign,
# T = trainer NPC, X = blocked, E = exit/entrance
# Maps connect via labeled exits

def make_hometown():
    """Starting town - Rodent Village."""
    w, h = 30, 25
    tiles = [['.' for _ in range(w)] for _ in range(h)]
    # Surround with trees
    for x in range(w):
        tiles[0][x] = '#'
        tiles[h-1][x] = '#'
    for y in range(h):
        tiles[y][0] = '#'
        tiles[y][w-1] = '#'

    # Paths
    for x in range(5, 25):
        tiles[12][x] = 'P'
        tiles[13][x] = 'P'
    for y in range(3, 22):
        tiles[y][14] = 'P'
        tiles[y][15] = 'P'

    # Player house (top-left area)
    for x in range(5, 10):
        tiles[4][x] = 'R'
        tiles[5][x] = 'H'
        tiles[6][x] = 'H'
    tiles[6][7] = 'D'

    # Rodent Lab (top-right area)
    for x in range(18, 25):
        tiles[4][x] = 'R'
        tiles[5][x] = 'H'
        tiles[6][x] = 'H'
        tiles[7][x] = 'H'
    tiles[7][21] = 'D'

    # Heal Center (bottom area)
    for x in range(10, 16):
        tiles[17][x] = 'R'
        tiles[18][x] = 'H'
        tiles[19][x] = 'H'
    tiles[19][12] = 'D'
    tiles[19][13] = 'D'

    # Signs
    tiles[11][7] = 'S'
    tiles[11][21] = 'S'

    # Exit north to route1
    tiles[0][14] = 'P'
    tiles[0][15] = 'P'

    # Some decorative water
    for x in range(2, 5):
        for y in range(17, 20):
            tiles[y][x] = '~'

    return {
        "name": "Rodent Village",
        "tiles": tiles, "w": w, "h": h,
        "encounters": None,
        "exits": [
            {"x": 14, "y": 0, "dest": "route1", "dx": 14, "dy": 23},
            {"x": 15, "y": 0, "dest": "route1", "dx": 15, "dy": 23},
        ],
        "signs": {
            (7, 11): "Welcome to Rodent Village!\nYour adventure begins here.",
            (21, 11): "Prof. Whiskers' Lab ->\nGet your first rodent!",
        },
        "doors": {
            (7, 6): {"action": "enter", "dest": "interior_house", "dx": 4, "dy": 6},
            (21, 7): {"action": "enter", "dest": "interior_lab", "dx": 5, "dy": 8},
            (12, 19): {"action": "enter", "dest": "interior_center_hometown", "dx": 5, "dy": 6},
            (13, 19): {"action": "enter", "dest": "interior_center_hometown", "dx": 5, "dy": 6},
        },
        "spawn": (14, 13),
    }

def make_route(num, w, h, enc_table, dest_south, dest_north, trainers=None):
    tiles = [['.' for _ in range(w)] for _ in range(h)]
    # Trees on edges
    for x in range(w):
        tiles[0][x] = '#'
        tiles[h-1][x] = '#'
    for y in range(h):
        tiles[y][0] = '#'
        tiles[y][w-1] = '#'

    # Path through middle
    for y in range(h):
        tiles[y][14] = 'P'
        tiles[y][15] = 'P'

    # Some random trees for variety
    random.seed(num * 42)
    for _ in range(w * h // 8):
        rx, ry = random.randint(2, w-3), random.randint(2, h-3)
        if tiles[ry][rx] == '.' and (rx, ry) not in [(14, 0), (15, 0), (14, h-1), (15, h-1)]:
            tiles[ry][rx] = '#'

    # Water features on some routes
    if num == 2:
        for x in range(3, 8):
            for y in range(8, 12):
                if tiles[y][x] == '.':
                    tiles[y][x] = '~'

    # Openings
    tiles[0][14] = 'P'
    tiles[0][15] = 'P'
    tiles[h-1][14] = 'P'
    tiles[h-1][15] = 'P'

    exits = [
        {"x": 14, "y": h-1, "dest": dest_south, "dx": 14, "dy": 1},
        {"x": 15, "y": h-1, "dest": dest_south, "dx": 15, "dy": 1},
    ]
    if dest_north:
        exits.extend([
            {"x": 14, "y": 0, "dest": dest_north, "dx": 14, "dy": 23},
            {"x": 15, "y": 0, "dest": dest_north, "dx": 15, "dy": 23},
        ])

    trainer_list = []
    if trainers:
        for t in trainers:
            tx, ty = t["pos"]
            tiles[ty][tx] = 'T'
            trainer_list.append(t)

    sign_text = f"Route {num}"
    tiles[h-2][12] = 'S'

    return {
        "name": f"Route {num}",
        "tiles": tiles, "w": w, "h": h,
        "encounters": enc_table,
        "exits": exits,
        "signs": {(12, h-2): sign_text},
        "doors": {},
        "trainers": trainer_list,
        "spawn": (14, h-2),
    }


def make_town2():
    """Second town - Burrow Town."""
    w, h = 30, 25
    tiles = [['.' for _ in range(w)] for _ in range(h)]
    for x in range(w):
        tiles[0][x] = '#'
        tiles[h-1][x] = '#'
    for y in range(h):
        tiles[y][0] = '#'
        tiles[y][w-1] = '#'

    for x in range(5, 25):
        tiles[12][x] = 'P'
        tiles[13][x] = 'P'
    for y in range(3, 22):
        tiles[y][14] = 'P'
        tiles[y][15] = 'P'

    # Heal center
    for x in range(6, 12):
        tiles[9][x] = 'R'
        tiles[10][x] = 'H'
        tiles[11][x] = 'H'
    tiles[11][8] = 'D'
    tiles[11][9] = 'D'

    # Gym
    for x in range(18, 26):
        tiles[7][x] = 'R'
        tiles[8][x] = 'H'
        tiles[9][x] = 'H'
        tiles[10][x] = 'H'
        tiles[11][x] = 'H'
    tiles[11][21] = 'D'

    tiles[0][14] = 'P'
    tiles[0][15] = 'P'
    tiles[h-1][14] = 'P'
    tiles[h-1][15] = 'P'

    tiles[13][5] = 'S'
    tiles[13][22] = 'S'

    return {
        "name": "Burrow Town",
        "tiles": tiles, "w": w, "h": h,
        "encounters": None,
        "exits": [
            {"x": 14, "y": h-1, "dest": "route1", "dx": 14, "dy": 1},
            {"x": 15, "y": h-1, "dest": "route1", "dx": 15, "dy": 1},
            {"x": 14, "y": 0, "dest": "route2", "dx": 14, "dy": 23},
            {"x": 15, "y": 0, "dest": "route2", "dx": 15, "dy": 23},
        ],
        "signs": {
            (5, 13): "Burrow Town\nHome of the first Gym!",
            (22, 13): "Burrow Town Gym\nLeader: Sandy",
        },
        "doors": {
            (8, 11): {"action": "enter", "dest": "interior_center_town2", "dx": 5, "dy": 6},
            (9, 11): {"action": "enter", "dest": "interior_center_town2", "dx": 5, "dy": 6},
            (21, 11): {"action": "enter", "dest": "interior_gym1", "dx": 5, "dy": 8},
        },
        "spawn": (14, 13),
    }


def make_town3():
    """Third town - Nest City."""
    w, h = 30, 25
    tiles = [['.' for _ in range(w)] for _ in range(h)]
    for x in range(w):
        tiles[0][x] = '#'
        tiles[h-1][x] = '#'
    for y in range(h):
        tiles[y][0] = '#'
        tiles[y][w-1] = '#'

    for x in range(5, 25):
        tiles[12][x] = 'P'
        tiles[13][x] = 'P'
    for y in range(3, 22):
        tiles[y][14] = 'P'
        tiles[y][15] = 'P'

    # Heal center
    for x in range(6, 12):
        tiles[9][x] = 'R'
        tiles[10][x] = 'H'
        tiles[11][x] = 'H'
    tiles[11][8] = 'D'

    # Gym 2
    for x in range(18, 26):
        tiles[7][x] = 'R'
        tiles[8][x] = 'H'
        tiles[9][x] = 'H'
        tiles[10][x] = 'H'
        tiles[11][x] = 'H'
    tiles[11][21] = 'D'

    tiles[0][14] = 'P'
    tiles[0][15] = 'P'
    tiles[h-1][14] = 'P'
    tiles[h-1][15] = 'P'
    tiles[13][5] = 'S'

    return {
        "name": "Nest City",
        "tiles": tiles, "w": w, "h": h,
        "encounters": None,
        "exits": [
            {"x": 14, "y": h-1, "dest": "route3", "dx": 14, "dy": 1},
            {"x": 15, "y": h-1, "dest": "route3", "dx": 15, "dy": 1},
            {"x": 14, "y": 0, "dest": "route4", "dx": 14, "dy": 23},
            {"x": 15, "y": 0, "dest": "route4", "dx": 15, "dy": 23},
        ],
        "signs": {
            (5, 13): "Nest City\nThe final challenge awaits!",
        },
        "doors": {
            (8, 11): {"action": "enter", "dest": "interior_center_town3", "dx": 5, "dy": 6},
            (21, 11): {"action": "enter", "dest": "interior_gym2", "dx": 5, "dy": 8},
        },
        "spawn": (14, 13),
    }


# ---------------------------------------------------------------------------
# Interior map builders
# ---------------------------------------------------------------------------
def make_interior_house():
    """Player's house interior."""
    layout = [
        "WWWWWWWWWW",
        "WFFBFFBFFW",
        "WFFFFFFKFW",
        "WFNFFFFKFW",
        "WFFFFFFFFW",
        "WFFFFFFFFW",
        "WFFFFFFFFW",
        "WWWWGWWWWW",
    ]
    h = len(layout)
    w = len(layout[0])
    tiles = [[c for c in row] for row in layout]
    return {
        "name": "Your House",
        "tiles": tiles, "w": w, "h": h,
        "encounters": None,
        "exits": [{"x": 4, "y": 7, "dest": "hometown", "dx": 7, "dy": 7}],
        "signs": {},
        "doors": {},
        "npcs": [
            {"name": "Mom", "pos": (2, 3), "color": PINK,
             "msg": "Be careful out there, dear!\nI'll always be here for you."},
        ],
        "spawn": (4, 6),
        "is_interior": True,
    }


def make_interior_lab():
    """Prof. Whiskers' Lab interior."""
    layout = [
        "WWWWWWWWWWWW",
        "WFFLLLLLLWFW",
        "WFFLLLLLLWFW",
        "WFFFFFFFFFFW",
        "WNFFFFFFFFFW",
        "WFFFFFFFFFFW",
        "WFFLFFFLFBFW",
        "WFFLFFFLFBFW",
        "WFFFFFFFFFFW",
        "WWWWWGWWWWWW",
    ]
    h = len(layout)
    w = len(layout[0])
    tiles = [[c for c in row] for row in layout]
    return {
        "name": "Rodent Lab",
        "tiles": tiles, "w": w, "h": h,
        "encounters": None,
        "exits": [{"x": 5, "y": 9, "dest": "hometown", "dx": 21, "dy": 8}],
        "signs": {},
        "doors": {},
        "npcs": [
            {"name": "Prof. Whiskers", "pos": (1, 4), "color": WHITE,
             "action": "lab",
             "msg": "Prof. Whiskers: Take good\ncare of your rodents!"},
        ],
        "spawn": (5, 8),
        "is_interior": True,
    }


def make_interior_center(return_map, return_dx, return_dy):
    """Rodent Center interior."""
    layout = [
        "WWWWWWWWWWWW",
        "WFKKKKKKFFFW",
        "WFNFFFFFKFFW",
        "WFFFFFFFKFFW",
        "WFFFFFFFFFFW",
        "WFFFFFFFFFFW",
        "WFFFFFFFFFFW",
        "WWWWWGWWWWWW",
    ]
    h = len(layout)
    w = len(layout[0])
    tiles = [[c for c in row] for row in layout]
    return {
        "name": "Rodent Center",
        "tiles": tiles, "w": w, "h": h,
        "encounters": None,
        "exits": [{"x": 5, "y": 7, "dest": return_map, "dx": return_dx, "dy": return_dy}],
        "signs": {},
        "doors": {},
        "npcs": [
            {"name": "Nurse Joy", "pos": (2, 2), "color": PINK,
             "action": "heal",
             "msg": "Welcome to the Rodent Center!\nYour rodents have been healed!"},
        ],
        "spawn": (5, 6),
        "is_interior": True,
    }


def make_interior_gym(gym_id, return_map, return_dx, return_dy):
    """Gym interior."""
    gym = GYM_DATA[gym_id]
    leader_color = SAND if gym_id == 1 else PURPLE
    layout = [
        "WWWWWWWWWWWW",
        "WFFFFFFFFFFW",
        "WFFAAAAAAFFW",
        "WFFAAAAAAFFW",
        "WFFAANAAAFFW",
        "WFFAAAAAAFFW",
        "WFFAAAAAAFFW",
        "WFFFFFFFFFFW",
        "WFFFFFFFFFFW",
        "WWWWWGWWWWWW",
    ]
    h = len(layout)
    w = len(layout[0])
    tiles = [[c for c in row] for row in layout]
    return {
        "name": f"{gym['leader']}'s Gym",
        "tiles": tiles, "w": w, "h": h,
        "encounters": None,
        "exits": [{"x": 5, "y": 9, "dest": return_map, "dx": return_dx, "dy": return_dy}],
        "signs": {},
        "doors": {},
        "npcs": [
            {"name": gym["leader"], "pos": (5, 4), "color": leader_color,
             "action": "gym", "gym_id": gym_id,
             "msg": f"{gym['leader']}: Come back\nwhen you're ready!"},
        ],
        "spawn": (5, 8),
        "is_interior": True,
    }


# Trainer definitions
TRAINER_DATA = {
    "route1": [
        {"name": "Youngster Joey", "pos": (17, 12), "party": [("Mouse", 5)],
         "msg_before": "My Mouse is in\nthe top percentage!", "msg_after": "Wow, you're strong!",
         "reward": 100},
        {"name": "Lass Amy", "pos": (12, 7), "party": [("Squirrel", 4), ("Bat", 4)],
         "msg_before": "Let's battle!", "msg_after": "Good match!",
         "reward": 120},
    ],
    "route2": [
        {"name": "Bug Catcher Dan", "pos": (17, 10), "party": [("Bat", 8), ("Bat", 9)],
         "msg_before": "Bats are basically\nbig bugs, right?", "msg_after": "I need more bats...",
         "reward": 200},
        {"name": "Hiker Mike", "pos": (12, 5), "party": [("Gerbil", 10), ("Mouse", 8)],
         "msg_before": "The mountains are\nfull of gerbils!", "msg_after": "You climb well!",
         "reward": 250},
    ],
    "route3": [
        {"name": "Ace Trainer Zoe", "pos": (17, 8),
         "party": [("Squirrel", 14), ("Gerbil", 13), ("Bat", 14)],
         "msg_before": "I've trained hard\nfor this!", "msg_after": "Incredible skill!",
         "reward": 500},
    ],
    "route4": [
        {"name": "Veteran Rex", "pos": (12, 10),
         "party": [("Rat", 18), ("Desert Gerbil", 19)],
         "msg_before": "Only the best\npass through here!", "msg_after": "You ARE the best!",
         "reward": 800},
    ],
}

GYM_DATA = {
    1: {
        "leader": "Sandy",
        "title": "Sand Gym Leader",
        "party": [("Gerbil", 14), ("Desert Gerbil", 16)],
        "msg_before": "I am Sandy, master of\nthe desert rodents!\nPrepare for a sandstorm!",
        "msg_after": "The sands have spoken...\nYou've earned the\nDust Badge!",
        "badge": "Dust Badge",
        "reward": 1000,
    },
    2: {
        "leader": "Shade",
        "title": "Dark Gym Leader",
        "party": [("Bat", 22), ("Vampire Bat", 25), ("Rat", 23)],
        "msg_before": "Welcome to the shadows.\nI am Shade.\nFew survive my onslaught!",
        "msg_after": "You've pierced the\ndarkness! Take the\nShadow Badge!",
        "badge": "Shadow Badge",
        "reward": 2000,
    },
}


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def draw_rodent_sprite(surface, species_name, x, y, size=64, flip=False):
    """Draw a simple pixel-art rodent."""
    data = SPECIES[species_name]
    color = data["color"]
    lighter = tuple(min(255, c + 40) for c in color)
    darker = tuple(max(0, c - 40) for c in color)
    s = size

    if "Bat" in species_name or species_name == "Vampire Bat":
        # Bat shape: wings spread
        body_rect = pygame.Rect(x + s//3, y + s//4, s//3, s//3)
        pygame.draw.ellipse(surface, color, body_rect)
        # Wings
        wing_pts_l = [(x + s//3, y + s//3), (x + 2, y + s//6), (x + 4, y + s//2)]
        wing_pts_r = [(x + 2*s//3, y + s//3), (x + s - 2, y + s//6), (x + s - 4, y + s//2)]
        if flip:
            wing_pts_l, wing_pts_r = wing_pts_r, wing_pts_l
        pygame.draw.polygon(surface, darker, wing_pts_l)
        pygame.draw.polygon(surface, darker, wing_pts_r)
        # Eyes
        eye_y = y + s//3
        pygame.draw.circle(surface, RED if "Vampire" in species_name else WHITE,
                          (x + s//2 - 4, eye_y), 3)
        pygame.draw.circle(surface, RED if "Vampire" in species_name else WHITE,
                          (x + s//2 + 4, eye_y), 3)
        pygame.draw.circle(surface, BLACK, (x + s//2 - 4, eye_y), 1)
        pygame.draw.circle(surface, BLACK, (x + s//2 + 4, eye_y), 1)
        # Ears
        pygame.draw.polygon(surface, color,
                          [(x + s//2 - 6, y + s//4), (x + s//2 - 10, y + s//8), (x + s//2 - 2, y + s//4)])
        pygame.draw.polygon(surface, color,
                          [(x + s//2 + 6, y + s//4), (x + s//2 + 10, y + s//8), (x + s//2 + 2, y + s//4)])
    elif "Squirrel" in species_name:
        # Squirrel: round body, big tail
        body_rect = pygame.Rect(x + s//4, y + s//4, s//2, s//2)
        pygame.draw.ellipse(surface, color, body_rect)
        # Big bushy tail
        tail_x = x + 3*s//4 if not flip else x + s//8
        pygame.draw.ellipse(surface, lighter, (tail_x - s//6, y + s//8, s//3, s//2))
        pygame.draw.ellipse(surface, color, (tail_x - s//8, y + s//6, s//4, s//3))
        # Head
        pygame.draw.circle(surface, color, (x + s//2, y + s//4), s//6)
        # Eyes
        pygame.draw.circle(surface, BLACK, (x + s//2 - 3, y + s//4 - 2), 2)
        pygame.draw.circle(surface, BLACK, (x + s//2 + 3, y + s//4 - 2), 2)
        # Ears
        pygame.draw.circle(surface, lighter, (x + s//2 - 6, y + s//6), 4)
        pygame.draw.circle(surface, lighter, (x + s//2 + 6, y + s//6), 4)
        # Feet
        pygame.draw.ellipse(surface, darker, (x + s//3, y + 3*s//4 - 2, 8, 5))
        pygame.draw.ellipse(surface, darker, (x + s//2, y + 3*s//4 - 2, 8, 5))
    elif "Gerbil" in species_name:
        # Gerbil: elongated body
        body_rect = pygame.Rect(x + s//5, y + s//3, 3*s//5, s//3)
        pygame.draw.ellipse(surface, color, body_rect)
        # Head
        head_x = x + s//4 if not flip else x + 3*s//5
        pygame.draw.circle(surface, color, (head_x, y + s//3), s//5)
        # Big eyes
        pygame.draw.circle(surface, BLACK, (head_x - 3, y + s//3 - 2), 3)
        pygame.draw.circle(surface, BLACK, (head_x + 3, y + s//3 - 2), 3)
        pygame.draw.circle(surface, WHITE, (head_x - 3, y + s//3 - 3), 1)
        pygame.draw.circle(surface, WHITE, (head_x + 3, y + s//3 - 3), 1)
        # Big ears
        pygame.draw.ellipse(surface, lighter, (head_x - 8, y + s//5 - 4, 8, 12))
        pygame.draw.ellipse(surface, lighter, (head_x + 2, y + s//5 - 4, 8, 12))
        # Long tail
        tail_x = x + 3*s//4 if not flip else x + s//6
        pygame.draw.line(surface, darker, (x + s//2, y + s//2), (tail_x, y + 2*s//3), 2)
        # Feet
        pygame.draw.ellipse(surface, darker, (x + s//3, y + 2*s//3 - 2, 6, 4))
        pygame.draw.ellipse(surface, darker, (x + s//2, y + 2*s//3 - 2, 6, 4))
    else:
        # Mouse / Rat: classic rodent
        body_w = s//2 if "Rat" not in species_name else 3*s//5
        body_rect = pygame.Rect(x + (s - body_w)//2, y + s//3, body_w, s//3)
        pygame.draw.ellipse(surface, color, body_rect)
        # Head
        head_r = s//5 if "Rat" not in species_name else s//4
        pygame.draw.circle(surface, color, (x + s//2, y + s//3), head_r)
        # Ears
        ear_size = 6 if "Rat" not in species_name else 8
        pygame.draw.circle(surface, PINK if "Rat" not in species_name else darker,
                          (x + s//2 - head_r + 2, y + s//4 - 4), ear_size)
        pygame.draw.circle(surface, PINK if "Rat" not in species_name else darker,
                          (x + s//2 + head_r - 2, y + s//4 - 4), ear_size)
        # Eyes
        pygame.draw.circle(surface, BLACK, (x + s//2 - 4, y + s//3 - 2), 2)
        pygame.draw.circle(surface, BLACK, (x + s//2 + 4, y + s//3 - 2), 2)
        # Nose
        pygame.draw.circle(surface, PINK, (x + s//2, y + s//3 + 3), 2)
        # Whiskers
        for dy in [-1, 0, 1]:
            pygame.draw.line(surface, GREY, (x + s//2 - 4, y + s//3 + 3 + dy*2),
                           (x + s//2 - 14, y + s//3 + dy*4), 1)
            pygame.draw.line(surface, GREY, (x + s//2 + 4, y + s//3 + 3 + dy*2),
                           (x + s//2 + 14, y + s//3 + dy*4), 1)
        # Tail
        tail_start = (x + s//2 + body_w//2, y + s//2)
        tail_end = (x + s - 4, y + 2*s//3)
        pygame.draw.line(surface, PINK, tail_start, tail_end, 2)
        # Feet
        pygame.draw.ellipse(surface, darker, (x + s//3, y + 2*s//3, 7, 4))
        pygame.draw.ellipse(surface, darker, (x + s//2, y + 2*s//3, 7, 4))


def draw_tile(surface, tile, x, y):
    """Draw a single map tile."""
    rect = pygame.Rect(x, y, TILE, TILE)
    if tile == '#':
        pygame.draw.rect(surface, DARK_GREEN, rect)
        # Tree details
        pygame.draw.circle(surface, (30, 120, 30), (x + TILE//2, y + TILE//3), TILE//3)
        pygame.draw.rect(surface, BROWN, (x + TILE//2 - 2, y + TILE//2, 4, TILE//2))
    elif tile == '~':
        pygame.draw.rect(surface, WATER_BLUE, rect)
        # Wave details
        for wx in range(x + 4, x + TILE - 4, 8):
            pygame.draw.arc(surface, (100, 160, 230), (wx, y + TILE//3, 8, 6), 0, 3.14, 1)
    elif tile == 'P':
        pygame.draw.rect(surface, PATH_COLOR, rect)
        pygame.draw.rect(surface, (190, 170, 130), rect, 1)
    elif tile == 'H':
        pygame.draw.rect(surface, (220, 200, 170), rect)
        pygame.draw.rect(surface, BROWN, rect, 1)
    elif tile == 'R':
        pygame.draw.rect(surface, ROOF_RED, rect)
        pygame.draw.line(surface, (150, 30, 30), (x, y + TILE), (x + TILE//2, y), 1)
        pygame.draw.line(surface, (150, 30, 30), (x + TILE, y + TILE), (x + TILE//2, y), 1)
    elif tile == 'D':
        pygame.draw.rect(surface, (220, 200, 170), rect)
        pygame.draw.rect(surface, BROWN, (x + 4, y + 2, TILE - 8, TILE - 2))
        pygame.draw.circle(surface, YELLOW, (x + TILE - 8, y + TILE//2), 2)
    elif tile == 'S':
        pygame.draw.rect(surface, LIGHT_GREEN, rect)
        pygame.draw.rect(surface, BROWN, (x + TILE//2 - 3, y + 4, 6, TILE - 4))
        pygame.draw.rect(surface, (200, 180, 140), (x + 4, y + 2, TILE - 8, TILE//2))
    elif tile == 'T':
        pygame.draw.rect(surface, LIGHT_GREEN, rect)
    elif tile == 'C':
        pygame.draw.rect(surface, WHITE, rect)
        pygame.draw.rect(surface, RED, (x + 8, y + 4, TILE - 16, TILE - 8), 0)
    elif tile == 'F' or tile == 'N':
        # Interior floor (N = NPC standing spot, drawn as floor)
        pygame.draw.rect(surface, FLOOR_TAN, rect)
        # Subtle checkerboard
        half = TILE // 2
        pygame.draw.rect(surface, (225, 210, 185), (x, y, half, half))
        pygame.draw.rect(surface, (225, 210, 185), (x + half, y + half, half, half))
    elif tile == 'W':
        # Interior wall
        pygame.draw.rect(surface, WALL_CREAM, rect)
        pygame.draw.line(surface, (210, 200, 180), (x, y + TILE - 1), (x + TILE, y + TILE - 1), 2)
        pygame.draw.line(surface, (220, 210, 195), (x, y + TILE // 2), (x + TILE, y + TILE // 2), 1)
    elif tile == 'K':
        # Counter / desk
        pygame.draw.rect(surface, FLOOR_TAN, rect)
        pygame.draw.rect(surface, COUNTER_BROWN, (x + 1, y + 1, TILE - 2, TILE - 2))
        pygame.draw.rect(surface, (140, 90, 40), (x + 1, y + 1, TILE - 2, 4))
    elif tile == 'B':
        # Bookshelf
        pygame.draw.rect(surface, BROWN, rect)
        for by in range(y + 2, y + TILE - 2, 8):
            pygame.draw.rect(surface, RED, (x + 3, by, 6, 6))
            pygame.draw.rect(surface, BLUE, (x + 11, by, 5, 6))
            pygame.draw.rect(surface, GREEN, (x + 18, by, 6, 6))
            pygame.draw.rect(surface, YELLOW, (x + 25, by, 4, 6))
    elif tile == 'L':
        # Lab table
        pygame.draw.rect(surface, FLOOR_TAN, rect)
        pygame.draw.rect(surface, (180, 190, 200), (x + 2, y + 2, TILE - 4, TILE - 4))
        pygame.draw.rect(surface, (160, 170, 180), (x + 2, y + 2, TILE - 4, TILE - 4), 1)
        # Beaker
        pygame.draw.rect(surface, (200, 220, 240), (x + 10, y + 8, 6, 10))
        pygame.draw.circle(surface, (180, 240, 200), (x + 20, y + 14), 4)
    elif tile == 'A':
        # Arena floor
        pygame.draw.rect(surface, ARENA_GREEN, rect)
        pygame.draw.rect(surface, (100, 150, 100), rect, 1)
    elif tile == 'G':
        # Entrance mat
        pygame.draw.rect(surface, MAT_RED, rect)
        pygame.draw.rect(surface, (140, 50, 50), rect, 1)
    else:  # '.' grass
        pygame.draw.rect(surface, LIGHT_GREEN, rect)
        # Grass blades
        for gx in range(x + 4, x + TILE - 2, 6):
            pygame.draw.line(surface, (100, 200, 100), (gx, y + TILE), (gx + 2, y + TILE - 6), 1)


def draw_player(surface, x, y, direction=0):
    """Draw player character on the map."""
    # Body
    pygame.draw.rect(surface, BLUE, (x + 8, y + 10, 16, 16))
    # Head
    pygame.draw.circle(surface, (240, 210, 180), (x + 16, y + 8), 7)
    # Hat
    pygame.draw.rect(surface, RED, (x + 8, y + 1, 16, 6))
    # Eyes based on direction
    if direction == 0:  # down
        pygame.draw.circle(surface, BLACK, (x + 13, y + 8), 1)
        pygame.draw.circle(surface, BLACK, (x + 19, y + 8), 1)
    elif direction == 1:  # up
        pass  # back of head
    elif direction == 2:  # left
        pygame.draw.circle(surface, BLACK, (x + 12, y + 8), 1)
    elif direction == 3:  # right
        pygame.draw.circle(surface, BLACK, (x + 20, y + 8), 1)
    # Legs
    pygame.draw.rect(surface, DARK_BLUE, (x + 10, y + 26, 5, 4))
    pygame.draw.rect(surface, DARK_BLUE, (x + 17, y + 26, 5, 4))


def draw_npc(surface, x, y, color=ORANGE):
    """Draw NPC trainer."""
    pygame.draw.rect(surface, color, (x + 8, y + 10, 16, 16))
    pygame.draw.circle(surface, (240, 210, 180), (x + 16, y + 8), 7)
    pygame.draw.rect(surface, color, (x + 9, y + 1, 14, 6))
    pygame.draw.circle(surface, BLACK, (x + 13, y + 8), 1)
    pygame.draw.circle(surface, BLACK, (x + 19, y + 8), 1)
    pygame.draw.rect(surface, DARK_GREY, (x + 10, y + 26, 5, 4))
    pygame.draw.rect(surface, DARK_GREY, (x + 17, y + 26, 5, 4))
    # Exclamation mark for undefeated trainer
    pygame.draw.rect(surface, RED, (x + 14, y - 8, 4, 8))
    pygame.draw.rect(surface, RED, (x + 14, y + 2, 4, 3))


def draw_npc_simple(surface, x, y, color=ORANGE):
    """Draw NPC without exclamation mark."""
    pygame.draw.rect(surface, color, (x + 8, y + 10, 16, 16))
    pygame.draw.circle(surface, (240, 210, 180), (x + 16, y + 8), 7)
    pygame.draw.rect(surface, color, (x + 9, y + 1, 14, 6))
    pygame.draw.circle(surface, BLACK, (x + 13, y + 8), 1)
    pygame.draw.circle(surface, BLACK, (x + 19, y + 8), 1)
    pygame.draw.rect(surface, DARK_GREY, (x + 10, y + 26, 5, 4))
    pygame.draw.rect(surface, DARK_GREY, (x + 17, y + 26, 5, 4))


# ---------------------------------------------------------------------------
# Text rendering
# ---------------------------------------------------------------------------
class TextBox:
    def __init__(self, font):
        self.font = font
        self.messages = []
        self.current_msg = ""
        self.char_index = 0
        self.timer = 0
        self.active = False
        self.callback = None

    def show(self, text, callback=None):
        self.messages = text if isinstance(text, list) else [text]
        self.current_msg = self.messages.pop(0)
        self.char_index = 0
        self.timer = 0
        self.active = True
        self.callback = callback

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        if self.timer > 25:
            self.timer = 0
            if self.char_index < len(self.current_msg):
                self.char_index += 1

    def advance(self):
        """Called when player presses action. Returns True if textbox closed."""
        if self.char_index < len(self.current_msg):
            self.char_index = len(self.current_msg)
            return False
        elif self.messages:
            self.current_msg = self.messages.pop(0)
            self.char_index = 0
            return False
        else:
            self.active = False
            if self.callback:
                self.callback()
            return True

    def draw(self, surface, screen_w, screen_h):
        if not self.active:
            return
        box_h = 80
        box_y = screen_h - box_h - 8
        box_rect = pygame.Rect(8, box_y, screen_w - 16, box_h)
        pygame.draw.rect(surface, WHITE, box_rect)
        pygame.draw.rect(surface, BLACK, box_rect, 3)

        text = self.current_msg[:self.char_index]
        lines = text.split('\n')
        for i, line in enumerate(lines[:3]):
            rendered = self.font.render(line, True, BLACK)
            surface.blit(rendered, (20, box_y + 8 + i * 22))

        # Blinking arrow if done
        if self.char_index >= len(self.current_msg):
            if pygame.time.get_ticks() % 800 < 400:
                pygame.draw.polygon(surface, BLACK,
                    [(screen_w - 30, box_y + box_h - 18),
                     (screen_w - 22, box_y + box_h - 18),
                     (screen_w - 26, box_y + box_h - 12)])


# ---------------------------------------------------------------------------
# Battle system
# ---------------------------------------------------------------------------
class Battle:
    """Turn-based battle system."""

    STATE_INTRO = 0
    STATE_MENU = 1
    STATE_MOVE_SELECT = 2
    STATE_EXECUTING = 3
    STATE_SWITCH = 4
    STATE_ITEM = 5
    STATE_RESULT = 6
    STATE_XP = 7
    STATE_RUN = 8

    def __init__(self, game, enemy_party, is_wild=True, trainer_name=None,
                 win_callback=None, lose_callback=None, reward=0):
        self.game = game
        self.font = game.font
        self.small_font = game.small_font
        self.player_party = game.party
        self.enemy_party = [Rodent(sp, lv) for sp, lv in enemy_party]
        self.is_wild = is_wild
        self.trainer_name = trainer_name
        self.win_callback = win_callback
        self.lose_callback = lose_callback
        self.reward = reward

        # Active rodents
        self.player_active = self._first_alive(self.player_party)
        self.enemy_active = 0

        self.state = self.STATE_INTRO
        self.menu_cursor = 0
        self.move_cursor = 0
        self.switch_cursor = 0
        self.messages = []
        self.msg_index = 0
        self.msg_timer = 0

        self.anim_timer = 0
        self.player_slide = -200
        self.enemy_slide = 200
        self.flash_timer = 0
        self.shake_timer = 0
        self.catching = False
        self.catch_anim = 0

        self.battle_over = False
        self.result = None  # "win", "lose", "run", "catch"

        if is_wild:
            enemy = self.enemy_party[0]
            self.messages = [f"A wild {enemy.nickname} (Lv.{enemy.level}) appeared!"]
        else:
            self.messages = [f"{trainer_name} wants to battle!",
                             f"{trainer_name} sent out {self.enemy_party[0].nickname}!"]
        self.msg_index = 0

    # ------------------------------------------------------------------ #
    # Sound-effect helpers
    # ------------------------------------------------------------------ #

    def _sfx(self, name: str):
        """Play a sound effect if sfx is available."""
        s = getattr(self.game, 'sfx', None)
        if s:
            s.play(name)

    def _sfx_for_msg(self, msg: str):
        """Derive the appropriate sfx name from a battle message string."""
        if 'used' in msg:          return 'attack'
        if 'super effective' in msg: return 'super_effective'
        if 'not very effective' in msg: return 'not_effective'
        if 'fainted' in msg:       return 'faint'
        if 'Gotcha' in msg:        return 'catch_success'
        if 'Rodent Ball' in msg:   return 'catch_throw'
        if 'broke free' in msg:    return 'catch_fail'
        if 'grew to level' in msg: return 'level_up'
        if 'evolved' in msg:       return 'evolve'
        if 'XP' in msg:            return 'xp'
        if 'Got away' in msg:      return 'run'
        if 'received $' in msg:    return 'win'
        return None

    def _play_msg_sfx(self):
        """Play the sfx corresponding to the currently-displayed message."""
        if self.msg_index < len(self.messages):
            name = self._sfx_for_msg(self.messages[self.msg_index])
            if name:
                self._sfx(name)

    def _set_messages(self, msgs):
        """Set the message list, reset index, and play the first sfx."""
        self.messages = msgs
        self.msg_index = 0
        self._play_msg_sfx()

    # ------------------------------------------------------------------ #

    def _first_alive(self, party):
        for i, r in enumerate(party):
            if r.hp > 0:
                return i
        return 0

    def _player_rodent(self):
        return self.player_party[self.player_active]

    def _enemy_rodent(self):
        return self.enemy_party[self.enemy_active]

    def _calc_damage(self, attacker, defender, move_data):
        if move_data["power"] == 0:
            return 0
        # Basic damage formula
        base = ((2 * attacker.level / 5 + 2) * move_data["power"] *
                attacker.effective_atk() / defender.effective_def()) / 50 + 2
        # Type effectiveness
        move_type = move_data["type"]
        def_type = defender.type
        eff = TYPE_CHART.get(move_type, {}).get(def_type, 1.0)
        # STAB
        stab = 1.3 if move_type == attacker.type else 1.0
        # Random factor
        rand = random.uniform(0.85, 1.0)
        damage = int(base * eff * stab * rand)
        return max(1, damage), eff

    def _apply_effect(self, move_data, target, attacker):
        """Apply move side effects. Returns message or None."""
        effect = move_data.get("effect")
        if not effect:
            return None
        if effect == "def_down":
            target.def_mod -= 1
            return f"{target.nickname}'s defense fell!"
        elif effect == "atk_down":
            target.atk_mod -= 1
            return f"{target.nickname}'s attack fell!"
        elif effect == "acc_down":
            target.acc_mod -= 1
            return f"{target.nickname}'s accuracy fell!"
        elif effect == "def_up":
            attacker.def_mod += 1
            return f"{attacker.nickname}'s defense rose!"
        elif effect == "poison":
            if not target.poisoned:
                target.poisoned = True
                return f"{target.nickname} was poisoned!"
        elif effect == "drain":
            heal = max(1, move_data["power"] // 3)
            attacker.hp = min(attacker.max_hp, attacker.hp + heal)
            return f"{attacker.nickname} drained energy!"
        return None

    def _do_turn(self, player_move_idx):
        """Execute one turn of combat. Returns list of messages."""
        msgs = []
        pr = self._player_rodent()
        er = self._enemy_rodent()

        player_move = MOVES[pr.moves[player_move_idx]]
        enemy_move_name = random.choice(er.moves)
        enemy_move = MOVES[enemy_move_name]

        # Determine order by speed
        p_first = pr.spd >= er.spd
        if pr.spd == er.spd:
            p_first = random.random() < 0.5

        turns = []
        if p_first:
            turns = [("player", pr, er, pr.moves[player_move_idx], player_move),
                     ("enemy", er, pr, enemy_move_name, enemy_move)]
        else:
            turns = [("enemy", er, pr, enemy_move_name, enemy_move),
                     ("player", pr, er, pr.moves[player_move_idx], player_move)]

        for who, attacker, defender, move_name, move_data in turns:
            if attacker.hp <= 0:
                continue

            # Accuracy check
            acc = move_data["acc"] + attacker.acc_mod * 10
            if random.randint(1, 100) > acc:
                msgs.append(f"{attacker.nickname} used {move_name}!")
                msgs.append("But it missed!")
                continue

            msgs.append(f"{attacker.nickname} used {move_name}!")

            if move_data["power"] > 0:
                dmg, eff = self._calc_damage(attacker, defender, move_data)
                defender.hp = max(0, defender.hp - dmg)
                if eff > 1.0:
                    msgs.append("It's super effective!")
                elif eff < 1.0:
                    msgs.append("It's not very effective...")

            effect_msg = self._apply_effect(move_data, defender, attacker)
            if effect_msg:
                msgs.append(effect_msg)

            if defender.hp <= 0:
                msgs.append(f"{defender.nickname} fainted!")
                break

        # Poison damage
        for r in [pr, er]:
            if r.hp > 0 and r.poisoned:
                pdmg = max(1, r.max_hp // 8)
                r.hp = max(0, r.hp - pdmg)
                msgs.append(f"{r.nickname} took poison damage!")
                if r.hp <= 0:
                    msgs.append(f"{r.nickname} fainted!")

        return msgs

    def _try_catch(self):
        """Attempt to catch wild rodent."""
        er = self._enemy_rodent()
        data = SPECIES[er.species]
        catch_rate = data["catch_rate"]
        hp_factor = (1 - er.hp / er.max_hp) * 150
        roll = random.randint(0, 255)
        caught = roll < (catch_rate + hp_factor) / 2

        msgs = [f"You threw a Rodent Ball!"]
        if caught:
            msgs.append(f"Gotcha! {er.nickname} was caught!")
            if len(self.player_party) < 6:
                self.player_party.append(er)
                msgs.append(f"{er.nickname} joined your party!")
            else:
                msgs.append(f"But your party is full! {er.nickname} was released.")
            self.result = "catch"
        else:
            msgs.append(f"Oh no! {er.nickname} broke free!")
            # Enemy gets a turn
            enemy_move_name = random.choice(er.moves)
            enemy_move = MOVES[enemy_move_name]
            pr = self._player_rodent()
            msgs.append(f"{er.nickname} used {enemy_move_name}!")
            if enemy_move["power"] > 0 and random.randint(1, 100) <= enemy_move["acc"]:
                dmg, eff = self._calc_damage(er, pr, enemy_move)
                pr.hp = max(0, pr.hp - dmg)
                if pr.hp <= 0:
                    msgs.append(f"{pr.nickname} fainted!")
        return msgs

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.state in (self.STATE_INTRO, self.STATE_EXECUTING, self.STATE_XP):
            if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                self.msg_index += 1
                if self.msg_index >= len(self.messages):
                    if self.state == self.STATE_INTRO:
                        self.state = self.STATE_MENU
                    elif self.state == self.STATE_XP:
                        self.battle_over = True
                    else:
                        self._after_turn()
                else:
                    self._play_msg_sfx()

        elif self.state == self.STATE_MENU:
            if event.key == pygame.K_UP:
                self.menu_cursor = (self.menu_cursor - 1) % 4
                self._sfx('cursor')
            elif event.key == pygame.K_DOWN:
                self.menu_cursor = (self.menu_cursor + 1) % 4
                self._sfx('cursor')
            elif event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                if self.menu_cursor == 0:  # Fight
                    self.state = self.STATE_MOVE_SELECT
                    self.move_cursor = 0
                    self._sfx('confirm')
                elif self.menu_cursor == 1:  # Rodents
                    self.state = self.STATE_SWITCH
                    self.switch_cursor = 0
                    self._sfx('confirm')
                elif self.menu_cursor == 2:  # Catch (wild only)
                    if self.is_wild:
                        self._set_messages(self._try_catch())
                        self.state = self.STATE_EXECUTING
                    else:
                        self._set_messages(["Can't catch a trainer's rodent!"])
                        self.state = self.STATE_EXECUTING
                elif self.menu_cursor == 3:  # Run
                    if self.is_wild:
                        pr = self._player_rodent()
                        er = self._enemy_rodent()
                        if random.randint(0, 100) < 50 + pr.spd - er.spd:
                            msgs = ["Got away safely!"]
                            self.result = "run"
                        else:
                            msgs = ["Can't escape!"]
                            move_name = random.choice(er.moves)
                            move_data = MOVES[move_name]
                            msgs.append(f"{er.nickname} used {move_name}!")
                            if move_data["power"] > 0 and random.randint(1, 100) <= move_data["acc"]:
                                dmg, eff = self._calc_damage(er, pr, move_data)
                                pr.hp = max(0, pr.hp - dmg)
                                if pr.hp <= 0:
                                    msgs.append(f"{pr.nickname} fainted!")
                        self._set_messages(msgs)
                        self.state = self.STATE_EXECUTING
                    else:
                        self._set_messages(["Can't run from a trainer battle!"])
                        self.state = self.STATE_EXECUTING
            elif event.key in (pygame.K_x, pygame.K_ESCAPE):
                self._sfx('back')

        elif self.state == self.STATE_MOVE_SELECT:
            pr = self._player_rodent()
            n_moves = len(pr.moves)
            if event.key == pygame.K_UP:
                self.move_cursor = (self.move_cursor - 1) % n_moves
                self._sfx('cursor')
            elif event.key == pygame.K_DOWN:
                self.move_cursor = (self.move_cursor + 1) % n_moves
                self._sfx('cursor')
            elif event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                self._set_messages(self._do_turn(self.move_cursor))
                self.state = self.STATE_EXECUTING
            elif event.key in (pygame.K_x, pygame.K_ESCAPE):
                self.state = self.STATE_MENU
                self._sfx('back')

        elif self.state == self.STATE_SWITCH:
            n = len(self.player_party)
            if event.key == pygame.K_UP:
                self.switch_cursor = (self.switch_cursor - 1) % n
                self._sfx('cursor')
            elif event.key == pygame.K_DOWN:
                self.switch_cursor = (self.switch_cursor + 1) % n
                self._sfx('cursor')
            elif event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                target = self.player_party[self.switch_cursor]
                if target.hp <= 0:
                    self._set_messages([f"{target.nickname} has fainted!"])
                    self.state = self.STATE_EXECUTING
                elif self.switch_cursor == self.player_active:
                    self._set_messages([f"{target.nickname} is already out!"])
                    self.state = self.STATE_EXECUTING
                else:
                    old = self._player_rodent()
                    old.reset_battle_mods()
                    self.player_active = self.switch_cursor
                    new = self._player_rodent()
                    msgs = [f"Come back, {old.nickname}!", f"Go, {new.nickname}!"]
                    er = self._enemy_rodent()
                    move_name = random.choice(er.moves)
                    move_data = MOVES[move_name]
                    msgs.append(f"{er.nickname} used {move_name}!")
                    if move_data["power"] > 0 and random.randint(1, 100) <= move_data["acc"]:
                        dmg, eff = self._calc_damage(er, new, move_data)
                        new.hp = max(0, new.hp - dmg)
                        if new.hp <= 0:
                            msgs.append(f"{new.nickname} fainted!")
                    self._set_messages(msgs)
                    self.state = self.STATE_EXECUTING
            elif event.key in (pygame.K_x, pygame.K_ESCAPE):
                if self._player_rodent().hp > 0:
                    self.state = self.STATE_MENU
                    self._sfx('back')

        elif self.state == self.STATE_RESULT:
            if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                self.msg_index += 1
                if self.msg_index >= len(self.messages):
                    self.battle_over = True
                else:
                    self._play_msg_sfx()

    def _after_turn(self):
        """Check win/lose conditions after a turn resolves."""
        pr = self._player_rodent()
        er = self._enemy_rodent()

        if self.result == "run":
            self.state = self.STATE_RESULT
            self._set_messages(["Got away safely!"])
            return

        if self.result == "catch":
            self.state = self.STATE_RESULT
            self._set_messages(["Battle over!"])
            return

        # Enemy fainted
        if er.hp <= 0:
            er.reset_battle_mods()
            xp_gain = (er.level * 10) + 20
            xp_msgs = pr.gain_xp(xp_gain)
            msgs = [f"{pr.nickname} gained {xp_gain} XP!"] + xp_msgs

            next_enemy = None
            for i in range(len(self.enemy_party)):
                if self.enemy_party[i].hp > 0:
                    next_enemy = i
                    break
            if next_enemy is not None:
                self.enemy_active = next_enemy
                ne = self._enemy_rodent()
                if self.trainer_name:
                    msgs.append(f"{self.trainer_name} sent out {ne.nickname}!")
                self._set_messages(msgs)
                self.state = self.STATE_EXECUTING
                return
            else:
                self.result = "win"
                if self.reward > 0:
                    self.game.money += self.reward
                    msgs.append(f"You received ${self.reward}!")
                self._set_messages(msgs)
                self.state = self.STATE_XP
                return

        # Player fainted
        if pr.hp <= 0:
            pr.reset_battle_mods()
            alive = [i for i, r in enumerate(self.player_party) if r.hp > 0]
            if alive:
                self._set_messages(["Choose next rodent!"])
                self.state = self.STATE_SWITCH
                self.switch_cursor = alive[0]
                return
            else:
                self.result = "lose"
                self._set_messages(["All your rodents fainted!", "You blacked out..."])
                self.state = self.STATE_RESULT
                return

        self.state = self.STATE_MENU

    def draw(self, surface):
        # Background
        surface.fill((200, 220, 200))

        # Battle ground
        pygame.draw.ellipse(surface, (160, 200, 160), (50, 280, 200, 50))
        pygame.draw.ellipse(surface, (160, 200, 160), (380, 140, 200, 50))

        # Draw rodents
        pr = self._player_rodent()
        er = self._enemy_rodent()

        # Player rodent (bottom-left)
        px = 100 + int(max(0, self.player_slide))
        draw_rodent_sprite(surface, pr.species, px, 220, 80)

        # Enemy rodent (top-right)
        ex = 420 + int(min(0, self.enemy_slide))
        draw_rodent_sprite(surface, er.species, ex, 80, 80, flip=True)

        # Flash effect on hit
        if self.flash_timer > 0:
            flash_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, min(128, self.flash_timer * 8)))
            surface.blit(flash_surf, (0, 0))

        # HP bars - Player
        self._draw_hp_bar(surface, pr, 20, 330, True)
        # HP bars - Enemy
        self._draw_hp_bar(surface, er, 350, 30, False)

        # UI based on state
        if self.state in (self.STATE_INTRO, self.STATE_EXECUTING, self.STATE_RESULT, self.STATE_XP):
            self._draw_message_box(surface)

        elif self.state == self.STATE_MENU:
            self._draw_battle_menu(surface)

        elif self.state == self.STATE_MOVE_SELECT:
            self._draw_move_menu(surface, pr)

        elif self.state == self.STATE_SWITCH:
            self._draw_switch_menu(surface)

    def _draw_hp_bar(self, surface, rodent, x, y, is_player):
        box = pygame.Rect(x, y, 250, 60)
        pygame.draw.rect(surface, WHITE, box)
        pygame.draw.rect(surface, BLACK, box, 2)

        # Name and level
        name_text = self.font.render(f"{rodent.nickname}", True, BLACK)
        level_text = self.small_font.render(f"Lv.{rodent.level}", True, BLACK)
        surface.blit(name_text, (x + 8, y + 4))
        surface.blit(level_text, (x + 180, y + 6))

        # Type indicator
        type_color = TYPE_COLORS.get(rodent.type, GREY)
        pygame.draw.rect(surface, type_color, (x + 8, y + 24, 40, 12))
        type_text = self.small_font.render(rodent.type, True, WHITE)
        surface.blit(type_text, (x + 10, y + 24))

        # HP bar
        bar_x, bar_y = x + 55, y + 26
        bar_w = 180
        hp_pct = max(0, rodent.hp / rodent.max_hp)
        hp_color = GREEN if hp_pct > 0.5 else YELLOW if hp_pct > 0.2 else RED
        pygame.draw.rect(surface, DARK_GREY, (bar_x, bar_y, bar_w, 10))
        pygame.draw.rect(surface, hp_color, (bar_x, bar_y, int(bar_w * hp_pct), 10))
        pygame.draw.rect(surface, BLACK, (bar_x, bar_y, bar_w, 10), 1)

        # HP text
        hp_text = self.small_font.render(f"{max(0, rodent.hp)}/{rodent.max_hp}", True, BLACK)
        surface.blit(hp_text, (bar_x + bar_w // 2 - hp_text.get_width() // 2, y + 40))

        # XP bar (player only)
        if is_player:
            xp_pct = rodent.xp / max(1, rodent.xp_to_next)
            pygame.draw.rect(surface, DARK_GREY, (bar_x, y + 52, bar_w, 4))
            pygame.draw.rect(surface, LIGHT_BLUE, (bar_x, y + 52, int(bar_w * xp_pct), 4))

    def _draw_message_box(self, surface):
        box = pygame.Rect(8, SCREEN_H - 80, SCREEN_W - 16, 72)
        pygame.draw.rect(surface, WHITE, box)
        pygame.draw.rect(surface, BLACK, box, 3)
        if self.msg_index < len(self.messages):
            text = self.font.render(self.messages[self.msg_index], True, BLACK)
            surface.blit(text, (20, SCREEN_H - 68))
            # Arrow
            if pygame.time.get_ticks() % 800 < 400:
                pygame.draw.polygon(surface, BLACK,
                    [(SCREEN_W - 30, SCREEN_H - 20),
                     (SCREEN_W - 22, SCREEN_H - 20),
                     (SCREEN_W - 26, SCREEN_H - 14)])

    def _draw_battle_menu(self, surface):
        box = pygame.Rect(8, SCREEN_H - 80, SCREEN_W - 16, 72)
        pygame.draw.rect(surface, WHITE, box)
        pygame.draw.rect(surface, BLACK, box, 3)

        what_text = self.font.render(f"What will {self._player_rodent().nickname} do?", True, BLACK)
        surface.blit(what_text, (20, SCREEN_H - 74))

        options = ["FIGHT", "RODENTS", "CATCH" if self.is_wild else "-----", "RUN"]
        menu_box = pygame.Rect(SCREEN_W - 200, SCREEN_H - 80, 192, 72)
        pygame.draw.rect(surface, WHITE, menu_box)
        pygame.draw.rect(surface, BLACK, menu_box, 2)

        for i, opt in enumerate(options):
            col, row = i % 2, i // 2
            x = SCREEN_W - 190 + col * 95
            y = SCREEN_H - 74 + row * 30
            color = BLACK if not (not self.is_wild and i == 2) else GREY
            text = self.font.render(opt, True, color)
            surface.blit(text, (x + 14, y))
            if i == self.menu_cursor:
                pygame.draw.polygon(surface, BLACK, [(x, y + 4), (x, y + 14), (x + 10, y + 9)])

    def _draw_move_menu(self, surface, rodent):
        box = pygame.Rect(8, SCREEN_H - 120, SCREEN_W - 16, 112)
        pygame.draw.rect(surface, WHITE, box)
        pygame.draw.rect(surface, BLACK, box, 3)

        for i, move_name in enumerate(rodent.moves):
            move_data = MOVES[move_name]
            y = SCREEN_H - 114 + i * 26
            # Type color dot
            tc = TYPE_COLORS.get(move_data["type"], GREY)
            pygame.draw.circle(surface, tc, (30, y + 8), 5)
            text = self.font.render(f"{move_name}", True, BLACK)
            surface.blit(text, (42, y))
            pow_text = self.small_font.render(
                f"POW:{move_data['power']}" if move_data["power"] > 0 else "STATUS",
                True, DARK_GREY)
            surface.blit(pow_text, (240, y + 2))
            acc_text = self.small_font.render(f"ACC:{move_data['acc']}%", True, DARK_GREY)
            surface.blit(acc_text, (340, y + 2))

            if i == self.move_cursor:
                pygame.draw.polygon(surface, BLACK, [(20, y + 3), (20, y + 13), (26, y + 8)])

        # Move description
        if self.move_cursor < len(rodent.moves):
            desc = MOVES[rodent.moves[self.move_cursor]]["desc"]
            desc_text = self.small_font.render(desc, True, DARK_GREY)
            surface.blit(desc_text, (42, SCREEN_H - 18))

    def _draw_switch_menu(self, surface):
        box = pygame.Rect(40, 20, SCREEN_W - 80, SCREEN_H - 40)
        pygame.draw.rect(surface, WHITE, box)
        pygame.draw.rect(surface, BLACK, box, 3)

        title = self.font.render("Choose a Rodent:", True, BLACK)
        surface.blit(title, (60, 30))

        for i, rodent in enumerate(self.player_party):
            y = 60 + i * 60
            row_rect = pygame.Rect(50, y, SCREEN_W - 100, 52)

            if rodent.hp <= 0:
                pygame.draw.rect(surface, (240, 200, 200), row_rect)
            elif i == self.player_active:
                pygame.draw.rect(surface, (200, 240, 200), row_rect)
            else:
                pygame.draw.rect(surface, (230, 230, 230), row_rect)
            pygame.draw.rect(surface, BLACK, row_rect, 1)

            # Mini sprite
            draw_rodent_sprite(surface, rodent.species, 55, y - 5, 40)

            name = self.font.render(f"{rodent.nickname} Lv.{rodent.level}", True, BLACK)
            surface.blit(name, (100, y + 4))

            hp_text = self.small_font.render(f"HP: {rodent.hp}/{rodent.max_hp}", True,
                                             RED if rodent.hp <= 0 else BLACK)
            surface.blit(hp_text, (100, y + 26))

            type_text = self.small_font.render(rodent.type, True, TYPE_COLORS.get(rodent.type, GREY))
            surface.blit(type_text, (250, y + 26))

            if i == self.switch_cursor:
                pygame.draw.polygon(surface, BLACK, [(45, y + 18), (45, y + 30), (52, y + 24)])

    def update(self, dt):
        # Slide-in animation
        if self.player_slide < 0:
            self.player_slide += dt * 0.5
        if self.enemy_slide > 0:
            self.enemy_slide -= dt * 0.5
        if self.flash_timer > 0:
            self.flash_timer -= dt * 0.05


# ---------------------------------------------------------------------------
# Main Game
# ---------------------------------------------------------------------------
class Game:
    STATE_TITLE = 0
    STATE_STARTER = 1
    STATE_OVERWORLD = 2
    STATE_BATTLE = 3
    STATE_MENU = 4
    STATE_SLOT_SELECT = 5
    STATE_SETTINGS = 6

    NUM_SAVE_SLOTS = 3

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("RodentMon")
        self.clock = pygame.time.Clock()

        # Music — synthesised on startup; gracefully skipped if numpy missing
        if _MUSIC_AVAILABLE:
            self.music = MusicPlayer()
            self.music.play('title')
        else:
            self.music = None

        # Sound effects
        self.sfx = SoundFX() if _SFX_AVAILABLE else None

        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.big_font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 64)

        self.state = self.STATE_TITLE
        self.party = []
        self.money = 1000
        self.badges = []
        self.defeated_trainers = set()
        self.has_starter = False

        # Build maps
        self.maps = {
            "hometown": make_hometown(),
            "route1": make_route(1, 30, 25, "route1", "hometown", "town2",
                                TRAINER_DATA["route1"]),
            "town2": make_town2(),
            "route2": make_route(2, 30, 25, "route2", "town2", "route3",
                                TRAINER_DATA["route2"]),
            "route3": make_route(3, 30, 25, "route3", "route2", "town3",
                                TRAINER_DATA["route3"]),
            "town3": make_town3(),
            "route4": make_route(4, 30, 25, "route4", "town3", None,
                                TRAINER_DATA["route4"]),
            # Interiors
            "interior_house": make_interior_house(),
            "interior_lab": make_interior_lab(),
            "interior_center_hometown": make_interior_center("hometown", 12, 20),
            "interior_center_town2": make_interior_center("town2", 8, 12),
            "interior_center_town3": make_interior_center("town3", 8, 12),
            "interior_gym1": make_interior_gym(1, "town2", 21, 12),
            "interior_gym2": make_interior_gym(2, "town3", 21, 12),
        }

        self.current_map_name = "hometown"
        self.current_map = self.maps["hometown"]
        spawn = self.current_map["spawn"]
        self.player_x = spawn[0]
        self.player_y = spawn[1]
        self.player_dir = 0
        self.moving = False
        self.move_timer = 0
        self.step_counter = 0

        self.textbox = TextBox(self.font)
        self.battle = None
        self.menu_cursor = 0
        self.title_cursor = 0

        self.camera_x = 0
        self.camera_y = 0

        self.transition_alpha = 0
        self.transitioning = False
        self.transition_phase = "in"  # "in" = fading to black, "out" = fading back
        self.transition_callback = None

        # Settings
        self.settings_cursor = 0    # 0=music vol, 1=music on/off, 2=sfx on/off

        # Save slots
        self.save_slot = None        # active slot number (1-3)
        self.slot_cursor = 0         # cursor row in slot select screen (0-2)
        self.slot_mode = 'new'       # 'new' or 'load'
        self.confirm_action = None   # None | 'delete' | 'overwrite'

    def _start_transition(self, callback):
        self.transitioning = True
        self.transition_alpha = 0
        self.transition_phase = "in"
        self.transition_callback = callback

    def _change_map(self, map_name, px, py):
        self.current_map_name = map_name
        self.current_map = self.maps[map_name]
        self.player_x = px
        self.player_y = py
        if self.music and self.state != self.STATE_BATTLE:
            self.music.play_for_map(map_name)
        self._save_game()

    def _heal_party(self):
        for r in self.party:
            r.hp = r.max_hp
            r.poisoned = False
            r.reset_battle_mods()

    def _is_walkable(self, x, y):
        m = self.current_map
        if x < 0 or y < 0 or x >= m["w"] or y >= m["h"]:
            return False
        tile = m["tiles"][y][x]
        return tile not in ('#', '~', 'H', 'R', 'X', 'D', 'S', 'T', 'W', 'K', 'B', 'L', 'N')

    def _check_encounters(self):
        if not self.party:
            return
        m = self.current_map
        tile = m["tiles"][self.player_y][self.player_x]
        if tile == '.' and m.get("encounters"):
            self.step_counter += 1
            if self.step_counter >= random.randint(8, 20):
                self.step_counter = 0
                table = ENCOUNTER_TABLES.get(m["encounters"])
                if table:
                    roll = random.randint(1, 100)
                    cumulative = 0
                    for species, min_lv, max_lv, chance in table:
                        cumulative += chance
                        if roll <= cumulative:
                            level = random.randint(min_lv, max_lv)
                            self._start_battle([(species, level)], is_wild=True)
                            return

    def _check_exits(self):
        m = self.current_map
        for ex in m.get("exits", []):
            if self.player_x == ex["x"] and self.player_y == ex["y"]:
                dest = ex["dest"]
                dx, dy = ex["dx"], ex["dy"]
                self._start_transition(lambda d=dest, x=dx, y=dy: self._change_map(d, x, y))

    def _interact(self):
        """Interact with the tile the player is facing."""
        dx, dy = [(0, 1), (0, -1), (-1, 0), (1, 0)][self.player_dir]
        tx, ty = self.player_x + dx, self.player_y + dy
        m = self.current_map

        if tx < 0 or ty < 0 or tx >= m["w"] or ty >= m["h"]:
            return

        tile = m["tiles"][ty][tx]

        # Signs
        if (tx, ty) in m.get("signs", {}):
            self.textbox.show(m["signs"][(tx, ty)])
            return

        # Doors - transition into building
        if tile == 'D' and (tx, ty) in m.get("doors", {}):
            door = m["doors"][(tx, ty)]
            if door["action"] == "enter":
                dest = door["dest"]
                ddx, ddy = door["dx"], door["dy"]
                self._start_transition(lambda d=dest, x=ddx, y=ddy: self._change_map(d, x, y))
            return

        # Interior NPCs
        if tile == 'N':
            for npc in m.get("npcs", []):
                if tuple(npc["pos"]) == (tx, ty):
                    action = npc.get("action")
                    if action == "heal":
                        self._heal_party()
                        self.textbox.show(npc["msg"])
                    elif action == "lab":
                        if not self.has_starter:
                            self.state = self.STATE_STARTER
                        else:
                            self.textbox.show(npc["msg"])
                    elif action == "gym":
                        if not self.party:
                            self.textbox.show("You don't have any rodents!\nVisit Prof. Whiskers' Lab first.")
                        else:
                            gym_id = npc["gym_id"]
                            gym = GYM_DATA[gym_id]
                            if gym["badge"] in self.badges:
                                self.textbox.show(f"You've already earned the\n{gym['badge']}!")
                            else:
                                self.textbox.show(gym["msg_before"],
                                    callback=lambda gid=gym_id: self._start_gym(gid))
                    else:
                        self.textbox.show(npc["msg"])
                    return

        # Trainers (overworld)
        if tile == 'T':
            for t in m.get("trainers", []):
                if t["pos"] == (tx, ty):
                    tid = f"{self.current_map_name}_{t['name']}"
                    if tid in self.defeated_trainers:
                        self.textbox.show(t["msg_after"])
                    elif not self.party:
                        self.textbox.show("You don't have any rodents!\nVisit Prof. Whiskers' Lab first.")
                    else:
                        self.textbox.show(t["msg_before"],
                            callback=lambda t=t: self._start_trainer_battle(t))
                    return

    def _start_battle(self, enemy_party, is_wild=True, trainer_name=None,
                      win_cb=None, lose_cb=None, reward=0):
        self.battle = Battle(self, enemy_party, is_wild, trainer_name,
                           win_cb, lose_cb, reward)
        self.state = self.STATE_BATTLE
        if self.music:
            track = 'gym' if not is_wild and 'gym' in self.current_map_name else 'battle'
            self.music.play(track)

    def _start_trainer_battle(self, trainer):
        tid = f"{self.current_map_name}_{trainer['name']}"
        def on_win():
            self.defeated_trainers.add(tid)
        self._start_battle(trainer["party"], is_wild=False,
                          trainer_name=trainer["name"],
                          win_cb=on_win, reward=trainer["reward"])

    def _start_gym(self, gym_id):
        gym = GYM_DATA[gym_id]
        def on_win():
            self.badges.append(gym["badge"])
            self.textbox.show(gym["msg_after"])
        self._start_battle(gym["party"], is_wild=False,
                          trainer_name=f"Leader {gym['leader']}",
                          win_cb=on_win, reward=gym["reward"])

    # ------------------------------------------------------------------ #
    # Save-slot helpers
    # ------------------------------------------------------------------ #

    def _slot_path(self, slot: int) -> str:
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, f"rodentmon_save_{slot}.json")

    def _slot_info(self, slot: int):
        """Return a summary dict for the slot, or None if empty/corrupt."""
        path = self._slot_path(slot)
        if not os.path.exists(path):
            return None
        try:
            with open(path) as f:
                data = json.load(f)
            return {
                "map":      data.get("map", "?"),
                "badges":   len(data.get("badges", [])),
                "party":    [r["species"] for r in data.get("party", [])],
                "saved_at": data.get("saved_at", ""),
            }
        except Exception:
            return None

    def _delete_slot(self, slot: int):
        path = self._slot_path(slot)
        if os.path.exists(path):
            os.remove(path)

    def _start_new_game_in_slot(self, slot: int):
        """Reset all game state and begin a fresh game in the given slot."""
        self.save_slot = slot
        self.party = []
        self.money = 1000
        self.badges = []
        self.defeated_trainers = set()
        self.has_starter = False
        self.current_map_name = "hometown"
        self.current_map = self.maps["hometown"]
        spawn = self.current_map["spawn"]
        self.player_x = spawn[0]
        self.player_y = spawn[1]
        self.state = self.STATE_STARTER

    def _save_game(self):
        """Auto-save to the active slot.  Does nothing if no slot is active."""
        if self.save_slot is None:
            return
        data = {
            "party":         [r.to_dict() for r in self.party],
            "money":         self.money,
            "badges":        self.badges,
            "defeated":      list(self.defeated_trainers),
            "map":           self.current_map_name,
            "px":            self.player_x,
            "py":            self.player_y,
            "has_starter":   self.has_starter,
            "saved_at":      datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "music_volume":  self.music.volume  if self.music else 1.0,
            "music_enabled": self.music.enabled if self.music else True,
            "sfx_enabled":   self.sfx.enabled   if self.sfx   else True,
        }
        with open(self._slot_path(self.save_slot), 'w') as f:
            json.dump(data, f)

    def _load_game(self, slot: int):
        path = self._slot_path(slot)
        if not os.path.exists(path):
            return False
        with open(path) as f:
            data = json.load(f)
        self.party = [Rodent.from_dict(d) for d in data["party"]]
        self.money = data["money"]
        self.badges = data["badges"]
        self.defeated_trainers = set(data["defeated"])
        self.current_map_name = data["map"]
        self.current_map = self.maps[self.current_map_name]
        self.player_x = data["px"]
        self.player_y = data["py"]
        self.has_starter = data["has_starter"]
        self.save_slot = slot
        if self.music:
            self.music.set_volume(data.get("music_volume", 1.0))
            self.music.set_enabled(data.get("music_enabled", True))
        if self.sfx:
            self.sfx.set_enabled(data.get("sfx_enabled", True))
        self.state = self.STATE_OVERWORLD
        if self.music:
            self.music.play_for_map(self.current_map_name)
        return True

    def run(self):
        crash_log = os.path.join(os.path.dirname(__file__), "crash.log")
        try:
            running = True
            while running:
                dt = self.clock.tick(FPS)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    self._handle_event(event)

                self._update(dt)
                self._draw()
                pygame.display.flip()
        except Exception:
            tb = traceback.format_exc()
            print(f"\n{'='*60}\nRodentMon crashed! Stack trace:\n{'='*60}\n{tb}", file=sys.stderr)
            with open(crash_log, "w") as f:
                f.write(f"RodentMon crash report\n{'='*60}\n")
                f.write(f"Map: {self.current_map_name}  Pos: ({self.player_x}, {self.player_y})\n")
                f.write(f"State: {self.state}  Transitioning: {self.transitioning}\n")
                f.write(f"Party: {[(r.species, r.level, r.hp) for r in self.party]}\n")
                f.write(f"{'='*60}\n{tb}")
            print(f"Crash log written to: {crash_log}", file=sys.stderr)
        finally:
            pygame.quit()

    def _handle_event(self, event):
        if self.transitioning:
            return

        if self.state == self.STATE_TITLE:
            if event.type == pygame.KEYDOWN:
                any_save = any(
                    self._slot_info(s) for s in range(1, self.NUM_SAVE_SLOTS + 1)
                )
                max_opt = 1 if any_save else 0
                if event.key == pygame.K_UP:
                    self.title_cursor = max(0, self.title_cursor - 1)
                    if self.sfx: self.sfx.play('cursor')
                elif event.key == pygame.K_DOWN:
                    self.title_cursor = min(max_opt, self.title_cursor + 1)
                    if self.sfx: self.sfx.play('cursor')
                elif event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                    self.slot_cursor = 0
                    self.confirm_action = None
                    if self.title_cursor == 0:           # NEW GAME
                        self.slot_mode = 'new'
                        self.state = self.STATE_SLOT_SELECT
                        if self.sfx: self.sfx.play('confirm')
                    elif self.title_cursor == 1 and any_save:   # LOAD GAME
                        self.slot_mode = 'load'
                        self.state = self.STATE_SLOT_SELECT
                        if self.sfx: self.sfx.play('confirm')

        elif self.state == self.STATE_SLOT_SELECT:
            if event.type == pygame.KEYDOWN:
                slot = self.slot_cursor + 1   # 1-based
                info = self._slot_info(slot)

                if self.confirm_action == 'delete':
                    if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                        self._delete_slot(slot)
                        if self.save_slot == slot:
                            self.save_slot = None
                        self.confirm_action = None
                        if self.sfx: self.sfx.play('back')
                    elif event.key in (pygame.K_x, pygame.K_ESCAPE):
                        self.confirm_action = None
                        if self.sfx: self.sfx.play('back')

                elif self.confirm_action == 'overwrite':
                    if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                        self.confirm_action = None
                        self._start_new_game_in_slot(slot)
                        if self.sfx: self.sfx.play('confirm')
                    elif event.key in (pygame.K_x, pygame.K_ESCAPE):
                        self.confirm_action = None
                        if self.sfx: self.sfx.play('back')

                else:
                    if event.key == pygame.K_UP:
                        self.slot_cursor = (self.slot_cursor - 1) % self.NUM_SAVE_SLOTS
                        if self.sfx: self.sfx.play('cursor')
                    elif event.key == pygame.K_DOWN:
                        self.slot_cursor = (self.slot_cursor + 1) % self.NUM_SAVE_SLOTS
                        if self.sfx: self.sfx.play('cursor')
                    elif event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                        if self.slot_mode == 'load':
                            if info:
                                self._load_game(slot)
                                if self.sfx: self.sfx.play('confirm')
                        else:  # 'new'
                            if info:
                                self.confirm_action = 'overwrite'
                                if self.sfx: self.sfx.play('cursor')
                            else:
                                self._start_new_game_in_slot(slot)
                                if self.sfx: self.sfx.play('confirm')
                    elif event.key == pygame.K_d:
                        if info:
                            self.confirm_action = 'delete'
                            if self.sfx: self.sfx.play('cursor')
                    elif event.key in (pygame.K_x, pygame.K_ESCAPE):
                        self.state = self.STATE_TITLE
                        self.title_cursor = 0
                        if self.sfx: self.sfx.play('back')

        elif self.state == self.STATE_STARTER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.menu_cursor = (self.menu_cursor - 1) % 3
                    if self.sfx: self.sfx.play('cursor')
                elif event.key == pygame.K_RIGHT:
                    self.menu_cursor = (self.menu_cursor + 1) % 3
                    if self.sfx: self.sfx.play('cursor')
                elif event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                    starters = ["Mouse", "Gerbil", "Squirrel"]
                    chosen = starters[self.menu_cursor]
                    self.party.append(Rodent(chosen, 5))
                    self.has_starter = True
                    self.state = self.STATE_OVERWORLD
                    if self.music:
                        self.music.play_for_map(self.current_map_name)
                    self._save_game()
                    self.textbox.show(f"You chose {chosen}!\n{chosen} seems happy!")
                elif event.key in (pygame.K_x, pygame.K_ESCAPE):
                    self.state = self.STATE_OVERWORLD
                    if self.music:
                        self.music.play_for_map(self.current_map_name)

        elif self.state == self.STATE_OVERWORLD:
            if self.textbox.active:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                    self.textbox.advance()
                    if self.sfx: self.sfx.play('text')
                return

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                    self._interact()
                    if self.sfx: self.sfx.play('confirm')
                elif event.key == pygame.K_ESCAPE:
                    self.state = self.STATE_MENU
                    self.menu_cursor = 0
                    if self.sfx: self.sfx.play('cursor')

        elif self.state == self.STATE_BATTLE:
            if self.battle:
                self.battle.handle_input(event)

        elif self.state == self.STATE_MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.menu_cursor = (self.menu_cursor - 1) % 5
                    if self.sfx: self.sfx.play('cursor')
                elif event.key == pygame.K_DOWN:
                    self.menu_cursor = (self.menu_cursor + 1) % 5
                    if self.sfx: self.sfx.play('cursor')
                elif event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                    if self.menu_cursor == 0:  # Party
                        pass
                    elif self.menu_cursor == 1:  # Save
                        self._save_game()
                        self.state = self.STATE_OVERWORLD
                        slot_label = f" (Slot {self.save_slot})" if self.save_slot else ""
                        self.textbox.show(f"Game saved{slot_label}!")
                        if self.sfx: self.sfx.play('save')
                    elif self.menu_cursor == 2:  # Badges
                        pass
                    elif self.menu_cursor == 3:  # Settings
                        self.state = self.STATE_SETTINGS
                        self.settings_cursor = 0
                        if self.sfx: self.sfx.play('confirm')
                    elif self.menu_cursor == 4:  # Back
                        self.state = self.STATE_OVERWORLD
                        if self.sfx: self.sfx.play('back')
                elif event.key in (pygame.K_x, pygame.K_ESCAPE):
                    self.state = self.STATE_OVERWORLD
                    if self.sfx: self.sfx.play('back')

        elif self.state == self.STATE_SETTINGS:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.settings_cursor = (self.settings_cursor - 1) % 3
                    if self.sfx: self.sfx.play('cursor')
                elif event.key == pygame.K_DOWN:
                    self.settings_cursor = (self.settings_cursor + 1) % 3
                    if self.sfx: self.sfx.play('cursor')
                elif self.settings_cursor == 0:  # Music Volume
                    if event.key == pygame.K_LEFT and self.music:
                        self.music.set_volume(round(max(0.0, self.music.volume - 0.1), 1))
                        if self.sfx: self.sfx.play('cursor')
                        self._save_game()
                    elif event.key == pygame.K_RIGHT and self.music:
                        self.music.set_volume(round(min(1.0, self.music.volume + 0.1), 1))
                        if self.sfx: self.sfx.play('cursor')
                        self._save_game()
                elif self.settings_cursor == 1:  # Music on/off
                    if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE,
                                     pygame.K_LEFT, pygame.K_RIGHT):
                        if self.music:
                            self.music.set_enabled(not self.music.enabled)
                        if self.sfx: self.sfx.play('confirm')
                        self._save_game()
                elif self.settings_cursor == 2:  # SFX on/off
                    if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE,
                                     pygame.K_LEFT, pygame.K_RIGHT):
                        if self.sfx:
                            new_state = not self.sfx.enabled
                            self.sfx.set_enabled(new_state)
                            if new_state:
                                self.sfx.play('confirm')
                        self._save_game()
                if event.key in (pygame.K_x, pygame.K_ESCAPE):
                    self.state = self.STATE_MENU
                    if self.sfx: self.sfx.play('back')

    def _update(self, dt):
        if self.transitioning:
            if self.transition_phase == "in":
                self.transition_alpha += dt * 0.8
                if self.transition_alpha >= 255:
                    self.transition_alpha = 255
                    if self.transition_callback:
                        self.transition_callback()
                        self.transition_callback = None
                    self.transition_phase = "out"
            else:  # "out"
                self.transition_alpha -= dt * 0.8
                if self.transition_alpha <= 0:
                    self.transition_alpha = 0
                    self.transitioning = False
                    self.moving = False
                    self.move_timer = 0
            return

        if self.state == self.STATE_OVERWORLD:
            self.textbox.update(dt)
            if not self.textbox.active and not self.moving:
                keys = pygame.key.get_pressed()
                dx, dy = 0, 0
                if keys[pygame.K_UP]:
                    dy = -1; self.player_dir = 1
                elif keys[pygame.K_DOWN]:
                    dy = 1; self.player_dir = 0
                elif keys[pygame.K_LEFT]:
                    dx = -1; self.player_dir = 2
                elif keys[pygame.K_RIGHT]:
                    dx = 1; self.player_dir = 3

                if dx != 0 or dy != 0:
                    nx, ny = self.player_x + dx, self.player_y + dy
                    if self._is_walkable(nx, ny):
                        self.player_x = nx
                        self.player_y = ny
                        self.moving = True
                        self.move_timer = 120
                        if self.sfx: self.sfx.play('step')
                        self._check_exits()
                        if not self.transitioning:
                            self._check_encounters()

            if self.moving:
                self.move_timer -= dt
                if self.move_timer <= 0:
                    self.moving = False

        elif self.state == self.STATE_BATTLE:
            if self.battle:
                self.battle.update(dt)
                if self.battle.battle_over:
                    if self.battle.result == "win" and self.battle.win_callback:
                        self.battle.win_callback()
                    elif self.battle.result == "lose":
                        # Heal and return to town
                        self._heal_party()
                        self._change_map("hometown", 14, 13)
                    # Reset battle mods
                    for r in self.party:
                        r.reset_battle_mods()
                    self.battle = None
                    self.state = self.STATE_OVERWORLD
                    if self.music:
                        self.music.play_for_map(self.current_map_name)
                    self._save_game()

    def _draw(self):
        if self.state == self.STATE_TITLE:
            self._draw_title()
        elif self.state == self.STATE_SLOT_SELECT:
            self._draw_slot_select()
        elif self.state == self.STATE_STARTER:
            self._draw_starter_select()
        elif self.state == self.STATE_OVERWORLD:
            self._draw_overworld()
        elif self.state == self.STATE_BATTLE:
            if self.battle:
                self.battle.draw(self.screen)
        elif self.state == self.STATE_MENU:
            self._draw_overworld()
            self._draw_pause_menu()
        elif self.state == self.STATE_SETTINGS:
            self._draw_overworld()
            self._draw_pause_menu()
            self._draw_settings()

        if self.transitioning:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H))
            overlay.fill(BLACK)
            overlay.set_alpha(min(255, int(self.transition_alpha)))
            self.screen.blit(overlay, (0, 0))

    def _draw_title(self):
        self.screen.fill(BLACK)

        # Title
        title = self.title_font.render("RodentMon", True, YELLOW)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 80))

        subtitle = self.font.render("Gotta Catch 'Em All... Rodents!", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_W // 2 - subtitle.get_width() // 2, 140))

        # Draw some rodents on title screen
        draw_rodent_sprite(self.screen, "Mouse", 80, 200, 64)
        draw_rodent_sprite(self.screen, "Squirrel", 200, 190, 64)
        draw_rodent_sprite(self.screen, "Bat", 340, 195, 64)
        draw_rodent_sprite(self.screen, "Gerbil", 460, 200, 64)

        # Menu
        options = ["NEW GAME"]
        if any(self._slot_info(s) for s in range(1, self.NUM_SAVE_SLOTS + 1)):
            options.append("LOAD GAME")

        for i, opt in enumerate(options):
            y = 320 + i * 40
            color = YELLOW if i == self.title_cursor else WHITE
            text = self.font.render(opt, True, color)
            self.screen.blit(text, (SCREEN_W // 2 - text.get_width() // 2, y))
            if i == self.title_cursor:
                pygame.draw.polygon(self.screen, color,
                    [(SCREEN_W // 2 - text.get_width() // 2 - 20, y + 4),
                     (SCREEN_W // 2 - text.get_width() // 2 - 20, y + 16),
                     (SCREEN_W // 2 - text.get_width() // 2 - 10, y + 10)])

        controls = self.small_font.render("Arrow keys: Move | Z/Enter: Confirm | X/Esc: Back", True, GREY)
        self.screen.blit(controls, (SCREEN_W // 2 - controls.get_width() // 2, SCREEN_H - 30))

    # Pretty map labels for slot cards
    _MAP_LABELS = {
        "hometown": "Hometown", "route1": "Route 1", "town2": "Riverside Town",
        "route2": "Route 2", "route3": "Route 3", "town3": "Summit Town",
        "route4": "Route 4", "interior_house": "House", "interior_lab": "Lab",
        "interior_center_hometown": "Pokémon Centre", "interior_center_town2": "Pokémon Centre",
        "interior_center_town3": "Pokémon Centre", "interior_gym1": "Gym 1",
        "interior_gym2": "Gym 2",
    }

    def _draw_slot_select(self):
        self.screen.fill(DARK_BLUE)

        heading = "SELECT A SLOT  —  " + ("NEW GAME" if self.slot_mode == 'new' else "LOAD GAME")
        ht = self.font.render(heading, True, YELLOW)
        self.screen.blit(ht, (SCREEN_W // 2 - ht.get_width() // 2, 18))

        card_w, card_h = 560, 88
        card_x = (SCREEN_W - card_w) // 2
        top_y  = 55

        for i in range(self.NUM_SAVE_SLOTS):
            slot = i + 1
            cy   = top_y + i * (card_h + 8)
            info = self._slot_info(slot)
            selected = (i == self.slot_cursor)

            border_col = YELLOW if selected else GREY
            bg_col     = (30, 50, 80) if selected else (20, 30, 50)
            pygame.draw.rect(self.screen, bg_col,   (card_x, cy, card_w, card_h), border_radius=6)
            pygame.draw.rect(self.screen, border_col, (card_x, cy, card_w, card_h), 2, border_radius=6)

            # Cursor arrow
            if selected:
                pygame.draw.polygon(self.screen, YELLOW,
                    [(card_x - 16, cy + card_h // 2 - 6),
                     (card_x - 16, cy + card_h // 2 + 6),
                     (card_x - 6,  cy + card_h // 2)])

            slot_lbl = self.font.render(f"SLOT {slot}", True, YELLOW if selected else WHITE)
            self.screen.blit(slot_lbl, (card_x + 12, cy + 8))

            if info:
                map_label = self._MAP_LABELS.get(info["map"], info["map"])
                badges_str = f"Badges: {info['badges']}"
                party_str  = "  ".join(info["party"][:6]) or "No rodents"
                saved_str  = info["saved_at"]

                loc = self.small_font.render(f"{map_label}  ·  {badges_str}", True, LIGHT_BLUE)
                self.screen.blit(loc, (card_x + 12, cy + 32))

                pty = self.small_font.render(party_str, True, LIGHT_GREEN)
                self.screen.blit(pty, (card_x + 12, cy + 50))

                sav = self.small_font.render(f"Saved: {saved_str}", True, GREY)
                self.screen.blit(sav, (card_x + card_w - sav.get_width() - 12, cy + 66))
            else:
                empty = self.font.render("— EMPTY —", True, DARK_GREY)
                self.screen.blit(empty, (card_x + card_w // 2 - empty.get_width() // 2,
                                         cy + card_h // 2 - empty.get_height() // 2))

        # Confirmation overlay
        if self.confirm_action:
            slot  = self.slot_cursor + 1
            ox, oy, ow, oh = 140, 185, 360, 80
            pygame.draw.rect(self.screen, BLACK,  (ox, oy, ow, oh), border_radius=8)
            pygame.draw.rect(self.screen, RED,    (ox, oy, ow, oh), 2, border_radius=8)
            if self.confirm_action == 'delete':
                msg = f"Delete Slot {slot}? This cannot be undone."
            else:
                msg = f"Slot {slot} has data. Overwrite?"
            m1 = self.small_font.render(msg, True, WHITE)
            m2 = self.small_font.render("[Z / Enter] Yes     [X / Esc] No", True, GREY)
            self.screen.blit(m1, (ox + ow // 2 - m1.get_width() // 2, oy + 16))
            self.screen.blit(m2, (ox + ow // 2 - m2.get_width() // 2, oy + 46))
            return   # don't draw controls hint below while overlay is up

        # Controls hint
        if self.slot_mode == 'load':
            hint = "[Z] Load   [D] Delete slot   [Esc] Back"
        else:
            hint = "[Z] New game here   [D] Delete slot   [Esc] Back"
        ht2 = self.small_font.render(hint, True, GREY)
        self.screen.blit(ht2, (SCREEN_W // 2 - ht2.get_width() // 2, SCREEN_H - 24))

    def _draw_settings(self, interactive=True):
        # Panel over the content area (left side, same as party/badges)
        menu_w = 200
        panel = pygame.Rect(10, 10, SCREEN_W - menu_w - 30, SCREEN_H - 20)
        pygame.draw.rect(self.screen, WHITE, panel)
        pygame.draw.rect(self.screen, BLACK, panel, 2)

        title = self.font.render("SETTINGS", True, BLACK)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 12))

        music_vol = self.music.volume  if self.music else 1.0
        music_on  = self.music.enabled if self.music else True
        sfx_on    = self.sfx.enabled   if self.sfx   else True

        rows = [
            ("Music Volume", 'slider', music_vol),
            ("Music",        'toggle', music_on),
            ("Sound Effects", 'toggle', sfx_on),
        ]

        row_h   = 58
        start_y = panel.y + 50
        seg_w, gap = 12, 2

        for i, (label, kind, value) in enumerate(rows):
            y        = start_y + i * row_h
            selected = interactive and (i == self.settings_cursor)

            if selected:
                pygame.draw.rect(self.screen, LIGHT_GREEN,
                                 (panel.x + 4, y - 4, panel.w - 8, row_h - 4),
                                 border_radius=4)

            lbl = self.font.render(label, True, BLACK)
            self.screen.blit(lbl, (panel.x + 24, y + 2))

            if selected:
                pygame.draw.polygon(self.screen, BLACK,
                    [(panel.x + 10, y + 6),
                     (panel.x + 10, y + 18),
                     (panel.x + 20, y + 12)])

            if kind == 'slider':
                bx, by = panel.x + 24, y + 26
                steps  = 10
                filled = round(value * steps)
                arr_col = DARK_GREY if not interactive else BLACK
                self.screen.blit(self.small_font.render("<", True, DARK_GREY if value <= 0 else arr_col), (bx, by))
                bx += 14
                for s in range(steps):
                    col = DARK_GREEN if s < filled else GREY
                    pygame.draw.rect(self.screen, col, (bx + s * (seg_w + gap), by + 1, seg_w, 10))
                bx += steps * (seg_w + gap) + 4
                self.screen.blit(self.small_font.render(">", True, DARK_GREY if value >= 1 else arr_col), (bx, by))
                pct = self.small_font.render(f"{round(value * 100)}%", True, DARK_GREY)
                self.screen.blit(pct, (bx + 14, by))

            else:  # toggle
                on_col  = DARK_GREEN if value else GREY
                off_col = GREY       if value else RED
                tx, ty  = panel.x + 24, y + 26
                pygame.draw.rect(self.screen, on_col,  (tx,      ty, 44, 20), border_radius=4)
                pygame.draw.rect(self.screen, off_col, (tx + 48, ty, 44, 20), border_radius=4)
                self.screen.blit(self.font.render("ON",  True, WHITE if value     else GREY), (tx +  8, ty + 2))
                self.screen.blit(self.font.render("OFF", True, WHITE if not value else GREY), (tx + 52, ty + 2))

        if interactive:
            hint = self.small_font.render("↑↓ Select   ◄► / Z Adjust   Esc Back", True, GREY)
            self.screen.blit(hint, (panel.centerx - hint.get_width() // 2, panel.bottom - 22))

    def _draw_starter_select(self):
        self.screen.fill(DARK_GREEN)

        title = self.big_font.render("Choose Your First Rodent!", True, WHITE)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 20))

        starters = ["Mouse", "Gerbil", "Squirrel"]
        for i, species in enumerate(starters):
            x = 60 + i * 200
            y = 100

            # Card background
            card_rect = pygame.Rect(x - 10, y - 10, 160, 280)
            color = YELLOW if i == self.menu_cursor else WHITE
            pygame.draw.rect(self.screen, color, card_rect)
            pygame.draw.rect(self.screen, BLACK, card_rect, 3)

            # Sprite
            draw_rodent_sprite(self.screen, species, x + 30, y + 10, 80)

            # Info
            data = SPECIES[species]
            name = self.font.render(species, True, BLACK)
            self.screen.blit(name, (x + 60 - name.get_width() // 2, y + 100))

            type_text = self.small_font.render(f"Type: {data['type']}", True,
                                               TYPE_COLORS.get(data["type"], GREY))
            self.screen.blit(type_text, (x + 5, y + 125))

            stats = [
                f"HP:  {data['base_hp'] + 10}",
                f"ATK: {data['base_atk'] + 5}",
                f"DEF: {data['base_def'] + 5}",
                f"SPD: {data['base_spd'] + 5}",
            ]
            for j, s in enumerate(stats):
                st = self.small_font.render(s, True, BLACK)
                self.screen.blit(st, (x + 5, y + 148 + j * 18))

            desc = self.small_font.render(data["desc"], True, DARK_GREY)
            self.screen.blit(desc, (x + 5, y + 230))

        hint = self.font.render("< LEFT / RIGHT >  then  Z to choose", True, WHITE)
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 40))

    def _draw_overworld(self):
        m = self.current_map

        # Camera
        self.camera_x = self.player_x * TILE - SCREEN_W // 2 + TILE // 2
        self.camera_y = self.player_y * TILE - SCREEN_H // 2 + TILE // 2
        # Clamp
        self.camera_x = max(0, min(self.camera_x, m["w"] * TILE - SCREEN_W))
        self.camera_y = max(0, min(self.camera_y, m["h"] * TILE - SCREEN_H))

        self.screen.fill(BLACK)

        # Draw visible tiles
        start_x = max(0, self.camera_x // TILE)
        start_y = max(0, self.camera_y // TILE)
        end_x = min(m["w"], start_x + SCREEN_W // TILE + 2)
        end_y = min(m["h"], start_y + SCREEN_H // TILE + 2)

        for ty in range(start_y, end_y):
            for tx in range(start_x, end_x):
                screen_x = tx * TILE - self.camera_x
                screen_y = ty * TILE - self.camera_y
                draw_tile(self.screen, m["tiles"][ty][tx], screen_x, screen_y)

        # Draw trainer NPCs
        for t in m.get("trainers", []):
            tx, ty_pos = t["pos"]
            sx = tx * TILE - self.camera_x
            sy = ty_pos * TILE - self.camera_y
            tid = f"{self.current_map_name}_{t['name']}"
            if tid in self.defeated_trainers:
                draw_npc_simple(self.screen, sx, sy)
            else:
                draw_npc(self.screen, sx, sy)

        # Draw interior NPCs
        for npc in m.get("npcs", []):
            nx, ny = npc["pos"]
            sx = nx * TILE - self.camera_x
            sy = ny * TILE - self.camera_y
            draw_npc_simple(self.screen, sx, sy, npc.get("color", ORANGE))

        # Draw player
        px = self.player_x * TILE - self.camera_x
        py = self.player_y * TILE - self.camera_y
        draw_player(self.screen, px, py, self.player_dir)

        # HUD
        map_name = self.font.render(m["name"], True, WHITE)
        name_bg = pygame.Rect(4, 4, map_name.get_width() + 12, 22)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), name_bg)
        pygame.draw.rect(self.screen, WHITE, name_bg, 1)
        self.screen.blit(map_name, (10, 6))

        # Party indicator
        for i, r in enumerate(self.party):
            ball_x = SCREEN_W - 20 - i * 18
            color = GREEN if r.hp > 0 else RED
            pygame.draw.circle(self.screen, color, (ball_x, 14), 6)
            pygame.draw.circle(self.screen, BLACK, (ball_x, 14), 6, 1)

        # Textbox
        self.textbox.draw(self.screen, SCREEN_W, SCREEN_H)

    def _draw_pause_menu(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))

        menu_w, menu_h = 200, 175
        mx = SCREEN_W - menu_w - 10
        my = 10
        menu_rect = pygame.Rect(mx, my, menu_w, menu_h)
        pygame.draw.rect(self.screen, WHITE, menu_rect)
        pygame.draw.rect(self.screen, BLACK, menu_rect, 3)

        options = ["RODENTS", "SAVE", "BADGES", "SETTINGS", "BACK"]
        for i, opt in enumerate(options):
            y = my + 10 + i * 30
            color = BLACK
            text = self.font.render(opt, True, color)
            self.screen.blit(text, (mx + 30, y))
            if i == self.menu_cursor:
                pygame.draw.polygon(self.screen, BLACK,
                    [(mx + 12, y + 3), (mx + 12, y + 15), (mx + 22, y + 9)])

        # Content area
        content_rect = pygame.Rect(10, 10, SCREEN_W - menu_w - 30, SCREEN_H - 20)
        pygame.draw.rect(self.screen, WHITE, content_rect)
        pygame.draw.rect(self.screen, BLACK, content_rect, 2)

        if self.menu_cursor == 0:  # Party
            title = self.font.render("Your Rodents:", True, BLACK)
            self.screen.blit(title, (20, 20))
            for i, r in enumerate(self.party):
                y = 50 + i * 65
                draw_rodent_sprite(self.screen, r.species, 20, y - 10, 48)
                info = self.font.render(f"{r.nickname} Lv.{r.level}", True, BLACK)
                self.screen.blit(info, (75, y))
                hp = self.small_font.render(f"HP: {r.hp}/{r.max_hp}  ATK:{r.effective_atk()} DEF:{r.effective_def()} SPD:{r.spd}", True, DARK_GREY)
                self.screen.blit(hp, (75, y + 20))
                type_t = self.small_font.render(f"Type: {r.type}  Moves: {', '.join(r.moves)}", True, DARK_GREY)
                self.screen.blit(type_t, (75, y + 36))

        elif self.menu_cursor == 2:  # Badges
            title = self.font.render("Badges:", True, BLACK)
            self.screen.blit(title, (20, 20))
            if self.badges:
                for i, b in enumerate(self.badges):
                    bt = self.font.render(f"- {b}", True, DARK_GREY)
                    self.screen.blit(bt, (30, 50 + i * 25))
            else:
                nb = self.font.render("No badges yet!", True, DARK_GREY)
                self.screen.blit(nb, (30, 50))

            money_t = self.font.render(f"Money: ${self.money}", True, BLACK)
            self.screen.blit(money_t, (20, 140))

        elif self.menu_cursor == 3:  # Settings preview (read-only)
            self._draw_settings(interactive=False)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    game = Game()
    game.run()
