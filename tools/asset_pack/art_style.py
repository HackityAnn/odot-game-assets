"""Shared game art settings. Pure Python; safe to import in fast tests and tools."""
from dataclasses import dataclass
import math
import re
from types import MappingProxyType

STYLE_ID = 'soft_painted_fantasy_v1'
PAINTED_VERSION = 'painted_softness_v1'


@dataclass(frozen=True)
class MaterialStyle:
    color: tuple
    roughness: float = .84
    metallic: float = 0
    emission: float = 0

    def __post_init__(self):
        if len(self.color) != 3 or not all(math.isfinite(c) and 0 <= c <= 1 for c in self.color):
            raise ValueError('Material colors must be three finite sRGB channels in [0, 1]')
        if not all(math.isfinite(v) and 0 <= v <= 1 for v in (self.roughness, self.metallic)):
            raise ValueError('Roughness and metallic must be in [0, 1]')
        if not math.isfinite(self.emission) or self.emission < 0:
            raise ValueError('Emission must be finite and nonnegative')


def srgb_to_linear(color):
    return tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in color)


def material_name(name):
    return re.sub(r'\.\d+$', '', name)


FAMILY_PREFIXES = (
    ('crystal', 'crystal'), ('mushroom', 'mushroom'), ('forest_leaf', 'leaf'),
    ('leaf', 'leaf'), ('grass', 'ground'), ('moss', 'moss'), ('pine', 'leaf'),
    ('wood', 'wood'), ('bark', 'wood'), ('roof', 'roof'), ('stone', 'stone'),
    ('wall', 'plaster'), ('gill_glow', 'gill'), ('window', 'window'), ('water', 'water'),
)
NORMAL_FAMILIES = frozenset(('wood', 'stone', 'leaf', 'plaster', 'roof'))


def material_family(name):
    name = material_name(name)
    return next((family for prefix, family in FAMILY_PREFIXES if name.startswith(prefix)), None)


@dataclass(frozen=True)
class TextureStyle:
    size: int = 512
    crystal_size: int = 1024
    ground_size: int = 1024
    normal_relief: float = .12
    roughness_variation: float = .035
    roughness_min: float = .12
    roughness_max: float = .94
    color_space: str = 'sRGB'
    data_space: str = 'Non-Color'
    uv_name: str = 'PaintedUV'
    contact_strength: float = .28
    bounce_strength: float = .13
    bounce_emission: float = .07

    def __post_init__(self):
        for size in (self.size, self.crystal_size, self.ground_size):
            if not isinstance(size, int) or size < 1 or size & (size - 1):
                raise ValueError('Texture sizes must be positive powers of two')
        if not 0 <= self.roughness_min <= self.roughness_max <= 1:
            raise ValueError('Invalid texture roughness bounds')

    def size_for(self, family):
        return self.crystal_size if family == 'crystal' else self.size


@dataclass(frozen=True)
class GeometryStyle:
    bevel_width: float = .025
    bevel_segments: int = 2
    stone_bevel_width: float = .008
    stone_bevel_angle: float = .38
    crystal_sides: int = 5
    mushroom_sides: int = 32
    footprint_tolerance: float = .025
    pivot_tolerance: float = .000001
    export_tolerance: float = .005

    def __post_init__(self):
        if self.crystal_sides < 3 or self.mushroom_sides < 8 or self.bevel_segments < 1:
            raise ValueError('Invalid facet or bevel segment count')


@dataclass(frozen=True)
class HexStyle:
    radius: float = 2.55
    surface: float = 0
    bottom: float = -.36
    bank_cut: float = .46
    water_width: float = .91
    water_center: float = -.18
    water_thickness: float = .025

    def __post_init__(self):
        if not math.isfinite(self.radius) or self.radius <= 0 or self.bottom >= self.surface:
            raise ValueError('Hex needs a positive radius and a foundation below its surface')

    @property
    def half_height(self):
        return math.sqrt(3) * self.radius / 2

    @property
    def spacing_x(self):
        return 1.5 * self.radius

    @property
    def spacing_y(self):
        return 2 * self.half_height

    def contains(self, x, y, tolerance=0):
        return (abs(y) <= self.half_height + tolerance and
                math.sqrt(3) * abs(x) + abs(y) <= math.sqrt(3) * self.radius + tolerance)


