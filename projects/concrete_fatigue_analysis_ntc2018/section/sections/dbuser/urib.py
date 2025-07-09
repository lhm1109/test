from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.fillet import apply_fillet

import math

class URibSection(DBUserValueBaseSection):
    """DBUSER: Urib Section"""
    
    def _get_section_shape(self):
        return "U_Rib"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)
        
        return {
            "H": dimension.get("h",0)*unit_conversion_factor,
            "B1": dimension.get("b1",0)*unit_conversion_factor,
            "B2": dimension.get("b2",0)*unit_conversion_factor,
            "t": dimension.get("t",0)*unit_conversion_factor,
            "R": dimension.get("r",0)*unit_conversion_factor,
        }
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 5:
            return None
        elif len(vSize) > 5:
            vSize = vSize[:5]
        
        return {
            "H": vSize[0],
            "B1": vSize[1],
            "B2": vSize[2],
            "t": vSize[3],
            "R": vSize[4],
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B1 = dimensions["B1"]
        B2 = dimensions["B2"]
        t = dimensions["t"]
        R = dimensions["R"]
        
        if math.isclose(B1, B2, abs_tol=1e-9):
            yco = [-B2/2 + t, -B2/2 + t, -B1/2, -B1/2, B1/2, B1/2, B2/2 - t, B2/2 - t, -B2/2 + t]
            zco = [t, H, H, 0, 0, H, H, t, t]
        else:
            yz1 = (B2/2, 0)
            yz2 = (B1/2, H)
            
            th = abs(math.atan(H/((B1-B2)/2)))
            
            m = (yz2[1] - yz1[1]) / (yz2[0] - yz1[0])
            b = yz1[1] - m * yz1[0]
            d = t/math.sin(th)*-1
            
            z1 = H
            z2 = t
            
            y1 = (z1 - (b - m*d)) / m
            y2 = (z2 - (b - m*d)) / m
            
            y0 = (y1 + m*(z1 - b)) / (m**2 + 1)
            z0 = (m * y0 + b)
            
            yco = [-y2, -y1, -y0, -B2/2, B2/2, y0, y1, y2, -y2]
            zco = [z2, z1, z0, 0, 0, z0, z1, z2, z2]
            
            point_1 = [yco[2], zco[1]]
            point_2 = [yco[-4], zco[-3]]
            point_3 = [B2/2, 0]
            point_4 = [-B2/2, 0]
        
        R_fin = R if not math.isclose(R, 0.0, abs_tol=1e-9) else None
        if R_fin is not None:
            close_coord = apply_fillet({"y": yco, "z": zco}, [R_fin, None, None, R_fin+t,  R_fin+t, None, None, R_fin])
            yco = close_coord["y"]
            zco = close_coord["z"]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(yco)
        zo = TransFormGeometry.calculate_origin_coordinates(zco)
        
        yco = [y - yo for y in yco]
        zco = [z - zo for z in zco]
        
        if math.isclose(B1, B2, abs_tol=1e-9):
            point_1 = [-B1/2 - yo, H - zo]
            point_2 = [B1/2 - yo, H - zo]
            point_3 = [B2/2 - yo, 0 - zo]
            point_4 = [-B2/2 - yo, 0 - zo]
        else:
            point_1 = [point_1[0] - yo, point_1[1] - zo]
            point_2 = [point_2[0] - yo, point_2[1] - zo]
            point_3 = [point_3[0] - yo, point_3[1] - zo]
            point_4 = [point_4[0] - yo, point_4[1] - zo]

        
        # 기준 좌표 추출
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
                        "name": "urib",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points = {
            "urib": {
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
            "name": ["urib"],
            "control": "urib"
        }
        
        return vertices, reference_points, properties_control
    