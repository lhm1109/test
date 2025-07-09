from projects.concrete_fatigue_analysis_ntc2018.section.base.combined_base import CombinedBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.fillet import apply_fillet

import math

class HPlateSection(CombinedBaseSection):
    """COMBINED: H-Shape with Plate Section"""
    
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
            "tw1": vSize_i[2],
            "tf": vSize_i[3],
            "C": vSize_j[0],
            "tw2": vSize_j[1],
        }
    
    def _generate_shape_vertices(self, dimensions):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        tw1 = dimensions["tw1"]
        tf = dimensions["tf"]
        C = dimensions["C"]
        tw2 = dimensions["tw2"]
        
        # 좌표 생성
        h_shape_coords = ShapeGenerator.generate_h_shape(H, B, tw1, tf, B, tf)
        
        trans_h_shape_coords = TransFormGeometry.translate_coordinates(h_shape_coords, 0, H/2)
        
        ycoh = trans_h_shape_coords["y"]
        zcoh = trans_h_shape_coords["z"]
        
        ycol = [-(C+tw2)/2, -(C+tw2)/2, -(C-tw2)/2, -(C-tw2)/2, -(C+tw2)/2]
        zcol = [H/2-tf, -H/2+tf, -H/2+tf, H/2-tf, H/2-tf]
        
        ycor = [(C-tw2)/2, (C-tw2)/2, (C+tw2)/2, (C+tw2)/2, (C-tw2)/2]
        zcor = [H/2-tf, -H/2+tf, -H/2+tf, H/2-tf, H/2-tf]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(ycoh, ycol, ycor)
        zo = TransFormGeometry.calculate_origin_coordinates(zcoh, zcol, zcor)
        
        ycoh = [y - yo for y in ycoh]
        zcoh = [z - zo for z in zcoh]
        
        ycol = [y - yo for y in ycol]
        zcol = [z - zo for z in zcol]
        
        ycor = [y - yo for y in ycor]
        zcor = [z - zo for z in zcor]
        
        # 기준 좌표 추출
        point_1 = [ycoh[0], zcoh[0]]
        point_2 = [ycoh[-2], zcoh[-2]]
        point_3 = [ycoh[6], zcoh[6]]
        point_4 = [ycoh[5], zcoh[5]]
        
        point_1_w_pl = [ycol[0], zcol[0]]
        point_2_w_pl = [ycol[-2], zcol[-2]]
        point_3_w_pl = [ycol[2], zcol[2]]
        point_4_w_pl = [ycol[1], zcol[1]]
        
        point_1_w_pr = [ycor[0], zcor[0]]
        point_2_w_pr = [ycor[-2], zcor[-2]]
        point_3_w_pr = [ycor[2], zcor[2]]
        point_4_w_pr = [ycor[1], zcor[1]]
        
        yt = max(ycoh, ycol, ycor)
        yb = min(ycoh, ycol, ycor)
        zt = max(zcoh, zcol, zcor)
        zb = min(zcoh, zcol, zcor)
        
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
                    "y": ycoh,
                    "z": zcoh,
                    "reference": {
                        "name": "h_shape",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycol,
                    "z": zcol,
                    "reference": {
                        "name": "web_plate_left",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycor,
                    "z": zcor,
                    "reference": {
                        "name": "web_plate_right",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "h_shape": {
                "point_1": point_1,
                "point_2": point_2,
                "point_3": point_3,
                "point_4": point_4
            },
            "web_plate_left": {
                "point_1": point_1_w_pl,
                "point_2": point_2_w_pl,
                "point_3": point_3_w_pl,
                "point_4": point_4_w_pl
            },
            "web_plate_right": {
                "point_1": point_1_w_pr,
                "point_2": point_2_w_pr,
                "point_3": point_3_w_pr,
                "point_4": point_4_w_pr
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
            "name": ["h_shape", "web_plate_left", "web_plate_right"],
            "control": "h_shape"
        }
        
        return vertices, reference_points, properties_control
