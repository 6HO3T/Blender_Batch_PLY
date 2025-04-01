
bl_info = {
    "name": "Batch PLY",
    "author": "Philip McCloskey",
    "version": (0, 3),
    "blender": (4, 4, 0),
    "location": "File > Import-Export",
    "description": "Batch import PLY files, transform, build hierarchy, assign material, and export as DAE",
    "category": "Import-Export",
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
        layout.prop(context.scene, "import_folder_path", text="Import Folder")
        layout.prop(context.scene, "export_folder_path", text="Export Folder")
        layout.prop(context.scene, "scale_factor")
        layout.label(text="Rotation Angles:")
        layout.prop(context.scene, "rotation_angle_x", text="X")
        layout.prop(context.scene, "rotation_angle_y", text="Y")
        layout.prop(context.scene, "rotation_angle_z", text="Z")
        layout.prop(context.scene, "base_z_height", text="Base Z Height")
        layout.operator("script.batch_import_export")

class BatchImportExportOperator(bpy.types.Operator):
    bl_idname = "script.batch_import_export"
    bl_label = "Batch Import Export"
    bl_description = "Batch import PLY files, transform, build hierarchy, assign material, and export as DAE"

    def execute(self, context):
        import_folder_path = bpy.context.scene.import_folder_path
        export_folder_path = bpy.context.scene.export_folder_path
        scale_factor = bpy.context.scene.scale_factor
        rotation_angle_x = math.radians(bpy.context.scene.rotation_angle_x)
        rotation_angle_y = math.radians(bpy.context.scene.rotation_angle_y)
        rotation_angle_z = math.radians(bpy.context.scene.rotation_angle_z)
        base_z = bpy.context.scene.base_z_height

        files = os.listdir(import_folder_path)
        for file_name in files:
            if file_name.lower().endswith('.ply'):
                file_path = os.path.join(import_folder_path, file_name)
                bpy.ops.wm.ply_import(filepath=file_path)
                mesh_obj = bpy.context.selected_objects[-1]
                base_name = os.path.splitext(file_name)[0]
                mesh_obj.name = base_name + '_mesh'

                # Apply transform to mesh
                bpy.ops.object.select_all(action='DESELECT')
                mesh_obj.select_set(True)
                bpy.context.view_layer.objects.active = mesh_obj

                mesh_obj.scale = (scale_factor, scale_factor, scale_factor)
                mesh_obj.rotation_euler = (rotation_angle_x, rotation_angle_y, rotation_angle_z)
                bpy.context.view_layer.update()
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

                # Set origin to center of mass and move to (0, 0, Z)
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
                mesh_obj.location = (0, 0, base_z)
                bpy.context.view_layer.update()

                # Reapply transform after final position set
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

                # Create hierarchy: root -> base_name -> Top_Node -> mesh
                bpy.ops.object.empty_add(type='PLAIN_AXES')
                root = bpy.context.active_object
                root.name = "root"
                root.scale = (0.001, 0.001, 0.001)

                bpy.ops.object.empty_add(type='PLAIN_AXES')
                name_node = bpy.context.active_object
                name_node.name = base_name
                name_node.parent = root

                bpy.ops.object.empty_add(type='PLAIN_AXES')
                top_node = bpy.context.active_object
                top_node.name = "Top_Node"
                top_node.parent = name_node

                mesh_obj.parent = top_node

                # Set material
                mat_name = "Metal_Alum_Cast"
                mat = bpy.data.materials.get(mat_name)
                if not mat:
                    mat = bpy.data.materials.new(name=mat_name)
                    mat.use_nodes = True
                    bsdf = mat.node_tree.nodes.get('Principled BSDF')
                    if bsdf:
                        bsdf.inputs['Base Color'].default_value = (0.588, 0.588, 0.588, 1)  # #969696FF
                        bsdf.inputs['Metallic'].default_value = 0.0
                        bsdf.inputs['Roughness'].default_value = 0.5
                        bsdf.inputs['IOR'].default_value = 1.0
                        bsdf.inputs['Specular'].default_value = 0.5
                if not mesh_obj.data.materials:
                    mesh_obj.data.materials.append(mat)
                else:
                    mesh_obj.data.materials[0] = mat

                # Export
                export_path = os.path.join(export_folder_path, base_name + '.dae')
                bpy.ops.object.select_all(action='DESELECT')
                root.select_set(True)
                bpy.context.view_layer.objects.active = root
                bpy.ops.wm.collada_export(filepath=export_path, selected=False)

                # Cleanup
                bpy.data.objects.remove(mesh_obj, do_unlink=True)
                bpy.data.objects.remove(top_node, do_unlink=True)
                bpy.data.objects.remove(name_node, do_unlink=True)
                bpy.data.objects.remove(root, do_unlink=True)

        # Cleanup unused materials
        for mat in bpy.data.materials:
            if not mat.users:
                bpy.data.materials.remove(mat)

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
    bpy.types.Scene.base_z_height = bpy.props.FloatProperty(
        name="Base Z Height",
        description="Z position to place mesh in world space",
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
    del bpy.types.Scene.base_z_height

if __name__ == "__main__":
    register()
