"""Run only in an isolated Blender process; these tests never open or save sources."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
from mathutils import Euler, Matrix, Vector
import characters


class AttachmentTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        data=bpy.data.armatures.new('attachment_fixture')
        self.rig=bpy.data.objects.new('rig',data)
        bpy.context.scene.collection.objects.link(self.rig)
        bpy.context.view_layer.objects.active=self.rig
        self.rig.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for name,head,tail in [('head',(0,0,2),(0,.3,2.2)),
                               ('pelvis',(0,0,1),(0,.2,1.3)),
                               ('weapon_socket.R',(1,0,1),(1,.2,1))]:
            bone=data.edit_bones.new(name); bone.head=head; bone.tail=tail
        bpy.ops.object.mode_set(mode='OBJECT')
        self.rig.location=(.3,-.2,.5)
        self.rig.rotation_euler=(.1,.2,-.15)
        self.rig.scale=(1.1,1.1,1.1)
        self.prop=bpy.data.objects.new('scaled_skull',None)
        bpy.context.scene.collection.objects.link(self.prop)
        self.prop.scale=(.35,.21,.48)
        bpy.ops.mesh.primitive_cube_add(size=1)
        self.mesh=bpy.context.object
        self.mesh.parent=self.prop

    def attach(self,bone):
        location=(.1,-.2,1.9); rotation=(.2,-.3,.1)
        desired=(Matrix.Translation(Vector(location)) @ Euler(rotation).to_matrix().to_4x4()
                 @ Matrix.Diagonal((.35,.21,.48,1)))
        characters.equip(self.prop,self.rig,bone,location,rotation)
        bpy.context.view_layer.update()
        return desired

    def assert_matrix(self,actual,expected):
        self.assertLess(max(abs(actual[i][j]-expected[i][j])
                            for i in range(4) for j in range(4)),1e-5)

    def test_scaled_head_attachment_keeps_world_transform_and_geometry(self):
        desired=self.attach('head')
        self.assert_matrix(self.prop.matrix_world,desired)
        actual=self.mesh.matrix_world @ self.mesh.data.vertices[0].co
        expected=desired @ self.mesh.data.vertices[0].co
        self.assertLess((actual-expected).length,1e-5)
        self.assertTrue(self.rig.data.bones['head'].use_deform)

    def test_pelvis_attachment_keeps_deforming_bone(self):
        self.attach('pelvis')
        self.assertTrue(self.rig.data.bones['pelvis'].use_deform)

    def test_only_weapon_socket_becomes_non_deforming(self):
        self.attach('weapon_socket.R')
        self.assertFalse(self.rig.data.bones['weapon_socket.R'].use_deform)
        self.assertTrue(self.rig.data.bones['head'].use_deform)
        self.assertTrue(self.rig.data.bones['pelvis'].use_deform)

    def test_attachment_follows_animated_bone_without_changing_scale(self):
        desired=self.attach('head')
        tail=Matrix.Translation((0,self.rig.data.bones['head'].length,0))
        rest=self.rig.matrix_world @ self.rig.pose.bones['head'].matrix @ tail
        self.rig.pose.bones['head'].rotation_mode='XYZ'
        self.rig.pose.bones['head'].rotation_euler=(.4,.1,-.2)
        bpy.context.view_layer.update()
        animated=self.rig.matrix_world @ self.rig.pose.bones['head'].matrix @ tail
        self.assert_matrix(self.prop.matrix_world,animated @ rest.inverted() @ desired)
        self.assertLess((self.prop.matrix_basis.to_scale()-Vector((.35,.21,.48))).length,1e-5)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AttachmentTests))
    if not result.wasSuccessful(): raise RuntimeError('Attachment regression tests failed')
