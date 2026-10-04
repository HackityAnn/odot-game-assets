"""Real Blender fixtures and GLB round trips; all generated files are temporary."""
from dataclasses import replace
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import numpy as np
import art_style as style
import characters
import forest_kit
import geometry as g
import painted_finish as paint
import reference_finish as finish
import style_blender
from style_validation import asset_violations, material_violations, preview_violations


class BlenderStyleTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        g.M.clear();characters.WEIGHTS.clear()
        g.palette();finish.palette()
        self.col=g.collection('fixture');g.target(self.col)
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)
        root=patch.object(g,'ROOT',self.directory);root.start();self.addCleanup(root.stop)
        # Smaller fixture maps exercise the same path without writing real assets.
        maps=patch.object(style,'TEXTURES',replace(style.TEXTURES,size=64,crystal_size=128,ground_size=128))
        maps.start();self.addCleanup(maps.stop)

    def painted_cube(self):
        obj=g.cube('Stone fixture',(0,0,.5),(1,1,1),'stone')
        paint.apply(self.col)
        return obj

    def assert_clean(self):
        self.assertEqual(asset_violations(list(self.col.objects),'environment',painted=True),[])

    def test_shared_palette_is_applied_to_principled_bsdf(self):
        for name in ['stone','wood','crystal_cyan','window']:
            spec=style.PAINTED_MATERIALS[name]
            shader=next(n for n in g.M[name].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
            for actual,expected in zip(shader.inputs['Base Color'].default_value[:3],style.srgb_to_linear(spec.color),strict=True):
                self.assertAlmostEqual(actual,expected,places=6)
            self.assertAlmostEqual(shader.inputs['Roughness'].default_value,spec.roughness,places=6)

    def test_studio_uses_shared_preview_and_is_idempotent(self):
        g.studio()
        scene=bpy.context.scene
        self.assertEqual(preview_violations(scene),[])
        count=len(bpy.data.node_groups)
        before={obj.name:obj.data.energy for obj in scene.objects if obj.type=='LIGHT'}
        finish.studio_finish();style_blender.preview(scene)
        self.assertEqual(count,len(bpy.data.node_groups))
        self.assertEqual(before,{obj.name:obj.data.energy for obj in scene.objects if obj.type=='LIGHT'})
        self.assertEqual(preview_violations(scene),[])

    def test_preview_check_detects_a_small_hard_key_light(self):
        g.studio()
        bpy.data.objects['Warm key'].data.size=.1
        self.assertTrue(any('Warm key' in error for error in preview_violations(bpy.context.scene)))

    def test_stone_edges_do_not_duplicate_modifiers(self):
        obj=g.ico('Stone fixture',(0,0,0),(1,1,1),'stone',2)
        finish.rock_finish(obj);finish.rock_finish(obj)
        self.assertEqual([mod.type for mod in obj.modifiers],['BEVEL','WEIGHTED_NORMAL'])
        self.assertAlmostEqual(obj.modifiers[0].width,style.GEOMETRY.stone_bevel_width,places=6)
        self.assertTrue(obj.modifiers[0].harden_normals)

    def test_crystal_builder_uses_configurable_facet_count_and_keeps_flat_normals(self):
        with patch.object(style,'GEOMETRY',replace(style.GEOMETRY,crystal_sides=7)):
            forest_kit.crystal()
            crystal=next(iter(self.col.objects))
            self.assertEqual(len(crystal.data.vertices),29)
            self.assertTrue(all(max(poly.vertices)<len(crystal.data.vertices) for poly in crystal.data.polygons))
        paint.apply(self.col);self.assert_clean()
        for poly in crystal.data.polygons:poly.use_smooth=True
        self.assertTrue(any('facet normals' in error for error in asset_violations(list(self.col.objects),'environment')))

    def test_mushroom_builder_and_checker_preserve_smooth_organic_normals(self):
        forest_kit.mushroom()
        paint.apply(self.col);self.assert_clean()
        cap=next(obj for obj in self.col.objects if obj.name.startswith('Broad faceted mushroom cap'))
        for poly in cap.data.polygons:poly.use_smooth=False
        self.assertTrue(any('organic surface normals' in error for error in asset_violations(list(self.col.objects),'environment')))

    def test_image_writer_encodes_color_once_and_leaves_normal_data_linear(self):
        value=style.srgb_to_linear((.5,.5,.5))
        color=paint.image_map('Midtone',np.full((8,8,3),value,dtype=np.float32),self.directory)
        data=paint.image_map('Normal data',np.full((8,8,3),.5,dtype=np.float32),self.directory,data=True)
        loaded=bpy.data.images.load(color.filepath,check_existing=False)
        self.assertAlmostEqual(loaded.pixels[0],.5,delta=2/255)
        self.assertAlmostEqual(data.pixels[0],.5,delta=2/255)
        self.assertEqual(color.colorspace_settings.name,style.TEXTURES.color_space)
        self.assertEqual(data.colorspace_settings.name,style.TEXTURES.data_space)

    def test_painted_maps_have_uvs_packing_and_color_spaces(self):
        obj=self.painted_cube();self.assert_clean()
        self.assertTrue(obj.data.uv_layers)
        self.assertTrue(all(image.packed_file for image in bpy.data.images if image.name.startswith('painted_')))

    def test_missing_normal_map_is_reported(self):
        obj=self.painted_cube()
        shader=next(n for n in obj.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        obj.data.materials[0].node_tree.links.remove(shader.inputs['Normal'].links[0])
        self.assertTrue(any('missing baked Normal' in error for error in material_violations(obj.data.materials[0],True)))

    def test_unused_principled_node_cannot_hide_an_unsupported_surface_shader(self):
        obj=self.painted_cube();mat=obj.data.materials[0]
        diffuse=mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        output=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL')
        mat.node_tree.links.new(diffuse.outputs[0],output.inputs['Surface'])
        self.assertTrue(any('Principled BSDF' in error for error in material_violations(mat,True)))

    def test_color_space_error_and_missing_uvs_are_reported(self):
        obj=self.painted_cube()
        normal=bpy.data.images['painted_stone_normal'];normal.colorspace_settings.name='sRGB'
        obj.data.uv_layers.remove(obj.data.uv_layers.active)
        errors=asset_violations(list(self.col.objects),'environment',painted=True)
        self.assertTrue(any('Non-Color' in error for error in errors))
        self.assertTrue(any('needs UVs' in error for error in errors))

    def test_receiving_ground_maps_are_checked_even_with_custom_material_names(self):
        obj=g.cube('Standard hex meadow top',(0,0,-.02),(2,2,.04),'grass')
        paint.apply(self.col);paint.ground(self.col,'fixture')
        self.assert_clean()
        mat=obj.material_slots[0].material;mat.name='Artist ground finish'
        shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        shader.inputs['Emission Color'].links[0].from_node.image.colorspace_settings.name='Non-Color'
        self.assertTrue(any('Emission Color needs sRGB' in error for error in material_violations(mat,True)))

    def test_hard_light_disk_and_shifted_root_are_reported(self):
        g.empty('fixture_root',(.1,0,0))
        g.cube('Crystal ground reflection',(0,0,0),(1,1,.01),'stone')
        errors=asset_violations(list(self.col.objects),'environment')
        self.assertTrue(any('receiving surface' in error for error in errors))
        self.assertTrue(any('pivot' in error for error in errors))

    def test_hex_builder_has_matching_river_endpoints_and_footprint(self):
        forest_kit.hex_stream()
        water=next(obj for obj in self.col.objects if obj.name=='Continuous river water')
        points=[vertex.co for vertex in water.data.vertices]
        self.assertAlmostEqual(max(p.y for p in points),style.HEX.half_height,places=6)
        self.assertAlmostEqual(min(p.y for p in points),-style.HEX.half_height,places=6)
        self.assertAlmostEqual(max(p.x for p in points)-min(p.x for p in points),style.HEX.water_width,places=6)
        root=g.empty('fixture_root')
        for key,value in [('hex_radius',style.HEX.radius),('grid_spacing_x',style.HEX.spacing_x),('grid_spacing_y',style.HEX.spacing_y)]:root[key]=value
        bpy.context.view_layer.update()
        self.assertEqual(asset_violations(list(self.col.objects),'environment'),[])
        water.data.vertices[0].co.x=style.HEX.radius*2
        self.assertTrue(any('footprint' in error for error in asset_violations(list(self.col.objects),'environment')))

    def test_unit_builder_uses_shared_clips_and_attachment_contract(self):
        rig=characters.create_rig(self.col)
        with patch.object(style,'CLIP_FRAMES',{clip:2 for clip in style.CLIP_FRAMES}):
            actions=characters.animate(rig,'knight')
            self.assertEqual(set(actions),set(style.CLIP_FRAMES))
            self.assertTrue(all(tuple(action.frame_range)==(1,3) for action in actions.values()))
        prop=g.empty('Sword grip')
        characters.equip(prop,rig,'weapon_socket.R',(0,0,1))
        self.assertEqual(asset_violations(list(self.col.objects),'characters'),[])
        rig.data.bones['weapon_socket.R'].use_deform=True
        self.assertTrue(any('weapon_socket.R' in error for error in asset_violations(list(self.col.objects),'characters')))

    def test_unit_checker_rejects_missing_clips_and_wrong_fps(self):
        characters.create_rig(self.col)
        bpy.context.scene.render.fps=30
        errors=asset_violations(list(self.col.objects),'characters',scene=bpy.context.scene)
        self.assertTrue(any('six animation clips' in error for error in errors))
        self.assertTrue(any('FPS' in error for error in errors))

    def test_painted_maps_and_uvs_survive_actual_glb_export(self):
        obj=self.painted_cube()
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        bpy.context.view_layer.objects.active=obj
        path=self.directory/'fixture.glb'
        bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_apply=True,export_animations=False)
        data=path.read_bytes();length=struct.unpack_from('<I',data,12)[0]
        document=json.loads(data[20:20+length])
        mat=document['materials'][0];pbr=mat['pbrMetallicRoughness']
        self.assertIn('baseColorTexture',pbr);self.assertIn('metallicRoughnessTexture',pbr)
        self.assertIn('normalTexture',mat)
        self.assertTrue(all('bufferView' in image for image in document['images']))
        self.assertTrue(all('TEXCOORD_0' in primitive['attributes'] for mesh in document['meshes'] for primitive in mesh['primitives']))


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(BlenderStyleTests))
    if not result.wasSuccessful():raise RuntimeError('Blender art style regression tests failed')
