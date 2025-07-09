#calc/railway_concrete_lambda.py
import math
lambda1_table = {
    ("Simply Supported Beams", "Compression zone", 2): (0.70, 0.70),
    ("Simply Supported Beams", "Compression zone", 20): (0.75, 0.75),
    ("Simply Supported Beams", "Precompressed tensile zone", 2): (0.95, 1.00),
    ("Simply Supported Beams", "Precompressed tensile zone", 20): (0.90, 0.90),
    ("Continuous Beams (mid span)", "Compression zone", 2): (0.75, 0.90),
    ("Continuous Beams (mid span)", "Compression zone", 20): (0.55, 0.55),
    ("Continuous Beams (mid span)", "Precompressed tensile zone", 2): (1.05, 1.15),
    ("Continuous Beams (mid span)", "Precompressed tensile zone", 20): (0.65, 0.70),
    ("Continuous Beams (end span)", "Compression zone", 2): (0.75, 0.80),
    ("Continuous Beams (end span)", "Compression zone", 20): (0.70, 0.70),
    ("Continuous Beams (end span)", "Precompressed tensile zone", 2): (1.10, 1.20),
    ("Continuous Beams (end span)", "Precompressed tensile zone", 20): (0.70, 0.70),
    ("Continuous Beams (intermediate support area)", "Compression zone", 2): (0.70, 0.75),
    ("Continuous Beams (intermediate support area)", "Compression zone", 20): (0.85, 0.85),
    ("Continuous Beams (intermediate support area)", "Precompressed tensile zone", 2): (1.10, 1.15),
    ("Continuous Beams (intermediate support area)", "Precompressed tensile zone", 20): (0.80, 0.85),
}

def get_lambda1_rail(beam_type, zone_type, span_length, traffic):
    """Lambda1 계수 계산 (로그 보간 적용)
    """
    # 기준점 설정
    k1 = (beam_type, zone_type, 2)
    k2 = (beam_type, zone_type, 20)

    # 테이블에서 값 추출
    s1, h1 = lambda1_table.get(k1, (None, None))
    s2, h2 = lambda1_table.get(k2, (None, None))

    # 값이 없으면 None 반환
    if s1 is None or s2 is None:
        return None

    is_heavy = traffic == "Heavy traffic"
    print("span_length =", span_length, type(span_length))
    # 경계 조건
    if float(span_length) <= 2:
        return h1 if is_heavy else s1
    elif float(span_length) >= 20:
        return h2 if is_heavy else s2
    else:
        # 로그 보간: log10(span) 기준
        logL = math.log10(span_length)
        log2 = math.log10(2)
        log20 = math.log10(20)
        ratio = (logL - log2) / (log20 - log2)

        if is_heavy:
            return h1 + (h2 - h1) * ratio
        else:
            return s1 + (s2 - s1) * ratio



# 
if __name__ == "__main__":
    # print(get_lambda1_rail("simply", "compression", 75, "heavy"))  
    pass
