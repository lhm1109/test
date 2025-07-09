from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class SolidRectangleSection(DBUserValueBaseSection):
    """DBUSER: Solid Rectangle Section"""
    
    def _get_section_shape(self):
        return "Solid_Rectangle"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)
        
        return {
            "H": dimension.get("h",0)*unit_conversion_factor,
            "B": dimension.get("b",0)*unit_conversion_factor
        }
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 2:
            return None
        elif len(vSize) > 2:
            vSize = vSize[:2]
        
        return {
            "H": vSize[0],
            "B": vSize[1]
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        
        # 좌표 생성
        solid_rectangle_coords = ShapeGenerator.generate_solid_rectangle_shape(H, B)
        
        yco = solid_rectangle_coords["y"]
        zco = solid_rectangle_coords["z"]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(yco)
        zo = TransFormGeometry.calculate_origin_coordinates(zco)
        
        yco = [y - yo for y in yco]
        zco = [z - zo for z in zco]
        
        # 기준 좌표 추출
        point_1 = [yco[0], zco[0]]
        point_2 = [yco[3], zco[3]]
        point_3 = [yco[2], zco[2]]
        point_4 = [yco[1], zco[1]]
        
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
                        "name": "solid_rectangle",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "solid_rectangle": {
                "point_1": point_1,
                "point_2": point_2,
                "point_3": point_3,
                "point_4": point_4,
            },
            "total":{
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
            "name": ["solid_rectangle"],
            "control": "solid_rectangle"
        }
        
        return vertices, reference_points, properties_control
    