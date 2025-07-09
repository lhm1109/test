from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

import math

class BoxSection(DBUserValueBaseSection):
    """DBUSER: Box Shape Section"""
    
    def _get_section_shape(self):
        return "Box"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)
        
        return {
            "H": dimension.get("h",0)*unit_conversion_factor,
            "B": dimension.get("b",0)*unit_conversion_factor,
            "tw": dimension.get("tw",0)*unit_conversion_factor,
            "tf1": dimension.get("tf1",0)*unit_conversion_factor,
            "C": dimension.get("c",0)*unit_conversion_factor,
            "tf2": dimension.get("tf2",0)*unit_conversion_factor
        }
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 6:
            return None
        elif len(vSize) > 6:
            vSize = vSize[:6]
        
        return {
            "H": vSize[0],
            "B": vSize[1],
            "tw": vSize[2],
            "tf1": vSize[3],
            "C": vSize[4],
            "tf2": vSize[5]
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        tw = dimensions["tw"]
        tf1 = dimensions["tf1"]
        C = dimensions["C"]
        tf2 = dimensions["tf2"]
        
        # 좌표 생성
        box_shape_coords = ShapeGenerator.generate_box_shape(H, B, tw, tf1, C, tf2)
        
        outer_coords = box_shape_coords["outer"]
        inner_coords = box_shape_coords["inner"]
        
        reverse_inner_coords = TransFormGeometry.reverse_coordinates_list(inner_coords)
        
        yco = outer_coords["y"]
        zco = outer_coords["z"]
        yci = reverse_inner_coords["y"]
        zci = reverse_inner_coords["z"]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(yco)
        zo = TransFormGeometry.calculate_origin_coordinates(zco)
        
        yco = [y - yo for y in yco]
        zco = [z - zo for z in zco]
        yci = [y - yo for y in yci]
        zci = [z - zo for z in zci]
        
        # 기준 좌표 추출
        point_1 = [yco[0], zco[0]]
        point_2 = [yco[11], zco[11]]
        point_3 = [yco[6], zco[6]]
        point_4 = [yco[5], zco[5]]
        
        yt = max(yco)
        yb = min(yco)
        zt = max(zco)
        zb = min(zco)
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": yco,
                    "z": zco,
                    "reference": {
                        "name": "box",
                        "elast": 1.0
                    }
                }
            ],
            "inner": [
                {
                    "y": yci,
                    "z": zci,
                    "reference": {
                        "name": "box",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "box": {
                "point_1": point_1,
                "point_2": point_2,
                "point_3": point_3,
                "point_4": point_4,
            },
            "total": {
                "point_1": point_1,
                "point_2": point_2,
                "point_3": point_3,
                "point_4": point_4,
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
            "name": ["box"],
            "control": "box"
        }
        
        return vertices, reference_points, properties_control
    