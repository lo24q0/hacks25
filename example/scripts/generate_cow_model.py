#!/usr/bin/env python3
"""
生成一个简单的 3D 牛模型 STL 文件
使用 trimesh 库创建基本的几何体组合来模拟牛的形状
"""

import numpy as np
import trimesh

def create_cow_model():
    """
    创建一个简单的 3D 牛模型
    
    使用基本几何体组合:
    - 身体: 拉长的球体
    - 头部: 较小的球体
    - 腿: 4个圆柱体
    - 耳朵: 2个扁平的椭球
    - 角: 2个小圆锥
    """
    meshes = []
    
    # 1. 身体 (椭球体 - 拉长的球体)
    body = trimesh.creation.icosphere(subdivisions=3, radius=20)
    # 沿 X 轴拉长以形成身体
    body.apply_scale([1.5, 1.0, 0.8])
    body.apply_translation([0, 0, 25])
    meshes.append(body)
    
    # 2. 头部 (稍小的球体)
    head = trimesh.creation.icosphere(subdivisions=3, radius=12)
    head.apply_translation([30, 0, 28])
    meshes.append(head)
    
    # 3. 鼻子 (小圆柱体)
    nose = trimesh.creation.cylinder(radius=6, height=8)
    # 旋转使其水平
    nose.apply_transform(trimesh.transformations.rotation_matrix(
        np.pi/2, [0, 1, 0]
    ))
    nose.apply_translation([40, 0, 25])
    meshes.append(nose)
    
    # 4. 四条腿 (圆柱体)
    leg_positions = [
        [15, 12, 0],   # 前右
        [15, -12, 0],  # 前左
        [-15, 12, 0],  # 后右
        [-15, -12, 0], # 后左
    ]
    
    for pos in leg_positions:
        leg = trimesh.creation.cylinder(radius=4, height=25)
        leg.apply_translation([pos[0], pos[1], pos[2] + 12.5])
        meshes.append(leg)
    
    # 5. 耳朵 (扁平椭球)
    ear_left = trimesh.creation.icosphere(subdivisions=2, radius=5)
    ear_left.apply_scale([0.3, 1.0, 1.2])
    ear_left.apply_translation([35, -10, 35])
    meshes.append(ear_left)
    
    ear_right = trimesh.creation.icosphere(subdivisions=2, radius=5)
    ear_right.apply_scale([0.3, 1.0, 1.2])
    ear_right.apply_translation([35, 10, 35])
    meshes.append(ear_right)
    
    # 6. 角 (圆锥体)
    horn_left = trimesh.creation.cone(radius=2, height=8)
    horn_left.apply_translation([32, 8, 38])
    meshes.append(horn_left)
    
    horn_right = trimesh.creation.cone(radius=2, height=8)
    horn_right.apply_translation([32, -8, 38])
    meshes.append(horn_right)
    
    # 7. 尾巴 (细圆柱体 + 球体末端)
    tail_base = trimesh.creation.cylinder(radius=1.5, height=18)
    # 旋转使其斜向后
    tail_base.apply_transform(trimesh.transformations.rotation_matrix(
        np.pi/6, [0, 1, 0]
    ))
    tail_base.apply_translation([-25, 0, 20])
    meshes.append(tail_base)
    
    tail_end = trimesh.creation.icosphere(subdivisions=1, radius=3)
    tail_end.apply_translation([-33, 0, 15])
    meshes.append(tail_end)
    
    # 合并所有网格
    cow = trimesh.util.concatenate(meshes)
    
    # 确保模型适合打印机尺寸(拓竹 H2D: 256x256x256mm)
    # 缩放到合适的尺寸 (大约 60mm x 40mm x 40mm)
    bounds = cow.bounds
    size = bounds[1] - bounds[0]
    scale_factor = min(60 / size[0], 40 / size[1], 40 / size[2])
    cow.apply_scale(scale_factor)
    
    # 将模型底部放在 Z=0 平面上
    cow.apply_translation([0, 0, -cow.bounds[0][2]])
    
    return cow

def main():
    """主函数"""
    print("正在生成 3D 牛模型...")
    
    # 创建牛模型
    cow = create_cow_model()
    
    # 输出模型信息
    print(f"\n✅ 模型生成完成!")
    print(f"   顶点数: {len(cow.vertices)}")
    print(f"   三角面数: {len(cow.faces)}")
    print(f"   尺寸: {cow.bounds[1] - cow.bounds[0]} mm")
    print(f"   体积: {cow.volume:.2f} mm³")
    print(f"   表面积: {cow.area:.2f} mm²")
    print(f"   是否流形(可打印): {cow.is_watertight}")
    
    # 保存为 STL 文件
    output_path = "/tmp/cow_model.stl"
    cow.export(output_path)
    print(f"\n💾 STL 文件已保存到: {output_path}")
    
    return output_path

if __name__ == "__main__":
    main()
