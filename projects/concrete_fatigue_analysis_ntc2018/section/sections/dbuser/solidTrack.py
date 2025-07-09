from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class SolidTrackSection(DBUserValueBaseSection):
    """DBUSER: Solid Track Section"""
    
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
        arc_outer_left = ShapeGenerator.generate_arc_shape(R, 180, 360, (-(B-H)/2, -H/2))
        arc_outer_right = ShapeGenerator.generate_arc_shape(R, 0, 180, ((B-H)/2, -H/2))
        
        merged_outer = TransFormGeometry.merge_coordinates(arc_outer_left, arc_outer_right)
        closed_outer = TransFormGeometry.close_polygon(merged_outer)
        
        yco = closed_outer["y"]
        zco = closed_outer["z"]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(yco)
        zo = TransFormGeometry.calculate_origin_coordinates(zco)
        yco = [y - yo for y in yco]
        zco = [z - zo for z in zco]
        
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
                        "name": "solid_track",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points = {
            "solid_track": {
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
            "name": ["solid_track"],
            "control": "solid_track"
        }
        
        return vertices, reference_points, properties_control
    