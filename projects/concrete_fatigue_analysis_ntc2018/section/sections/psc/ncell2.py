from projects.concrete_fatigue_analysis_ntc2018.section.base.psc_base import PSCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.chamfer import apply_chamfer
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.fillet import apply_fillet

import math

class NCell2Section(PSCBaseSection):
    """PSC: N Cell 2 Section"""
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # Variable Initialization
        HOL1, HOL2, HOL21, HOL3, HOL4, BOL1, BOL11, BOL2, BOL3, BOL4, BOL5 = dimensions["vSize_PSC_A"]
        HIL1, HIL2, HIL21, HIL3, HIL4, HIL5, HIL6, BIL1, BIL2, BIL21, BIL3, BIL4, BIL5, BIL6, BIL7, BIL8, RL1, RL2 = dimensions["vSize_PSC_B"]
        HOR1, HOR2, HOR21, HOR3, HOR4, BOR1, BOR11, BOR2, BOR3, BOR4, BOR5 = dimensions["vSize_PSC_C"]
        HIR1, HIR2, HIR21, HIR3, HIR4, HIR5, HIR6, BIR1, BIR2, BIR21, BIR3, BIR4, BIR5, BIR6, BIR7, BIR8, RR1, RR2 = dimensions["vSize_PSC_D"]
        sWidth = dimensions["swidth"]
        
        sub_shape = options["psc_opt1"]
        num_cell = int(options["psc_opt2"])
        JO, JI = options["joint"]
        small_hole = options["small_hole"]
        
        # Outer Coordinates
        ycol, zcol, fillet_info_left = self._generate_outer_coordinates(
            HOL1, HOL2, HOL21, HOL3, HOL4, BOL1, BOL11, BOL2, BOL3, BOL5, JO, sWidth, RL1, RL2,
            fillet=True
        )
        
        ycor, zcor, fillet_info_right = self._generate_outer_coordinates(
            HOR1, HOR2, HOR21, HOR3, HOR4, BOR1, BOR11, BOR2, BOR3, BOR5, JO, sWidth, RR1, RR2,
            fillet=True, reverse=True,  mirror_z=True
        )
        
        outer_y = ycol + ycor
        outer_z = zcol + zcor
        
        outer_y.append(outer_y[0])
        outer_z.append(outer_z[0])

        # Inner Cells
        inner_cells = []
        if sub_shape == "POLYGON":
            yicol, zicol = self._generate_inner_edge_cells(
                sWidth, BOL1, BOL2, BOL3, BOL4, HOL1, HOL2, HOL3, HOL4,
                HIL1, HIL2, HIL21, HIL3, HIL4, HIL5, HIL6, BIL1, BIL2, BIL21, BIL3, BIL4, BIL5, BIL6,
                JI, reverse=False, mirror_z=False
            )
            
            yicor, zicor = self._generate_inner_edge_cells(
                sWidth, BOR1, BOR2, BOR3, BOR4, HOR1, HOR2, HOR3, HOR4,
                HIR1, HIR2, HIR21, HIR3, HIR4, HIR5, HIR6, BIR1, BIR2, BIR21, BIR3, BIR4, BIR5, BIR6,
                JI, reverse=True, mirror_z=True
            )
            
            if num_cell == 1:
                y_left = yicol[:-5]
                z_left = zicol[:-5]
                
                y_right = [-y for y in y_left]
                z_right = [z for z in z_left]
                
                y_left.reverse()
                z_left.reverse()
                
                y_inner = y_left + y_right
                z_inner = z_left + z_right
                
                y_inner.append(y_inner[0])
                z_inner.append(z_inner[0])
                
                y_inner.reverse()
                z_inner.reverse()
                
                inner_cells.append(
                    {
                        "y": y_inner,
                        "z": z_inner
                    }
                )
                
            elif num_cell >= 2:
                
                inner_cells.append(
                    {
                        "y": yicol,
                        "z": zicol
                    }
                )
                inner_cells.append(
                    {
                        "y": yicor,
                        "z": zicor
                    }
                )
                
                if num_cell > 2:
                    y1 = -sWidth/2 + BOL1 + BOL2 + BOL3 + BOL4 + BIL6
                    y2 = sWidth/2 - BOL1 - BOL2 - BOL3 - BOL4 - BIL6
                    z1 = -HIL1
                    z2 = -HOL1 - HOL2 - HOL3 - HOL4 + HIL6

                    cells = self._generate_inner_cells(y1, y2, z1, z2, BIL6*2, num_cell-2)
                    
                    for cell in cells:
                        inner_cells.append(apply_chamfer(cell, [[BIL7, HIL3], [HIL4, BIL8], [BIL8, HIL4], [HIL3, BIL7]]))
            
        elif sub_shape == "CIRCLE":
            height = HOL1 + HOL2 + HOL3 + HOL4
            R = (height - HIL1 - HIL2) / 2
            
            if num_cell == 1:
                yc = 0
                zc = -HIL1 - R
                
                inner_circle = ShapeGenerator.generate_circle_shape(R, (yc, zc))
                
                inner_cells.append(
                    {
                        "y": inner_circle["y"],
                        "z": inner_circle["z"]
                    }
                )
            
            else:
                yc1 = -sWidth/2 + BOL1 + BOL2 + BOL3 + BOL4
                yc2 = sWidth/2 - BOL1 - BOL2 - BOL3 - BOL4
                
                zc = -HIL1 - R
                
                yc_step = (yc2 - yc1) / (num_cell - 1)
                
                for i in range(num_cell):
                    yc = yc1 + yc_step * i
                    zc = zc
                    
                    inner_circle = ShapeGenerator.generate_circle_shape(R, (yc, zc))
                    
                    inner_cells.append(
                        {
                            "y": inner_circle["y"],
                            "z": inner_circle["z"]
                        }
                    )
            
            if small_hole:
                yc1 = -sWidth/2 + BIL1
                zc1 = -HIL3
                r1 = BIL2/2
                
                yc2 = sWidth/2 - BIR1
                zc2 = -HIR3
                r2 = BIR2/2
                
                inner_circle_1 = ShapeGenerator.generate_circle_shape(r1, (yc1, zc1))
                inner_circle_2 = ShapeGenerator.generate_circle_shape(r2, (yc2, zc2))
                
                inner_cells.append(
                    {
                        "y": inner_circle_1["y"],
                        "z": inner_circle_1["z"]
                    }
                )
                inner_cells.append(
                    {
                        "y": inner_circle_2["y"],
                        "z": inner_circle_2["z"]
                    }
                )
                
        else:
            return {
                "error": "sub_shape is not found",
                "error_code": "PSCBASESECTION_NCELL2SECTION"
            }, {}, {}
        
        reversed_inner_cells = []
        for cell in inner_cells:
            reversed_cell = TransFormGeometry.reverse_coordinates_list(cell)
            reversed_cell["reference"] = {
                "name": "psc_ncell2",
                "elast": 1.0
            }
            reversed_inner_cells.append(reversed_cell)
        
        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(outer_y)
        zo = TransFormGeometry.calculate_origin_coordinates(outer_z)
        outer_y = [y - yo for y in outer_y]
        outer_z = [z - zo for z in outer_z]
        
        for cell in reversed_inner_cells:
            cell["y"] = [y - yo for y in cell["y"]]
            cell["z"] = [z - zo for z in cell["z"]]
        
        # 기준 좌표 추출
        if math.isclose(BOL5, 0, abs_tol=1e-9):
            point_1 = [outer_y[0], outer_z[0]]
        else:
            point_1 = [outer_y[1], outer_z[1]]
        
        if math.isclose(BOR5, 0, abs_tol=1e-9):
            point_2 = [outer_y[-2], outer_z[-2]]
        else:
            point_2 = [outer_y[-3], outer_z[-3]]
        
        point_4 = []
        if math.isclose(RL2, 0, abs_tol=1e-9):
            point_4.append(-((BOL5 + sWidth + BOR5)/2-(BOL5 + BOL1 + BOL2 + BOL3)))
            point_4.append(-(HOL1 + HOL2 + HOL3 + HOL4)/2)
        else:
            index_list = [item["index"] for item in fillet_info_left]            
            max_index = max(index_list)
            
            for value in fillet_info_left:
                if value["index"] == max_index:
                    radius_left = value["radius"]
                    angle1 = value["angle1"]
                    angle2 = value["angle2"]
                    angle = (angle1 + angle2) / 2
                    center_y = value["center"][0]
                    center_z = value["center"][1]
                    
                    point_4.append((center_y + radius_left * math.sin(math.radians(angle)))-yo)
                    point_4.append((center_z + radius_left * math.cos(math.radians(angle)))-zo)
                    break
        
        point_3 = []
        if math.isclose(RR2, 0, abs_tol=1e-9):
            point_3.append(((BOL5 + sWidth + BOR5)/2-(BOR5 + BOR1 + BOR2 + BOR3)))
            point_3.append(-(HOL1 + HOL2 + HOL3 + HOL4)/2)
        else:
            index_list = [item["index"] for item in fillet_info_right]            
            max_index = max(index_list)
            
            for value in fillet_info_right:
                if value["index"] == max_index:
                    radius_right = value["radius"]
                    angle1 = value["angle1"]
                    angle2 = value["angle2"]
                    angle = (angle1 + angle2) / 2
                    center_y = value["center"][0]
                    center_z = value["center"][1]
                    
                    point_3.append(-(center_y + radius_right * math.sin(math.radians(angle)))-yo)
                    point_3.append((center_z + radius_right * math.cos(math.radians(angle)))-zo)
                    break
        
        yt = max(outer_y)
        yb = min(outer_y)
        zt = max(outer_z)
        zb = min(outer_z)
        
        # 좌표 정리
        vertices = {
            "outer": [
                {
                    "y": outer_y,
                    "z": outer_z,
                    "reference": {
                        "name": "psc_ncell2",
                        "elast": 1.0
                    }
                }
            ],
            "inner": reversed_inner_cells
        }
        
        # 특정 좌표 저장
        reference_points = {
            "psc_ncell2": {
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
            "name": ["psc_ncell2"],
            "control": "psc_ncell2"
        }
        
        return vertices, reference_points, properties_control

    @staticmethod
    def _generate_outer_coordinates(
        HO1, HO2, HO21, HO3, HO4, BO1, BO11, BO2, BO3, BO5, JO, sWidth, R1, R2,
        fillet=False, reverse=False, mirror_z=False
        ):
        
        y = [0]
        z = [0]
        
        y.append(-sWidth/2)
        z.append(0)
        
        if not math.isclose(BO5, 0, abs_tol=1e-9):
            y.append(-sWidth/2 - BO5)
            z.append(0)
            y.append(y[-1])
            z.append(-HO1)
            
        y.append(-sWidth/2)
        z.append(-HO1)
        
        if JO:
            y.append(y[-1] + BO11)
            z.append(z[-1] - HO21)
        
        y.append(-sWidth/2 + BO1)
        z.append(-HO1 - HO2)
        y.append(y[-1] + BO2)
        z.append(z[-1] - HO3)
        y.append(y[-1] + BO3)
        z.append(z[-1] - HO4)
        
        y.append(0)
        z.append(-HO1-HO2-HO3-HO4)
        
        y.append(0)
        z.append(0)
        
        if fillet:
            coord = {"y": y, "z": z}
            
            # 기본 필렛 리스트 생성 (모두 None으로 초기화)
            fillet_list = [None] * (len(y) - 1)
            
            # BO5와 JO 조건에 따라 R1, R2 위치 결정
            if not math.isclose(BO5, 0, abs_tol=1e-9):
                if JO:
                    if not math.isclose(R1, 0, abs_tol=1e-9): fillet_list[7] = R1
                    if not math.isclose(R2, 0, abs_tol=1e-9): fillet_list[8] = R2
                else:
                    if not math.isclose(R1, 0, abs_tol=1e-9): fillet_list[6] = R1
                    if not math.isclose(R2, 0, abs_tol=1e-9): fillet_list[7] = R2
            else:
                if JO:
                    if not math.isclose(R1, 0, abs_tol=1e-9): fillet_list[5] = R1
                    if not math.isclose(R2, 0, abs_tol=1e-9): fillet_list[6] = R2
                else:
                    if not math.isclose(R1, 0, abs_tol=1e-9): fillet_list[4] = R1
                    if not math.isclose(R2, 0, abs_tol=1e-9): fillet_list[5] = R2
            
            results = apply_fillet(coord, fillet_list)
            
            y = results["y"]
            z = results["z"]
            fillet_info = results["fillet_info"]
        
        y = y[1:-2]
        z = z[1:-2]
                
        if reverse:
            y.reverse()
            z.reverse()
        
        if mirror_z:
            y = [-y for y in y]
        
        return y, z, fillet_info

    @staticmethod
    def _generate_inner_edge_cells(
        sWidth, BO1, BO2, BO3, BO4, HO1, HO2, HO3, HO4,
        HI1, HI2, HI21, HI3, HI4, HI5, HI6, BI1, BI2, BI21, BI3, BI4, BI5, BI6,
        JI, reverse=False, mirror_z=False
    ):
        # Web
        yz1 = (-sWidth/2 + BO1 + BO2, -HO1 - HO2 - HO3 )
        yz2 = (-sWidth/2 + BO1 + BO2 + BO3, -HO1 - HO2 - HO3 -HO4)

        th = math.atan(abs(HO4)/abs(BO3))
        
        m = (yz2[1] - yz1[1]) / (yz2[0] - yz1[0])
        b = yz1[1] - m * yz1[0]
        d = BI1 / math.sin(th)
        
        y = []
        z = []
        if JI:
            z1 = -HI1 - HI2 - HI21
            z2 = -HO1 - HO2 - HO3 - HO4 + HI6 + HI5
            y1 = (z1 - (b - m*d)) / m
            y2 = (z2 - (b - m*d)) / m
            
            y.append(y1 + BI21 + BI2)
            z.append(z1 + HI21 + HI2)
            y.append(y1 + BI21)
            z.append(z1 + HI21)
            y.append(y1)
            z.append(z1)
            y.append(y2)
            z.append(z2)
            y.append(y2 + BI5)
            z.append(z2 - HI5)
            
        else:
            z1 = -HI1 - HI2
            z2 = -HO1 - HO2 - HO3 - HO4 + HI6 + HI5
            y1 = (z1 - (b - m*d)) / m
            y2 = (z2 - (b - m*d)) / m
            
            y.append(y1 + BI2)
            z.append(z1 + HI2)
            y.append(y1)
            z.append(z1)
            y.append(y2)
            z.append(z2)
            y.append(y2 + BI5)
            z.append(z2 - HI5)
        
        y.append(-sWidth/2 + BO1 + BO2 + BO3 + BO4 - BI6 - BI4)
        z.append(z[-1])
        y.append(y[-1] + BI4)
        z.append(z[-1] + HI4)
        y.append(y[-1])
        z.append(-HI1 - HI3)
        y.append(y[-1] - BI3)
        z.append(z[-1] + HI3)
        y.append(y[0])
        z.append(z[0])
        
        if reverse:
            y.reverse()
            z.reverse()
        
        if mirror_z:
            y = [-y for y in y]
        
        return y, z
        
    @staticmethod
    def _generate_inner_cells(y1, y2, z1, z2, t, num_cell):
        def make_cell(y_start, y_end):
            return {
                "y": [y_start, y_start, y_end, y_end, y_start],
                "z": [z1, z2, z2, z1, z1]
            }

        if num_cell == 1:
            inner = make_cell(y1, y2)
            return [inner]

        # For cell_shape > 1
        segment_width = (abs(y2 - y1) - (num_cell - 1) * t) / num_cell
        transformed_cells = []

        for i in range(num_cell):
            y_start = y1 + segment_width * i + t * i
            y_end = y1 + segment_width * (i+1) + t * i

            inner = make_cell(y_start, y_end)
            transformed_cells.append(inner)
            transformed_cells[i]["material"] = {"ref_name": "main"}

        return transformed_cells
