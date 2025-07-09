from projects.concrete_fatigue_analysis_ntc2018.section.base.src_base import SRCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class SRCBoxStiffenerSection(SRCBaseSection):
    """SRC: Box with Stiffener Section"""
    
    def _get_section_shape(self):
        """Not Available"""
        return None
    
    def _get_dimensions_from_db_data(self, data_base):
        """Not Available"""
        return None
    
    def _get_dimensions_from_vsize(self, vSize):
        
        steel_size = vSize.get("steel_size", [])
        concrete_size = vSize.get("concrete_size", [])
        
        if len(steel_size) < 10:
            return None
        elif len(steel_size) > 10:
            steel_size = steel_size[:10]
        
        return {
            "steel_size": steel_size,
            "concrete_size": concrete_size
        }
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # 치수 추출
        H, B, tf, tw, S1, Hr1, tr1, S2, Hr2, tr2 = dimensions["steel_size"]
        
        N1 = options["cell_shape"]
        N2 = options["cell_type"]
        
        flange_stiff_width= S1*(N1 - 1) + tr1
        web_stiff_width = S2*(N2 - 1) + tr2
        
        if flange_stiff_width >= (B - tw*2):
            return {
                "error": "flange_stiff_width is too large",
                "error_code": "SRCBOXSTIFFENERSECTION_GENERATE_SHAPE_VERTICES"
            }, {}, {}
        
        if web_stiff_width >= (H - tf*2):
            return {
                "error": "web_stiff_width is too large",
                "error_code": "SRCBOXSTIFFENERSECTION_GENERATE_SHAPE_VERTICES"
            }, {}, {}
        
        # 좌표 생성
        outer_coords = ShapeGenerator.generate_solid_rectangle_shape(H, B)
        
        y_top_flange = []
        z_top_flange = []
        for i in range(N1):
            y_top_flange.append(i*S1)
            z_top_flange.append(0)
            y_top_flange.append(i*S1)
            z_top_flange.append(-Hr1)
            y_top_flange.append(tr1 + i*S1)
            z_top_flange.append(-Hr1)
            y_top_flange.append(tr1 + i*S1)
            z_top_flange.append(0)
        
        y_right_web = []
        z_right_web = []
        for i in range(N2):
            y_right_web.append(0)
            z_right_web.append(-i*S2)
            y_right_web.append(-Hr2)
            z_right_web.append(-i*S2)
            y_right_web.append(-Hr2)
            z_right_web.append(-tr2 -i*S2)
            y_right_web.append(0)
            z_right_web.append(-tr2 -i*S2)

        top_flange = TransFormGeometry.translate_coordinates(
            {"y": y_top_flange, "z": z_top_flange}, -flange_stiff_width/2, -tf)
        
        bottom_flange = TransFormGeometry.mirror_coordinates(top_flange, "y")
        bottom_flange = TransFormGeometry.translate_coordinates(
            bottom_flange, 0, -H)
        bottom_flange = TransFormGeometry.reverse_coordinates_list(bottom_flange)
        
        right_web = TransFormGeometry.translate_coordinates(
            {"y": y_right_web, "z": z_right_web}, B/2 - tw, web_stiff_width/2-H/2)
        
        left_web =  TransFormGeometry.mirror_coordinates(right_web, "z")
        left_web = TransFormGeometry.reverse_coordinates_list(left_web)
        
        merged_inner_coords = TransFormGeometry.merge_coordinates({"y":[-B/2 + tw], "z":[-tf]}, top_flange)
        merged_inner_coords = TransFormGeometry.merge_coordinates(merged_inner_coords, {"y":[B/2 - tw], "z":[-tf]})
        merged_inner_coords = TransFormGeometry.merge_coordinates(merged_inner_coords, right_web)
        merged_inner_coords = TransFormGeometry.merge_coordinates(merged_inner_coords, {"y":[B/2 - tw], "z":[-H + tf]})
        merged_inner_coords = TransFormGeometry.merge_coordinates(merged_inner_coords, bottom_flange)
        merged_inner_coords = TransFormGeometry.merge_coordinates(merged_inner_coords, {"y":[-B/2 + tw], "z":[-H + tf]})
        merged_inner_coords = TransFormGeometry.merge_coordinates(merged_inner_coords, left_web)

        close_inner_coords = TransFormGeometry.close_polygon(merged_inner_coords)
        
        yco = outer_coords["y"]
        zco = outer_coords["z"]
        yci = close_inner_coords["y"]
        zci = close_inner_coords["z"]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(yco)
        zo = TransFormGeometry.calculate_origin_coordinates(zco)
        
        yco = [y - yo for y in yco]
        zco = [z - zo for z in zco]
        yci = [y - yo for y in yci]
        zci = [z - zo for z in zci]
        
        # 콘크리트 좌표 추출
        yci_c = yci.copy()
        zci_c = zci.copy()
        
        yci_c.reverse()
        zci_c.reverse()
        
        # 기준 좌표 추출
        point_1_s = [-B/2, H/2]
        point_2_s = [B/2, H/2]
        point_3_s = [B/2, -H/2]
        point_4_s = [-B/2, -H/2]
        
        point_1_c = [-(B-tw*2)/2, H/2-tf]
        point_2_c = [(B-tw*2)/2, H/2-tf]
        point_3_c = [(B-tw*2)/2, -H/2+tf]
        point_4_c = [-(B-tw*2)/2, -H/2+tf]
        
        yt = max(yco, yci_c)
        yb = min(yco, yci_c)
        zt = max(zco, zci_c)
        zb = min(zco, zci_c)
        
        # 재료 값
        stif_factor = options["matl_stif_factor"]
        steel_elast = 1.0
        concrete_elast = 1.0 / options["matl_elast"] * stif_factor
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": yco,
                    "z": zco,
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
                    "y": yci,
                    "z": zci,
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
    
