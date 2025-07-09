from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection

import math

class OctagonSection(DBUserValueBaseSection):
    """DBUSER: Octagon Section"""
    
    def _get_section_shape(self):
        """Not Available"""
        return None
    
    def _get_dimensions_from_db_data(self, data_base):
        """Not Available"""
        return  None
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 5:
            return None
        elif len(vSize) > 5:
            vSize = vSize[:5]
        
        return {
            "H": vSize[0],
            "B": vSize[1],
            "a": vSize[2],
            "b": vSize[3],
            "t": vSize[4],
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        a = dimensions["a"]
        b = dimensions["b"]
        t = dimensions["t"]
        
        if math.isclose(a, 0.0, abs_tol=1e-9) or math.isclose(b, 0.0, abs_tol=1e-9):
            return {
                "error": "a or b is 0",
                "error_code": "OCTAGONSECTION_GENERATE_SHAPE_VERTICES"
            }, {}, {}
        
        # 좌표 생성
        outer_coords = {
            "y": [-B/2 + a, -B/2, -B/2, -B/2 + a, B/2 - a, B/2, B/2, B/2 - a, -B/2 +a],
            "z": [H/2, H/2 - b, -H/2 + b, -H/2, -H/2, -H/2 + b, H/2 - b, H/2, H/2]
        }
        
        # inner
        yz1 = (B/2 - a, H/2)
        yz2 = (B/2, H/2 - b)
        
        th = math.atan(abs(b) / abs(a))
        
        m = (yz2[1] - yz1[1]) / (yz2[0] - yz1[0])
        b = yz1[1] - m * yz1[0]
        d = -t / math.sin(th)
        
        z1 = H/2 - t
        y2 = B/2 - t
        y1 = (z1 - (b - m*d)) / m
        z2 = m*y2 + (b - m*d)
        
        inner_coords = {
            "y": [y1, y2, y2, y1, -y1, -y2, -y2, -y1, y1],
            "z": [z1, z2, -z2, -z1, -z1, -z2, z2, z1, z1]
        }

        # 기준 좌표 추출
        point_1 = [0, H/2]
        point_2 = [B/2, 0]
        point_3 = [0, -H/2]
        point_4 = [-B/2, 0]
        
        yt = max(outer_coords["y"])
        yb = min(outer_coords["y"])
        zt = max(outer_coords["z"])
        zb = min(outer_coords["z"])
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": outer_coords["y"],
                    "z": outer_coords["z"],
                    "reference": {
                        "name": "octagon",
                        "elast": 1.0
                    }
                }
            ],
            "inner": [
                {
                    "y": inner_coords["y"],
                    "z": inner_coords["z"],
                    "reference": {
                        "name": "octagon",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "octagon": {
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
            "name": ["octagon"],
            "control": "octagon"
        }
        
        return vertices, reference_points, properties_control
    