from projects.concrete_fatigue_analysis_ntc2018.section.base.combined_base import CombinedBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.fillet import apply_fillet

import math

class T21CombinedSection(CombinedBaseSection):
    """COMBINED: 2T(Web Opened H) Section"""
    
    def _get_section_shape(self):
        """A"""
        return "H_Section"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)

        return {
            "H": dimension.get("h",0)*unit_conversion_factor,
            "B1": dimension.get("b1",0)*unit_conversion_factor,
            "tw": dimension.get("tw",0)*unit_conversion_factor,
            "tf1": dimension.get("tf1",0)*unit_conversion_factor,
            "B2": dimension.get("b2",0)*unit_conversion_factor,
            "tf2": dimension.get("tf2",0)*unit_conversion_factor,
            "r1": dimension.get("r1",0)*unit_conversion_factor,
            "r2": dimension.get("r2",0)*unit_conversion_factor
        }
    
    def _get_dimensions_from_vsize(self, vSize_i, vSize_j):
        
        if len(vSize_i) < 5:
            return None
        elif len(vSize_i) > 5:
            vSize_i = vSize_i[:5]

        if len(vSize_j) < 4:
            return None
        elif len(vSize_j) > 4:
            vSize_j = vSize_j[:4]
        
        return {
            "Ht": vSize_i[0],
            "Bt": vSize_i[1],
            "twt": vSize_i[2],
            "tft": vSize_i[3],
            "C": vSize_i[4],
            "Hb": vSize_j[0],
            "Bb": vSize_j[1],
            "twb": vSize_j[2],
            "tfb": vSize_j[3]
        }
    
    def _generate_shape_vertices(self, dimensions):
        
        # 치수 추출
        Ht = dimensions["Ht"]
        Bt = dimensions["Bt"]
        twt = dimensions["twt"]
        tft = dimensions["tft"]
        C = dimensions["C"]
        Hb = dimensions["Hb"]
        Bh = dimensions["Bb"]
        twb = dimensions["twb"]
        tfb = dimensions["tfb"]
        
        # 좌표 생성
        tt_shape_coords = ShapeGenerator.generate_t_shape(Ht, Bt, twt, tft)
        tb_shape_coords = ShapeGenerator.generate_t_shape(Hb, Bh, twb, tfb)
        
        rotated_tb_shape_coords = TransFormGeometry.rotate_coordinates(tb_shape_coords, 180)
        trans_tb_shape_coords = TransFormGeometry.translate_coordinates(rotated_tb_shape_coords, 0, -Ht-Hb-C)

        ycot = tt_shape_coords["y"]
        zcot = tt_shape_coords["z"]
        
        ycob = trans_tb_shape_coords["y"]
        zcob = trans_tb_shape_coords["z"]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(ycob, ycot)
        zo = TransFormGeometry.calculate_origin_coordinates(zcob, zcot)

        ycot = [y - yo for y in ycot]
        zcot = [z - zo for z in zcot]
        
        ycob = [y - yo for y in ycob]
        zcob = [z - zo for z in zcob]
        
        # 기준 좌표 추출
        point_1 = [ycot[0], zcot[0]]
        point_2 = [ycot[-2], zcot[-2]]
        point_3 = [ycob[0], zcob[0]]
        point_4 = [ycob[-2], zcob[-2]]
        
        point_1_h_t = [ycot[0], zcot[0]]
        point_2_h_t = [ycot[-2], zcot[-2]]
        point_3_h_t = [ycot[4], zcot[4]]
        point_4_h_t = [ycot[3], zcot[3]]
        
        point_1_h_b = [ycob[0], zcob[0]]
        point_2_h_b = [ycob[-2], zcob[-2]]
        point_3_h_b = [ycob[4], zcob[4]]
        point_4_h_b = [ycob[3], zcob[3]]
        
        yt = max(ycot, ycob)
        yb = min(ycot, ycob)
        zt = max(zcot, zcob)
        zb = min(zcot, zcob)
        
        # # 필렛 적용
        # r1_fin = r1 if not math.isclose(r1, 0.0, abs_tol=1e-9) else None
        # r2_fin = r2 if not math.isclose(r2, 0.0, abs_tol=1e-9) else None
        
        # if not (r1_fin is None and r2_fin is None):
        #     transformed_coords = apply_fillet({"y": yco, "z": zco}, [None, None, None, r2_fin, r1_fin, r1_fin, r2_fin, None])
        #     yco = transformed_coords["y"]
        #     zco = transformed_coords["z"]
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": ycob,
                    "z": zcob,
                    "reference": {
                        "name": "t_top",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycot,
                    "z": zcot,
                    "reference": {
                        "name": "t_bottom",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "t_top": {
                "point_1": point_1_h_t,
                "point_2": point_2_h_t,
                "point_3": point_3_h_t,
                "point_4": point_4_h_t
            },
            "t_bottom": {
                "point_1": point_1_h_b,
                "point_2": point_2_h_b,
                "point_3": point_3_h_b,
                "point_4": point_4_h_b
            },
            "total": {
                "point_1": point_1,
                "point_2": point_2,
                "point_3": point_3,
                "point_4": point_4
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
            "name": ["t_top", "t_bottom"],
            "control": "t_top"
        }
        
        return vertices, reference_points, properties_control
