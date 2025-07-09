from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.chamfer import apply_chamfer

class SolidOctagonSection(DBUserValueBaseSection):
    """DBUSER: Solid Octagon Section"""
    
    def _get_section_shape(self):
        """Not Available"""
        return None
    
    def _get_dimensions_from_db_data(self, data_base):
        """Not Available"""
        return  None
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 4:
            return None
        elif len(vSize) > 4:
            vSize = vSize[:4]
        
        return {
            "H": vSize[0],
            "B": vSize[1],
            "a": vSize[2],
            "b": vSize[3],
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        a = dimensions["a"]
        b = dimensions["b"]
        
        # 좌표 생성
        solid_rectangle_coords = ShapeGenerator.generate_solid_rectangle_shape(H, B)
        outer_octagon = apply_chamfer(solid_rectangle_coords, [[a, b], [b, a], [a, b], [b, a]])
        
        yco = outer_octagon["y"]
        zco = outer_octagon["z"]
        
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
                        "name": "solid_octagon",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "solid_octagon": {
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
            "name": ["solid_octagon"],
            "control": "solid_octagon"
        }
        
        return vertices, reference_points, properties_control
    