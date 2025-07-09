# calc/fatigue_prestressing_steel_desm_rail_design.py # 1992-2- annex NN3
import pandas as pd
import math
from projects.concrete_fatigue_analysis_ntc2018.calc.railway_prestressing_steel_lambda import *
import streamlit as st

def make_general_settings_df_prestressing_steel_rail(data):
    """일반 설정값 데이터프레임 생성"""
    return pd.DataFrame([data])

def make_input_df_prestressing_steel_rail(case_id, method, inputs):
    """입력 데이터 데이터프레임 생성"""
    df = pd.DataFrame([inputs])
    df["case_id"] = case_id
    df["method"] = method
    return df

def update_lambda1_prestressing_steel_rail(inputs, temp_result_df, temp_input_df=None):
    """Lambda1 계수 계산 및 업데이트"""
    case_id = inputs["case_id"]
    
    # 계산에 필요한 값 가져오기
    support_type = inputs.get("support_type", "Simply supported beams")
    steel_type = inputs.get("steel_type", "Straight and bent bars")
    span_length = inputs.get("span_length", 35.0)
    traffic_type = inputs.get("traffic_type", "Standard traffic")
    
    # lambda1 계산
    lambda1 = get_lambda1_rail(support_type, steel_type, span_length, traffic_type)
    
    # 결과 저장
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda1"] = lambda1
    return temp_result_df

def update_lambda2_prestressing_steel_rail(inputs, temp_result_df, temp_input_df=None):
    """Lambda2 계수 계산 및 업데이트"""
    case_id = inputs["case_id"]
    
    # 필요한 값 가져오기
    vol = inputs.get("vol", 100000)  # 연간 통과 톤수
    steel_type = inputs.get("steel_type", "Straight and bent bars")
    
    # k2 값 가져오기 (S-N 곡선 지수)
    k2 = get_k2_value_rail(steel_type)
    
    # lambda2 계산 (올바른 공식 사용)
    lambda2 = calculate_lambda2_rail(vol, k2)
    
    # 결과 저장
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda2"] = lambda2
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "k2"] = k2  # k2 값도 저장
    
    return temp_result_df
def update_lambda3_prestressing_steel_rail(inputs, temp_result_df, temp_input_df=None):
    """Lambda3 계수 계산 및 업데이트"""
    case_id = inputs["case_id"]
    
    # 필요한 값 가져오기
    nyear = inputs.get("nyear", 50)  # 설계 수명
    steel_type = inputs.get("steel_type", "Straight and bent bars")
    
    # k2 값 가져오기
    k2 = get_k2_value_rail(steel_type)
    
    # lambda3 계산 (올바른 공식 사용)
    lambda3 = calculate_lambda3_rail(nyear, k2)
    
    # 결과 저장
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda3"] = lambda3
    
    return temp_result_df

def update_lambda4_prestressing_steel_rail(inputs, temp_result_df, temp_input_df=None):
    """Lambda4 계수 계산 및 업데이트"""
    case_id = inputs["case_id"]
    
    # 필요한 값 가져오기
    delta_sigma_1 = inputs.get("delta_sigma_1", 0.0)
    delta_sigma_12 = inputs.get("delta_sigma_12", 0.0)
    nc = inputs.get("nc", 2)
    nt = inputs.get("nt", 1)
    steel_type = inputs.get("steel_type", "Straight and bent bars")
    
    # k2 값 가져오기
    k2 = get_k2_value_rail(steel_type)
    
    # lambda4 계산 (올바른 공식 사용)
    lambda4 = calculate_lambda4_rail(delta_sigma_1, delta_sigma_12, nc, nt, k2)
    
    # 결과 저장
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda4"] = lambda4
    
    return temp_result_df

def update_lambda_s(inputs, temp_result_df, temp_input_df=None):
    """총 등가 계수 Lambda_s 계산 및 업데이트"""
    case_id = inputs["case_id"]
    
    # lambda1~4 값 가져오기
    lambda1 = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda1"].values[0]
    lambda2 = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda2"].values[0]
    lambda3 = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda3"].values[0]
    lambda4 = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda4"].values[0]
    
    # lambda_s 계산 (총 보정계수)
    lambda_s = lambda1 * lambda2 * lambda3 * lambda4
    
    # 결과 저장
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda_s"] = lambda_s
    return temp_result_df

def update_delta_sigma_equ_prestressing_steel_rail(inputs, temp_result_df, temp_input_df=None):
    """등가 응력 범위 계산 및 업데이트"""
    case_id = inputs["case_id"]
    
    # 필요한 값 가져오기
    try:
        lambda_s = temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda_s"].values[0]
    except:
        lambda_s = inputs.get("lambda_s", 0.0)
    delta_sigma_1 = inputs.get("delta_sigma_1", 0.0) 
    section_type = inputs.get("section_type",)
    
    # # 단면 상태에 따른 등가 응력 범위 계산
    # if section_type == "Uncracked section":
    #     delta_sigma_equ = lambda_s * delta_sigma_1
    # else:  # Cracked section
    #     delta_sigma_equ = lambda_s * delta_sigma_1 * 5  # 균열 단면에 대한 보정계수 5

    if st.session_state.get('section_type', '') == 'Cracked section' :
        delta_sigma_equ = 0
    else:
        delta_sigma_equ = delta_sigma_1




    # 결과 저장
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "delta_sigma_equ"] = delta_sigma_equ
    return temp_result_df

