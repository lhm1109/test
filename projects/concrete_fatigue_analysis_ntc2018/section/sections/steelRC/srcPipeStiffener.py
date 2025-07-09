from projects.concrete_fatigue_analysis_ntc2018.section.base.src_base import SRCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

import math

class SRCPipeStiffenerSection(SRCBaseSection):
    """DBUSER: Pipe with Stiffener Section"""
    
    def _get_section_shape(self):
        """Not Available"""
        return None
    
    def _get_dimensions_from_db_data(self, data_base):
        """Not Available"""
        return None
    
    def _get_dimensions_from_vsize(self, vSize):
        steel_size = vSize.get("steel_size", [])
        concrete_size = vSize.get("concrete_size", [])
        
        if len(steel_size) < 4:
            return None
        elif len(steel_size) > 4:
            steel_size = steel_size[:4]
        
        return {
            "steel_size": steel_size,
            "concrete_size": concrete_size
        }
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # 치수 추출
        D, tw, Hr, tr = dimensions["steel_size"]
        
        N1 = options["cell_shape"]
        
        r = (D - tw*2)/2
        
        # 좌표 생성
        outer_coords = ShapeGenerator.generate_circle_shape(D/2)

        # Stiffener 한 개의 내부 각도
        stiffener_angle = math.degrees(math.asin(tr/(2*r)))
        
        # 각 Stiffener 중심 각도
        ref_angle = []
        for i in range(N1):
            if i == 0:
                ref_angle.append(0)
            else:
                ref_angle.append(math.degrees(i*2*math.pi/N1))
        
        # 각 Stiffener 시작 각도와 끝 각도
        ref_angle_start_end = []
        for i in range(N1):
            if i == 0:
                ref_angle_start_end.append([360-stiffener_angle, stiffener_angle])
            else:
                ref_angle_start_end.append([ref_angle[i]-stiffener_angle, ref_angle[i]+stiffener_angle])
        
        # Stiffener 기준 좌표
        y1 = r*math.sin(math.radians(ref_angle_start_end[0][0]))
        y2 = r*math.sin(math.radians(ref_angle_start_end[0][1]))
        z1 = r*math.cos(math.radians(ref_angle_start_end[0][0]))
        z2 = r*math.cos(math.radians(ref_angle_start_end[0][0])) - Hr

        stiffener_coordinates = {
            "y":[y1, y1, y2, y2],
            "z":[z1, z2, z2, z1]
        }

        # 각 Stiffener 좌표들
        stiffener_coordinates_list = []
        for i in range(N1):
            if i == 0:
                stiffener_coordinates_list.append(stiffener_coordinates)
            else:
                results = TransFormGeometry.rotate_coordinates(stiffener_coordinates, ref_angle[i]*-1)
                stiffener_coordinates_list.append(results)
        
        # 각 스티프너 사이들의 좌표
        arc_coordinates_list = []
        if N1 == 1:
            results = ShapeGenerator.generate_arc_shape(r, ref_angle_start_end[0][1], ref_angle_start_end[0][0], include_endpoints=False)
            arc_coordinates_list.append(results)
        else:
            for i in range(N1):
                if i == (N1-1):
                    results = ShapeGenerator.generate_arc_shape(r, ref_angle_start_end[i][1], ref_angle_start_end[0][0], include_endpoints=False)
                else:
                    results = ShapeGenerator.generate_arc_shape(r, ref_angle_start_end[i][1], ref_angle_start_end[i+1][0], include_endpoints=False)
                
                reversed_results = TransFormGeometry.reverse_coordinates_list(results)
                arc_coordinates_list.append(reversed_results)
        
        # 좌표 조합
        for i in range(N1):
            if i == 0:
                merged_coordinates = TransFormGeometry.merge_coordinates(stiffener_coordinates_list[i], arc_coordinates_list[i])
            else:
                merged_coordinates = TransFormGeometry.merge_coordinates(merged_coordinates, stiffener_coordinates_list[i])
                merged_coordinates = TransFormGeometry.merge_coordinates(merged_coordinates, arc_coordinates_list[i])
        
        closed_inner_coords = TransFormGeometry.close_polygon(merged_coordinates)
        
        # 콘크리트 좌표 추출
        yci_c = closed_inner_coords["y"].copy()
        zci_c = closed_inner_coords["z"].copy()
        
        yci_c.reverse()
        zci_c.reverse()
        
        # 기준 좌표 추출
        point_1_s = [0, D/2]
        point_2_s = [D/2, 0]
        point_3_s = [0, -D/2]
        point_4_s = [-D/2, 0]
        
        point_1_c = [0, (D-tw*2)/2]
        point_2_c = [(D-tw*2)/2, 0]
        point_3_c = [0, -(D-tw*2)/2]
        point_4_c = [-(D-tw*2)/2, 0]
        
        yt = max(outer_coords["y"], yci_c)
        yb = min(outer_coords["y"], yci_c)
        zt = max(outer_coords["z"], zci_c)
        zb = min(outer_coords["z"], zci_c)
        
        # 재료 값
        stif_factor = options["matl_stif_factor"]
        steel_elast = 1.0
        concrete_elast = 1.0 / options["matl_elast"] * stif_factor
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": outer_coords["y"],
                    "z": outer_coords["z"],
                    "reference": {
                        "name": "steel",
                        "elast": steel_elast
                    }
                },
                {
                    "y": yci_c,
                    "z": zci_c,
                    "reference": {
                        "name": "concrete",
                        "elast": concrete_elast
                    }
                }   
            ],
            "inner": [
                {
                    "y": closed_inner_coords["y"],
                    "z": closed_inner_coords["z"],
                    "reference": {
                        "name": "steel",
                        "elast": steel_elast
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points = {
            "steel": {
                "point_1": point_1_s,
                "point_2": point_2_s,
                "point_3": point_3_s,
                "point_4": point_4_s
            },
            "concrete": {
                "point_1": point_1_c,
                "point_2": point_2_c,
                "point_3": point_3_c,
                "point_4": point_4_c,
            },
            "total": {
                "point_1": point_1_s,
                "point_2": point_2_s,
                "point_3": point_3_s,
                "point_4": point_4_s
            },
            "extreme_fiber": {
                "yt": yt,
                "yb": yb,
                "zt": zt,
                "zb": zb
            }
        }
        
        # 특성 컨트롤 데이터
        properties_control = {
            "name": ["steel", "concrete"],
            "control": "steel"
        }
        
        return vertices, reference_points, properties_control
