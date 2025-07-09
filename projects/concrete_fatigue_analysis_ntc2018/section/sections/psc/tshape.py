from projects.concrete_fatigue_analysis_ntc2018.section.base.psc_base import PSCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class TShapeSection(PSCBaseSection):
    """PSC: T Section"""
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # Variable Initialization
        H10, HL10, HL20, HL30, BL10, BL20, BL30, BL40 = dimensions["vSize_PSC_A"]
        HL21, HL22, HL31, HL32, BL21, BL22, BL31, BL32 = dimensions["vSize_PSC_B"]
        HR10, HR20, HR30, BR10, BR20, BR30, BR40 = dimensions["vSize_PSC_C"]
        HR21, HR22, HR31, HR32, BR21, BR22, BR31, BR32 = dimensions["vSize_PSC_D"]
        J1, JL1, JL2, JL3, JL4, JR1, JR2, JR3, JR4 = options["joint"]
        
        # Height Calculation
        heightL = HL10 + HL20 + HL30
        heightR = HR10 + HR20 + HR30
        heightC = 0
        
        if J1 :
            heightC = H10
        
        else :
            if heightR > heightL :
                heightC = BL40 * (heightR - heightL) / (BL40 + BR40) + heightL
            elif heightR < heightL :
                heightC = BR40 * (heightL - heightR) / (BL40 + BR40) + heightR
            elif heightR == heightL :
                heightC = (heightL + heightR) / 2
        
        heightM = max(heightL, heightR, heightC)
        
        # Outer Cell_Left Side
        ycol = [0]
        zcol = [heightC - heightM]
        ycol.append(-BL40)
        zcol.append(heightL - heightM)
        ycol.append(-(BL10 + BL20 + BL30)) 
        zcol.append(zcol[1] - HL10)
        ycol.append(-(BL10 + BL20))
        zcol.append(zcol[2] - HL20)
        ycol.append(-BL10)
        zcol.append(zcol[3] - HL30)
        ycol.append(0)
        zcol.append(-heightM)
        
        # Added Vertex
        addedVertex = 0
        
        # Left joint 1
        if JL1:
            ycol.insert(3, ycol[2] + BL31)
            zcol.insert(3, zcol[2] - HL21)
            addedVertex += 1
        
        # Left joint 2
        if JL2:
            ycol.insert(3 + addedVertex, ycol[2] + BL32)
            zcol.insert(3 + addedVertex, zcol[2] - HL22)
            addedVertex += 1
        
        # Left joint 3
        if JL3:
            ycol.insert(4 + addedVertex, ycol[4 + addedVertex] - BL21)
            zcol.insert(4 + addedVertex, zcol[4 + addedVertex] + HL31)
            addedVertex += 1
        
        # Left joint 4
        if JL4:
            ycol.insert(4 + addedVertex, ycol[4 + addedVertex] - BL22)
            zcol.insert(4 + addedVertex, zcol[4 + addedVertex] + HL32)
            addedVertex += 1
        
        # Outer Cell_Right Side
        ycor = [0]
        zcor = [heightC - heightM]
        ycor.append(BR40)
        zcor.append(heightR - heightM)
        ycor.append(BR10 + BR20 + BR30)
        zcor.append(zcor[1] - HR10)
        ycor.append(BR10 + BR20)
        zcor.append(zcor[2] - HR20)
        ycor.append(BR10)
        zcor.append(zcor[3] - HR30)
        ycor.append(0)
        zcor.append(-heightM)
        
        # Added Vertex
        addedVertex = 0
        
        # Right joint 1
        if JR1:
            ycor.insert(3, ycor[2] - BR31)
            zcor.insert(3, zcor[2] - HR21)
            addedVertex += 1
        
        # Right joint 2
        if JR2:
            ycor.insert(3 + addedVertex, ycor[2] - BR32)
            zcor.insert(3 + addedVertex, zcor[2] - HR22)
            addedVertex += 1
        
        # Right joint 3
        if JR3:
            ycor.insert(4 + addedVertex, ycor[4 + addedVertex] + BR21)
            zcor.insert(4 + addedVertex, zcor[4 + addedVertex] + HR31)
            addedVertex += 1
        
        # Right joint 4
        if JR4:
            ycor.insert(4 + addedVertex, ycor[4 + addedVertex] + BR22)
            zcor.insert(4 + addedVertex, zcor[4 + addedVertex] + HR32)
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
        
        joint_count = JL1 + JL2 + JL3 + JL4
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
        elif joint_count == 4:
            point_3 = [ycoAll[10], zcoAll[10]]
            point_4 = [ycoAll[8], zcoAll[8]]

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
                        "name": "psc_t_shape",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장    
        reference_points = {
            "psc_t_shape": {
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
            "name": ["psc_t_shape"],
            "control": "psc_t_shape"
        }
        
        return vertices, reference_points, properties_control
