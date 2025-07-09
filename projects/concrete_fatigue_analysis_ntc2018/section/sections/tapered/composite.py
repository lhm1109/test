from projects.concrete_fatigue_analysis_ntc2018.section.base.tapered_base import TaperedBaseSection
from projects.concrete_fatigue_analysis_ntc2018.section.sections.composite import (
    SteelBoxType1Section, SteelBoxType2Section, SteelIType1Section, SteelIType2Section,
    SteelTubType1Section, SteelTubType2Section, CompositeISection, CompositeTSection
)

class CompositeTaperedSection(TaperedBaseSection):
    """PSC: Angle Section"""
    
    def _generate_shape_vertices(self):
        
        Mapping = {
            "CP_B": SteelBoxType1Section,
            "CP_I": SteelIType1Section,
            "CP_T": SteelTubType1Section,
            "CSGB": SteelBoxType2Section,
            "CSGI": SteelIType2Section,
            "CSGT": SteelTubType2Section,
            "CPCI": CompositeISection,
            "CPCT": CompositeTSection
        }
        
        Section_Class = Mapping[self.section_shape]
        
        i_section = Section_Class(self.i_data, self.unit_system)
        j_section = Section_Class(self.j_data, self.unit_system)
        
        vertices_i, reference_points_i, properties_control_i, ref_dimension_i = i_section.calculate_vertices()
        vertices_j, reference_points_j, properties_control_j, ref_dimension_j = j_section.calculate_vertices()
        
        if vertices_i.get("error") or vertices_j.get("error"):
            return vertices_i, reference_points_i, properties_control_i, ref_dimension_i, vertices_j, reference_points_j, properties_control_j, ref_dimension_j
        
        properties_i = i_section.calculate_properties()
        properties_j = j_section.calculate_properties()
        
        
        return vertices_i, reference_points_i, properties_control_i, ref_dimension_i, properties_i, vertices_j, reference_points_j, properties_control_j, ref_dimension_j, properties_j
    