@dataclass(frozen=True)
class PreviewStyle:
    resolution: int = 1200
    samples: int = 64
    threads: int = 4
    engine: str = 'CYCLES'
    transform: str = 'AgX'
    look: str = 'AgX - Medium High Contrast'
    world_color: tuple = (.20, .22, .25)
    world_strength: float = .32
    glare_threshold: float = .8
    glare_strength: float = .18
    glare_size: float = .25


@dataclass(frozen=True)
class LightStyle:
    name: str
    position: tuple
    energy: float
    size: float
    color: tuple


@dataclass(frozen=True)
class UnitStyle:
    fps: int = 24
    bone_count: int = 19
    forward: str = '-Y'
    sockets: tuple = ('weapon_socket.L', 'weapon_socket.R')
    rounded_materials: tuple = ('skin', 'face_dark', 'leather', 'leather_light', 'magic')


TEXTURES = TextureStyle()
GEOMETRY = GeometryStyle()
HEX = HexStyle()
PREVIEW = PreviewStyle()
UNITS = UnitStyle()
CLIP_FRAMES = MappingProxyType({'idle': 48, 'walk': 24, 'run': 18, 'attack': 24, 'hit': 12, 'death': 30})
LOOP_CLIPS = frozenset(('idle', 'walk', 'run'))
LIGHTS = (
    LightStyle('Warm key', (-3, -4, 8), 1012, 5.2, (1, .86, .69)),
    LightStyle('Soft sky', (5, -1, 5), 533, 5, (.72, .83, 1)),
    LightStyle('Leaf rim', (1, 5, 7), 1000, 4, (1, .94, .73)),
)

BASE_COLORS = {'wood': (0.43, 0.245, 0.115),
 'wood_light': (0.64, 0.385, 0.19),
 'wood_edge': (0.73, 0.47, 0.255),
 'wood_dark': (0.255, 0.145, 0.085),
 'bark': (0.4, 0.205, 0.095),
 'bark_light': (0.51, 0.285, 0.115),
 'stone': (0.54, 0.54, 0.51),
 'stone_light': (0.66, 0.65, 0.59),
 'stone_dark': (0.39, 0.41, 0.4),
 'wall': (0.81, 0.76, 0.62),
 'wall_light': (0.9, 0.85, 0.72),
 'shadow': (0.105, 0.075, 0.07),
 'grass': (0.54, 0.68, 0.2),
 'grass_light': (0.67, 0.76, 0.28),
 'grass_dark': (0.36, 0.51, 0.125),
 'leaf': (0.4, 0.6, 0.14),
 'leaf_light': (0.57, 0.72, 0.18),
 'leaf_dark': (0.28, 0.44, 0.105),
 'pine': (0.25, 0.43, 0.14),
 'pine_light': (0.34, 0.52, 0.18),
 'soil': (0.29, 0.28, 0.235),
 'base': (0.28, 0.29, 0.29),
 'roof_red': (0.74, 0.255, 0.125),
 'roof_red_light': (0.87, 0.36, 0.18),
 'roof_red_dark': (0.61, 0.18, 0.09),
 'roof_blue': (0.19, 0.39, 0.55),
 'roof_blue_light': (0.29, 0.49, 0.66),
 'roof_blue_dark': (0.13, 0.29, 0.43),
 'blue': (0.15, 0.34, 0.75),
 'blue_light': (0.25, 0.47, 0.94),
 'blue_dark': (0.09, 0.2, 0.48),
 'purple': (0.4, 0.18, 0.62),
 'purple_light': (0.58, 0.3, 0.78),
 'purple_dark': (0.24, 0.11, 0.39),
 'green': (0.29, 0.48, 0.14),
 'green_light': (0.42, 0.62, 0.2),
 'green_dark': (0.17, 0.33, 0.09),
 'skin': (0.96, 0.69, 0.35),
 'skin_light': (1, 0.78, 0.47),
 'leather': (0.34, 0.205, 0.115),
 'leather_light': (0.46, 0.29, 0.16),
 'silver': (0.7, 0.74, 0.79),
 'silver_light': (0.88, 0.89, 0.87),
 'silver_dark': (0.4, 0.45, 0.5),
 'gold': (0.96, 0.65, 0.15),
 'gold_light': (1, 0.79, 0.3),
 'cream': (0.99, 0.92, 0.73),
 'red': (0.82, 0.18, 0.11),
 'mushroom': (0.55, 0.23, 0.83),
 'black': (0.07, 0.047, 0.04),
 'face_dark': (0.19, 0.095, 0.24),
 'flower': (0.94, 0.88, 0.73),
 'window': (1, 0.64, 0.075),
 'magic': (0.86, 0.19, 1)}

