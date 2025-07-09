from projects.concrete_fatigue_analysis_ntc2018.section.base.psc_base import PSCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.chamfer import apply_chamfer

import math

class NCellSection(PSCBaseSection):
    """PSC: N Cell Section"""
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # Variable Initialization
        H1, H2, H3, H4, H5 = dimensions["vSize_PSC_A"]
        B1, B2, B3, B4, B5, B6, B7, B8 = dimensions["vSize_PSC_B"]
        sub_shape = options["psc_opt1"]
        num_cell = int(options["psc_opt2"])
        
        if sub_shape == "VERTICAL" or (sub_shape == "SLOPE" and math.isclose(B7, 0, abs_tol=1e-9)):
            # Outer Coordinates
            ycol = [
                -B1/2, -B1/2, -B1/2 + B2, -B1/2 + B2
            ]
            zcol = [
                0, -H3, -H2, -H1
            ]
            
            left_coord = {
                "y": ycol,
                "z": zcol
            }
            
            right_coord = TransFormGeometry.mirror_coordinates(left_coord, "z")
            right_coord = TransFormGeometry.reverse_coordinates_list(right_coord)
            merged_coord = TransFormGeometry.merge_coordinates(left_coord, right_coord)
            
            closed_coord = TransFormGeometry.close_polygon(merged_coord)
            
            # Inner Coordinates
            cell_width = (B1 - 2*B2 - 2*B6 - B3*(num_cell-1))/num_cell
            
            if cell_width <= 0:
                return {
                    "error": "Cell width is larger than 0",
                    "error_code": "PSCBASESECTION_NCELLSECTION"
                }, {}, {}
            if cell_width < 2*B4 or cell_width < 2*B5:
                return {
                    "error": "Cell width is larger than 2*B4 or 2*B5",
                    "error_code": "PSCBASESECTION_NCELLSECTION"
                }, {}, {}
            
            y1 = -B1/2 + B2 + B6
            y2 = B1/2 - B2 - B6
            z1 = -H5
            z2 = -H1 + H4
            
            cells = self._generate_inner_cells(y1, y2, z1, z2, B3, num_cell, B4, B5)
            
        elif sub_shape == "SLOPE" and not math.isclose(B7, 0, abs_tol=1e-9):
            # Outer Coordinates
            ycol = [
                -B1/2, -B1/2, -B1/2 + B2, -B1/2 + B2 + B7
            ]
            zcol = [
                0, -H3, -H2, -H1
            ]
            
            left_coord = {
                "y": ycol,
                "z": zcol
            }
            
            right_coord = TransFormGeometry.mirror_coordinates(left_coord, "z")
            right_coord = TransFormGeometry.reverse_coordinates_list(right_coord)
            merged_coord = TransFormGeometry.merge_coordinates(left_coord, right_coord)
            
            closed_coord = TransFormGeometry.close_polygon(merged_coord)
            
            # Inner Coordinates
            yz1 = (-B1/2 + B2, -H2)
            yz2 = (-B1/2 + B2 + B7, -H1)
            
            th = math.atan(abs(H1-H2)/ abs(B7))
            
            m = (yz2[1] - yz1[1]) / (yz2[0] - yz1[0])
            b = yz1[1] - m * yz1[0]
            d = B6 / math.sin(th)

            z1 = -H5
            z2 = -H1 + H4
            y1 = (z1 - (b - m*d)) / m
            y2 = (z2 - (b - m*d)) / m

            cell_width = (abs(y1)*2 - B3*(num_cell-1))/num_cell
            
            if cell_width <= 0:
                return {
                    "error": "Cell width is larger than 0",
                    "error_code": "PSCBASESECTION_NCELLSECTION"
                }, {}, {}
            if cell_width < 2*B4 or cell_width < 2*B5:
                return {
                    "error": "Cell width is larger than 2*B4 or 2*B5",
                    "error_code": "PSCBASESECTION_NCELLSECTION"
                }, {}, {}

            base_cells = self._generate_inner_cells(y1, -y1, z1, z2, B3, num_cell, B4, B5, chamfer=False)
            
            base_cells[0]["y"][1] = y2
            base_cells[-1]["y"][2] = -y2
            
            cells = []
            for i in range(num_cell):
                num_cell = apply_chamfer(base_cells[i], [[B4, B4], [B5, B5], [B5, B5], [B4, B4]])
                num_cell["reference"] = {
                    "name": "psc_ncell",
                    "elast": 1.0
                }
                cells.append(num_cell)
        
        elif sub_shape == "CHAMFER":
            # Outer Coordinates
            ycol = [
                -B1/2, -B1/2, -B1/2 + B2, -B1/2 + B2, -B1/2 + B2 + B7
            ]
            zcol = [
                0, -H3, -H2, -H1 + B7, -H1
            ]
            
            left_coord = {
                "y": ycol,
                "z": zcol
            }
            
            right_coord = TransFormGeometry.mirror_coordinates(left_coord, "z")
            right_coord = TransFormGeometry.reverse_coordinates_list(right_coord)
            merged_coord = TransFormGeometry.merge_coordinates(left_coord, right_coord)
            
            closed_coord = TransFormGeometry.close_polygon(merged_coord)
            
            y1 = -B1/2 + B2 + B6
            y2 = -B1/2 + B2 + B7 + (B8 - B5)
            z1 = -H5
            z2 = -H1 + H4
            
            base_cells = self._generate_inner_cells(y1, -y1, z1, z2, B3, num_cell, B4, B5, chamfer=False)
            
            base_cells[0]["y"][1] = y2
            base_cells[-1]["y"][2] = -y2
            
            cells = []
            for i in range(num_cell):
                num_cell = apply_chamfer(base_cells[i], [[B4, B4], [B5, B5], [B5, B5], [B4, B4]])
                num_cell["reference"] = {
                    "name": "psc_ncell",
                    "elast": 1.0
                }
                cells.append(num_cell)
        
        else:
            return {
                "error": "sub_shape is not found",
                "error_code": "PSCBASESECTION_NCELLSECTION"
            }, {}, {}
        
        yco = closed_coord["y"]
        zco = closed_coord["z"]
        
        inner_cells = []
        for cell in cells:
            reversed_cell = TransFormGeometry.reverse_coordinates_list(cell)
            reversed_cell["reference"] = {
                "name": "psc_ncell",
                "elast": 1.0
            }
            inner_cells.append(reversed_cell)
        
        # 원점 좌표 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(yco)
        zo = TransFormGeometry.calculate_origin_coordinates(zco)
        
        yco = [y - yo for y in yco]
        zco = [z - zo for z in zco]
        
        for cell in inner_cells:
            cell["y"] = [y - yo for y in cell["y"]]
            cell["z"] = [z - zo for z in cell["z"]]
        
        # 기준 좌표 추출
        point_1 = [yco[0], zco[0]]
        point_2 = [yco[-2], zco[-2]]
        
        if sub_shape == "VERTICAL" or sub_shape == "SLOPE":
            point_3 = [yco[4], zco[4]]
            point_4 = [yco[3], zco[3]]
        
        elif sub_shape == "CHAMFER":
            point_3 = [yco[5], zco[5]]
            point_4 = [yco[4], zco[4]]
        
        yt = max(yco)
        yb = min(yco)
        zt = max(zco)
        zb = min(zco)
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": yco,
                    "z": zco,
                    "reference": {
                        "name": "psc_ncell",
                        "elast": 1.0
                    }
                }
            ],
            "inner": inner_cells
        }
        
        # 특정 좌표 저장
        reference_points = {
            "psc_ncell": {
                "point_1": point_1,
                "point_2": point_2,
                "point_3": point_3,
                "point_4": point_4
            },
            "total": {
                "point_1": point_1,
                "point_2": point_2,
                "point_3": point_3,
                "point_4": point_4
            },
            "extreme_fiber": {
                "yt": yt,
                "yb": yb,
                "zt": zt,
                "zb": zb
            }
        }
        
        # 특성 컨트롤 데이터
        properties_control = {
            "name": ["psc_ncell"],
            "control": "psc_ncell"
        }
        
        return vertices, reference_points, properties_control

    @staticmethod
    def _generate_inner_cells(y1, y2, z1, z2, t, num_cell, a, b, chamfer=True):
        def make_cell(y_start, y_end):
            return {
                "y": [y_start, y_start, y_end, y_end, y_start],
                "z": [z1, z2, z2, z1, z1]
            }

        def chamfer_cell(cell):
            return apply_chamfer(cell, [[a, a], [b, b], [b, b], [a, a]])

        if num_cell == 1:
            inner = make_cell(y1, y2)
            return [chamfer_cell(inner)]

        # For cell_shape > 1
        segment_width = (abs(y2 - y1) - (num_cell - 1) * t) / num_cell
        transformed_cells = []

        for i in range(num_cell):
            y_start = y1 + segment_width * i + t * i
            y_end = y1 + segment_width * (i+1) + t * i

            inner = make_cell(y_start, y_end)
            if chamfer:
                inner = chamfer_cell(inner)
            transformed_cells.append(inner)
            transformed_cells[i]["reference"] = {
                "name": "psc_ncell",
                "elast": 1.0
            }

        return transformed_cells
