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
from bpy.props import BoolProperty, StringProperty, EnumProperty

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
            bpy.ops.image.open(filepath = filepath)
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
        image_node.location = (0, 0)

        if bpy.data.images.get(node_image):
            image_node.image = bpy.data.images.get(node_image)
        elif node_image == 'null':
            return 0
        else:
            print("Unable to find image " + node_image + " for " + node_name)
            return -1
        return 0
    else:
        print("Failed to create as " + mat.name + " is null")
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
        print(name + " already exists in Material: " + mat.name)
        return -1

    special_names = {'DirtTint', 'materialDiffuse', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour',
                'LightmappedLightsRedChannelColour', 'window_Tint', 'pearlescentColour', 'ReversingColour', 'UnusedColour',
                'mCrackedGlassSpecularColour', 'BrakeColour', 'RunningColour', 'mGlassColour', 'OverlayA_Diffuse', 'DiffuseB',
                'OverlayB_Diffuse', 'DiffuseA', 'Colour', 'gEmissiveColour', 'tiling1Diffuse', 'tiling3Diffuse', 'tiling2Diffuse',
                'decal_Diffuse', 'mMaterialDiffuse', 'Line_Diffuse', 'DiffuseColour', 'EmissiveColour', 'algaeColour', 'mExternalGlassColour'}
    
    if name in special_names:
        property_manager = mat.id_properties_ui(name)
        property_manager.update(subtype='COLOR')

    return 0

