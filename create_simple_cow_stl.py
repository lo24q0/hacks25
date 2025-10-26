#!/usr/bin/env python3
"""
创建一个简单的3D牛模型STL文件(ASCII格式)
不依赖任何外部库,手动构建STL几何
"""

import math


def write_stl_triangle(f, v1, v2, v3):
    """
    写入一个三角面到STL文件

    Args:
        f: 文件对象
        v1, v2, v3: 三个顶点坐标 [(x, y, z), (x, y, z), (x, y, z)]
    """
    # 计算法向量
    u = (v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2])
    v = (v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2])

    # 叉积得到法向量
    nx = u[1] * v[2] - u[2] * v[1]
    ny = u[2] * v[0] - u[0] * v[2]
    nz = u[0] * v[1] - u[1] * v[0]

    # 归一化
    length = math.sqrt(nx**2 + ny**2 + nz**2)
    if length > 0:
        nx, ny, nz = nx/length, ny/length, nz/length

    # 写入三角面
    f.write(f"  facet normal {nx:.6f} {ny:.6f} {nz:.6f}\n")
    f.write("    outer loop\n")
    f.write(f"      vertex {v1[0]:.6f} {v1[1]:.6f} {v1[2]:.6f}\n")
    f.write(f"      vertex {v2[0]:.6f} {v2[1]:.6f} {v2[2]:.6f}\n")
    f.write(f"      vertex {v3[0]:.6f} {v3[1]:.6f} {v3[2]:.6f}\n")
    f.write("    endloop\n")
    f.write("  endfacet\n")


def create_box(f, x, y, z, w, h, d):
    """
    创建一个长方体并写入STL文件

    Args:
        f: 文件对象
        x, y, z: 中心坐标
        w, h, d: 宽度、高度、深度
    """
    # 8个顶点
    x0, x1 = x - w/2, x + w/2
    y0, y1 = y - h/2, y + h/2
    z0, z1 = z - d/2, z + d/2

    vertices = [
        (x0, y0, z0),  # 0
        (x1, y0, z0),  # 1
        (x1, y1, z0),  # 2
        (x0, y1, z0),  # 3
        (x0, y0, z1),  # 4
        (x1, y0, z1),  # 5
        (x1, y1, z1),  # 6
        (x0, y1, z1),  # 7
    ]

    # 12个三角面(6个面 x 2个三角形)
    faces = [
        # 底面 (z0)
        (0, 1, 2), (0, 2, 3),
        # 顶面 (z1)
        (4, 6, 5), (4, 7, 6),
        # 前面 (y0)
        (0, 5, 1), (0, 4, 5),
        # 后面 (y1)
        (3, 2, 6), (3, 6, 7),
        # 左面 (x0)
        (0, 3, 7), (0, 7, 4),
        # 右面 (x1)
        (1, 5, 6), (1, 6, 2),
    ]

    for face in faces:
        write_stl_triangle(f, vertices[face[0]], vertices[face[1]], vertices[face[2]])


def create_cylinder_approx(f, x, y, z, radius, height, segments=8):
    """
    创建圆柱体(用多边形近似)

    Args:
        f: 文件对象
        x, y, z: 底部中心坐标
        radius: 半径
        height: 高度
        segments: 分段数
    """
    # 底部和顶部圆心
    bottom_center = (x, y, z)
    top_center = (x, y, z + height)

    # 计算圆周上的点
    bottom_points = []
    top_points = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        bottom_points.append((px, py, z))
        top_points.append((px, py, z + height))

    # 侧面
    for i in range(segments):
        next_i = (i + 1) % segments
        # 两个三角形组成侧面四边形
        write_stl_triangle(f, bottom_points[i], top_points[i], top_points[next_i])
        write_stl_triangle(f, bottom_points[i], top_points[next_i], bottom_points[next_i])

    # 底面
    for i in range(segments):
        next_i = (i + 1) % segments
        write_stl_triangle(f, bottom_center, bottom_points[next_i], bottom_points[i])

    # 顶面
    for i in range(segments):
        next_i = (i + 1) % segments
        write_stl_triangle(f, top_center, top_points[i], top_points[next_i])


def create_cow_stl(output_path):
    """
    创建一个简单的3D牛模型STL文件

    使用基本几何体:
    - 身体: 长方体
    - 头部: 立方体
    - 腿: 4个圆柱体
    - 角: 2个小圆锥(用圆柱近似)
    """
    with open(output_path, 'w') as f:
        f.write("solid cow\n")

        # 1. 身体 (中心位置, 拉长的长方体)
        create_box(f, x=0, y=0, z=15, w=30, h=20, d=15)

        # 2. 头部 (前方的立方体)
        create_box(f, x=20, y=0, z=18, w=12, h=12, d=10)

        # 3. 鼻子 (小立方体)
        create_box(f, x=28, y=0, z=16, w=4, h=6, d=4)

        # 4. 四条腿 (圆柱体)
        # 前右
        create_cylinder_approx(f, x=10, y=8, z=0, radius=2.5, height=15, segments=8)
        # 前左
        create_cylinder_approx(f, x=10, y=-8, z=0, radius=2.5, height=15, segments=8)
        # 后右
        create_cylinder_approx(f, x=-10, y=8, z=0, radius=2.5, height=15, segments=8)
        # 后左
        create_cylinder_approx(f, x=-10, y=-8, z=0, radius=2.5, height=15, segments=8)

        # 5. 耳朵 (小长方体)
        # 左耳
        create_box(f, x=22, y=-7, z=25, w=3, h=4, d=2)
        # 右耳
        create_box(f, x=22, y=7, z=25, w=3, h=4, d=2)

        # 6. 角 (小圆锥,用渐小的圆柱近似)
        # 左角
        create_cylinder_approx(f, x=20, y=-5, z=26, radius=1.5, height=5, segments=6)
        # 右角
        create_cylinder_approx(f, x=20, y=5, z=26, radius=1.5, height=5, segments=6)

        # 7. 尾巴 (细圆柱)
        create_cylinder_approx(f, x=-16, y=0, z=10, radius=1, height=12, segments=6)

        f.write("endsolid cow\n")

    print(f"✅ STL 文件已生成: {output_path}")
    print(f"   模型尺寸: 约 50mm x 25mm x 30mm")
    print(f"   适合拓竹 H2D 打印机 (256x256x256mm)")


if __name__ == "__main__":
    output_path = "/tmp/cow_model.stl"
    create_cow_stl(output_path)

    # 显示文件信息
    import os
    file_size = os.path.getsize(output_path)
    print(f"   文件大小: {file_size / 1024:.2f} KB")
