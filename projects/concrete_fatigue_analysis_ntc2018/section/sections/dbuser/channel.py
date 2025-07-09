from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.fillet import apply_fillet

import math

class ChannelSection(DBUserValueBaseSection):
    """DBUSER: Channel Section"""

    def _get_section_shape(self):
        return "Channel"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)
        
        return {
            "H": dimension.get("h",0)*unit_conversion_factor,
            "B1": dimension.get("b1",0)*unit_conversion_factor,
            "tw": dimension.get("tw",0)*unit_conversion_factor,
            "tf1": dimension.get("tf1",0)*unit_conversion_factor,
            "B2": dimension.get("b2",0)*unit_conversion_factor,
            "tf2": dimension.get("tf2",0)*unit_conversion_factor,
            "r1": dimension.get("r1",0)*unit_conversion_factor,
            "r2": dimension.get("r2",0)*unit_conversion_factor
        }
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 8:
            return None
        elif len(vSize) > 8:
            vSize = vSize[:8]
        
        return {
            "H": vSize[0],
            "B1": vSize[1],
            "tw": vSize[2],
            "tf1": vSize[3],
            "B2": vSize[4],
            "tf2": vSize[5],
            "r1": vSize[6],
            "r2": vSize[7]
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B1 = dimensions["B1"]
        tw = dimensions["tw"]
        tf1 = dimensions["tf1"]
        B2 = dimensions["B2"]
        tf2 = dimensions["tf2"]
        r1 = dimensions["r1"]
        r2 = dimensions["r2"]
        
        # 좌표 생성
        c_shape_coords = ShapeGenerator.generate_c_shape(H, B1, tw, tf1, B2, tf2)
        
        yco = c_shape_coords["y"]
        zco = c_shape_coords["z"]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(yco)
        zo = TransFormGeometry.calculate_origin_coordinates(zco)
        
        yco = [y - yo for y in yco]
        zco = [z - zo for z in zco]
        
        # 기준 좌표 추출
        point_1 = [yco[0], zco[0]]
        point_2 = [yco[7], zco[7]]
        point_3 = [yco[2], zco[2]]
        point_4 = [yco[1], zco[1]]
        
        yt = max(yco)
        yb = min(yco)
        zt = max(zco)
        zb = min(zco)

        # 필렛 적용
        r1_fin = r1 if not math.isclose(r1, 0.0, abs_tol=1e-9) else None
        r2_fin = r2 if not math.isclose(r2, 0.0, abs_tol=1e-9) else None
        
        if not (r1_fin is None and r2_fin is None):
            transformed_coords = apply_fillet({"y": yco, "z": zco}, [None, None, None, r2_fin, r1_fin, r1_fin, r2_fin, None])
            yco = transformed_coords["y"]
            zco = transformed_coords["z"]
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": yco,
                    "z": zco,
                    "reference": {
                        "name": "channel",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "channel": {
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
            "name": ["channel"],
            "control": "channel"
        }
        
        return vertices, reference_points, properties_control
