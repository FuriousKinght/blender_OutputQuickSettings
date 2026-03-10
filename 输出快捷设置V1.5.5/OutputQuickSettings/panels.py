# OutputQuickSettings/panels.py
import bpy
import os
from . import compat

class OUTPUT_PT_final_panel(bpy.types.Panel):
    bl_label = "输出快捷设置V1.5.5"
    bl_idname = "OUTPUT_PT_final_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MMD"
    bl_order = 10

    def get_current_blender_settings(self, context):
        scene = context.scene
        r = scene.render
        img = r.image_settings
        settings = {
            'output_path': r.filepath,
            'file_format': img.file_format,
            'color_mode': img.color_mode,
            'color_depth': img.color_depth,
            'compression': getattr(img, 'compression', 15),
            'fps': r.fps,
            'resolution_x': r.resolution_x,
            'resolution_y': r.resolution_y,
            'render_engine': r.engine,
        }
        try:
            if r.engine == 'CYCLES':
                settings['render_samples'] = scene.cycles.samples
                settings['viewport_samples'] = scene.cycles.preview_samples
            elif compat.is_eevee_engine(r.engine):
                rp, vp = compat.get_eevee_samples_properties()
                settings['render_samples'] = getattr(scene.eevee, rp)
                settings['viewport_samples'] = getattr(scene.eevee, vp)
            else:
                settings['render_samples'] = settings['viewport_samples'] = 64
        except:
            settings['render_samples'] = settings['viewport_samples'] = 64

        format_map = {'PNG': 'PNG', 'JPEG': 'JPEG', 'OPEN_EXR': 'OPEN_EXR', 'FFMPEG': 'FFMPEG'}
        settings['file_format'] = format_map.get(settings['file_format'], settings['file_format'])
        return settings

    def draw_engine_selector(self, layout, current_engine):
        box = layout.box()
        row = box.row(align=True)
        row.label(text="引擎:", icon='RENDERLAYERS')
        op = row.operator("output_settings.set_render_engine", text="Cycles", depress=(current_engine == 'CYCLES'))
        op.engine = 'CYCLES'
        name = compat.get_eevee_display_name()
        op = row.operator("output_settings.set_render_engine", text=name, depress=compat.is_eevee_engine(current_engine))
        op.engine = 'EEVEE'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.output_settings
        b = self.get_current_blender_settings(context)

        # 作者信息
        row = layout.row()
        col = row.column(align=True)
        col.scale_y = 0.7
        col.label(text="by FK")
        col.label(text="Q群：1042375616")
        row.operator("output_settings.copy_qq_group", text="", icon='COPYDOWN')

        # 1. 引擎
        self.draw_engine_selector(layout, b['render_engine'])

        # 2. 采样
        box = layout.box()
        r1 = box.row(align=True)
        r1.label(text="渲染采样:", icon='RESTRICT_RENDER_OFF')
        for v in [16,32,64]:
            op = r1.operator("output_settings.set_render_samples", text=str(v), depress=(b['render_samples']==v))
            op.samples_type = 'render'; op.samples_value = v
        r2 = box.row(align=True)
        r2.label(text="自定义:")
        r2.prop(settings, "custom_render_samples", text="")

        r1 = box.row(align=True)
        r1.label(text="视口采样:", icon='RESTRICT_VIEW_OFF')
        for v in [16,32,64]:
            op = r1.operator("output_settings.set_render_samples", text=str(v), depress=(b['viewport_samples']==v))
            op.samples_type = 'viewport'; op.samples_value = v
        r2 = box.row(align=True)
        r2.label(text="自定义:")
        r2.prop(settings, "custom_viewport_samples", text="")

        # 3. 分辨率
        box = layout.box()
        row = box.row(align=True)
        row.label(text="分辨率:", icon='RENDER_RESULT')
        cur_x, cur_y = (b['resolution_y'], b['resolution_x']) if settings.resolution_orientation == 'PORTRAIT' else (b['resolution_x'], b['resolution_y'])
        for k, (x,y) in {'720p':(1280,720),'1080p':(1920,1080),'2k':(2048,1080),'4k':(3840,2160)}.items():
            op = row.operator("render.set_resolution", text=k.replace('p','P').replace('k','K'), depress=(cur_x==x and cur_y==y))
            op.resolution = k
        row = box.row(align=True)
        icon = 'ORIENTATION_GIMBAL' if settings.resolution_orientation == 'LANDSCAPE' else 'ORIENTATION_NORMAL'
        row.operator("render.toggle_orientation", text="横/竖", icon=icon)

        # 4. 帧率
        box = layout.box()
        row = box.row(align=True)
        row.label(text="帧率:", icon='PREVIEW_RANGE')
        for v in ['30','60','120']:
            op = row.operator("render.set_fps", text=v, depress=(b['fps']==int(v)))
            op.fps = v

        # 5. 时间线帧设置
        box = layout.box()
        row = box.row(align=True)
        row.label(text="时间线帧:", icon='TIME')
        current_frame = scene.frame_current
        start_frame = scene.frame_start
        
        # 预设按钮 - 使用紧凑布局
        for v in [0, 5, 30]:
            op = row.operator("output_settings.set_frame", text=str(v), 
                             depress=(current_frame == v and start_frame == v))
            op.frame_value = v
        
        # 自定义输入框 - 添加图标和提示
        row = box.row(align=True)
        row.label(text="自定义:", icon='GREASEPENCIL')
        row.prop(settings, "custom_frame", text="")
        
        # 添加当前帧状态显示
        row = box.row(align=True)
        row.scale_y = 0.8
        row.label(text=f"当前: {current_frame}, 起始: {start_frame}", icon='INFO')

        # 6. 输出路径 + 格式
        box = layout.box()
        row = box.row(align=True)
        row.label(text="输出:", icon='FILE_FOLDER')
        row.prop(settings, "output_path", text="")
        row.operator("render.open_output_folder", text="", icon='FILE_FOLDER')
        row = box.row(align=True)
        row.prop(settings, "file_format", text="格式")

        # 6. 图像设置
        if settings.file_format == 'FFMPEG':
            box = layout.box()
            row = box.row(align=True)
            row.label(text="编码:")
            row.prop(settings, "video_codec", text="")
        else:
            box = layout.box()
            row = box.row(align=True)
            row.label(text="颜色:")
            for mode in ['BW','RGB','RGBA']:
                op = row.operator("output_settings.set_color_mode", text=mode, depress=(b['color_mode']==mode))
                op.color_mode = mode
            row = box.row(align=True)
            row.label(text="色深:")
            for d in ['8','16']:
                op = row.operator("output_settings.set_color_depth", text=d, depress=(b['color_depth']==d))
                op.color_depth = d
            row.label(text="压缩:")
            row.prop(settings, "compression", text="", slider=True)

        # 7. 渲染按钮
        box = layout.box()
        box.operator("render.quick_render_animation", text="渲染动画", icon='RENDER_ANIMATION')

        # 8. 状态栏
        box = layout.box()
        box.scale_y = 0.6
        engine_name = "Cycles" if b['render_engine']=='CYCLES' else compat.get_eevee_display_name()
        box.label(text=f"引擎: {engine_name}, 渲染: {b['render_samples']}采样, 视口: {b['viewport_samples']}采样")
        ori = "横屏" if settings.resolution_orientation == 'LANDSCAPE' else "竖屏"
        box.label(text=f"分辨率: {b['resolution_x']}×{b['resolution_y']} ({ori})")
        box.label(text=f"帧率: {b['fps']}")
        box.label(text=f"当前帧: {scene.frame_current}, 起始帧: {scene.frame_start}")
        box.label(text=f"格式: {b['file_format']}")
        box.label(text=f"路径: {os.path.basename(b['output_path']) or '未设置'}")
        box.label(text=f"色彩: {scene.view_settings.view_transform}")