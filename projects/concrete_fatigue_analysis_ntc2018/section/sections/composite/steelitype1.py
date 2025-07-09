from projects.concrete_fatigue_analysis_ntc2018.section.base.composite_base import CompositeBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class SteelIType1Section(CompositeBaseSection):
    """Compostie: Steel I Type 1 Section"""
    
    def _generate_shape_vertices(self, dimensions, dimensions_sub, options):
        
        # Variable Initialization
        Hw, tw, B1, tf1, B2, tf2 = dimensions["vSize"]
        Bc, tc, Hh = dimensions_sub["slab"]
        
        # Outer Cell - Left Side
        ycol = [0]
        zcol = [-(tc + Hh)]
        ycol.append(-(B1 / 2))
        zcol.append(zcol[0])
        ycol.append(ycol[1])
        zcol.append(zcol[1] - tf1)
        ycol.append(-(tw / 2))
        zcol.append(zcol[2])
        ycol.append(ycol[3])
        zcol.append(zcol[3] - Hw)
        ycol.append(-(B2 / 2))
        zcol.append(zcol[4])
        ycol.append(ycol[5])
        zcol.append(zcol[5] - tf2)
        ycol.append(0)
        zcol.append(zcol[6])
        
        # Outer Cell - Right Side
        ycor = [-x for x in ycol]
        zcor = zcol.copy()
        
        # Reverse
        ycor.reverse()
        zcor.reverse()
        
        # Remove Origin
        ycor.pop(0)
        zcor.pop(0)
        
        # All Cell
        ycoAll = ycol + ycor
        zcoAll = zcol + zcor
        
        # Slab
        slab_result = ShapeGenerator.generate_solid_rectangle_shape(tc, Bc)
        slab_y = slab_result["y"]
        slab_z = slab_result["z"]
        
        # 원점 좌표로 이동
        yo = TransFormGeometry.calculate_origin_coordinates(ycoAll, slab_y)
        zo = TransFormGeometry.calculate_origin_coordinates(zcoAll, slab_z)
        
        ycoAll = [y - yo for y in ycoAll]
        zcoAll = [z - zo for z in zcoAll]
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
                "value": tf1 + tf2 + Hw
            },
            "girder_web_thickness": {
                "value": tw
            },
            "girder_width": {
                "top": B1,
                "bottom": B2
            },
            "girder_height_to_slab": {
                "bottom": tf1 + tf2 + Hw + Hh,
                "top": tf1 + tf2 + Hw + Hh + tc
            }
        }
        
        return vertices, reference_points, properties_control, ref_dimension
    
