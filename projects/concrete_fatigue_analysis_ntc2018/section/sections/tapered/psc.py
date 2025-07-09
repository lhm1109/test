from projects.concrete_fatigue_analysis_ntc2018.section.base.tapered_base import TaperedBaseSection
from projects.concrete_fatigue_analysis_ntc2018.section.sections.psc import (
    Cell1Section, Cell2Section, Cell3Section, PlatSection, IShapeSection, TShapeSection,
    HalfSection, MidSection, NCellSection, NCell2Section, CMPWebSection
)

class PSCTaperedSection(TaperedBaseSection):
    """PSC: Angle Section"""
    
    def _generate_shape_vertices(self):
        
        Mapping = {
            "1CEL": Cell1Section,
            "2CEL": Cell2Section,
            "3CEL": Cell3Section,
            "PSCB": PlatSection,
            "PSCI": IShapeSection,
            "PSCT": TShapeSection,
            "PSCH": HalfSection,
            "PSCM": MidSection,
            "NCEL": NCellSection,
            "NCE2": NCell2Section,
            "CMPW": CMPWebSection
        }
        
        Section_Class = Mapping[self.section_shape]
        
        i_section = Section_Class(self.i_data, self.unit_system)
        j_section = Section_Class(self.j_data, self.unit_system)
        
        vertices_i, reference_points_i, properties_control_i = i_section.calculate_vertices()
        vertices_j, reference_points_j, properties_control_j = j_section.calculate_vertices()
        
        if vertices_i.get("error") or vertices_j.get("error"):
            return vertices_i, reference_points_i, properties_control_i, {}, {}, vertices_j, reference_points_j, properties_control_j, {}, {}
        
        properties_i = i_section.calculate_properties()
        properties_j = j_section.calculate_properties()
        
        return vertices_i, reference_points_i, properties_control_i, {}, properties_i, vertices_j, reference_points_j, properties_control_j, {}, properties_j
    