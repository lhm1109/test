from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.fillet import apply_fillet

import math

class ZSection(DBUserValueBaseSection):
    """DBUSER: Z Section"""
    
    def _get_section_shape(self):
        return "Z_Section"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)
        
        return {
            "H": dimension.get("h",0)*unit_conversion_factor,
            "B": dimension.get("b",0)*unit_conversion_factor,
            "tw": dimension.get("tw",0)*unit_conversion_factor,
            "r": dimension.get("r",0)*unit_conversion_factor,
            "d": dimension.get("d",0)*unit_conversion_factor,
            "th": dimension.get("th",0)*unit_conversion_factor
        }
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 6:
            return None
        elif len(vSize) > 6:
            vSize = vSize[:6]
        
        return {
            "H": vSize[0],
            "B": vSize[1],
            "tw": vSize[2],
            "r": vSize[3],
            "d": vSize[4],
            "th": vSize[5]
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        tw = dimensions["tw"]
        r = dimensions["r"]
        d = dimensions["d"]
        th = dimensions["th"]
        
        # 좌표 생성
        y_coords = [tw/2]
        z_coords = [-H/2]
        y_coords.append(-B+tw/2)
        z_coords.append(-H/2)
        if math.isclose(d, 0.0, abs_tol=1e-9):
            y_coords.append(y_coords[-1])
            z_coords.append(z_coords[-1] + tw)
        else:
            y_coords.append(y_coords[-1] - math.cos(math.radians(th))*d)
            z_coords.append(z_coords[-1] + math.sin(math.radians(th))*d)
        y_coords.append(y_coords[-1] + math.cos(math.pi/2 - math.radians(th))*tw)
        z_coords.append(z_coords[-1] + math.sin(math.pi/2 - math.radians(th))*tw)
        y_coords.append(-B + tw/2 + math.tan(math.radians(th)/2)*tw)
        z_coords.append(-H/2 + tw)
        y_coords.append(-tw/2)
        z_coords.append(-H/2 + tw)
        
        base_coords = {
            "y": y_coords,
            "z": z_coords
        }
        
        bot_coords = TransFormGeometry.reverse_coordinates_list(base_coords)
        top_coords = TransFormGeometry.mirror_coordinates(bot_coords, "z")
        top_coords = TransFormGeometry.mirror_coordinates(top_coords, "y")
    
        sum_coords = TransFormGeometry.merge_coordinates(bot_coords, top_coords)
        closed_coords = TransFormGeometry.close_polygon(sum_coords)
        
        # 기준 좌표 추출
        if math.isclose(d, 0.0, abs_tol=1e-9):
            point_1 = [B/2-tw/2, H/2]
            point_2 = [B-tw/2, H/2]
            point_3 = [-B/2+tw/2, -H/2]
            point_4 = [-B+tw/2, -H/2]
        else:
            point_1 = [B/2-tw/2, H/2]
            point_2 = [closed_coords["y"][9], closed_coords["z"][9]]
            point_3 = [-B/2+tw/2, -H/2]
            point_4 = [closed_coords["y"][3], closed_coords["z"][3]]
        
        # 필렛 적용
        r_fin = r if not math.isclose(r, 0.0, abs_tol=1e-9) else None
        if math.isclose(d, 0.0, abs_tol=1e-9):
            if not r_fin is None:
                closed_coords = apply_fillet(closed_coords, [
                    r_fin, None, None, None, None, r_fin+tw, r_fin,
                    None, None, None, None, r_fin+tw])
        else:
            if not r_fin is None:
                closed_coords = apply_fillet(closed_coords, [
                    r_fin, r_fin, None, None, r_fin+tw, r_fin+tw, r_fin,
                    r_fin, None, None, r_fin+tw, r_fin+tw])

        yt = max(closed_coords["y"])
        yb = min(closed_coords["y"])
        zt = max(closed_coords["z"])
        zb = min(closed_coords["z"])
                
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": closed_coords["y"],
                    "z": closed_coords["z"],
                    "reference": {
                        "name": "z_shape",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points = {
            "z_shape": {
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
            "name": ["z_shape"],
            "control": "z_shape"
        }
        
        return vertices, reference_points, properties_control
