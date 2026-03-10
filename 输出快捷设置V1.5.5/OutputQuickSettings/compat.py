# OutputQuickSettings/compat.py
import bpy

def get_blender_version():
    return bpy.app.version

def is_blender_4_or_above():
    return get_blender_version() >= (4, 0, 0)

def get_eevee_engine_name():
    return 'BLENDER_EEVEE_NEXT' if is_blender_4_or_above() else 'BLENDER_EEVEE'

def get_eevee_samples_properties():
    if is_blender_4_or_above():
        return 'taa_render_samples', 'taa_samples'
    else:
        return 'taa_samples', 'taa_samples'

def set_render_engine_safe(scene, engine):
    target = get_eevee_engine_name() if engine == 'EEVEE' else engine
    try:
        scene.render.engine = target
        return True
    except Exception as e:
        print(f"设置渲染引擎失败: {e}")
        return False

def get_eevee_display_name():
    return "EEVEE Next" if is_blender_4_or_above() else "EEVEE"

def is_eevee_engine(engine_name):
    return engine_name in ['BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT']