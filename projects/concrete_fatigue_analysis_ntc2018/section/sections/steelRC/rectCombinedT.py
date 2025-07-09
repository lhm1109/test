from projects.concrete_fatigue_analysis_ntc2018.section.base.src_base import SRCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

import math

class RectCombinedTSection(SRCBaseSection):
    """SRC: RectCombinedT Section"""
    
    def _get_section_shape(self):
        """H_Section, T_Section"""
        return "H_Section", "T_Section"
    
    def _get_dimensions_from_db_data(self, data_base):
        """재검토 필요"""
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
        H, B, tw, tf, Ht, Bt, twt, tft = dimensions["steel_size"]
        Hc, Bc = dimensions["concrete_size"]
        
        # 강재 H 단면 생성
        h_shape_coords = ShapeGenerator.generate_h_shape(H, B, tw, tf, B, tf)
        
        ycoh_s = h_shape_coords["y"]
        zcoh_s = h_shape_coords["z"]
        
        # 강재 T 단면 생성
        t_shape_coords = ShapeGenerator.generate_t_shape(Ht, Bt, twt, tft)
        rotated_t_shape_coords = TransFormGeometry.rotate_coordinates(t_shape_coords, 90)
        left_coords = TransFormGeometry.translate_coordinates(rotated_t_shape_coords, -Ht-tw/2, -H/2)
        
        ycotl_s = left_coords["y"]
        zcotl_s = left_coords["z"]

        # 원점 좌표로 이동 (Center of Section)
        yo_s = TransFormGeometry.calculate_origin_coordinates(ycoh_s, ycotl_s)
        zo_s = TransFormGeometry.calculate_origin_coordinates(zcoh_s, zcotl_s)

        ycoh_s = [y - yo_s for y in ycoh_s]
        zcoh_s = [z - zo_s for z in zcoh_s]
        ycotl_s = [y - yo_s for y in ycotl_s]
        zcotl_s = [z - zo_s for z in zcotl_s]
        
        # 콘크리트 단면 생성
        yco_c = [-Bc/2, -Bc/2, Bc/2, Bc/2, -Bc/2]
        zco_c = [Hc/2, -Hc/2, -Hc/2, Hc/2, Hc/2]
        
        ycih_c = ycoh_s.copy()
        zcih_c = zcoh_s.copy()
        
        ycih_c.reverse()
        zcih_c.reverse()
        
        ycitl_c = ycotl_s.copy()
        zcitl_c = zcotl_s.copy()
        
        ycitl_c.reverse()
        zcitl_c.reverse()
        
        # 기준 좌표 추출
        point_1_s_h = [0, H/2]
        point_2_s_h = [(Ht+B/2-tw/2)/2, 0]
        point_3_s_h = [0, -H/2]
        point_4_s_h = [-(Ht+B/2-tw/2)/2, 0]
        
        point_1_s_t = [0, Ht/2]
        point_2_s_t = [(Ht+Bt/2-twt/2)/2, 0]
        point_3_s_t = [0, -Ht/2]
        point_4_s_t = [-(Ht+Bt/2-twt/2)/2, 0]
        
        point_1_c = [yco_c[0], zco_c[0]]
        point_2_c = [yco_c[3], zco_c[3]]
        point_3_c = [yco_c[2], zco_c[2]]
        point_4_c = [yco_c[1], zco_c[1]]
        
        yt = max(ycoh_s, ycotl_s, yco_c)
        yb = min(ycoh_s, ycotl_s, yco_c)
        zt = max(zcoh_s, zcotl_s, zco_c)
        zb = min(zcoh_s, zcotl_s, zco_c)
        
        # 재료 값
        stif_factor = options["matl_stif_factor"]
        steel_elast = 1.0
        concrete_elast = 1.0 / options["matl_elast"] * stif_factor
        
        # 좌표 반환
        vertices= {
            "outer": [
                {
                    "y": ycoh_s,
                    "z": zcoh_s,
                    "reference": {
                        "name": "steel_h_shape",
                        "elast": steel_elast
                    }
                },
                {
                    "y": ycotl_s,
                    "z": zcotl_s,
                    "reference": {
                        "name": "steel_t_shape",
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
                    "y": ycih_c,
                    "z": zcih_c,
                    "reference": {
                        "name": "concrete",
                        "elast": concrete_elast
                    }
                },
                {
                    "y": ycitl_c,
                    "z": zcitl_c,
                    "reference": {
                        "name": "concrete",
                        "elast": concrete_elast
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "steel_h_shape": {
                "point_1": point_1_s_h,
                "point_2": point_2_s_h,
                "point_3": point_3_s_h,
                "point_4": point_4_s_h
            },
            "steel_t_shape": {
                "point_1": point_1_s_t,
                "point_2": point_2_s_t,
                "point_3": point_3_s_t,
                "point_4": point_4_s_t
            },
            "concrete": {
                "point_1": point_1_c,
                "point_2": point_2_c,
                "point_3": point_3_c,
                "point_4": point_4_c
            },
            "total": {
                "point_1": point_1_c,
                "point_2": point_2_c,
                "point_3": point_3_c,
                "point_4": point_4_c
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
            "name": ["steel_h_shape", "steel_t_shape", "concrete"],
            "control": "steel_h_shape"
        }
        
        return vertices, reference_points, properties_control
    