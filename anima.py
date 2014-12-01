bl_info = {
        "name": "Anima",
        "description":"Custom animation panel for DaTinta Studio",
        "author":"mauriciovegaperez@hotmail.com",
        "version":(0,1),
        "blender":(2,72,0),
        "location":"UI panel",
        "warning":"Work in progress",
        "wiki_url":"",
        "category": "Animation"
        }


import bpy

### pose library
class Pose_library(bpy.types.Panel):
    bl_label = "Pose Library"
    bl_context = "posemode"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'    
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.pose)

    def draw(self, context):
        layout = self.layout

        ob = context.object
        poselib = ob.pose_library

        layout.template_ID(ob, "pose_library", new="poselib.new", unlink="poselib.unlink")

        if poselib:
            # list of poses in pose library
            row = layout.row()
            row.template_list("UI_UL_list", "pose_markers", poselib, "pose_markers",
                              poselib.pose_markers, "active_index", rows=5)

            # column of operators for active pose
            # - goes beside list
            col = row.column(align=True)
            col.active = (poselib.library is None)

            # invoke should still be used for 'add', as it is needed to allow
            # add/replace options to be used properly
            col.operator("poselib.pose_add", icon='ZOOMIN', text="")

            col.operator_context = 'EXEC_DEFAULT'  # exec not invoke, so that menu doesn't need showing

            pose_marker_active = poselib.pose_markers.active

            if pose_marker_active is not None:
                col.operator("poselib.pose_remove", icon='ZOOMOUT', text="")
                col.operator("poselib.apply_pose", icon='ZOOM_SELECTED', text="").pose_index = poselib.pose_markers.active_index

            col.operator("poselib.action_sanitize", icon='HELP', text="")  # XXX: put in menu?

            # properties for active marker
            if pose_marker_active is not None:
                layout.prop(pose_marker_active, "name")
                
            col.operator("pose.copy", text="", icon="COPYDOWN")
            col.operator("pose.paste", text="", icon="PASTEDOWN")
            col.operator("pose.paste", text="", icon="PASTEFLIPUP").flipped=True        
            col = layout.column(align=True)
            col.operator(bone_snap_location.bl_idname)
            col.operator(bone_snap_rotation.bl_idname)
            col.operator(bone_snap_locrot.bl_idname)  

### ANIMA 
class Anima(bpy.types.Panel):
    bl_context = "posemode"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Anima"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.pose)
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        #Simplify
        row = layout.row()
        row.prop(context.scene.render, "use_simplify", text="Simplify")
        row.prop(context.scene.render, "simplify_subdivision", text="levels")

        #show_only_render
        row = layout.row()
        row.prop(context.space_data, "show_only_render", text="Hide controllers")

        # Auto key + handles
        row = layout.row(align=True)
        row.prop(context.tool_settings, "use_keyframe_insert_auto", text="", toggle=True)
        row.prop(context.user_preferences.edit, "keyframe_new_interpolation_type", text="")
        
        # Silhouette
        row = layout.row(align=True)
        row.operator("button.silhouette")
        row.operator("button.normal")

        #
        col = layout.column(align=True)
        row = col.row()
        row.operator("pose.push", text="Push")
        row.operator("pose.relax", text="Relax")
        row.operator("pose.breakdown", text="Breakdowner") 

# ANIMA - Apply Silhoutte view
class silhouette(bpy.types.Operator):
    bl_label = "Silhouette"
    bl_idname = "button.silhouette"
    
    def execute(self, context):
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        bpy.data.lamps['Lamp'].energy = 0.0 #hacerla para lamparas en general
        bpy.context.scene.game_settings.material_mode = 'GLSL'  # GLSL shading
        for area in bpy.context.screen.areas: # iterate through areas in current screen
            if area.type == 'VIEW_3D':
                for space in area.spaces: # iterate through spaces in current VIEW_3D area
                    if space.type == 'VIEW_3D': # check if space is a 3D view
                        space.viewport_shade = 'TEXTURED' # set the viewport shading to rendered
                             
        return{"FINISHED"}

# ANIMA - Return to normal view after applied Silhouette
class normal(bpy.types.Operator):
    bl_label = "Normal"
    bl_idname = "button.normal"
    
    def execute(self, context):
        for area in bpy.context.screen.areas: # iterate through areas in current screen
            if area.type == 'VIEW_3D':
                for space in area.spaces: # iterate through spaces in current VIEW_3D area
                    if space.type == 'VIEW_3D': # check if space is a 3D view
                        space.viewport_shade = 'SOLID' # set the viewport shading to rendered
        bpy.data.lamps['Lamp'].energy = 1.0 #hacerla para lamparas en general 
        
        bpy.context.scene.render.engine = 'CYCLES'
                           
        return{"FINISHED"}




def register():
    bpy.utils.register_module(__name__)
    
    #Toogle between Dopesheet and Graph Editor
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Graph Editor', space_type='GRAPH_EDITOR')
        kmi = km.keymap_items.new('wm.context_set_enum', 'TAB', 'PRESS', ctrl=True)
        kmi.properties.data_path = 'area.type'
        kmi.properties.value = 'DOPESHEET_EDITOR'
    
def unregister():
    bpy.utils.unregister_module(__name__)
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    clear_properties()
