"""Fast contract tests for the shared art configuration; no Blender dependency."""
from dataclasses import FrozenInstanceError, replace
import math
import unittest

from tools.asset_pack import art_style as style


class ArtStyleTests(unittest.TestCase):
    def test_invalid_colors_and_material_parameters_are_rejected(self):
        for color in [(1, 0), (1.1, 0, 0), (math.nan, 0, 0)]:
            with self.subTest(color=color), self.assertRaises(ValueError):
                style.MaterialStyle(color)
        for parameters in [{'roughness': 2}, {'metallic': -.1}, {'emission': -1}]:
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                style.MaterialStyle((.5, .5, .5), **parameters)

    def test_family_matching_handles_library_suffixes_and_unknown_materials(self):
        for name, family in [('forest_leaf_light.014', 'leaf'), ('wood_dark.003', 'wood'),
                             ('crystal_purple', 'crystal'), ('wall_light', 'plaster'),
                             ('window_shade.002', 'window'), ('skin', None), ('artist_custom', None)]:
            self.assertEqual(style.material_family(name), family)
        self.assertEqual(style.material_name('wood.variant.001'), 'wood.variant')

    def test_srgb_conversion_does_not_double_encode_midtones(self):
        linear = style.srgb_to_linear((0, .5, 1))
        self.assertEqual(linear[0], 0)
        self.assertAlmostEqual(linear[1], .21404114048)
        self.assertEqual(linear[2], 1)

    def test_presets_are_immutable_and_can_be_replaced_explicitly(self):
        with self.assertRaises(FrozenInstanceError):
            style.TEXTURES.size = 256
        with self.assertRaises(TypeError):
            style.CLIP_FRAMES['walk'] = 100
        custom = replace(style.TEXTURES, crystal_size=2048)
        self.assertEqual(custom.size_for('crystal'), 2048)
        self.assertEqual(custom.size_for('wood'), style.TEXTURES.size)

    def test_invalid_texture_and_geometry_settings_fail_early(self):
        for options in [{'size': 0}, {'crystal_size': 1000}, {'roughness_min': .9, 'roughness_max': .3}]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                replace(style.TEXTURES, **options)
        with self.assertRaises(ValueError):
            replace(style.GEOMETRY, crystal_sides=2)

    def test_hex_boundary_accepts_edges_and_rejects_outside_points(self):
        for i in range(6):
            a=i*math.tau/6
            self.assertTrue(style.HEX.contains(style.HEX.radius*math.cos(a),style.HEX.radius*math.sin(a),1e-8))
        self.assertFalse(style.HEX.contains(style.HEX.radius+.01,0))
        self.assertFalse(style.HEX.contains(0,style.HEX.half_height+.01))
        self.assertFalse(style.HEX.contains(style.HEX.radius*.9,style.HEX.half_height*.9))
        self.assertAlmostEqual(style.HEX.spacing_y,math.sqrt(3)*style.HEX.radius)

    def test_replaced_hex_dimensions_keep_neighbor_spacing_coherent(self):
        custom=replace(style.HEX,radius=3)
        self.assertEqual(custom.spacing_x,4.5)
        self.assertAlmostEqual(custom.spacing_y,math.sqrt(3)*3)
        with self.assertRaises(ValueError):replace(style.HEX,bottom=1)

    def test_shared_palettes_have_valid_native_principled_values(self):
        for palette in [style.BASE_MATERIALS,style.PAINTED_MATERIALS]:
            for material in palette.values():
                self.assertTrue(all(0<=c<=1 for c in material.color))
                self.assertTrue(0<=material.roughness<=1)
        self.assertTrue(style.LOOP_CLIPS<=style.CLIP_FRAMES.keys())
        self.assertTrue(all(frames>0 for frames in style.CLIP_FRAMES.values()))


if __name__=='__main__':unittest.main()
