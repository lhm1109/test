from projects.concrete_fatigue_analysis_ntc2018.section.base.composite_base import CompositeBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

import math

class SteelBoxType2Section(CompositeBaseSection):
    """Compostie: Steel Box Type 2 Section"""
    
    def _generate_shape_vertices(self, dimensions, dimensions_sub, options):
        
        # Variable Initialization
        B1, B2, B3, B4, B5, B6, H, t1, t2, tw1, tw2 = dimensions["vSize"]
        Bc, tc, Hh = dimensions_sub["slab"]
        Sg, Top, Bot = dimensions_sub["reference_size"]
        twx1 = tw1 * math.sqrt(H ** 2 + ((Bot + B4) - (Top + B1)) ** 2) / H
        twx2 = tw2 * math.sqrt(H ** 2 + ((Top + B1 + B2) - (Bot + B4 + B5)) ** 2) / H
        
        # Outer Cell - Left Side
        ycol = [(B2 / 2 + B1 + Top) - (Sg + Bc / 2)]
        zcol = [-(tc + Hh)]
        ycol.append(ycol[0] - B2 / 2 - B1)
        zcol.append(zcol[0])
        ycol.append(ycol[1])
        zcol.append(zcol[1] - t1)
        ycol.append(ycol[2] + B1 - twx1)
        zcol.append(zcol[2])
        ycol.append((B5 / 2 + B4 + Bot) - (Sg + Bc / 2) - B5 / 2 - twx1)
        zcol.append(zcol[3] - H)
        ycol.append(ycol[4] - B4 + twx1)
        zcol.append(zcol[4])
        ycol.append(ycol[5])
        zcol.append(zcol[5] - t2)
        ycol.append((B5 / 2 + B4 + Bot) - (Sg + Bc / 2))
        zcol.append(zcol[6])
        
        # Outer Cell - Right Side
        ycor = [(B2 / 2 + B1 + Top) - (Sg + Bc / 2)]
        zcor = [-(tc + Hh)]
        ycor.append(ycor[0] + B2 / 2 + B3)
        zcor.append(zcor[0])
        ycor.append(ycor[1])
        zcor.append(zcor[1] - t1)
        ycor.append(ycor[2] - B3 + twx2)
        zcor.append(zcor[2])
        ycor.append((B5 / 2 + B4 + Bot) - (Sg + Bc / 2) + B5 / 2 + twx2)
        zcor.append(zcor[3] - H)
        ycor.append(ycor[4] + B6 - twx2)
        zcor.append(zcor[4])
        ycor.append(ycor[5])
        zcor.append(zcor[5] - t2) 
        ycor.append((B5 / 2 + B4 + Bot) - (Sg + Bc / 2))
        zcor.append(zcor[6])
        
        # Inner Cell - Left Side
        ycil = [(B2 / 2 + B1 + Top) - (Sg + Bc / 2)]
        zcil = [zcol[0] - t1]
        ycil.append(ycil[0] - B2 / 2)
        zcil.append(zcil[0])
        ycil.append((B5 / 2 + B4 + Bot) - (Sg + Bc / 2) - B5 / 2)
        zcil.append(zcil[1] - H)
        ycil.append((B5 / 2 + B4 + Bot) - (Sg + Bc / 2))
        zcil.append(zcil[2])
        
        # Inner Cell - Right Side
        ycir = [(B2 / 2 + B1 + Top) - (Sg + Bc / 2)]
        zcir = [zcor[0] - t1]
        ycir.append(ycir[0] + B2 / 2)
        zcir.append(zcir[0])
        ycir.append((B5 / 2 + B4 + Bot) - (Sg + Bc / 2) + B5 / 2)
        zcir.append(zcir[1] - H)
        ycir.append((B5 / 2 + B4 + Bot) - (Sg + Bc / 2))
        zcir.append(zcir[2])
        
        # Reverse
        ycor.reverse()
        zcor.reverse()
        ycil.reverse()
        zcil.reverse()
        
        # Remove Origin
        ycor.pop(0)
        zcor.pop(0)
        ycil.pop(0)
        zcil.pop(0)
        
        # All Cell
        ycoAll = ycol + ycor
        zcoAll = zcol + zcor
        yciAll = ycir + ycil
        zciAll = zcir + zcil
        
        # Slab
        slab_result = ShapeGenerator.generate_solid_rectangle_shape(tc, Bc)
        slab_y = slab_result["y"]
        slab_z = slab_result["z"]
        
        # 원점 좌표로 이동
        yo = TransFormGeometry.calculate_origin_coordinates(ycoAll, slab_y)
        zo = TransFormGeometry.calculate_origin_coordinates(zcoAll, slab_z)
        
        ycoAll = [y - yo for y in ycoAll]
        zcoAll = [z - zo for z in zcoAll]
        yciAll = [y - yo for y in yciAll]
        zciAll = [z - zo for z in zciAll]
        slab_y = [y - yo for y in slab_y]
        slab_z = [z - zo for z in slab_z]
        
        # 기준 좌표 추출
        g_point_1 = [ycoAll[1], zcoAll[1]]
        g_point_2 = [ycoAll[-2], zcoAll[-2]]
        g_point_3 = [ycoAll[8], zcoAll[8]]
        g_point_4 = [ycoAll[6], zcoAll[6]]
        
        g_yt = max(ycoAll)
        g_yb = min(ycoAll)
        g_zt = max(zcoAll)
        g_zb = min(zcoAll)
        
        s_point_1 = [slab_y[0], slab_z[0]]
        s_point_2 = [slab_y[-2], slab_z[-2]]
        s_point_3 = [slab_y[2], slab_z[2]]
        s_point_4 = [slab_y[1], slab_z[1]]
        
        s_yt = max(slab_y)
        s_yb = min(slab_y)
        s_zt = max(slab_z)
        s_zb = min(slab_z)
        
        yt = max(ycoAll, slab_y)
        yb = min(ycoAll, slab_y)
        zt = max(zcoAll, slab_z)
        zb = min(zcoAll, slab_z)
        
        # 재료 값
        slab_elast = 1.0 / options["matl_elast"]
        girder_elast = 1.0
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": ycoAll,
                    "z": zcoAll,
                    "reference": {
                        "name": "girder",
                        "elast": girder_elast
                    }
                },
                {
                    "y": slab_y,
                    "z": slab_z,
                    "reference": {
                        "name": "slab",
                        "elast": slab_elast
                    }
                }
            ],
            "inner": [
                {
                    "y": yciAll,
                    "z": zciAll,
                    "reference": {
                        "name": "girder",
                        "elast": girder_elast
                    }
                }
            ]
        }
        
        # 기준 좌표 반환
        reference_points = {
            "girder": {
                "point_1": g_point_1,
                "point_2": g_point_2,
                "point_3": g_point_3,
                "point_4": g_point_4,
                "yt": g_yt,
                "yb": g_yb,
                "zt": g_zt,
                "zb": g_zb
            },
            "slab": {
                "point_1": s_point_1,
                "point_2": s_point_2,
                "point_3": s_point_3,
                "point_4": s_point_4,
                "yt": s_yt,
                "yb": s_yb,
                "zt": s_zt,
                "zb": s_zb
            },
            "total": {
                "point_1": g_point_1,
                "point_2": g_point_2,
                "point_3": g_point_3,
                "point_4": g_point_4
            },
            "extreme_fiber":{
                "yt": yt,
                "yb": yb,
                "zt": zt,
                "zb": zb
            }
        }
        
        # 특성 컨트롤 데이터
        properties_control = {
            "name": ["girder", "slab"],
            "control": "girder"
        }

        # 특정 Dimension 추출
        ref_dimension = {
                "girder_height": {
                    "value": t1 + t2 + H
                },
                "girder_web_thickness": {
                    "left": tw1,
                    "right": tw2,
                    "left_inclined": twx1,
                    "right_inclined": twx2
                },
                "girder_width": {
                    "top": B1 + B2 + B3,
                    "bottom": B4 + B5 + B6
                },
                "girder_height_to_slab": {
                    "bottom": t1 + t2 + H + Hh,
                    "top": t1 + t2 + H + Hh + tc
                }
            }
        
        return vertices, reference_points, properties_control, ref_dimension
    
