from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class BoxwithStiffenerSection(DBUserValueBaseSection):
    """DBUSER: Box with Stiffener Section"""
    
    def _get_section_shape(self):
        """Not Available"""
        return None
    
    def _get_dimensions_from_db_data(self, data_base):
        """Not Available"""
        return  None
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 10:
            return None
        elif len(vSize) > 10:
            vSize = vSize[:10]
        
        return {
            "H": vSize[0],
            "B": vSize[1],
            "tf": vSize[2],
            "tw": vSize[3],
            "S1": vSize[4],
            "Hr1": vSize[5],
            "tr1": vSize[6],
            "S2": vSize[7],
            "Hr2": vSize[8],
            "tr2": vSize[9],
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        tf = dimensions["tf"]
        tw = dimensions["tw"]
        S1 = dimensions["S1"]
        Hr1 = dimensions["Hr1"]
        tr1 = dimensions["tr1"]
        S2 = dimensions["S2"]
        Hr2 = dimensions["Hr2"]
        tr2 = dimensions["tr2"]
        
        N1 = options["cell_shape"]
        N2 = options["cell_type"]
        
        flange_stiff_width= S1*(N1 - 1) + tr1
        web_stiff_width = S2*(N2 - 1) + tr2
        
        if flange_stiff_width >= (B - tw*2):
            return {"error": "flange_stiff_width is too large"}
        
        if web_stiff_width >= (H - tf*2):
            return {"error": "web_stiff_width is too large"}
        
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
        
        # 기준 좌표 추출
        point_1 = [-B/2, H/2]
        point_2 = [B/2, H/2]
        point_3 = [B/2, -H/2]
        point_4 = [-B/2, -H/2]
        
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
                        "name": "box_with_stiffener",
                        "elast": 1.0
                    }
                }
            ],
            "inner": [
                {
                    "y": yci,
                    "z": zci,
                    "reference": {
                        "name": "box_with_stiffener",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points = {
            "box_with_stiffener": {
                "point_1": point_1,
                "point_2": point_2,
                "point_3": point_3,
                "point_4": point_4
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
            "name": ["box_with_stiffener"],
            "control": "box_with_stiffener"
        }
        
        return vertices, reference_points, properties_control
    
