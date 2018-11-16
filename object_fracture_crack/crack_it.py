# gpl: author Nobuyuki Hirakata

import bpy

import bmesh
from random import (
        gauss,
        seed,
        )
from math import radians, pi
from mathutils import Euler


# Allow changing the original material names from the .blend file
# by replacing them with the UI Names from the EnumProperty
def get_ui_mat_name(mat_name):
    mat_ui_name = "CrackIt Material"
    try:
        # access the Scene type directly to get the name from the enum
        mat_items = bpy.types.Scene.crackit[1]["type"].bl_rna.material_preset[1]["items"]
        for mat_id, mat_list in enumerate(mat_items):
            if mat_name in mat_list:
                mat_ui_name = mat_items[mat_id][1]
                break
        del mat_items
    except Exception as e:
        error_handlers(
                False, "get_ui_mat_name", e,
                "Retrieving the EnumProperty key UI Name could not be completed", True
                )
        pass

    return mat_ui_name

# error_type='ERROR' for popup massage
def error_handlers(self, op_name, error, reports="ERROR", func=False, error_type='WARNING'):
    if self and reports:
        self.report({error_type}, reports + " (See Console for more info)")

    is_func = "Function" if func else "Operator"
    print("\n[Cell Fracture Crack It]\n{}: {}\nError: "
          "{}\nReport: {}\n".format(is_func, op_name, error, reports))

          
# -------------------- Crack -------------------
# Cell fracture and post-process:
# Setting before crack from grease pencil
def grease_pencil_setting():
    obj = bpy.context.object
    sce = bpy.context.scene
    sce.tool_settings.grease_pencil_source = 'OBJECT'
    if sce.grease_pencil and not obj.grease_pencil:
        obj.grease_pencil = sce.grease_pencil
    if obj.grease_pencil:
        obj.grease_pencil.layers[0].parent = obj
    else:
        print("Detecting Grease Pencil was failed. "
              "Set pencil source to 'OBJECT' from 'SCENE' and set parent.")

def simplifyOriginal(simplify):
    bpy.ops.object.modifier_add(type='DECIMATE')
    decimate = bpy.context.object.modifiers[-1]
    decimate.name = 'DECIMATE_crackit_original'
    decimate.ratio = 1-simplify

def desimplifyOriginal(original_obj, cracked_obj):
    bpy.context.scene.objects.active = original_obj
    if 'DECIMATE_crackit_original' in bpy.context.object.modifiers.keys():
         bpy.ops.object.modifier_remove(modifier='DECIMATE_crackit_original')
    bpy.context.scene.objects.active = cracked_obj

# Join fractures into an object
def makeJoin(self, original_loc):
    # Get active object name and active layer
    active_name = bpy.context.scene.objects.active.name
    active_layer = bpy.context.scene.active_layer

    # Get object by name
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern=active_name + '_cell*')
    fractures = bpy.context.selected_objects

    if fractures:
        # Execute join
        bpy.context.scene.objects.active = fractures[0]
        fractures[0].select = True
        bpy.ops.object.join()
    else:
        error_handlers(
            self, "_makeJoin", "if fractures condition has not passed",
            "Warning: No objects could be joined.\nIt can happen with too big margin: 0.20-1.00",
            True, error_type='ERROR'
            )
        # Duplicate ojbect
        bpy.ops.object.select_pattern(pattern=active_name)
        bpy.ops.object.duplicate_move(TRANSFORM_OT_translate={"value":(2, 0, 0)})      

    # Change name
    bpy.context.scene.objects.active.name = active_name + '_crack'
    # Change origin
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
    # Change location to avoid overlap of two objects
    new_location = bpy.context.object.location.copy()
    new_location[0] += original_loc
    bpy.context.scene.objects.active.location = new_location
    
    return bpy.context.scene.objects.active


# Add modifier and setting
def addModifiers(decimate_val=0.4, smooth_val=0.5):
    bpy.ops.object.modifier_add(type='DECIMATE')
    decimate = bpy.context.object.modifiers[-1]
    decimate.name = 'DECIMATE_crackit'
    #decimate.decimate_type = 'DISSOLVE'
    decimate.ratio = decimate_val
    #decimate.angle_limit = decimate_val*pi

    bpy.ops.object.modifier_add(type='SUBSURF')
    subsurf = bpy.context.object.modifiers[-1]
    subsurf.name = 'SUBSURF_crackit'

    bpy.ops.object.modifier_add(type='SMOOTH')
    smooth = bpy.context.object.modifiers[-1]
    smooth.name = 'SMOOTH_crackit'
    smooth.factor = smooth_val
   