def material_Badge(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Greyscale_Textured_Normalmapped_Reflective"
        mat.name = "Badge_" + mat.name

        status += createImageNode(mat, "NormalTextureSampler", 'E7_A5_A4_93.dds')
        status += createImageNode(mat, "DiffuseTextureSampler")

        status += createMaterialCustomProperty(mat, "LightMultipliers", [3.0, 1.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [0.0010000000474974513, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mReflectionControls", [0.013000000268220901, 0.30000001192092896, 3.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.5, 1.0, 60.0, 1.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [0.0, 0.0, 0.0, 1.0])

    return status, "Badge"

def material_Glass(mat):

    status = 0

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

    return status, "Glass"

def material_GlassRed(mat):

    status = 0

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

    return status, "GlassRed"

def material_GlassLivery(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Glass_Emissive_Coloured_Singlesided_Wrap"
        mat.name = "GlassRed_" + mat.name

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

    return status, "GlassLivery"

def material_GlassSurround(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Glass_Emissive_Coloured_Singlesided_Wrap"
        mat.name = "GlassSurround_" + mat.name

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
        status += createMaterialCustomProperty(mat, "mGlassControls", [0.03999999910593033, 1.0, 3.5, 0.7400000095367432])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])

    return status, "GlassSurround"

def material_Grille(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_1Bit_Textured_NormalMapped_Emissive_AO_Livery"
        mat.name = "Grille_" + mat.name

        status += createImageNode(mat, "NormalTextureSampler", 'E7_A5_A4_93.dds')
        status += createImageNode(mat, "DiffuseTextureSampler")
        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "ScratchTextureSampler", '85_68_7E_F0.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", '89_20_8C_6D.dds')

        status += createMaterialCustomProperty(mat, "LightMultipliers", [60.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEmissiveAdditiveAmount", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mScratchSpecularControls", [0.009999999776482582, 0.15000000596046448, 5.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [0.0010000000474974513, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.04, 0.7, 35.0, 0.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [0.0, 0.0, 0.0, 1.0])

    return status, "Grille"

def material_Interior(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_Textured_Phong"
        mat.name = "Interior_" + mat.name

        status += createImageNode(mat, "DiffuseTextureSampler")

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [1.0, 0.699999988079071, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.0500000007450581, 0.850000023841858, 2.0, 1.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [0.00150000001303852, 0.0, 0.0, 0.0])

    return status, "Interior"

def material_InteriorEmissive(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_Textured_NormalMapped_Emissive_AO"
        mat.name = "InteriorEmissive_" + mat.name

        status += createImageNode(mat, "NormalTextureSampler", 'E7_A5_A4_93.dds')
        status += createImageNode(mat, "DiffuseTextureSampler")
        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", '89_20_8C_6D.dds')

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 1.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEmissiveAdditiveAmount", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.05000000074505806, 0.10000000149011612, 4.0, 0.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [1.0, 1.0, 1.0, 1.0])

    return status, "InteriorEmissive"

def material_Lights(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO"
        mat.name = "Lights_" + mat.name

        status += createImageNode(mat, "NormalTextureSampler", 'E7_A5_A4_93.dds')
        status += createImageNode(mat, "DiffuseTextureSampler")
        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", '89_20_8C_6D.dds')

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 1.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEmissiveAdditiveAmount", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mReflectionControls", [0.0099999997764825820, 0.5, 3.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.05000000074505806, 0.10000000149011612, 4.0, 0.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [1.0, 1.0, 1.0, 1.0])

    return status, "Lights"

def material_MetalChrome(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_Emissive_Reflective_AO"
        mat.name = "MetalChrome_" + mat.name

        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", '89_20_8C_6D.dds')

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 1.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEmissiveAdditiveAmount", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mReflectionControls", [0.0099999997764825820, 0.8500000238, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.05000000074505806, 0.10000000149011612, 4.0, 0.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [1.0, 1.0, 1.0, 1.0])

    return status, "MetalChrome"

def material_MetalColorable(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Wrap"
        mat.name = "MetalColorable_" + mat.name

        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "CrumpleTextureSampler", '11_BF_74_F7.dds')
        status += createImageNode(mat, "ScratchTextureSampler", '85_68_7E_F0.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", '89_20_8C_6D.dds')

        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mPaintColourIndex", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])

    return status, "MetalColorable"

def material_MetalHalfLivery(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Livery"
        mat.name = "MetalHalfLivery_" + mat.name

        status += createImageNode(mat, "DiffuseTextureSampler")
        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "CrumpleTextureSampler", '11_BF_74_F7.dds')
        status += createImageNode(mat, "ScratchTextureSampler", '85_68_7E_F0.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", '89_20_8C_6D.dds')

        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mPaintColourIndex", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])

    return status, "MetalHalfLivery"

def material_MetalLiveryCarbon(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride_Livery"
        mat.name = "MetalLiveryCarbon_" + mat.name

        status += createImageNode(mat, "DiffuseTextureSampler", '90_73_F3_CE.dds')
        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "CrumpleTextureSampler", '11_BF_74_F7.dds')
        status += createImageNode(mat, "ScratchTextureSampler", '85_68_7E_F0.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", '89_20_8C_6D.dds')

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 0.699999988079071, 1.0, 0.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mDiffuseFresnel", [1.5, 0.0, 4.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEmissiveAdditiveAmount", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEnvSpecularControls", [0.44999998807907104, 0.20000000298023224, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mPearlescentPower", [20.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mReflectionControls", [0.019999999552965164, 0.4000000059604645, 12.0, 0.0])
        status += createMaterialCustomProperty(mat, "mScratchSpecularControls", [0.4000000059604645, 0.15000000596046448, 50.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [3.0, 0.4000000059604645, 35.0, 0.9800000190734863])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "pearlescentColour", [1.0, 1.0, 1.0, 1.0])

    return status, "MetalLiveryCarbon"

def material_MetalLiveryGloss(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride_Livery"
        mat.name = "MetalLiveryGloss_" + mat.name

        status += createImageNode(mat, "DiffuseTextureSampler")
        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "CrumpleTextureSampler", '11_BF_74_F7.dds')
        status += createImageNode(mat, "ScratchTextureSampler", '85_68_7E_F0.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", '89_20_8C_6D.dds')

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 1.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mDiffuseFresnel", [1.0, 0.75, 5.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEmissiveAdditiveAmount", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEnvSpecularControls", [1.0, 0.20000000298023224, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mPearlescentPower", [4.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mReflectionControls", [0.0099999997764825820, 0.600000023841858, 5.0, 0.0])
        status += createMaterialCustomProperty(mat, "mScratchSpecularControls", [0.25, 0.25, 20.0, 0.20000000298023224])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.05000000074505806, 0.10000000149011612, 4.0, 1.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "pearlescentColour", [1.0, 1.0, 1.0, 1.0])

    return status, "MetalLiveryGloss"

def material_MetalLiveryMatte(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride_Livery"
        mat.name = "MetalLiveryMatte_" + mat.name

        status += createImageNode(mat, "DiffuseTextureSampler")
        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "CrumpleTextureSampler", '11_BF_74_F7.dds')
        status += createImageNode(mat, "ScratchTextureSampler", '85_68_7E_F0.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", '89_20_8C_6D.dds')

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 1.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mDiffuseFresnel", [1.0, 0.75, 5.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEmissiveAdditiveAmount", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEnvSpecularControls", [1.0, 0.20000000298023224, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "mPearlescentPower", [4.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mReflectionControls", [0.0, 0.0, 5.0, 0.0])
        status += createMaterialCustomProperty(mat, "mScratchSpecularControls", [0.25, 0.25, 20.0, 0.20000000298023224])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.100000001490116, 0.10000000149011612, 4.0, 1.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "pearlescentColour", [1.0, 1.0, 1.0, 1.0])

    return status, "MetalLiveryMatte"

def material_MetalSecondaryColouredLivery(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_Two_PaintGloss_Textured_LightmappedLights_Livery_Wrap"
        mat.name = "MetalSecondaryColouredLivery_" + mat.name

        status += createImageNode(mat, "DiffuseTextureSampler")
        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "CrumpleTextureSampler", '11_BF_74_F7.dds')
        status += createImageNode(mat, "ScratchTextureSampler", '85_68_7E_F0.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", '89_20_8C_6D.dds')

        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])

    return status, "MetalSecondaryColouredLivery"

def material_OpaqueDULL(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_Textured"
        mat.name = "OpaqueDULL_" + mat.name

        status += createImageNode(mat, "DiffuseTextureSampler")

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 1.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.05000000074505806, 0.10000000149011612, 4.0, 1.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [1.0, 1.0, 1.0, 1.0])

    return status, "OpaqueDULL"

def material_PlasticBlack(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_Textured_Phong"
        mat.name = "PlasticBlack_" + mat.name

        status += createImageNode(mat, "DiffuseTextureSampler", '89_20_8C_6D.dds')

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [1.0, 0.699999988079071, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.0500000007450581, 0.850000023841858, 2.0, 1.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [0.00150000001303852, 0.0, 0.0, 0.0])

    return status, "PlasticBlack"

def material_Mirror(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_Reflective"
        mat.name = "Mirror_" + mat.name

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 1.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [9.999999747378752e-06, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mReflectionControls", [1.0, 0.5, 3.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.05000000074505806, 0.10000000149011612, 4.0, 1.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [1.0, 1.0, 1.0, 1.0])

    return status, "Mirror"

def material_PlateRacer(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery"
        mat.name = "PlateRacer_" + mat.name
        
        status += createImageNode(mat, "NormalTextureSampler", '19_97_AA_7C.dds')
        status += createImageNode(mat, "DiffuseTextureSampler", '10_C3_82_CD.dds')
        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "ScratchTextureSampler", '85_68_7E_F0.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", 'E7_A5_A4_93.dds')

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 1.0, 1.0, 0.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [0.0010000000474974513, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEmissiveAdditiveAmount", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mReflectionControls", [0.009999999776482582, 0.009999999776482582, 3.0, 0.0])
        status += createMaterialCustomProperty(mat, "mScratchSpecularControls", [0.25, 0.25, 50.0, 0.10000000149011612])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [0.4, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.04, 0.7, 35.0, 0.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [1.0, 1.0, 1.0, 1.0])

    return status, "PlateRacer"

def material_PlateCop(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery"
        mat.name = "PlateCop_" + mat.name
        
        status += createImageNode(mat, "NormalTextureSampler", 'F9_E1_60_01.dds')
        status += createImageNode(mat, "DiffuseTextureSampler", '75_C5_BD_C5.dds')
        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "ScratchTextureSampler", '85_68_7E_F0.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", 'E7_A5_A4_93.dds')

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 1.0, 1.0, 0.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [0.0010000000474974513, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEmissiveAdditiveAmount", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mReflectionControls", [0.009999999776482582, 0.009999999776482582, 3.0, 0.0])
        status += createMaterialCustomProperty(mat, "mScratchSpecularControls", [0.25, 0.25, 50.0, 0.10000000149011612])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [0.4, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.04, 0.7, 35.0, 0.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [1.0, 1.0, 1.0, 1.0])

    return status, "PlateCop"

def material_InteriorBadge(mat):

    status = 0

    if mat:
        mat["shader_type"] = "Vehicle_1Bit_Textured_NormalMapped_Emissive_AO_Livery"
        mat.name = "InteriorBadge_" + mat.name

        status += createImageNode(mat, "NormalTextureSampler", 'E7_A5_A4_93.dds')
        status += createImageNode(mat, "DiffuseTextureSampler")
        status += createImageNode(mat, "AoMapTextureSampler", '13_94_2A_CA.dds')
        status += createImageNode(mat, "ScratchTextureSampler", '85_68_7E_F0.dds')
        status += createImageNode(mat, "LightmapLightsTextureSampler", '89_20_8C_6D.dds')

        status += createMaterialCustomProperty(mat, "LightMultipliers", [1.0, 1.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsBlueChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsGreenChannelColour", [1.0, 1.0, 1.0, 1.0])
        status += createMaterialCustomProperty(mat, "LightmappedLightsRedChannelColour", [1.0, 0.0, 0.0, 1.0])
        status += createMaterialCustomProperty(mat, "MaterialShadowMapBias", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mEmissiveAdditiveAmount", [0.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mScratchSpecularControls", [0.009999999776482582, 0.15000000596046448, 5.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSelfIlluminationMultiplier", [1.0, 0.0, 0.0, 0.0])
        status += createMaterialCustomProperty(mat, "mSpecularControls", [0.05, 0.5, 25.0, 0.0])
        status += createMaterialCustomProperty(mat, "materialDiffuse", [0.016807, 0.016807, 0.016807, 1.0])

    return status, "InteriorBadge"

#Main Menu
class EXPORTER_PLUGINS_MT_HPR(bpy.types.Menu):
    
    bl_idname = "EXPORTER_PLUGINS_MT_HPR"
    bl_label = "HP Exporter Plugins"
    
    def draw(self, context):
        layout = self.layout
        layout.menu("VEHICLE_SUBMENU_MT_HPR", icon = "AUTO")

#Sub Menu
class VEHICLE_SUBMENU_MT_HPR(bpy.types.Menu):

    bl_idname = "VEHICLE_SUBMENU_MT_HPR"
    bl_label = "Vehicle"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("initialize.scene", icon = "OUTLINER_COLLECTION")
        layout.operator("assign.empty", icon = "EMPTY_AXIS")
        layout.operator("material.vehicle", icon = "MATERIAL")

#Operators
class Initialize_Scene_OT_HPR(bpy.types.Operator):
    
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

        if self.clear_scene:
            box.prop(self, "car_id")

        row = box.row()
        row.enabled = False
        row.prop(self, "import_default_textures")
        
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
        
class Assign_Empty_OT_HPR(bpy.types.Operator):
    
    bl_idname = "assign.empty"
    bl_label = "Assign parent to selected mesh (Body only)"
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

class Material_Vehicles_OT_HPR(bpy.types.Operator):

    bl_idname = "material.vehicle"
    bl_label = "Vehicle Material Templates"
    bl_description = "Material templates for vehicles with pre-tuned values."

    enum_items = [
            ('Badge', "Badge", "Material for badges, which supports transparency"),
            ('Glass', "Glass", "Material for glass"),
            ('Glass_Red', "GlassRed (Taillight Glass)", "Material for taillight glass (Red)"),
            ('Glass_Livery', "GlassLivery", "Material for glass that supports wrap editing"),
            ('Glass_Surround', "GlassSurround", "Material for glass that surrounds the windshield, livery is supported"),
            ('Grille', "Grille", "Material for grille, which supports transparency"),
            ('Interior', "Interior", "Material for interior that doesn't support emissive nor transparency"),
            ('Interior_Emissive', "InteriorEmissive", "Material for emissives part in interior"),
            ('Lights', "Lights", "Material for lights"),
            ('Metal_Chrome', "MetalChrome", "Material for metallic chrome"),
            ('Metal_Colorable', "MetalColorable", "Material for vehicle paint which supports livery editing"),
            ('Metal_Half_Livery', "MetalHalfLivery", "Material that supports vehicle wrap, transparency area would be paint colour"),
            ('Metal_Livery_Carbon', "MetalLiveryCarbon", "Material for carbon fiber"),
            ('Metal_Livery_Gloss', "MetalLiveryGloss", "Material for glossy looking diffuse"),
            ('Metal_Livery_Matte', "MetalLiveryMatte", "Material for matte looking diffuse"),
            ('Metal_Secondary_Coloured_Livery', "MetalSecondaryColouredLivery", "Material for vehicle paint that has secondary colour setting"),
            ('Opaque_DULL', "OpaqueDULL", "Material for dull looking diffuse"),
            ('Plastic_Black', "PlasticBlack", "Material for pure black"),
            ('Mirror', "Mirror", "Material for mirrors"),
            ('Plate_Racer', "PlateRacer", "Material for racer variant license plate"),
            ('Plate_Cop', "PlateCop", "Material for cop variant license plate"),
            ('Interior_Badge', "InteriorBadge", "Material for interior badging for more details"),
        ]

    #sort list
    sorted_enum_items = sorted(enum_items, key = lambda item: item[1])

    enum_mat_name: bpy.props.EnumProperty(
        name = "Setting",
        description = "Choose a material template",
        items = sorted_enum_items
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
        
        box.prop(self, "enum_mat_name")
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width = 250)

    def execute(self, context):

        option_functions = {
            'Badge' : material_Badge,
            'Glass': material_Glass,
            'Glass_Red': material_GlassRed,
            'Glass_Livery' : material_GlassLivery,
            'Glass_Surround' : material_GlassSurround,
            'Grille' : material_Grille,
            'Interior' : material_Interior,
            'Interior_Emissive' : material_InteriorEmissive,
            'Lights' : material_Lights,
            'Metal_Chrome' : material_MetalChrome,
            'Metal_Colorable' : material_MetalColorable,
            'Metal_Half_Livery' : material_MetalHalfLivery,
            'Metal_Livery_Carbon' : material_MetalLiveryCarbon,
            'Metal_Livery_Gloss' : material_MetalLiveryGloss,
            'Metal_Livery_Matte' : material_MetalLiveryMatte,
            'Metal_Secondary_Coloured_Livery' : material_MetalSecondaryColouredLivery,
            'Opaque_DULL' : material_OpaqueDULL,
            'Plastic_Black' : material_PlasticBlack,
            'Mirror' : material_Mirror,
            'Plate_Racer' : material_PlateRacer,
            'Plate_Cop' : material_PlateCop,
            'Interior_Badge' : material_InteriorBadge,
        }

        status = 0
        mat = getMaterial()
        status, description = option_functions[self.enum_mat_name](mat)

        if status == 0:
            self.report({'INFO'}, f"Successfully applied material template \'{description}\' to selected material.")
        else:
            self.report({'ERROR'}, "An error has occured. Please check console log for more information.")
        
        return {'FINISHED'}

register_classes = (
    EXPORTER_PLUGINS_MT_HPR,
    VEHICLE_SUBMENU_MT_HPR,
    Initialize_Scene_OT_HPR,
    Assign_Empty_OT_HPR,
    Material_Vehicles_OT_HPR,
)

def menu_func(self, context):
    self.layout.menu(EXPORTER_PLUGINS_MT_HPR.bl_idname)

def register():
    for items in register_classes:
        bpy.utils.register_class(items)
    bpy.types.VIEW3D_MT_add.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    for items in register_classes:
        bpy.utils.unregister_class(items)