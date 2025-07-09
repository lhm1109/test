from projects.concrete_fatigue_analysis_ntc2018.section.base.psc_base import PSCBaseSection
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class CMPWebSection(PSCBaseSection):
    """PSC: CMP Web Section"""
    
    def _generate_shape_vertices(self, dimensions, options):
        
        # Variable Initialization
        a, b, h, t = dimensions["vSize"]
        HO1, HO2, HO3, HO4, HO5, HO6, HO61 = dimensions["vSize_PSC_A"]
        BO1, BO2, BO3, BO4, BO5, BO6, BO7, BO8, BO9, BO10, BO11 = dimensions["vSize_PSC_B"]
        HI1, HI2, HI3, HI4, HI5, HI6, HI7, HI8 = dimensions["vSize_PSC_C"]
        BI1, BI2, BI3, BI4, BI5, _, BOR1, BOR2, BOR11 = dimensions["vSize_PSC_D"]
        symmetric = options["symmetric"]
        haunch = options["small_hole"]
        
        # Outer_Top
        ytcol = [-(BO11 + BO1 + BO2 + BO6 + BO7)]
        ztcol = [0]
        ytcol.append(ytcol[-1])
        ztcol.append(-HO1)
        ytcol.append(ytcol[-1] + BO11)
        ztcol.append(ztcol[-1])
        ytcol.append(ytcol[-1] + BO1)
        ztcol.append(ztcol[-1] - HO2)
        ytcol.append(ytcol[-1] + BO2)
        ztcol.append(ztcol[-1] - HO3)
        
        if haunch:
            ytcol.append(ytcol[-1] + BO3 - BO4)
            ztcol.append(ztcol[-1] - HO4)
            ytcol.append(ytcol[-1] + BO4 + BO5)
            ztcol.append(-HI1 - HI2 - HI3 - HI4)
        
        ytcol.append(-BO7 - BO6 + BO3)
        ztcol.append(-HI1 - HI2 - HI3)
        ytcol.append(ytcol[-1] + BI1)
        ztcol.append(ztcol[-1] + HI3)
        ytcol.append(ytcol[-1] + BI2)
        ztcol.append(ztcol[-1] + HI2)
        
        if symmetric:
            ytcor = [-y for y in ytcol]
            ztcor = [z for z in ztcol]
            
            ytcor.reverse()
            ztcor.reverse()
            
        else:
            ytcor = [BO6 + BO7 - BO3 - BI1 - BI2]
            ztcor = [-HI1]
            ytcor.append(ytcor[-1] + BI2)
            ztcor.append(ztcor[-1] - HI2)
            ytcor.append(ytcor[-1] + BI1)
            ztcor.append(ztcor[-1] - HI3)
            
            if haunch:
                ytcor.append(ytcor[-1] - BO5)
                ztcor.append(ztcor[-1] - HI4)
                ytcor.append(ytcor[-1] + BO4 + BO5)
                ztcor.append(-HO1 - HO2 - HO3 - HO4)
            
            ytcor.append(BO6 + BO7)
            ztcor.append(-HO1 - HO2 - HO3)
            ytcor.append(ytcor[-1] + BOR2)
            ztcor.append(ztcor[-1] + HO3)
            ytcor.append(ytcor[-1] + BOR1)
            ztcor.append(ztcor[-1] + HO2)
            ytcor.append(ytcor[-1] + BOR11)
            ztcor.append(ztcor[-1])
            ytcor.append(ytcor[-1])
            ztcor.append(ztcor[-1] + HO1)
        
        ytcoAll = ytcor + ytcol
        ztcoAll = ztcor + ztcol
        
        ytcoAll.append(ytcoAll[0])
        ztcoAll.append(ztcoAll[0])
        
        # Outer_Bottom
        ybcol = [-BO7 + BI3 + BI4 + BI5]
        zbcol = [-(HO1 + HO2 + HO3 + HO5 + HO6) + HI8]
        ybcol.append(ybcol[-1] - BI5)
        zbcol.append(zbcol[-1] + HI7)
        ybcol.append(ybcol[-1] - BI4)
        zbcol.append(zbcol[-1] + HI6)
        
        if haunch:
            ybcol.append(-BO7 + BO10)
            zbcol.append(zbcol[-1] + HI5)
            ybcol.append(ybcol[-1] - BO9 - BO10)
            zbcol.append(-(HO1 + HO2 + HO3 + HO5) + HO61)
        
        ybcol.append(-(BO7 + BO8))
        zbcol.append(-(HO1 + HO2 + HO3 + HO5))
        ybcol.append(ybcol[-1] + BO8)
        zbcol.append(zbcol[-1] - HO6)
        
        ybcor = [-y for y in ybcol]
        zbcor = [z for z in zbcol]
        
        ybcor.reverse()
        zbcor.reverse()
        
        ybcoAll = ybcor + ybcol
        zbcoAll = zbcor + zbcol
        
        ybcoAll.append(ybcoAll[0])
        zbcoAll.append(zbcoAll[0])

        # 원점 좌표로 이동 (Center of Section)
        yo = TransFormGeometry.calculate_origin_coordinates(ytcoAll, ybcoAll)
        zo = TransFormGeometry.calculate_origin_coordinates(ztcoAll, zbcoAll)
        ytcoAll = [y - yo for y in ytcoAll]
        ztcoAll = [z - zo for z in ztcoAll]
        ybcoAll = [y - yo for y in ybcoAll]
        zbcoAll = [z - zo for z in zbcoAll]
        
        # 기준 좌표 추출
        if haunch:
            point_1 = [ytcoAll[10], ztcoAll[10]]
            point_2 = [ytcoAll[9], ztcoAll[9]]
            point_3 = [ybcoAll[14], zbcoAll[14]]
            point_4 = [ybcoAll[13], zbcoAll[13]]
        else:
            point_1 = [ytcoAll[8], ztcoAll[8]]
            point_2 = [ytcoAll[7], ztcoAll[7]]
            point_3 = [ybcoAll[10], zbcoAll[10]]
            point_4 = [ybcoAll[9], zbcoAll[9]]
        
        yt = max(ytcoAll, ybcoAll)
        yb = min(ytcoAll, ybcoAll)
        zt = max(ztcoAll, zbcoAll)
        zb = min(ztcoAll, zbcoAll)
        
        # 좌표 반환
        vertices = {
            "outer": [
                {
                    "y": ytcoAll,
                    "z": ztcoAll,
                    "reference": {
                        "name": "psc_cmpweb",
                        "elast": 1.0
                    }
                },
                {
                    "y": ybcoAll,
                    "z": zbcoAll,
                    "reference": {
                        "name": "psc_cmpweb",
                        "elast": 1.0
                    }
                }
            ]
        }
        
        # 특정 좌표 저장
        reference_points = {
            "psc_cmpweb": {
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
            "name": ["psc_cmpweb"],
            "control": "psc_cmpweb"
        }
        
        return vertices, reference_points, properties_control
    