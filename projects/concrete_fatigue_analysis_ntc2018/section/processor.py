from projects.concrete_fatigue_analysis_ntc2018.section.sections.dbuser import (
    AngleSection, ChannelSection, HSection, TSection, BoxSection, PipeSection, DoubleAngleSection,
    StarBattenedAngleSection, DoubleChannelSection, SolidRectangleSection, SolidRoundSection,
    OctagonSection, SolidOctagonSection, ROctagonSection, TrackSection, SolidTrackSection,
    HalfTrackSection, UprightSection, URibSection, BoxwithStiffenerSection, PipewithStiffenerSection,
    InvertedTSection, ColdFormedChannelSection, ZSection
)

from projects.concrete_fatigue_analysis_ntc2018.section.sections.psc import (
    Cell1Section, Cell2Section, Cell3Section, PlatSection, IShapeSection, TShapeSection,
    HalfSection, MidSection, NCellSection, NCell2Section, CMPWebSection
)

from projects.concrete_fatigue_analysis_ntc2018.section.sections.composite import (
    SteelBoxType1Section, SteelBoxType2Section, SteelIType1Section, SteelIType2Section,
    SteelTubType1Section, SteelTubType2Section, CompositeISection, CompositeTSection
)

from projects.concrete_fatigue_analysis_ntc2018.section.sections.tapered import (
    DBUSERVALUETaperedSection, PSCTaperedSection, CompositeTaperedSection
)

from projects.concrete_fatigue_analysis_ntc2018.section.sections.steelRC import (
    RectBoxOpenSection, RectBoxCloseSection, RectPipeOpenSection, RectPipeCloseSection,
    CircleBoxOpenSection, CircleBoxCloseSection, CirclePipeOpenSection, CirclePipeCloseSection,
    SRCBoxSection, SRCPipeSection, RectHBeamSection, CircleHBeamSection,
    RectCrossHSection, RectCombinedTSection, SRCBoxStiffenerSection, SRCPipeStiffenerSection
)

from projects.concrete_fatigue_analysis_ntc2018.section.sections.combined import (
    H2CombinedSection, HC1CombinedSection, HC2CombinedSection, HTCombinedSection,
    T21CombinedSection, T22CombinedSection, H2TCombinedSection,
    WebOpendHStiffenedSection, FlangeOpendHStiffenedSection,
    C21WebPlateSection, C22WebPlateSection, C1WebPlateSection, C2WebPlateSection,
    Angle4Section, HPlateSection
)