# -------------- multi extrude --------------------
# var1=random offset, var2=random rotation, var3=random scale
def multiExtrude(off=0.1, rotx=0, roty=0, rotz=0, sca=0.0,
                var1=0.01, var2=0.01, var3=0.01, num=1, ran=0):

    obj = bpy.context.object
    bpy.context.tool_settings.mesh_select_mode = [False, False, True]

    # bmesh operations
    bpy.ops.object.mode_set()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    sel = [f for f in bm.faces if f.select]

    # faces loop
    for i, of in enumerate(sel):
        rot = _vrot(r=i, ran=ran, rotx=rotx, var2=var2, roty=roty, rotz=rotz)
        off = _vloc(r=i, ran=ran, off=off, var1=var1)
        of.normal_update()

        # extrusion loop
        for r in range(num):
            nf = of.copy()
            nf.normal_update()
            no = nf.normal.copy()
            ce = nf.calc_center_bounds()
            s = _vsca(r=i + r, ran=ran, var3=var3, sca=sca)

            for v in nf.verts:
                v.co -= ce
                v.co.rotate(rot)
                v.co += ce + no * off
                v.co = v.co.lerp(ce, 1 - s)

            # extrude code from TrumanBlending
            for a, b in zip(of.loops, nf.loops):
                sf = bm.faces.new((a.vert, a.link_loop_next.vert,
                                   b.link_loop_next.vert, b.vert))
                sf.normal_update()

            bm.faces.remove(of)
            of = nf

    for v in bm.verts:
        v.select = False

    for e in bm.edges:
        e.select = False

    bm.to_mesh(obj.data)
    obj.data.update()


def _vloc(r, ran, off, var1):
    seed(ran + r)
    return off * (1 + gauss(0, var1 / 3))


def _vrot(r, ran, rotx, var2, roty, rotz):
    seed(ran + r)
    return Euler((radians(rotx) + gauss(0, var2 / 3),
                radians(roty) + gauss(0, var2 / 3),
                radians(rotz) + gauss(0, var2 / 3)), 'XYZ')


def _vsca(r, ran, sca, var3):
    seed(ran + r)
    return sca * (1 + gauss(0, var3 / 3))


# Centroid of a selection of vertices
def _centro(ver):
    vvv = [v for v in ver if v.select]
    if not vvv or len(vvv) == len(ver):
        return ('error')

    x = sum([round(v.co[0], 4) for v in vvv]) / len(vvv)
    y = sum([round(v.co[1], 4) for v in vvv]) / len(vvv)
    z = sum([round(v.co[2], 4) for v in vvv]) / len(vvv)

    return (x, y, z)


# Retrieve the original state of the object
def _volver(obj, copia, om, msm, msv):
    for i in copia:
        obj.data.vertices[i].select = True
    bpy.context.tool_settings.mesh_select_mode = msm

    for i in range(len(msv)):
        obj.modifiers[i].show_viewport = msv[i]


# -------------- Material preset --------------------------
def appendMaterial(addon_path, material_name, mat_ui_names="Nameless Material"):
    # Load material from the addon directory
    file_path = _makeFilePath(addon_path=addon_path)
    bpy.ops.wm.append(filename=material_name, directory=file_path)

    # If material is loaded some times, select the last-loaded material
    last_material = _getAppendedMaterial(material_name)

    if last_material:
        mat = bpy.data.materials[last_material]
        # skip renaming if the prop is True
        if not bpy.context.scene.crackit.material_lib_name:
            mat.name = mat_ui_names

        # Apply Only one material in the material slot
        for m in bpy.context.object.data.materials:
            bpy.ops.object.material_slot_remove()

        bpy.context.object.data.materials.append(mat)

        return True

    return False


# Make file path of addon
def _makeFilePath(addon_path):
    material_folder = "/materials"
    blend_file = "/materials1.blend"
    category = "\\Material\\"

    file_path = addon_path + material_folder + blend_file + category
    return file_path


# Get last-loaded material, such as ~.002
def _getAppendedMaterial(material_name):
    # Get material name list
    material_names = [m.name for m in bpy.data.materials if material_name in m.name]
    if material_names:
        # Return last material in the sorted order
        material_names.sort()

        return material_names[-1]

    return None
