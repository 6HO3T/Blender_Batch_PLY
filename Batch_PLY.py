bl_info = {
    "name": "Batch PLY",
    "author": "Philip McCloskey",
    "version": (0, 2),
    "blender": (4, 0, 0),
    "location": "File > Import-Export",
    "description": "Batch import PLY files from a folder, apply transformations, and export them as Collada DAE to another folder",
    "category": "Import-Export",
    "doc_url": "https://github.com/6HO3T/Blender_Batch_PLY",
    "tracker_url": "https://github.com/6HO3T/Blender_Batch_PLY/issues"
}


import bpy
import os
import math


class BatchImportExportPanel(bpy.types.Panel):
    bl_label = "Batch PLY"
    bl_idname = "OBJECT_PT_batch_import_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Batch PLY'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, "import_folder_path", text="Import Folder")
        row = layout.row()
        row.prop(context.scene, "export_folder_path", text="Export Folder")
        row = layout.row()
        row.prop(context.scene, "scale_factor")
        
        col = layout.column()
        col.label(text="Rotation Angles:")
        col.prop(context.scene, "rotation_angle_x", text="X")
        col.prop(context.scene, "rotation_angle_y", text="Y")
        col.prop(context.scene, "rotation_angle_z", text="Z")
        
        row = layout.row()
        row.operator("script.batch_import_export")


class BatchImportExportOperator(bpy.types.Operator):
    bl_idname = "script.batch_import_export"
    bl_label = "Batch Import Export"
    bl_description = "Batch import files from a folder, apply transformations, and export"

    def execute(self, context):
        import_folder_path = bpy.context.scene.import_folder_path
        export_folder_path = bpy.context.scene.export_folder_path
        scale_factor = bpy.context.scene.scale_factor
        rotation_angle_x = math.radians(bpy.context.scene.rotation_angle_x)
        rotation_angle_y = math.radians(bpy.context.scene.rotation_angle_y)
        rotation_angle_z = math.radians(bpy.context.scene.rotation_angle_z)

        files = os.listdir(import_folder_path)
        
        for file_name in files:
            if file_name.endswith('.PLY'):
                file_path = os.path.join(import_folder_path, file_name)
                bpy.ops.wm.ply_import(filepath=file_path)
                
                # Get the last imported object directly from selected objects
                obj = bpy.context.selected_objects[-1] 
                
                # Create a copy of the object to apply transformations
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.duplicate(linked=False)
                obj_copy = bpy.context.selected_objects[-1]
                
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                obj_copy.scale = (scale_factor, scale_factor, scale_factor)
                obj_copy.rotation_euler = (rotation_angle_x, rotation_angle_y, rotation_angle_z)
                
                export_file_path = os.path.join(export_folder_path, os.path.splitext(file_name)[0] + '.dae')
                try:
                    # Apply all transformations
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    
                    # Center the object origin
                    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
                                
                    # Remove the original object
                    bpy.data.objects.remove(obj, do_unlink=True)
                    
                    # Remove ".001" suffix from object name
                    obj_copy.name = obj_copy.name.split(".")[0]
                    
                    # Export to Collada format (.dae)
                    bpy.ops.wm.collada_export(filepath=export_file_path)
                    print("Export successful:", export_file_path)
                except Exception as e:
                    print("Error exporting file:", e)

                bpy.data.objects.remove(obj_copy, do_unlink=True)
        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BatchImportExportPanel)
    bpy.utils.register_class(BatchImportExportOperator)

    bpy.types.Scene.import_folder_path = bpy.props.StringProperty(
        name="Import Folder Path",
        description="Folder path containing files to import",
        subtype='DIR_PATH'
    )
    bpy.types.Scene.export_folder_path = bpy.props.StringProperty(
        name="Export Folder Path",
        description="Folder path for exporting the files",
        subtype='DIR_PATH'
    )
    bpy.types.Scene.scale_factor = bpy.props.FloatProperty(
        name="Scale Factor",
        description="Factor to scale the imported objects",
        default=1.0
    )
    bpy.types.Scene.rotation_angle_x = bpy.props.FloatProperty(
        name="Rotation Angle X",
        description="Angle (in degrees) to rotate the imported objects along the X axis",
        default=0.0
    )
    bpy.types.Scene.rotation_angle_y = bpy.props.FloatProperty(
        name="Rotation Angle Y",
        description="Angle (in degrees) to rotate the imported objects along the Y axis",
        default=0.0
    )
    bpy.types.Scene.rotation_angle_z = bpy.props.FloatProperty(
        name="Rotation Angle Z",
        description="Angle (in degrees) to rotate the imported objects along the Z axis",
        default=0.0
    )
    bpy.types.Scene.location_x = bpy.props.FloatProperty(
        name="Location X",
        description="Location along the X axis",
        default=0.0
    )
    bpy.types.Scene.location_y = bpy.props.FloatProperty(
        name="Location Y",
        description="Location along the Y axis",
        default=0.0
    )
    bpy.types.Scene.location_z = bpy.props.FloatProperty(
        name="Location Z",
        description="Location along the Z axis",
        default=0.0
    )


def unregister():
    bpy.utils.unregister_class(BatchImportExportPanel)
    bpy.utils.unregister_class(BatchImportExportOperator)

    del bpy.types.Scene.import_folder_path
    del bpy.types.Scene.export_folder_path
    del bpy.types.Scene.scale_factor
    del bpy.types.Scene.rotation_angle_x
    del bpy.types.Scene.rotation_angle_y
    del bpy.types.Scene.rotation_angle_z


if __name__ == "__main__":
    register()
