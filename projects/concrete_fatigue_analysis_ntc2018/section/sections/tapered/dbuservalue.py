from projects.concrete_fatigue_analysis_ntc2018.section.base.tapered_base import TaperedBaseSection
from projects.concrete_fatigue_analysis_ntc2018.section.sections.dbuser import (
    AngleSection, ChannelSection, HSection, TSection, BoxSection, PipeSection, DoubleAngleSection,
    DoubleChannelSection, SolidRectangleSection, SolidRoundSection,
    OctagonSection, SolidOctagonSection,  TrackSection, SolidTrackSection,
    HalfTrackSection
)

class DBUSERVALUETaperedSection(TaperedBaseSection):
    """DBUSER: Angle Section"""
    
    def _generate_shape_vertices(self):
        
        Mapping = {
            "L": AngleSection,
            "C": ChannelSection,
            "H": HSection,
            "T": TSection,
            "B": BoxSection,
            "P": PipeSection,
            "2L": DoubleAngleSection,
            "2C": DoubleChannelSection,
            "SB": SolidRectangleSection,
            "SR": SolidRoundSection,
            "OCT": OctagonSection,
            "SOCT": SolidOctagonSection,
            "TRK": TrackSection,
            "STRK": SolidTrackSection,
            "HTRK": HalfTrackSection
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
    