PAINTED_COLORS = {'wood': (0.36, 0.18, 0.075),
 'wood_light': (0.56, 0.3, 0.12),
 'wood_edge': (0.74, 0.43, 0.18),
 'wood_dark': (0.17, 0.085, 0.035),
 'bark': (0.28, 0.13, 0.055),
 'bark_light': (0.43, 0.23, 0.085),
 'roof_blue': (0.08, 0.27, 0.48),
 'roof_blue_light': (0.15, 0.38, 0.64),
 'roof_blue_dark': (0.055, 0.18, 0.34),
 'wall': (0.67, 0.63, 0.5),
 'wall_light': (0.83, 0.78, 0.63),
 'stone': (0.48, 0.5, 0.49),
 'stone_light': (0.56, 0.57, 0.54),
 'stone_dark': (0.39, 0.42, 0.42),
 'grass': (0.48, 0.63, 0.18),
 'grass_light': (0.58, 0.7, 0.24),
 'grass_dark': (0.32, 0.48, 0.12),
 'moss': (0.36, 0.53, 0.13),
 'forest_leaf': (0.32, 0.53, 0.16),
 'forest_leaf_light': (0.46, 0.63, 0.2),
 'crystal_cyan': (0.08, 0.7, 0.96),
 'crystal_blue': (0.16, 0.48, 0.86),
 'crystal_light': (0.32, 0.86, 1),
 'crystal_purple': (0.47, 0.27, 0.82),
 'crystal_lilac': (0.64, 0.43, 0.93),
 'mushroom_blue': (0.24, 0.35, 0.76),
 'mushroom_purple': (0.49, 0.25, 0.74)}

PAINTED_ACCENTS = {'carved_shadow': ((0.16, 0.2, 0.19), 0),
 'stone_edge': ((0.67, 0.69, 0.61), 0),
 'crystal_edge': ((0.24, 0.84, 1), 1.2),
 'magic_core': ((0.38, 0.94, 1), 3),
 'window': ((1, 0.43, 0.045), 2.6),
 'window_hot': ((1, 0.82, 0.18), 2.1),
 'window_shade': ((0.69, 0.2, 0.012), 0.65),
 'gill_glow': ((0.23, 0.78, 0.87), 1.05),
 'rune_glow': ((0.24, 0.86, 1), 2.0),
 'water': ((0.025, 0.41, 0.55), 0.15),
 'water_light': ((0.14, 0.75, 0.89), 0.65)}

BASE_MATERIALS = MappingProxyType({
    name: MaterialStyle(color, .42 if name.startswith('silver') else .78,
                        .35 if name.startswith('silver') else .10 if name.startswith('gold') else 0,
                        1.5 if name == 'window' else 2.5 if name == 'magic' else 0)
    for name, color in BASE_COLORS.items()
})
PAINTED_MATERIALS = MappingProxyType({
    **{name: MaterialStyle(color, .23 if name.startswith('crystal') else .84,
                          emission=1.2 if name.startswith('crystal') else .08 if name.startswith('mushroom') else 0)
       for name, color in PAINTED_COLORS.items()},
    **{name: MaterialStyle(color, .75, emission=emission)
       for name, (color, emission) in PAINTED_ACCENTS.items()},
})
