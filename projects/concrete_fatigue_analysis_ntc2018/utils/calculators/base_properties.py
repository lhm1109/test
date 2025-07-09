from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.base_calculator import BaseCalculator
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from typing import Dict, List, Tuple, Any

class CommonProperties:
    """공통 속성 계산기"""
    
    def calculate_properties(self, vertices: Dict, reference_points: Dict, properties_control: Dict) -> Dict:
        """단면 속성 계산"""
        if "error" in vertices or "outer" not in vertices:
            return {"error": "Invalid vertices"}
        
        results_by_ref_name = {}
        ref_names = properties_control["name"]
        
        # 결과 저장 딕셔너리 초기화
        for ref_name in ref_names:
            results_by_ref_name[ref_name] = self._initialize_results_dict()
        
        # 외부/내부 도형 처리
        self._process_vertices(vertices, results_by_ref_name, properties_control)
        
        # 관성 모멘트 계산
        self._calculate_moments_of_inertia(vertices, results_by_ref_name, properties_control)
        
        # 첫 번째 모멘트 계산
        self._calculate_first_moment_of_area(vertices, results_by_ref_name, properties_control)
        
        # 참조점 변환
        self._transform_reference_points(reference_points, results_by_ref_name)
        
        return results_by_ref_name

    def _initialize_results_dict(self) -> Dict:
        """결과 저장 딕셔너리 초기화"""
        return {
            "area": 0,
            "outer_perimeter": 0,
            "inner_perimeter": 0,
            "centroid": (0, 0),
            "first_moment_of_area": {
                "positive_side": {"area": 0, "centroid": (0, 0), "Qyy": 0},
                "negative_side": {"area": 0, "centroid": (0, 0), "Qyy": 0}
            },
            "second_moment_of_area": {"Iyy": 0, "Izz": 0},
            "product_moment_of_area": {"Iyz": 0}
        }

    def _process_vertices(self, vertices: Dict, results_by_ref_name: Dict, properties_control: Dict) -> None:
        """외부/내부 도형 처리"""
        # 외부 도형 처리
        for outer in vertices["outer"]:
            ref_name = outer["reference"]["name"]
            if ref_name in properties_control["name"]:
                self._process_single_vertices(outer, results_by_ref_name[ref_name], is_outer=True)
        
        # 내부 도형 처리
        if "inner" in vertices:
            for inner in vertices["inner"]:
                ref_name = inner["reference"]["name"]
                if ref_name in properties_control["name"]:
                    self._process_single_vertices(inner, results_by_ref_name[ref_name], is_outer=False)

    def _process_single_vertices(self, vertices: List, properties: Dict, is_outer: bool) -> None:
        """단일 도형 처리"""
        area = BaseCalculator.calculate_area(vertices)
        perimeter = BaseCalculator.calculate_perimeter(vertices)
        centroid = BaseCalculator.calculate_centroid(vertices)
        
        if is_outer:
            properties["area"] += area
            properties["outer_perimeter"] += perimeter
        else:
            properties["area"] += area
            properties["inner_perimeter"] += perimeter
        
        self._update_centroid(properties, area, centroid)

    def _calculate_first_moment_of_area(self, vertices: Dict, results_by_ref_name: Dict, properties_control: Dict) -> None:
        """첫 번째 모멘트 계산"""
        for name in properties_control["name"]:
            outer_vertices = [v for v in vertices["outer"] if v["reference"]["name"] == name]
            inner_vertices = [v for v in vertices.get("inner", []) if v["reference"]["name"] == name]
            
            _, cz = results_by_ref_name[name]["centroid"]
            cutting_result = TransFormGeometry.cut_polygons(outer_vertices, inner_vertices, cut_axis='z', cut_value=cz)
            
            self._process_cutting_result(cutting_result, results_by_ref_name[name])
            self._calculate_qyy(results_by_ref_name[name])

    def _process_cutting_result(self, cutting_result: Dict, properties: Dict) -> None:
        """절단 결과 처리"""
        for side in ["positive", "negative"]:
            for part in ["outer", "inner"]:
                if cutting_result[side][part]:
                    for vertices in cutting_result[side][part]:
                        area = BaseCalculator.calculate_area(vertices)
                        centroid = BaseCalculator.calculate_centroid(vertices)
                        
                        if side == "positive":
                            self._update_first_positive_properties(properties, area, centroid)
                        else:
                            self._update_first_negative_properties(properties, area, centroid)

    def _calculate_qyy(self, properties: Dict) -> None:
        """Qyy 계산"""
        for side in ["positive_side", "negative_side"]:
            moment = properties["first_moment_of_area"][side]
            moment["Qyy"] = moment["area"] * abs(moment["centroid"][1] - properties["centroid"][1])

    def _update_centroid(self, properties: Dict, new_area: float, new_centroid: Tuple[float, float]) -> None:
        """무게중심 업데이트"""
        total_area = properties["area"]
        prev_centroid = properties["centroid"]
        prev_area = total_area - new_area
        
        if total_area > 0:
            new_cx = (prev_centroid[0] * prev_area + new_centroid[0] * new_area) / total_area
            new_cy = (prev_centroid[1] * prev_area + new_centroid[1] * new_area) / total_area
            properties["centroid"] = (new_cx, new_cy)

    def _update_first_positive_properties(self, properties: Dict, area: float, centroid: Tuple[float, float]) -> None:
        """첫 번째 양수 무게중심 업데이트"""
        moment = properties["first_moment_of_area"]["positive_side"]
        moment["area"] += area
        self._update_first_moment_centroid(moment, area, centroid)

    def _update_first_negative_properties(self, properties: Dict, area: float, centroid: Tuple[float, float]) -> None:
        """첫 번째 음수 무게중심 업데이트"""
        moment = properties["first_moment_of_area"]["negative_side"]
        moment["area"] += area
        self._update_first_moment_centroid(moment, area, centroid)

    def _update_first_moment_centroid(self, properties: Dict, new_area: float, new_centroid: Tuple[float, float]) -> None:
        """첫 번째 모멘트 무게중심 업데이트"""
        total_area = properties["area"]
        prev_centroid = properties["centroid"]
        prev_area = total_area - new_area
        
        if total_area > 0:
            new_cx = (prev_centroid[0] * prev_area + new_centroid[0] * new_area) / total_area
            new_cy = (prev_centroid[1] * prev_area + new_centroid[1] * new_area) / total_area
            properties["centroid"] = (new_cx, new_cy)

    def _calculate_moments_of_inertia(self, vertices: Dict, results_by_ref_name: Dict, properties_control: Dict) -> None:
        """관성 모멘트 계산"""
        for ref_name, properties in results_by_ref_name.items():
            if ref_name in properties_control["name"]:
                cy, cz = properties["centroid"]
                
                for part in ["outer", "inner"]:
                    if part in vertices:
                        for vertex in vertices[part]:
                            if vertex["reference"]["name"] == ref_name:
                                self._add_moment_of_inertia(vertex, cy, cz, properties["second_moment_of_area"], properties["product_moment_of_area"])

    def _add_moment_of_inertia(self, vertices: List, cy: float, cz: float, second_moment: Dict, product_moment: Dict) -> None:
        """관성 모멘트 추가"""
        inertia = BaseCalculator.calculate_moment_of_inertia(vertices, cy, cz)
        second_moment["Iyy"] += inertia["Iyy"]
        second_moment["Izz"] += inertia["Izz"]
        product_moment["Iyz"] += inertia["Iyz"]

    def _transform_reference_points(self, reference_points: Dict, results_by_ref_name: Dict) -> None:
        """참조점 좌표 변환"""
        for ref_name, properties in results_by_ref_name.items():
            centroid = properties["centroid"]
            transformed_points = {}
            
            for i in range(1, 5):
                point = reference_points[ref_name][f"point_{i}"]
                if isinstance(point, (list, tuple)):
                    transformed_points[f"point_{i}"] = [
                        point[0] - centroid[0],
                        point[1] - centroid[1]
                    ]
                else:
                    # point가 단일 float 값인 경우
                    transformed_points[f"point_{i}"] = point - centroid[0]
            
            results_by_ref_name[ref_name]["reference_points"] = transformed_points
        