from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

import math

class UprightSection(DBUserValueBaseSection):
    """DBUSER: Upright Section"""
    
    def _get_section_shape(self):
        return "Upright"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)
        
        return {
            "H": dimension.get("h",0)*unit_conversion_factor,
            "B": dimension.get("b",0)*unit_conversion_factor,
            "tw": dimension.get("tw",0)*unit_conversion_factor,
            "Hw1": dimension.get("hw1",0)*unit_conversion_factor,
            "Hw2": dimension.get("hw2",0)*unit_conversion_factor,
            "B1": dimension.get("b1",0)*unit_conversion_factor,
            "B2": dimension.get("b2",0)*unit_conversion_factor,
            "B3": dimension.get("b3",0)*unit_conversion_factor,
            "Bf3": dimension.get("bf3",0)*unit_conversion_factor,
            "d": dimension.get("d",0)*unit_conversion_factor,
        }
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 10:
            return None
        elif len(vSize) > 10:
            vSize = vSize[:10]
        
        return {
            "H": vSize[0],
            "B": vSize[1],
            "tw": vSize[2],
            "Hw1": vSize[3],
            "Hw2": vSize[4],
            "B1": vSize[5],
            "B2": vSize[6],
            "B3": vSize[7],
            "Bf3": vSize[8],
            "d": vSize[9],
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        tw = dimensions["tw"]
        Hw1 = dimensions["Hw1"]
        Hw2 = dimensions["Hw2"]
        B1 = dimensions["B1"]
        B2 = dimensions["B2"]
        B3 = dimensions["B3"]
        Bf3 = dimensions["Bf3"]
        d = dimensions["d"]
        
        # 좌표 생성
        # Outer
        ycol = [-B2/2]
        zcol = [-d]
        ycol.append(-B/2 + B1)
        zcol.append(0)
        ycol.append(-B/2)
        zcol.append(zcol[-1])
        ycol.append(ycol[-1])
        zcol.append(-Hw1)
        ycol.append(-B3/2-tw)
        zcol.append(-H + tw + Hw2)
        ycol.append(ycol[-1])
        zcol.append(zcol[-1] - Hw2)
        
        if math.isclose(Bf3, 0.0, abs_tol=1e-9):
            ycol.append(ycol[-1])
            zcol.append(zcol[-1] - tw)
            ycol.append(ycol[-1] + tw)
            zcol.append(zcol[-1])
        else:
            ycol.append(-B3/2 - Bf3)
            zcol.append(zcol[-1])
            ycol.append(ycol[-1])
            zcol.append(zcol[-1] - tw)
            ycol.append(ycol[-1] + Bf3)
            zcol.append(zcol[-1])
        
        angle_rad, _ = TransFormGeometry.angle_between_three_points(
            (ycol[3], zcol[3]), (ycol[4], zcol[4]), (ycol[5], zcol[5])
        )
        part_length = math.tan(math.pi/2 - angle_rad/2) * tw
        
        ycol.append(ycol[-1])        
        zcol.append(zcol[4] + part_length)
        
        angle_rad, _ = TransFormGeometry.angle_between_three_points(
            (ycol[2], zcol[2]), (ycol[3], zcol[3]), (ycol[4], zcol[4])
        )
        part_length = math.tan(math.pi/2 - angle_rad/2) * tw
        
        ycol.append(ycol[3] + tw)
        zcol.append(zcol[3] + part_length)
        
        ycol.append(ycol[2] + tw)
        zcol.append(-tw)
        
        angle_rad, _ = TransFormGeometry.angle_between_three_points(
            (ycol[0], zcol[0]), (ycol[1], zcol[1]), (ycol[2], zcol[2])
        )
        part_length = math.tan(math.pi/2 - angle_rad/2) * tw
        
        ycol.append(ycol[1] - part_length)
        zcol.append(-tw)
        
        angle_rad, _ = TransFormGeometry.angle_between_three_points(
            (0, -d), (ycol[0], zcol[0]), (ycol[1], zcol[1])
        )
        part_length = math.tan(math.pi/2 - angle_rad/2) * tw
        
        ycol.append(ycol[0] - part_length)
        zcol.append(zcol[0] - tw)
        
        left = {"y": ycol, "z": zcol}
        
        right = TransFormGeometry.mirror_coordinates(left, "z")
        reverse_right = TransFormGeometry.reverse_coordinates_list(right)
        
        merged = TransFormGeometry.merge_coordinates(left, reverse_right)
        close = TransFormGeometry.close_polygon(merged)
        
        yco = close["y"]
        zco = close["z"]
        
        # 원점 좌표로 이동
        yo = TransFormGeometry.calculate_origin_coordinates(yco)
        zo = TransFormGeometry.calculate_origin_coordinates(zco)
        
        yco = [y - yo for y in yco]
        zco = [z - zo for z in zco]
        
        # 기준 좌표 추출
        point_1 = [yco[2], zco[2]]
        
        if math.isclose(Bf3, 0.0, abs_tol=1e-9):
            point_2 = [yco[23], zco[23]]
            point_3 = [yco[19], zco[19]]
            point_4 = [yco[6], zco[6]]
        else:
            point_2 = [yco[25], zco[25]]
            point_3 = [yco[20], zco[20]]
            point_4 = [yco[7], zco[7]]
        
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
                        "name": "upright",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points = {
            "upright": {
                "point_1": point_1,
                "point_2": point_2,
                "point_3": point_3,
                "point_4": point_4
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
            "name": ["upright"],
            "control": "upright"
        }
        
        return vertices, reference_points, properties_control
    