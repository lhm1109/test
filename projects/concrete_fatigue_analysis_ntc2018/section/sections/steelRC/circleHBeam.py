from projects.concrete_fatigue_analysis_ntc2018.section.base.src_base import SRCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

import math

class CircleHBeamSection(SRCBaseSection):
    """DBUSER: CircleHBeam Section"""
    
    def _get_section_shape(self):
        return "H_Section"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)
        
        return [
            dimension.get("h",0)*unit_conversion_factor,
            dimension.get("b1",0)*unit_conversion_factor,
            dimension.get("tw",0)*unit_conversion_factor,
            dimension.get("tf1",0)*unit_conversion_factor,
            dimension.get("b2",0)*unit_conversion_factor,
            dimension.get("tf2",0)*unit_conversion_factor,
            dimension.get("r1",0)*unit_conversion_factor,
            dimension.get("r2",0)*unit_conversion_factor
        ]
    
    def _get_dimensions_from_vsize(self, vSize):
        
        steel_size = vSize.get("steel_size", [])
        concrete_size = vSize.get("concrete_size", [])
        
        if len(steel_size) < 8:
            return None
        elif len(steel_size) > 8:
            steel_size = steel_size[:8]
        
        if len(concrete_size) < 1:
            return None
        elif len(concrete_size) > 1:
            concrete_size = concrete_size[:2]
        
        return {
            "steel_size": steel_size,
            "concrete_size": concrete_size
        }
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # 치수 추출
        H, B1, tw, tf1, B2, tf2, r1, r2 = dimensions["steel_size"]
        Hc = dimensions["concrete_size"][0]
        
        # 강재 단면 생성
        h_shape_coords = ShapeGenerator.generate_h_shape(H, B1, tw, tf1, B2, tf2)
        
        yco_s = h_shape_coords["y"]
        zco_s = h_shape_coords["z"]
        
        # 원점 좌표로 이동 (Center of Section)
        yo_s = TransFormGeometry.calculate_origin_coordinates(yco_s)
        zo_s = TransFormGeometry.calculate_origin_coordinates(zco_s)

        yco_s = [y - yo_s for y in yco_s]
        zco_s = [z - zo_s for z in zco_s]
        
        # 콘크리트 단면 생성
        concrete = ShapeGenerator.generate_circle_shape(Hc / 2)
        yco_c = concrete["y"]
        zco_c = concrete["z"]
        
        yci_c = yco_s.copy()
        zci_c = zco_s.copy()
        
        yci_c.reverse()
        zci_c.reverse()
        
        # 기준 좌표 추출
        point_1_s = [yco_s[0], zco_s[0]]
        point_2_s = [yco_s[11], zco_s[11]]
        point_3_s = [yco_s[6], zco_s[6]]
        point_4_s = [yco_s[5], zco_s[5]]
        
        point_1_c = [0, Hc/2]
        point_2_c = [Hc/2, 0]
        point_3_c = [0, -Hc/2]
        point_4_c = [-Hc/2, 0]
        
        yt = max(yco_s, yco_c)
        yb = min(yco_s, yco_c)
        zt = max(zco_s, zco_c)
        zb = min(zco_s, zco_c)
        
        # 재료 값
        stif_factor = options["matl_stif_factor"]
        steel_elast = 1.0
        concrete_elast = 1.0 / options["matl_elast"] * stif_factor
        
        # 좌표 반환
        vertices= {
            "outer": [
                {
                    "y": yco_s,
                    "z": zco_s,
                    "reference": {
                        "name": "steel",
                        "elast": steel_elast
                    }
                },
                {
                    "y": yco_c,
                    "z": zco_c,
                    "reference": {
                        "name": "concrete",
                        "elast": concrete_elast
                    }
                }
            ],
            "inner": [
                {
                    "y": yci_c,
                    "z": zci_c,
                    "reference": {
                        "name": "concrete",
                        "elast": concrete_elast
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
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
                "point_4": point_4_c
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
    