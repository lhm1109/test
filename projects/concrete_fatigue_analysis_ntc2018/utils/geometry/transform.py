from shapely.geometry import Polygon, LineString, Point, LinearRing
from shapely.ops import split

import numpy as np
import math

class TransFormGeometry:
    """
    기본 형상 변형 클래스
    y-z 평면을 기본으로 한다.
    """
    
    @staticmethod
    def mirror_coordinates(coordinates, mirror_axis):
        """
        좌표 반전
        
        Args:
            coordinates (list): 좌표 리스트
            axis (str): 반전할 축 (y, z)
            
        Returns:
            list: 반전된 좌표 리스트
        
        input_example = {
            "y": [0, 0, 0, 0],
            "z": [0, 0, 0, 0]
        }
        """
        if mirror_axis == "y":
            return {
                "y": coordinates["y"],
                "z": [-z for z in coordinates["z"]]
            }
        elif mirror_axis == "z":
            return {
                "y": [-y for y in coordinates["y"]],
                "z": coordinates["z"]
            }
    
    @staticmethod
    def translate_coordinates(coordinates, y_offset = 0, z_offset = 0):
        """
        좌표 이동
        
        Args:
            coordinates (list): 좌표 리스트
            y (float): y 좌표 이동 거리
            z (float): z 좌표 이동 거리
            
        Returns:
            list: 이동된 좌표 리스트
        """
        
        return {
            "y": [y + y_offset for y in coordinates["y"]],
            "z": [z + z_offset for z in coordinates["z"]]
        }

    @staticmethod
    def reverse_coordinates_list(coordinates):
        """
        리스트를 역순으로 반환해 준다.
        
        Args:
            coordinates (list): 좌표 리스트
            
        Returns:
            list: 역순으로 반환된 좌표 리스트
        """
        return {
            "y": coordinates["y"][::-1],
            "z": coordinates["z"][::-1]
        }

    @staticmethod
    def merge_coordinates(coord1, coord2):
        return {
            "y": coord1["y"] + coord2["y"],
            "z": coord1["z"] + coord2["z"]
        }
        
    @staticmethod
    def close_polygon(coords):
        if (coords["y"][0], coords["z"][0]) == (coords["y"][-1], coords["z"][-1]):
            return coords  # 이미 폐곡선이면 그대로 반환
        return {
            "y": coords["y"] + [coords["y"][0]],
            "z": coords["z"] + [coords["z"][0]]
        }

    @staticmethod
    def angle_between_three_points(p1, p2, p3):
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        def normalize(v):
            mag = math.hypot(v[0], v[1])
            return (v[0] / mag, v[1] / mag)
        
        if v1[0] * v2[1] - v1[1] * v2[0] == 0:
            return math.pi, 180

        nv1 = normalize(v1)
        nv2 = normalize(v2)
        
        dot_product = nv1[0] * nv2[0] + nv1[1] * nv2[1]
        
        angle_rad = math.acos(dot_product)
        angle_deg = math.degrees(angle_rad)

        return angle_rad, angle_deg
    
    @staticmethod
    def rotate_coordinates(coordinates, angle, origin=(0, 0)):
        """
        좌표 회전 (반시계방향 회전)
        
        angle - 회전 각도 (단위: 도)
        origin - 회전 중심점 (단위: 픽셀)
        """
        yc, zc = origin
        angle_rad = np.radians(angle)

        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)

        rotated_y = []
        rotated_z = []

        for y, z in zip(coordinates['y'], coordinates['z']):
            # 중심점 기준으로 평행이동
            dy = y - yc
            dz = z - zc

            # 회전 행렬 적용
            ry = cos_a * dy - sin_a * dz
            rz = sin_a * dy + cos_a * dz

            # 다시 원래 위치로 복귀
            rotated_y.append(ry + yc)
            rotated_z.append(rz + zc)

        return {"y": rotated_y, "z": rotated_z}

    @staticmethod
    def calculate_origin_coordinates(*coordinate_lists):
        """
        여러 개의 좌표 리스트를 받아 중심을 계산한다
        
        Args:
            *coordinates (list): 좌표 리스트
            
        Returns:
            float: 중심
        """
        
        combined_list = []
        for coord_list in coordinate_lists:
            combined_list.extend(coord_list)
        
        result = max(combined_list) - (max(combined_list) - min(combined_list)) / 2
        
        return result
    
    @staticmethod
    def cut_polygons(outers, inners, cut_axis='y', cut_value=0.0):
        def ensure_winding(coords, clockwise=False):
            """Ensure ring orientation: outer (CCW), inner (CW)"""
            ring = LinearRing(coords)
            if clockwise:
                return list(coords) if not ring.is_ccw else list(coords)[::-1]
            else:
                return list(coords) if ring.is_ccw else list(coords)[::-1]

        def coords_to_dict(coords):
            y_coords, z_coords = zip(*coords)
            return {"y": list(y_coords), "z": list(z_coords)}

        result = {
            "positive": {"outer": [], "inner": []},
            "negative": {"outer": [], "inner": []}
        }

        # 절단선 정의
        if cut_axis == 'y':
            all_z = [z for poly in outers for z in poly["z"]]
            min_z, max_z = min(all_z), max(all_z)
            cutting_line = LineString([(cut_value, min_z - 10), (cut_value, max_z + 10)])
            coord_idx = 0  # index 0: y
        elif cut_axis == 'z':
            all_y = [y for poly in outers for y in poly["y"]]
            min_y, max_y = min(all_y), max(all_y)
            cutting_line = LineString([(min_y - 10, cut_value), (max_y + 10, cut_value)])
            coord_idx = 1  # index 1: z
        else:
            raise ValueError("cut_axis must be 'y' or 'z'")

        # inner polygon 객체 생성
        inner_polygons = []
        for inner in inners or []:
            coords = list(zip(inner["y"], inner["z"]))
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            poly = Polygon(coords)
            inner_polygons.append(poly)

        # outer polygon 처리
        for outer in outers:
            outer_coords = list(zip(outer["y"], outer["z"]))
            if outer_coords[0] != outer_coords[-1]:
                outer_coords.append(outer_coords[0])
            outer_poly = Polygon(outer_coords)

            # 이 outer에 포함된 inner 검색
            matched_holes = []
            for inner in inner_polygons:
                if outer_poly.contains(inner):
                    matched_holes.append(list(inner.exterior.coords))

            # 복합 polygon 생성
            compound = Polygon(outer_coords, holes=matched_holes)

            try:
                parts = split(compound, cutting_line)
            except Exception:
                continue

            for part in parts.geoms:
                side = "positive" if part.centroid.coords[0][coord_idx] >= cut_value else "negative"

                # 외곽: 반시계 방향 보정
                outer_coords = ensure_winding(part.exterior.coords, clockwise=False)
                result[side]["outer"].append(coords_to_dict(outer_coords))

                # 구멍들: 시계 방향 보정
                for ring in part.interiors:
                    inner_coords = ensure_winding(ring.coords, clockwise=True)
                    result[side]["inner"].append(coords_to_dict(inner_coords))

        return result