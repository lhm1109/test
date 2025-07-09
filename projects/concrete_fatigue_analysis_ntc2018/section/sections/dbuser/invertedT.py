from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class InvertedTSection(DBUserValueBaseSection):
    """DBUSER: Inverted T Section"""
    
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
            "B1": vSize[1],
            "B2": vSize[2],
            "tw": vSize[3],
            "tf": vSize[4]
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B1 = dimensions["B1"]
        B2 = dimensions["B2"]
        tw = dimensions["tw"]
        tf = dimensions["tf"]
        
        # 좌표 생성
        outer_coords = {
            "y": [0, 0, -B1, -B1, B2+tw, B2+tw, tw, tw, 0],
            "z": [0, -H + tf, -H + tf, -H, -H, -H + tf, -H + tf, 0, 0]
        }
        
        yco = outer_coords["y"]
        zco = outer_coords["z"]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(yco)
        zo = TransFormGeometry.calculate_origin_coordinates(zco)
        
        yco = [y - yo for y in yco]
        zco = [z - zo for z in zco]

        # 기준 좌표 추출
        point_1 = [yco[0], zco[0]]
        point_2 = [yco[7], zco[7]]
        point_3 = [yco[4], zco[4]]
        point_4 = [yco[3], zco[3]]
        
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
                        "name": "inverted_t",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "inverted_t": {
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
            "name": ["inverted_t"],
            "control": "inverted_t"
        }
        
        return vertices, reference_points, properties_control
    