def update_delta_sigma_Rsk_prestressing_steel_rail(inputs, temp_result_df, temp_input_df=None):
    """기준 응력 범위 정보 업데이트"""
    case_id = inputs["case_id"]
    
    # 강재 유형
    steel_type = inputs.get("steel_type", "Straight and bent bars")
    
    # 기준 응력 범위 가져오기
    delta_sigma_Rsk = get_stress_range_rail(steel_type)
    
    # temp_result_df에 결과 저장
    temp_result_df.loc[temp_result_df["case_name"] == case_id, "delta_sigma_Rsk"] = delta_sigma_Rsk
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "delta_sigma_Rsk"] = delta_sigma_Rsk
    # 🔧 중요: session_state에도 값 저장
    st.session_state.delta_sigma_Rsk = delta_sigma_Rsk
    
    return temp_result_df

def calculate_verification_prestressing_steel_rail(inputs, temp_result_df, general=None):
    """철강 피로 최종 판정 계산"""
    case_id = inputs["case_id"]
    
    # 필요한 값 가져오기
    delta_sigma_equ = temp_result_df.loc[temp_result_df["case_id"] == case_id, "delta_sigma_equ"].values[0]
    delta_sigma_Rsk = temp_result_df.loc[temp_result_df["case_id"] == case_id, "delta_sigma_Rsk"].values[0]
    
    # 안전계수 가져오기
    if general is not None and 'factor_rsfat' in general.iloc[0]:
        gamma_fat = general.iloc[0]['factor_rsfat']
    else:
        gamma_fat = inputs.get("factor_rsfat", 1.15)
    
    if general is not None and 'factor_rf' in general.iloc[0]:
        gamma_F = general.iloc[0]['factor_rf']
    else:
        gamma_F = inputs.get("factor_rf", 1.0)
    lambda_s =  temp_result_df.loc[temp_result_df["case_id"] == case_id, "lambda_s"].values[0] 
    # 기본값
    gamma_fat = st.session_state.factor_rsfat
    gamma_F = st.session_state.factor_rf
    gamma_Sd = st.session_state.factor_rsd
    n_cables = st.session_state.get('n_steel', 1.0)
    A_cable = st.session_state.get('A_steel', 98.7)
    Msd = st.session_state.get('Msd', 0.0)    
    d = st.session_state.get('d', 0.0)
    # 판정식: γF·γSd·Δσs,equ ≤ ΔσRsk/γs,fat
    if st.session_state.section_type == "Non-cracked section":
         left_side = gamma_F * gamma_Sd * delta_sigma_equ * lambda_s
    else:  # 균열 단면
        delta_sigma_equ = (Msd * 1e6) / (d * n_cables * A_cable)
        left_side = (Msd * 1e6) / (d * n_cables * A_cable) * lambda_s  * gamma_F * gamma_Sd 

    right_side = delta_sigma_Rsk / gamma_fat
    
    # 판정 결과
    is_ok = left_side <= right_side
    
    # 판정값 (discriminant)
    discriminant_steel = right_side - left_side
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "delta_sigma_equ"] = delta_sigma_equ
    # 결과 저장
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "gamma_fat"] = gamma_fat
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "gamma_F"] = gamma_F
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "gamma_Sd"] = gamma_Sd
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "left_side"] = left_side
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "right_side"] = right_side
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "is_steel_ok"] = is_ok
    temp_result_df.loc[temp_result_df["case_id"] == case_id, "discriminant_steel"] = discriminant_steel
    
    return temp_result_df

# 테스트 코드
# if __name__ == "__main__":
    # case_id = "case_001"
    # method = "steel_fatigue"
    
    # # 일반 설정
    # general = make_general_settings_df({
    #     "bridge_type": "railway_bridge",
    #     "factor_rcfat": 1.5,
    #     "factor_rsfat": 1.15,
    #     "factor_rspfat": 1.15,
    #     "factor_rf": 1.0
    # })
    
    # # 입력 데이터
    # input_data = {
    #     "case_id": case_id,
    #     "case_name": "Steel Fatigue Test",
    #     "steel_type": "Straight and bent bars",
    #     "span_length": 35.0,
    #     "delta_sigma_1": 60.0,
    #     "delta_sigma_12": 70.0,
    #     "section_type": "Uncracked section",
    #     "support_type": "Simply supported beams",
    #     "traffic_type": "Standard traffic",
    #     "nyear": 50,
    #     "vol": 100000,
    #     "nc": 2,
    #     "nt": 1,
    #     "Es": 1.95e5,
    #     "Ec": 3.7e4,
    #     "A_steel": 98.7,
    #     "n_steel": 44,
    #     "d": 2700,
    #     "factor_rsfat": 1.15,
    #     "factor_rf": 1.0
    # }
    
    # # 입력 데이터프레임
    # temp_input_df = make_input_df(case_id, method, input_data)
    
    # # 결과 데이터프레임 초기화
    # temp_result_df = pd.DataFrame([{"case_id": case_id}])
    
    # # 계산 단계별 실행
    # temp_result_df = update_lambda1(input_data, temp_result_df)
    # temp_result_df = update_lambda2(input_data, temp_result_df)
    # temp_result_df = update_lambda3(input_data, temp_result_df)
    # temp_result_df = update_lambda4(input_data, temp_result_df)
    # temp_result_df = update_lambda_s(input_data, temp_result_df)
    # temp_result_df = update_delta_sigma_equ(input_data, temp_result_df)
    # temp_result_df = update_delta_sigma_Rsk(input_data, temp_result_df)
    # temp_result_df = calculate_verification(input_data, temp_result_df, general)
    
    # # 결과 출력
    # print(temp_input_df)
    # print("\nResults:")
    # print(temp_result_df)