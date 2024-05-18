bl_info = {
    "name": "NFSHP/NFSHPR Exporter Plugins",
    "author": "Enthuse",
    "version": (1, 0),
    "blender": (3, 6, 11),
    "location": "3D View > Add > HP Exporter Plugins",
    "description": "Makes your life easier while setting up scene for exporting HP/HPR models",
    "category": "Miscellaneous",
    "support": "COMMUNITY"
}

import bpy
import math
import os
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty


def clear_scene():

    for block in bpy.data.objects:
        #if block.users == 0:
            bpy.data.objects.remove(block, do_unlink=True)

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)

    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)

    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)

    for block in bpy.data.armatures:
        if block.users == 0:
            bpy.data.armatures.remove(block)

    for block in bpy.data.collections:
        if block.users == 0:
            bpy.data.collections.remove(block)
        else:
            bpy.data.collections.remove(block, do_unlink=True)
            
    return 0

    
def import_default_hp_textures():

    script_directory = os.path.dirname(__file__)
    directory = os.path.join(script_directory, "HP_DefaultTextures")

    if os.path.exists(directory) and os.path.isdir(directory):
        files = os.listdir(directory)
        dds_files = [f for f in files if f.endswith('.dds')]

        for dds_file in dds_files:
            filepath = os.path.join(directory, dds_file)
            bpy.ops.image.open(filepath=filepath)
            image = bpy.data.images.get(dds_file)
            image.is_shared_asset = True
    else:
        print("Could not find folder HP_DefaultTextures.")
        return -1
        
    return 0
        
        
def setup_vehicle_id(car_id):

    vehicle_collection_name = "VEH_" + car_id + "_MS"
    
    if vehicle_collection_name not in bpy.data.collections:
        vehicle_collection = bpy.data.collections.new(vehicle_collection_name)
        vehicle_collection["resource_type"] = "GraphicsSpec"
        
        #Sub-Collection (graphics)
        graphics_collection_name = car_id + "_Graphics"
        graphics_collection = bpy.data.collections.new(graphics_collection_name)
        graphics_collection["resource_type"] = "GraphicsSpec"
        vehicle_collection.children.link(graphics_collection)
        
        #Sub-Collection (wheels)
        wheels_collection_name = car_id + "_Wheels"
        wheels_collection = bpy.data.collections.new(wheels_collection_name)
        wheels_collection["resource_type"] = "WheelGraphicsSpec"
        vehicle_collection.children.link(wheels_collection)
        
        bpy.context.scene.collection.children.link(vehicle_collection)
    else:
        print("Collection already exists.")
        return -1
        
    return 0
        
        
def only_selected_mesh():

    return [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        
        
def apply_mesh_rotation():

    meshes = only_selected_mesh()
    
    #If no mesh selected
    if not meshes:
        print("No meshes are selected.")
        return -1
        
    #Perform check if all meshes fit criteria
    for mesh in meshes:
        if mesh.parent:
            print("Please make sure selected meshes are not linked to any parent.")
            return -1
            
        #Not sure why it doesn't really detect hidden meshes but whatever
        if mesh.hide_get():
            print("Please make sure selected meshes are not hidden.")
            return -1
        
    for mesh in meshes:
        #Apply transformation to mesh first before proceeding
        mesh.select_set(True)
        bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
        mesh.select_set(False)

        #Create parent
        empty_name = "Empty_" + mesh.name
        bpy.ops.object.empty_add(type = "PLAIN_AXES")
        empty = bpy.context.active_object
        empty.name = empty_name
        
        #Rotate mesh -90 deg
        mesh.rotation_euler = (math.radians(-90), 0.0, 0.0)
        mesh.select_set(True)
        bpy.ops.object.transform_apply(location = False, rotation = True, scale = False)
        
        #Assign parent, then rotate empty +90 deg
        empty.select_set(True)
        bpy.context.view_layer.objects.active = empty
        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = True)
        empty.rotation_euler = (math.radians(90), 0.0, 0.0)
        
        mesh.select_set(False)
        empty.select_set(False)
            
    return 0


