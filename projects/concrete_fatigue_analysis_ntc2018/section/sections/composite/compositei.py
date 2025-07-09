from projects.concrete_fatigue_analysis_ntc2018.section.base.composite_base import CompositeBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class CompositeISection(CompositeBaseSection):
    """Compostie: I Section"""
    
    def _generate_shape_vertices(self, dimensions, dimensions_sub, options):
        
        # Variable Initialization
        Bc, tc, Hh = dimensions_sub["slab"]
        _, JL1, JL2, JL3, JL4, _, _, _, _ = options["joint"]
        
        psc_i_coordinates = ShapeGenerator.generate_psc_i_shape(
            dimensions["vSize_PSC_A"],
            dimensions["vSize_PSC_B"],
            dimensions["vSize_PSC_C"],
            dimensions["vSize_PSC_D"],
            options["joint"]
        )
        
        ref_dimension = psc_i_coordinates["reference"]
        
        psc_i_coordinates = TransFormGeometry.translate_coordinates(
            psc_i_coordinates,
            z_offset= -(tc + Hh)
        )
        
        psc_y = psc_i_coordinates["y"]
        psc_z = psc_i_coordinates["z"]
        
        slab_result = ShapeGenerator.generate_solid_rectangle_shape(tc, Bc)
        slab_y = slab_result["y"]
        slab_z = slab_result["z"]
        
        # 원점 좌표로 이동
        yo = TransFormGeometry.calculate_origin_coordinates(psc_y, slab_y)
        zo = TransFormGeometry.calculate_origin_coordinates(psc_z, slab_z)
        
        psc_y = [y - yo for y in psc_y]
        psc_z = [z - zo for z in psc_z]
        slab_y = [y - yo for y in slab_y]
        slab_z = [z - zo for z in slab_z]
        
        # 기준 좌표 추출
        g_point_1 = [psc_y[1], psc_z[1]]
        g_point_2 = [psc_y[-2], psc_z[-2]]
        
        joint_count = JL1 + JL2 + JL3 + JL4
        if joint_count == 0:
            g_point_3 = [psc_y[8], psc_z[8]]
            g_point_4 = [psc_y[6], psc_z[6]]
        elif joint_count == 1:
            g_point_3 = [psc_y[9], psc_z[9]]
            g_point_4 = [psc_y[7], psc_z[7]]
        elif joint_count == 2:
            g_point_3 = [psc_y[10], psc_z[10]]
            g_point_4 = [psc_y[8], psc_z[8]]
        elif joint_count == 3:
            g_point_3 = [psc_y[11], psc_z[11]]
            g_point_4 = [psc_y[9], psc_z[9]]
        elif joint_count == 4:
            g_point_3 = [psc_y[12], psc_z[12]]
            g_point_4 = [psc_y[10], psc_z[10]]
        
        g_yt = max(psc_y)
        g_yb = min(psc_y)
        g_zt = max(psc_z)
        g_zb = min(psc_z)
        
        s_point_1 = [slab_y[0], slab_z[0]]
        s_point_2 = [slab_y[-2], slab_z[-2]]
        s_point_3 = [slab_y[2], slab_z[2]]
        s_point_4 = [slab_y[1], slab_z[1]]
        
        s_yt = max(slab_y)
        s_yb = min(slab_y)
        s_zt = max(slab_z)
        s_zb = min(slab_z)
        
        yt = max(psc_y, slab_y)
        yb = min(psc_y, slab_y)
        zt = max(psc_z, slab_z)
        zb = min(psc_z, slab_z)
        
        # 재료 값
        slab_elast = 1.0 / options["matl_elast"]
        girder_elast = 1.0
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": psc_y,
                    "z": psc_z,
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
        left_height = ref_dimension["girder_height"]["left"]
        right_height = ref_dimension["girder_height"]["right"]
        center_height = ref_dimension["girder_height"]["center"]
        
        height_to_slab_bottom = max((left_height + right_height) / 2, center_height) + Hh
        height_to_slab_top = height_to_slab_bottom + tc
        
        ref_dimension["girder_height_to_slab"] = {
            "bottom": height_to_slab_bottom,
            "top": height_to_slab_top
        }
        
        return vertices, reference_points, properties_control, ref_dimension
    