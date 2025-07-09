from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor

class SolidRoundSection(DBUserValueBaseSection):
    """DBUSER: Solid Round Section"""
    
    def _get_section_shape(self):
        return "Solid_Round"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)
        
        return {
            "D": dimension.get("d",0)*unit_conversion_factor,
        }
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 1:
            return None
        elif len(vSize) > 1:
            vSize = vSize[:1]
        
        return {
            "D": vSize[0],
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        D = dimensions["D"]
        
        # 좌표 생성
        circle_coords = ShapeGenerator.generate_circle_shape(D/2)
        
        # 기준 좌표 추출
        point_1 = [0, D/2]
        point_2 = [D/2, 0]
        point_3 = [0, -D/2]
        point_4 = [-D/2, 0]
        
        yt = max(circle_coords["y"])
        yb = min(circle_coords["y"])
        zt = max(circle_coords["z"])
        zb = min(circle_coords["z"])
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": circle_coords["y"],
                    "z": circle_coords["z"],
                    "reference": {
                        "name": "solid_round",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "solid_round": {
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
            "name": ["solid_round"],
            "control": "solid_round"
        }
        
        return vertices, reference_points, properties_control
    