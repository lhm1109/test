from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.base_calculator import BaseCalculator
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class MomentProperties:
    Qyy: float = 0.0
    area: float = 0.0
    centroid: Tuple[float, float] = (0.0, 0.0)

class CompositeProperties(BaseCalculator):
    def calculate_properties(self, vertices: Dict, reference_points: Dict, properties: Dict, properties_control: Dict) -> None:
        # 초기화
        self._initialize_properties(properties, properties_control)
        
        # 면적과 도심 계산
        self._calculate_areas_and_centroids(vertices, properties, properties_control)
        
        # 관성 모멘트 계산
        cy, cz = properties["total"]["centroid"]
        self._calculate_moments_of_inertia(vertices, cy, cz, properties["total"], properties_control)
        
        # 참조점 계산
        self._calculate_reference_points(reference_points, properties["total"])
        
        # 1차 단면 모멘트 계산
        self._calculate_first_moments(vertices, properties, properties_control)

    def _initialize_properties(self, properties: Dict, properties_control: Dict) -> None:
        """속성 초기화"""
        properties["total"] = {
            "area": {"total": 0.0},
            "centroid": (0.0, 0.0),
            "first_moment_of_area": {"total": {
                "positive_side": MomentProperties().__dict__,
                "negative_side": MomentProperties().__dict__
            }},
            "second_moment_of_area": {"total": {"Iyy": 0.0, "Izz": 0.0}},
            "product_moment_of_area": {"total": {"Iyz": 0.0}},
            "reference_points": {"total":{
                "point_1": (0.0, 0.0),
                "point_2": (0.0, 0.0),
                "point_3": (0.0, 0.0),
                "point_4": (0.0, 0.0)
            }}
        }
        
        for name in properties_control["name"]:
            properties["total"]["area"][name] = 0.0
            properties["total"]["second_moment_of_area"][name] = {"Iyy": 0.0, "Izz": 0.0}
            properties["total"]["product_moment_of_area"][name] = {"Iyz": 0.0}
            properties["total"]["first_moment_of_area"][name] = {
                "positive_side": MomentProperties().__dict__,
                "negative_side": MomentProperties().__dict__
            }
            properties["total"]["reference_points"][name] = {
                f"point_{i}": (0.0, 0.0) for i in range(1, 5)
            }

    def _calculate_areas_and_centroids(self, vertices: Dict, properties: Dict, properties_control: Dict) -> None:
        """면적과 도심 계산"""
        for name in properties_control["name"]:
            for vertex_type in ["outer", "inner"]:
                if vertex_type not in vertices:
                    continue
                    
                for vertex in vertices[vertex_type]:
                    if vertex["reference"]["name"] == name:
                        elast = vertex["reference"]["elast"]
                        area = BaseCalculator.calculate_area(vertex, elast)
                        centroid = BaseCalculator.calculate_centroid(vertex, elast)
                        self._update_properties(properties["total"], area, centroid, name)

    def _calculate_moments_of_inertia(self, vertices: Dict, cy: float, cz: float, properties: Dict, properties_control: Dict) -> None:
        """관성 모멘트 계산"""
        for vertex_type in ["outer", "inner"]:
            if vertex_type not in vertices:
                continue
                
            for vertex in vertices[vertex_type]:
                elast = vertex["reference"]["elast"]
                self._add_moment_of_inertia(
                    vertex, cy, cz,
                    properties["second_moment_of_area"]["total"],
                    properties["product_moment_of_area"]["total"],
                    elast
                )
        
        for name in properties_control["name"]:
            for vertex_type in ["outer", "inner"]:
                if vertex_type not in vertices:
                    continue
                
                for vertex in vertices[vertex_type]:
                    if vertex["reference"]["name"] == name:
                        elast = vertex["reference"]["elast"]
                        self._add_moment_of_inertia(
                            vertex, cy, cz,
                            properties["second_moment_of_area"][name],
                            properties["product_moment_of_area"][name],
                            elast
                        )

    def _calculate_reference_points(self, reference_points: Dict, properties: Dict) -> None:
        """참조점 계산"""
        comp_cy, comp_cz = properties["centroid"]
        for ref_name, points in reference_points.items():
            if ref_name != "extreme_fiber":
                for i in range(1, 5):
                    point = points[f"point_{i}"]
                    properties["reference_points"][ref_name][f"point_{i}"] = (
                        point[0] - comp_cy,
                        point[1] - comp_cz
                    )

    def _calculate_first_moments(self, vertices: Dict, properties: Dict, properties_control: Dict) -> None:
        """1차 단면 모멘트 계산"""
        total_positive = MomentProperties()
        total_negative = MomentProperties()
        
        for name in properties_control["name"]:
            outer_vertices = [v for v in vertices["outer"] if v["reference"]["name"] == name]
            inner_vertices = [v for v in vertices.get("inner", []) if v["reference"]["name"] == name]
            
            _, cz = properties["total"]["centroid"]
            cutting_result = TransFormGeometry.cut_polygons(
                outer_vertices, inner_vertices, cut_axis='z', cut_value=cz
            )
            
            self._process_cutting_result(
                cutting_result,
                properties["total"]["first_moment_of_area"][name],
                next(v["reference"]["elast"] for v in outer_vertices)
            )
            
            self._update_total_moments(
                properties["total"]["first_moment_of_area"][name],
                total_positive,
                total_negative
            )
            
            # 각 name에 대한 Qyy 계산
            self._calculate_qyy_for_name(properties["total"]["first_moment_of_area"][name], properties["total"]["centroid"])
        
        self._finalize_total_moments(properties["total"], total_positive, total_negative)

    def _update_total_moments(self, moment: Dict, total_positive: MomentProperties, total_negative: MomentProperties) -> None:
        """전체 모멘트 업데이트"""
        for side, total in [("positive_side", total_positive), ("negative_side", total_negative)]:
            moment_data = moment[side]
            total.area += moment_data["area"]
            total.centroid = (
                total.centroid[0] + moment_data["centroid"][0] * moment_data["area"],
                total.centroid[1] + moment_data["centroid"][1] * moment_data["area"]
            )

    def _finalize_total_moments(self, properties: Dict, total_positive: MomentProperties, total_negative: MomentProperties) -> None:
        """전체 모멘트 최종 계산"""
        for side, total in [("positive_side", total_positive), ("negative_side", total_negative)]:
            if total.area > 0:
                total.centroid = (
                    total.centroid[0] / total.area,
                    total.centroid[1] / total.area
                )
            
            properties["first_moment_of_area"]["total"][side].update({
                "area": total.area,
                "centroid": total.centroid,
                "Qyy": total.area * abs(total.centroid[1] - properties["centroid"][1])
            })

    def _calculate_qyy_for_name(self, properties: Dict, total_centroid: Tuple[float, float]) -> None:
        """각 name에 대한 Qyy 계산"""
        for side in ["positive_side", "negative_side"]:
            moment = properties[side]
            if moment["area"] > 0:
                moment["Qyy"] = moment["area"] * abs(moment["centroid"][1] - total_centroid[1])

    def _process_cutting_result(self, cutting_result, properties, elast):
        """절단 결과 처리"""
        for side in ["positive", "negative"]:
            for part in ["outer", "inner"]:
                if cutting_result[side][part]:
                    for vertices in cutting_result[side][part]:
                        area = BaseCalculator.calculate_area(vertices, elast)
                        centroid = BaseCalculator.calculate_centroid(vertices, elast)
                        
                        if side == "positive":
                            self._update_first_positive_properties(properties, area, centroid)
                        else:
                            self._update_first_negative_properties(properties, area, centroid)
    
    def _update_first_positive_properties(self, properties, area, centroid):
        """첫 번째 양수 무게중심 업데이트"""
        moment = properties["positive_side"]
        moment["area"] += area
        self._update_first_moment_centroid(moment, area, centroid)
    
    def _update_first_negative_properties(self, properties, area, centroid):
        """첫 번째 음수 무게중심 업데이트"""
        moment = properties["negative_side"]
        moment["area"] += area
        self._update_first_moment_centroid(moment, area, centroid)
    
    def _calculate_qyy(self, properties, centroid):
        """Qyy 계산"""
        for side in ["positive_side", "negative_side"]:
            moment = properties[side]
            moment["Qyy"] = moment["area"] * abs(moment["centroid"][1] - centroid[1])
    
    def _update_first_moment_centroid(self, properties, area, centroid):
        """첫 번째 모멘트 무게중심 업데이트"""
        total_area = properties["area"]
        prev_centroid = properties["centroid"]
        prev_area = total_area - area
        
        if total_area > 0:
            new_cx = (prev_centroid[0] * prev_area + centroid[0] * area) / total_area
            new_cy = (prev_centroid[1] * prev_area + centroid[1] * area) / total_area
            properties["centroid"] = (new_cx, new_cy)
    
    def _add_moment_of_inertia(self, vertices, cy, cz, second_moment_of_area, product_moment_of_area, elast):
        """관성 모멘트 추가"""
        inertia = BaseCalculator.calculate_moment_of_inertia(vertices, cy, cz, elast)
        second_moment_of_area["Iyy"] += inertia["Iyy"]
        second_moment_of_area["Izz"] += inertia["Izz"]
        product_moment_of_area["Iyz"] += inertia["Iyz"]
    
    def _update_properties(self, properties, area, centroid, name):
        """속성 업데이트"""
        properties["area"]["total"] += area
        properties["area"][name] += area
        
        self._update_centroid(properties, area, centroid)
        
    def _update_centroid(self, properties, new_area, new_centroid):
        """무게중심 업데이트"""
        total_area = properties["area"]["total"]
        prev_centroid = properties["centroid"]
        prev_area = total_area - new_area
        
        if total_area > 0:
            new_cx = (prev_centroid[0] * prev_area + new_centroid[0] * new_area) / total_area
            new_cy = (prev_centroid[1] * prev_area + new_centroid[1] * new_area) / total_area
            properties["centroid"] = (new_cx, new_cy)