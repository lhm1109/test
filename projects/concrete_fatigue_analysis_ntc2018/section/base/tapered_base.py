from projects.concrete_fatigue_analysis_ntc2018.section.base_section import BaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.offset_change import OffsetChange

import copy

class TaperedBaseSection(BaseSection):

    def __init__(self, section_data, unit_system):
        super().__init__(section_data, unit_system)
        
        self.section_shape = section_data.get("SECT_BEFORE", {}).get("SHAPE", "")
        self.i_data = {}
        self.j_data = {}
        self.base_data = {}
        
        if self.section_shape in ["L", "C", "H", "T", "B", "P", "2L", "2C", "SB", "SR", "OCT", "SOCT", "TRK", "STRK", "HTRK"]:
            self._create_dbuservalue_section(section_data)
        elif self.section_shape in ["1CEL", "2CEL", "3CEL", "NCEL", "NCE2", "PSCM", "PSCI", "PSCH", "PSCT", "PSCB", "CMPW"]:
            self._create_psc_section(section_data)
        elif self.section_shape in ["CP_B", "CP_I", "CP_T", "CSGB", "CSGI", "CSGT", "CPCI", "CPCT"]:
            self._create_composite_section(section_data)

    def calculate_vertices(self):
        
        if not (self.i_data and self.j_data):
            self.vertices_i = {"error": "Invalid section data"}
            return self.vertices_i, self.reference_points_i, self.properties_control_i, self.ref_dimension_i, self.properties_i, self.vertices_j, self.reference_points_j, self.properties_control_j, self.ref_dimension_j, self.properties_j
        
        self.vertices_i, self.reference_points_i, self.properties_control_i, self.ref_dimension_i, self.properties_i, self.vertices_j, self.reference_points_j, self.properties_control_j, self.ref_dimension_j, self.properties_j = self._generate_shape_vertices()
    
    def calculate_properties(self):
        # 이미 _generate_shape_vertices()에서 계산했으므로 그대로 반환
        return

    def calculate_offset(self):
        
        self.offset_point_i = OffsetChange.calculate_offset(self.section_data, self.properties_i, self.reference_points_i)
        self.offset_point_j = OffsetChange.calculate_offset(self.section_data, self.properties_j, self.reference_points_j)
        
        return self.offset_point_i, self.offset_point_j
    
    def _create_dbuservalue_section(self, section_data):
        """DBUSER/VALUE 단면 생성"""
        
        data_type = section_data.get("SECT_BEFORE", {}).get("TYPE",0)
        
        self.base_data = {
            "name": section_data.get("SECT_NAME"),
            "type": "TAPERED",
            "shape": section_data.get("SECT_BEFORE", {}).get("SHAPE", ""),
            "unit_system": self.unit_system
        }
        
        if data_type == 1:
            self.i_data = {
                "SECT_NAME": section_data.get("SECT_NAME"),
                "SECT_BEFORE":{
                    "OFFSET_PT": section_data.get("SECT_BEFORE", {}).get("OFFSET_PT", {}),
                    "OFFSET_CENTER": section_data.get("SECT_BEFORE", {}).get("OFFSET_CENTER", {}),
                    "USER_OFFSET_REF": section_data.get("SECT_BEFORE", {}).get("USER_OFFSET_REF", {}),
                    "HORZ_OFFSET_OPT": section_data.get("SECT_BEFORE", {}).get("HORZ_OFFSET_OPT", {}),
                    "USERDEF_OFFSET_YI": section_data.get("SECT_BEFORE", {}).get("USERDEF_OFFSET_YI", {}),
                    "VERT_OFFSET_OPT": section_data.get("SECT_BEFORE", {}).get("VERT_OFFSET_OPT", {}),
                    "USERDEF_OFFSET_ZI": section_data.get("SECT_BEFORE", {}).get("USERDEF_OFFSET_ZI", {}),
                    "DATATYPE": data_type,
                    "SHAPE": section_data.get("SECT_BEFORE", {}).get("SHAPE", ""),
                    "SECT_I": {
                        "DB_NAME": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("DB_NAME", ""),
                        "SECT_NAME": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("SECT_NAME", ""),
                    }
                }
            }
            self.j_data = copy.deepcopy(self.i_data)
            self.j_data["SECT_BEFORE"]["SECT_I"]["SECT_NAME"] = section_data.get("SECT_BEFORE", {}).get("SECT_J", {}).get("SECT_NAME", "")
        
        elif data_type == 2 or data_type == 3:
            self.i_data = {
                "SECT_NAME": section_data.get("SECT_NAME"),
                "SECT_BEFORE":{
                    "DATATYPE": data_type,
                    "SHAPE": section_data.get("SECT_BEFORE", {}).get("SHAPE", ""),
                    "SECT_I": {
                        "vSIZE": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE", []),
                    }
                }
            }
            
            self.j_data = copy.deepcopy(self.i_data)
            self.j_data["SECT_BEFORE"]["SECT_I"]["vSIZE"] = section_data.get("SECT_BEFORE", {}).get("SECT_J", {}).get("vSIZE", [])
    
    def _create_psc_section(self, section_data):
        """PSC 단면 생성"""
        
        self.base_data = {
            "name": section_data.get("SECT_NAME"),
            "type": "TAPERED",
            "shape": section_data.get("SECT_BEFORE", {}).get("SHAPE", ""),
            "unit_system": self.unit_system
        }
        
        self.i_data = {
            "SECT_NAME": section_data.get("SECT_NAME"),
            "SECTTYPE": section_data.get("SECTTYPE"),
            "SECT_BEFORE": {
                "SHAPE": section_data.get("SECT_BEFORE", {}).get("SHAPE", ""),
                "SECT_I": {
                    "vSIZE": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE", []),
                    "vSIZE_PSC_A": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE_PSC_A", []),
                    "vSIZE_PSC_B": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE_PSC_B", []),
                    "vSIZE_PSC_C": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE_PSC_C", []),
                    "vSIZE_PSC_D": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE_PSC_D", []),
                    "OUTER_POLYGON": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("OUTER_POLYGON", []),
                    "INNER_POLYGON": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("INNER_POLYGON", []),
                    "SWIDTH": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("SWIDTH", [])
                },
                "JOINT": section_data.get("SECT_BEFORE", {}).get("JOINT", None),
                "PSC_OPT1": section_data.get("SECT_BEFORE", {}).get("PSC_OPT1", None),
                "PSC_OPT2": section_data.get("SECT_BEFORE", {}).get("PSC_OPT2", None),
                "USE_SYMMETRIC": section_data.get("SECT_BEFORE", {}).get("USE_SYMMETRIC", None),
                "USE_SMALL_HOLE": section_data.get("SECT_BEFORE", {}).get("USE_SMALL_HOLE", None),
                "MATL_ELAST": section_data.get("SECT_BEFORE", {}).get("MATL_ELAST", None),
                "MATL_DENS": section_data.get("SECT_BEFORE", {}).get("MATL_DENS", None),
                "MATL_POIS_S": section_data.get("SECT_BEFORE", {}).get("MATL_POIS_S", None),
                "MATL_POIS_C": section_data.get("SECT_BEFORE", {}).get("MATL_POIS_C", None)
            }
        }
        
        self.j_data = {
            "SECT_NAME": section_data.get("SECT_NAME"),
            "SECTTYPE": section_data.get("SECTTYPE"),
            "SECT_BEFORE": {
                "SHAPE": section_data.get("SECT_BEFORE", {}).get("SHAPE", ""),
                "SECT_I": {
                    "vSIZE": section_data.get("SECT_BEFORE", {}).get("SECT_J", {}).get("vSIZE", []),
                    "vSIZE_PSC_A": section_data.get("SECT_BEFORE", {}).get("SECT_J", {}).get("vSIZE_PSC_A", []),
                    "vSIZE_PSC_B": section_data.get("SECT_BEFORE", {}).get("SECT_J", {}).get("vSIZE_PSC_B", []),
                    "vSIZE_PSC_C": section_data.get("SECT_BEFORE", {}).get("SECT_J", {}).get("vSIZE_PSC_C", []),
                    "vSIZE_PSC_D": section_data.get("SECT_BEFORE", {}).get("SECT_J", {}).get("vSIZE_PSC_D", []),
                    "OUTER_POLYGON": section_data.get("SECT_BEFORE", {}).get("SECT_J", {}).get("OUTER_POLYGON", []),
                    "INNER_POLYGON": section_data.get("SECT_BEFORE", {}).get("SECT_J", {}).get("INNER_POLYGON", []),
                    "SWIDTH": section_data.get("SECT_BEFORE", {}).get("SECT_J", {}).get("SWIDTH", [])
                },
                "JOINT": section_data.get("SECT_BEFORE", {}).get("JOINT", None),
                "PSC_OPT1": section_data.get("SECT_BEFORE", {}).get("PSC_OPT1", None),
                "PSC_OPT2": section_data.get("SECT_BEFORE", {}).get("PSC_OPT2", None),
                "USE_SYMMETRIC": section_data.get("SECT_BEFORE", {}).get("USE_SYMMETRIC", None),
                "USE_SMALL_HOLE": section_data.get("SECT_BEFORE", {}).get("USE_SMALL_HOLE", None),
                "MATL_ELAST": section_data.get("SECT_BEFORE", {}).get("MATL_ELAST", None),
                "MATL_DENS": section_data.get("SECT_BEFORE", {}).get("MATL_DENS", None),
                "MATL_POIS_S": section_data.get("SECT_BEFORE", {}).get("MATL_POIS_S", None),
                "MATL_POIS_C": section_data.get("SECT_BEFORE", {}).get("MATL_POIS_C", None)
            }
        }
    
    def _create_composite_section(self, section_data):
        """Composite 단면 생성"""
        
        self.base_data = {
            "name": section_data.get("SECT_NAME"),
            "type": "TAPERED",
            "shape": section_data.get("SECT_BEFORE", {}).get("SHAPE", ""),
            "unit_system": self.unit_system
        }
        
        self.i_data = {
            "SECT_NAME": section_data.get("SECT_NAME"),
            "SECTTYPE": section_data.get("SECTTYPE"),
            "SECT_BEFORE": {
                "SHAPE": section_data.get("SECT_BEFORE", {}).get("SHAPE", ""),
                "SECT_I": {
                    "vSIZE": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE", []),
                    "vSIZE_PSC_A": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE_PSC_A", []),
                    "vSIZE_PSC_B": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE_PSC_B", []),
                    "vSIZE_PSC_C": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE_PSC_C", []),
                    "vSIZE_PSC_D": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE_PSC_D", []),
                    "OUTER_POLYGON": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("OUTER_POLYGON", []),
                    "INNER_POLYGON": section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("INNER_POLYGON", []),
                },
                "MATL_ELAST": section_data.get("SECT_BEFORE", {}).get("MATL_ELAST", None),
                "MATL_DENS": section_data.get("SECT_BEFORE", {}).get("MATL_DENS", None),
                "MATL_POIS_S": section_data.get("SECT_BEFORE", {}).get("MATL_POIS_S", None),
                "MATL_POIS_C": section_data.get("SECT_BEFORE", {}).get("MATL_POIS_C", None),
                "MATL_THERMAL": section_data.get("SECT_BEFORE", {}).get("MATL_THERMAL", None),
                "JOINT": section_data.get("SECT_BEFORE", {}).get("JOINT", None),
            },
            "SECT_AFTER": {
                "SECT_I": {
                    "vSIZE": section_data.get("SECT_AFTER", {}).get("SECT_I", {}).get("vSIZE", []),
                },
                "SLAB": section_data.get("SECT_AFTER", {}).get("SLAB", None),
            }
        }
        
        self.j_data = {
            "SECT_NAME": section_data.get("SECT_NAME"),
            "SECTTYPE": section_data.get("SECTTYPE"),
            "SECT_BEFORE": {
                "SHAPE": section_data.get("SECT_BEFORE", {}).get("SHAPE", ""),
                "SECT_I": {
                    "vSIZE": section_data.get("COMPOSITE_J", {}).get("vSIZE", []),
                    "vSIZE_PSC_A": section_data.get("COMPOSITE_J", {}).get("vSIZE_PSC_A", []),
                    "vSIZE_PSC_B": section_data.get("COMPOSITE_J", {}).get("vSIZE_PSC_B", []),
                    "vSIZE_PSC_C": section_data.get("COMPOSITE_J", {}).get("vSIZE_PSC_C", []),
                    "vSIZE_PSC_D": section_data.get("COMPOSITE_J", {}).get("vSIZE_PSC_D", []),
                    "OUTER_POLYGON": section_data.get("SECT_BEFORE", {}).get("SECT_J", {}).get("OUTER_POLYGON", []),
                    "INNER_POLYGON": section_data.get("SECT_BEFORE", {}).get("SECT_J", {}).get("INNER_POLYGON", []),
                },
                "MATL_ELAST": section_data.get("SECT_BEFORE", {}).get("MATL_ELAST", None),
                "MATL_DENS": section_data.get("SECT_BEFORE", {}).get("MATL_DENS", None),
                "MATL_POIS_S": section_data.get("SECT_BEFORE", {}).get("MATL_POIS_S", None),
                "MATL_POIS_C": section_data.get("SECT_BEFORE", {}).get("MATL_POIS_C", None),
                "MATL_THERMAL": section_data.get("SECT_BEFORE", {}).get("MATL_THERMAL", None),
                "JOINT": section_data.get("SECT_BEFORE", {}).get("JOINT", None),
            },
            "SECT_AFTER": {
                "SECT_I": {
                    "vSIZE": section_data.get("SECT_AFTER", {}).get("SECT_J", {}).get("vSIZE", []),
                },
                "SLAB": section_data.get("SECT_AFTER", {}).get("SLAB", None),
            }
        }
    
    def _generate_shape_vertices(self, data, psc_data, composite_data):
        """단면 정점 생성"""
        raise NotImplementedError