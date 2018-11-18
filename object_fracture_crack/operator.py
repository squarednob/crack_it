# gpl: author Nobuyuki Hirakata

import bpy
from bpy.types import (
        Operator,
        Panel,
        )
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty
        )
from . import crack_it


def check_object_cell_fracture():
    if "object_fracture_cell" in bpy.context.user_preferences.addons.keys():
        return True
    return False


# Access by bpy.ops.mesh.crackit_fracture
class FractureOperation(Operator):
    bl_idname = "mesh.crackit_fracture"
    bl_label = "1.Crack"
    bl_description = ("Make cracks using the cell fracture add-on\n"
                      "Needs only one Selected Mesh Object")
    bl_options = {'REGISTER', 'UNDO'}
    
    pre_simplify = FloatProperty(
            name="Simplify Base Mesh",
            description="Simplify base mesh before making crack. Lower face size, faster calculation.",
            default=0.00,
            min=0.00,
            max=1.00
            )        
    fracture_div = IntProperty(
            name="Crack Limit",
            description="Crack Limit",
            default=4,
            min=1,
            max=5000
            )
    join_location = FloatProperty(
            name="Change Loation",
            description="Location X",
            default=2.5,
            min=-50,
            max=50
            )
    fracture_noise = FloatProperty(
            name="Random Crack Point",
            description="Random Crack point",
            default=0.00,
            min=0.00,
            max=1.00
            )            
    fracture_scalex = FloatProperty(
            name="Scale X",
            description="Scale X",
            default=0.00,
            min=0.00,
            max=1.00
            )
    fracture_scaley = FloatProperty(
            name="Scale Y",
            description="Scale Y",
            default=0.00,
            min=0.00,
            max=1.00
            )
    fracture_scalez = FloatProperty(
            name="Scale Z",
            description="Scale Z",
            default=0.00,
            min=0.00,
            max=1.00
            )
    fracture_margin = FloatProperty(
            name="Margin Size",
            description="Margin Size",
            default=0.001,
            min=0.000,
            max=1.000
            )
    fracture_edge_split = BoolProperty(
            name="Split Edge",
            description="Split Edge",
            default=True
            )
    fracture_edge_sharp = BoolProperty(
            name="Flatten",
            description="Sharp Edges",
            default=False
            )    
    fracture_recursion = IntProperty(
            name="Recursion",
            description="Recursion",
            default=0,
            min=0,
            max=5
            )
    fracture_recur_maxdiv = IntProperty(
            name="Recursion_Limit Crack",
            description="Recursion Limit Crack",
            default=8,
            min=1,
            max=100
            )
    fracture_recur_clamp = IntProperty(
            name="Recursion Clamp",
            description="Recursion Clamp",
            default=250,
            min=0,
            max=1000
            )
    fracture_recur_chance = FloatProperty(
            name="Recursion Chance",
            description="Recursion Chance",
            default=0.25,
            min=0.00,
            max=1.00
            )
    fracture_recur_chance_select = EnumProperty(
            name = "Recursion Chance Select",
            description = "Recursion Chance Select",
            items = [('RANDOM', "Random", "Random"),
                     ('SIZE_MIN', "Small", "Small"),
                     ('SIZE_MAX', "Big", "Big"),
                     ('CURSOR_MIN', "Cursor Close", "Cursor Close"),
                     ('CURSOR_MAX', "Cursor Far", "Cursor Far")]
            )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        sel_obj = len(context.selected_objects) == 1

        return (obj is not None and obj.type == "MESH" and sel_obj)
    
    def execute(self, context):
        if check_object_cell_fracture():
            crackit = context.scene.crackit
            original_obj =  bpy.context.scene.objects.active
            
            # Grease pencil setting
            if crackit.fracture_source == 'PENCIL':
                try:
                    crack_it.grease_pencil_setting()
                except Exception as e:
                    crack_it.error_handlers(
                            self, "mesh.crackit_fracture", e, "Detecting Grease Pencil was failed. "
                            "Set pencil source to 'OBJECT' from 'SCENE' and set parent. "
                            )
                    crackit.fracture_source = 'PARTICLE_OWN'
                    return {"PASS_THROUGH"}
            
            # Make Crack
            try:
                crack_it.simplifyOriginal(self.pre_simplify)
                bpy.ops.object.add_fracture_cell_objects(
                    source={crackit.fracture_source}, source_limit=self.fracture_div+1,
                    source_noise=self.fracture_noise,
                    cell_scale=(1-self.fracture_scalex, 1-self.fracture_scaley, 1-self.fracture_scalez),
                    recursion=self.fracture_recursion, recursion_source_limit=self.fracture_recur_maxdiv,
                    recursion_clamp=self.fracture_recur_clamp, recursion_chance=self.fracture_recur_chance,
                    recursion_chance_select=self.fracture_recur_chance_select, use_smooth_faces=False,
                    use_sharp_edges=self.fracture_edge_sharp, use_sharp_edges_apply=self.fracture_edge_split,
                    use_data_match=True, use_island_split=False, margin=self.fracture_margin,
                    material_index=0, use_interior_vgroup=False, mass_mode='VOLUME', mass=1,
                    use_recenter=True, use_remove_original=True, use_layer_index=0, use_layer_next=False,
                    group_name="", use_debug_points=False, use_debug_redraw=False, use_debug_bool=False
                    )
                cracked_obj = crack_it.makeJoin(self, original_loc=self.join_location)
                crack_it.desimplifyOriginal(original_obj=original_obj, cracked_obj=cracked_obj)
                crack_it.addModifiers()
                
                
            except Exception as e:
                crack_it.error_handlers(
                        self, "mesh.crackit_fracture", e, "Crack It! could not be completed."
                        )
                return {"CANCELLED"}
        else:
            self.report({'WARNING'},
                        "Depends on Object: Cell Fracture addon. Please enable it first. "
                        "Operation Cancelled"
                        )
            return {"CANCELLED"}

        return {'FINISHED'}
    
    def invoke(self, context, event):
        crackit = context.scene.crackit
        # Integrate Props in __init__.py into props in the class
        self.fracture_div = crackit.fracture_div
        self.fracture_recursion = crackit.fracture_recursion
        self.pre_simplify = crackit.pre_simplify
        return self.execute(context)
        

