class OffsetChange():
    """offset 변경"""
    
    @staticmethod
    def calculate_offset(section_data, properties, reference_points):
        """offset 변경"""
        
        # 데이터 추출 및 초기화
        context = OffsetChange._extract_context(section_data, properties, reference_points)
        
        if context.get("error"):
            return context
        
        # offset_pt에 따른 계산 분기
        offset_handlers = {
            "CC": OffsetChange._handle_center_center,
            "LT": OffsetChange._handle_left_top,
            "CT": OffsetChange._handle_center_top,
            "RT": OffsetChange._handle_right_top,
            "LC": OffsetChange._handle_left_center,
            "RC": OffsetChange._handle_right_center,
            "LB": OffsetChange._handle_left_bottom,
            "CB": OffsetChange._handle_center_bottom,
            "RB": OffsetChange._handle_right_bottom,
        }
        
        handler = offset_handlers.get(context["offset_pt"])
        if handler:
            return handler(context)
        else:
            return {
                "error": "offset data is not valid",
                "error_code": "UTILS_CALCULATORS_OFFSET_CHANGE"
            }
    
    @staticmethod
    def _extract_context(section_data, properties, reference_points):
        """컨텍스트 데이터 추출 및 변환"""
        
        # 원본 데이터 추출
        offset_pt = section_data.get("SECT_BEFORE", {}).get("OFFSET_PT", "")
        offset_center = section_data.get("SECT_BEFORE", {}).get("OFFSET_CENTER", None)
        user_offset_ref = section_data.get("SECT_BEFORE", {}).get("USER_OFFSET_REF", None)
        horz_offset_opt = section_data.get("SECT_BEFORE", {}).get("HORZ_OFFSET_OPT", None)
        userdef_offset_y = section_data.get("SECT_BEFORE", {}).get("USERDEF_OFFSET_YI", None)
        vert_offset_opt = section_data.get("SECT_BEFORE", {}).get("VERT_OFFSET_OPT", None)
        userdef_offset_z = section_data.get("SECT_BEFORE", {}).get("USERDEF_OFFSET_ZI", None)
        
        centroid = properties.get("total", {}).get("centroid", [])
        extreme_fiber = reference_points.get("extreme_fiber", {})
        
        if offset_pt == "":
            return {"error": "offset_pt is empty"}
        
        # 매핑 테이블
        offset_center_mapping = {0: "Centroid", 1: "Center_of_Section"}
        user_offset_ref_mapping = {0: "Centroid", 1: "Extreme_Fiber"}
        offset_opt_mapping = {0: "to_Extreme_Fiber", 1: "User"}
        
        # 컨텍스트 구성
        context = {
            "offset_pt": offset_pt,
            "offset_center": offset_center_mapping.get(offset_center) if offset_center is not None else None,
            "user_offset_ref": user_offset_ref_mapping.get(user_offset_ref) if user_offset_ref is not None else None,
            "horz_offset_opt": offset_opt_mapping.get(horz_offset_opt) if horz_offset_opt is not None else None,
            "vert_offset_opt": offset_opt_mapping.get(vert_offset_opt) if vert_offset_opt is not None else None,
            "userdef_offset_y": userdef_offset_y,
            "userdef_offset_z": userdef_offset_z,
            "centroid_y": centroid[0] if centroid else 0.0,
            "centroid_z": centroid[1] if centroid else 0.0,
            "center_y": 0.0,
            "center_z": 0.0,
            "yt": extreme_fiber.get("yt", 0.0),
            "yb": extreme_fiber.get("yb", 0.0),
            "zt": extreme_fiber.get("zt", 0.0),
            "zb": extreme_fiber.get("zb", 0.0),
        }
        
        return context
    
    @staticmethod
    def _create_result(offset_pt_name, center_location, horz_offset, vert_offset, coordinates):
        """결과 객체 생성"""
        return {
            "offset_pt": offset_pt_name,
            "center_location": center_location,
            "Horizontal_offset": horz_offset,
            "Vertical_offset": vert_offset,
            "offset_coordinates": coordinates
        }
    
    @staticmethod
    def _create_error(offset_pt):
        """에러 객체 생성"""
        return {
            "error": f"offset data({offset_pt}) is not valid",
            "error_code": "UTILS_CALCULATORS_OFFSET_CHANGE"
        }
    
    @staticmethod
    def _handle_center_center(context):
        """CC: Center to Center 처리"""
        offset_center = context["offset_center"]
        horz_offset_opt = context["horz_offset_opt"]
        vert_offset_opt = context["vert_offset_opt"]
        
        if offset_center == "Centroid":
            coordinates = [context["centroid_y"], context["centroid_z"]]
        elif offset_center == "Center_of_Section":
            coordinates = [context["center_y"], context["center_z"]]
        else:
            return OffsetChange._create_error("CC")
        
        return OffsetChange._create_result("Center-Center", offset_center, horz_offset_opt, vert_offset_opt, coordinates)
    
    @staticmethod
    def _handle_left_top(context):
        """LT: Left to Top 처리"""
        horz_opt = context["horz_offset_opt"]
        vert_opt = context["vert_offset_opt"]
        user_ref = context["user_offset_ref"]
        
        # Y 좌표 계산
        if horz_opt == "to_Extreme_Fiber":
            y_coord = context["yb"]
        elif horz_opt == "User":
            if user_ref == "Extreme_Fiber":
                y_coord = context["yb"] + context["userdef_offset_y"]
            elif user_ref == "Centroid":
                y_coord = context["centroid_y"] - context["userdef_offset_y"]
            else:
                return OffsetChange._create_error("LT")
        else:
            return OffsetChange._create_error("LT")
        
        # Z 좌표 계산
        if vert_opt == "to_Extreme_Fiber":
            z_coord = context["zt"]
        elif vert_opt == "User":
            if user_ref == "Extreme_Fiber":
                z_coord = context["zt"] - context["userdef_offset_z"]
            elif user_ref == "Centroid":
                z_coord = context["centroid_z"] + context["userdef_offset_z"]
            else:
                return OffsetChange._create_error("LT")
        else:
            return OffsetChange._create_error("LT")
        
        return OffsetChange._create_result("Left-Top", None, horz_opt, vert_opt, [y_coord, z_coord])
    
    @staticmethod
    def _handle_center_top(context):
        """CT: Center to Top 처리"""
        offset_center = context["offset_center"]
        horz_opt = context["horz_offset_opt"]
        vert_opt = context["vert_offset_opt"]
        user_ref = context["user_offset_ref"]
        
        # Y 좌표 계산
        if horz_opt == "to_Extreme_Fiber":
            if offset_center == "Centroid":
                y_coord = context["centroid_y"]
            elif offset_center == "Center_of_Section":
                y_coord = context["center_y"]
            else:
                return OffsetChange._create_error("CT")
        else:
            return OffsetChange._create_error("CT")
        
        # Z 좌표 계산
        if vert_opt == "to_Extreme_Fiber":
            z_coord = context["zt"]
        elif vert_opt == "User":
            if user_ref == "Centroid":
                z_coord = context["centroid_z"] + context["userdef_offset_z"]
            elif user_ref == "Extreme_Fiber":
                z_coord = context["zt"] - context["userdef_offset_z"]
            else:
                return OffsetChange._create_error("CT")
        else:
            return OffsetChange._create_error("CT")
        
        return OffsetChange._create_result("Center-Top", offset_center, horz_opt, vert_opt, [y_coord, z_coord])
    
    @staticmethod
    def _handle_right_top(context):
        """RT: Right to Top 처리"""
        horz_opt = context["horz_offset_opt"]
        vert_opt = context["vert_offset_opt"]
        user_ref = context["user_offset_ref"]
        
        # Y 좌표 계산
        if horz_opt == "to_Extreme_Fiber":
            y_coord = context["yt"]
        elif horz_opt == "User":
            if user_ref == "Extreme_Fiber":
                y_coord = context["yt"] - context["userdef_offset_y"]
            elif user_ref == "Centroid":
                y_coord = context["centroid_y"] + context["userdef_offset_y"]
            else:
                return OffsetChange._create_error("RT")
        else:
            return OffsetChange._create_error("RT")
        
        # Z 좌표 계산
        if vert_opt == "to_Extreme_Fiber":
            z_coord = context["zt"]
        elif vert_opt == "User":
            if user_ref == "Extreme_Fiber":
                z_coord = context["zt"] - context["userdef_offset_z"]
            elif user_ref == "Centroid":
                z_coord = context["centroid_z"] + context["userdef_offset_z"]
            else:
                return OffsetChange._create_error("RT")
        else:
            return OffsetChange._create_error("RT")
        
        return OffsetChange._create_result("Right-Top", None, horz_opt, vert_opt, [y_coord, z_coord])
    
    @staticmethod
    def _handle_left_center(context):
        """LC: Left to Center 처리"""
        offset_center = context["offset_center"]
        horz_opt = context["horz_offset_opt"]
        vert_opt = context["vert_offset_opt"]
        user_ref = context["user_offset_ref"]
        
        # Y 좌표 계산
        if horz_opt == "to_Extreme_Fiber":
            y_coord = context["yb"]
        elif horz_opt == "User":
            if user_ref == "Centroid":
                y_coord = context["centroid_y"] - context["userdef_offset_y"]
            elif user_ref == "Extreme_Fiber":
                y_coord = context["yb"] + context["userdef_offset_y"]
            else:
                return OffsetChange._create_error("LC")
        else:
            return OffsetChange._create_error("LC")
        
        # Z 좌표 계산
        if vert_opt == "to_Extreme_Fiber":
            if offset_center == "Centroid":
                z_coord = context["centroid_z"]
            elif offset_center == "Center_of_Section":
                z_coord = context["center_z"]
            else:
                return OffsetChange._create_error("LC")
        else:
            return OffsetChange._create_error("LC")
        
        return OffsetChange._create_result("Left-Center", offset_center, horz_opt, vert_opt, [y_coord, z_coord])
    
    @staticmethod
    def _handle_right_center(context):
        """RC: Right to Center 처리"""
        offset_center = context["offset_center"]
        horz_opt = context["horz_offset_opt"]
        vert_opt = context["vert_offset_opt"]
        user_ref = context["user_offset_ref"]
        
        # Y 좌표 계산
        if horz_opt == "to_Extreme_Fiber":
            y_coord = context["yt"]
        elif horz_opt == "User":
            if user_ref == "Centroid":
                y_coord = context["centroid_y"] + context["userdef_offset_y"]
            elif user_ref == "Extreme_Fiber":
                y_coord = context["yt"] - context["userdef_offset_y"]
            else:
                return OffsetChange._create_error("RC")
        else:
            return OffsetChange._create_error("RC")
        
        # Z 좌표 계산
        if vert_opt == "to_Extreme_Fiber":
            if offset_center == "Centroid":
                z_coord = context["centroid_z"]
            elif offset_center == "Center_of_Section":
                z_coord = context["center_z"]
            else:
                return OffsetChange._create_error("RC")
        else:
            return OffsetChange._create_error("RC")
        
        return OffsetChange._create_result("Right-Center", offset_center, horz_opt, vert_opt, [y_coord, z_coord])
    
    @staticmethod
    def _handle_left_bottom(context):
        """LB: Left to Bottom 처리"""
        horz_opt = context["horz_offset_opt"]
        vert_opt = context["vert_offset_opt"]
        user_ref = context["user_offset_ref"]
        
        # Y 좌표 계산
        if horz_opt == "to_Extreme_Fiber":
            y_coord = context["yb"]
        elif horz_opt == "User":
            if user_ref == "Extreme_Fiber":
                y_coord = context["yb"] + context["userdef_offset_y"]
            elif user_ref == "Centroid":
                y_coord = context["centroid_y"] - context["userdef_offset_y"]
            else:
                return OffsetChange._create_error("LB")
        else:
            return OffsetChange._create_error("LB")
        
        # Z 좌표 계산
        if vert_opt == "to_Extreme_Fiber":
            z_coord = context["zb"]
        elif vert_opt == "User":
            if user_ref == "Extreme_Fiber":
                z_coord = context["zb"] + context["userdef_offset_z"]
            elif user_ref == "Centroid":
                z_coord = context["centroid_z"] - context["userdef_offset_z"]
            else:
                return OffsetChange._create_error("LB")
        else:
            return OffsetChange._create_error("LB")
        
        return OffsetChange._create_result("Left-Bottom", None, horz_opt, vert_opt, [y_coord, z_coord])
    
    @staticmethod
    def _handle_center_bottom(context):
        """CB: Center to Bottom 처리"""
        offset_center = context["offset_center"]
        horz_opt = context["horz_offset_opt"]
        vert_opt = context["vert_offset_opt"]
        user_ref = context["user_offset_ref"]
        
        # Y 좌표 계산
        if horz_opt == "to_Extreme_Fiber":
            if offset_center == "Centroid":
                y_coord = context["centroid_y"]
            elif offset_center == "Center_of_Section":
                y_coord = context["center_y"]
            else:
                return OffsetChange._create_error("CB")
        else:
            return OffsetChange._create_error("CB")
        
        # Z 좌표 계산
        if vert_opt == "to_Extreme_Fiber":
            z_coord = context["zb"]
        elif vert_opt == "User":
            if user_ref == "Centroid":
                z_coord = context["centroid_z"] - context["userdef_offset_z"]
            elif user_ref == "Extreme_Fiber":
                z_coord = context["zb"] + context["userdef_offset_z"]
            else:
                return OffsetChange._create_error("CB")
        else:
            return OffsetChange._create_error("CB")
        
        return OffsetChange._create_result("Center-Bottom", offset_center, horz_opt, vert_opt, [y_coord, z_coord])
    
    @staticmethod
    def _handle_right_bottom(context):
        """RB: Right to Bottom 처리"""
        horz_opt = context["horz_offset_opt"]
        vert_opt = context["vert_offset_opt"]
        user_ref = context["user_offset_ref"]
        
        # Y 좌표 계산
        if horz_opt == "to_Extreme_Fiber":
            y_coord = context["yt"]
        elif horz_opt == "User":
            if user_ref == "Extreme_Fiber":
                y_coord = context["yt"] - context["userdef_offset_y"]
            elif user_ref == "Centroid":
                y_coord = context["centroid_y"] + context["userdef_offset_y"]
            else:
                return OffsetChange._create_error("RB")
        else:
            return OffsetChange._create_error("RB")
        
        # Z 좌표 계산
        if vert_opt == "to_Extreme_Fiber":
            z_coord = context["zb"]
        elif vert_opt == "User":
            if user_ref == "Extreme_Fiber":
                z_coord = context["zb"] + context["userdef_offset_z"]
            elif user_ref == "Centroid":
                z_coord = context["centroid_z"] - context["userdef_offset_z"]
            else:
                return OffsetChange._create_error("RB")
        else:
            return OffsetChange._create_error("RB")
        
        return OffsetChange._create_result("Right-Bottom", None, horz_opt, vert_opt, [y_coord, z_coord])