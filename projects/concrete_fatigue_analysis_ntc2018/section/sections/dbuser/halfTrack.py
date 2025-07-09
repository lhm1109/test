from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection

import math

class HalfTrackSection(DBUserValueBaseSection):
    """DBUSER: Half Track Section"""
    
    def _get_section_shape(self):
        """Not Available"""
        return None
    
    def _get_dimensions_from_db_data(self, data_base):
        """Not Available"""
        return  None
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 2:
            return None
        elif len(vSize) > 2:
            vSize = vSize[:2]
        
        return {
            "H": vSize[0],
            "B": vSize[1],
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        R = H / 2
        
        # 좌표 생성
        y = [-B/2, -B/2]
        z = [H/2, -H/2]
        
        yc = B/2 - R
        zc = 0
        yr = []
        zr = []
        for i in range(180, -1, -3):
            yr.append(yc + R * math.sin(math.radians(i)))
            zr.append(zc + R * math.cos(math.radians(i)))
        
        yco = y + yr
        zco = z + zr
        
        yco.append(-B/2)
        zco.append(H/2)
        
        # 기준 좌표 추출
        point_1 = [0, H/2]
        point_2 = [B/2, 0]
        point_3 = [0, -H/2]
        point_4 = [-B/2, 0]
        
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
                        "name": "half_track",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points = {
            "half_track": {
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
            "name": ["half_track"],
            "control": "half_track"
        }
        
        return vertices, reference_points, properties_control
    