# Access by bpy.ops.mesh.crackit_surface
class SurfaceOperation(Operator):
    bl_idname = "mesh.crackit_surface"
    bl_label = "2.Surface"
    bl_description = ("Post Processing after making basic crack")
    bl_options = {'REGISTER', 'UNDO'}
    
    modifier_decimate = FloatProperty(
        name="SImplify",
        description="Modifier Decimate",
        default=0.40,
        min=0.00,
        max=1.00
        )
    modifier_smooth = FloatProperty(
            name="Loose | Tight",
            description="Modifier Smooth",
            default=-0.50,
            min=-3.00,
            max=3.00
            )
    extrude_scale = FloatProperty(
            name="Extrude Blob",
            description="Extrude Scale",
            default=0.00,
            min=0.00,
            max=5.00
            )
    extrude_var = FloatProperty(
            name="Extrude Random ",
            description="Extrude Var",
            default=0.01,
            min=-4.00,
            max=4.00
            )
    extrude_num = IntProperty(
            name="Extrude Num",
            description="Extrude Num",
            default=1,
            min=0,
            max=10
            )
    modifier_wireframe = BoolProperty(
            name="Wireframe Modifier",
            description="Wireframe Modifier",
            default=False
            )             
           
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        sel_obj = len(context.selected_objects) == 1

        return (obj is not None and obj.type == "MESH" and sel_obj)
    
    def execute(self, context):
        if check_object_cell_fracture():
            crackit = context.scene.crackit
            try:
                bpy.context.object.modifiers['DECIMATE_crackit'].ratio = self.modifier_decimate
                bpy.context.object.modifiers['SMOOTH_crackit'].factor = self.modifier_smooth
                crack_it.multiExtrude(
                    off=0.1,
                    rotx=0, roty=0, rotz=0,
                    sca=self.extrude_scale,
                    var1=self.extrude_var, var2=self.extrude_var, var3=self.extrude_var,
                    num=self.extrude_num, ran=0
                    )
                bpy.ops.object.shade_smooth()
                if self.modifier_wireframe == True:
                    bpy.ops.object.modifier_add(type='WIREFRAME')
                    wireframe = bpy.context.object.modifiers[-1]
                    wireframe.name = 'WIREFRAME_crackit'
                    wireframe.use_even_offset = False
                    wireframe.thickness = 0.01
                
            except Exception as e:
                crack_it.error_handlers(
                        self, "mesh.crackit_surface", e, "Crack It! could not be completed."
                        )
                return {"CANCELLED"}
        else:
            self.report({'WARNING'},
                        "Please Crack object first. "
                        "Operation Cancelled"
                        )
            return {"CANCELLED"}

        return {'FINISHED'}
    

