from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.fillet import apply_fillet

import math

class ColdFormedChannelSection(DBUserValueBaseSection):
    """DBUSER: Cold Formed Channel Section"""
    
    def _get_section_shape(self):
        return "Cold_Formed_Channel"
    
    def _get_dimensions_from_db_data(self, data_base):
        units = data_base.get("unit","")
        dimension = data_base.get("dimension",{})
        unit_conversion_factor = get_unit_conversion_factor(units, self.unit_system)
        
        return {
            "H": dimension.get("h",0)*unit_conversion_factor,
            "B": dimension.get("b",0)*unit_conversion_factor,
            "tw": dimension.get("tw",0)*unit_conversion_factor,
            "r": dimension.get("r",0)*unit_conversion_factor,
            "d": dimension.get("d",0)*unit_conversion_factor,
        }
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 5:
            return None
        elif len(vSize) > 5:
            vSize = vSize[:5]
        
        return {
            "H": vSize[0],
            "B": vSize[1],
            "tw": vSize[2],
            "r": vSize[3],
            "d": vSize[4]
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        tw = dimensions["tw"]
        r = dimensions["r"]
        d = dimensions["d"]
        
        combined_type = options["cold_shape"]
        
        # 좌표 생성
        if math.isclose(d, 0.0, abs_tol=1e-9):
            base_coord = {
                "y": [
                    0, 0, B, B, B-tw, B-tw, tw, tw, B-tw, B-tw, B, B, 0
                ],
                "z": [
                    0, -H, -H, -H+tw, -H+tw, -H+tw, -H+tw, -tw, -tw, -tw, -tw, 0, 0
                ]
            }
            
            r_fin = r if not math.isclose(r, 0.0, abs_tol=1e-9) else None
            
            if not r_fin is None:
                base_coord = apply_fillet(base_coord,
                                        [r_fin+tw, r_fin+tw, None, None, None,
                                        None, r_fin, r_fin, None, None, None, None])
            
        else:
            base_coord = {
                "y": [
                    0, 0, B, B, B-tw, B-tw, tw, tw, B-tw, B-tw, B, B, 0
                ],
                "z": [
                    0, -H, -H, -H+d, -H+d, -H+tw, -H+tw, -tw, -tw, -d, -d, 0, 0
                ]
            }
            
            r_fin = r if not math.isclose(r, 0.0, abs_tol=1e-9) else None
            
            if not r_fin is None:
                base_coord = apply_fillet(base_coord,
                                        [r_fin+tw, r_fin+tw, r_fin+tw, None, None,
                                        r_fin, r_fin, r_fin, r_fin, None, None, r_fin+tw])
        
        if combined_type in ["2IS", "2IW"]:
            left_coord = TransFormGeometry.mirror_coordinates(base_coord, "z")
            reverse_left_coord = TransFormGeometry.reverse_coordinates_list(left_coord)
            
            ycol = reverse_left_coord["y"]
            zcol = reverse_left_coord["z"]
            
            ycor = base_coord["y"]
            zcor = base_coord["z"]
            
            # 원점 좌표로 이동 (Center of Section)
            yo = TransFormGeometry.calculate_origin_coordinates(ycol, ycor)
            zo = TransFormGeometry.calculate_origin_coordinates(zcol, zcor)
            
            ycol = [y - yo for y in ycol]
            zcol = [z - zo for z in zcol]
            ycor = [y - yo for y in ycor]
            zcor = [z - zo for z in zcor]
            
            # 기준 좌표 추출
            point_1_right = [B/2, H/2]
            point_2_right = [B, H/2 - d]
            point_3_right = [-B/2, -H/2]
            point_4_right = [0, 0]
            
            point_1_left = [-B/2, H/2]
            point_2_left = [-B, H/2 - d]
            point_3_left = [B/2, -H/2]
            point_4_left = [0, 0]
            
            point_1_total = [0, H/2]
            point_2_total = [B, H/2 - d]
            point_3_total = [-B/2, -H/2]
            point_4_total = [-B, H/2-d]
            
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
                            "name": "cf_channel_right",
                            "elast": 1.0
                        }
                    },
                    {
                        "y": ycol,
                        "z": zcol,
                        "reference": {
                            "name": "cf_channel_left",
                            "elast": 1.0
                        }
                    }
                ]
            }
            
            # 특정 좌표 저장
            reference_points = {
                "cf_channel_right": {
                    "point_1": point_1_right,
                    "point_2": point_2_right,
                    "point_3": point_3_right,
                    "point_4": point_4_right,
                },
                "cf_channel_left": {
                    "point_1": point_1_left,
                    "point_2": point_2_left,
                    "point_3": point_3_left,
                    "point_4": point_4_left,
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
                "name": ["cf_channel_right", "cf_channel_left"],
                "control": "cf_channel_right"
            }
        
        elif combined_type in ["2BS", "2BW"]:
            left_coord = TransFormGeometry.translate_coordinates(base_coord, y_offset=-B)
            right_coord = TransFormGeometry.mirror_coordinates(left_coord, "z")
            reversed_right_coord = TransFormGeometry.reverse_coordinates_list(right_coord)
            
            ycol = left_coord["y"]
            zcol = left_coord["z"]
            
            ycor = reversed_right_coord["y"]
            zcor = reversed_right_coord["z"]
            
            # 원점 좌표로 이동 (Center of Section)
            yo = TransFormGeometry.calculate_origin_coordinates(ycol, ycor)
            zo = TransFormGeometry.calculate_origin_coordinates(zcol, zcor)
            
            ycol = [y - yo for y in ycol]
            zcol = [z - zo for z in zcol]
            ycor = [y - yo for y in ycor]
            zcor = [z - zo for z in zcor]
            
            # 기준 좌표 추출
            point_1_right = [-B/2, H/2]
            point_2_right = [0, H/2 - d]
            point_3_right = [-B/2, -H/2]
            point_4_right = [-B, 0]
            
            point_1_left = [B/2, H/2]
            point_2_left = [0, H/2 - d]
            point_3_left = [B/2, -H/2]
            point_4_left = [B, 0]
            
            point_1_total = [0, H/2]
            point_2_total = [B, H/2 - d]
            point_3_total = [-B/2, -H/2]
            point_4_total = [-B, H/2 - d]
            
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
                            "name": "cf_channel_right",
                            "elast": 1.0
                        }
                    },
                    {
                        "y": ycol,
                        "z": zcol,
                        "reference": {
                            "name": "cf_channel_left",
                            "elast": 1.0
                        }
                    }
                ]
            }

        # 특정 좌표 저장
            reference_points = {
                "cf_channel_right": {
                    "point_1": point_1_right,
                    "point_2": point_2_right,
                    "point_3": point_3_right,
                    "point_4": point_4_right,
                },
                "cf_channel_left": {
                    "point_1": point_1_left,
                    "point_2": point_2_left,
                    "point_3": point_3_left,
                    "point_4": point_4_left,
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
                "name": ["cf_channel_right", "cf_channel_left"],
                "control": "cf_channel_right"
            }
            
        elif combined_type in ["3BS", "3BW"]:
            left_coord = TransFormGeometry.translate_coordinates(base_coord, y_offset=(-B - B/2))
            middle_coord = TransFormGeometry.translate_coordinates(base_coord, y_offset=(-B/2))
            right_coord = TransFormGeometry.mirror_coordinates(base_coord, "z")
            right_coord = TransFormGeometry.translate_coordinates(right_coord, y_offset=(B + B/2))
            reversed_right_coord = TransFormGeometry.reverse_coordinates_list(right_coord)
            
            ycol = left_coord["y"]
            zcol = left_coord["z"]
            ycom = middle_coord["y"]
            zcom = middle_coord["z"]
            ycor = reversed_right_coord["y"]
            zcor = reversed_right_coord["z"]
            
            # 원점 좌표로 이동 (Center of Section)
            yo = TransFormGeometry.calculate_origin_coordinates(ycol, ycom, ycor)
            zo = TransFormGeometry.calculate_origin_coordinates(zcol, zcom, zcor)
            
            ycol = [y - yo for y in ycol]
            zcol = [z - zo for z in zcol]
            ycom = [y - yo for y in ycom]
            zcom = [z - zo for z in zcom]
            ycor = [y - yo for y in ycor]
            zcor = [z - zo for z in zcor]
            
            # 기준 좌표 추출
            point_1_left = [-B, H/2]
            point_2_left = [-B/2, H/2 - d]
            point_3_left = [-B, -H/2]
            point_4_left = [-3*B/2, 0]
            
            point_1_middle = [0, H/2]
            point_2_middle = [B/2, H/2 - d]
            point_3_middle = [0, -H/2]
            point_4_middle = [-B/2, 0]
            
            point_1_right = [B, H/2]
            point_2_right = [B/2, H/2 - d]
            point_3_right = [B, -H/2]
            point_4_right = [3*B/2, 0]
            
            point_1_total = [0, H/2]
            point_2_total = [3*B/2, 0]
            point_3_total = [0, -H/2]
            point_4_total = [-3*B/2, 0]
            
            yt = max(ycor, ycom, ycol)
            yb = min(ycor, ycom, ycol)
            zt = max(zcor, zcom, zcol)
            zb = min(zcor, zcom, zcol)
            
            # 좌표 반환
            vertices = {
                "outer": [
                    {
                        "y": ycol,
                        "z": zcol,
                        "reference": {
                            "name": "cf_channel_left",
                            "elast": 1.0
                        }
                    },
                    {
                        "y": ycom,
                        "z": zcom,
                        "reference": {
                            "name": "cf_channel_middle",
                            "elast": 1.0
                        }
                    },
                    {
                        "y": ycor,
                        "z": zcor,
                        "reference": {
                            "name": "cf_channel_right",
                            "elast": 1.0
                        }
                    }
                ]
            }

        # 특정 좌표 저장
            reference_points = {
                "cf_channel_right": {
                    "point_1": point_1_right,
                    "point_2": point_2_right,
                    "point_3": point_3_right,
                    "point_4": point_4_right,
                },
                "cf_channel_middle": {
                    "point_1": point_1_middle,
                    "point_2": point_2_middle,
                    "point_3": point_3_middle,
                    "point_4": point_4_middle,
                },
                "cf_channel_left": {
                    "point_1": point_1_left,
                    "point_2": point_2_left,
                    "point_3": point_3_left,
                    "point_4": point_4_left,
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
                "name": ["cf_channel_right", "cf_channel_middle", "cf_channel_left"],
                "control": "cf_channel_right"
            }

        elif combined_type in ["4BS", "4BW"]:
            coord1 = TransFormGeometry.translate_coordinates(base_coord, y_offset=(-2*B))
            coord2 = TransFormGeometry.translate_coordinates(base_coord, y_offset=(-B))

            coord3 = TransFormGeometry.mirror_coordinates(base_coord, "z")
            coord3 = TransFormGeometry.translate_coordinates(coord3, y_offset=(2*B))
            reversed_coord3 = TransFormGeometry.reverse_coordinates_list(coord3)
            
            yco1 = coord1["y"]
            zco1 = coord1["z"]
            yco2 = coord2["y"]
            zco2 = coord2["z"]
            yco3 = base_coord["y"]
            zco3 = base_coord["z"]
            yco4 = reversed_coord3["y"]
            zco4 = reversed_coord3["z"]
            
            # 원점 좌표로 이동 (Center of Section)
            yo = TransFormGeometry.calculate_origin_coordinates(yco1, yco2, yco3, yco4)
            zo = TransFormGeometry.calculate_origin_coordinates(zco1, zco2, zco3, zco4)
            
            yco1 = [y - yo for y in yco1]
            zco1 = [z - zo for z in zco1]
            yco2 = [y - yo for y in yco2]
            zco2 = [z - zo for z in zco2]
            yco3 = [y - yo for y in yco3]
            zco3 = [z - zo for z in zco3]
            yco4 = [y - yo for y in yco4]
            zco4 = [z - zo for z in zco4]
            
            # 기준 좌표 추출
            point_1_left_2 = [-3*B/2, H/2]
            point_2_left_2 = [-B, H/2 - d]
            point_3_left_2 = [-3*B/2, -H/2]
            point_4_left_2 = [-2*B, 0]
            
            point_1_left_1 = [-B/2, H/2]
            point_2_left_1 = [0, H/2 - d]
            point_3_left_1 = [-B/2, -H/2]
            point_4_left_1 = [-B, 0]
            
            point_1_right_1 = [B/2, H/2]
            point_2_right_1 = [0, H/2 - d]
            point_3_right_1 = [B/2, -H/2]
            point_4_right_1 = [0, 0]
            
            point_1_right_2 = [3*B/2, H/2]
            point_2_right_2 = [B, H/2 - d]
            point_3_right_2 = [3*B/2, -H/2]
            point_4_right_2 = [2*B, 0]
            
            point_1_total = [0, H/2]
            point_2_total = [2*B, 0]
            point_3_total = [0, -H/2]
            point_4_total = [-2*B, 0]
            
            yt = max(yco1, yco2, yco3, yco4)
            yb = min(yco1, yco2, yco3, yco4)
            zt = max(zco1, zco2, zco3, zco4)
            zb = min(zco1, zco2, zco3, zco4)
            
            # 좌표 반환
            vertices = {
                "outer": [
                    {
                        "y": yco1,
                        "z": zco1,
                        "reference": {
                            "name": "cf_channel_left_2",
                            "elast": 1.0
                        }
                    },
                    {
                        "y": yco2,
                        "z": zco2,
                        "reference": {
                            "name": "cf_channel_left_1",
                            "elast": 1.0
                        }
                    },
                    {
                        "y": yco3,
                        "z": zco3,
                        "reference": {
                            "name": "cf_channel_right_1",
                            "elast": 1.0
                        }
                    },
                    {
                        "y": yco4,
                        "z": zco4,
                        "reference": {
                            "name": "cf_channel_right_2",
                            "elast": 1.0
                        }
                    }
                ]
            }
            
            # 특정 좌표 저장
            reference_points = {
                "cf_channel_left_2": {
                    "point_1": point_1_left_2,
                    "point_2": point_2_left_2,
                    "point_3": point_3_left_2,
                    "point_4": point_4_left_2,
                },
                "cf_channel_left_1": {
                    "point_1": point_1_left_1,
                    "point_2": point_2_left_1,
                    "point_3": point_3_left_1,
                    "point_4": point_4_left_1,
                },
                "cf_channel_right_1": {
                    "point_1": point_1_right_1,
                    "point_2": point_2_right_1,
                    "point_3": point_3_right_1,
                    "point_4": point_4_right_1,
                },
                "cf_channel_right_2": {
                    "point_1": point_1_right_2,
                    "point_2": point_2_right_2,
                    "point_3": point_3_right_2,
                    "point_4": point_4_right_2,
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
                "name": ["cf_channel_right_2", "cf_channel_right_1", "cf_channel_left_1", "cf_channel_left_2"],
                "control": "cf_channel_left_1"
            }
            
        else:
            yco = base_coord["y"]
            zco = base_coord["z"]
            
            # 원점 좌표로 이동 (Center of Section)
            yo = TransFormGeometry.calculate_origin_coordinates(yco)
            zo = TransFormGeometry.calculate_origin_coordinates(zco)
            
            yco = [y - yo for y in yco]
            zco = [z - zo for z in zco]
            
            # 기준 좌표 추출
            point_1 = [0, H/2]
            point_2 = [B/2, H/2 - d]
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
                            "name": "cf_channel",
                            "elast": 1.0
                        }
                    }
                ]
            }
        
            # 특정 좌표 저장
            reference_points = {
                "cf_channel": {
                    "point_1": point_1,
                    "point_2": point_2,
                    "point_3": point_3,
                    "point_4": point_4,
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
                "name": ["cf_channel"],
                "control": "cf_channel"
            }
        
        return vertices, reference_points, properties_control
    