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
from . import orthocrop_2d as oc

bl_info = {
    "name": "Orthocrop 2D",
    "author": "Malek El-Tannir <malek.e.tannir@makelek.com>",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "category": "Camera",
    "location": "Object Properties",
    "description": "Crops and moves an orthographic camera onto the selected object.",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
}


def register():
    bpy.utils.register_class(oc.CropToActiveOperator)
    bpy.utils.register_class(oc.SetCustomPropertiesOperator)
    bpy.utils.register_class(oc.CropToActivePanel)

    oc.init_vars()


def unregister():
    bpy.utils.unregister_class(oc.CropToActiveOperator)
    bpy.utils.unregister_class(oc.SetCustomPropertiesOperator)
    bpy.utils.unregister_class(oc.CropToActivePanel)

    oc.remove_vars()
