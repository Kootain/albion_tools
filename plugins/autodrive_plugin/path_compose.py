import math
from typing import List

from base.base2 import P


def point_to_line_distance(point: P, line_start: P, line_end: P) -> float:
    """
    计算单个点到直线（由line_start和line_end确定）的垂直距离
    :param point: 待计算的点 (x0, y0)
    :param line_start: 直线起点 (x1, y1)
    :param line_end: 直线终点 (x2, y2)
    :return: 点到直线的垂直距离
    """
    x0, y0 = point.x, point.y
    x1, y1 = line_start.x, line_start.y
    x2, y2 = line_end.x, line_end.y
    
    # 直线的一般式：Ax + By + C = 0
    A = y2 - y1
    B = x1 - x2
    C = x2 * y1 - x1 * y2
    
    # 点到直线的垂直距离公式：|Ax0 + By0 + C| / sqrt(A² + B²)
    distance = abs(A * x0 + B * y0 + C) / math.hypot(A, B)
    return distance

def douglas_peucker(points: List[P], epsilon: float) -> List[P]:
    """
    道格拉斯-普克算法压缩路径点
    :param points: 原始路径点序列（至少包含2个点）
    :param epsilon: 误差阈值（距离），值越大压缩越厉害
    :return: 压缩后的路径点序列
    """
    # 递归终止条件：路径点数量≤2，直接返回（无需压缩）
    if len(points) <= 2:
        return points.copy()
    
    # 1. 找到距离起点-终点连线最远的点
    start_point = points[0]
    end_point = points[-1]
    max_distance = 0.0
    max_index = 0  # 最远点的索引
    
    for i in range(1, len(points)-1):
        current_distance = point_to_line_distance(points[i], start_point, end_point)
        if current_distance > max_distance:
            max_distance = current_distance
            max_index = i
    
    # 2. 判断最远点是否超过误差阈值
    compressed_points = []
    if max_distance > epsilon:
        # 超过阈值：保留该点，递归处理左侧（起点到最远点）和右侧（最远点到终点）子路径
        left_part = douglas_peucker(points[:max_index+1], epsilon)
        right_part = douglas_peucker(points[max_index:], epsilon)
        # 合并结果（避免重复添加最远点）
        compressed_points = left_part[:-1] + right_part
    else:
        # 未超过阈值：只保留起点和终点
        compressed_points = [start_point, end_point]
    
    return compressed_points

# ------------------- 测试用例 -------------------
if __name__ == "__main__":
    # 构造原始路径点：近似直线，中间有少量噪点
    original_points = [
        P(0.0, 0.0),
        P(1.0, 1.1),  # 偏离直线一点
        P(2.0, 2.0),
        P(3.0, 2.9),  # 偏离直线一点
        P(4.0, 4.0),
        P(5.0, 5.2),  # 偏离直线一点
        P(6.0, 6.0)
    ]
    
    # 设定误差阈值（单位：与坐标同维度）
    epsilon = 0.2
    
    # 执行压缩
    compressed_points = douglas_peucker(original_points, epsilon)
    
    # 输出结果
    print("原始路径点数量：", len(original_points))
    print("原始点序列：", original_points)
    print("\n压缩后路径点数量：", len(compressed_points))
    print("压缩后点序列：", compressed_points)