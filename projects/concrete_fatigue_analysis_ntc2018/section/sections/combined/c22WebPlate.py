from projects.concrete_fatigue_analysis_ntc2018.section.base.combined_base import CombinedBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.fillet import apply_fillet

import math

class C22WebPlateSection(CombinedBaseSection):
    """COMBINED: 2C with Web Plate 2 Section"""
    
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
        
        if len(vSize_i) < 4:
            return None
        elif len(vSize_i) > 4:
            vSize_i = vSize_i[:4]

        if len(vSize_j) < 2:
            return None
        elif len(vSize_j) > 2:
            vSize_j = vSize_j[:2]
        
        return {
            "H": vSize_i[0],
            "B": vSize_i[1],
            "tw": vSize_i[2],
            "tf": vSize_i[3],
            "Bs": vSize_j[0],
            "ts": vSize_j[1],
        }
    
    def _generate_shape_vertices(self, dimensions):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        tw = dimensions["tw"]
        tf = dimensions["tf"]
        Bs = dimensions["Bs"]
        ts = dimensions["ts"]
        
        # 좌표 생성
        c_shape_coords = ShapeGenerator.generate_c_shape(H, B, tw, tf, B, tf)
        
        rotated_ct_shape_coords = TransFormGeometry.rotate_coordinates(c_shape_coords, 270)
        rotated_cb_shape_coords = TransFormGeometry.rotate_coordinates(c_shape_coords, 90)
        
        trans_ct_shape_coords = TransFormGeometry.translate_coordinates(rotated_ct_shape_coords, H/2, Bs/2+tw)
        trans_cb_shape_coords = TransFormGeometry.translate_coordinates(rotated_cb_shape_coords, -H/2, -Bs/2-tw)
        
        ycot = trans_ct_shape_coords["y"]
        zcot = trans_ct_shape_coords["z"]
        
        ycob = trans_cb_shape_coords["y"]
        zcob = trans_cb_shape_coords["z"]
        
        ycop = [-ts/2, -ts/2, ts/2, ts/2, -ts/2]
        zcop = [Bs/2, -Bs/2, -Bs/2, Bs/2, Bs/2]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(ycot, ycob, ycop)
        zo = TransFormGeometry.calculate_origin_coordinates(zcot, zcob, zcop)
        
        ycot = [y - yo for y in ycot]
        zcot = [z - zo for z in zcot]
        
        ycob = [y - yo for y in ycob]
        zcob = [z - zo for z in zcob]
        
        ycop = [y - yo for y in ycop]
        zcop = [z - zo for z in zcop]
        
        # 기준 좌표 추출
        point_1 = [ycot[1], zcot[1]]
        point_2 = [ycot[0], zcot[0]]
        point_3 = [ycob[1], zcob[1]]
        point_4 = [ycob[0], zcob[0]]
        
        point_1_c_t = [ycot[0], zcot[0]]
        point_2_c_t = [ycot[-2], zcot[-2]]
        point_3_c_t = [ycot[2], zcot[2]]
        point_4_c_t = [ycot[1], zcot[1]]
        
        point_1_c_b = [ycob[0], zcob[0]]
        point_2_c_b = [ycob[-2], zcob[-2]]
        point_3_c_b = [ycob[2], zcob[2]]
        point_4_c_b = [ycob[1], zcob[1]]
        
        point_1_w_p = [ycop[0], zcop[0]]
        point_2_w_p = [ycop[-2], zcop[-2]]
        point_3_w_p = [ycop[2], zcop[2]]
        point_4_w_p = [ycop[1], zcop[1]]
        
        yt = max(ycot, ycob, ycop)
        yb = min(ycot, ycob, ycop)
        zt = max(zcot, zcob, zcop)
        zb = min(zcot, zcob, zcop)
        
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
                    "y": ycot,
                    "z": zcot,
                    "reference": {
                        "name": "c_top",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycob,
                    "z": zcob,
                    "reference": {
                        "name": "c_bottom",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycop,
                    "z": zcop,
                    "reference": {
                        "name": "web_plate",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "c_top": {
                "point_1": point_1_c_t,
                "point_2": point_2_c_t,
                "point_3": point_3_c_t,
                "point_4": point_4_c_t
            },
            "c_bottom": {
                "point_1": point_1_c_b,
                "point_2": point_2_c_b,
                "point_3": point_3_c_b,
                "point_4": point_4_c_b
            },
            "web_plate": {
                "point_1": point_1_w_p,
                "point_2": point_2_w_p,
                "point_3": point_3_w_p,
                "point_4": point_4_w_p
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
            "name": ["c_top", "c_bottom", "web_plate"],
            "control": "c_top"
        }
        
        return vertices, reference_points, properties_control
