from projects.concrete_fatigue_analysis_ntc2018.section.base.combined_base import CombinedBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.fillet import apply_fillet

import math

class Angle4Section(CombinedBaseSection):
    """COMBINED: C21 Web Plate Section"""
    
    def _get_section_shape(self):
        """A"""
        return "Angle"
    
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

        if len(vSize_j) < 1:
            return None
        elif len(vSize_j) > 1:
            vSize_j = vSize_j[:1]
        
        return {
            "H": vSize_i[0],
            "B": vSize_i[1],
            "tw": vSize_i[2],
            "tf": vSize_i[3],
            "C": vSize_j[0],
        }
    
    def _generate_shape_vertices(self, dimensions):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        tw = dimensions["tw"]
        tf = dimensions["tf"]
        C = dimensions["C"]
        
        # 좌표 생성
        l_shape_coords = ShapeGenerator.generate_l_shape(H, B, tw, tf)
        
        trans_rb_coords = TransFormGeometry.translate_coordinates(l_shape_coords, C/2, -C/2)
        
        mirrored_lb_coords = TransFormGeometry.mirror_coordinates(trans_rb_coords, "z")
        reverse_lb_coords = TransFormGeometry.reverse_coordinates_list(mirrored_lb_coords)
        
        mirrored_rt_coords = TransFormGeometry.mirror_coordinates(trans_rb_coords, "y")
        reverse_rt_coords = TransFormGeometry.reverse_coordinates_list(mirrored_rt_coords)
        
        mirrored_lt_coords = TransFormGeometry.mirror_coordinates(mirrored_lb_coords, "y")
        
        ycorb = trans_rb_coords["y"]
        zcorb = trans_rb_coords["z"]
        
        ycolb = reverse_lb_coords["y"]
        zcolb = reverse_lb_coords["z"]
        
        ycort = reverse_rt_coords["y"]
        zcort = reverse_rt_coords["z"]
        
        ycolt = mirrored_lt_coords["y"]
        zcolt = mirrored_lt_coords["z"]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(ycorb, ycolb, ycort, ycolt)
        zo = TransFormGeometry.calculate_origin_coordinates(zcorb, zcolb, zcort, zcolt)
        
        ycorb = [y - yo for y in ycorb]
        zcorb = [z - zo for z in zcorb]
        
        ycolb = [y - yo for y in ycolb]
        zcolb = [z - zo for z in zcolb]
        
        ycort = [y - yo for y in ycort]
        zcort = [z - zo for z in zcort]
        
        ycolt = [y - yo for y in ycolt]
        zcolt = [z - zo for z in zcolt]
        
        # 기준 좌표 추출
        point_1 = [ycolt[2], zcolt[2]]
        point_2 = [ycort[4], zcort[4]]
        point_3 = [ycorb[2], zcorb[2]]
        point_4 = [ycolb[4], zcolb[4]]
        
        point_1_h_lt = [ycolt[0], zcolt[0]]
        point_2_h_lt = [ycolt[1], zcolt[1]]
        point_3_h_lt = [ycolt[4], zcolt[4]]
        point_4_h_lt = [ycolt[5], zcolt[5]]
        
        point_1_h_rt = [ycort[0], zcort[0]]
        point_2_h_rt = [ycort[5], zcort[5]]
        point_3_h_rt = [ycort[2], zcort[2]]
        point_4_h_rt = [ycort[1], zcort[1]]
        
        point_1_h_rb = [ycorb[0], zcorb[0]]
        point_2_h_rb = [ycorb[1], zcorb[1]]
        point_3_h_rb = [ycorb[4], zcorb[4]]
        point_4_h_rb = [ycorb[5], zcorb[5]]
        
        point_1_h_lb = [ycolb[0], zcolb[0]]
        point_2_h_lb = [ycolb[5], zcolb[5]]
        point_3_h_lb = [ycolb[2], zcolb[2]]
        point_4_h_lb = [ycolb[1], zcolb[1]]
        
        yt = max(ycorb, ycolb, ycort, ycolt)
        yb = min(ycorb, ycolb, ycort, ycolt)
        zt = max(zcorb, zcolb, zcort, zcolt)
        zb = min(zcorb, zcolb, zcort, zcolt)
        
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
                    "y": ycolt,
                    "z": zcolt,
                    "reference": {
                        "name": "l_left_top",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycort,
                    "z": zcort,
                    "reference": {
                        "name": "l_right_top",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycorb,
                    "z": zcorb,
                    "reference": {
                        "name": "l_right_bottom",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycolb,
                    "z": zcolb,
                    "reference": {
                        "name": "l_left_bottom",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "l_left_top": {
                "point_1": point_1_h_lt,
                "point_2": point_2_h_lt,
                "point_3": point_3_h_lt,
                "point_4": point_4_h_lt
            },
            "l_right_top": {
                "point_1": point_1_h_rt,
                "point_2": point_2_h_rt,
                "point_3": point_3_h_rt,
                "point_4": point_4_h_rt
            },
            "l_right_bottom": {
                "point_1": point_1_h_rb,
                "point_2": point_2_h_rb,
                "point_3": point_3_h_rb,
                "point_4": point_4_h_rb
            },
            "l_left_bottom": {
                "point_1": point_1_h_lb,
                "point_2": point_2_h_lb,
                "point_3": point_3_h_lb,
                "point_4": point_4_h_lb
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
            "name": ["l_left_top", "l_right_top", "l_right_bottom", "l_left_bottom"],
            "control": "l_left_top"
        }
        
        return vertices, reference_points, properties_control
