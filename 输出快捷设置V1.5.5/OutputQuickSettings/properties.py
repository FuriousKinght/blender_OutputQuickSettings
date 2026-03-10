# OutputQuickSettings/properties.py
import bpy
from . import compat

# ===== 修复：把所有 lambda 改成 def 函数 =====
def update_output_path(self, context):
    context.scene.render.filepath = self.output_path

def update_file_format(self, context):
    context.scene.render.image_settings.file_format = self.file_format
    self.apply_file_format(context)  # 注意：这里原来是 apply_image_settings，应该是笔误！已修复

def update_video_codec(self, context):
    self.apply_video_settings(context)

def update_color_mode(self, context):
    self.apply_image_settings(context)

def update_color_depth(self, context):
    self.apply_image_settings(context)

def update_compression(self, context):
    self.apply_image_settings(context)

def update_custom_render_samples(self, context):
    self.apply_custom_render_samples(context)

def update_custom_viewport_samples(self, context):
    self.apply_custom_viewport_samples(context)

def update_custom_frame(self, context):
    # 添加输入验证
    if self.custom_frame < 0:
        self.custom_frame = 0
    elif self.custom_frame > 100000:
        self.custom_frame = 100000
    
    self.apply_custom_frame(context)
# =========================================

class OutputSettingsProperties(bpy.types.PropertyGroup):

    resolution_orientation: bpy.props.EnumProperty(
        name="方向",
        items=[('LANDSCAPE', "横", ""), ('PORTRAIT', "竖", "")],
        default='LANDSCAPE'
    )

    output_path: bpy.props.StringProperty(
        name="输出路径",
        default="//render_output/",
        subtype='DIR_PATH',
        update=update_output_path        # ← 改这里
    )

    file_format: bpy.props.EnumProperty(
        name="文件格式",
        items=[('PNG', "PNG", ""), ('JPEG', "JPEG", ""), ('OPEN_EXR', "EXR", ""), ('FFMPEG', "视频", "")],
        default='PNG',
        update=update_file_format        # ← 改这里
    )

    video_codec: bpy.props.EnumProperty(
        name="视频编码",
        items=[('H264', "H264", ""), ('H265', "H265", ""), ('MPEG4', "MPEG4", "")],
        default='H264',
        update=update_video_codec        # ← 改这里
    )

    color_mode: bpy.props.EnumProperty(
        name="颜色模式",
        items=[('BW', "BW", ""), ('RGB', "RGB", ""), ('RGBA', "RGBA", "")],
        default='RGB',
        update=update_color_mode         # ← 改这里
    )

    color_depth: bpy.props.EnumProperty(
        name="色深",
        items=[('8', "8", ""), ('16', "16", "")],
        default='8',
        update=update_color_depth        # ← 改这里
    )

    compression: bpy.props.IntProperty(
        name="压缩", default=15, min=0, max=100,
        update=update_compression        # ← 改这里
    )

    custom_render_samples: bpy.props.IntProperty(
        name="自定义渲染采样", default=128, min=1, max=10000,
        update=update_custom_render_samples   # ← 改这里
    )

    custom_viewport_samples: bpy.props.IntProperty(
        name="自定义视口采样", default=32, min=1, max=10000,
        update=update_custom_viewport_samples # ← 改这里
    )

    custom_frame: bpy.props.IntProperty(
        name="自定义帧", default=0, min=0, max=100000,
        update=update_custom_frame
    )

    # ========== 下面的方法保持不变 ==========
    def apply_file_format(self, context):
        context.scene.render.image_settings.file_format = self.file_format
        self.apply_image_settings(context)

    def apply_video_settings(self, context):
        if self.file_format == 'FFMPEG':
            ff = context.scene.render.ffmpeg
            ff.format = 'MPEG4'
            ff.codec = self.video_codec
            ff.quality = 90

    def apply_image_settings(self, context):
        img = context.scene.render.image_settings
        if self.file_format in ['PNG', 'JPEG', 'OPEN_EXR']:
            img.color_mode = self.color_mode
        if self.file_format in ['PNG', 'OPEN_EXR']:
            img.color_depth = self.color_depth
        if self.file_format == 'PNG':
            img.compression = self.compression

    def apply_custom_render_samples(self, context):
        scene = context.scene
        engine = scene.render.engine
        try:
            if engine == 'CYCLES':
                scene.cycles.samples = self.custom_render_samples
            elif compat.is_eevee_engine(engine):
                prop, _ = compat.get_eevee_samples_properties()
                setattr(scene.eevee, prop, self.custom_render_samples)
        except Exception as e:
            print(f"应用自定义渲染采样失败: {e}")

    def apply_custom_viewport_samples(self, context):
        scene = context.scene
        engine = scene.render.engine
        try:
            if engine == 'CYCLES':
                scene.cycles.preview_samples = self.custom_viewport_samples
            elif compat.is_eevee_engine(engine):
                _, prop = compat.get_eevee_samples_properties()
                setattr(scene.eevee, prop, self.custom_viewport_samples)
        except Exception as e:
            print(f"应用自定义视口采样失败: {e}")

    def apply_custom_frame(self, context):
        scene = context.scene
        frame_value = self.custom_frame
        scene.frame_current = frame_value
        scene.frame_start = frame_value