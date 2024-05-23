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
        material = active.active_material

        if material and not material.use_nodes:
            material.use_nodes = True

        return active.active_material
    
    else:
        return None
    

def createImageNode(mat, node_name, node_image = 'null'):

    if mat:
        nodes = mat.node_tree.nodes
        image_node = nodes.new(type = 'ShaderNodeTexImage')
        image_node.name = node_name
        if bpy.data.images.get(node_image):
            image_node.image = bpy.data.images.get(node_image)
        else:
            print("Unable to find image " + node_image + "for " + node_name)
            return -1
        image_node.location = (0, 0)
        return 0
    else:
        print("Failed to create as material" + mat.name + "is null")
        return -1
    
    # node_locations = {
    #     "NormalTextureSampler": (-300, 300),
    #     "DiffuseTextureSampler": (-300, 0),
    #     "AoMapTextureSampler": (-300, -300),
    #     "ScratchTextureSampler": (-600, 300),
    #     "LightmapLightsTextureSampler": (-600, 0),
    #     "CrackedGlassTextureSampler": (-600, -300),
    #     "CrackedGlassNormalTextureSampler": (500, 300),
    #     "EmissiveTextureSampler": (500, 0),
    #     "CrumpleTextureSampler": (500, -300),
    #     "ExternalNormalTextureSampler": (800, 300),
    #     "InternalNormalTextureSampler": (800, 0),
    #     "DisplacementSampler": (800, -300),
    #     "DiffuseSampler": (800, -600),
    #     "BlurNormalTextureSampler": (500, -600),
    #     "BlurDiffuseTextureSampler": (200, -600),
    #     "SpecularAndAOTextureSampler": (-100, -600),
    #     "BlurSpecularAndAOTextureSampler": (-400, -600),
    # }
    # image_node.location = node_locations.get(node_name, (0, 0))


def createMaterialCustomProperty(mat, name, values):
    if name not in mat:
        mat[name] = values  #Values should be array of size 4
    else:
        print(name + "already exists in Material: " + mat.name)
        return -1

    #arigato
    if name in ('DirtTint', 'materialDiffuse', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour',
                'LightmappedLightsRedChannelColour', 'window_Tint', 'pearlescentColour', 'ReversingColour', 'UnusedColour',
                'mCrackedGlassSpecularColour', 'BrakeColour', 'RunningColour', 'mGlassColour', 'OverlayA_Diffuse', 'DiffuseB',
                'OverlayB_Diffuse', 'DiffuseA', 'Colour', 'gEmissiveColour', 'tiling1Diffuse', 'tiling3Diffuse', 'tiling2Diffuse',
                'decal_Diffuse', 'mMaterialDiffuse', 'Line_Diffuse', 'DiffuseColour', 'EmissiveColour', 'algaeColour', 'mExternalGlassColour'):
        
        property_manager = mat.id_properties_ui(name)
        property_manager.update(subtype='COLOR')

    return 0


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
        layout.menu("SUB_MENU_MATERIAL_VEHICLE", icon = "MATERIAL")

class SUB_MENU_MATERIAL_VEHICLE(bpy.types.Menu):

    bl_idname = "SUB_MENU_MATERIAL_VEHICLE"
    bl_label = "Vehicle Material Templates"

    def draw(self, context):
        layout = self.layout
        layout.operator("mat_veh.glass")
        layout.operator("mat_veh.glassred")


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
    

