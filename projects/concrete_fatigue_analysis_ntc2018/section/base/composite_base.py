from projects.concrete_fatigue_analysis_ntc2018.section.base_section import BaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.offset_change import OffsetChange

class CompositeBaseSection(BaseSection):
    """
    Composite 단면 기본 클래스
    
    그 외 공통 속성을 처리하자
    """
    
    def __init__(self, section_data, unit_system):
        super().__init__(section_data, unit_system)
        
        base_data = {
            "name": section_data.get("SECT_NAME"),
            "type": section_data.get("SECTTYPE"),
            "shape": section_data.get("SECT_BEFORE").get("SHAPE"),
            "unit_system": unit_system
        }
        
        self.base_data = base_data

    def calculate_vertices(self):
        """단면 정점 계산의 공통 로직"""
        
        dimensions = None
        options = None
        
        # Dimensions
        vSize =self.section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE", None)
        
        vSize_PSC_A = self.section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE_PSC_A", None)
        vSize_PSC_B = self.section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE_PSC_B", None)
        vSize_PSC_C = self.section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE_PSC_C", None)
        vSize_PSC_D = self.section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("vSIZE_PSC_D", None)
        
        outer_polygon = self.section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("OUTER_POLYGON", None)
        inner_polygon = self.section_data.get("SECT_BEFORE", {}).get("SECT_I", {}).get("INNER_POLYGON", None)
        
        dimensions = {
            "vSize": vSize,
            "vSize_PSC_A": vSize_PSC_A,
            "vSize_PSC_B": vSize_PSC_B,
            "vSize_PSC_C": vSize_PSC_C,
            "vSize_PSC_D": vSize_PSC_D,
            "outer_polygon": outer_polygon,
            "inner_polygon": inner_polygon,
        }
        
        # Dimension_sub
        reference_size = self.section_data.get("SECT_AFTER", {}).get("SECT_I", {}).get("vSIZE", None)
        slab = self.section_data.get("SECT_AFTER", {}).get("SLAB", None)
        
        dimensions_sub = {
            "reference_size": reference_size,
            "slab": slab,
        }
        
        # Material properties
        matl_elast = self.section_data.get("SECT_BEFORE", {}).get("MATL_ELAST", None)
        matl_dens = self.section_data.get("SECT_BEFORE", {}).get("MATL_DENS", None)
        matl_pois_s = self.section_data.get("SECT_BEFORE", {}).get("MATL_POIS_S", None)
        matl_pois_c = self.section_data.get("SECT_BEFORE", {}).get("MATL_POIS_C", None)
        matl_thermal = self.section_data.get("SECT_BEFORE", {}).get("MATL_THERMAL", None)
        
        joint = self.section_data.get("SECT_BEFORE", {}).get("JOINT", None)
        
        options = {
            "joint": joint,
            "matl_elast": matl_elast,
            "matl_dens": matl_dens,
            "matl_pois_s": matl_pois_s,
            "matl_pois_c": matl_pois_c,
            "matl_thermal": matl_thermal,
        }
        
        #단면별로 데이터가 제대로 들어와 있는지 확인
        shape_type = self.section_data.get("SECT_BEFORE", {}).get("SHAPE","")
        
        required_fields_by_shape = {
            "B": [vSize, matl_elast, matl_dens, matl_pois_s, matl_pois_c, matl_thermal, slab],
            "I": [vSize, matl_elast, matl_dens, matl_pois_s, matl_pois_c, matl_thermal, slab],
            "Tub": [vSize, matl_elast, matl_dens, matl_pois_s, matl_pois_c, matl_thermal, slab],
            "GB": [vSize, matl_elast, matl_dens, matl_pois_s, matl_pois_c, matl_thermal, reference_size, slab],
            "GI": [vSize, matl_elast, matl_dens, matl_pois_s, matl_pois_c, matl_thermal, reference_size, slab],
            "GT": [vSize, matl_elast, matl_dens, matl_pois_s, matl_pois_c, matl_thermal, reference_size, slab],
            "CI": [vSize_PSC_A, vSize_PSC_B, vSize_PSC_C, vSize_PSC_D, matl_elast, matl_dens, matl_pois_s, matl_pois_c, matl_thermal, joint, slab],
            "CT": [vSize_PSC_A, vSize_PSC_B, vSize_PSC_C, vSize_PSC_D, matl_elast, matl_dens, matl_pois_s, matl_pois_c, matl_thermal, joint, slab],
            "PC": [outer_polygon, inner_polygon],
        }
        
        if shape_type in required_fields_by_shape:
            message = self._check_missing_inputs(shape_type, required_fields_by_shape[shape_type])
            if not message == None:
                self.vertices_i = message
                return self.vertices_i, self.reference_points_i, self.properties_control_i, self.ref_dimension_i
        
        self.vertices_i, self.reference_points_i, self.properties_control_i, self.ref_dimension_i = self._generate_shape_vertices(dimensions, dimensions_sub, options)
        
        return self.vertices_i, self.reference_points_i, self.properties_control_i, self.ref_dimension_i
    
    def _check_missing_inputs(self, shape_type, required_params):
        if any(param is None for param in required_params):
            return {"error": f"Missing required dimensions or joint information for {shape_type} section"}
        return None
        
    # 자식 클래스에서 구현해야 할 추상 메서드들
    def _generate_shape_vertices(self, dimensions, dimensions_sub, options):
        """단면 정점 생성"""
        raise NotImplementedError