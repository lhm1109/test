from projects.concrete_fatigue_analysis_ntc2018.section.base.src_base import SRCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

import math

class RectPipeCloseSection(SRCBaseSection):
    """SRC: RectPipeClose Section"""
    
    def _get_section_shape(self):
        return "Pipe"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)
        
        return [
            dimension.get("d",0)*unit_conversion_factor,
            dimension.get("tw",0)*unit_conversion_factor
        ]
    
    def _get_dimensions_from_vsize(self, vSize):
        
        steel_size = vSize.get("steel_size", [])
        concrete_size = vSize.get("concrete_size", [])
        
        if len(steel_size) < 2:
            return None
        elif len(steel_size) > 2:
            steel_size = steel_size[:2]
        
        if len(concrete_size) < 2:
            return None
        elif len(concrete_size) > 2:
            concrete_size = concrete_size[:2]
        
        return {
            "steel_size": steel_size,
            "concrete_size": concrete_size
        }
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # 치수 추출
        D, tw= dimensions["steel_size"]
        Hc, Bc = dimensions["concrete_size"]
        
        # 강재 단면 생성
        radius_outer = D / 2
        radius_inner = D / 2 - tw
        
        steel_outer = ShapeGenerator.generate_circle_shape(radius_outer)
        results_inner = ShapeGenerator.generate_circle_shape(radius_inner)
        steel_inner = TransFormGeometry.reverse_coordinates_list(results_inner)
        
        yco_s = steel_outer["y"]
        zco_s = steel_outer["z"]
        
        yci_s = steel_inner["y"]
        zci_s = steel_inner["z"]
        
        # 콘크리트 단면 생성
        yco_c = [-Bc/2, -Bc/2, Bc/2, Bc/2, -Bc/2]
        zco_c = [Hc/2, -Hc/2, -Hc/2, Hc/2, Hc/2]
        
        yci_c = yco_s.copy()
        zci_c = zco_s.copy()
        
        yci_c.reverse()
        zci_c.reverse()
        
        yco_c_2 = yci_s.copy()
        zco_c_2 = zci_s.copy()
        
        yco_c_2.reverse()
        zco_c_2.reverse()
        
        # 기준 좌표 추출
        point_1_s = [0, D/2]
        point_2_s = [D/2, 0]
        point_3_s = [0, -D/2]
        point_4_s = [-D/2, 0]
        
        point_1_c_encase = [yco_c[0], zco_c[0]]
        point_2_c_encase = [yco_c[3], zco_c[3]]
        point_3_c_encase = [yco_c[2], zco_c[2]]
        point_4_c_encase = [yco_c[1], zco_c[1]]
        
        point_1_c_infill = [0, (D-2*tw)/2]
        point_2_c_infill = [(D-2*tw)/2, 0]
        point_3_c_infill = [0, -(D-2*tw)/2]
        point_4_c_infill = [-(D-2*tw)/2, 0]
        
        yt = max(yco_s, yco_c, yco_c_2)
        yb = min(yco_s, yco_c, yco_c_2)
        zt = max(zco_s, zco_c, zco_c_2)
        zb = min(zco_s, zco_c, zco_c_2)
        
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
                        "name": "concrete_encase",
                        "elast": concrete_elast
                    }
                },
                {
                    "y": yco_c_2,
                    "z": zco_c_2,
                    "reference": {
                        "name": "concrete_infill",
                        "elast": concrete_elast
                    }
                }
            ],
            "inner": [
                {
                    "y": yci_s,
                    "z": zci_s,
                    "reference": {
                        "name": "steel",
                        "elast": steel_elast
                    }
                },
                {
                    "y": yci_c,
                    "z": zci_c,
                    "reference": {
                        "name": "concrete_encase",
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
            "concrete_encase": {
                "point_1": point_1_c_encase,
                "point_2": point_2_c_encase,
                "point_3": point_3_c_encase,
                "point_4": point_4_c_encase
            },
            "concrete_infill": {
                "point_1": point_1_c_infill,
                "point_2": point_2_c_infill,
                "point_3": point_3_c_infill,
                "point_4": point_4_c_infill
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
            "name": ["steel", "concrete_encase", "concrete_infill"],
            "control": "steel"
        }
        
        return vertices, reference_points, properties_control
    