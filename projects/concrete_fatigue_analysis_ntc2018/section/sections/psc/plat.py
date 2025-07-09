from projects.concrete_fatigue_analysis_ntc2018.section.base.psc_base import PSCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

import math

class PlatSection(PSCBaseSection):
    """PSC: Plat Section"""
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # Variable Initialization
        H10, H20, HOL10, HOL20, HOL30, BOL10, BOL20, BOL30, HOL11, BOL11 = dimensions["vSize_PSC_A"]
        HIL10, HIL20, BIL10, BIL20, BIL30, BIL40 = dimensions["vSize_PSC_B"]
        HOR10, HOR20, HOR30, BOR10, BOR20, BOR30, HOR11, BOR11 = dimensions["vSize_PSC_C"]
        HIR10, HIR20, BIR10, BIR20, BIR30 = dimensions["vSize_PSC_D"]
        JL1, JR1 = options["joint"]
        opt1, opt2 = options["psc_opt1"], options["psc_opt2"]
        
        # Height Calculation
        heightC = 0
        heightL = HOL10 + HOL20 + HOL30
        heightR = HOR10 + HOR20 + HOR30
        
        if heightR > heightL :
            heightC = BOL10 * (heightR - heightL) / (BOL10 + BOR10) + heightL
        
        elif heightR < heightL :
            heightC = BOR10 * (heightL - heightR) / (BOL10 + BOR10) + heightR
        
        elif heightR == heightL :
            heightC = (heightL + heightR) / 2
        
        heightM = max(heightL, heightR, heightC)
        
        # Outer Cell
        if opt1 == "HALF" and opt2 == "LEFT" :
            ycol = [0]
            zcol = [0]
            ycol.append(ycol[0] - BOL10)
            zcol.append(zcol[0])
            ycol.append(-BOL30 + BOL20)
            zcol.append(-HOL10)
            ycol.append(-BOL30)
            zcol.append(zcol[2] - HOL20)
            ycol.append(ycol[3])
            zcol.append(zcol[3] - HOL30)
            ycol.append(0)
            zcol.append(zcol[4])
            
            if JL1 :
                ycol.insert(2, ycol[1] + BOL11)
                zcol.insert(2, zcol[1] - HOL11)
        
        elif opt1 == "HALF" and opt2 == "RIGHT" :
            ycor = [0]
            zcor = [0]
            ycor.append(ycor[0] + BOR10)
            zcor.append(zcor[0])
            ycor.append(BOR30 - BOR20)
            zcor.append(-HOR10)
            ycor.append(BOR30)
            zcor.append(zcor[2] - HOR20)
            ycor.append(ycor[3])
            zcor.append(zcor[3] - HOR30)
            ycor.append(0)
            zcor.append(zcor[4])
        
            if JR1 :
                ycor.insert(2, ycor[1] - BOR11)
                zcor.insert(2, zcor[1] - HOR11)
        
        elif opt1 == "1CELL" or opt1 == "2CELL" :
            ycol = [0]
            zcol = [heightC - heightM]
            ycol.append(ycol[0] - BOL10)
            zcol.append(heightL - heightM)
            ycol.append(-BOL30 + BOL20)
            zcol.append(zcol[1] - HOL10)
            ycol.append(-BOL30)
            zcol.append(zcol[2] - HOL20)
            ycol.append(ycol[3])
            zcol.append(zcol[3] - HOL30)
            ycol.append(0)
            zcol.append(zcol[4])
        
            if JL1 :
                ycol.insert(2, ycol[1] + BOL11)
                zcol.insert(2, zcol[1] - HOL11)
        
            ycor = [0]
            zcor = [heightC - heightM]
            ycor.append(ycor[0] + BOR10)
            zcor.append(heightR - heightM)
            ycor.append(BOR30 - BOR20)
            zcor.append(zcor[1] - HOR10)
            ycor.append(BOR30)
            zcor.append(zcor[2] - HOR20)
            ycor.append(ycor[3])
            zcor.append(zcor[3] - HOR30)
            ycor.append(0)
            zcor.append(zcor[4])
        
            if JR1 :
                ycor.insert(2, ycor[1] - BOR11)
                zcor.insert(2, zcor[1] - HOR11)
        
        # Inner Cell
        radius = 0
        ycr = 0
        zcr = 0
        ycil = []
        zcil = []
        ycir = []
        zcir = []
        ycill = []
        zcill  = []
        ycilr  = []
        zcilr = []
        ycirl = []
        zcirl = []
        ycirr = []
        zcirr = []
        
        if opt1 == "HALF" and opt2 == "LEFT" :
            radius = H10 / 2
            ycr = 0
            zcr = -(HOL10 + HOL20 + HOL30) + (H20 + H10 / 2)
            
            for i in range(73) :
                ycil.append(ycr + radius * math.sin(2 * math.pi - math.pi * i / 72))
                zcil.append(zcr + radius * math.cos(2 * math.pi - math.pi * i / 72))
        
        elif opt1 == "HALF" and opt2 == "RIGHT" :
            radius = H10 / 2
            ycr = 0
            zcr = -(HOR10 + HOR20 + HOR30) + (H20 + H10 / 2)
            
            for i in range(73) :
                ycir.append(ycr + radius * math.sin(math.pi * i / 72))
                zcir.append(zcr + radius * math.cos(math.pi * i / 72))
        
        elif opt1 == "1CELL" and opt2 == "CIRCLE" :
            radius = H10 / 2
            ycr = 0
            zcr = -heightM + (H20 + H10 / 2)
            
            for i in range(72) :
                ycil.append(ycr + radius * math.sin(2 * math.pi - math.pi * i / 72))
                zcil.append(zcr + radius * math.cos(2 * math.pi - math.pi * i / 72))
                ycir.append(ycr + radius * math.sin(math.pi * i / 72))
                zcir.append(zcr + radius * math.cos(math.pi * i / 72))
        
        elif opt1 == "1CELL" and opt2 == "POLYGON" :
            ycil.append(0)
            zcil.append(-heightM + (H10 + H20))
            ycil.append(ycil[0] - BIL10)
            zcil.append(zcil[0])
            ycil.append(ycil[1] - BIL20)
            zcil.append(zcil[1] - HIL10)
            ycil.append(ycil[0] - BIL30)
            zcil.append(-heightM + H20 + HIL20)
            ycil.append(0)
            zcil.append(-heightM + H20)
            ycir.append(0)
            zcir.append(-heightM + (H10 + H20))
            ycir.append(ycir[0] + BIR10)
            zcir.append(zcir[0])
            ycir.append(ycir[1] + BIR20)
            zcir.append(zcir[1] - HIR10)
            ycir.append(ycir[0] + BIR30)
            zcir.append(-heightM + H20 + HIR20)
            ycir.append(0)
            zcir.append(-heightM + H20)
        
        elif opt1 == "2CELL" :
            radius = H10 / 2
            ycr = -(BIL40 + H10 / 2)
            zcr = -heightM + (H20 + H10 / 2)
            
            for i in range(72) :
                ycill.append(ycr + radius * math.sin(2 * math.pi - math.pi * i / 72))
                zcill.append(zcr + radius * math.cos(2 * math.pi - math.pi * i / 72))
                ycilr.append(ycr + radius * math.sin(math.pi * i / 72))
                zcilr.append(zcr + radius * math.cos(math.pi * i / 72))
            
            ycr = BIL40 + H10 / 2
            for i in range(72) :
                ycirl.append(ycr + radius * math.sin(2 * math.pi - math.pi * i / 72))
                zcirl.append(zcr + radius * math.cos(2 * math.pi - math.pi * i / 72))
                ycirr.append(ycr + radius * math.sin(math.pi * i / 72))
                zcirr.append(zcr + radius * math.cos(math.pi * i / 72))
        
        # All Cell
        if opt1 == "HALF" and opt2 == "LEFT" :
            ycil.reverse()
            zcil.reverse()
            ycoAll = ycol + ycil + [ycol[0]]
            zcoAll = zcol + zcil + [zcol[0]]
            
            # 원점 좌표로 이동 (Center of Section)
            y_origin = max(ycoAll) - (max(ycoAll) - min(ycoAll)) / 2
            z_origin = max(zcoAll) - (max(zcoAll) - min(zcoAll)) / 2
            ycoAll = [y - y_origin for y in ycoAll]
            zcoAll = [z - z_origin for z in zcoAll]
            
            # 기준 좌표 추출
            point_1 = [ycoAll[1], zcoAll[1]]
            point_2 = [ycoAll[-1], zcoAll[-1]]
            
            if JL1 :
                point_3 = [ycoAll[6], zcoAll[6]]
                point_4 = [ycoAll[5], zcoAll[5]]
            else:
                point_3 = [ycoAll[5], zcoAll[5]]
                point_4 = [ycoAll[4], zcoAll[4]]
            
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
                            "name": "psc_plat",
                            "elast": 1.0
                        }
                    }
                ]
            }

        elif opt1 == "HALF" and opt2 == "RIGHT" :
            ycor.reverse()
            zcor.reverse()
            ycoAll = ycor + ycir + [ycor[0]]
            zcoAll = zcor + zcir + [zcor[0]]
            
            # 원점 좌표로 이동 (Center of Section)
            y_origin = max(ycoAll) - (max(ycoAll) - min(ycoAll)) / 2
            z_origin = max(zcoAll) - (max(zcoAll) - min(zcoAll)) / 2
            ycoAll = [y - y_origin for y in ycoAll]
            zcoAll = [z - z_origin for z in zcoAll]
            
            # 기준 좌표 추출
            point_3 = [ycoAll[1], zcoAll[1]]
            point_4 = [ycoAll[-1], zcoAll[-1]]
            
            if JR1 :
                point_1 = [ycoAll[6], zcoAll[6]]
                point_2 = [ycoAll[5], zcoAll[5]]
            else:
                point_1 = [ycoAll[5], zcoAll[5]]
                point_2 = [ycoAll[4], zcoAll[4]]
            
            yt = max(ycoAll)
            yb = min(ycoAll)
            zt = max(zcoAll)
            zb = min(zcoAll)
            
            # Return
            vertices = {
                "outer": [
                    {
                        "y": ycoAll,
                        "z": zcoAll,
                        "reference": {
                            "name": "psc_plat",
                            "elast": 1.0
                        }
                    }
                ]
            }
            
        elif opt1 == "1CELL" :
            ycor.reverse()
            zcor.reverse()
            ycil.reverse()
            zcil.reverse()
            ycor.pop(0)
            zcor.pop(0)
            ycil.pop(0)
            zcil.pop(0)
            ycoAll = ycol + ycor
            zcoAll = zcol + zcor
            ycilAll = ycir + ycil
            zcilAll = zcir + zcil
            
            # 원점 좌표로 이동 (Center of Section)
            y_origin = max(ycoAll) - (max(ycoAll) - min(ycoAll)) / 2
            z_origin = max(zcoAll) - (max(zcoAll) - min(zcoAll)) / 2
            ycoAll = [y - y_origin for y in ycoAll]
            zcoAll = [z - z_origin for z in zcoAll]
            ycilAll = [y - y_origin for y in ycilAll]
            zcilAll = [z - z_origin for z in zcilAll]
            
            # 기준 좌표 추출
            point_1 = [ycoAll[1], zcoAll[1]]
            point_2 = [ycoAll[-2], zcoAll[-2]]
            
            if JL1 :
                point_3 = [ycoAll[7], zcoAll[7]]
                point_4 = [ycoAll[5], zcoAll[5]]
            else:
                point_3 = [ycoAll[6], zcoAll[6]]
                point_4 = [ycoAll[4], zcoAll[4]]
            
            yt = max(ycoAll)
            yb = min(ycoAll)
            zt = max(zcoAll)
            zb = min(zcoAll)
            
            # Return
            vertices = {
                "outer": [
                    {
                        "y": ycoAll,
                        "z": zcoAll,
                        "reference": {
                            "name": "psc_plat",
                            "elast": 1.0
                        }
                    }
                ],
                "inner": [
                    {
                        "y": ycilAll,
                        "z": zcilAll,
                        "reference": {
                            "name": "psc_plat",
                            "elast": 1.0
                        }
                    }
                ]
            }
            
        elif opt1 == "2CELL" :
            ycor.reverse()
            zcor.reverse()
            ycill.reverse()
            zcill.reverse()
            ycirl.reverse()
            zcirl.reverse()
            ycor.pop(0)
            zcor.pop(0)
            ycill.pop(0)
            zcill.pop(0)
            ycirl.pop(0)
            zcirl.pop(0)
            ycoAll = ycol + ycor
            zcoAll = zcol + zcor
            ycilAll = ycilr + ycill
            zcilAll = zcilr + zcill
            ycirAll = ycirr + ycirl
            zcirAll = zcirr + zcirl

            # 원점 좌표로 이동 (Center of Section)
            yo = TransFormGeometry.calculate_origin_coordinates(ycoAll)
            zo = TransFormGeometry.calculate_origin_coordinates(zcoAll)
            ycoAll = [y - yo for y in ycoAll]
            zcoAll = [z - zo for z in zcoAll]
            ycilAll = [y - yo for y in ycilAll]
            zcilAll = [z - zo for z in zcilAll]
            ycirAll = [y - yo for y in ycirAll]
            zcirAll = [z - zo for z in zcirAll]
            
            # 기준 좌표 추출
            point_1 = [ycoAll[1], zcoAll[1]]
            point_2 = [ycoAll[-2], zcoAll[-2]]
            
            if JL1 :
                point_3 = [ycoAll[7], zcoAll[7]]
                point_4 = [ycoAll[5], zcoAll[5]]
            else:
                point_3 = [ycoAll[6], zcoAll[6]]
                point_4 = [ycoAll[4], zcoAll[4]]
            
            yt = max(ycoAll)
            yb = min(ycoAll)
            zt = max(zcoAll)
            zb = min(zcoAll)
            
            # Return
            vertices = {
                "outer": [
                    {
                        "y": ycoAll,
                        "z": zcoAll,
                        "reference": {
                            "name": "psc_plat",
                            "elast": 1.0
                        }
                    }
                ],
                "inner": [
                    {
                        "y": ycilAll,
                        "z": zcilAll,
                        "reference": {
                            "name": "psc_plat",
                            "elast": 1.0
                        }
                    },
                    {
                        "y": ycirAll,
                        "z": zcirAll,
                        "reference": {
                            "name": "psc_plat",
                            "elast": 1.0
                        }
                    }
                ]
            }
        
        # 특정 좌표 저장
        reference_points = {
            "psc_plat": {
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
            "name": ["psc_plat"],
            "control": "psc_plat"
        }
        
        return vertices, reference_points, properties_control