# Apply material preset
# Access by bpy.ops.mesh.crackit_material
class MaterialOperation(Operator):
    bl_idname = "mesh.crackit_material"
    bl_label = "3.Material"
    bl_description = ("Apply a preset material\n"
                      "The Material will be applied to the Active Object\n"
                      "from the type of Mesh, Curve, Surface, Font, Meta")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        # included - type that can have materials
        included = ['MESH', 'CURVE', 'SURFACE', 'FONT', 'META']
        return (obj is not None and obj.type in included)

    def execute(self, context):
        crackit = context.scene.crackit
        mat_name = crackit.material_preset
        mat_lib_name = crackit.material_lib_name
        mat_ui_name = crack_it.get_ui_mat_name(mat_name) if not mat_lib_name else mat_name

        try:
            crack_it.appendMaterial(
                    crackit = crackit,
                    addon_path=crackit.material_addonpath,
                    material_name=mat_name,
                    mat_ui_names=mat_ui_name
                    )
        except Exception as e:
            crack_it.error_handlers(
                    self, "mesh.crackit_material", e,
                    "The active Object could not have the Material {} applied".format(mat_ui_name)
                    )
            return {"CANCELLED"}

        return {'FINISHED'}


# Menu settings
class crackitPanel(Panel):
    bl_label = "Crack it!"
    bl_idname = 'crack_it'
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Create"
    bl_context = 'objectmode'
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        crackit = context.scene.crackit
        layout = self.layout
        
        # 1.Crack section
        box = layout.box()
        col = box.column(align=True)
        col.label("1.Crack Setting:")
        col.prop(crackit, "fracture_source")
        col.prop(crackit, "pre_simplify")
        col.prop(crackit, "fracture_div")               
        col.prop(crackit, "fracture_recursion") 
        col = box.column(align=True)
        # Warning if the fracture cell addon is not enabled
        if not check_object_cell_fracture():
            col = box.column()
            col.label(text="Please enable Object: Cell Fracture addon", icon="INFO")
            col.separator()
            col.operator("wm.addon_userpref_show",
                         text="Go to Cell Fracture addon",
                         icon="PREFERENCES").module = "object_fracture_cell"

            layout.separator()
            return
        else:
            col.operator(FractureOperation.bl_idname, icon="SPLITSCREEN")
        
        # 2.Surface secion
        col.separator()
        col.label("2.Surface Setting:")
        col.operator(SurfaceOperation.bl_idname, icon="FREEZE")
        
        # 3.material Preset
        box = layout.box()
        col = box.column(align=True)
        row = col.row()
        row.label("3.Material Preset:")
        row_sub = row.row()
        row_sub.prop(crackit, "material_lib_name", text="",
                     toggle=True, icon="LONGDISPLAY")
        row = box.row()
        row.prop(crackit, "material_preset")

        row = box.row()
        row.operator(MaterialOperation.bl_idname, icon="MATERIAL_DATA")
