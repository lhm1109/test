from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class PipeSection(DBUserValueBaseSection):
    """DBUSER: Pipe Shape Section"""

    def _get_section_shape(self):
        return "Pipe"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)
        
        return {
            "D": dimension.get("d",0)*unit_conversion_factor,
            "tw": dimension.get("tw",0)*unit_conversion_factor
        }
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 2:
            return None
        elif len(vSize) > 2:
            vSize = vSize[:2]
        
        return {
            "D": vSize[0],
            "tw": vSize[1]
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        D = dimensions["D"]
        tw = dimensions["tw"]
        
        # 좌표 생성
        radius_outer = D / 2
        radius_inner = D / 2 - tw
        
        results_outer = ShapeGenerator.generate_circle_shape(radius_outer)
        results_inner = ShapeGenerator.generate_circle_shape(radius_inner)
        reverse_results_inner = TransFormGeometry.reverse_coordinates_list(results_inner)
        
        # 기준 좌표 추출
        point_1 = [0, D/2]
        point_2 = [D/2, 0]
        point_3 = [0, -D/2]
        point_4 = [-D/2, 0]
        
        yt = max(results_outer["y"])
        yb = min(results_outer["y"])
        zt = max(results_outer["z"])
        zb = min(results_outer["z"])
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": results_outer["y"],
                    "z": results_outer["z"],
                    "reference": {
                        "name": "pipe",
                        "elast": 1.0
                    }
                }
            ],
            "inner": [
                {
                    "y": reverse_results_inner["y"],
                    "z": reverse_results_inner["z"],
                    "reference": {
                        "name": "pipe",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "pipe": {
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
            "name": ["pipe"],
            "control": "pipe"
        }
        
        return vertices, reference_points, properties_control
