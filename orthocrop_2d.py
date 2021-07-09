'''
Copyright (C) 2021 Malek El-Tannir
malek.e.tannir@makelek.com

Created by Malek El-Tannir

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
import mathutils
import math


def init_vars():

    bpy.types.Object.block_margin = bpy.props.IntProperty(
        name="Block Margin", default=2,
        description="Margin in grid blocks around the object.",
        soft_min=0, soft_max=8, step=1)

    # Block size in Units
    bpy.types.Scene.block_size = bpy.props.FloatProperty(
        name="Block Size", default=0.1,
        description="Block size in unit scale",
        soft_min=0.1, soft_max=10, step=0.1)

    bpy.types.Scene.block_ortho_scale = bpy.props.FloatProperty(
        name="Reference Ortho Scale", default=6.0,
        description="Ortho scale at which blocks have their full resolution",
        soft_min=1, soft_max=20, step=1.0)

    bpy.types.Scene.orthocrop_set_origin = bpy.props.BoolProperty(
        name="Center Origin", default=True,
        description="Set the origin to the center of the bounding "
                    "box over all frames \nwhen initializing and "
                    "setting width and height")

    bpy.types.Scene.orthocrop_overwrite = bpy.props.BoolProperty(
        name="Overwrite Properties", default=True,
        description="Recalculate width and height")


def remove_vars():
    del bpy.types.Object.block_margin
    del bpy.types.Scene.block_size
    del bpy.types.Scene.block_ortho_scale
    del bpy.types.Scene.orthocrop_set_origin
    del bpy.types.Scene.orthocrop_overwrite


def crop_to_active(context):

    w = context.active_object["Width"]
    h = context.active_object["Height"]
    blocksize = context.scene.block_size

    obj_pos = context.active_object.location
    cam = context.scene.camera
    resolution_factor = cam.data.ortho_scale / context.scene.block_ortho_scale
    cam_pos = cam.location
    obj_vec = mathutils.Vector((obj_pos.x, obj_pos.z))
    cam_vec = mathutils.Vector((cam_pos.x, cam_pos.z))
    scene_res_x = context.scene.render.resolution_x
    scene_res_y = context.scene.render.resolution_y

    if scene_res_y < scene_res_x:
        aspect = scene_res_y / scene_res_x
        blocks_x = (cam.data.ortho_scale)/blocksize
        blocks_y = (aspect * cam.data.ortho_scale)/blocksize
    else:
        aspect = scene_res_x / scene_res_y
        blocks_x = (aspect*cam.data.ortho_scale)/blocksize
        blocks_y = (cam.data.ortho_scale)/blocksize

    diff_obj_cam = obj_vec-cam_vec
    diff_offset = -mathutils.Vector((blocks_x/2.0, blocks_y/2.0))
    diff_offset += mathutils.Vector((w/2, h/2))
    cam_pos.xz += diff_obj_cam + diff_offset*blocksize

    render = context.scene.render
    render.resolution_percentage = 100*resolution_factor

    blocksize_x = 1.0/blocks_x
    blocksize_y = 1.0/blocks_y
    block_margin = context.object.block_margin
    margin_x = block_margin*blocksize_x
    margin_y = block_margin*blocksize_y

    # Camera Postion accounts for Margin
    cam_pos.xz += mathutils.Vector(
        (block_margin/2.0, block_margin/2.0))*blocksize
    render.border_max_x = 1
    render.border_max_y = 1
    render.border_min_x = render.border_max_x - (margin_x + w * blocksize_x)
    render.border_min_y = render.border_max_y-(margin_y+h*blocksize_y)


def set_custom_properties(context, overwrite: bool):
    """Sets custom width and height as the objects custom properties.
    function(context,overwrite) -> void
    Keyword arguments:
    context -- the blender context
    overwrite -- true overwrite already existing properties
    """
    obj = context.active_object
    min_x = math.inf
    min_z = math.inf
    max_x = -math.inf
    max_z = -math.inf
    blocksize = context.scene.block_size

    if obj.type == "GPENCIL":
        for layer in obj.data.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    for point in stroke.points:
                        v = point.co

                        if v.x > max_x:
                            max_x = v.x
                        if v.z > max_z:
                            max_z = v.z

                        if v.x < min_x:
                            min_x = v.x
                        if v.z < min_z:
                            min_z = v.z

    else:
        for i in range(8):
            v = mathutils.Vector(obj.bound_box[i])
            v.resize_4d()
            if v.x > max_x:
                max_x = v.x
            if v.x < min_x:
                min_x = v.x

            if v.z > max_z:
                max_z = v.z
            if v.z < min_z:
                min_z = v.z

    if overwrite:
        obj["Width"] = max(round(abs(min_x - max_x) / blocksize), 1)
        obj["Height"] = max(round(abs(min_z - max_z) / blocksize), 1)
    else:
        if "Width" not in obj.keys():
            obj["Width"] = max(round(abs(min_x-max_x)/blocksize), 1)
        if "Height" not in obj.keys():
            obj["Height"] = max(round(abs(min_z-max_z)/blocksize), 1)
    # Also sets the objects origin of so chosen
    if (context.scene.orthocrop_set_origin):
        context.scene.cursor.location.x = min_x+abs(min_x-max_x)/2.0
        context.scene.cursor.location.z = min_z+abs(min_z-max_z)/2.0
        context.scene.cursor.location = \
            obj.matrix_world @ context.scene.cursor.location
        context.scene.cursor.location.y = obj.location.y
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")


class SetCustomPropertiesOperator(bpy.types.Operator):
    """Set custom properties for cropping \n"""\
        """Object is expected to be on y = 0"""
    bl_idname = "object.set_custom_properties"
    bl_label = "Set Width & Height"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        set_custom_properties(context, context.scene.orthocrop_overwrite)
        return {'FINISHED'}


class CropToActiveOperator(bpy.types.Operator):
    """Crops camera renderer to active object"""\
        """ bounding box from the top right of the view.\n"""\
        """Custom properties "Width" and "Height" must be set before. \n"""\
        """Make sure the camera is looking towards positive y"""
    bl_idname = "object.crop_to_active"
    bl_label = "Crop to Active"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        crop_to_active(context)
        return {'FINISHED'}


class CropToActivePanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Orthocrop 2D"
    bl_idname = "OBJECT_PT_crop_to_active"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        if context.scene.camera.data.type == "ORTHO":
            row = layout.row()
            row.operator("object.crop_to_active")

            row = layout.row()
            row.prop(context.scene, "orthocrop_set_origin")
            row.prop(context.scene, "orthocrop_overwrite")

            row = layout.row()
            row.operator("object.set_custom_properties")
            # row.operator("object.overwrite_custom_properties")

            row = layout.row()
            row.prop(context.object, "block_margin")
            row.prop(context.scene, "block_size")

            row = layout.row()
            row.prop(context.scene, "block_ortho_scale")
        else:
            row = layout.row()
            row.label(
                text="The scene camera needs to be in orthographic mode.")
