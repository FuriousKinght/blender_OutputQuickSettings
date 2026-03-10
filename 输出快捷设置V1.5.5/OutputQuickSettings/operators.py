# OutputQuickSettings/operators.py
import bpy
import os
import subprocess
from . import compat

classes = ()

# ==================== 操作符定义 ====================

class SetResolutionOperator(bpy.types.Operator):
    bl_idname = "render.set_resolution"
    bl_label = "设置分辨率"
    resolution: bpy.props.StringProperty()

    def execute(self, context):
        res = {'720p': (1280,720), '1080p': (1920,1080), '2k': (2048,1080), '4k': (3840,2160)}
        x, y = res.get(self.resolution, (1920,1080))
        if context.scene.output_settings.resolution_orientation == 'PORTRAIT':
            x, y = y, x
        context.scene.render.resolution_x = x
        context.scene.render.resolution_y = y
        return {'FINISHED'}
classes += (SetResolutionOperator,)

class SetFPSOperator(bpy.types.Operator):
    bl_idname = "render.set_fps"
    bl_label = "设置帧率"
    fps: bpy.props.StringProperty()
    def execute(self, context):
        context.scene.render.fps = int(self.fps)
        context.scene.render.fps_base = 1.0
        return {'FINISHED'}
classes += (SetFPSOperator,)

class ToggleOrientationOperator(bpy.types.Operator):
    bl_idname = "render.toggle_orientation"
    bl_label = "切换方向"
    def execute(self, context):
        s = context.scene.output_settings
        s.resolution_orientation = 'PORTRAIT' if s.resolution_orientation == 'LANDSCAPE' else 'LANDSCAPE'
        x = context.scene.render.resolution_x
        context.scene.render.resolution_x = context.scene.render.resolution_y
        context.scene.render.resolution_y = x
        return {'FINISHED'}
classes += (ToggleOrientationOperator,)

class BrowseOutputPathOperator(bpy.types.Operator):
    bl_idname = "render.browse_output_path"
    bl_label = "浏览输出路径"
    directory: bpy.props.StringProperty(subtype='DIR_PATH')
    def execute(self, context):
        context.scene.output_settings.output_path = self.directory
        return {'FINISHED'}
    def invoke(self, context, event):
        self.directory = context.scene.output_settings.output_path or "//"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
classes += (BrowseOutputPathOperator,)

class OpenOutputFolderOperator(bpy.types.Operator):
    bl_idname = "render.open_output_folder"
    bl_label = "打开输出文件夹"
    def execute(self, context):
        path = bpy.path.abspath(context.scene.output_settings.output_path)
        if not os.path.exists(path):
            try: os.makedirs(path)
            except: self.report({'WARNING'}, f"无法创建目录: {path}"); return {'CANCELLED'}
        try:
            if os.name == 'nt':
                os.startfile(path)
            else:
                subprocess.run(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', path])
        except Exception as e:
            self.report({'ERROR'}, f"无法打开文件夹: {e}")
            return {'CANCELLED'}
        return {'FINISHED'}
classes += (OpenOutputFolderOperator,)

class QuickRenderAnimationOperator(bpy.types.Operator):
    bl_idname = "render.quick_render_animation"
    bl_label = "渲染动画"
    def execute(self, context):
        bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
        return {'FINISHED'}
classes += (QuickRenderAnimationOperator,)

class CopyQQGroupOperator(bpy.types.Operator):
    bl_idname = "output_settings.copy_qq_group"
    bl_label = "复制QQ群号"
    def execute(self, context):
        context.window_manager.clipboard = "1042375616"
        self.report({'INFO'}, "QQ群号已复制: 1042375616")
        return {'FINISHED'}
classes += (CopyQQGroupOperator,)

class SetColorModeOperator(bpy.types.Operator):
    bl_idname = "output_settings.set_color_mode"
    bl_label = "设置颜色模式"
    color_mode: bpy.props.StringProperty()
    def execute(self, context):
        context.scene.output_settings.color_mode = self.color_mode
        return {'FINISHED'}
classes += (SetColorModeOperator,)

class SetColorDepthOperator(bpy.types.Operator):
    bl_idname = "output_settings.set_color_depth"
    bl_label = "设置色深"
    color_depth: bpy.props.StringProperty()
    def execute(self, context):
        context.scene.output_settings.color_depth = self.color_depth
        return {'FINISHED'}
classes += (SetColorDepthOperator,)

class SetRenderEngineOperator(bpy.types.Operator):
    bl_idname = "output_settings.set_render_engine"
    bl_label = "设置渲染引擎"
    engine: bpy.props.StringProperty()
    def execute(self, context):
        if compat.set_render_engine_safe(context.scene, self.engine):
            return {'FINISHED'}
        self.report({'ERROR'}, "设置渲染引擎失败")
        return {'CANCELLED'}
classes += (SetRenderEngineOperator,)

class SetRenderSamplesOperator(bpy.types.Operator):
    bl_idname = "output_settings.set_render_samples"
    bl_label = "设置渲染采样"
    samples_type: bpy.props.StringProperty()
    samples_value: bpy.props.IntProperty()
    def execute(self, context):
        scene = context.scene
        settings = scene.output_settings
        engine = scene.render.engine
        try:
            if engine == 'CYCLES':
                if self.samples_type == 'render':
                    scene.cycles.samples = self.samples_value
                    settings.custom_render_samples = self.samples_value
                else:
                    scene.cycles.preview_samples = self.samples_value
                    settings.custom_viewport_samples = self.samples_value
            elif compat.is_eevee_engine(engine):
                rp, vp = compat.get_eevee_samples_properties()
                if self.samples_type == 'render':
                    setattr(scene.eevee, rp, self.samples_value)
                    settings.custom_render_samples = self.samples_value
                else:
                    setattr(scene.eevee, vp, self.samples_value)
                    settings.custom_viewport_samples = self.samples_value
        except Exception as e:
            self.report({'ERROR'}, f"设置采样失败: {e}")
            return {'CANCELLED'}
        return {'FINISHED'}
classes += (SetRenderSamplesOperator,)

class SetFrameOperator(bpy.types.Operator):
    bl_idname = "output_settings.set_frame"
    bl_label = "设置帧"
    frame_value: bpy.props.IntProperty()
    
    def execute(self, context):
        scene = context.scene
        frame_value = self.frame_value
        
        # 验证帧值范围
        if frame_value < 0:
            self.report({'WARNING'}, "帧值不能为负数")
            return {'CANCELLED'}
        
        if frame_value > 100000:
            self.report({'WARNING'}, "帧值过大，建议使用小于100000的值")
            return {'CANCELLED'}
        
        scene.frame_current = frame_value
        scene.frame_start = frame_value
        context.scene.output_settings.custom_frame = frame_value
        
        self.report({'INFO'}, f"已设置当前帧和起始帧为: {frame_value}")
        return {'FINISHED'}
classes += (SetFrameOperator,)