from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

import math

class StarBattenedAngleSection(DBUserValueBaseSection):
    """DBUSER: Star Battened Angle Section"""
    
    def _get_section_shape(self):
        return "Angle"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)
        
        return {
            "H": dimension.get("h",0)*unit_conversion_factor,
            "B": dimension.get("b",0)*unit_conversion_factor,
            "tw": dimension.get("tw",0)*unit_conversion_factor,
            "tf": dimension.get("tf",0)*unit_conversion_factor,
            "r1": dimension.get("r1",0)*unit_conversion_factor,
            "r2": dimension.get("r2",0)*unit_conversion_factor
        }
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 5:
            return None
        elif len(vSize) > 5:
            vSize = vSize[:5]
        
        return {
            "H": vSize[0],
            "B": vSize[1],
            "tw": vSize[2],
            "tf": vSize[3],
            "C": vSize[4]
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        tw = dimensions["tw"]
        tf = dimensions["tf"]
        C = dimensions["C"]
        
        # 좌표 생성
        l_shape_coords = ShapeGenerator.generate_l_shape(H, B, tw, tf)
        
        left_angle = TransFormGeometry.mirror_coordinates(l_shape_coords, "z")
        reverse_left_angle = TransFormGeometry.reverse_coordinates_list(left_angle)

        right_angle = TransFormGeometry.mirror_coordinates(l_shape_coords, "y")
        reverse_right_angle = TransFormGeometry.reverse_coordinates_list(right_angle)
        
        if not math.isclose(C, 0.0, abs_tol=1e-9):
            reverse_left_angle = TransFormGeometry.translate_coordinates(reverse_left_angle, -C/2, -C/2)
            reverse_right_angle = TransFormGeometry.translate_coordinates(reverse_right_angle, C/2, C/2)
        
        ycor = reverse_right_angle["y"]
        zcor = reverse_right_angle["z"]
        
        ycol = reverse_left_angle["y"]
        zcol = reverse_left_angle["z"]
        
        # 기준 좌표 추출
        point_1_right = [ycor[0], zcor[0]]
        point_2_right = [ycor[1], zcor[1]]
        point_3_right = [ycor[4], zcor[4]]
        point_4_right = [ycor[5], zcor[5]]

        point_1_left = [ycol[0], zcol[0]]
        point_2_left = [ycol[1], zcol[1]]
        point_3_left = [ycol[4], zcol[4]]
        point_4_left = [ycol[5], zcol[5]]

        point_1_total = [-(B + C/2), -(tf + C/2)]
        point_2_total = [(tw + C/2), (H + C/2)]
        point_3_total = [(B + C/2), (tf + C/2)]
        point_4_total = [-(tw + C/2), -(H + C/2)]
        
        yt = max(ycor, ycol)
        yb = min(ycor, ycol)
        zt = max(zcor, zcol)
        zb = min(zcor, zcol)
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": ycor,
                    "z": zcor,
                    "reference": {
                        "name": "star_battened_angle_right",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycol,
                    "z": zcol,
                    "reference": {
                        "name": "star_battened_angle_left",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points = {
            "star_battened_angle_right": {
                "point_1": point_1_right,
                "point_2": point_2_right,
                "point_3": point_3_right,
                "point_4": point_4_right
            },
            "star_battened_angle_left": {
                "point_1": point_1_left,
                "point_2": point_2_left,
                "point_3": point_3_left,
                "point_4": point_4_left
            },
            "total": {
                "point_1": point_1_total,
                "point_2": point_2_total,
                "point_3": point_3_total,
                "point_4": point_4_total
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
            "name": ["star_battened_angle_right", "star_battened_angle_left"],
            "control": "star_battened_angle_right"
        }
        
        return vertices, reference_points, properties_control
    