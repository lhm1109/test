import math
from projects.concrete_fatigue_analysis_ntc2018.utils.geometry.transform import TransFormGeometry

class ShapeGenerator:
    """
    기본 형태 생성기
    
    규칙:
        외곽선은 반시계 방향으로 생성
        내곽선은 시계 방향으로 생성
        좌표는 Closed Shape 형태로 생성(처음 좌표와 마지막 좌표가 같음)
        원형, 호의 경우 5도 간격으로 좌표 생성
    """
    
    @staticmethod
    def generate_l_shape(height, width, web_thickness, flange_thickness, origin=(0, 0)):
        """
        L 형태 단면의 vertex 좌표 생성
        
        좌상단 좌표를 기준으로 설정: 제품 기준 1번 정점
        """
        y0, z0 = origin
        points = [
            (y0, z0),
            (y0, z0 - height),
            (y0 + web_thickness, z0 - height),
            (y0 + web_thickness, z0 - flange_thickness),
            (y0 + width, z0 - flange_thickness),
            (y0 + width, z0),
            (y0, z0)  # Closed shape
        ]
        
        y, z = zip(*points)
        
        return {
            "y": list(y),
            "z": list(z)
        }
    
    @staticmethod
    def generate_c_shape(height, top_width, web_thickness, top_flange_thickness, bottom_width=0, bottom_flange_thickness=0, origin=(0, 0)):
        """
        C 형태 단면의 vertex 좌표 생성
        
        좌상단 좌표를 기준으로 설정: 제품 기준 1번 정점
        """
        # Bottom 데이터는 0일 경우, Top 데이터와 동일하게 설정
        if math.isclose(bottom_width, 0, abs_tol=1e-9):
            bottom_width = top_width
        
        if math.isclose(bottom_flange_thickness, 0, abs_tol=1e-9):
            bottom_flange_thickness = top_flange_thickness
        
        y0, z0 = origin
        points = [
            (y0, z0),
            (y0, z0 - height),
            (y0 + bottom_width, z0 - height),
            (y0 + bottom_width, z0 - height + bottom_flange_thickness),
            (y0 + web_thickness, z0 - height + bottom_flange_thickness),
            (y0 + web_thickness, z0 - top_flange_thickness),
            (y0 + top_width, z0 - top_flange_thickness),
            (y0 + top_width, z0),
            (y0, z0)  # Closed shape
        ]
        
        y, z = zip(*points)
        
        return {
            "y": list(y),
            "z": list(z)
        }

    @staticmethod
    def generate_h_shape(height, top_width, web_thickness, top_flange_thickness, bottom_width, bottom_flange_thickness, origin=(0, 0)):
        """
        H 형태 단면의 vertex 좌표 생성
        
        상단 중심 좌표를 기준으로 설정: 제품 기준 1번과 2번의 중간점
        """
        # Bottom 데이터는 0일 경우, Top 데이터와 동일하게 설정
        if math.isclose(bottom_width, 0, abs_tol=1e-9):
            bottom_width = top_width
        
        if math.isclose(bottom_flange_thickness, 0, abs_tol=1e-9):
            bottom_flange_thickness = top_flange_thickness
        
        y0, z0 = origin
        points = [
            (y0 - top_width / 2, z0),
            (y0 - top_width / 2, z0 - top_flange_thickness),
            (y0 - web_thickness / 2, z0 - top_flange_thickness),
            (y0 - web_thickness / 2, z0 - height + bottom_flange_thickness),
            (y0 - bottom_width / 2, z0 - height + bottom_flange_thickness),
            (y0 - bottom_width / 2, z0 - height)
        ]
        
        mirrored_points = [(-y, z) for y, z in reversed(points)]
        
        full_points = points + mirrored_points
        full_points.append(full_points[0])
        
        y, z = zip(*full_points)
        
        return {
            "y": list(y),
            "z": list(z)
        }

    @staticmethod
    def generate_t_shape(height, width, web_thickness, flange_thickness, origin=(0, 0)):
        """
        T 형태 단면의 vertex 좌표 생성
        
        상단 중심 좌표를 기준으로 설정: 제품 기준 1번과 2번의 중간점
        """
        y0, z0 = origin
        points = [
            (y0 - width / 2, z0),
            (y0 - width / 2, z0 - flange_thickness),
            (y0 - web_thickness / 2, z0 - flange_thickness),
            (y0 - web_thickness / 2, z0 - height)
        ]
        
        mirrored_points = [(-y, z) for y, z in reversed(points)]
        
        full_points = points + mirrored_points
        full_points.append(full_points[0])
        
        y, z = zip(*full_points)
        
        return {
            "y": list(y),
            "z": list(z)
        }
        
    @staticmethod
    def generate_box_shape(height, width, web_thickness, top_flange_thickness, web_center_dist, bottom_flange_thickness, origin=(0, 0)):
        """
        Box 형태 단면의 vertex 좌표 생성
        
        상단 중심 좌표를 기준으로 설정: 제품 기준 1번과 2번의 중간점
        """
        # Bottom 데이터는 0일 경우, Top 데이터와 동일하게 설정
        if math.isclose(bottom_flange_thickness, 0, abs_tol=1e-9):
            bottom_flange_thickness = top_flange_thickness
        
        y0, z0 = origin
        
        outer_points = [
            (y0 - width / 2, z0),
            (y0 - width / 2, z0 - top_flange_thickness),
            (y0 - width / 2, z0 - height + bottom_flange_thickness),
            (y0 - width / 2, z0 - height)
        ]
        
        inner_points = []
        
        if math.isclose(web_center_dist, 0, abs_tol=1e-9):
            outer_points.insert(2, (y0 - width / 2, z0 - top_flange_thickness))
            outer_points.insert(3, (y0 - width / 2, z0 - height + bottom_flange_thickness))
            
            inner_points.append((y0 - width / 2 + web_thickness, z0 - top_flange_thickness))
            inner_points.append((y0 - width / 2 + web_thickness, z0 - height + bottom_flange_thickness))
            
        else:
            outer_points.insert(2, (y0 - web_center_dist / 2 - web_thickness / 2, z0 - top_flange_thickness))
            outer_points.insert(3, (y0 - web_center_dist / 2 - web_thickness / 2, z0 - height + bottom_flange_thickness))
            
            inner_points.append((y0 - web_center_dist / 2 + web_thickness / 2, z0 - top_flange_thickness))
            inner_points.append((y0 - web_center_dist / 2 + web_thickness / 2, z0 - height + bottom_flange_thickness))
            
        
        mirrored_outer_points = [(-y, z) for y, z in reversed(outer_points)]
        mirrored_inner_points = [(-y, z) for y, z in reversed(inner_points)]
        
        full_outer_points = outer_points + mirrored_outer_points
        full_outer_points.append(full_outer_points[0])
        
        full_inner_points = inner_points + mirrored_inner_points
        full_inner_points.append(full_inner_points[0])
        
        outer_y, outer_z = zip(*full_outer_points)
        inner_y, inner_z = zip(*full_inner_points)
        
        return {
            "outer": {
                "y": list(outer_y),
                "z": list(outer_z)
            },
            "inner": {
                "y": list(inner_y),
                "z": list(inner_z)
            }
        }
        
    @staticmethod
    def generate_circle_shape(radius, origin=(0, 0)):
        """
        Circle 형태 단면의 vertex 좌표 생성
        시계방향으로 생성하고, 반시계방향으로 반환
        
        중심 좌표를 기준으로 설정
        """
        y0, z0 = origin
        points = []
        
        for degree in range(0, 361, 3):
            rad = math.radians(degree)
            y = y0 + radius * math.sin(rad)
            z = z0 + radius * math.cos(rad)
            points.append((y, z))
        
        y, z = zip(*points)
        
        coordinates = {
            "y": list(y),
            "z": list(z)
        }
        
        coordinates = TransFormGeometry.reverse_coordinates_list(coordinates)
        
        return coordinates
        
    @staticmethod
    def generate_solid_rectangle_shape(height, width, origin=(0, 0)):
        """
        Solid Rectangle 형태 단면의 vertex 좌표 생성
        
        상단 중심 좌표를 기준으로 설정: 제품 기준 1번과 2번의 중간점
        """
        y0, z0 = origin
        points = [
            (y0 - width / 2, z0),
            (y0 - width / 2, z0 - height),
            (y0 + width / 2, z0 - height),
            (y0 + width / 2, z0),
            (y0 - width / 2, z0)
        ]
        
        y, z = zip(*points)
        
        return {
            "y": list(y),
            "z": list(z)
        }
        
    @staticmethod
    def generate_arc_shape(radius, start_angle, end_angle, origin=(0, 0), include_endpoints=True):
        """
        arc_shape 형태 단면의 vertex 좌표 생성
        시계방향으로 생성
        """
        y0, z0 = origin

        total_angle = abs(end_angle - start_angle)
        num_points = max(int(total_angle // 3), 1) + 1  # 최소 2개 점 이상
        angles = [
            start_angle + i * (end_angle - start_angle) / (num_points - 1)
            for i in range(num_points)
        ]

        # 만약 endpoint 포함하지 않도록 설정되면 양 끝 각도를 제외
        if not include_endpoints:
            angles = angles[1:-1]

        points = []
        for degree in angles:
            rad = math.radians(degree)
            y = y0 + radius * math.sin(rad)
            z = z0 + radius * math.cos(rad)
            points.append((y, z))

        y, z = zip(*points) if points else ([], [])
        coordinates = {
            "y": list(y),
            "z": list(z)
        }

        coordinates = TransFormGeometry.reverse_coordinates_list(coordinates)

        return coordinates
    
    @staticmethod
    def generate_psc_i_shape(vSize_PSC_A, vSize_PSC_B, vSize_PSC_C, vSize_PSC_D, joint):
        
        # Variable Initialization
        H10, HL10, HL20, HL21, HL22, HL30, HL40, HL41, HL42, HL50 = vSize_PSC_A
        BL10, BL20, BL21, BL22, BL40, BL41, BL42 = vSize_PSC_B
        HR10, HR20, HR21, HR22, HR30, HR40, HR41, HR42, HR50 = vSize_PSC_C
        BR10, BR20, BR21, BR22, BR40, BR41, BR42 = vSize_PSC_D
        J1, JL1, JL2, JL3, JL4, JR1, JR2, JR3, JR4 = joint
        
        # Height Calculation
        heightL = HL10 + HL20 + HL30 + HL40 + HL50
        heightR = HR10 + HR20 + HR30 + HR40 + HR50
        heightC = 0
        
        if J1 :
            heightC = H10
        else :
            if heightR > heightL :
                heightC = BL20 * (heightR - heightL) / (BL20 + BR20) + heightL
            elif heightR < heightL :
                heightC = BR20 * (heightL - heightR) / (BL20 + BR20) + heightR
            elif heightR == heightL :
                heightC = (heightL + heightR) / 2
        
        # heightM = max(heightL, heightR, heightC)
        height_LR = (heightL + heightR) / 2
        heightM = max(height_LR, heightC)
                
        # Outer Cell_Left Side
        ycol = [0]
        zcol = [heightC - heightM]
        ycol.append(-BL20)
        zcol.append(heightL - heightM)
        ycol.append(ycol[1])
        zcol.append(zcol[1] - HL10)
        ycol.append(-BL10)
        zcol.append(zcol[2] - HL20)
        ycol.append(ycol[3])
        zcol.append(zcol[3] - HL30)
        ycol.append(-BL40)
        zcol.append(zcol[4] - HL40)
        ycol.append(ycol[5])
        zcol.append(zcol[5] - HL50)
        ycol.append(0)
        zcol.append(-heightM)
        
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
        ycor = [0]
        zcor = [heightC - heightM]
        ycor.append(BR20)
        zcor.append(heightR - heightM)
        ycor.append(ycor[1])
        zcor.append(zcor[1] - HR10)
        ycor.append(BR10)
        zcor.append(zcor[2] - HR20)
        ycor.append(ycor[3])
        zcor.append(zcor[3] - HR30)
        ycor.append(BR40)
        zcor.append(zcor[4] - HR40)
        ycor.append(ycor[5])
        zcor.append(zcor[5] - HR50)
        ycor.append(0)
        zcor.append(-heightM)
        
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
        
        # dimension 추출
        maximum_height = max(heightL, heightR, heightC)
        
        coordinates = {
            "y": ycoAll,
            "z": zcoAll,
            "reference": {
                "girder_height": {
                    "left": heightL,
                    "right": heightR,
                    "center": heightC,
                    "max": maximum_height
                },
                "girder_web_thickness": {
                    "left": BL10,
                    "right": BR10,
                    "all": BL10 + BR10
                },
                "girder_width": {
                    "top": BL20 + BR20,
                    "bottom": BL40 + BR40
                }
            }
        }
        
        return coordinates
    
    @staticmethod
    def generate_psc_t_shape(vSize_PSC_A, vSize_PSC_B, vSize_PSC_C, vSize_PSC_D, joint):
        # Variable Initialization
        H10, HL10, HL20, HL30, BL10, BL20, BL30, BL40 = vSize_PSC_A
        HL21, HL22, HL31, HL32, BL21, BL22, BL31, BL32 = vSize_PSC_B
        HR10, HR20, HR30, BR10, BR20, BR30, BR40 = vSize_PSC_C
        HR21, HR22, HR31, HR32, BR21, BR22, BR31, BR32 = vSize_PSC_D
        J1, JL1, JL2, JL3, JL4, JR1, JR2, JR3, JR4 = joint
        
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
        
        # heightM = max(heightL, heightR, heightC)
        height_LR = (heightL + heightR) / 2
        heightM = max(height_LR, heightC)
        
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
        
        # dimension 추출
        maximum_height = max(heightL, heightR, heightC)
        
        coordinates = {
            "y": ycoAll,
            "z": zcoAll,
            "reference": {
                "girder_height": {
                    "left": heightL,
                    "right": heightR,
                    "center": heightC,
                    "max": maximum_height
                },
                "girder_web_thickness": {
                    "left": BL20+BL10,
                    "right": BR20+BR10,
                    "all": BL20+BL10+BR20+BR10
                },
                "girder_width": {
                    "top": BL40 + BR40,
                    "bottom": BL10 + BR10
                }
            }
        }
        
        return coordinates