class material_Glass(bpy.types.Operator):

    bl_idname = "mat_veh.glass"
    bl_label = "Glass"
    bl_description = "Material for glass."

    def execute(self, context):

        status = 0
        mat = getMaterial()

        if mat:
            mat["shader_type"] = "Vehicle_Glass_Emissive_Coloured"
            mat.name = "Glass_" + mat.name

            status += createImageNode(mat, "EmissiveTextureSampler", '89_20_8C_6D.dds')
            status += createImageNode(mat, "CrackedGlassTextureSampler", 'BE_12_78_F1.dds')
            status += createImageNode(mat, "CrackedGlassNormalTextureSampler", '52_5D_C3_15.dds')

            status += createMaterialCustomProperty(mat, "BrakeColour", [0.25, 0.0, 0.0, 1.0])
            status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
            status += createMaterialCustomProperty(mat, "ReversingColour", [1.0, 1.0, 1.0, 1.0])
            status += createMaterialCustomProperty(mat, "RunningColour", [0.07035999745130539, 0.07035999745130539, 0.07035999745130539, 1.0])
            status += createMaterialCustomProperty(mat, "UnusedColour", [0.0, 0.0, 0.0, 1.0])
            status += createMaterialCustomProperty(mat, "mCrackedGlassSpecularColour", [0.19599999487400055, 0.6549999713897705, 0.7879999876022339, 1.0])
            status += createMaterialCustomProperty(mat, "mCrackedGlassSpecularControls", [0.10999999940395355, 3.5, 1.0, 0.0])
            status += createMaterialCustomProperty(mat, "mGlassColour", [0.0, 0.0, 0.0, 1.0])
            status += createMaterialCustomProperty(mat, "mGlassControls", [0.03999999910593033, 1.0, 3.0, 0.9900000095367432])
            status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])

        if status == 0:
            self.report({'INFO'}, "Successfully applied material template Glass to selected material.")
        else:
            self.report({'ERROR'}, "An error has occured. Please check console log for more information.")

        return {'FINISHED'}


class material_GlassRed(bpy.types.Operator):

    bl_idname = "mat_veh.glassred"
    bl_label = "GlassRed (Taillight Glass)"
    bl_description = "Material for taillight glass (edited to be red)."

    def execute(self, context):

        status = 0
        mat = getMaterial()

        if mat:
            mat["shader_type"] = "Vehicle_Glass_Emissive_Coloured"
            mat.name = "GlassRed_" + mat.name

            status += createImageNode(mat, "EmissiveTextureSampler", '89_20_8C_6D.dds')
            status += createImageNode(mat, "CrackedGlassTextureSampler", 'BE_12_78_F1.dds')
            status += createImageNode(mat, "CrackedGlassNormalTextureSampler", '52_5D_C3_15.dds')

            status += createMaterialCustomProperty(mat, "BrakeColour", [0.25, 0.0, 0.0, 1.0])
            status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
            status += createMaterialCustomProperty(mat, "ReversingColour", [1.0, 1.0, 1.0, 1.0])
            status += createMaterialCustomProperty(mat, "RunningColour", [0.0822829976677895, 0.00367700005881488, 0.00439100014045835, 1.0])
            status += createMaterialCustomProperty(mat, "UnusedColour", [0.0, 0.0, 0.0, 1.0])
            status += createMaterialCustomProperty(mat, "mCrackedGlassSpecularColour", [0.19599999487400055, 0.6549999713897705, 0.7879999876022339, 1.0])
            status += createMaterialCustomProperty(mat, "mCrackedGlassSpecularControls", [0.10999999940395355, 3.5, 1.0, 0.0])
            status += createMaterialCustomProperty(mat, "mGlassColour", [1.0, 0.0, 0.0, 1.0])
            status += createMaterialCustomProperty(mat, "mGlassControls", [0.0149999996647239, 0.600000023841858, 3.0, 0.800000011920929])
            status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])

        if status == 0:
            self.report({'INFO'}, "Successfully applied material template Glass to selected material.")
        else:
            self.report({'ERROR'}, "An error has occured. Please check console log for more information.")

        return {'FINISHED'}


register_classes = (
    MAIN_MENU_HP_EXPORTER_PLUGINS,
    SUB_MENU_CAR,
    SUB_MENU_MATERIAL_VEHICLE,
    Initialize_Scene,
    Assign_Empty,
    material_Glass,
    material_GlassRed,
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
        
        

        
        
        