def getMaterial():
    active = bpy.context.active_object

    if active and active.type == 'MESH':
        return active.active_material


#Main Menu
class MAIN_MENU_HP_EXPORTER_PLUGINS(bpy.types.Menu):
    
    bl_idname = "MAIN_MENU_HP_EXPORTER_PLUGINS"
    bl_label = "HP Exporter Plugins"
    
    def draw(self, context):
        layout = self.layout
        layout.menu("SUB_MENU_CAR", icon = "AUTO")
        
        
#Sub Menu
class SUB_MENU_CAR(bpy.types.Menu):

    bl_idname = "SUB_MENU_CAR"
    bl_label = "Vehicle"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("initialize.scene", icon = "OUTLINER_COLLECTION")
        layout.operator("assign.empty", icon = "EMPTY_AXIS")


#Operators
class Initialize_Scene(bpy.types.Operator):
    
    bl_idname = "initialize.scene"
    bl_label = "Prepare Collection"
    bl_description = "Creates a main collection for the vehicle while importing default textures"
    
    clear_scene: BoolProperty(
        name = "Clear Scene",
        description = "Deletes everything in scene",
        default = True,
    )
    
    import_default_textures : BoolProperty(
        name = "Import default Hot Pursuit Vehicle Textures",
        description = "Import the default textures in VEHICLETEX.BIN",
        default = True,
    )
    
    car_id : StringProperty(
        name = "Vehicle ID",
        description = "Enter the Car ID you wish to set the scene up for",
        default = "0",
    )
        
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False  # No animation.
        
        ##
        box = layout.box()
        split = box.split(factor=0.75)
        col = split.column(align=True)
        col.label(text="Preferences", icon="OPTIONS")
        
        box.prop(self, "clear_scene")
        box.prop(self, "import_default_textures")
        
        if self.clear_scene:
            box.prop(self, "car_id")
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width = 250)
    
    def execute(self, context):
        status = 0
    
        if self.clear_scene:
            status += clear_scene()
            status += setup_vehicle_id(self.car_id)
            
        if self.import_default_textures:
            status += import_default_hp_textures()
            
        if status == 0:
            self.report({'INFO'}, "Scene prepared.")
        else:
            self.report({'ERROR'}, "An error has occured. Please check console log for more information.")
            
        return {'FINISHED'}
        
        
class Assign_Empty(bpy.types.Operator):
    
    bl_idname = "assign.empty"
    bl_label = "Assign parent to selected mesh"
    bl_description = "Auto assign each mesh a parent with the correct rotation."
    
    only_selected: BoolProperty(
        name = "Only selected mesh",
        description = "Only assign parent to selected meshes",
        default = True,
    )
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False  # No animation.
        
        ##
        box = layout.box()
        split = box.split(factor=0.75)
        col = split.column(align=True)
        col.label(text="Preferences", icon="OPTIONS")
        
        box.prop(self, "only_selected")
        box.enabled = False
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width = 250)   
        
    def execute(self, context):
        status = 0
    
        if self.only_selected:
            status += apply_mesh_rotation()
            
        if status == 0:
            self.report({'INFO'}, "Parents applied to mesh.")
        else:
            self.report({'ERROR'}, "An error has occured. Please check console log for more information.")
            
        return {'FINISHED'}
        
        
register_classes = (
    MAIN_MENU_HP_EXPORTER_PLUGINS,
    SUB_MENU_CAR,
    Initialize_Scene,
    Assign_Empty,
)

def menu_func(self, context):
    self.layout.menu(MAIN_MENU_HP_EXPORTER_PLUGINS.bl_idname)


def register():
    for items in register_classes:
        bpy.utils.register_class(items)
    bpy.types.VIEW3D_MT_add.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    for items in register_classes:
        bpy.utils.unregister_class(items)
        
        

        
        
        