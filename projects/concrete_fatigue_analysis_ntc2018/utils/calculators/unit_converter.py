def get_unit_conversion_factor(from_unit: str, to_unit: str) -> float:
    """
    두 단위 사이의 변환 인자를 반환합니다.
    
    Args:
        from_unit: 변환할 원본 단위 (mm, m, cm, in, ft 중 하나)
        to_unit: 변환할 대상 단위 (mm, m, cm, in, ft 중 하나)
        
    Returns:
        변환 인자 (float): from_unit을 to_unit으로 변환하기 위해 곱해야 하는 값
        
    Examples:
        get_unit_conversion_factor("m", "cm") -> 100.0
        get_unit_conversion_factor("ft", "m") -> 0.3048
    """
    to_unit = to_unit.lower()
    # 모든 단위를 미터(m)로 변환하는 인자
    units_to_meter = {
        "mm": 0.001,     # 1mm = 0.001m
        "cm": 0.01,      # 1cm = 0.01m
        "m": 1.0,        # 1m = 1m
        "in": 0.0254,    # 1in = 0.0254m
        "ft": 0.3048     # 1ft = 0.3048m
    }
    
    # 입력 검증
    if from_unit not in units_to_meter or to_unit not in units_to_meter:
        raise ValueError(f"지원하지 않는 단위입니다. 지원하는 단위: {list(units_to_meter.keys())}")
    
    # 변환 공식: (from_unit의 미터 변환 인자) / (to_unit의 미터 변환 인자)
    return units_to_meter[from_unit] / units_to_meter[to_unit]
