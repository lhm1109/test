from projects.concrete_fatigue_analysis_ntc2018.section.base.dbuservalue_base import DBUserValueBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.chamfer import apply_chamfer

class ROctagonSection(DBUserValueBaseSection):
    """DBUSER: R-Octagon Section"""
    
    def _get_section_shape(self):
        """Not Available"""
        return None
    
    def _get_dimensions_from_db_data(self, data_base):
        """Not Available"""
        return  None
    
    def _get_dimensions_from_vsize(self, vSize):
        if len(vSize) < 7:
            return None
        elif len(vSize) > 7:
            vSize = vSize[:7]
        
        return {
            "H": vSize[0],
            "B": vSize[1],
            "a": vSize[2],
            "b": vSize[3],
            "t1": vSize[4],
            "t2": vSize[5],
            "t3": vSize[6],
        }
    
    def _generate_shape_vertices(self, dimensions, options={}):
        
        # 치수 추출
        H = dimensions["H"]
        B = dimensions["B"]
        a = dimensions["a"]
        b = dimensions["b"]
        t1 = dimensions["t1"]
        t2 = dimensions["t2"]
        t3 = dimensions["t3"]
        
        # 좌표 추출
        outer_coords = ShapeGenerator.generate_solid_rectangle_shape(H, B)
        yco = outer_coords["y"]
        zco = outer_coords["z"]
        
        cell_shape = options["cell_shape"]
        
        if cell_shape == 0:
            return {"error": "cell_shape is not found"}
        else:
            y1 = -B/2 + t1
            y2 = B/2 - t1
            z1 = -t2
            z2 = -H + t2
            
            inner_coords = self._generate_inner_cells(y1, y2, z1, z2, t3, cell_shape, a, b)

        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(yco)
        zo = TransFormGeometry.calculate_origin_coordinates(zco)

        yco = [y - yo for y in yco]
        zco = [z - zo for z in zco]
        
        transformed_inner_coords = []
        for cell in inner_coords:
            reverse_cell = TransFormGeometry.reverse_coordinates_list(cell)
            yci = [y - yo for y in reverse_cell["y"]]
            zci = [z - zo for z in reverse_cell["z"]]
            transformed_inner_coords.append({"y": yci, "z": zci})
        
        for cell in transformed_inner_coords:
            cell["reference"] = {
                "name": "r_octagon",
                "elast": 1.0
            }
        
        # 기준 좌표 추출
        point_1 = [yco[0], zco[0]]
        point_2 = [yco[3], zco[3]]
        point_3 = [yco[2], zco[2]]
        point_4 = [yco[1], zco[1]]
        
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
                        "name": "r_octagon",
                        "elast": 1.0
                    }
                }
            ],
            "inner": transformed_inner_coords
        }
        
        # 특정 좌표 저장
        reference_points = {
            "r_octagon": {
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
            "name": ["r_octagon"],
            "control": "r_octagon"
        }
        
        return vertices, reference_points, properties_control
    
    @staticmethod
    def _generate_inner_cells(y1, y2, z1, z2, t3, cell_shape, a, b):
        def make_cell(y_start, y_end):
            return {
                "y": [y_start, y_start, y_end, y_end, y_start],
                "z": [z1, z2, z2, z1, z1]
            }

        def chamfer_cell(cell):
            return apply_chamfer(cell, [[a, b], [b, a], [a, b], [b, a]])

        if cell_shape == 1:
            inner = make_cell(y1, y2)
            return [chamfer_cell(inner)]

        # For cell_shape > 1
        segment_width = (abs(y2 - y1) - (cell_shape - 1) * t3) / cell_shape
        transformed_cells = []

        for i in range(cell_shape):
            y_start = y1 + segment_width * i + t3 * i
            y_end = y1 + segment_width * (i+1) + t3 * i

            inner = make_cell(y_start, y_end)
            transformed_cells.append(chamfer_cell(inner))

        return transformed_cells
    