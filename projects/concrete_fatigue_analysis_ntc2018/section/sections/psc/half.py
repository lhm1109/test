from projects.concrete_fatigue_analysis_ntc2018.section.base.psc_base import PSCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

import math

class HalfSection(PSCBaseSection):
    """PSC: Half Section"""
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # Variable Initialization
        HO10, HO20, HO21, HO22, HO30, HO31 = dimensions["vSize_PSC_A"]
        BO10, BO11, BO12, BO20, BO21, BO30 = dimensions["vSize_PSC_B"]
        HI10, HI20, HI21, HI22, HI30, HI31, HI40, HI41, HI42, HI50 = dimensions["vSize_PSC_C"]
        BI10, BI11, BI12, BI21, BI30, BI31, BI32 = dimensions["vSize_PSC_D"]
        JO1, JO2, JO3, JI1, JI2, JI3, JI4, JI5 = options["joint"]
        opt1, opt2 = options["psc_opt1"], options["psc_opt2"]
        
        # Height Calculation
        xc_sign = 0
        
        if opt1 == "LEFT" :
            xc_sign = -1
        elif opt1 == "RIGHT" :
            xc_sign = 1
        
        heightO = HO10 + HO20 + HO30
        heightI = 0
        
        if opt2 == "POLYGON" :
            heightI = HI10 + HI20 + HI30 + HI40 + HI50
        elif opt2 == "CIRCLE" :
            heightI = HI10 + HI30 + HI50
        elif opt2 == "NONE" :
            heightI = HI10
        
        heightM = max(heightO, heightI) 
        
        # Outer Cell
        yco = [0]
        zco = [heightI - heightM]
        yco.append(xc_sign * (BO10 + BO20 + BO30))
        zco.append(heightO - heightM)
        yco.append(yco[1])
        zco.append(zco[1] - HO10)
        yco.append(yco[2] - xc_sign * BO10)
        zco.append(zco[2] - HO20)
        yco.append(yco[3] - xc_sign * BO20)
        zco.append(zco[3] - HO30)
        yco.append(yco[4] - xc_sign * BO30)
        zco.append(zco[4])
        
        # Added Vertex
        addedVertex = 0
        
        # Outer joint 1
        if JO1:
            yco.insert(3, yco[2] - xc_sign * BO11)
            zco.insert(3, zco[2] - HO21)
            addedVertex += 1
        
        # Outer joint 2
        if JO2:
            yco.insert(3 + addedVertex, yco[2] - xc_sign * BO12)
            zco.insert(3 + addedVertex, zco[2] - HO22)
            addedVertex += 1
        
        # Outer joint 3
        if JO3:
            yco.insert(4 + addedVertex, yco[4 + addedVertex] + xc_sign * BO21)
            zco.insert(4 + addedVertex, zco[4 + addedVertex] + HO31)
            addedVertex += 1
        
        # Inner Cell
        yci = []
        zci = []
        
        if opt2 == "POLYGON" :
            yci.append(yco[0])
            zci.append(zco[0] - HI10)
            yci.append(yci[0] + xc_sign * BI10)
            zci.append(zci[0] - HI20)
            yci.append(yco[-1] + xc_sign * BI30)
            zci.append(zci[1] - HI30)
            yci.append(yco[-1])
            zci.append(zci[2] - HI40)
            
            # Added Vertex
            addedVertex = 0
            
            # Inner joint 1
            if JI1:
                yci.insert(1, yci[0] + xc_sign * BI11)
                zci.insert(1, zci[0] - HI21)
                addedVertex += 1
            
            # Inner joint 2
            if JI2:
                yci.insert(1 + addedVertex, yci[0] + xc_sign * BI12)
                zci.insert(1 + addedVertex, zci[0] - HI22)
                addedVertex += 1
            
            # Inner joint 3
            if JI3:
                yci.insert(2 + addedVertex, yci[3 + addedVertex] + xc_sign * BI21)
                zci.insert(2 + addedVertex, zci[1 + addedVertex] - HI31)
                addedVertex += 1
            
            # Inner joint 4
            if JI4:
                yci.insert(3 + addedVertex, yci[-1] + xc_sign * BI32)
                zci.insert(3 + addedVertex, zci[-1] + HI42)
                addedVertex += 1
            
            # Inner joint 5
            if JI5:
                yci.insert(3 + addedVertex, yci[-1] + xc_sign * BI31)
                zci.insert(3 + addedVertex, zci[-1] + HI41)
                addedVertex += 1
        
        elif opt2 == "CIRCLE" :
            radius = HI30 / 2
            ycr = yco[-1]
            zcr = zco[-1] + HI50 + HI30 / 2
            
            if opt1 == "LEFT" :
                for i in range(73) :
                    yci.append(ycr + radius * math.sin(2 * math.pi - math.pi * i / 72))
                    zci.append(zcr + radius * math.cos(2 * math.pi - math.pi * i / 72))
            
            elif opt1 == "RIGHT" :
                for i in range(73) :
                    yci.append(ycr + radius * math.sin(math.pi * i / 72))
                    zci.append(zcr + radius * math.cos(math.pi * i / 72))
        
        elif opt2 == "NONE" :
            yci.append(yco[0])
            zci.append(zco[0])
            yci.append(yco[-1])
            zci.append(zco[-1])
        
        # Reverse and All Cell
        if (opt1 == "LEFT" and opt2 == "POLYGON") or (opt1 == "LEFT" and opt2 == "CIRCLE") :
            # Reverse
            yci.reverse()
            zci.reverse()
            
            # All Cell
            ycAll = yco + yci + [yco[0]]
            zcAll = zco + zci + [zco[0]]
        
        elif (opt1 == "RIGHT" and opt2 == "POLYGON") or (opt1 == "RIGHT" and opt2 == "CIRCLE"):
            # Reverse
            yco.reverse()
            zco.reverse()
            
            # All Cell
            ycAll = yco + yci + [yco[0]]
            zcAll = zco + zci + [zco[0]]
        
        elif opt1 == "LEFT" and opt2 == "NONE" :
            # All Cell
            ycAll = yco + [yco[0]]
            zcAll = zco + [zco[0]]
        
        elif opt1 == "RIGHT" and opt2 == "NONE" :
            # Reverse
            yco.reverse()
            zco.reverse()
            
            # All Cell
            ycAll = yco + [yco[0]]
            zcAll = zco + [zco[0]]

        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(ycAll)
        zo = TransFormGeometry.calculate_origin_coordinates(zcAll)
        ycAll = [y - yo for y in ycAll]
        zcAll = [z - zo for z in zcAll]

        # 기준 좌표 추출
        if opt1 == "LEFT":
            point_1 = [ycAll[1], zcAll[1]]
            point_2 = [ycAll[-1], zcAll[-1]]
            
            joint_count = JO1 + JO2 + JO3
            if joint_count == 0:
                point_3 = [ycAll[5], zcAll[5]]
                point_4 = [ycAll[4], zcAll[4]]
            elif joint_count == 1:
                point_3 = [ycAll[6], zcAll[6]]
                point_4 = [ycAll[5], zcAll[5]]
            elif joint_count == 2:
                point_3 = [ycAll[7], zcAll[7]]
                point_4 = [ycAll[6], zcAll[6]]
            elif joint_count == 3:
                point_3 = [ycAll[8], zcAll[8]]
                point_4 = [ycAll[7], zcAll[7]]

        elif opt1 == "RIGHT":
            point_3 = [ycAll[1], zcAll[1]]
            point_4 = [ycAll[-1], zcAll[-1]]
            
            joint_count = JO1 + JO2 + JO3
            if joint_count == 0:
                point_1 = [ycAll[5], zcAll[5]]
                point_2 = [ycAll[4], zcAll[4]]
            elif joint_count == 1:
                point_1 = [ycAll[6], zcAll[6]]
                point_2 = [ycAll[5], zcAll[5]]
            elif joint_count == 2:
                point_1 = [ycAll[7], zcAll[7]]
                point_2 = [ycAll[6], zcAll[6]]
            elif joint_count == 3:
                point_1 = [ycAll[8], zcAll[8]]
                point_2 = [ycAll[7], zcAll[7]]
        
        yt = max(ycAll)
        yb = min(ycAll)
        zt = max(zcAll)
        zb = min(zcAll)
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": ycAll,
                    "z": zcAll,
                    "reference": {
                        "name": "psc_half",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points = {
            "psc_half": {
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
            "name": ["psc_half"],
            "control": "psc_half"
        }
        
        return vertices, reference_points, properties_control
    