# OutputQuickSettings/__init__.py
bl_info = {
    "name": "输出属性快捷设置 终测版V1.5.5",
    "author": "FK",
    "version": (1, 5, 5),
    "blender": (2, 93, 0),
    "location": "视图3D > 属性面板 > MMD",
    "description": "终测版V1.5.5 - 超紧凑型输出属性快捷设置工具（多版本兼容）+ 时间线帧设置",
    "category": "Render",
}

import bpy
from . import compat, properties, operators, panels

classes = (
    properties.OutputSettingsProperties,
    *operators.classes,
    panels.OUTPUT_PT_final_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.output_settings = bpy.props.PointerProperty(type=properties.OutputSettingsProperties)

def unregister():
    if hasattr(bpy.types.Scene, 'output_settings'):
        del bpy.types.Scene.output_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()