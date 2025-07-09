from projects.concrete_fatigue_analysis_ntc2018.section.base.combined_base import CombinedBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.fillet import apply_fillet

import math

class HC2CombinedSection(CombinedBaseSection):
    """COMBINED: H-C Combined Shape 2 Section"""
    
    def _get_section_shape(self):
        """A"""
        return "H_Section"
    
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
    
    def _get_dimensions_from_vsize(self, vSize_i, vSize_j):
        
        if len(vSize_i) < 4:
            return None
        elif len(vSize_i) > 4:
            vSize_i = vSize_i[:4]

        if len(vSize_j) < 4:
            return None
        elif len(vSize_j) > 4:
            vSize_j = vSize_j[:4]
        
        return {
            "Hh": vSize_i[0],
            "Bh": vSize_i[1],
            "twh": vSize_i[2],
            "tfh": vSize_i[3],
            "Hc": vSize_j[0],
            "Bc": vSize_j[1],
            "twc": vSize_j[2],
            "tfc": vSize_j[3]
        }
    
    def _generate_shape_vertices(self, dimensions):
        
        # 치수 추출
        Hh = dimensions["Hh"]
        Bh = dimensions["Bh"]
        twh = dimensions["twh"]
        tfh = dimensions["tfh"]
        Hc = dimensions["Hc"]
        Bc = dimensions["Bc"]
        twc = dimensions["twc"]
        tfc = dimensions["tfc"]
        
        # 좌표 생성
        h_shape_coords = ShapeGenerator.generate_h_shape(Hh, Bh, twh, tfh, Bh, tfh)
        c_shape_coords = ShapeGenerator.generate_c_shape(Hc, Bc, twc, tfc, Bc, tfc)
        
        rotated_c_shape_coords = TransFormGeometry.rotate_coordinates(c_shape_coords, 90)
        trans_c_shape_coords = TransFormGeometry.translate_coordinates(rotated_c_shape_coords, -Hc/2, 0)
        
        ycoh = h_shape_coords["y"]
        zcoh = h_shape_coords["z"]
        
        ycoc = trans_c_shape_coords["y"]
        zcoc = trans_c_shape_coords["z"]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(ycoh, ycoc)
        zo = TransFormGeometry.calculate_origin_coordinates(zcoh, zcoc)
        
        ycoh = [y - yo for y in ycoh]
        zcoh = [z - zo for z in zcoh]
        
        ycoc = [y - yo for y in ycoc]
        zcoc = [z - zo for z in zcoc]
        
        # 기준 좌표 추출
        point_1 = [ycoc[7], zcoc[7]]
        point_2 = [ycoc[2], zcoc[2]]
        point_3 = [ycoh[6], zcoh[6]]
        point_4 = [ycoh[5], zcoh[5]]
        
        point_1_h = [ycoh[0], zcoh[0]]
        point_2_h = [ycoh[-2], zcoh[-2]]
        point_3_h = [ycoh[6], zcoh[6]]
        point_4_h = [ycoh[5], zcoh[5]]
        
        point_1_c = [ycoc[0], zcoc[0]]
        point_2_c = [ycoc[-2], zcoc[-2]]
        point_3_c = [ycoc[2], zcoc[2]]
        point_4_c = [ycoc[1], zcoc[1]]
        
        yt = max(ycoh, ycoc)
        yb = min(ycoh, ycoc)
        zt = max(zcoh, zcoc)
        zb = min(zcoh, zcoc)
        
        # # 필렛 적용
        # r1_fin = r1 if not math.isclose(r1, 0.0, abs_tol=1e-9) else None
        # r2_fin = r2 if not math.isclose(r2, 0.0, abs_tol=1e-9) else None
        
        # if not (r1_fin is None and r2_fin is None):
        #     transformed_coords = apply_fillet({"y": yco, "z": zco}, [None, None, None, r2_fin, r1_fin, r1_fin, r2_fin, None])
        #     yco = transformed_coords["y"]
        #     zco = transformed_coords["z"]
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": ycoh,
                    "z": zcoh,
                    "reference": {
                        "name": "h_shape",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycoc,
                    "z": zcoc,
                    "reference": {
                        "name": "c_shape",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "h_shape": {
                "point_1": point_1_h,
                "point_2": point_2_h,
                "point_3": point_3_h,
                "point_4": point_4_h
            },
            "c_shape": {
                "point_1": point_1_c,
                "point_2": point_2_c,
                "point_3": point_3_c,
                "point_4": point_4_c
            },
            "total":{
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
            "name": ["h_shape", "c_shape"],
            "control": "h_shape"
        }
        
        return vertices, reference_points, properties_control
