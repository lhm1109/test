from projects.concrete_fatigue_analysis_ntc2018.section.base.psc_base import PSCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class Cell3Section(PSCBaseSection):
    """PSC: 3 Cell Section"""
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # Variable Initialization
        HI10, HI20, HI30, HI40, HI50, HI60, HI70, HI80, HI90, HI100 = dimensions["vSize_PSC_A"]
        BI10, BI20, BI30, BI40, BI50, BI60, BI70, HO10, HO20, BO10, BO20, BO30 = dimensions["vSize_PSC_B"]
        HO21, HO22, HI21, HI22, HI42, HI41, HI61, HI62, HI63, HI91, HI92, HI81, HI82 = dimensions["vSize_PSC_C"]
        BO21, BO22, BI11, BI12, BI41, BI42, BI31, BI32, BI33, BI71, BI72, BI61, BI62 = dimensions["vSize_PSC_D"]
        JI1, JI2, JI3, JI4, JI5, JI6, JI7, JI8, JI9, JI10, JI11, JO1, JO2 = options["joint"]
        
        # Height Calculation
        heightO = HO10 + HO20
        heightI = HI10 + HI20 + HI30 + HI40 + HI50
        heightM = max(heightO, heightI)
        
        # Outer Cell_Left Side
        ycol = [0]
        zcol = [heightI - heightM]
        ycol.append(-(BO10 + BO20) + BO30)
        zcol.append(heightO - heightM)
        ycol.append(ycol[1] - BO30)
        zcol.append(zcol[1] - HO10)
        ycol.append(ycol[2] + BO20)
        zcol.append(zcol[2] - HO20)
        ycol.append(ycol[3] + BO10)
        zcol.append(zcol[3])
        
        # Added Vertex
        addedVertex = 0
        
        # Outer joint 1
        if JO1:
            ycol.insert(3, ycol[3] - BO21)
            zcol.insert(3, zcol[3] + HO21)
            addedVertex += 1
        
        # Outer joint 2
        if JO2:
            ycol.insert(3 + addedVertex, ycol[3 + addedVertex] - BO22)
            zcol.insert(3 + addedVertex, zcol[3 + addedVertex] + HO22)
            addedVertex += 1
        
        # Left Inner Cell_Left Side
        ycill = [-(BI10 + BI20 + BI30), -(BI40 + BI50 + BI60 + BI70), -(BI40 + BI50 + BI60)]
        zcill = [(HI60 + HI70 + HI80) - heightM, (HI90 + HI100) - heightM, HI100 - heightM]
        
        # Added Vertex
        addedVertex = 0
        
        # Inner joint 8
        if JI8:
            ycill.insert(2, ycill[2] - BI71)
            zcill.insert(2, zcill[2] + HI91)
            addedVertex += 1
        
        # Inner joint 9
        if JI9:
            ycill.insert(2 + addedVertex, ycill[2 + addedVertex] - BI72)
            zcill.insert(2 + addedVertex, zcill[2 + addedVertex] + HI92)
            addedVertex += 1
        
        # Left Inner Cell_Right Side
        ycilr = [-(BI10 + BI20 + BI30), -(BI10 + BI20), -(BI40 + BI50), -(BI40 + BI50 + BI60)]
        zcilr = [(HI60 + HI70 + HI80) - heightM, (HI70 + HI80) - heightM, HI80 - heightM, HI100 - heightM]
        
        # Added Vertex
        addedVertex = 0
        
        # Inner joint 7
        if JI7:
            ycilr.insert(1, ycilr[1] - BI33)
            zcilr.insert(1, zcilr[1] + HI63)
            addedVertex += 1
        
        # Inner joint 6
        if JI6:
            ycilr.insert(1 + addedVertex, ycilr[1 + addedVertex] - BI32)
            zcilr.insert(1 + addedVertex, zcilr[1 + addedVertex] + HI62)
            addedVertex += 1
        
        # Inner joint 5
        if JI5:
            ycilr.insert(1 + addedVertex, ycilr[1 + addedVertex] - BI31)
            zcilr.insert(1 + addedVertex, zcilr[1 + addedVertex] + HI61)
            addedVertex += 1
        
        # Added Vertex
        addedVertex2 = 0
        
        # Inner joint 11
        if JI11:
            ycilr.insert(3 + addedVertex, ycilr[2 + addedVertex] - BI62)
            zcilr.insert(3 + addedVertex, zcilr[2 + addedVertex] - HI82)
            addedVertex2 += 1
        
        # Inner joint 10
        if JI10:
            ycilr.insert(3 + addedVertex + addedVertex2, ycilr[2 + addedVertex] - BI61)
            zcilr.insert(3 + addedVertex + addedVertex2, zcilr[2 + addedVertex] - HI81)
            addedVertex2 += 1
        
        # Middle Inner Cell_Left Side
        yciml = [0, -BI10, -BI40, 0]
        zciml = [(HI20 + HI30 + HI40 + HI50) - heightM, (HI30 + HI40 + HI50) - heightM, (HI40 + HI50) - heightM, HI50 - heightM]
        
        # Added Vertex
        addedVertex = 0
        
        # Inner joint 1
        if JI1:
            yciml.insert(1, yciml[0] - BI11)
            zciml.insert(1, zciml[0] - HI21)
            addedVertex += 1
        
        # Inner joint 2
        if JI2:
            yciml.insert(1 + addedVertex, yciml[0] - BI12)
            zciml.insert(1 + addedVertex, zciml[0] - HI22)
            addedVertex += 1
        
        # Added Vertex
        addedVertex2 = 0
        
        # Inner joint 3
        if JI3:
            yciml.insert(3 + addedVertex, yciml[3 + addedVertex] - BI41)
            zciml.insert(3 + addedVertex, zciml[3 + addedVertex] + HI41)
            addedVertex2 += 1
        
        # Inner joint 4
        if JI4:
            yciml.insert(3 + addedVertex + addedVertex2, yciml[3 + addedVertex + addedVertex2] - BI42)
            zciml.insert(3 + addedVertex + addedVertex2, zciml[3 + addedVertex + addedVertex2] + HI42)
            addedVertex2 += 1
        
        # Outer Cell_Right Side
        ycor = [-x for x in ycol]
        zcor = zcol.copy()
        
        # Right Inner Cell_Left Side
        ycirl = [-x for x in ycilr]
        zcirl = zcilr.copy()
        
        # Right Inner Cell_Right Side
        ycirr = [-x for x in ycill]
        zcirr = zcill.copy()
        
        # Middle Inner Cell_Right Side
        ycimr = [-x for x in yciml]
        zcimr = zciml.copy()
        
        # Reverse
        ycor.reverse()
        zcor.reverse()
        ycill.reverse()
        zcill.reverse()
        ycirl.reverse()
        zcirl.reverse()
        yciml.reverse()
        zciml.reverse()
        
        # Remove Origin
        ycor.pop(0)
        zcor.pop(0)
        ycill.pop(0)
        zcill.pop(0)
        ycirl.pop(0)
        zcirl.pop(0)
        yciml.pop(0)
        zciml.pop(0)
        
        # All Cell
        ycoAll = ycol + ycor
        zcoAll = zcol + zcor
        ycilAll = ycilr + ycill
        zcilAll = zcilr + zcill
        ycirAll = ycirr + ycirl
        zcirAll = zcirr + zcirl
        ycimAll = ycimr + yciml
        zcimAll = zcimr + zciml

        # 원점 좌표로 이동
        yo = TransFormGeometry.calculate_origin_coordinates(ycoAll)
        zo = TransFormGeometry.calculate_origin_coordinates(zcoAll)
        ycoAll = [y - yo for y in ycoAll]
        zcoAll = [z - zo for z in zcoAll]
        ycilAll = [y - yo for y in ycilAll]
        zcilAll = [z - zo for z in zcilAll]
        ycirAll = [y - yo for y in ycirAll]
        zcirAll = [z - zo for z in zcirAll]
        ycimAll = [y - yo for y in ycimAll]
        zcimAll = [z - zo for z in zcimAll]
        
        # 기준 좌표 추출
        point_1 = [ycoAll[1], zcoAll[1]]
        point_2 = [ycoAll[-2], zcoAll[-2]]
        
        joint_count = JO1 + JO2
        if joint_count == 0:
            point_3 = [ycoAll[5], zcoAll[5]]
            point_4 = [ycoAll[3], zcoAll[3]]
                    
        elif joint_count == 1:
            point_3 = [ycoAll[6], zcoAll[6]]
            point_4 = [ycoAll[4], zcoAll[4]]
        
        elif joint_count == 2:
            point_3 = [ycoAll[7], zcoAll[7]]
            point_4 = [ycoAll[5], zcoAll[5]]
            
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
                        "name": "psc_3cell",
                        "elast": 1.0
                    }
                }
            ],
            "inner": [
                {
                    "y": ycilAll,
                    "z": zcilAll,
                    "reference": {
                        "name": "psc_3cell",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycimAll,
                    "z": zcimAll,
                    "reference": {
                        "name": "psc_3cell",
                        "elast": 1.0
                    }
                },
                {
                    "y": ycirAll,
                    "z": zcirAll,
                    "reference": {
                        "name": "psc_3cell",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points= {
            "psc_3cell": {
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
            "name": ["psc_3cell"],
            "control": "psc_3cell"
        }
        
        return vertices, reference_points, properties_control
    