from abc import ABC, abstractmethod
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.offset_change import OffsetChange
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.base_properties import CommonProperties
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.composite_properties import CompositeProperties
from urllib.parse import quote

import requests

class BaseSection(ABC):
    """모든 단면 유형의 기본 클래스"""
    
    def __init__(self, section_data, unit_system):
        """
        vertices :{
            "outer": [
                {
                    "y": [y1, y2, y3, ...],
                    "z": [z1, z2, z3, ...],
                    "material":{
                        "ref_name": "main",
                        "elast": number,
                        ....
                    }
                },
                ...
            ],
            "inner": [
                {   
                    "y": [y1, y2, y3, ...],
                    "z": [z1, z2, z3, ...],
                    "material":{
                        "ref_name": "main",
                        ....
                    }
                },
                ...
            ]
        }
        """
        self.section_data = section_data
        self.unit_system = unit_system
        
        self.vertices_i = {}
        self.reference_points_i = {}
        self.properties_control_i = {}
        self.properties_i = {}
        
        self.vertices_j = {}
        self.reference_points_j = {}
        self.properties_control_j = {}
        self.properties_j = {}
        
        self.ref_dimension_i = {}
        self.ref_dimension_j = {}
        
        self.offset_point_i = {}
        self.offset_point_j = {}
        
    def process(self):
        """단면 데이터 처리"""
        
        self.calculate_vertices()
        
        if self.vertices_i.get("error"):
            return {
                "error": self.vertices_i.get("error"),
                "error_code": self.vertices_i.get("error_code")
            }
        
        self.calculate_properties()
        self.calculate_offset()

        section_type = self.section_data.get("SECTTYPE", "")
        section_shape = self.section_data.get("SECT_BEFORE", {}).get("SECT_SHAPE", "")
        
        section_data = {
            "base_data": self.base_data,
            "i_data":{
                "vertices": self.vertices_i,
                "reference_points": self.reference_points_i,
                "properties_control": self.properties_control_i,
                "properties": self.properties_i,
                "offset_points": self.offset_point_i
            },
            "j_data":{}
        }
        
        if section_type in ["COMPOSITE"]:
            section_data["i_data"]["ref_dimension"] = self.ref_dimension_i
        
        if section_type in ["TAPERED"]:
            section_data["j_data"] = {
                "vertices": self.vertices_j,
                "reference_points": self.reference_points_j,
                "properties_control": self.properties_control_j,
                "properties": self.properties_j,
                "offset_points": self.offset_point_j
            }
        
        if section_type in ["TAPERED"] and section_shape in ["CP_B", "CP_I", "CP_T", "CSGB", "CSGI", "CSGT", "CPCI", "CPCT"]:
            section_data["j_data"]["ref_dimension"] = self.ref_dimension_j
        
        return section_data

    @abstractmethod
    def calculate_vertices(self):
        """정점 처리"""
        pass
    
    def calculate_properties(self):
        """단면 속성 계산"""
        
        if self.vertices_i.get("error"):
            self.properties_i = {"error": "vertices is not found"}
            return self.properties_i
        
        properties = CommonProperties().calculate_properties(self.vertices_i, self.reference_points_i, self.properties_control_i)
        self.properties_i = properties
        
        CompositeProperties().calculate_properties(self.vertices_i, self.reference_points_i, self.properties_i, self.properties_control_i)
        
        return self.properties_i
    
    def _get_section_data(self, db_name, section_shape, section_name):
        """DB 단면은 API를 통해 데이터를 가져오자"""
        encoded_section_name = quote(section_name, safe='') 
        
        url = f"https://moa.rpm.kr-dv-midasit.com/backend/wgsd/dbase/sections/codes/{db_name}/types/{section_shape}/names/{encoded_section_name}"
        response = requests.get(url)
        
        try:
            return response.json()
        except:
            return {"error": "failed to get DB section data"}

    def calculate_offset(self):
        """offset 처리"""
        
        self.offset_point_i = OffsetChange.calculate_offset(self.section_data, self.properties_i, self.reference_points_i)
        
        return self.offset_point_i

