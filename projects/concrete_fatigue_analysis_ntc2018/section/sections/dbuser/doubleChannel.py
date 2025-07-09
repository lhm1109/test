from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class DoubleChannelSection(DBUserValueBaseSection):
    """DBUSER: Double Channel Section"""
    
    def _get_section_shape(self):
        return "Double_Channel"
    
    def _get_dimensions_from_db_data(self, data_base):
        """수정 필요"""
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
        if len(vSize) < 5:
            return None
        elif len(vSize) > 5:
            vSize = vSize[:5]
        
        return {
            "H": vSize[0],
            "B1": vSize[1],
            "tw": vSize[2],
            "tf1": vSize[3],
            "C": vSize[4]
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B1 = dimensions["B1"]
        tw = dimensions["tw"]
        tf1 = dimensions["tf1"]
        C = dimensions["C"]
        
        # 좌표 생성
        c_shape_coords = ShapeGenerator.generate_c_shape(H, B1, tw, tf1)
        
        right_channel = TransFormGeometry.translate_coordinates(c_shape_coords, C / 2, 0)
        
        left_channel = TransFormGeometry.mirror_coordinates(right_channel, "z")
        reverse_left_channel = TransFormGeometry.reverse_coordinates_list(left_channel)
        
        ycor = right_channel["y"]
        zcor = right_channel["z"]
        ycol = reverse_left_channel["y"]
        zcol = reverse_left_channel["z"]
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(ycor, ycol)
        zo = TransFormGeometry.calculate_origin_coordinates(zcor, zcol)
        
        ycor = [y - yo for y in ycor]
        zcor = [z - zo for z in zcor]
        ycol = [y - yo for y in ycol]
        zcol = [z - zo for z in zcol]
        
        # 기준 좌표 추출
        point_1_right = [ycor[0], zcor[0]]
        point_2_right = [ycor[7], zcor[7]]
        point_3_right = [ycor[2], zcor[2]]
        point_4_right = [ycor[1], zcor[1]]

        point_1_left = [ycol[0], zcol[0]]
        point_2_left = [ycol[1], zcol[1]]
        point_3_left = [ycol[6], zcol[6]]
        point_4_left = [ycol[7], zcol[7]]

        point_1_total = [ycol[1], zcol[1]]
        point_2_total = [ycor[7], zcor[7]]
        point_3_total = [ycor[2], zcor[2]]
        point_4_total = [ycol[6], zcol[6]]
        
        yt = max(ycor, ycol)
        yb = min(ycor, ycol)
        zt = max(zcor, zcol)
        zb = min(zcor, zcol)

        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": ycor,
                    "z": zcor,
                    "reference": {
                        "name": "double_channel_right",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycol,
                    "z": zcol,
                    "reference": {
                        "name": "double_channel_left",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "double_channel_right": {
                "point_1": point_1_right,
                "point_2": point_2_right,
                "point_3": point_3_right,
                "point_4": point_4_right
            },
            "double_channel_left": {
                "point_1": point_1_left,
                "point_2": point_2_left,
                "point_3": point_3_left,
                "point_4": point_4_left
            },
            "total": {
                "point_1": point_1_total,
                "point_2": point_2_total,
                "point_3": point_3_total,
                "point_4": point_4_total,
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
            "name": ["double_channel_right", "double_channel_left"],
            "control": "double_channel_right"
        }
        
        return vertices, reference_points, properties_control
    
