# calc/railway_steel_lambda.py
import math

# λs,1 값 테이블 (이미지 3 기반)
# 키: (beam_type, steel_type, span_length)
# 값: (standard_traffic, heavy_traffic)
lambda1_table_rail = {
    # 단순지지보
    ("Simply supported beams", "reinforcing steel", 2): (0.90, 0.95),
    ("Simply supported beams", "reinforcing steel", 20): (0.65, 0.70),
    ("Simply supported beams", "curved tendons in steel ducts", 2): (1.00, 1.05),
    ("Simply supported beams", "curved tendons in steel ducts", 20): (0.70, 0.70),
    ("Simply supported beams", "splice devices (prestressing)", 2): (1.25, 1.35),
    ("Simply supported beams", "splice devices (prestressing)", 20): (0.75, 0.75),
    ("Simply supported beams", "splice devices (reinforcing)", 2): (0.80, 0.85),
    ("Simply supported beams", "splice devices (reinforcing)", 20): (0.40, 0.40),
    
    # 연속보 (중간 경간)
    ("Continuous beams (mid span)", "reinforcing steel", 2): (0.95, 1.05),
    ("Continuous beams (mid span)", "reinforcing steel", 20): (0.50, 0.55),
    ("Continuous beams (mid span)", "curved tendons in steel ducts", 2): (1.00, 1.15),
    ("Continuous beams (mid span)", "curved tendons in steel ducts", 20): (0.55, 0.55),
    ("Continuous beams (mid span)", "splice devices (prestressing)", 2): (1.25, 1.40),
    ("Continuous beams (mid span)", "splice devices (prestressing)", 20): (0.55, 0.55),
    ("Continuous beams (mid span)", "splice devices (reinforcing)", 2): (0.75, 0.90),
    ("Continuous beams (mid span)", "splice devices (reinforcing)", 20): (0.35, 0.30),
    
    # 연속보 (단부 경간)
    ("Continuous beams (end span)", "reinforcing steel", 2): (0.90, 1.00),
    ("Continuous beams (end span)", "reinforcing steel", 20): (0.65, 0.65),
    ("Continuous beams (end span)", "curved tendons in steel ducts", 2): (1.05, 1.15),
    ("Continuous beams (end span)", "curved tendons in steel ducts", 20): (0.65, 0.65),
    ("Continuous beams (end span)", "splice devices (prestressing)", 2): (1.30, 1.45),
    ("Continuous beams (end span)", "splice devices (prestressing)", 20): (0.65, 0.70),
    ("Continuous beams (end span)", "splice devices (reinforcing)", 2): (0.80, 0.90),
    ("Continuous beams (end span)", "splice devices (reinforcing)", 20): (0.35, 0.35),
    
    # 연속보 (중간 지지부)
    ("Continuous beams (intermediate support)", "reinforcing steel", 2): (0.85, 0.85),
    ("Continuous beams (intermediate support)", "reinforcing steel", 20): (0.70, 0.75),
    ("Continuous beams (intermediate support)", "curved tendons in steel ducts", 2): (0.90, 0.95),
    ("Continuous beams (intermediate support)", "curved tendons in steel ducts", 20): (0.70, 0.75),
    ("Continuous beams (intermediate support)", "splice devices (prestressing)", 2): (1.10, 1.10),
    ("Continuous beams (intermediate support)", "splice devices (prestressing)", 20): (0.75, 0.80),
    ("Continuous beams (intermediate support)", "splice devices (reinforcing)", 2): (0.70, 0.70),
    ("Continuous beams (intermediate support)", "splice devices (reinforcing)", 20): (0.35, 0.40),
}

# 강재 유형별 기준 응력 범위 테이블 UNI ENV 1992-2
steel_stress_range_table = {
    "Straight and bent bars": 180,               # 일반 철근
    "Welded bars and wire fabrics": 100,          # 용접 철근
    "Splicing devices (reinforcing)": 100,        # 철근 이음장치
    "Pre-tensioning": 170,                       # 프리텐션
    "Single strands in plastic ducts": 170,      # 플라스틱 덕트 내 단일 강선
    "Straight tendons or curved in plastic ducts": 145,  # 플라스틱 덕트 내 직선/곡선 강연선
    "Curved tendons in steel ducts": 110,        # 강재 덕트 내 곡선 강연선
    "Splicing devices (prestressing)": 70        # 강연선 이음장치
}
# 강재 유형별 S-N 곡선 지수 (k2)
steel_k2_values = {
    "Straight and bent bars": 9,
    "Welded bars and wire fabrics": 5,
    "Splicing devices (reinforcing)": 5,
    "Pre-tensioning": 9,
    "Single strands in plastic ducts": 9,
    "Straight tendons or curved in plastic ducts": 9,
    "Curved tendons in steel ducts": 7,
    "Splicing devices (prestressing)": 5
}
# 강재 유형을 표준 유형으로 매핑하는 함수
def map_steel_type_to_standard(steel_type):
    """사용자 인터페이스의 강재 유형을 표준 유형으로 매핑"""
    if "Straight and bent" in steel_type:
        return "reinforcing steel"
    elif "Curved tendons in steel ducts" in steel_type:
        return "curved tendons in steel ducts"
    elif "Splicing devices (prestressing)" in steel_type:
        return "splice devices (prestressing)"
    elif "Splicing devices" in steel_type or "Welded bars" in steel_type:
        return "splice devices (reinforcing)"
    else:
        return "reinforcing steel"  # 기본값


