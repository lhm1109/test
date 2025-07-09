from projects.concrete_fatigue_analysis_ntc2018.section.base.psc_base import PSCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.shape_generator import ShapeGenerator
from projects.concrete_fatigue_analysis_ntc2018.utils.calculators.unit_converter import get_unit_conversion_factor
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class Cell1Section(PSCBaseSection):
    """PSC: 1 Cell Section"""
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # Variable Initialization
        HO10, HO20, HO21, HO22, HO30, HO31 = dimensions["vSize_PSC_A"]
        BO10, BO11, BO12, BO20, BO21, BO30 = dimensions["vSize_PSC_B"]
        HI10, HI20, HI21, HI22, HI30, HI31, HI40, HI41, HI42, HI50 = dimensions["vSize_PSC_C"]
        BI10, BI11, BI12, BI21, BI30, BI31, BI32, _ = dimensions["vSize_PSC_D"]
        JO1, JO2, JO3, JI1, JI2, JI3, JI4, JI5 = options["joint"]
        
        # Height Calculation
        heightO = HO10 + HO20 + HO30
        heightI = HI10 + HI20 + HI30 + HI40 + HI50
        heightM = max(heightO, heightI)
        
        # Outer Cell_Left Side
        ycol = [0]
        zcol = [heightI - heightM]
        ycol.append(-(BO10 + BO20 + BO30))
        zcol.append(heightO - heightM)
        ycol.append(ycol[1])
        zcol.append(zcol[1] - HO10)
        ycol.append(ycol[2] + BO10)
        zcol.append(zcol[2] - HO20)
        ycol.append(ycol[3] + BO20)
        zcol.append(zcol[3] - HO30)
        ycol.append(ycol[4] + BO30)
        zcol.append(zcol[4])
        
        # Added Vertex
        addedVertex = 0
        
        # Outer joint 1
        if JO1:
            ycol.insert(3, ycol[2] + BO11)
            zcol.insert(3, zcol[2] - HO21)
            addedVertex += 1
        
        # Outer joint 2
        if JO2:
            ycol.insert(3 + addedVertex, ycol[2] + BO12)
            zcol.insert(3 + addedVertex, zcol[2] - HO22)
            addedVertex += 1
        
        # Outer joint 3
        if JO3:
            ycol.insert(4 + addedVertex, ycol[4 + addedVertex] - BO21)
            zcol.insert(4 + addedVertex, zcol[4 + addedVertex] + HO31)
            addedVertex += 1
        
        # Inner Cell
        ycil = [ycol[0], ycol[0] - BI10, ycol[-1] - BI30, ycol[-1]]
        zcil = [zcol[0] - HI10, zcol[0] - HI10 - HI20,  zcol[0] - HI10 - HI20 - HI30, zcol[0] - HI10 - HI20 - HI30 - HI40]
        
        # Added Vertex
        addedVertex = 0
        
        # Inner joint 1
        if JI1:
            ycil.insert(1, ycil[0] - BI11)
            zcil.insert(1, zcil[0] - HI21)
            addedVertex += 1
        
        # Inner joint 2
        if JI2:
            ycil.insert(1 + addedVertex, ycil[0] - BI12)
            zcil.insert(1 + addedVertex, zcil[0] - HI22)
            addedVertex += 1
        
        # Inner joint 3
        if JI3:
            ycil.insert(2 + addedVertex, ycil[3 + addedVertex] - BI21)
            zcil.insert(2 + addedVertex, zcil[1 + addedVertex] - HI31)
            addedVertex += 1
        
        # Inner joint 4
        if JI4:
            ycil.insert(3 + addedVertex, ycil[-1] - BI32)
            zcil.insert(3 + addedVertex, zcil[-1] + HI42)
            addedVertex += 1
        
        # Inner joint 5
        if JI5:
            ycil.insert(3 + addedVertex, ycil[-1] - BI31)
            zcil.insert(3 + addedVertex, zcil[-1] + HI41)
            addedVertex += 1
        
        # Outer Cell_Right Side
        ycor = [-x for x in ycol]
        zcor = zcol.copy()
        
        # Inner Cell_Right Side
        ycir = [-x for x in ycil]
        zcir = zcil.copy()
        
        # Reverse
        ycor.reverse()
        zcor.reverse()
        ycil.reverse()
        zcil.reverse()
        
        # Remove Origin
        ycor.pop(0)
        zcor.pop(0)
        ycil.pop(0)
        zcil.pop(0)
        
        # All Cell
        ycoAll = ycol + ycor
        zcoAll = zcol + zcor
        yciAll = ycir + ycil
        zciAll = zcir + zcil

        # 원점 좌표로 이동
        yo = TransFormGeometry.calculate_origin_coordinates(ycoAll)
        zo = TransFormGeometry.calculate_origin_coordinates(zcoAll)
        ycoAll = [y - yo for y in ycoAll]
        zcoAll = [z - zo for z in zcoAll]
        yciAll = [y - yo for y in yciAll]
        zciAll = [z - zo for z in zciAll]
        
        # 기준 좌표 추출
        point_1 = [ycoAll[1], zcoAll[1]]
        point_2 = [ycoAll[-2], zcoAll[-2]]
        
        joint_count = JO1 + JO2 + JO3
        if joint_count == 0:
            point_3 = [ycoAll[6], zcoAll[6]]
            point_4 = [ycoAll[4], zcoAll[4]]
                    
        elif joint_count == 1:
            point_3 = [ycoAll[7], zcoAll[7]]
            point_4 = [ycoAll[5], zcoAll[5]]
        
        elif joint_count == 2:
            point_3 = [ycoAll[8], zcoAll[8]]
            point_4 = [ycoAll[6], zcoAll[6]]
        
        elif joint_count == 3:
            point_3 = [ycoAll[9], zcoAll[9]]
            point_4 = [ycoAll[7], zcoAll[7]]
            
        yt = max(ycoAll)
        yb = min(ycoAll)
        zt = max(zcoAll)
        zb = min(zcoAll)

        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": ycoAll,
                    "z": zcoAll,
                    "reference": {
                        "name": "psc_1cell",
                        "elast": 1.0
                    }
                }
            ],
            "inner": [
                {
                    "y": yciAll,
                    "z": zciAll,
                    "reference": {
                        "name": "psc_1cell",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "psc_1cell": {
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
            "name": ["psc_1cell"],
            "control": "psc_1cell"
        }
        
        return vertices, reference_points, properties_control
    
