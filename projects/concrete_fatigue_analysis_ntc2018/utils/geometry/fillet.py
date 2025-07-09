import math

def normalize(v):
    mag = math.hypot(v[0], v[1])
    return (v[0] / mag, v[1] / mag)

def angle_from_point_y_up(origin, target):
    """
    origin 기준에서 target까지 벡터의 각도를 계산.
    기준: y축 양의 방향 = 0도
    방향: 반시계 방향
    범위: [0°, 360°)
    """
    x0, y0 = origin
    x1, y1 = target

    dx = x1 - x0
    dy = y1 - y0

    # y축 기준이므로 atan2(dx, dy)
    angle_rad = math.atan2(dx, dy)
    angle_deg = math.degrees(angle_rad)

    if angle_deg < 0:
        angle_deg += 360  # 보정하여 0~360 범위로

    return angle_deg

def foot_of_perpendicular(pt1, pt2, c):
    x1, y1 = pt1
    x2, y2 = pt2
    x0, y0 = c

    dx = x2 - x1
    dy = y2 - y1
    denom = dx*dx + dy*dy
    if denom == 0:
        return (x1, y1)  # 점과 점이 같을 경우

    t = ((x0 - x1) * dx + (y0 - y1) * dy) / denom
    fx = x1 + t * dx
    fy = y1 + t * dy
    return (fx, fy)

def apply_fillet(coordinates, radius):
    """
    주어진 y-z 평면 단면 좌표(coordinates)에 대해 필렛 반경(radius)을 적용하기 위한 함수의 시작 부분입니다.

    Parameters:
    - coordinates (dict): {"y": [...], "z": [...]} 형태의 딕셔너리로,
                        y, z는 같은 길이의 리스트이며 클로즈드 형태입니다.
    - radius (list): 각 점 사이에 적용할 필렛 반경 값의 리스트로,
                    길이는 len(coordinates["y"]) - 1 와 같아야 합니다.
                    0이면 필렛을 적용하지 않습니다.
    """

    # 유효성 검사
    y_coords  = coordinates.get("y", [])
    z_coords = coordinates.get("z", [])

    if len(y_coords) != len(z_coords):
        raise ValueError("y와 z 좌표 리스트의 길이가 같아야 합니다.")

    if len(radius) != len(y_coords) - 1:
        raise ValueError("radius 리스트의 길이는 좌표 개수보다 하나 적어야 합니다.")

    # 필렛 처리 로직 시작
    results = []
    for i, r in enumerate(radius):
        if r == None:
            continue
        
        # 앞뒤 점 인덱스
        idx1 = i - 1
        idx2 = i
        idx3 = i + 1
        
        # 점 좌표
        if i == 0:
            p1 = (y_coords[idx1-1], z_coords[idx1-1])
        else:
            p1 = (y_coords[idx1], z_coords[idx1])
        p2 = (y_coords[idx2], z_coords[idx2])
        p3 = (y_coords[idx3], z_coords[idx3])
        
        # 선분의 벡터
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        # 만약 두선의 벡터가 평행하다면, 필렛 적용 안함.
        if v1[0] * v2[1] - v1[1] * v2[0] == 0:
            continue
        nv1 = normalize(v1)
        nv2 = normalize(v2)
        
        # 각도 계산
        dot_product = nv1[0] * nv2[0] + nv1[1] * nv2[1]
        angle = math.acos(dot_product)
        
        # 두 벡터의 내각 방향으로 bisector 계산
        bisector = normalize((nv1[0] + nv2[0], nv1[1] + nv2[1]))
        
        # 필렛 중심까지의 거리
        d = r / math.sin(angle / 2)
        
        # 중심좌표
        center_y = p2[0] + bisector[0] * d
        center_z = p2[1] + bisector[1] * d
        
        # 수선의 좌표
        foot1 = foot_of_perpendicular(p1, p2, (center_y, center_z))
        foot2 = foot_of_perpendicular(p2, p3, (center_y, center_z))
        
        # 각도계산
        angle1 = angle_from_point_y_up((center_y, center_z), foot1)
        angle2 = angle_from_point_y_up((center_y, center_z), foot2)
        
        # 각도 증분 (5도 이하보다 작은 값으로 계산)
        angle_diff = abs(angle2 - angle1)
        if angle_diff < 180:
            num_points = int(angle_diff / 3)
            angle_step = angle_diff / num_points
            if angle1 > angle2:
                angle_step = -angle_step
        else:
            num_points = int((360 - angle_diff) / 3)
            angle_step = (360 - angle_diff) / num_points
            if angle1 < angle2:
                angle_step = -angle_step
        
        y_new_coords = []
        z_new_coords = []
        for step in range(num_points+1):
            y_new_coords.append(center_y + r * math.sin(math.radians(angle1 + angle_step * step)))
            z_new_coords.append(center_z + r * math.cos(math.radians(angle1 + angle_step * step)))
        
        results.append({
            "index": i,
            "center": (center_y, center_z),
            "angle_deg": math.degrees(angle),
            "radius": r,
            "foot1": foot1,
            "foot2": foot2,
            "angle1": angle1,
            "angle2": angle2,
            "num_points": num_points,
            "angle_step": angle_step,
            "y_new_coords": y_new_coords,
            "z_new_coords": z_new_coords
        })
    
    fillet_y_coords = []
    fillet_z_coords = []
    
    y_coords = y_coords[:-1]
    z_coords = z_coords[:-1]
    
    index_map = {item["index"]: item for item in results}
    index_list = [item["index"] for item in results]
    
    for i in range(len(y_coords)):
        if i in index_list:
            fillet_y_coords.extend(index_map[i]["y_new_coords"])
            fillet_z_coords.extend(index_map[i]["z_new_coords"])
        else:
            fillet_y_coords.append(y_coords[i])
            fillet_z_coords.append(z_coords[i])
    
    vertices= {
        "y": fillet_y_coords + [fillet_y_coords[0]],
        "z": fillet_z_coords + [fillet_z_coords[0]],
        "fillet_info": results
    }
    
    return vertices