def get_lambda1_rail(beam_type, steel_type, span_length, traffic_type):
    """Lambda1 계수 값 계산 (로그 보간 적용)

    Args:
        beam_type (str): 보 유형 (예: 'Simply supported beams', 'Continuous beams mid')
        steel_type (str): 강재 유형 (예: 'Post-tensioning[Curved tendons in steel ducts]')
        span_length (float): 영향선의 임계 길이 또는 경간 (단위: m)
        traffic_type (str): 교통 하중 유형 ('Standard traffic' 또는 'Heavy traffic')

    Returns:
        float: 계산된 λs,1 값
    """
    # 강재 유형을 표준 강재 유형으로 매핑
    std_steel_type = map_steel_type_to_standard(steel_type)

    # 2m, 20m 기준의 테이블 키 구성
    k1 = (beam_type, std_steel_type, 2)
    k2 = (beam_type, std_steel_type, 20)

    # 테이블에서 λs,1 값 불러오기
    s1, h1 = lambda1_table_rail.get(k1)
    s2, h2 = lambda1_table_rail.get(k2)

    is_heavy = traffic_type == "Heavy traffic"

    # 경계 조건 처리
    if span_length <= 2:
        return h1 if is_heavy else s1
    elif span_length >= 20:
        return h2 if is_heavy else s2
    else:
        # 로그 보간 공식 적용
        logL = math.log10(span_length)
        delta_log = logL - 0.3

        if is_heavy:
            return h1 + (h2 - h1) * delta_log
        else:
            return s1 + (s2 - s1) * delta_log
    
def get_k2_value_rail(steel_type):
    """강재 유형에 따른 S-N 곡선 지수(k2) 반환"""
    return steel_k2_values.get(steel_type, 9)  # 기본값 9 (일반 철근용)

def get_stress_range_rail(steel_type):
    """강재 유형에 따른 기준 응력 범위(ΔσRsk) 반환"""
    return steel_stress_range_table.get(steel_type, 0.0)  # 기본값 162.5 MPa

def calculate_lambda2_rail(vol, k2):
    """λs,2 계산 - 연간 통과 톤수에 따른 보정"""
    # 올바른 공식: λs,2 = (Vol/25×10^6)^(1/k2)
    return (vol / (25 * 10**6)) ** (1 / k2)

def calculate_lambda3_rail(nyear, k2):
    """λs,3 계산 - 설계 수명에 따른 보정"""
    # 올바른 공식: λs,3 = (Nyears/100)^(1/k2)
    return (nyear / 100) ** (1 / k2)

def calculate_lambda4_rail(delta_sigma_1, delta_sigma_12, nc, nt, k2):
    """λs,4 계산 - 다중 트랙 효과"""
    # s1 계산
    s1 = delta_sigma_1 / delta_sigma_12 if delta_sigma_12 != 0 else 0
    
    # s2 계산 (간소화: 양방향 교통의 경우, s2도 s1과 같다고 가정)
    s2 = s1
    
    # n 계산
    n = 0.12
    
    # λs,4 계산
    # 올바른 공식: λs,4 = [n + (1-n)·s1^k2 + (1-n)·s2^k2]^(1/k2)
    result = (n + (1-n) * (s1**k2) + (1-n) * (s2**k2)) ** (1/k2)
    
    # 압축 응력만 있는 경우 (s1 = 0)
    if s1 <= 0:
        return 1.0
        
    return result
# 테스트
# if __name__ == "__main__":
#     # 테스트 예시
#     lambda1 = get_lambda1_rail("Simply supported beams", "Straight and bent bars", 35, "Standard traffic")
#     print(f"Lambda1 = {lambda1}")
    
#     stress_range = get_stress_range_rail("Straight and bent bars")
#     print(f"ΔσRsk = {stress_range} MPa")