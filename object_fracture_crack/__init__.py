# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Cell Fracture Crack It",
    "author": "Nobuyuki Hirakata",
    "version": (0, 2, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Toolshelf > Create Tab",
    "description": "Displaced Cell Fracture Addon",
    "warning": "Make sure to enable 'Object: Cell Fracture' Addon",
    "wiki_url": "https://wiki.blender.org/index.php/Extensions:2.6/"
                "Py/Scripts/Object/CrackIt",
    "category": "Object"
}

if 'bpy' in locals():
    import importlib
    importlib.reload(operator)

else:
    from . import operator

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        )
import os


class CrackItProperties(PropertyGroup):
    # Input on toolshelf before execution
    # In Panel subclass, In bpy.types.Operator subclass,
    # reference them by context.scene.crackit

    fracture_source = EnumProperty(
            name="From",
            description="Position for origin of crack",
            items=[('PARTICLE_OWN', "Own Particles", "All particle systems of the source object"),
                   ('VERT_OWN', "Own Verts", "Use own vertices"),
                   ('VERT_CHILD', "Child Verts", "Use child object vertices"),
                   ('PARTICLE_CHILD', "Child Particles", "All particle systems of the child objects"),
                   ('PENCIL', "Grease Pencil", "This object's grease pencil"),
                   ],
            default='VERT_OWN'
            )
    fracture_div = IntProperty(
            name="Crack Limit",
            description="Max Crack",
            default=4,
            min=1,
            max=5000
            )
    fracture_recursion = IntProperty(
            name="Recursion",
            description="Recursion",
            default=0,
            min=0,
            max=5
            )
    pre_simplify = FloatProperty(
            name="Simplify Base Mesh",
            description="Simplify base mesh before making crack. Lower face size, faster calculation.",
            default=0.00,
            min=0.00,
            max=1.00
            )            
    # Path of the addon
    material_addonpath = os.path.dirname(__file__)
    # Selection of material preset
    # Note: you can choose the original name in the library blend
    # or the prop name
    material_preset = EnumProperty(
            name="Preset",
            description="Material Preset",
            items=[
                ('crackit_organic_mud', "Organic Mud", "Mud material"),
                ('crackit_mud', "Mud", "Mud material"),
                ('crackit_tree_moss', "Tree Moss", "Tree Material"),
                ('crackit_tree_dry', "Tree Dry", "Tree Material"),
                ('crackit_tree_red', "Tree Red", "Tree Material"),
                ('crackit_rock', "Rock", "Rock Material"),
                ('crackit_lava', "Lava", "Lava Material"),
                ('crackit_wet-paint', "Wet Paint", "Paint Material"),
                ('crackit_soap', "Soap", "Soap Material"),
                ]
            )
    material_lib_name = BoolProperty(
            name="Library Name",
            description="Use the original Material name from the .blend library\n"
                        "instead of the one defined in the Preset",
            default=True
            )


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.crackit = PointerProperty(
                                    type=CrackItProperties
                                    )


def unregister():
    del bpy.types.Scene.crackit
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
