from projects.concrete_fatigue_analysis_ntc2018.section.base_section import BaseSection

class DBUserValueBaseSection(BaseSection):
    """
    DBUSER 단면 기본 클래스
    
    그 외 공통 속성을 처리하자
    """
    
    def __init__(self, section_data, unit_system):
        super().__init__(section_data, unit_system)
        
        self.section_type = section_data.get("SECTTYPE")
        self.data_type = section_data.get("SECT_BEFORE",{}).get("DATATYPE",3)
        
        self.base_data = self._build_base_data()

    def _build_base_data(self):
        """DBUser/Value 단면 기본 데이터 생성"""
        base_data = {
            "name": self.section_data.get("SECT_NAME"),
            "type": self.section_type,
            "shape": self.section_data.get("SECT_BEFORE").get("SHAPE"),
            "unit_system": self.unit_system
        }
        
        if self.section_type == "DBUSER" and self.data_type == 1:
            base_data.update({
                "data_base": {
                    "db_name": self.section_data.get("SECT_BEFORE").get("SECT_I").get("DB_NAME"),
                    "section_name": self.section_data.get("SECT_BEFORE").get("SECT_I").get("SECT_NAME")
                }
            })
        else:
            base_data["data_type"] = "USER" if self.data_type=="DBUSER" else "VALUE"
        
        return base_data
    
    def calculate_vertices(self):
        """단면 정점 계산의 공통 로직"""
        
        if self.data_type not in (1, 2, 3):
            self.vertices_i = {
                "error": "data_type is not found",
                "error_code": "DBUSERVALUEBASESECTION_CALCULATE_VERTICES"
            }
            return self.vertices_i, self.reference_points_i, self.properties_control_i
        
        dimensions = None
        if self.data_type == 1:
            """
            DB 단면은 일단 막아두도록 하자. Section DB를 제대로 구현할 수 있게 되면 해제하자
            DB 가 없는 단면은 처음부터 None으로 반환됨
            """
            self.vertices_i = {
                "error": "DB section is not supported",
                "error_code": "DBUSERVALUEBASESECTION_CALCULATE_VERTICES"
            }
            return self.vertices_i, self.reference_points_i, self.properties_control_i
            # db_name = self.section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("DB_NAME")
            # section_shape = self._get_section_shape()
            # section_name = self.section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("SECT_NAME")
            
            # data_base = self._get_section_data(db_name, section_shape, section_name)
            # if data_base.get("error"):
            #     self.vertices = {"error": "failed to get DB section data"}
            #     return
            
            # dimensions = self._get_dimensions_from_db_data(data_base)
        
        elif self.data_type in (2, 3):
            vSize = self.section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE", [])
            
            cell_shape = self.section_data.get("SECT_BEFORE", {}).get("CELL_SHAPE", 0)
            cell_type = self.section_data.get("SECT_BEFORE", {}).get("CELL_TYPE", 0)
            cold_shape = self.section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("SHAPE", 0)
        
            options = {
                "cell_shape": cell_shape,
                "cell_type": cell_type,
                "cold_shape": cold_shape
            }
            
            if not vSize:
                self.vertices_i = { 
                    "error": "vSize is not found",
                    "error_code": "DBUSERVALUEBASESECTION_CALCULATE_VERTICES"
                }
                return self.vertices_i, self.reference_points_i, self.properties_control_i
            
            dimensions = self._get_dimensions_from_vsize(vSize)
        
        if not dimensions:
            self.vertices_i = {
                "error": "dimensions is not found",
                "error_code": "DBUSERVALUEBASESECTION_CALCULATE_VERTICES"
            }
            return self.vertices_i, self.reference_points_i, self.properties_control_i
        
        self.vertices_i, self.reference_points_i, self.properties_control_i = self._generate_shape_vertices(dimensions, options)
        
        return self.vertices_i, self.reference_points_i, self.properties_control_i
    
    # 자식 클래스에서 구현해야 할 추상 메서드들
    def _get_section_shape(self):
        """DB에서 사용할 단면 형상 이름"""
        raise NotImplementedError
        
    def _get_dimensions_from_db_data(self, data_base):
        """DB에서 가져온 데이터로부터 치수 정보 추출"""
        raise NotImplementedError
        
    def _get_dimensions_from_vsize(self, vSize):
        """vSize 배열에서 치수 정보 추출"""
        raise NotImplementedError
        
    def _generate_shape_vertices(self, dimensions, options={}):
        """단면 정점 생성"""
        raise NotImplementedError