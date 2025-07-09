from projects.concrete_fatigue_analysis_ntc2018.section.base.psc_base import PSCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

import math

class MidSection(PSCBaseSection):
    """PSC: Mid Section"""
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # Variable Initialization
        H10, HL10, HL20, HL21, HL22, HL30, HL40, HL41, HL42, HL50 = dimensions["vSize_PSC_A"]
        BL10, BL20, BL21, BL22, BL41, BL42 = dimensions["vSize_PSC_B"]
        HR10, HR20, HR21, HR22, HR30, HR40, HR41, HR42, HR50 = dimensions["vSize_PSC_C"]
        BR10, BR20, BR21, BR22, BR41, BR42 = dimensions["vSize_PSC_D"]
        J1, JL1, JL2, JL3, JL4, JR1, JR2, JR3, JR4 = options["joint"]
        opt1, opt2 = options["psc_opt1"], options["psc_opt2"]
        
        # Height Calculation
        heightC = 0
        heightL = 0
        heightR = 0
        
        # Left Height
        if opt1 == "NONE" :
            heightL = HL10
        elif opt1 == "CIRCLE" :
            heightL = HL10 + HL30 + HL50
        elif opt1 == "POLYGON" :
            heightL = HL10 + HL20 + HL30 + HL40 + HL50
        
        # Right Height
        if opt2 == "NONE" :
            heightR = HR10
        elif opt2 == "CIRCLE" :
            heightR = HR10 + HR30 + HR50
        elif opt2 == "POLYGON" :
            heightR = HR10 + HR20 + HR30 + HR40 + HR50
        
        # Center Height
        if J1:
            heightC = H10
        else :
            if heightR > heightL :
                heightC = BL20 * (heightR - heightL) / (BL20 + BR20) + heightL
            elif heightR < heightL :
                heightC = BR20 * (heightL - heightR) / (BL20 + BR20) + heightR
            elif heightR == heightL :
                heightC = (heightL + heightR) / 2
        
        heightM = max(heightL, heightR, heightC)
        
        # Outer Cell_Left Side
        radius = 0
        ycr = 0
        zcr = 0
        addedVertex = 0
        ycol = [0]
        zcol = [heightC - heightM]
        
        if opt1 == "NONE" :
            ycol.append(ycol[0] - BL20)
            zcol.append(HL10 - heightM)
            ycol.append(ycol[1])
            zcol.append(zcol[1] - HL10)
            ycol.append(ycol[2] + BL20)
            zcol.append(zcol[2])
        
        elif opt1 == "CIRCLE" :
            radius = HL30 / 2
            ycr = -BL20
            zcr = (heightL - heightM) - (HL10 + HL30 / 2)
            ycol.append(ycol[0] - BL20)
            zcol.append(heightL - heightM)  
            ycol.append(ycol[1])
            zcol.append(zcol[1] - HL10)
        
            for i in range(73) :
                ycol.append(ycr + radius * math.sin(math.pi * i / 72))
                zcol.append(zcr + radius * math.cos(math.pi * i / 72))
        
            ycol.append(ycol[-1])
            zcol.append(zcol[-1] - HL50)
            ycol.append(ycol[-1] + BL20)
            zcol.append(zcol[-1])
        
        elif opt1 == "POLYGON" :
            ycol.append(ycol[0] - BL20)
            zcol.append(heightL - heightM)
            ycol.append(ycol[1])
            zcol.append(zcol[1] - HL10)
            ycol.append(ycol[0] - BL10)
            zcol.append(zcol[2] - HL20)
            ycol.append(ycol[3])
            zcol.append(zcol[3] - HL30)
            ycol.append(ycol[0] - BL20)
            zcol.append(zcol[4] - HL40)
            ycol.append(ycol[5])
            zcol.append(zcol[5] - HL50)
            ycol.append(0)
            zcol.append(zcol[6])
            
            # Added Vertex
            addedVertex = 0
            
            # Left joint 1
            if JL1:
                ycol.insert(3, ycol[2] + BL21)
                zcol.insert(3, zcol[2] - HL21)
                addedVertex += 1
            
            # Left joint 2
            if JL2:
                ycol.insert(3 + addedVertex, ycol[2] + BL22)
                zcol.insert(3 + addedVertex, zcol[2] - HL22)
                addedVertex += 1
            
            # Left joint 3
            if JL3:
                ycol.insert(5 + addedVertex, ycol[5 + addedVertex] + BL42)
                zcol.insert(5 + addedVertex, zcol[5 + addedVertex] + HL42)
                addedVertex += 1
            
            # Left joint 4
            if JL4:
                ycol.insert(5 + addedVertex, ycol[5 + addedVertex] + BL41)
                zcol.insert(5 + addedVertex, zcol[5 + addedVertex] + HL41)
                addedVertex += 1
        
        # Outer Cell_Right Side
        radius = 0
        ycr = 0
        zcr = 0
        addedVertex = 0
        ycor = [0]
        zcor = [heightC - heightM]
        
        if opt2 == "NONE" :
            ycor.append(ycor[0] + BR20)
            zcor.append(HR10 - heightM)
            ycor.append(ycor[1])
            zcor.append(zcor[1] - HR10)
            ycor.append(ycor[2] - BR20)
            zcor.append(zcor[2])
        
        elif opt2 == "CIRCLE" :
            radius = HR30 / 2
            ycr = BR20
            zcr = (heightR - heightM) - (HR10 + HR30 / 2)
            ycor.append(ycor[0] + BR20)
            zcor.append(heightR - heightM)
            ycor.append(ycor[1])
            zcor.append(zcor[1] - HR10)
            
            for i in range(73) :
                ycor.append(ycr + radius * math.sin(2 * math.pi - math.pi * i / 72))
                zcor.append(zcr + radius * math.cos(2 * math.pi - math.pi * i / 72))
            
            ycor.append(ycor[-1])
            zcor.append(zcor[-1] - HR50)
            ycor.append(ycor[-1] - BR20)
            zcor.append(zcor[-1])
        
        elif opt2 == "POLYGON" :
            ycor.append(ycor[0] + BR20)
            zcor.append(heightR - heightM)
            ycor.append(ycor[1])
            zcor.append(zcor[1] - HR10)
            ycor.append(ycor[0] + BR10)
            zcor.append(zcor[2] - HR20)
            ycor.append(ycor[3])
            zcor.append(zcor[3] - HR30)
            ycor.append(ycor[0] + BR20)
            zcor.append(zcor[4] - HR40)
            ycor.append(ycor[5])
            zcor.append(zcor[5] - HR50)
            ycor.append(0)
            zcor.append(zcor[6])
            
            # Added Vertex
            addedVertex = 0
            
            # Right joint 1
            if JR1:
                ycor.insert(3, ycor[2] - BR21)
                zcor.insert(3, zcor[2] - HR21)
                addedVertex += 1
            
            # Right joint 2
            if JR2:
                ycor.insert(3 + addedVertex, ycor[2] - BR22)
                zcor.insert(3 + addedVertex, zcor[2] - HR22)
                addedVertex += 1
            
            # Right joint 3
            if JR3:
                ycor.insert(5 + addedVertex, ycor[5 + addedVertex] - BR42)
                zcor.insert(5 + addedVertex, zcor[5 + addedVertex] + HR42)
                addedVertex += 1
            
            # Right joint 4
            if JR4:
                ycor.insert(5 + addedVertex, ycor[5 + addedVertex] - BR41)
                zcor.insert(5 + addedVertex, zcor[5 + addedVertex] + HR41)
                addedVertex += 1
        
        # Reverse
        ycor.reverse()
        zcor.reverse()
        
        # Remove Origin
        ycor.pop(0)
        zcor.pop(0)
        
        # All Cell
        ycoAll = ycol + ycor
        zcoAll = zcol + zcor

        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(ycoAll)
        zo = TransFormGeometry.calculate_origin_coordinates(zcoAll)
        ycoAll = [y - yo for y in ycoAll]
        zcoAll = [z - zo for z in zcoAll]
        
        # 기준 좌표 추출
        point_1 = [ycoAll[1], zcoAll[1]]
        point_2 = [ycoAll[-2], zcoAll[-2]]
        
        if opt1 == "NONE":
            point_3 = [ycoAll[4], zcoAll[4]]
            point_4 = [ycoAll[2], zcoAll[2]]
        
        elif opt1 == "CIRCLE":
            point_3 = [ycoAll[78], zcoAll[78]]
            point_4 = [ycoAll[76], zcoAll[76]]
        
        elif opt1 == "POLYGON":
            joint_count = JL1 + JL2 + JL3 + JL4
            if joint_count == 0:
                point_3 = [ycoAll[8], zcoAll[8]]
                point_4 = [ycoAll[6], zcoAll[6]]
            elif joint_count == 1:
                point_3 = [ycoAll[9], zcoAll[9]]
                point_4 = [ycoAll[7], zcoAll[7]]
            elif joint_count == 2:
                point_3 = [ycoAll[10], zcoAll[10]]
                point_4 = [ycoAll[8], zcoAll[8]]
            elif joint_count == 3:
                point_3 = [ycoAll[11], zcoAll[11]]
                point_4 = [ycoAll[9], zcoAll[9]]
            elif joint_count == 4:
                point_3 = [ycoAll[12], zcoAll[12]]
                point_4 = [ycoAll[10], zcoAll[10]]
        
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
                        "name": "psc_mid",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points = {
            "psc_mid": {
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
            "name": ["psc_mid"],
            "control": "psc_mid"
        }
        
        return vertices, reference_points, properties_control
