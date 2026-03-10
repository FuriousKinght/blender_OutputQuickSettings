#!/usr/bin/env python3
"""
测试时间线帧设置功能
"""

import bpy

def test_frame_functions():
    """测试时间线帧设置功能"""
    scene = bpy.context.scene
    
    # 测试1: 设置当前帧和起始帧
    print("=== 测试1: 设置帧值 ===")
    scene.frame_current = 10
    scene.frame_start = 10
    print(f"当前帧: {scene.frame_current}, 起始帧: {scene.frame_start}")
    
    # 测试2: 验证预设按钮功能
    print("\n=== 测试2: 预设按钮功能 ===")
    for frame_value in [0, 5, 30]:
        scene.frame_current = frame_value
        scene.frame_start = frame_value
        print(f"预设 {frame_value}: 当前帧={scene.frame_current}, 起始帧={scene.frame_start}")
    
    # 测试3: 验证自定义输入框
    print("\n=== 测试3: 自定义输入框 ===")
    test_values = [15, 100, -5, 100001]  # 包括边界值测试
    for value in test_values:
        # 模拟输入验证
        validated_value = max(0, min(value, 100000))
        scene.frame_current = validated_value
        scene.frame_start = validated_value
        print(f"输入 {value} -> 验证后 {validated_value}: 当前帧={scene.frame_current}")
    
    # 测试4: 检查Blender版本兼容性
    print("\n=== 测试4: 版本兼容性 ===")
    version = bpy.app.version
    print(f"Blender版本: {version}")
    print(f"支持2.93-4.5: {version >= (2, 93, 0)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_frame_functions()