class SectionProcessor:
    """단면 데이터 처리 클래스"""
    
    def __init__(self, json_data, unit_system):
        self.section_data = json_data
        units = unit_system.get("UNIT", {}).get("1").get("DIST")
        self.unit_system = units.lower()
        
        self.section_map = self._build_section_map()
        
    def _build_section_map(self):
        """단면 유형과 클래스 매핑 구성"""
        return {
            "DBUSER": {
                "L": AngleSection,
                "C": ChannelSection,
                "H": HSection,
                "T": TSection,
                "B": BoxSection,
                "P": PipeSection,
                "2L": DoubleAngleSection,
                "CL": StarBattenedAngleSection,
                "2C": DoubleChannelSection,
                "SB": SolidRectangleSection,
                "SR": SolidRoundSection,
                "OCT": OctagonSection,
                "SOCT": SolidOctagonSection,
                "ROCT": ROctagonSection,
                "TRK": TrackSection,
                "STRK": SolidTrackSection,
                "HTRK": HalfTrackSection,
                "CC": ColdFormedChannelSection,
                "Z": ZSection,
                "UP": UprightSection,
                "URIB": URibSection,
                "BSTF": BoxwithStiffenerSection,
                "PSTF": PipewithStiffenerSection,
                "UDT": InvertedTSection,
            },
            "VALUE": {
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
                "ROCT": ROctagonSection,
                "TRK": TrackSection,
                "STRK": SolidTrackSection,
                "HTRK": HalfTrackSection,
            },
            "PSC":{
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
            },
            "COMPOSITE": {
                "B": SteelBoxType1Section,
                "I": SteelIType1Section,
                "Tub": SteelTubType1Section,
                "GB": SteelBoxType2Section,
                "GI": SteelIType2Section,
                "GT": SteelTubType2Section,
                "CI": CompositeISection,
                "CT": CompositeTSection
            },
            "TAPERED": {
                "L": DBUSERVALUETaperedSection,
                "C": DBUSERVALUETaperedSection,
                "H": DBUSERVALUETaperedSection,
                "T": DBUSERVALUETaperedSection,
                "B": DBUSERVALUETaperedSection,
                "P": DBUSERVALUETaperedSection,
                "2L": DBUSERVALUETaperedSection,
                "2C": DBUSERVALUETaperedSection,
                "SB": DBUSERVALUETaperedSection,
                "SR": DBUSERVALUETaperedSection,
                "OCT": DBUSERVALUETaperedSection,
                "SOCT": DBUSERVALUETaperedSection,
                "ROCT": DBUSERVALUETaperedSection,
                "TRK": DBUSERVALUETaperedSection,
                "STRK": DBUSERVALUETaperedSection,
                "HTRK": DBUSERVALUETaperedSection,
                "1CEL": PSCTaperedSection,
                "2CEL": PSCTaperedSection,
                "3CEL": PSCTaperedSection,
                "PSCB": PSCTaperedSection,
                "PSCI": PSCTaperedSection,
                "PSCT": PSCTaperedSection,
                "PSCH": PSCTaperedSection,
                "PSCM": PSCTaperedSection,
                "NCEL": PSCTaperedSection,
                "NCE2": PSCTaperedSection,
                "CMPW": PSCTaperedSection,
                "CP_B": CompositeTaperedSection,
                "CP_I": CompositeTaperedSection,
                "CP_T": CompositeTaperedSection,
                "CSGB": CompositeTaperedSection,
                "CSGI": CompositeTaperedSection,
                "CSGT": CompositeTaperedSection,
                "CPCI": CompositeTaperedSection,
                "CPCT": CompositeTaperedSection
            },
            "SRC": {
                "RBO": RectBoxOpenSection,
                "RBC": RectBoxCloseSection,
                "RPO": RectPipeOpenSection,
                "RPC": RectPipeCloseSection,
                "CBO": CircleBoxOpenSection,
                "CBC": CircleBoxCloseSection,
                "CPO": CirclePipeOpenSection,
                "CPC": CirclePipeCloseSection,
                "EBC": SRCBoxSection,
                "EPC": SRCPipeSection,
                "RHB": RectHBeamSection,
                "CHB": CircleHBeamSection,
                "RH2T": RectCrossHSection,
                "RHT": RectCombinedTSection,
                "SBSF": SRCBoxStiffenerSection,
                "SPSF": SRCPipeStiffenerSection
            },
            "COMBINED": {
                "2H": H2CombinedSection,
                "HC1": HC1CombinedSection,
                "HC2": HC2CombinedSection,
                "HT": HTCombinedSection,
                "2T1": T21CombinedSection,
                "2T2": T22CombinedSection,
                "H2T": H2TCombinedSection,
                "WOH": WebOpendHStiffenedSection,
                "FOH": FlangeOpendHStiffenedSection,
                "2CW1": C21WebPlateSection,
                "2CW2": C22WebPlateSection,
                "1CW1": C1WebPlateSection,
                "1CW2": C2WebPlateSection,
                "4L": Angle4Section,
                "HP": HPlateSection
            }
        }
    
    def get_section_class(self, section_type, section_shape):
        """타입과 형태에 따른 단면 클래스 반환"""
        return self.section_map.get(section_type, {}).get(section_shape)
    
    def process_all_sections(self):
        """
        모든 단면 데이터 처리
        
        SECT의 JSON 구조 전체를 받아서, 각 단면 타입과 형태에 따라 구분하여 각 클래스로 처리
        """
        
        results = {}
        
        if self.section_data.get("SECT", {}) == {}:
            return {
                "error": "Section data is not found",
                "error_code": "SECTIONPROCESSOR_PROCESS_ALL_SECTIONS"
            }
        
        for section_id, section_data in self.section_data.get("SECT", {}).items():
            section_type = section_data.get("SECTTYPE")
            section_shape = section_data.get("SECT_BEFORE").get("SHAPE")
            
            SectionClass = self.get_section_class(section_type, section_shape)
            
            if SectionClass:
                section = SectionClass(section_data, self.unit_system)
                results[section_id] = section.process()
                
                # print(f"Section {section_id} processed successfully.")
            else:
                results[section_id] = {"error": f"Section type {section_type} with shape {section_shape} is not supported."}
                print(f"Warning: Section type {section_type} with shape {section_shape} is not supported.")
        
        print(f'{len(results)} sections processed successfully.')
        
        return results
        