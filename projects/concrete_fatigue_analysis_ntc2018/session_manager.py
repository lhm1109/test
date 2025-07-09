# session_manager.py
import streamlit as st
import pandas as pd
from streamlit.components.v1 import html
import requests
import json
import math
from projects.concrete_fatigue_analysis_ntc2018.calc.section_calculate import fetch_and_process_section_data
from typing import Optional, Dict, Any, Tuple
import time
from datetime import datetime
import io

# PageManager 네비게이션 import
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from projects.concrete_fatigue_analysis_ntc2018.utils.navigator import navigate_to_page_by_method


def initialize_session():

    """Initialize all required session state variables with default values."""
    # Initialize DataFrames if they don't exist
    if 'temp_result_df' not in st.session_state:
        st.session_state.temp_result_df = pd.DataFrame()
    
    if 'result_df' not in st.session_state:
        st.session_state.result_df = pd.DataFrame()
    
    # Construction Stage 데이터용 데이터프레임 추가
    if 'civil_result_conststage_df' not in st.session_state:
        st.session_state['civil_result_conststage_df'] = pd.DataFrame()
    
    # del_data 파라미터 기본값 설정
    if 'conststage_del_data' not in st.session_state:
        st.session_state['conststage_del_data'] = 0
    if 'section_properties_df' not in st.session_state:
        st.session_state['section_properties_df'] = pd.DataFrame()



    # Set default values for all required fields 변수추가시 여기도 초기값
    default_values = {
        'sigma_s': 0.0,
        'get_total_area': 0.0,
        'get_girder_centroid_height': 0.0,
        'get_total_centroid_height': 0.0,
        'get_girder_height': 0.0,
        'get_total_height': 0.0,
        'area': 0.0,
        'get_slab_d': 0.0,
        'get_effective': 0.0,
        'get_d': 0.0,
        'get_bw': 0.0,
        'get_Qn': 0.0,
        'get_J': 0.0,
        'sigma_s_equ'   : 0.0,  
        'sigma_s_rsk'   : 180,  
        'traffic_category': "Standard",  
        'traffic_type_steel': "Type 1",
        'pavement_roughness':"Good",
        'import_option': True,
        'api_connected': False,
        'nobs':1e6,
        'qmk': 500,
        'crack_option': True,  # 기본값 설정
        'manual_input2': True,  # 필요시 수정
        'final_element': "0",
        'fck': 20.0,
        'fcd': 13.3,
        'scmax_fcd': 0.0,
        'scmin_fcd': 0.0,
        'is_ok': "N/A",
        'next_error': False,
        'bridge_type': '',
        'case_name': 'new case',
        'design_factor': 1.0,
        'Fatigue_method': '',
        'stress': 3.0,
        'fatigue_case_method': 'ccs',
        'edit_mode': False,  # 편집 모드 플래그
        # 디자인 파라미터 기본값 추가
        'factor_rcfat': 1.5,
        'factor_rsfat': 1.15,
        'factor_rspfat': 1.15,
        'factor_rf': 1.00,
        'factor_rsd': 1.00, #Partial  factor  associated  with  the  uncertainty  of the  action  and/or action effect model 
        # railway concrete desm 
        'scmax71' : 0.00,
        'scmax' : 0.0,
        'scmin' : 0.0,
        'scperm' : 0.00,
        'ds1' : 0.0,
        'ds12' : 0.0,
        'fcd' : 13.3,
        'nyear' : 50,
        'temp_nyear' : 50,  # 임시 값 초기화
        'vol' : 100000,
        'nc' : 2.0,
        'nt' : 1.0,
        'sp' : "Simply Supported Beams", 
        'az' : "Compression zone", 
        'tt' : "Standard traffic", 
        'lambda0' : 0.0,
        'lambda1' : 0.0,
        'lambda2' : 0.0,
        'lambda3' : 0.0,
        'lambda4' : 0.0,
        'element_number' : 0,
        'discriminant_rail_des': 0.0,
        # 임시 값 초기화
        # Steel fatigue design 관련 변수들
        'steel_type': 'Straight and bent bars',
        'delta_sigma_1': 0.0,
        'delta_sigma_12': 0.0,
        'lambda_s': 0.0,
        'delta_sigma_equ': 0.0,
        'delta_sigma_Rsk': 180,
        'section_type': '',
        'Es': 1.95e5,
        'Ec': 3.7e4,
        'A_steel': 98.7,
        'n_steel': 44,
        'support_type_road': 'Continuous Beam',
        'support_type_rail': 'Simply supported beams',
        'discriminant_steel': 0.0,
        # Steel Girder 피로 계산을 위한 추가 변수들
        'delta_sigma1': 0.00,          # 단일 열차 통과시 철골 직접 응력 (MPa)
        'delta_sigma12': 0.00,         # 두 열차 통과시 철골 직접 응력 (MPa)
        'delta_sigma_amm': 0.00,       # 2백만 사이클에서 직접 응력 피로 강도 (MPa)
        'delta_tau_amm': 100,          # 2백만 사이클에서 전단 응력 피로 강도 (MPa)
        'tau1': 0.00,                  # 단일 열차 통과시 전단 응력 (MPa)
        'tau12': 0.00,                  # 두 열차 통과시 전단 응력 (MPa)
        'Vs1': 0.00,                  # 단일 열차 통과시 전단력 (kN)
        'Vs12': 0.00,                 # 두 열차 통과시 전단력 (kN)
        'bw': 200,                     # 웹 두께 (mm)
        'J': 1090000000000,             # 단면 2차 모멘트 (mm⁴)
        'H': 2300.0,                    # 단면 높이 (mm)
        'Qn': 181000000,              # 첫 번째 면적 모멘트 (mm³)
        'annual_traffic': 25.0,         # 연간 교통량 (백만 톤/년)
        'design_life': 50,              # 설계 수명 (년)
        'traffic_category_road': "Standard", # 교통 카테고리 (Standard, Metropolitan, Heavy)
        'traffic_type_road': "Long distance",     # 교통 유형
        'traffic_type_rail': 'Standard traffic',  
        'traffic_type_steel': 'Mixed EC',  
        'calc_lambda1': 0.00,           # 람다1 계산값 
        'calc_lambda2': 0.00,            # 람다2 계산값
        'calc_lambda3': 0.00,           # 람다3 계산값
        'calc_lambda4': 0.00,           # 람다4 계산값
        'calc_lambda_s': 0.00,          # 람다_s 계산값 
        'lambda_max': 0.00,              # 최대 람다 값
        'lambda_check': "N/A",           # 람다 체크 결과
        'delta_sigma_equ': 0.0,         # 등가 직접 응력 범위
        'delta_tau_equ': 0.0,           # 등가 전단 응력 범위
        'delta_sigma_rsk': 180,       # 설계 직접 응력 피로 강도
        'delta_tau_rsk': 100,          # 설계 전단 응력 피로 강도
        'direct_stress_ratio': 0.0,     # 직접 응력 비율
        'shear_stress_ratio': 0.0,      # 전단 응력 비율
        'direct_stress_check': "N/A",   # 직접 응력 체크 결과
        'shear_stress_check': "N/A",    # 전단 응력 체크 결과
        'overall_check': "N/A",         # 전체 체크 결과
        'shear_calc_method': "Calculate from section properties", # 전단 계산 방법
        'correction_factor_auto_calculate': True,  # 보정 계수 자동 계산 여부
        'span_length': 35.00,            # 스팬 길이
        # road noncracked stress 관련 변수들
        'temp_sctraz': 0.0,             # σc,traz 임시 값
        'temp_element_number_sctraz': '', # σc,traz 요소 번호 임시 값
        'temp_element_number_ds1': '', # ds1 요소 번호 임시 값
        'temp_element_number_ds12': '', # ds12 요소 번호 임시 값
        #모멘트
        'temp_Msd': 0,
        'Msd': 0,
        'detail_category': '160',
        #스틸거더
        'factor_rm': 1.35,
        'direct_stress_ratio': 0.0,
        'steel_type': 'Straight and bent bars',
        'error_condition': False,
        'p_staffe': 10,
        'd_mandrel': 40,
        'reduction_factor': 1.0,
        'get_total_area': 0.0,
        'get_total_first_moment': 0.0,
        'get_iyy_total': 0.0,
        'get_total_centroid_height': 0.0,
        'get_girder_centroid_height': 0.0,
        'get_girder_height': 0.0,
        'get_total_height': 0.0,
        'get_slab_height': 0.0,
        'get_bw': 0.0,
        'get_Qn': 0.0,
        'get_J': 0.0,
        'fctd': 0.0,
        'fb': 0.0,
        'sctraz': 0.0,
        'stress_left': 0.0,
        'stress_right': 0.0,
        'is_cracked_section': False,
        'Vsdmax': 0.00,  # 최대 전단력
        'Vsdmin': 0.00,  # 최소 전단력
        'get_d' : 0.0,  # 단면 높이
        'get_bw' : 0.0,  # 슬래브 높이                        'get_bw', 'get_Qn', 'get_J', 'get_d',
        'get_Qn' : 0.0,  # 첫 번째 면적 모멘트
        'get_J' : 0.0,  # 단면 2차 모멘트

    }

    
    # 빈 문자열 문제 해결: fatigue_case가 있고 빈 문자열이면 제거
    if 'fatigue_case' in st.session_state and st.session_state.fatigue_case == '':
        del st.session_state.fatigue_case

    # Apply default values
    set_default_values(default_values)
    
    # 편집 모드인 경우, temp_result_df의 값을 세션 상태로 복원
    if st.session_state.edit_mode and not st.session_state.temp_result_df.empty:
        # temp_result_df의 첫 번째 행에서 기본 필드 값을 가져옴
        row = st.session_state.temp_result_df.iloc[0]
        for key in ['case_name', 'design_factor', 'stress', 'Fatigue_method']:
            if key in row:
                st.session_state[key] = row[key]
    # 편집 모드가 아니고 temp_result_df가 비어있는 경우에만 초기화 변수추가시 여기도
    elif st.session_state.temp_result_df.empty and not st.session_state.edit_mode:
        st.session_state.temp_result_df = pd.DataFrame([{
            'case_name': st.session_state.case_name,
            'design_factor': st.session_state.design_factor,
            'stress': st.session_state.stress,
            'Fatigue_method': st.session_state.Fatigue_method,
            'bridge_type': st.session_state.bridge_type,
            'factor_rcfat': st.session_state.factor_rcfat,
            'factor_rsfat': st.session_state.factor_rsfat,
            'factor_rspfat': st.session_state.factor_rspfat,
            'factor_rf': st.session_state.factor_rf,
            'factor_rm': st.session_state.factor_rm
        }])
def update_temp_with_all_params():
    """모든 중요 파라미터로 temp_result_df 업데이트"""
    # 기존 temp_result_df 확인
    if 'temp_result_df' not in st.session_state or st.session_state.temp_result_df.empty:
        st.session_state.temp_result_df = pd.DataFrame([{}])
    
    # 기본 필드들
    basic_params = {
        'case_name': st.session_state.case_name,
        'design_factor': st.session_state.design_factor,
        'stress': st.session_state.stress,
        'Fatigue_method': st.session_state.Fatigue_method,
        'bridge_type': st.session_state.bridge_type,
        'factor_rcfat': st.session_state.factor_rcfat,
        'factor_rsfat': st.session_state.factor_rsfat,
        'factor_rspfat': st.session_state.factor_rspfat,
        'factor_rf': st.session_state.factor_rf,
        'factor_rm': st.session_state.factor_rm
    }
    
    # temp_result_df에 업데이트
    for key, value in basic_params.items():
        st.session_state.temp_result_df.at[0, key] = value
    
    return st.session_state.temp_result_df



def update_temp_from_input_multi(keys):
    """Update multiple keys in the temp_result_df from session state."""
    # Ensure temp_result_df exists and has at least one row
    if 'temp_result_df' not in st.session_state or st.session_state.temp_result_df.empty:
        st.session_state.temp_result_df = pd.DataFrame([{}])
    
    # Update each specified key
    for key in keys:
        if key in st.session_state:
            st.session_state.temp_result_df.at[0, key] = st.session_state[key]

def select_bridge_type(bridge_type):
    """교량 타입 선택 시 세션 상태 업데이트"""
    st.session_state.bridge_type = bridge_type
    
    # temp_result_df에도 값 추가
    update_temp_from_input('bridge_type')
    
    return bridge_type
     
def update_design_factors():
    """디자인 파라미터 임시 값에서 세션 상태로 업데이트"""
    st.session_state.factor_rcfat = st.session_state.temp_rcfat
    st.session_state.factor_rsfat = st.session_state.temp_rsfat
    st.session_state.factor_rspfat = st.session_state.temp_rspfat
    st.session_state.factor_rf = st.session_state.temp_rf
    st.session_state.factor_rm = st.session_state.temp_rm
    st.session_state.factor_rsd = st.session_state.temp_rsd
    st.session_state.nyear = st.session_state.temp_nyear
    # temp_result_df에도 값 추가
    update_temp_from_input_multi([
        'factor_rcfat', 'factor_rsfat', 'factor_rspfat', 'factor_rf', 'factor_rm', 'nyear', 'factor_rsd'
    ])
def update_verification_options(options):
    """
    verification_options 업데이트 및 temp_result_df의 direct/shear 플래그 설정
    
    Args:
        options (list): 선택된 검증 옵션 목록
    """
    # 세션 상태에 verification_options 업데이트
    st.session_state.verification_options = options
    
    # temp_result_df가 존재하고 비어있지 않다면 direct/shear 플래그 업데이트
    if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
        st.session_state.temp_result_df.at[0, 'direct'] = "Direct Stress" in options
        st.session_state.temp_result_df.at[0, 'shear'] = "Shear Stress" in options


def update_temp_from_input(widget_key, state_key=None):
    if state_key is None:
        state_key = widget_key
    
    value = st.session_state.get(widget_key, "")
    
    # 이전 값을 별도 키로 저장해서 비교
    old_value_key = f"{state_key}_prev"
    old_value = st.session_state.get(old_value_key, None)
    
    if old_value != value:
        st.session_state['calculation_valid'] = False
        st.session_state['input_changed'] = True
    
    # 현재 값을 이전 값 키에 저장 (다음번 비교용)
    st.session_state[old_value_key] = value
    
    # 나머지 로직...
    if 'temp_result_df' not in st.session_state:
        st.session_state.temp_result_df = pd.DataFrame([{state_key: value}])
    elif st.session_state.temp_result_df.empty:
        st.session_state.temp_result_df = pd.DataFrame([{state_key: value}])
    else:
        st.session_state.temp_result_df.loc[0, state_key] = value
    
    st.session_state[state_key] = value
# def update_temp_from_input(widget_key, state_key=None):
#     """위젯의 값을 session_state와 temp_result_df에 업데이트"""
#     if state_key is None:
#         state_key = widget_key
    
#     value = st.session_state.get(widget_key, "")
    
#     # Ensure temp_result_df exists and has at least one row
#     if 'temp_result_df' not in st.session_state:
#         st.session_state.temp_result_df = pd.DataFrame([{state_key: value}])
#     elif st.session_state.temp_result_df.empty:
#         st.session_state.temp_result_df = pd.DataFrame([{state_key: value}])
#     else:
#         # Update the existing dataframe
#         st.session_state.temp_result_df.loc[0, state_key] = value
    
#     # Also update the session state value to keep them in sync
#     st.session_state[state_key] = value
    
#     # 빈 문자열 문제 해결: 특별히 fatigue_case에 대한 처리
#     if state_key == 'fatigue_case' and value == '':
#         del st.session_state.fatigue_case

def set_default_values(defaults: dict):
    """Set default values for session state variables if they don't exist."""
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def add_tab_switch_button(label, target_tab_text):
    """Add a button to switch to a different tab using JavaScript."""
    html(f"""<script>
        const tabButtons = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
        const btn = Array.from(tabButtons).find(el => el.innerText === "{target_tab_text}");
        if (btn) {{
            btn.click();
        }}
    </script>""", height=0)

def save_to_result_df():
    """Save the current temp_result_df to the result_df."""
    if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
        if 'result_df' not in st.session_state:
            st.session_state.result_df = pd.DataFrame()
        
        # Ensure case_id is present
        if 'case_id' not in st.session_state.temp_result_df.columns and 'case_name' in st.session_state.temp_result_df.columns:
            st.session_state.temp_result_df['case_id'] = st.session_state.temp_result_df['case_name']
        
        # 편집 모드인 경우, 기존 데이터를 업데이트
        if st.session_state.get('edit_mode', False) and 'fatigue_case_name' in st.session_state:
            # 기존 행 찾기
            mask = st.session_state.result_df['case_id'] == st.session_state.fatigue_case_name
            if any(mask):
                # 기존 행 제거
                st.session_state.result_df = st.session_state.result_df[~mask]
                # temp_result_df 추가
                st.session_state.result_df = pd.concat([st.session_state.result_df, st.session_state.temp_result_df], 
                                                   ignore_index=True)
                st.session_state.edit_mode = False  # 편집 모드 끄기
                st.session_state.pop('fatigue_case_name', None)  # 불필요한 상태 제거
            else:
                # 편집할 행을 찾지 못함 - 새 행으로 추가
                st.session_state.result_df = pd.concat([st.session_state.result_df, st.session_state.temp_result_df], 
                                                   ignore_index=True)
        else:
            # 일반 추가 모드
            st.session_state.result_df = pd.concat([st.session_state.result_df, st.session_state.temp_result_df], 
                                               ignore_index=True)
        
        # Clear temp_result_df
        st.session_state.temp_result_df = pd.DataFrame()
        return True
    return False

# 테이블 관리 및 세션 상태 동기화를 개선한 코드

# session_manager.py에 추가할 상수 정의
BASIC_FIELDS = ['case_name', 'design_factor', 'stress', 'Fatigue_method']

ADDITIONAL_FIELDS = [
    'fcm', 'span_length', 'scmax71', 'scperm', 'ds1', 'ds12', 
    'nyear', 'vol', 'nc', 'sp', 'az', 'tt', 'lambda0', 'lambda1', 
    'lambda2', 'lambda3', 'lambda4', 'element_number', 'd','import_option'
]

NUMERIC_FIELDS = [
    'fck', 'fcm', 'span_length', 'scmax71', 'scperm', 'ds1', 'ds12', 
    'nyear', 'vol', 'lambda0', 'lambda1', 'lambda2', 'lambda3', 
    'lambda4', 'element_number', 'design_factor', 'stress',
    'discriminant', 'fcd', 'is_ok', 'Tmax', 'Tmin', 'TRd1', 'Tmax_TRd1', 'Tmin_TRd1', 'discriminant'
]

INTEGER_FIELDS = ['nc', 'nt']

# 테이블 표시에 사용할 컬럼 매핑
COLUMN_MAPPING = {
    'case_id': 'Name',
    'case_method': 'Analysis Method',
    'discriminant': 'Safety Factor ',  #판정값 안전율
    'is_ok': 'Safety Factor ',  #판정값 안전율
    # 'fcm': '콘크리트 강도',
    # 'fcd': '설계 강도'
    # 필요한 다른 컬럼 매핑 추가
}

table_show_columns = ['case_method', 'is_ok']


# 수정된 load_data_for_edit 함수
def load_data_for_edit(case_id):
    """지정된 case_id의 데이터를 temp_result_df에 로드하고 편집 모드 설정"""
    if 'result_df' not in st.session_state or st.session_state.result_df.empty:
        return False
    
    # case_id로 데이터 필터링
    case_data = st.session_state.result_df[st.session_state.result_df['case_id'] == case_id]
    
    if not case_data.empty:
        # temp_result_df에 전체 데이터 복사 (모든 컬럼 포함)
        st.session_state.temp_result_df = case_data.copy().reset_index(drop=True)
        
        # 편집 모드 설정
        st.session_state.edit_mode = True
        st.session_state.fatigue_case_name = case_id
        
        # 첫 번째 행의 데이터 가져오기
        row_data = case_data.iloc[0].to_dict()
        
        # 모든 세션 상태 변수를 복원
        for key, value in row_data.items():
            if key == 'case_id':
                continue  # case_id는 특별 처리
            
            try:
                # NaN 값 처리
                if pd.isna(value):
                    if key in ['discriminant_rail_des', 'fcd', 'delta_sigma_rsk', 'delta_tau_rsk', 
                            'direct_stress_ratio', 'shear_stress_ratio', 'discriminant']:
                        st.session_state[key] = 0.0
                    elif key in ['crack_option', 'manual_input2', 'correction_factor_auto_calculate', 
                                'manual_input', 'edit_mode', 'vol_auto_calculate', 'import_option']:
                        st.session_state[key] = False  # boolean 기본값
                    elif key in ['case_name', 'Fatigue_method', 'bridge_type']:
                        st.session_state[key] = str(value) if not pd.isna(value) else ""
                    else:
                        st.session_state[key] = value
                else:
                    # 데이터 타입에 따른 변환 저장한값 불러오기
                    if key in ['fck', 'factor_rcfat', 'factor_rsfat', 'factor_rspfat', 'factor_rf', 'factor_rm',
                            'fcm', 'fcd', 'span_length', 'scmax71', 'scperm', 'ds1', 'ds12',
                            'nyear', 'vol', 'lambda0', 'lambda1', 'lambda2', 'lambda3', 'lambda4',
                            'discriminant_rail_des', 'delta_sigma1', 'delta_sigma12', 'delta_sigma_amm',
                            'delta_tau_amm', 'tau1', 'tau12', 'annual_traffic', 'design_life',
                            'calc_lambda1', 'calc_lambda2', 'calc_lambda3', 'calc_lambda4',
                            'calc_lambda_s', 'lambda_max', 'delta_sigma_equ', 'delta_tau_equ',
                            'delta_sigma_rsk', 'delta_tau_rsk', 'direct_stress_ratio', 'shear_stress_ratio',
                            'Es', 'Ec', 'A_steel', 'n_steel', 'delta_sigma_1', 'delta_sigma_12']:
                        st.session_state[key] = float(value)
                    elif key in ['nc', 'nt', 'design_life']:
                        st.session_state[key] = int(value)
                    elif key in ['crack_option', 'manual_input2', 'correction_factor_auto_calculate', 
                                'manual_input', 'edit_mode', 'vol_auto_calculate', 'import_option']:
                        # boolean 값 처리 
                        if isinstance(value, (bool, int)):
                            st.session_state[key] = bool(value)
                        elif isinstance(value, str):
                            st.session_state[key] = value.lower() in ['true', '1', 'yes', 'on']
                        else:
                            st.session_state[key] = bool(value)
                    else:
                        st.session_state[key] = value
                        
            except (ValueError, TypeError) as e:
                # 변환 실패 시 기본값 사용
                if key in ['discriminant_rail_des', 'fcd']:
                    st.session_state[key] = 0.0
                else:
                    st.session_state[key] = value
        
        # 특별히 처리해야 하는 필드들
        if 'case_name' in row_data:
            st.session_state.case_name = str(row_data['case_name'])
        
        # 계산된 값들도 복원 (calc_ 접두사가 있는 값들)
        calc_fields = ['calc_lambda0', 'calc_lambda1', 'calc_lambda2', 'calc_lambda3', 'calc_lambda4',
                      'calc_lambdac', 'calc_lambda_s', 'calc_delta_sigma_rsk', 'calc_delta_tau_rsk',
                      'calc_direct_stress_ratio', 'calc_shear_stress_ratio', 'calc_delta_sigma_equ',
                      'calc_delta_tau_equ']
        
        for calc_field in calc_fields:
            if calc_field in row_data:
                try:
                    st.session_state[calc_field] = float(row_data[calc_field]) if not pd.isna(row_data[calc_field]) else 0.0
                except (ValueError, TypeError):
                    st.session_state[calc_field] = 0.0
        
        return True
    return False

# session_manager.py에서 display_analysis_result_table 함수 개선
#결과테이블블
def display_analysis_result_table(page_mappings=None):
    """결과 테이블을 표시하고 삭제/수정 기능을 제공하는 함수."""
    
    # 컨테이너로 테이블 영역 설정 (높이 고정)
    table_container = st.container()
    
    with table_container:
      
        # 테이블 컨테이너 (고정 높이)
        # table_height = 634  # 픽셀 단위 로드
        table_height = 675  # 픽셀 단위 레일
        # CSS로 높이 고정
        st.markdown(f"""
        <style>
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {{
            max-height: {table_height}px;
            overflow-y: auto;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # 테이블 영역을 고정 높이 컨테이너로 생성
        with st.container(height=table_height-150, border=True):
            if 'result_df' not in st.session_state or len(st.session_state.result_df) == 0:
                # # 빈 테이블일 때도 형상 유지
                # st.markdown("""
                #     <div style="
                #         display: flex; 
                #         align-items: center; 
                #         justify-content: center; 
                #         height: 100%; 
                #         color: #888888;
                #         font-style: italic;
                #         text-align: center;
                #         padding: 50px;
                #     ">
                #         <div>
                #             <h4 style="color: #888888; margin-bottom: 10px;">📋 No Analysis Results</h4>
                #             <p>Please add a new fatigue analysis to see results here.</p>
                #         </div>
                #     </div>
                # """, unsafe_allow_html=True)
                
                # 빈 테이블 헤더만 표시 (구조 유지)
                empty_df = pd.DataFrame(columns=['Select', 'Name', 'Analysis Method', 'Safety Factor'])
                st.dataframe(
                    empty_df,
                    hide_index=True,
                    use_container_width=True,
                    height=50,  # 헤더만 보이도록 작은 높이
                    column_config={
                        "Select": st.column_config.CheckboxColumn(
                            "Select",
                            help="Select the case to delete or edit",
                            default=False
                        )
                    }
                )
            else:
                try:
                    # 표시할 컬럼 선택 (존재하는 컬럼만)
                    display_columns = ['case_id']
                    
                    # 'case_method' 컬럼이 없는 경우 'Fatigue_method'를 'case_method'로 복사
                    if 'case_method' not in st.session_state.result_df.columns and 'Fatigue_method' in st.session_state.result_df.columns:
                        st.session_state.result_df['case_method'] = st.session_state.result_df['Fatigue_method']
                    
                    for col in table_show_columns:
                        if col in st.session_state.result_df.columns:
                            display_columns.append(col)
                    
                    # 존재하는 컬럼으로 데이터프레임 생성
                    analysis_case_dataframe = pd.DataFrame(st.session_state.result_df[display_columns])
                    
                    # 컬럼명 변경 (존재하는 컬럼만)
                    rename_dict = {col: COLUMN_MAPPING.get(col, col) for col in display_columns if col in COLUMN_MAPPING}
                    analysis_case_dataframe.columns = [rename_dict.get(col, col) for col in analysis_case_dataframe.columns]
                    
                    # 체크박스 컬럼 추가 (다중 선택용)
                    analysis_case_dataframe.insert(0, 'Select', False)
                    
                    # 테이블 표시
                    edited_df = st.data_editor(
                        analysis_case_dataframe,
                        hide_index=True,
                        use_container_width=True,
                        height=table_height - 190,  # 테이블 자체 높이 설정 (버튼 영역 고려)
                        column_config={
                            "Select": st.column_config.CheckboxColumn(
                                "Select",
                                help="Select the case to delete or edit",
                                default=False
                            )
                        }
                    )
                    
                    # 선택한 항목들 저장
                    selected_rows = edited_df[edited_df['Select'] == True]
                    
                except Exception as e:
                    st.error(f"Error displaying results: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    selected_rows = pd.DataFrame()  # 에러 시 빈 DataFrame
        
        # 버튼 영역 - 테이블 컨테이너 외부에 배치하여 항상 표시
        # 결과가 있을 때만 선택 정보 표시
        # if 'result_df' in st.session_state and len(st.session_state.result_df) > 0:
        #     try:
        #         selected_count = len(selected_rows) if 'selected_rows' in locals() else 0
        #         total_count = len(st.session_state.result_df)
        #         st.markdown(f"**Analysis Cases**: {total_count} total, {selected_count} selected")
        #     except:
        #         st.markdown("**Analysis Cases**: Available")
        # else:
        #     st.markdown("**Analysis Cases**: 0 total, 0 selected")
        
        # 버튼 영역 - 항상 표시
        col1, col2, col3 = st.columns(3)
        
        # 결과가 있는지 확인
        has_results = 'result_df' in st.session_state and len(st.session_state.result_df) > 0
        has_selection = has_results and 'selected_rows' in locals() and not selected_rows.empty
        
        # 삭제 버튼
        with col1:
            delete_disabled = not has_selection
            if st.button("Delete", type="secondary", use_container_width=True, disabled=delete_disabled):
                if has_selection:
                    selected_cases = selected_rows['Name'].tolist() if 'Name' in selected_rows.columns else selected_rows['case_id'].tolist()
                    # Delete selected items
                    st.session_state.result_df = st.session_state.result_df[
                        ~st.session_state.result_df['case_id'].isin(selected_cases)
                    ]
                    st.rerun()
                else:
                    st.toast("No items selected for deletion")
        
        # Edit button
        with col2:
            edit_disabled = not has_selection
            if st.button("Edit", type="secondary", use_container_width=True, disabled=edit_disabled):
                if has_selection:
                    if len(selected_rows) > 1:
                        st.toast("Please select only one item to edit")
                    else:
                        selected_case = selected_rows.iloc[0]['Name'] if 'Name' in selected_rows.columns else selected_rows.iloc[0]['case_id']
                        
                        # Get all data for the selected case
                        case_data = st.session_state.result_df[st.session_state.result_df['case_id'] == selected_case]
                        
                        if not case_data.empty:
                            # Set edit mode
                            st.session_state.edit_mode = True
                            st.session_state.fatigue_case_name = selected_case
                            
                            # Find method
                            method_column = None
                            if 'case_method' in case_data.columns:
                                method_column = 'case_method'
                            elif 'Fatigue_method' in case_data.columns:
                                method_column = 'Fatigue_method'
                            
                            if method_column and page_mappings is not None:
                                method = case_data.iloc[0][method_column]
                                st.session_state.selected_method = method
                                # Find matching case_method
                                if method in page_mappings:
                                    # Load selected case data
                                    load_data_for_edit(selected_case)
                                    # Navigate to page
                                    print(f"Switching to page: {method}", page_mappings[method])
                                    navigate_to_page_by_method(method)
                                else:
                                    # Find page by partial match
                                    found = False
                                    for key, page_func in page_mappings.items():
                                        if key in method or method in key:
                                            # Load selected case data
                                            load_data_for_edit(selected_case)
                                            # Navigate to page
                                            print(f"Switching to page: {key}", page_func)
                                            navigate_to_page_by_method(key)
                                            found = True
                                            break
                                    
                                    if not found:
                                        st.error(f"No appropriate page mapping found: {method}")
                            else:
                                st.error("No analysis method found or page mapping is missing.")
                        else:
                            st.error(f"Selected case not found: {selected_case}")
                else:
                    st.toast("No items selected for editing")
        
        # Copy button
        with col3:
            copy_disabled = not has_selection
            if st.button("Copy", type="secondary", use_container_width=True, disabled=copy_disabled):
                if has_selection:
                    if len(selected_rows) > 1:
                        st.toast("Please select only one item to copy")
                    else:
                        selected_case = selected_rows.iloc[0]['Name'] if 'Name' in selected_rows.columns else selected_rows.iloc[0]['case_id']
                        
                        # Get selected case data
                        case_data = st.session_state.result_df[st.session_state.result_df['case_id'] == selected_case]
                        
                        if not case_data.empty:
                            # Create new case_id (copy)
                            new_case_id = f"{selected_case}_copy"
                            
                            # Add number if name exists
                            counter = 1
                            while new_case_id in st.session_state.result_df['case_id'].values:
                                new_case_id = f"{selected_case}_copy_{counter}"
                                counter += 1
                            
                            # Create new data
                            new_data = case_data.copy()
                            new_data['case_id'] = new_case_id
                            
                            # Add to dataframe
                            st.session_state.result_df = pd.concat([st.session_state.result_df, new_data], ignore_index=True)
                            
                            st.success(f"Case '{selected_case}' has been copied to '{new_case_id}'")
                            st.rerun()
                        else:
                            st.error(f"Selected case not found: {selected_case}")
                else:
                    st.toast("No items selected for copying")





# 모달 및 임포트 관련 함수들 ===============================

def initialize_import_state():
    """임포트 관련 세션 상태 초기화"""
    if 'civil_load_cases_data' not in st.session_state:
        st.session_state['civil_load_cases_data'] = []
    if 'load_cases_data' not in st.session_state:
        st.session_state['load_cases_data'] = {'load_case_list': []}
    
    # 임시 값 초기화
    for key in ['temp_scmax71', 'temp_scperm', 'temp_ds1', 'temp_ds12', 'temp_sctraz']:
        if key not in st.session_state:
            st.session_state[key] = 0
    
    for key in ['temp_Select_Elements', 'temp_Select_Elements2', 
                'temp_Select_Elements3', 'temp_Select_Elements4',
                'temp_element_number_scmax71', 'temp_element_number_scperm',
                'temp_element_number_sctraz', 'temp_element_number_ds1', 'temp_element_number_ds12']:
        if key not in st.session_state:
            st.session_state[key] = ''
    
    st.session_state.temp_state = True

def get_Select_Elements(session_key):
    """Midas Civil에서 요소 선택"""
    mapi_key = st.session_state.get('current_mapi_key', '')
    base_url = st.session_state.get('current_base_url', '')
    headers = {"MAPI-Key": mapi_key}
    
    try:
        select_Elements_request = requests.get(f"{base_url}/view/SELECT", headers=headers)
        selected_items = select_Elements_request.json()
        
        if selected_items != 0:
            if "SELECT" in selected_items and "ELEM_LIST" in selected_items["SELECT"]:
                Select_Elements = ','.join(str(x) for x in selected_items["SELECT"]["ELEM_LIST"])
                st.session_state[session_key] = Select_Elements
            else:
                Select_Elements = []
                st.session_state[session_key] = Select_Elements
    except Exception as e:
        st.session_state[f"error_{session_key}"] = f"Error selecting elements: {str(e)}"
        st.session_state[session_key] = ''
    
    return st.session_state.get(session_key, '')

def load_composit_stress_data(stress_type, elements_key, load_case_key, section_key, component_key, location_key, is_second=False):
    is_second = not is_second
    # API 설정 가져오기
    if stress_type == 'sctraz' or 'delta_sigma_1':
        is_second = False
    if stress_type == 'scmin' or 'scmax':
        is_second = True

    mapi_key = st.session_state.get('current_mapi_key', '')
    base_url = st.session_state.get('current_base_url', '')
    
    if not mapi_key or not base_url:
        st.session_state[f"error_{stress_type}"] = "API settings not found. Log in first."
        return
        
    headers = {"MAPI-Key": mapi_key}
    
    # 결과 저장 키 설정
    result_key = stress_type
    temp_result_key = f"temp_{stress_type}"
    
    # 선택된 요소 및 하중 케이스 가져오기
    try:
        selected_elements = [int(x) for x in st.session_state.get(elements_key, '').split(',') if x.strip()]
        if not selected_elements:
            st.session_state[f"error_{stress_type}"] = "No elements selected."
            return
        st.session_state[elements_key] = ','.join(map(str, selected_elements))
    except Exception as e:
        st.session_state[f"error_{stress_type}"] = f"Error processing selected elements: {str(e)}"
        return
    
    selected_load = st.session_state.get(load_case_key, '')
    selected_section = st.session_state.get(section_key, '')
    selected_component = st.session_state.get(component_key, '')
    selected_location = st.session_state.get(location_key, '')
    
    # civil_result_df 확인
    if 'civil_result_df' not in st.session_state:
        st.session_state[f"error_{stress_type}"] = "civil Data not found. Please check again in MIDAS Civil."
        return
        
    df = st.session_state.civil_result_df
    
    # 선택된 요소로 필터링
    df = df[df['Elem'].astype(int).isin(selected_elements)]
    
    if df.empty:
        st.session_state[f"error_{stress_type}"] = "Section not supported. Check again in MIDAS Civil."
        return
    
    # 선택된 하중 케이스로 필터링
    # 하중 케이스 형식 표준화 (괄호와 접두어 제거)
    selected_load_result = selected_load
    for prefix in ['CBC:', 'CB:', 'MV:', 'CBSM:', '(CB)', '(MV)', '(CBC)', '(CBSM)']:
        selected_load_result = selected_load_result.replace(prefix, '')
    
    df = df[df['Load'] == selected_load_result]

    
    if df.empty:
        st.session_state[f"error_{stress_type}"] = f"No data found for selected load case ({selected_load})."
        return
        
    # 섹션 파트 필터링
    if selected_section == "Part 1":
        df = df[df['Section Part'] == '1']
    elif selected_section == "Part 2": 
        df = df[df['Section Part'] == '2']
    
    if df.empty:
        st.session_state[f"error_{stress_type}"] = f"No data found for selected section part ({selected_section})."
        return
    
    # 응력 컬럼 처리
    stress_cols = ['Cb1(-y+z)', 'Cb2(+y+z)', 'Cb3(+y-z)', 'Cb4(-y-z)']
    
    # 응력 값을 숫자로 변환
    for col in stress_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            st.session_state[f"error_{stress_type}"] = f"Column '{col}' not found. Available columns: {list(df.columns)}"
            return
    
    # 선택된 컴포넌트에 따라 응력값 계산
    if selected_component == "Maximum":
        # 압축/인장에 따라 로직 변경
        # is_second=True: 압축응력 최대값 찾기 → 가장 작은 값(최소값) 선택
        # is_second=False: 인장응력 최대값 찾기 → 가장 큰 값(최대값) 선택
        if result_key == "sctraz" or result_key == "ds1" or result_key == "ds12" or result_key == "delta_sigma_1" or result_key == "delta_sigma_12"or result_key == "scperm":
            df['max_stress'] =df[stress_cols].max(axis=1)
        else:
            df['max_stress'] = df[stress_cols].max(axis=1) if not is_second else df[stress_cols].min(axis=1)

    elif selected_component == "1(-y, +z)":
        df['max_stress'] = df['Cb1(-y+z)']
    elif selected_component == "2(+y, +z)":
        df['max_stress'] = df['Cb2(+y+z)']
    elif selected_component == "3(+y, -z)":
        df['max_stress'] = df['Cb3(+y-z)']
    elif selected_component == "4(-y, -z)":
        df['max_stress'] = df['Cb4(-y-z)']
    else:
        st.session_state[f"error_{stress_type}"] = f"Unsupported component type: {selected_component}"
        return

    # 위치별 그룹화 및 필터링
    if selected_location != "Maximum" and selected_location != "Minimum":
        # 위치 필터링 (Part I, Part J, Part 1/4 등)
        location_part = selected_location.split()[-1]  # "Part I" -> "I" 추출
        df = df[df['Part'] == location_part]
        
        if df.empty:
            st.session_state[f"error_{stress_type}"] = f"No data found for selected location ({selected_location})."
            return
    # df.to_csv('./selected_load_result.csv', index=False)    
    # 최종 응력값 계산 - is_second 매개변수에 따라 최대/최소 결정
    # is_second=True는 압축응력의 최대값을 찾는 경우로 실제로는 최소값(min)을 찾아야 함
    try:
        # is_second 값에 따라 max/min 여부 결정
        if not is_second:
            # 인장 응력 최대값(양수 중 최대) 찾기
            final_value = df['max_stress'].max()
            max_index = df['max_stress'].idxmax()
            result_elem = df.loc[max_index, 'Elem'] if not pd.isna(max_index) else ""
        else:
            if result_key == "sctraz" or result_key == "ds1" or result_key == "ds12" or result_key == "scperm" or result_key == "delta_sigma_1" or result_key == "delta_sigma_12":
                final_value = df['max_stress'].max()
                max_index = df['max_stress'].idxmax()
                result_elem = df.loc[max_index, 'Elem'] if not pd.isna(max_index) else ""
                maxij = df.loc[max_index, 'Part'] if not pd.isna(max_index) else ""
            else:
                # 압축 응력 최대값(음수 중 최소) 찾기
                final_value = df['max_stress'].min()
                min_index = df['max_stress'].idxmin()
                result_elem = df.loc[min_index, 'Elem'] if not pd.isna(min_index) else ""
                maxij = df.loc[min_index, 'Part'] if not pd.isna(min_index) else ""
    except Exception as e:
        st.session_state[f"error_{stress_type}"] = f"Error occurred while calculating stress value: {str(e)}"
        return

    # Simple method 모달에서의 검증
    # Simple method 모달에서의 검증
    if 'is_simple_method' in st.session_state:
        # print(st.session_state.is_simple_method)
        pass
    if 'is_simple_method' in st.session_state and st.session_state.is_simple_method:
        if final_value > 0:
            st.session_state[f"error_{stress_type}"] = "Only compression stress is allowed. Tension stress has been detected."
            return
    elif result_key == "ds1" or result_key == "ds12":
        if final_value < 0:
            st.session_state[f"error_{stress_type}"] = "Only tension stress is allowed. Compression stress has been detected."
            final_value = 0
            return
    elif result_key == "sctraz":
        # 양수값 검증을 모달 내에서 처리하되, 에러로 중단하지 않고 0으로 설정
        if final_value < 0:
            # 세션 상태에 경고 메시지 저장하여 모달 내에서 표시
            st.session_state[f"warning_{stress_type}"] = f"Warning: The selected value is tension stress ({final_value:.3f} MPa). Set to 0."
            final_value = 0   
            return
    elif result_key == "scmax71":
        if final_value > 0:
            st.session_state[f"error_{stress_type}"] = "Only compression stress is allowed. Tension stress has been detected."
            return
    elif result_key == "scperm":
        if final_value < 0:
            # 세션 상태에 경고 메시지 저장하여 모달 내에서 표시
            st.session_state[f"warning_{stress_type}"] = f"Warning: The selected value is tension stress ({final_value:.3f} MPa). Set to 0."
            final_value = 0   
            return

    else:
        pass

    # 결과 저장
    st.session_state[result_key] = final_value
    st.session_state[temp_result_key] = final_value
    
    # 선택된 요소 번호 저장
    st.session_state[f"element_number_{stress_type}"] = result_elem
    st.session_state[f"temp_element_number_{stress_type}"] = result_elem
    
    st.session_state[f"element_part_{stress_type}"] = maxij
    st.session_state[f"temp_element_part_{stress_type}"] = maxij

    # 성공 메시지
    # print(f"응력값 로드 완료: {final_value:.3f} MPa (요소 번호: {result_elem})")

def apply_stress_data(apply_key, stress_symbol, **data):
    """응력 데이터를 세션 상태 및 데이터프레임에 적용"""
    # 현재 케이스 ID 가져오기
    case_id = st.session_state.get('fatigue_case_name', 'New Case')
    
    # 기본 데이터 준비
    new_data = {"case_id": case_id}
    
    # 모든 전달된 데이터를 처리
    for key, value in data.items():
        if key.startswith('temp_'):
            # temp_ 접두사 제거하고 실제 상태 키로 저장
            state_key = key[5:]
            st.session_state[state_key] = value
            
            # 데이터프레임용 데이터에도 접두사 없는 키로 저장
            new_data[state_key] = value
        else:
            # 접두사가 없는 키는 그대로 저장
            st.session_state[key] = value
            new_data[key] = value
    
    # 내부용 키 제거 (언더스코어로 시작하는 키)
    new_data = {k: v for k, v in new_data.items() if not k.startswith('_')}
    
    # 현재 케이스 데이터 업데이트 (첫 번째 행)
    for key, value in new_data.items():
        if key not in st.session_state.temp_result_df.columns:
            st.session_state.temp_result_df[key] = None
        st.session_state.temp_result_df.at[0, key] = value
    
    # 성공 메시지 생성
    if not stress_symbol:
        success_message = f"Data has been saved to case '{case_id}'"
    else:
        # Convert values to strings and create message
        values_text = ", ".join([f"{k}={v}" for k, v in new_data.items() if k not in ['case_id']])
        success_message = f"Stress values have been saved to case '{case_id}': {values_text}"
    
    # 성공 메시지 표시
    # st.success(success_message)
    
    # 임시 상태 재설정
    st.session_state.temp_state = False
    st.session_state[apply_key] = False

# 모달 다이얼로그 생성 함수들 ===============================

def create_stress_import_dialog(dialog_title="Midas Civil Load Import", data_type="stress"):
    """응력 데이터 임포트를 위한 모달 다이얼로그 생성"""
    
    @st.dialog(dialog_title)
    def import_dialog(item):
        # 세션 상태 초기화
        initialize_import_state()
        
        # st.write("응력 데이터 임포트")
        
        # 데이터 타입에 따라 다른 UI 표시
        if data_type == "regular_stress":
            # 정규 응력 (σc,max,71 및 σc,perm)
            show_regular_stress_ui()
        elif data_type == "moving_stress":
            # 이동 하중 응력 (Δσ1 및 Δσ1+2)
            show_moving_stress_ui()
        elif data_type == "force":
            # 하중 데이터
            show_force_ui()
        elif data_type == "road_noncracked_stress":
            # 비파괴 응력
            show_road_noncracked_stress_ui()
    
    return import_dialog





def create_simple_stress_import_dialog(dialog_title="Midas Civil Load Import - Simple Method"):
    """간단한 방법을 위한 응력 데이터 임포트 모달 다이얼로그 생성"""
    
    @st.dialog(dialog_title)
    def import_dialog(item):
        # 세션 상태 초기화
        initialize_import_state()
        
        # st.write("응력 데이터 임포트 (간단한 방법)")
        
        # Simple method 플래그 설정
        st.session_state.is_simple_method = True
        
        # σc max 입력 섹션
        expandoption = not st.session_state.get('temp_scmax', 0)
        with st.expander(f"**σc max = {st.session_state.get('temp_scmax', 0)}MPa**", expanded=expandoption):
            show_element_selection_section('scmax', 'temp_Select_Elements_simple', 'on_select_elements_simple')
        
        # σc min 입력 섹션
        expandoption2 = not st.session_state.get('temp_scmin', 0)
        with st.expander(f"**σc min = {st.session_state.get('temp_scmin', 0)}MPa**", expanded=expandoption2):
            # 이전 요소 선택 재사용
            st.session_state.temp_Select_Elements_simple2 = st.session_state.get('temp_Select_Elements_simple', '')
            show_element_selection_section('scmin', 'temp_Select_Elements_simple2', 'on_select_elements_simple2', is_second=True)
        
        # 적용 버튼
        if st.button("Apply", type="primary", on_click=on_apply_simple_stress_import, 
                    disabled=not st.session_state.get('temp_scmax', 0), use_container_width=True):
            st.rerun()
    
    return import_dialog

def on_apply_simple_stress_import():
    """간단한 방법을 위한 응력 적용"""
    scmax = st.session_state.get('temp_scmax', 0)
    scmin = st.session_state.get('temp_scmin', 0)
    element_number_scmax = st.session_state.get('temp_element_number_scmax', '')
    apply_stress_data(
        'civil_stress_import_simple', 
        'σc', 
        temp_scmax=abs(scmax),
        temp_scmin=abs(scmin),
        element_number_scmax=element_number_scmax,
    )

def show_regular_stress_ui():
    """정규 응력 (σc,max,71 및 σc,perm) UI 표시"""
    # σc,max,71 입력 섹션
    expandoption = not st.session_state.temp_scmax71
    with st.expander(f"**σc,max,71= {st.session_state.temp_scmax71}MPa**", expanded=expandoption):
        show_element_selection_section('scmax71', 'temp_Select_Elements', 'on_select_elements_1')
    
    # σc,perm 입력 섹션
    expandoption2 = not st.session_state.temp_scperm
    with st.expander(f"**σc,perm= {st.session_state.temp_scperm}MPa**", expanded=expandoption2):
        # 이전 요소 선택 재사용
        st.session_state.temp_Select_Elements2 = st.session_state.temp_Select_Elements
        show_element_selection_section('scperm', 'temp_Select_Elements2', 'on_select_elements2', is_second=True)
    
    # 적용 버튼
    if st.button("Apply", type="primary", on_click=on_apply_regular_stress_import, 
                disabled=not st.session_state.temp_scmax71, use_container_width=True):
        st.rerun()

def show_moving_stress_ui():
    """이동 하중 응력 (Δσ1 및 Δσ1+2) UI 표시"""
    # Δσ1 입력 섹션
    expandoption = not st.session_state.temp_ds1
    with st.expander(f"**Δσ₁= {st.session_state.temp_ds1}MPa**", expanded=expandoption):
        
        show_element_selection_section('ds1', 'temp_Select_Elements3', 'on_select_elements_3')
    
    # Δσ1+2 입력 섹션

    expandoption2 = not st.session_state.temp_ds12
    with st.expander(f"**Δσ₁₊₂= {st.session_state.temp_ds12}MPa**", expanded=expandoption2):
        st.session_state.temp_Select_Elements4 = st.session_state.get('temp_Select_Elements3', '')
        show_element_selection_section('ds12', 'temp_Select_Elements4', 'on_select_elements4', is_second=True)
    
    # 적용 버튼
    if st.button("Apply", type="primary", on_click=on_apply_moving_stress_import,
                disabled=not st.session_state.temp_ds1, use_container_width=True):
        st.rerun()

def show_force_ui():
    st.write("-"*100)


# simple method concrete compression 간단한 방법 요소 선택 섹션
def show_element_selection_section(stress_type, elements_key, select_callback, is_second=False):
    
    """요소 선택 및 데이터 로드 섹션 표시"""
    col1, col2 = st.columns([0.3, 0.7])
    
    # 요소 선택 버튼
    with col1:
        if not is_second:
            button_key = f"import_elements_btn_{stress_type}"
            if st.button("Import from MidasCivil", type="secondary", on_click=lambda: get_Select_Elements(elements_key), key=button_key):
                pass

    # 선택된 요소 표시
    with col2:
        elements_value = st.session_state.get(elements_key, "")
        display_text = "Select elements from MidasCivil" if not elements_value else elements_value
        input_key = f"selected_elements_input_{stress_type}"
        st.text_input("Selected Elements", display_text, disabled=True, key=input_key)
        elements_value = st.session_state.get(elements_key, "")
        
    if not is_second:
        if button_key in st.session_state and st.session_state[button_key]:
            if st.session_state.get(elements_key, ""): 
                st.session_state.temp_Select_Elements_simple2 = st.session_state.get(elements_key, "")
            else:
                st.error("Please select elements.")

    # 에러 메시지 표시 (Simple method 모달 내에서만)
    error_key = f"error_{stress_type}"
    if error_key in st.session_state and st.session_state[error_key]:
        st.error(st.session_state[error_key])
        st.session_state[error_key] = ""  # 에러 메시지 초기화
    
    # 일반 경고 메시지 표시 (모달 내에서)
    warning_key = f"warning_{stress_type}"
    if warning_key in st.session_state and st.session_state[warning_key]:
        st.warning(st.session_state[warning_key])
        st.session_state[warning_key] = ""  # 경고 메시지 초기화
    # 하중 케이스 및 기타 옵션 선택
    load_case_key = f"selected_load_case_{stress_type}"
    section_key = f"selected_section_{stress_type}"
    component_key = f"selected_component_{stress_type}"
    location_key = f"selected_location_{stress_type}"
    
    st.selectbox("Load Cases/Combinations", options=list(st.session_state.civil_load_cases_data), key=load_case_key)
    st.selectbox("Component Part", options=("Part 1", "Part 2"), key=section_key)
    st.selectbox("Stress Position", options=("Maximum", "1(-y, +z)", "2(+y, +z)", "3(+y, -z)", "4(-y, -z)"), key=component_key)
    st.selectbox("Element Location", options=("Maximum", "Minimum", "Part I", "Part J", "Part 1/4", "Part 2/4", "Part 3/4"), key=location_key)
    
    # 데이터 로드 버튼
    button_key = f"load_data_btn_{stress_type}"
    st.button("Load Data", type="secondary", 
            on_click=lambda: load_composit_stress_data(stress_type, elements_key, load_case_key, 
                                                    section_key, component_key, location_key, is_second), 
            disabled=not st.session_state.get(elements_key, ""), 
            use_container_width=True, key=button_key)
    
def show_road_noncracked_stress_ui():
    """비파괴 응력 (σc,traz) UI 표시"""
    # σc,traz 입력 섹션
    expandoption = not st.session_state.get('temp_sctraz', 0)
    with st.expander(f"**σc,traz= {st.session_state.get('temp_sctraz', 0)}MPa**", expanded=expandoption):
        show_element_selection_section('sctraz', 'temp_Select_Elements_sctraz', 'on_select_elements_sctraz')
    
    # 적용 버튼
    if st.button("Apply", type="primary", on_click=on_apply_road_noncracked_stress_import, 
                disabled=not st.session_state.get('temp_sctraz', 0), use_container_width=True):
        st.rerun()


def on_apply_road_noncracked_stress_import():
    """비파괴 응력 적용"""
    sctraz = st.session_state.get('temp_sctraz', 0)
    element_number_sctraz = st.session_state.get('temp_element_number_sctraz', '')
    element_part_sctraz = st.session_state.get('temp_element_part_sctraz', '')
    
    apply_stress_data(
        'civil_stress_import_road_noncracked', 
        'σc,traz', 
        temp_sctraz=sctraz,
        temp_element_part_sctraz=element_part_sctraz,
        element_number_sctraz=element_number_sctraz,
        element_part_sctraz=element_part_sctraz
    )

def on_apply_regular_stress_import():
    """정규 응력 적용"""
    scmax71 = st.session_state.get('temp_scmax71', 0)
    scperm = st.session_state.get('temp_scperm', 0)
    element_number_scmax71 = st.session_state.get('temp_element_number_scmax71', '')
    
    apply_stress_data(
        'civil_stress_import', 
        'σc', 
        temp_scmax71=scmax71,
        temp_scperm=scperm,
        temp_con_σcmax71=scmax71,
        temp_con_σcperm=scperm,
        element_number_scmax71=element_number_scmax71
    )

def on_apply_moving_stress_import():
    """이동 하중 응력 적용"""
    ds1 = st.session_state.get('temp_ds1', 0)
    ds12 = st.session_state.get('temp_ds12', 0)
    # 요소 번호와 위치 정보 추가
    element_number_ds1 = st.session_state.get('temp_element_number_ds1', '')
    element_part_ds1 = st.session_state.get('temp_element_part_ds1', '')
    element_number_ds12 = st.session_state.get('temp_element_number_ds12', '')
    element_part_ds12 = st.session_state.get('temp_element_part_ds12', '')    
    
    apply_stress_data(
        'civil_stress_import2', 
        'Δσ', 
        temp_ds1=ds1,
        temp_ds12=ds12,
        ds1=ds1,
        ds12=ds12,
        # 요소 번호와 위치 정보 추가
        element_number_ds1=element_number_ds1,
        element_part_ds1=element_part_ds1,
        element_number_ds12=element_number_ds12,
        element_part_ds12=element_part_ds12,
        temp_element_number_ds1=element_number_ds1,
        temp_element_part_ds1=element_part_ds1,
        temp_element_number_ds12=element_number_ds12,
        temp_element_part_ds12=element_part_ds12
    )

def on_apply_road_cracked_stress_import():
    """파괴 응력 적용"""
    sctraz = st.session_state.get('temp_sctraz', 0)
    
    apply_stress_data(
        'civil_stress_import3', 
        'σc,traz', 
        temp_sctraz=sctraz,
        sctraz=sctraz
    )


# steel grider 스틸거더 direct stress 축응력 --------------------------------------------------------------------------------------
def show_element_selection_section_steel_girder(stress_type, elements_key, select_callback, is_second=False):
    st.session_state.is_simple_method = False  # 간단한 방법 플래그 초기화
    """요소 선택 및 데이터 로드 섹션 표시"""
    col1, col2 = st.columns([0.3, 0.7])
    
    # 요소 선택 버튼
    with col1:
        if not is_second:
            button_key = f"import_elements_btn_{stress_type}"
            if st.button("Select Elements", type="secondary", on_click=lambda: get_Select_Elements(elements_key), key=button_key):
                pass

    # 선택된 요소 표시
    with col2:
        elements_value = st.session_state.get(elements_key, "")
        display_text = "Select elements from MidasCivil" if not elements_value else elements_value
        input_key = f"selected_elements_input_{stress_type}"
        st.text_input("Selected Elements", display_text, disabled=True, key=input_key)

    if not is_second:
        if button_key in st.session_state and st.session_state[button_key]:
            if elements_value: 
                st.session_state.temp_Select_Elements_steel2 = st.session_state.get('temp_Select_Elements_steel', '')
            else:
                st.error("Select elements.")
    # 에러 메시지 표시 (Simple method 모달 내에서만)
    if 'is_simple_method' in st.session_state and st.session_state.is_simple_method:
        error_key = f"error_{stress_type}"
        if error_key in st.session_state and st.session_state[error_key]:
            st.error(st.session_state[error_key])
            st.session_state[error_key] = ""  # 에러 메시지 초기화
    # 하중 케이스 및 기타 옵션 선택
    load_case_key = f"selected_load_case_{stress_type}"
    section_key = f"selected_section_{stress_type}"
    component_key = f"selected_component_{stress_type}"
    location_key = f"selected_location_{stress_type}"
    

    st.selectbox("Load Cases/Combinations", options=list(st.session_state.civil_load_cases_data), key=load_case_key)
    st.selectbox("Component Part", options=("Part 1", "Part 2"), key=section_key)
    st.selectbox("Stress Position", options=("Maximum", "1(-y, +z)", "2(+y, +z)", "3(+y, -z)", "4(-y, -z)"), key=component_key)
    st.selectbox("Element Location", options=("Maximum", "Minimum", "Part I", "Part J", "Part 1/4", "Part 2/4", "Part 3/4"), key=location_key)
    
    # 데이터 로드 버튼
    button_key = f"load_data_btn_{stress_type}"
    st.button("Load Data", type="secondary", 
            on_click=lambda: load_composit_stress_data(stress_type, elements_key, load_case_key, 
                                                    section_key, component_key, location_key, is_second), 
            disabled=not st.session_state.get(elements_key, ""), 
            use_container_width=True, key=button_key)

# steel grider 스틸거더
def create_steel_stress_import_dialog(dialog_title="Midas Civil Steel Stress Import"):
    """철강 응력 데이터 임포트를 위한 모달 다이얼로그 생성"""
    
    @st.dialog(dialog_title)
    def import_dialog(item):
        # 세션 상태 초기화
        initialize_import_state()
        
        # st.write("철강 응력 데이터 임포트")
        
        # 최대 응력 입력 섹션
        expandoption = not st.session_state.get('temp_delta_sigma_1', 0)
        with st.expander(f"**Δσ₁ = {st.session_state.get('temp_delta_sigma_1', 0)}MPa**", expanded=expandoption):
            show_element_selection_section_steel_girder('delta_sigma_1', 'temp_Select_Elements_steel', 'on_select_elements_steel')
        
        # 이중 트랙 응력 입력 섹션
        expandoption2 = not st.session_state.get('temp_delta_sigma_12', 0)
        with st.expander(f"**Δσ₁₊₂ = {st.session_state.get('temp_delta_sigma_12', 0)}MPa**", expanded=expandoption2):
            # 이전 요소 선택 재사용
            st.session_state.temp_Select_Elements_steel2 = st.session_state.get('temp_Select_Elements_steel', '')
            show_element_selection_section_steel_girder('delta_sigma_12', 'temp_Select_Elements_steel2', 'on_select_elements_steel2', is_second=True)
        
        # 적용 버튼
        if st.button("Apply", type="primary", on_click=on_apply_steel_stress_import, 
                    disabled=not st.session_state.get('temp_delta_sigma_1', 0), use_container_width=True):
            st.rerun()
    
    return import_dialog

# steel grider 스틸거더
def on_apply_steel_stress_import():
    """철강 응력 적용"""
    delta_sigma_1 = st.session_state.get('temp_delta_sigma_1', 0)
    delta_sigma_12 = st.session_state.get('temp_delta_sigma_12', 0)
    element_number_delta_sigma_1 = st.session_state.get('temp_element_number_delta_sigma_1', '')
    element_number_delta_sigma_12 = st.session_state.get('temp_element_number_delta_sigma_12', '')

    
    apply_stress_data(
        'civil_stress_import_steel', 
        'Δσ', 
        temp_delta_sigma_1=delta_sigma_1,
        temp_delta_sigma_12=delta_sigma_12,
        delta_sigma_1=delta_sigma_1,
        delta_sigma_12=delta_sigma_12,
        element_number_delta_sigma_1=element_number_delta_sigma_1,
        element_number_delta_sigma_12=element_number_delta_sigma_12


    )

#----------------------------------------------------------------------------------------------------------------------------

            #     st.number_input(
            #         r"$V_{s1}$ (kN)", 
            #         value=float(st.session_state.get('Vs1', 1828.0)),
            #         step=1.0, 
            #         key="Vs1_widget",
            #         on_change=update_temp_from_input,
            #         args=("Vs1_widget", "Vs1"),
            #         disabled=st.session_state.manual_input_direct,
            #         placeholder="Import from Midas" if st.session_state.manual_input_direct else None
            #     )
                
            # with col3:
            #     st.number_input(
            #         r"$V_{s1+2}$ (kN)", 
            #         value=float(st.session_state.get('Vs12', 1652.0)), 
            #         step=1.0, 
            #         key="Vs12_widget",
            #         on_change=update_temp_from_input,
            #         args=("Vs12_widget", "Vs12"),
            #         disabled=st.session_state.manual_input_direct
            #     )
# steel grider 스틸거더 shear stress 전단응력 -스틸전단모달-------------------------------------------------------------------
def create_steel_shear_force_import_dialog(dialog_title="Midas Civil 전단력 가져오기"):
    """전단력 데이터 임포트를 위한 모달 다이얼로그 생성"""
    
    @st.dialog(dialog_title)
    def import_dialog(item):
        # 세션 상태 초기화
        initialize_import_state()
        
        
        # Vs1 입력 섹션
        expandoption = not st.session_state.get('temp_Vs1', 0)
        with st.expander(f"**Vs1 = {st.session_state.get('temp_Vs1', 0)} kN**", expanded=expandoption):
            show_element_selection_for_steel_shear_force('Vs1', 'temp_Select_Elements_shear', 'on_select_elements_shear', is_second=False)
        
        # # Vs12 입력 섹션
        # expandoption2 = not st.session_state.get('temp_Vs12', 0)
        # with st.expander(f"**Vs1+2 = {st.session_state.get('temp_Vs12', 0)} kN**", expanded=expandoption2):
        #     # 이전 요소 선택 재사용
        #     st.session_state.temp_Select_Elements_shear2 = st.session_state.get('temp_Select_Elements_shear', '')
        #     show_element_selection_for_steel_shear_force('Vs12', 'temp_Select_Elements_shear2', 'on_select_elements_shear2', is_second=True)
        
        # 적용 버튼
        if st.button("Apply", type="primary", on_click=on_apply_steel_shear_force_import, 
                    disabled=not st.session_state.get('temp_Vs1', 0), use_container_width=True):
            st.rerun()
    
    return import_dialog
#전단력 불러오는 모달 내용
def show_element_selection_for_steel_shear_force(force_type, elements_key, select_callback, is_second=False):
    """요소 선택 및 전단력 데이터 로드 섹션 표시"""
    col1, col2 = st.columns([0.3, 0.7])
    
    # 요소 선택 버튼
    with col1:
        if not is_second:  # 두 번째 입력 필드(Vs12)에서는 요소 선택 버튼 숨기기
            button_key = f"import_elements_btn_{force_type}"
            if st.button("Select Elements", type="secondary", on_click=lambda: get_Select_Elements(elements_key), key=button_key):
                pass
    
    # 선택된 요소 표시
    with col2:
        elements_value = st.session_state.get(elements_key, "")
        display_text = "Select elements from MidasCivil" if not elements_value else elements_value
        input_key = f"selected_elements_input_{force_type}"
        st.text_input("Selected Elements", display_text, disabled=True, key=input_key)
    
    # 하중 케이스 및 기타 옵션 선택
    load_case_key = f"selected_load_case_{force_type}"
    section_key = f"selected_section_{force_type}"
    location_key = f"selected_location_{force_type}"
    #전단력 불러오기 하중케이스 선택
    # (CB가 포함된 하중 케이스만 필터링
    st.session_state.civil_shear_load_cases_data = [case for case in st.session_state.civil_load_cases_data if '(MV' in case]
    
    # 필터링된 결과가 없는 경우 에러 메시지 표시
    if not st.session_state.civil_shear_load_cases_data:
        st.error("No load cases containing (MV) found. Please check the load case.")
    st.selectbox("Load Cases", options=list(st.session_state.civil_shear_load_cases_data), key=load_case_key)

    # st.selectbox("단면 위치", options=("Part 1", "Part 2"), key=section_key)
    #st.selectbox("선택 위치", options=("Maximum", "Minimum", "Absolute Maximum","Absolute Minimum", "Part I", "Part J"), key=location_key, disabled=True)
    st.session_state[location_key] = "Maximum"
    
    # 부호 선택 은 여기서는 필요없어서 주석처리하고 모든값으로 강제로 넣음
    # sign_key = f"selected_sign_{force_type}"
    # st.selectbox("부호 선택", options=("모든 값", "양수만", "음수만"), index=0, key=sign_key)
    sign_key = f"selected_sign_{force_type}"
    if sign_key not in st.session_state:
        st.session_state[sign_key] = "모든 값"
    # 데이터 로드 버튼
    button_key = f"load_data_btn_{force_type}"
    st.button("Import from Midas Civil", type="secondary", 
            on_click=lambda: load_steel_shear_force_data(force_type, elements_key, load_case_key, 
                                               section_key, location_key, sign_key, is_second), 
            disabled=not st.session_state.get(elements_key, ""), 
            use_container_width=True, key=button_key)


def load_steel_shear_force_data(force_type, elements_key, load_case_key, section_key, location_key, sign_key, is_second=False):
    """Midas Civil에서 전단력 데이터 불러오기 (Z방향만)"""
    # API 설정 가져오기
    mapi_key = st.session_state.get('current_mapi_key', '')
    base_url = st.session_state.get('current_base_url', '')
    
    if not mapi_key or not base_url:
        st.error("API 설정을 찾을 수 없습니다. 먼저 로그인해주세요.")
        return
        
    headers = {"MAPI-Key": mapi_key}
    
    # 결과 저장 키 설정
    result_key = force_type
    temp_result_key = f"temp_{force_type}"
    
    # 선택된 요소 및 하중 케이스 가져오기
    try:
        selected_elements = [int(x) for x in st.session_state.get(elements_key, '').split(',') if x.strip()]
        if not selected_elements:
            st.error("No selected elements.")
            return
        st.session_state[elements_key] = ','.join(map(str, selected_elements))
    except Exception as e:
        st.error(f"Cannot process selected element list: {str(e)}")
        return
    
    selected_load = st.session_state.get(load_case_key, '')
    selected_section = st.session_state.get(section_key, '')
    # selected_location = st.session_state.get(location_key, '')
    selected_location = "Absolute Maximum"
    selected_sign = st.session_state.get(sign_key, "모든 값")
    
    # 하중 케이스 형식 표준화 (괄호와 접두어 제거)
    selected_load_result = selected_load
    for prefix in ['CBC:', 'CB:', 'MV:', 'CBSM:', '(CB)', '(MV)', '(CBC)', '(CBSM)']:
        selected_load_result = selected_load_result.replace(prefix, '')
    
    # civil_result_force_df 확인
    if 'civil_result_force_df' not in st.session_state:
        st.error("civil_result_force_df not found. Please load the data first.")
        return
        
    df = st.session_state.civil_result_force_df
    
    if df.empty:
        st.warning("The data is empty. Please load the data first.")
        return
    
    # 선택된 요소로 필터링
    df = df[df['Elem'].astype(str).isin([str(e) for e in selected_elements])]
    
    # 선택된 하중 케이스로 필터링
    df = df[df['Load'] == selected_load_result]
    
    if df.empty:
        st.warning(f"No data found for selected elements ({selected_elements}) and load case ({selected_load_result}).")
        return
    # print((list(df.columns)))
    # 섹션 파트 필터링

    
    # 전단력 컬럼 처리
    if 'Shear-z' not in df.columns:
        st.warning("Z-direction shear force column (Shear-z) not found in data.")
        return
    
    # 전단력 값을 숫자로 변환
    df['Shear-z'] = pd.to_numeric(df['Shear-z'], errors='coerce')
    
    # 부호 선택에 따라 필터링
    if selected_sign == "양수만":
        df_filtered = df[df['Shear-z'] > 0]
        if df_filtered.empty:
            st.warning("No positive shear force values.")
            return
        df = df_filtered
    elif selected_sign == "음수만":
        df_filtered = df[df['Shear-z'] < 0]
        if df_filtered.empty:
            st.warning("No negative shear force values.")
            return
        df = df_filtered

    # 위치별로 필터링
    if selected_location not in ["Maximum", "Minimum", "Absolute Maximum", "Absolute Minimum"]:
        # "Part I", "Part J" 등으로 필터링
        location_part = selected_location.split()[-1]  # "Part I" -> "I" 추출
        
        # 부분 문자열 매칭 사용 (I[숫자]와 같은 형식 처리)
        # df['Part']가 문자열이 아닐 경우를 대비한 안전 처리
        if 'Part' in df.columns:
            df_filtered = df[df['Part'].astype(str).str.startswith(location_part)]
            if df_filtered.empty:
                st.warning(f"No data found for selected location ({selected_location}).")
                try:
                    possible_parts = df['Part'].unique()
                    st.write("Possible location values:", possible_parts)
                except:
                    st.write("Please check the data structure.")
                return
            df = df_filtered
        else:
            st.warning("'Part' column not found in data.")
            return
    if is_second:
        selected_location = "Absolute Maximum"
    else:
        selected_location = "Absolute Maximum"

    # 선택에 따른 값 결정
    try:
        if selected_location == "Maximum":
            # 최대값 찾기
            idx = df['Shear-z'].idxmax()
        elif selected_location == "Minimum":
            # 최소값 찾기
            idx = df['Shear-z'].idxmin()
        elif selected_location == "Absolute Maximum":
            # 절대값 기준 최대값 찾기
            idx = df['Shear-z'].abs().idxmax()
        elif selected_location == "Absolute Minimum":
            # 절대값 기준 최소값 찾기
            idx = df['Shear-z'].abs().idxmin()
        else:
            # 기본 선택 (force_type에 따라)
            if force_type == 'Vs1':
                # 최대 전단력 (절대값이 가장 큰 값)
                idx = df['Shear-z'].abs().idxmax()
            else:  # Vs12
                # 최소 전단력 (절대값이 가장 작은 값)
                idx = df['Shear-z'].abs().idxmin()
    except Exception as e:
        st.error(f"Error calculating shear force: {str(e)}")
        return
    
    # 선택된 행 가져오기
    selected_row = df.loc[idx]
    
    # 전단력 값 가져오기
    shear_force = selected_row['Shear-z']
    
    # 부호를 유지한 전단력 값 저장
    st.session_state[result_key] = shear_force
    st.session_state[temp_result_key] = shear_force
    
    # 선택된 요소 번호와 위치 저장
    element_number = selected_row['Elem']
    element_part = selected_row.get('Part', 'N/A')
    
    st.session_state[f"element_number_{force_type}"] = element_number
    st.session_state[f"temp_element_number_{force_type}"] = element_number
    st.session_state[f"element_part_{force_type}"] = element_part
    st.session_state[f"temp_element_part_{force_type}"] = element_part
    
    # 성공 메시지
    st.success(f"{force_type} shear force value loaded: {shear_force:.3f} kN (element number: {element_number}, location: {element_part})")

def on_apply_steel_shear_force_import():
    """전단력 데이터 적용"""
    Vs1 = st.session_state.get('temp_Vs1', 0)
    Vs12 = st.session_state.get('temp_Vs12', 0)
    element_number_Vs1 = st.session_state.get('temp_element_number_Vs1', '')
    element_part_Vs1 = st.session_state.get('temp_element_part_Vs1', '')
    # 하중 케이스 키 동적으로 생성
    load_case_key = f"selected_load_case_Vs1"
    selected_load_case = st.session_state.get(load_case_key, '')


    # 섹션 특성 자동 로드 추가
    selected_elements = st.session_state.get('element_number_Vs1', '')
    if selected_elements:
        section_properties = get_section_properties_from_elements(selected_elements)
        
        if section_properties:
            # 섹션 특성을 세션 상태에 저장 (get_ 접두사 사용)
            st.session_state.get_d = section_properties.get('girder_height', 0)  # 또는 실제 키 이름
            st.session_state.get_bw = section_properties.get('bw', 0)
            st.session_state.get_Qn = section_properties.get('qn_girder_totcenter', 0)
            st.session_state.get_J = section_properties.get('iyy_girder', 0)
            st.session_state.get_total_centroid_height = section_properties.get('total_centroid_height', 0)
            st.session_state.get_girder_centroid_height = section_properties.get('girder_centroid_height', 0)
            st.session_state.get_girder_height = section_properties.get('girder_height', 0)
            st.session_state.get_slab_height = section_properties.get('slab_height', 0)
            st.session_state.get_total_height = section_properties.get('total_height', 0)
            st.session_state.get_total_area = section_properties.get('total_area', 0)
            st.session_state.get_total_first_moment = section_properties.get('total_first_moment', 0)
            st.session_state.get_iyy_total = section_properties.get('iyy_total', 0)

            st.success("Section properties have been automatically loaded.")
        else:
            st.warning("Unable to load section properties. Using default values.")


    apply_stress_data(
        'civil_shear_force_import', 
        'V', 
        temp_Vs1=Vs1,
        temp_Vs12=Vs12,
        Vs1=Vs1,  # 세션 상태에 직접 저장
        Vs12=Vs12,  # 세션 상태에 직접 저장
        element_number_Vs1=element_number_Vs1,
        element_part_Vs1=element_part_Vs1,
        shear_load_case=selected_load_case,  # 하중 케이스 추가
        get_d=st.session_state.get('get_d', 0),
        get_bw=st.session_state.get('get_bw', 0),
        get_Qn=st.session_state.get('get_Qn', 0),
        get_J=st.session_state.get('get_J', 0),
        get_total_centroid_height=st.session_state.get('get_total_centroid_height', 0),
        get_girder_centroid_height=st.session_state.get('get_girder_centroid_height', 0),
        get_girder_height=st.session_state.get('get_girder_height', 0),
        get_total_area=st.session_state.get('get_total_area', 0),
        get_total_first_moment=st.session_state.get('get_total_first_moment', 0),
        get_iyy_total=st.session_state.get('get_iyy_total', 0),
        get_slab_height=st.session_state.get('get_slab_height', 0),
        get_total_height=st.session_state.get('get_total_height', 0)
    )
#----------------------------------------------------------------------------------------------------------------------------






# session_manager.py
def get_section_properties_from_elements(temp_select_elements_string):
    """
    요소 번호 문자열에서 섹션 특성을 가져오는 함수
    
    Args:
        temp_select_elements_string (str): 요소 번호들이 콤마로 구분된 문자열 (예: "10,11,12")
    
    Returns:
        dict: 섹션 특성 정보 또는 None
    """
    try:
        # 1. 요소 번호 문자열을 리스트로 변환
        if not temp_select_elements_string or temp_select_elements_string.strip() == '':
            st.error("No elements selected.")
            return None
            
        selected_elements = [int(x.strip()) for x in temp_select_elements_string.split(',') if x.strip()]
        
        if not selected_elements:
            st.error("No valid element numbers.")
            return None
        
        # 2. civil_all_element_data에서 선택된 요소들의 section_id 찾기
        if 'civil_all_element_data' not in st.session_state or st.session_state.civil_all_element_data.empty:
            st.error("Element data not found. Please load the data first.")
            return None
        
        element_df = st.session_state.civil_all_element_data
        
        # 선택된 요소들 필터링
        selected_element_data = element_df[element_df['elem_id'].astype(int).isin(selected_elements)]
        
        if selected_element_data.empty:
            st.error(f"Selected elements ({selected_elements}) not found.")
            return None
        
        # 3. 선택된 요소들의 section_id 확인
        unique_section_ids = selected_element_data['sect_id'].unique()
        
        if len(unique_section_ids) > 1:
            st.error(f"Selected elements have different sections. "
                    f"Section IDs: {unique_section_ids}. "
                    f"Please select elements with the same section.")
            return None
        
        section_id = unique_section_ids[0]
        
        # 4. section_properties_df에서 해당 section_id의 특성 가져오기
        if 'section_properties_df' not in st.session_state or st.session_state.section_properties_df.empty:
            st.error("Section properties data not found. Please load the data first.")
            return None
        
        section_df = st.session_state.section_properties_df
        # print(section_df['section_id'].values[0].strip())
        # print(str(section_id).strip())
        section_data = section_df[section_df['section_id'].str.strip() == str(section_id).strip()]

        if section_data.empty:
            st.error(f"Section ID {section_id} not found.")
            return None
        
        # 5. 섹션 특성을 딕셔너리로 변환하여 저장
        section_properties = section_data.iloc[0].to_dict()
        
        # session_state에 저장
        st.session_state.section_prop_result = section_properties
        
        # 성공 메시지
        st.success(f"Section properties loaded: Section ID {section_id}, Name: {section_properties.get('name', 'Unknown')}")
        
        return section_properties
        
    except Exception as e:
        st.error(f"Error loading section properties: {str(e)}")
        return None



#일반전단
#전단하중 보강 불필요 불러오기 ---------------------------------------------------------------------------------------------------
def create_shear_force_import_dialog(dialog_title="Midas Civil 전단력 가져오기"):
    """전단력 데이터 임포트를 위한 모달 다이얼로그 생성"""
    
    @st.dialog(dialog_title)
    def import_dialog(item):
        # 세션 상태 초기화
        initialize_import_state()
 
        # Vsdmax 입력 섹션
        expandoption = not st.session_state.get('temp_Vsdmax', 0)
        with st.expander(f"**Vsdmax (Maximum Shear Force) = {st.session_state.get('temp_Vsdmax', 0)} kN**", expanded=expandoption):
            show_element_selection_for_shear_force_notreinforced('Vsdmax', 'temp_Select_Elements_shear', 'on_select_elements_shear', is_second=False)
        
        # Vsdmin 입력 섹션
        expandoption2 = not st.session_state.get('temp_Vsdmin', 0)
        with st.expander(f"**Vsdmin (Minimum Shear Force) = {st.session_state.get('temp_Vsdmin', 0)} kN**", expanded=expandoption2):
            # 이전 요소 선택 재사용
            st.session_state.temp_Select_Elements_shear2 = st.session_state.get('temp_Select_Elements_shear', '')
            show_element_selection_for_shear_force_notreinforced('Vsdmin', 'temp_Select_Elements_shear2', 'on_select_elements_shear2', is_second=True)
        
        # 적용 버튼
        if st.button("Apply", type="primary", on_click=on_apply_shear_force_import_notreinforced, 
                    disabled=not st.session_state.get('temp_Vsdmax', 0), use_container_width=True):
            try:
                st.session_state['final_element'] = ""
            except :
                pass           
            st.rerun()
    
    return import_dialog
#전단력 불러오는 모달 내용
def show_element_selection_for_shear_force_notreinforced(force_type, elements_key, select_callback, is_second=False):
    """요소 선택 및 전단력 데이터 로드 섹션 표시"""
    col1, col2 = st.columns([0.3, 0.7])
    
    # 요소 선택 버튼
    with col1:
        if not is_second:  # 두 번째 입력 필드(Vsdmin)에서는 요소 선택 버튼 숨기기
            button_key = f"import_elements_btn_{force_type}"
            if st.button("Select Elements", type="secondary", on_click=lambda: get_Select_Elements(elements_key), key=button_key):
                pass
    
    # 선택된 요소 표시
    with col2:
        elements_value = st.session_state.get(elements_key, "")
        display_text = "Select Elements from MidasCivil" if not elements_value else elements_value
        input_key = f"selected_elements_input_{force_type}"
        st.text_input("Selected Elements", display_text, disabled=True, key=input_key)
    
    # 하중 케이스 및 기타 옵션 선택
    load_case_key = f"selected_load_case_{force_type}"
    section_key = f"selected_section_{force_type}"
    location_key = f"selected_location_{force_type}"
    #전단력 불러오기 하중케이스 선택
    # (CB가 포함된 하중 케이스만 필터링
    st.session_state.civil_shear_load_cases_data = [case for case in st.session_state.civil_load_cases_data if '(CB' in case]
    
    # 필터링된 결과가 없는 경우 에러 메시지 표시
    if not st.session_state.civil_shear_load_cases_data:
        st.error("No load cases containing (CB:Concrete Design) found. Please check the load combinations.")
    st.selectbox("Load Case", options=list(st.session_state.civil_shear_load_cases_data), key=load_case_key)

    # st.selectbox("단면 위치", options=("Part 1", "Part 2"), key=section_key)
    #st.selectbox("선택 위치", options=("Maximum", "Minimum", "Absolute Maximum","Absolute Minimum", "Part I", "Part J"), key=location_key, disabled=True)
    st.session_state[location_key] = "Maximum"
    
    # 부호 선택 은 여기서는 필요없어서 주석처리하고 모든값으로 강제로 넣음
    # sign_key = f"selected_sign_{force_type}"
    # st.selectbox("부호 선택", options=("모든 값", "양수만", "음수만"), index=0, key=sign_key)
    sign_key = f"selected_sign_{force_type}"
    if sign_key not in st.session_state:
        st.session_state[sign_key] = "모든 값"
    # 데이터 로드 버튼
    button_key = f"load_data_btn_{force_type}"
    # 에러 메시지 표시 

    error_key = f"error_{force_type}"
    if error_key in st.session_state and st.session_state[error_key]:
        st.error(st.session_state[error_key])
        st.session_state[error_key] = ""  # 에러 메시지 초기화
    
    # 일반 경고 메시지 표시 (모달 내에서)
    warning_key = f"warning_{force_type}"
    if warning_key in st.session_state and st.session_state[warning_key]:
        st.warning(st.session_state[warning_key])
        st.session_state[warning_key] = ""  # 경고 메시지 초기화

    
    st.button("Load Data", type="secondary", 
            on_click=lambda: load_shear_force_data_notreinforced(force_type, elements_key, load_case_key, 
                                               section_key, location_key, sign_key, is_second), 
            disabled=not st.session_state.get(elements_key, ""), 
            use_container_width=True, key=button_key)


def load_shear_force_data_notreinforced(force_type, elements_key, load_case_key, section_key, location_key, sign_key, is_second=False):
    """Midas Civil에서 전단력 데이터 불러오기 (Z방향만)"""
    # API 설정 가져오기
    mapi_key = st.session_state.get('current_mapi_key', '')
    base_url = st.session_state.get('current_base_url', '')
    
    
    if not mapi_key or not base_url:
        st.error("API settings not found. Please login first.")
        return
        
    headers = {"MAPI-Key": mapi_key}
    
    # 결과 저장 키 설정
    result_key = force_type
    temp_result_key = f"temp_{force_type}"
    
    # 선택된 요소 및 하중 케이스 가져오기
    try:
        selected_elements = [int(x) for x in st.session_state.get(elements_key, '').split(',') if x.strip()]
        if not selected_elements:
            st.session_state[f"error_{force_type}"] = "No selected elements"

            return
        st.session_state[elements_key] = ','.join(map(str, selected_elements))
    except Exception as e:
        st.session_state[f"error_{force_type}"] = f"Cannot process selected element list: {str(e)}"
        return
    try: 
        selected_load = st.session_state.get(load_case_key, '')
        selected_section = st.session_state.get(section_key, '')
        selected_location = st.session_state.get(location_key, '')
        selected_sign = st.session_state.get(sign_key, "모든 값")
        
        # 하중 케이스 형식 표준화 (괄호와 접두어 제거)
        selected_load_result = selected_load
        for prefix in ['CBC:', 'CB:', 'MV:', 'CBSM:', '(CB)', '(MV)', '(CBC)', '(CBSM)']:
            selected_load_result = selected_load_result.replace(prefix, '')
        
        # civil_result_force_df 확인
        if 'civil_result_force_df' not in st.session_state:
            st.session_state[f"error_{force_type}"] = "civil_result_force_df not found. Please load the data first."
            return
            
        df = st.session_state.civil_result_force_df
        
        if df.empty:
            st.session_state[f"error_{force_type}"] = "Member force data is empty. Please load the data first."
            return
        print(st.session_state.get('final_element', '0'))

        if is_second:
            df = df[df['Elem'].astype(str).isin([str(st.session_state.get('final_element', '0'))])]
        else:
            df = df[df['Elem'].astype(str).isin([str(e) for e in selected_elements])]
        
        # 선택된 하중 케이스로 필터링
        df = df[df['Load'] == selected_load_result]
        
        if df.empty:
            st.session_state[f"error_{force_type}"] = f"Unsupported elements. Check in MIDAS Civil."
            return
        # print((list(df.columns)))
        # 섹션 파트 필터링

        
        # 전단력 컬럼 처리
        if 'Shear-z' not in df.columns:
            st.session_state[f"error_{force_type}"] = "Z-direction shear force column (Shear-z) not found in data."
            return
        
        # 전단력 값을 숫자로 변환
        df['Shear-z'] = pd.to_numeric(df['Shear-z'], errors='coerce')
        
        # 부호 선택에 따라 필터링
        if selected_sign == "양수만":
            df_filtered = df[df['Shear-z'] > 0]
            if df_filtered.empty:
                st.session_state[f"error_{force_type}"] = "No positive shear force values."
                return
            df = df_filtered
        elif selected_sign == "음수만":
            df_filtered = df[df['Shear-z'] < 0]
            if df_filtered.empty:
                st.session_state[f"error_{force_type}"] = "No negative shear force values."
                return
            df = df_filtered

        # 위치별로 필터링
        if selected_location not in ["Maximum", "Minimum", "Absolute Maximum", "Absolute Minimum"]:
            # "Part I", "Part J" 등으로 필터링
            location_part = selected_location.split()[-1]  # "Part I" -> "I" 추출
            
            # 부분 문자열 매칭 사용 (I[숫자]와 같은 형식 처리)
            # df['Part']가 문자열이 아닐 경우를 대비한 안전 처리
            if 'Part' in df.columns:
                df_filtered = df[df['Part'].astype(str).str.startswith(location_part)]
                if df_filtered.empty:
                    # st.warning(f"No data found for selected location ({selected_location}).")
                    try:
                        possible_parts = df['Part'].unique()
                        st.write("Possible location values:")
                    except:
                        st.write("Please check the data structure.")
                    return
                df = df_filtered
            else:
                st.session_state[f"error_{force_type}"] = "'Part' column not found in data."
                return
    except Exception as e:
        st.session_state[f"error_{force_type}"] = "Error: Load combinations must be defined for concrete design analysis."
    # if is_second:
    #     selected_location = "Absolute Maximum"
    # else:
    #     selected_location = "Absolute Maximum"

    # 선택에 따른 값 결정
    try:
        if selected_location == "Maximum":
            # 최대값 찾기
            idx = df['Shear-z'].idxmax()
            if is_second == False:
                final_element = df.loc[idx, 'Elem']
        elif selected_location == "Minimum":
            # 최소값 찾기
            idx = df['Shear-z'].idxmin()
            if is_second == False:
                final_element = df.loc[idx, 'Elem']    
        elif selected_location == "Absolute Maximum":
            # 절대값 기준 최대값 찾기
            idx = df['Shear-z'].abs().idxmax()
            if is_second == False:
                final_element = df.loc[idx, 'Elem']
        elif selected_location == "Absolute Minimum":
            # 절대값 기준 최소값 찾기
            idx = df['Shear-z'].abs().idxmin()
            if is_second == False:
                final_element = df.loc[idx, 'Elem']
        else:
            # 기본 선택 (force_type에 따라)
            if force_type == 'Vsdmax':
                # 최대 전단력 (절대값이 가장 큰 값)
                idx = df['Shear-z'].abs().idxmax()
                if is_second == False:
                    final_element = df.loc[idx, 'Elem']
            else:  # Vsdmin
                # 최소 전단력 (절대값이 가장 작은 값)
                idx = df['Shear-z'].abs().idxmin()
                if is_second == False:
                    final_element = df.loc[idx, 'Elem']
        st.session_state            
    except Exception as e:
        # st.error(f"Error calculating shear force: {str(e)}")
        return
    
    # 선택된 행 가져오기
    selected_row = df.loc[idx]
    
    # 전단력 값 가져오기
    shear_force = selected_row['Shear-z']
    
    # 부호를 유지한 전단력 값 저장
    st.session_state[result_key] = shear_force
    st.session_state[temp_result_key] = shear_force
    
    # 선택된 요소 번호와 위치 저장
    element_number = selected_row['Elem']
    element_part = selected_row.get('Part', 'N/A')
    if is_second == False:
        st.session_state['final_element'] = final_element
    st.session_state[f"element_number_{force_type}"] = element_number
    st.session_state[f"temp_element_number_{force_type}"] = element_number
    st.session_state[f"element_part_{force_type}"] = element_part
    st.session_state[f"temp_element_part_{force_type}"] = element_part
    
    # # 성공 메시지 error
    # st.toast(f"{force_type} shear force value loaded: {shear_force:.3f} kN (Element number: {element_number}, Location: {element_part})")

#전단에대한 단면속성 불러오기
def on_apply_shear_force_import_notreinforced():
    """전단력 데이터 적용 시 섹션 특성도 함께 로드"""
    Vsdmax = st.session_state.get('temp_Vsdmax', 0)
    Vsdmin = st.session_state.get('temp_Vsdmin', 0)
    element_number_Vsdmax = st.session_state.get('temp_element_number_Vsdmax', '')
    element_part_Vsdmax = st.session_state.get('temp_element_part_Vsdmax', '')
    
    # 하중 케이스 키 동적으로 생성
    load_case_key = f"selected_load_case_Vsdmax"
    selected_load_case = st.session_state.get(load_case_key, '')

    # 섹션 특성 자동 로드 추가
    selected_elements = st.session_state.get('temp_Select_Elements_shear', '')
    
    if selected_elements:
        section_properties = get_section_properties_from_elements(selected_elements)
        
        if section_properties:
            # 섹션 특성을 세션 상태에 저장 (get_ 접두사 사용) 일반전단
            st.session_state.get_d = section_properties.get('girder_height', 0)  # 또는 실제 키 이름
            st.session_state.get_bw = section_properties.get('bw', 0)
            st.session_state.get_Qn = section_properties.get('qn_girder_totcenter', 0)
            st.session_state.get_J = section_properties.get('iyy_girder', 0)
            st.session_state.get_total_centroid_height = section_properties.get('total_centroid_height', 0)
            st.session_state.get_girder_centroid_height = section_properties.get('girder_centroid_height', 0)
            st.session_state.get_girder_height = section_properties.get('girder_height', 0)
            st.session_state.get_slab_height = section_properties.get('slab_height', 0)
            st.session_state.get_total_height = section_properties.get('total_height', 0)
            st.session_state.get_total_area = section_properties.get('total_area', 0)
            st.session_state.get_total_first_moment = section_properties.get('total_first_moment', 0)
            st.session_state.get_iyy_total = section_properties.get('iyy_total', 0)
            st.session_state.get_slab_d = section_properties.get('slab_height', 0)

            st.success("Section properties have been automatically loaded.")
        else:
            st.warning("Unable to load section properties. Using default values.")

    # 기존 전단력 데이터 저장 로직
    apply_stress_data(
        'civil_shear_force_import', 
        'V', 
        temp_Vsdmax=Vsdmax,
        temp_Vsdmin=Vsdmin,
        Vsdmax=Vsdmax,  # 세션 상태에 직접 저장
        Vsdmin=Vsdmin,  # 세션 상태에 직접 저장
        element_number_Vsdmax=element_number_Vsdmax,
        element_part_Vsdmax=element_part_Vsdmax,
        shear_load_case=selected_load_case,  # 하중 케이스 추가
        # 섹션 특성도 함께 저장
        get_d=st.session_state.get('get_d', 0),
        get_bw=st.session_state.get('get_bw', 0),
        get_Qn=st.session_state.get('get_Qn', 0),
        get_J=st.session_state.get('get_J', 0),
        get_total_centroid_height=st.session_state.get('get_total_centroid_height', 0),
        get_girder_centroid_height=st.session_state.get('get_girder_centroid_height', 0),
        get_girder_height=st.session_state.get('get_girder_height', 0),
        get_total_area=st.session_state.get('get_total_area', 0),
        get_total_first_moment=st.session_state.get('get_total_first_moment', 0),
        get_iyy_total=st.session_state.get('get_iyy_total', 0),
        get_slab_height=st.session_state.get('get_slab_height', 0),
        get_total_height=st.session_state.get('get_total_height', 0)
    )
# 전단모달 보강불필요 끝-------------------------------------------------------------------------------------------




#전단하중 보강필요 불러오기 ---------------------------------------------------------------------------------------------------
def create_shear_force_reqreinf_import_dialog(dialog_title=""):
   
    @st.dialog(dialog_title)
    def import_dialog(item):
        # 세션 상태 초기화
        initialize_import_state()
        
        st.write("Shear Force Data Import")
        
        # Vsd 입력 섹션
        expandoption = not st.session_state.get('temp_Vsd', 0)
        with st.expander(f"**Vsd (Maximum Shear Force) = {st.session_state.get('temp_Vsd', 0)} kN**", expanded=expandoption):
            show_element_selection_for_shear_force('Vsd', 'temp_Select_Elements_shear', 'on_select_elements_shear', is_second=False)
        
        # 적용 버튼
        if st.button("Apply", type="primary", on_click=on_apply_shear_force_import, 
                    disabled=not st.session_state.get('temp_Vsd', 0), use_container_width=True):
            st.rerun()
    
    return import_dialog

#전단력 불러오는 모달 내용
def show_element_selection_for_shear_force(force_type, elements_key, select_callback, is_second=False):
    """요소 선택 및 전단력 데이터 로드 섹션 표시"""
    col1, col2 = st.columns([0.3, 0.7])
    
    # 요소 선택 버튼
    with col1:
        if not is_second:  # 두 번째 입력 필드(Vsdmin)에서는 요소 선택 버튼 숨기기
            button_key = f"import_elements_btn_{force_type}"
            #마이다스 에서 요소선택 버튼
            if st.button("Elements Import", type="secondary", on_click=lambda: get_Select_Elements(elements_key), key=button_key):
                pass
    
    # 선택된 요소 표시
    with col2:
        elements_value = st.session_state.get(elements_key, "")
        display_text = "Select Elements from MidasCivil" if not elements_value else elements_value
        input_key = f"selected_elements_input_{force_type}"
        st.text_input("Selected Elements From Midas Civil", display_text, disabled=True, key=input_key)
    
    # 하중 케이스 및 기타 옵션 선택
    load_case_key = f"selected_load_case_{force_type}"
    section_key = f"selected_section_{force_type}"
    location_key = f"selected_location_{force_type}"
    #전단력 불러오기 하중케이스 선택
    # (CB가 포함된 하중 케이스만 필터링
    st.session_state.civil_shear_load_cases_data = [case for case in st.session_state.civil_load_cases_data if '(MV' in case]
    
    # 필터링된 결과가 없는 경우 에러 메시지 표시
    if not st.session_state.civil_shear_load_cases_data:
        st.error("No load cases containing (MV) found. Please check the load case.")
    st.selectbox("Load Case", options=list(st.session_state.civil_shear_load_cases_data), key=load_case_key)

    # st.selectbox("단면 위치", options=("Part 1", "Part 2"), key=section_key)
    #st.selectbox("선택 위치", options=("Maximum", "Minimum", "Absolute Maximum","Absolute Minimum", "Part I", "Part J"), key=location_key, disabled=True)
    st.session_state[location_key] = "Maximum"
    
    # 부호 선택 은 여기서는 필요없어서 주석처리하고 모든값으로 강제로 넣음
    # sign_key = f"selected_sign_{force_type}"
    # st.selectbox("부호 선택", options=("모든 값", "양수만", "음수만"), index=0, key=sign_key)
    sign_key = f"selected_sign_{force_type}"
    if sign_key not in st.session_state:
        st.session_state[sign_key] = "모든 값"
    # 데이터 로드 버튼
    button_key = f"load_data_btn_{force_type}"
    # 에러 메시지 표시 (Simple method 모달 내에서만)
    error_key = f"error_{force_type}"
    check  = connect_check()

    if error_key in st.session_state and st.session_state[error_key]:
        st.error(st.session_state[error_key])
        st.session_state[error_key] = ""  # 에러 메시지 초기화
    
    # 일반 경고 메시지 표시 (모달 내에서)
    warning_key = f"warning_{force_type}"
    if warning_key in st.session_state and st.session_state[warning_key]:
        st.warning(st.session_state[warning_key])
        st.session_state[warning_key] = ""  # 경고 메시지 초기화

    st.button("Load Data", type="secondary", 
            on_click=lambda: load_shear_force_data(force_type, elements_key, load_case_key, 
                                               section_key, location_key, sign_key, is_second), 
            disabled=not st.session_state.get(elements_key, ""), 
            use_container_width=True, key=button_key)


def load_shear_force_data(force_type, elements_key, load_case_key, section_key, location_key, sign_key, is_second=False):
    """Midas Civil에서 전단력 데이터 불러오기 (Z방향만)"""
    # API 설정 가져오기
    mapi_key = st.session_state.get('current_mapi_key', '')
    base_url = st.session_state.get('current_base_url', '')
    
    if not mapi_key or not base_url:
        st.error("API settings not found. Please login first.")
        return
        
    headers = {"MAPI-Key": mapi_key}
    
    # 결과 저장 키 설정
    result_key = force_type
    temp_result_key = f"temp_{force_type}"
    
    # 선택된 요소 및 하중 케이스 가져오기
    try:
        selected_elements = [int(x) for x in st.session_state.get(elements_key, '').split(',') if x.strip()]
        if not selected_elements:
            st.session_state[f"error_{force_type}"] = "No selected elements."

            return
        st.session_state[elements_key] = ','.join(map(str, selected_elements))
    except Exception as e:
        st.error(f"Cannot process selected element list: {str(e)}")
        return
    
    selected_load = st.session_state.get(load_case_key, '')
    selected_section = st.session_state.get(section_key, '')
    selected_location = st.session_state.get(location_key, '')
    selected_sign = st.session_state.get(sign_key, "모든 값")
    
    # 하중 케이스 형식 표준화 (괄호와 접두어 제거)
    selected_load_result = selected_load
    for prefix in ['CBC:', 'CB:', 'MV:', 'CBSM:', '(CB)', '(MV)', '(CBC)', '(CBSM)']:
        selected_load_result = selected_load_result.replace(prefix, '')
    
    # civil_result_force_df 확인
    if 'civil_result_force_df' not in st.session_state:
        st.session_state[f"error_{force_type}"] = "civil_result_force_df not found. Please load the data first."
        return
        
    df = st.session_state.civil_result_force_df
    
    if df.empty:
        st.session_state[f"error_{force_type}"] = "Member force data is empty. Please load the data first."
        return
    
    # 선택된 요소로 필터링
    df = df[df['Elem'].astype(str).isin([str(e) for e in selected_elements])]
    
    # 선택된 하중 케이스로 필터링
    df = df[df['Load'] == selected_load_result]
    
    if df.empty:
        st.session_state[f"error_{force_type}"] = f"No data found for selected elements and load case."
        return
    # print((list(df.columns)))
    # # 섹션 파트 필터링

    
    # 전단력 컬럼 처리
    if 'Shear-z' not in df.columns:
        st.session_state[f"error_{force_type}"] = "Z-direction shear force column (Shear-z) not found in data."
        return
    
    # 전단력 값을 숫자로 변환
    df['Shear-z'] = pd.to_numeric(df['Shear-z'], errors='coerce')
    
    # 부호 선택에 따라 필터링
    if selected_sign == "양수만":
        df_filtered = df[df['Shear-z'] > 0]
        if df_filtered.empty:
            st.session_state[f"error_{force_type}"] = "No positive shear force values."
            return
        df = df_filtered
    elif selected_sign == "음수만":
        df_filtered = df[df['Shear-z'] < 0]
        if df_filtered.empty:
            st.session_state[f"error_{force_type}"] = "No negative shear force values."
            return
        df = df_filtered

    # 위치별로 필터링
    if selected_location not in ["Maximum", "Minimum", "Absolute Maximum", "Absolute Minimum"]:
        # "Part I", "Part J" 등으로 필터링
        location_part = selected_location.split()[-1]  # "Part I" -> "I" 추출
        
        # 부분 문자열 매칭 사용 (I[숫자]와 같은 형식 처리)
        # df['Part']가 문자열이 아닐 경우를 대비한 안전 처리
        if 'Part' in df.columns:
            df_filtered = df[df['Part'].astype(str).str.startswith(location_part)]
            if df_filtered.empty:
                st.session_state[f"error_{force_type}"] = f"No data found for selected location."
                try:
                    possible_parts = df['Part'].unique()
                    st.write("Possible location values:")
                except:
                    st.session_state[f"error_{force_type}"] = "Please check the data structure."
                return
            df = df_filtered
        else:
            st.session_state[f"error_{force_type}"] = "'Part' column not found in data."
            return
    if is_second:
        selected_location = "Absolute Minimum"
    else:
        selected_location = "Absolute Maximum"

    # 선택에 따른 값 결정
    try:
        if selected_location == "Maximum":
            # 최대값 찾기
            idx = df['Shear-z'].idxmax()
        elif selected_location == "Minimum":
            # 최소값 찾기
            idx = df['Shear-z'].idxmin()
        elif selected_location == "Absolute Maximum":
            # 절대값 기준 최대값 찾기
            idx = df['Shear-z'].abs().idxmax()
        elif selected_location == "Absolute Minimum":
            # 절대값 기준 최소값 찾기
            idx = df['Shear-z'].abs().idxmin()
        else:
            # 기본 선택 (force_type에 따라)
            if force_type == 'Vsdmax':
                # 최대 전단력 (절대값이 가장 큰 값)
                idx = df['Shear-z'].abs().idxmax()
            else:  # Vsdmin
                # 최소 전단력 (절대값이 가장 작은 값)
                idx = df['Shear-z'].abs().idxmin()
    except Exception as e:
        # st.error(f"Error calculating shear force: {str(e)}")
        return
    
    # 선택된 행 가져오기
    selected_row = df.loc[idx]
    
    # 전단력 값 가져오기
    shear_force = selected_row['Shear-z']
    
    # 부호를 유지한 전단력 값 저장
    st.session_state[result_key] = shear_force

    st.session_state[temp_result_key] = shear_force
    
    # 선택된 요소 번호와 위치 저장
    element_number = selected_row['Elem']
    element_part = selected_row.get('Part', 'N/A')
    
    st.session_state[f"element_number_{force_type}"] = element_number
    st.session_state[f"temp_element_number_{force_type}"] = element_number
    st.session_state[f"element_part_{force_type}"] = element_part
    st.session_state[f"temp_element_part_{force_type}"] = element_part
    
    # # 성공 메시지
    # st.toast(f"{force_type} shear force value loaded: {shear_force:.3f} kN (Element number: {element_number}, Location: {element_part})")


def on_apply_shear_force_import():
    """전단력 데이터 적용"""
    Vsdmax = st.session_state.get('temp_Vsdmax', 0)
    Vsdmin = st.session_state.get('temp_Vsdmin', 0)
    element_number_Vsdmax = st.session_state.get('temp_element_number_Vsdmax', '')
    element_part_Vsdmax = st.session_state.get('temp_element_part_Vsdmax', '')
    # 하중 케이스 키 동적으로 생성
    load_case_key = f"selected_load_case_Vsdmax"
    selected_load_case = st.session_state.get(load_case_key, '')

    apply_stress_data(
        'civil_shear_force_import', 
        'V', 
        temp_Vsdmax=Vsdmax,
        temp_Vsdmin=Vsdmin,
        Vsdmax=Vsdmax,  # 세션 상태에 직접 저장
        Vsdmin=Vsdmin,  # 세션 상태에 직접 저장
        element_number_Vsdmax=element_number_Vsdmax,
        element_part_Vsdmax=element_part_Vsdmax,
        shear_load_case=selected_load_case  # 하중 케이스 추가
    )
# 전단모달 필요 끝-------------------------------------------------------------------------------------------

#------------------------------------------------------모멘트 불러오기
def create_moment_reqreinf_import_dialog(dialog_title="Midas Civil 모멘트 가져오기"):
    """모멘트 데이터 임포트를 위한 모달 다이얼로그 생성"""
    
    @st.dialog(dialog_title)
    def import_dialog(item):
        # 세션 상태 초기화
        initialize_import_state()
        
        # st.write("Moment Data Import")
        
        # Msd 입력 섹션
        expandoption = not st.session_state.get('temp_Msd', 0)
        with st.expander(f"**Msd = {st.session_state.get('temp_Msd', 0)} kN·m**", expanded=expandoption):
            show_element_selection_for_moment_force('Msd', 'temp_Select_Elements_moment', 'on_select_elements_moment', is_second=False)
        
        # 적용 버튼
        if st.button("Apply", type="primary", on_click=on_apply_moment_force_reqreinf_import, 
                    disabled=not st.session_state.get('temp_Msd', 0), use_container_width=True):
            st.rerun()
    
    return import_dialog

def show_element_selection_for_moment_force(force_type, elements_key, select_callback, is_second=False):
    """요소 선택 및 모멘트 데이터 로드 섹션 표시"""
    col1, col2 = st.columns([0.3, 0.7])
    
    # 요소 선택 버튼
    with col1:
        if not is_second:  # 두 번째 입력 필드에서는 요소 선택 버튼 숨기기
            button_key = f"import_elements_btn_{force_type}"
            if st.button("Elements Import", type="secondary", on_click=lambda: get_Select_Elements(elements_key), key=button_key):
                pass
    
    # 선택된 요소 표시
    with col2:
        elements_value = st.session_state.get(elements_key, "")
        display_text = "Select Elements From Midas Civil" if not elements_value else elements_value
        input_key = f"selected_elements_input_{force_type}"
        st.text_input("Selected Elements From Midas Civil", display_text, disabled=True, key=input_key)
    
    # 하중 케이스 및 기타 옵션 선택
    load_case_key = f"selected_load_case_{force_type}"
    section_key = f"selected_section_{force_type}"
    location_key = f"selected_location_{force_type}"
    
    # 모멘트 하중 케이스 선택 (MV 하중 케이스만 필터링)
    st.session_state.civil_moment_load_cases_data = [case for case in st.session_state.civil_load_cases_data if '(MV' in case]
    
    # 필터링된 결과가 없는 경우 에러 메시지 표시
    if not st.session_state.civil_moment_load_cases_data:
        st.error("No load cases containing (MV) found. Please check the load case.")
    # 에러 메시지 표시 (Simple method 모달 내에서만)
    error_key = f"error_{force_type}"
    if error_key in st.session_state and st.session_state[error_key]:
        st.error(st.session_state[error_key])
        st.session_state[error_key] = ""  # 에러 메시지 초기화
    
    # 일반 경고 메시지 표시 (모달 내에서)
    warning_key = f"warning_{force_type}"
    if warning_key in st.session_state and st.session_state[warning_key]:
        st.warning(st.session_state[warning_key])
        st.session_state[warning_key] = ""  # 경고 메시지 초기화
    st.selectbox("Load Case", options=list(st.session_state.civil_moment_load_cases_data), key=load_case_key)

    # 위치 고정
    st.session_state[location_key] = "Maximum"
    
    # 부호 설정
    sign_key = f"selected_sign_{force_type}"
    if sign_key not in st.session_state:
        st.session_state[sign_key] = "모든 값"
    
    # 데이터 로드 버튼
    button_key = f"load_data_btn_{force_type}"
    st.button("Load Data", type="secondary", 
            on_click=lambda: load_moment_force_data(force_type, elements_key, load_case_key, 
                                               section_key, location_key, sign_key, is_second), 
            disabled=not st.session_state.get(elements_key, ""), 
            use_container_width=True, key=button_key)

def load_moment_force_data(force_type, elements_key, load_case_key, section_key, location_key, sign_key, is_second=False):
    """Midas Civil에서 모멘트 데이터 불러오기 (Z방향만)"""
    # API 설정 가져오기
    mapi_key = st.session_state.get('current_mapi_key', '')
    base_url = st.session_state.get('current_base_url', '')
    
    if not mapi_key or not base_url:
        st.error("API settings not found. Please login first.")
        return
        
    headers = {"MAPI-Key": mapi_key}
    
    # 결과 저장 키 설정
    result_key = force_type
    temp_result_key = f"temp_{force_type}"
    
    # 선택된 요소 및 하중 케이스 가져오기
    try:
        selected_elements = [int(x) for x in st.session_state.get(elements_key, '').split(',') if x.strip()]
        if not selected_elements:
            st.session_state[f"error_{force_type}"] = "No selected elements"
            return
        st.session_state[elements_key] = ','.join(map(str, selected_elements))
    except Exception as e:
        st.session_state[f"error_{force_type}"] = f"Cannot process selected element list: {str(e)}"
        return
    
    selected_load = st.session_state.get(load_case_key, '')
    selected_section = st.session_state.get(section_key, '')
    selected_location = st.session_state.get(location_key, '')
    selected_sign = st.session_state.get(sign_key, "모든 값")
    
    # 하중 케이스 형식 표준화 (괄호와 접두어 제거)
    selected_load_result = selected_load
    for prefix in ['CBC:', 'CB:', 'MV:', 'CBSM:', '(CB)', '(MV)', '(CBC)', '(CBSM)']:
        selected_load_result = selected_load_result.replace(prefix, '')
    
    # civil_result_force_df 확인
    if 'civil_result_force_df' not in st.session_state:
        st.session_state[f"error_{force_type}"] = "civil_result_force_df not found. Please load the data first."
        return
        
    df = st.session_state.civil_result_force_df
    
    if df.empty:
        st.session_state[f"error_{force_type}"] = "Member force data is empty. Please load the data first."
        return
    
    # 선택된 요소로 필터링
    df = df[df['Elem'].astype(str).isin([str(e) for e in selected_elements])]
    
    # 선택된 하중 케이스로 필터링
    df = df[df['Load'] == selected_load_result]
    
    if df.empty:
        st.session_state[f"error_{force_type}"] = f"No data found for selected elements ({selected_elements}) and load case ({selected_load_result})."
        return

    # 모멘트 컬럼 처리
    if 'Moment-y' not in df.columns:
        st.session_state[f"error_{force_type}"] = "Z-direction moment column (Moment-y) not found in data."
        return
    
    # 모멘트 값을 숫자로 변환
    df['Moment-y'] = pd.to_numeric(df['Moment-y'], errors='coerce')
    
    # 부호 선택에 따라 필터링
    if selected_sign == "양수만":
        df_filtered = df[df['Moment-y'] > 0]
        if df_filtered.empty:
            st.session_state[f"error_{force_type}"] = "No positive moment values."
            return
        df = df_filtered
    elif selected_sign == "음수만":
        df_filtered = df[df['Moment-y'] < 0]
        if df_filtered.empty:
            st.session_state[f"error_{force_type}"] = "No negative moment values."
            return
        df = df_filtered

    # 위치별로 필터링
    if selected_location not in ["Maximum", "Minimum", "Absolute Maximum", "Absolute Minimum"]:
        # "Part I", "Part J" 등으로 필터링
        location_part = selected_location.split()[-1]  # "Part I" -> "I" 추출
        
        # 부분 문자열 매칭 사용
        if 'Part' in df.columns:
            df_filtered = df[df['Part'].astype(str).str.startswith(location_part)]
            if df_filtered.empty:
                st.session_state[f"error_{force_type}"] = f"No data found for selected location ({selected_location})."
                try:
                    possible_parts = df['Part'].unique()
                    st.session_state[f"error_{force_type}"] = f"Possible location values: {possible_parts}"
                except:
                    st.session_state[f"error_{force_type}"] = "Please check the data structure."
                return
            df = df_filtered
        else:
            st.session_state[f"error_{force_type}"] = "'Part' column not found in data."
            return

    # 위치에 따른 모멘트 값 선택
    try:
        if selected_location == "Maximum":
            idx = df['Moment-y'].idxmax()
        elif selected_location == "Minimum":
            idx = df['Moment-y'].idxmin()
        elif selected_location == "Absolute Maximum":
            idx = df['Moment-y'].abs().idxmax()
        elif selected_location == "Absolute Minimum":
            idx = df['Moment-y'].abs().idxmin()
        else:
            idx = df['Moment-y'].abs().idxmax()
    except Exception as e:
        st.session_state[f"error_{force_type}"] = f"Error calculating moment: {str(e)}"
        return
    
    # 선택된 행 가져오기
    selected_row = df.loc[idx]
    
    # 모멘트 값 가져오기
    moment_force = selected_row['Moment-y']
    
    # 모멘트 값 저장
    st.session_state[result_key] = moment_force
    st.session_state[temp_result_key] = moment_force
    
    # 선택된 요소 번호와 위치 저장
    element_number = selected_row['Elem']
    element_part = selected_row.get('Part', 'N/A')
    
    st.session_state[f"element_number_{force_type}"] = element_number
    st.session_state[f"temp_element_number_{force_type}"] = element_number
    st.session_state[f"element_part_{force_type}"] = element_part
    st.session_state[f"temp_element_part_{force_type}"] = element_part
    
    # # 성공 메시지
    # st.success(f"{force_type} moment value loaded: {moment_force:.3f} kN·m (element number: {element_number}, location: {element_part})")

def on_apply_moment_force_reqreinf_import():
    """모멘트 데이터 적용"""
    Msd = st.session_state.get('temp_Msd', 0)
    element_number_Msd = st.session_state.get('temp_element_number_Msd', '')
    element_part_Msd = st.session_state.get('temp_element_part_Msd', '')
    
    load_case_key = f"selected_load_case_Msd"
    selected_load_case = st.session_state.get(load_case_key, '')

    apply_stress_data(
        'civil_moment_force_reqreinf_import', 
        'M', 
        temp_Msd=Msd,
        Msd=Msd,
        element_number_Msd=element_number_Msd,
        element_part_Msd=element_part_Msd,
        moment_load_case=selected_load_case
    )
#------------------------------------------------------모멘트끝




class cal_for_rail_desm:
    """콘크리트 피로 계산을 위한 클래스"""
    
    @staticmethod
    def update_fcm_and_calculate_fcd():
        """fcm 값을 업데이트하고 fcd 계산"""
        try:
            # fcm 값 가져오기
            fcm = st.session_state.fcm
            factor_rcfat = st.session_state.factor_rcfat
            
            # fcd 계산
            fcd = fcm / factor_rcfat
            
            # fcd 값 세션에 저장
            st.session_state.fcd = fcd
            
            # temp_result_df에 fcd 저장 (update_temp_from_input 함수 사용)
            update_temp_from_input('fcd')
            
            return fcd
        except Exception as e:
            st.error(f"Error calculating fcd: {str(e)}")
            return None
    
    @staticmethod
    def calculate_all_lambdas_concrete_rail():
        """모든 람다 계산"""
        try:
            fck = st.session_state.fck
            # 필요한 입력값 가져오기
            fcm = st.session_state.fcm
            scmax71 = st.session_state.scmax71
            scperm = st.session_state.scperm
            ds1 = st.session_state.ds1
            ds12 = st.session_state.ds12
            span_length = st.session_state.span_length
            nyear = st.session_state.nyear
            vol = st.session_state.vol
            nc = st.session_state.nc
            nt = st.session_state.nt
            support = st.session_state.sp
            zone_type = st.session_state.az
            traffic = st.session_state.tt
            
            # fcd 값 확인 또는 계산
            if 'fcd' not in st.session_state:
                factor_rcfat = st.session_state.factor_rcfat
                fcd = fcm / factor_rcfat
                st.session_state.fcd = fcd
            else:
                fcd = st.session_state.fcd
            if st.session_state.correction_factor_auto_calculate == True :
                # lambda0 계산
                if zone_type == "Compression zone":
                    lambda0 = 0.94 + 0.2 * (scperm / fcd)
                else:
                    lambda0 = 1.0
                
                # lambda1 계산
                from projects.concrete_fatigue_analysis_ntc2018.calc.railway_concrete_lambda import get_lambda1_rail
                lambda1 = get_lambda1_rail(support, zone_type, span_length, traffic)
                
                # lambda2 계산
                import math
                lambda2 = 1 + 1/8 * math.log10(vol / 25000000)
                
                # lambda3 계산
                lambda3 = 1 + 1/8 * math.log10(nyear / 100)
                n=0.12    
                # lambda4 계산
                judgement_a = ds1 / ds12 if ds12 != 0 else 0
                if judgement_a <= 0.8:
                    print(1 + 1/8 * math.log10(n))
                    lambda4 = max(1 + 1/8 * math.log10(n),0.54)
                else:
                    lambda4 = 1
            else:
                lambda0 = st.session_state.get('lambda0', 0)
                lambda1 = st.session_state.get('lambda1', 0)
                lambda2 = st.session_state.get('lambda2', 0)
                lambda3 = st.session_state.get('lambda3', 0)
                lambda4 = st.session_state.get('lambda4', 0)
            # lambdac 계산
            lambdac = lambda0 * lambda1 * lambda2 * lambda3 * lambda4
            
            # calc_ 접두사를 사용하여 계산된 값 저장
            st.session_state.calc_lambda0 = lambda0
            st.session_state.calc_lambda1 = lambda1
            st.session_state.calc_lambda2 = lambda2
            st.session_state.calc_lambda3 = lambda3
            st.session_state.calc_lambda4 = lambda4
            st.session_state.calc_lambdac = lambdac
            
            # 추가 계산 - sigma_cd_max_equ
            sigma_cd_max_equ = scperm + lambdac * (abs(scmax71) - scperm)
            st.session_state.sigma_cd_max_equ = sigma_cd_max_equ
            
            # sigma_cd_min_equ 계산
            sigma_cd_min_equ = scperm + lambdac * (scperm - 0)
            st.session_state.sigma_cd_min_equ = sigma_cd_min_equ
            
            # scd_max_equ 계산
            scd_max_equ = sigma_cd_max_equ / fcd
            st.session_state.scd_max_equ = scd_max_equ
            
            # scd_min_equ 계산
            scd_min_equ = sigma_cd_min_equ / fcd
            st.session_state.scd_min_equ = scd_min_equ
            
            # 판정값 계산
            requ = scd_min_equ / scd_max_equ
            discriminant_rail_des = 14 * ((1 - scd_max_equ) / (1 - requ) ** 0.5)
            
            try:
                if float(discriminant_rail_des.real) >= 6:
                    is_ok = "OK"
                else:
                    is_ok = "NG"
            except:
                is_ok = "NG"
            st.session_state.is_ok = is_ok
            st.session_state.requ = requ
            st.session_state.discriminant_rail_des = discriminant_rail_des
            
            # 세션 상태에서 temp_result_df로 값 복사
            for calc_key, save_key in [
                ('calc_lambda0', 'lambda0'),
                ('calc_lambda1', 'lambda1'),
                ('calc_lambda2', 'lambda2'),
                ('calc_lambda3', 'lambda3'),
                ('calc_lambda4', 'lambda4'),
                ('calc_lambdac', 'lambdac'),
                ('sigma_cd_max_equ', 'sigma_cd_max_equ'),
                ('sigma_cd_min_equ', 'sigma_cd_min_equ'),
                ('scd_max_equ', 'scd_max_equ'),
                ('scd_min_equ', 'scd_min_equ'),
                ('requ', 'requ'),
                ('discriminant_rail_des', 'discriminant_rail_des'),
                ('fcd', 'fcd'), ('is_ok', 'is_ok'), ('fck', 'fck')
            ]:
                if calc_key in st.session_state and 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
                    st.session_state.temp_result_df.loc[0, save_key] = st.session_state[calc_key]
            
            st.toast("✅ Lambda coefficients calculated successfully! ")
            
        except Exception as e:
            st.toast(f"⚠️ Warning: An error occurred while calculating Lambda coefficients: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


class SessionManager:
    @staticmethod
    def initialize():
        """세션 상태 초기화"""
        # 기존 초기화 코드...
        pass
    #하중 불러오기
    @staticmethod
    def initialize_import_dialogs():
        """임포트 모달 다이얼로그 초기화"""
        return {
            'regular_stress': create_stress_import_dialog("Stress Import", "regular_stress"),
            'simple_stress': create_simple_stress_import_dialog("Stress Import for Simple Method"),
            'moving_stress': create_stress_import_dialog("Moving Load Import (For Rail Fatigue Correction Factor)", "moving_stress"),
            'shear_force': create_shear_force_import_dialog("Shear Force Import"),  
            'steel_stress': create_steel_stress_import_dialog("Steel Direct Stress Import"),
            'steel_shear_force': create_steel_shear_force_import_dialog("Shear Force Import For Steel Girder"),
            'force': create_stress_import_dialog("Load Import", "force"),
            'shear_force_reqreinf': create_shear_force_reqreinf_import_dialog("Shear Force Import"), # Concrete Shear [Require Reinforcement]
            'road_noncracked_stress': create_stress_import_dialog("Reinforcing Steel Stress Import", "road_noncracked_stress"),
            'moment_force_reqreinf': create_moment_reqreinf_import_dialog("Moment Data Import"),
        }
    
    @staticmethod
    def get_lambda_value(lambda_name, default=0.0):
        """세션 상태나 temp_result_df에서 lambda 값을 가져오는 함수"""
        # 수정 모드인 경우 세션 상태에서 값을 가져옴
        if st.session_state.get('edit_mode', False):
            return float(st.session_state.get(lambda_name, default))
        
        # temp_result_df에서 값을 가져오려고 시도
        try:
            temp_df = st.session_state.get('temp_result_df', pd.DataFrame())
            if not temp_df.empty and 'case_id' in temp_df.columns and lambda_name in temp_df.columns:
                case_name = st.session_state.get('fatigue_case_name')
                filtered_df = temp_df[temp_df["case_id"] == case_name]
                if not filtered_df.empty:
                    return float(filtered_df[lambda_name].iloc[0])
        except Exception:
            pass
        
        return default
    


class FetchCivilData:
    """Midas Civil 데이터 로드 및 관리 클래스"""
    
    @staticmethod
    def initialize_civil_data():
        """Midas Civil 데이터 초기화 (앱 시작 시 한 번만 실행)"""
        # 기본값 설정
        if 'civil_load_cases_data' not in st.session_state:
            st.session_state['civil_load_cases_data'] = []
        if 'civil_result_df' not in st.session_state:
            st.session_state['civil_result_df'] = pd.DataFrame()
        if 'civil_all_element_data' not in st.session_state:
            st.session_state['civil_all_element_data'] = pd.DataFrame()
        if 'civil_result_force_df' not in st.session_state:
            st.session_state['civil_result_force_df'] = pd.DataFrame()
        if 'civil_result_conststage_df' not in st.session_state:
            st.session_state['civil_result_conststage_df'] = pd.DataFrame()
        if 'section_properties_df' not in st.session_state:
            st.session_state['section_properties_df'] = pd.DataFrame()

        # del_data 기본값 설정
        if 'conststage_del_data' not in st.session_state:
            st.session_state['conststage_del_data'] = 0

    @staticmethod
    def safe_api_request(url: str, headers: Dict[str, str], 
                        json_data: Optional[Dict[str, Any]] = None, 
                        method: str = "GET", 
                        delay: float = 0.5) -> Tuple[Optional[Dict[str, Any]], bool]:
        """
        안전한 API 요청을 위한 헬퍼 함수
        
        Args:
            url: API 엔드포인트 URL
            headers: 요청 헤더
            json_data: POST 요청 시 JSON 데이터
            method: HTTP 메서드 (GET 또는 POST)
            delay: 요청 간 지연 시간 (초)
        
        Returns:
            Tuple[API 응답 JSON 또는 None, 계속 진행 가능 여부]
        """
        try:
            # 요청 간 지연
            if delay > 0:
                time.sleep(delay)
            
            if method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json_data, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)
            
            response.raise_for_status()
            return response.json(), True
            
        except requests.exceptions.Timeout:
            # st.error(f"⏱️ **CRITICAL ERROR**: API request timeout for {url}")
            st.error("**Cannot proceed without this data. Please check your network connection and try again.**")
            return None, False
            
        except requests.exceptions.ConnectionError:
            # st.error(f"🔌 **CRITICAL ERROR**: Connection error for {url}")
            st.error("**Cannot proceed without this data. Please check your API connection and try again.**")
            return None, False
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            
            # 4xx 오류 (클라이언트 오류) - 중단해야 함
            if 400 <= status_code < 500:
                # st.error(f"❌ **CRITICAL ERROR**: HTTP {status_code} for {url}")
                if status_code == 400:
                    st.error("**Bad Request**: The request is malformed or invalid.")
                elif status_code == 401:
                    st.error("**Unauthorized**: Please check your API key.")
                elif status_code == 403:
                    st.error("**Forbidden**: You don't have permission to access this resource.")
                elif status_code == 404:
                    st.error("**Not Found**: The requested resource doesn't exist.")
                
                st.error("**Cannot proceed with invalid request. Please check your API settings and model data.**")
                return None, False
            
            # 5xx 오류 (서버 오류) - 재시도 가능하지만 일단 중단
            elif 500 <= status_code < 600:
                st.error(f"🚫 **SERVER ERROR**: HTTP {status_code} for {url}")
                st.error("**Server is experiencing issues. Please try again later.**")
                return None, False
            
            else:
                st.error(f"🚫 **HTTP ERROR**: {status_code} for {url}")
                return None, False
                
        except requests.exceptions.RequestException as e:
            st.error(f"🚫 **CRITICAL ERROR**: Request error for {url}: {str(e)}")
            st.error("**Cannot proceed without this data. Please check your connection and try again.**")
            return None, False
            
        except Exception as e:
            st.error(f"💥 **UNEXPECTED ERROR** for {url}: {str(e)}")
            st.error("**An unexpected error occurred. Cannot proceed safely.**")
            return None, False

    @staticmethod
    def fetch_element_data():
        """요소 데이터 가져오기"""
        try:
            # API 설정 가져오기
            mapi_key = st.session_state.get('current_mapi_key', '')
            base_url = st.session_state.get('current_base_url', '')
            
            if not mapi_key or not base_url:
                st.error("❌ **CRITICAL ERROR**: API settings not found. Please login first.")
                return None, False
                
            headers = {"MAPI-Key": mapi_key}
            
            # 요소 데이터 가져오기
            elem_data, can_continue = FetchCivilData.safe_api_request(f"{base_url}/db/elem", headers)
            
            if not can_continue:
                return None, False
            
            if elem_data and "ELEM" in elem_data:
                elements = []
                for elem_id, elem_info in elem_data["ELEM"].items():
                    element_row = {
                        "elem_id": elem_id,
                        "sect_id": elem_info.get("SECT", None),
                        "type": elem_info.get("TYPE", None),
                        "matl": elem_info.get("MATL", None)
                    }
                    elements.append(element_row)
                
                return pd.DataFrame(elements), True
            else:
                st.error("❌ **CRITICAL ERROR**: Failed to fetch element data - invalid response format")
                return None, False
                
        except Exception as e:
            st.error(f"💥 **CRITICAL ERROR**: Error fetching element data: {str(e)}")
            return None, False

    @staticmethod
    def fetch_load_cases_sequential(base_url: str, headers: Dict[str, str]) -> Tuple[list, bool]:
        """하중 케이스를 순차적으로 가져오기"""
        try:
            load_case_list = []
            
            # 1. STLD 데이터 (기본 하중 케이스) - 필수
            stld_data, can_continue = FetchCivilData.safe_api_request(f"{base_url}/db/stld", headers, delay=0.3)
            if not can_continue:
                st.error("❌ **CRITICAL ERROR**: Cannot load basic load cases (STLD). Process stopped.")
                return [], False
                
            if stld_data and "STLD" in stld_data:
                # CS 타입 제외
                filtered_stld = {k: v for k, v in stld_data["STLD"].items() 
                               if v.get("TYPE") != "CS"}
                load_case = [f"{filtered_stld[x].get('NAME', '')}({filtered_stld[x].get('TYPE', '')})" 
                           for x in filtered_stld]
                load_case_list.extend(load_case)
                st.success(f"✅ STLD: {len(load_case)} cases loaded")
            else:
                st.error("❌ **CRITICAL ERROR**: STLD data is invalid or missing. Cannot proceed.")
                return [], False
            
            # 2. 나머지 하중 케이스들 (선택적 - 오류가 있어도 계속 진행)
            optional_endpoints = [
                ("mvld", "MVLD"),
                ("mvldbs", "MVLDBS"),
                ("mvldeu", "MVLDEU"), 
                ("mvldpl", "MVLDPL")
            ]
            
            for endpoint, key in optional_endpoints:
                data, can_continue = FetchCivilData.safe_api_request(f"{base_url}/db/{endpoint}", headers, delay=0.3)
                if can_continue and data and key in data:
                    cases = []
                    for x in data[key]:
                        name = data[key][x].get('LCNAME', '')
                        cases.extend([f"{name}(MV:all)", f"{name}(MV:max)", f"{name}(MV:min)"])
                    load_case_list.extend(cases)
                    st.success(f"✅ {key}: {len(cases)} cases loaded")
                else:
                    # st.warning(f"⚠️ {key} load cases skipped due to error")
                    pass
            
            # 3. 조합 하중 케이스들 (선택적)
            combo_endpoints = [
                ("lcom-gen", "LCOM-GEN", "CB"),
                ("lcom-conc", "LCOM-CONC", "CBC"),
                ("lcom-stlcomp", "LCOM-STLCOMP", "CB"),
                ("lcom-seismic", "LCOM-SEISMIC", "CB")
            ]
            
            for endpoint, key, prefix in combo_endpoints:
                data, can_continue = FetchCivilData.safe_api_request(f"{base_url}/db/{endpoint}", headers, delay=0.3)
                if can_continue and data and key in data:
                    cases = []
                    for combo_key in data[key]:
                        name = data[key][combo_key].get('NAME', '')
                        if data[key][combo_key].get('bCB', '') == True:
                            cases.extend([
                                f"{name}({prefix}:all)",
                                f"{name}({prefix}:max)", 
                                f"{name}({prefix}:min)"
                            ])
                        else:
                            cases.append(f"{name}({prefix})")
                    load_case_list.extend(cases)
                    st.success(f"✅ {key}: {len(cases)} cases loaded")
                else:
                    # st.warning(f"⚠️ {key} load cases skipped due to error")
                    pass
            
            if len(load_case_list) == 0:
                st.error("❌ **CRITICAL ERROR**: No load cases loaded. Cannot proceed.")
                return [], False
                
            return load_case_list, True
            
        except Exception as e:
            st.error(f"💥 **CRITICAL ERROR**: Error loading load cases: {str(e)}")
            return [], False

    @staticmethod
    def fetch_stress_data_sequential(base_url: str, headers: Dict[str, str], 
                                   allelement: list, load_case_list: list) -> Tuple[Optional[pd.DataFrame], bool]:
        """응력 데이터를 순차적으로 가져오기"""
        try:
            request_data_stress = {
                "Argument": {
                    "TABLE_TYPE": "COMPSECTBEAMSTRESS",
                    "NODE_ELEMS": {
                        "KEYS": allelement
                    },
                    "UNIT": {
                        "FORCE": "N",
                        "DIST": "mm"
                    },
                    "LOAD_CASE_NAMES": load_case_list,
                    "PARTS": ["Part I", "Part J", "Part 1/4", "Part 2/4", "Part 3/4"],
                    "COMPONENTS": [
                        "Index", "Load", "Elem", "Section Part", "Part",
                        "Cb(min/max)", "Cb1(-y+z)", "Cb2(+y+z)", "Cb3(+y-z)", "Cb4(-y-z)"
                    ]
                }
            }
            
            result_data_stress, can_continue = FetchCivilData.safe_api_request(
                f"{base_url}/post/Table", 
                headers, 
                json_data=request_data_stress,
                method="POST",
                delay=1.0
            )
            
            if not can_continue:
                st.error("❌ **CRITICAL ERROR**: Failed to fetch stress data. Process stopped.")
                return pd.DataFrame(), False
            
            if (result_data_stress and 'empty' in result_data_stress and 
                'HEAD' in result_data_stress['empty'] and 
                'DATA' in result_data_stress['empty']):
                
                headers_stress = result_data_stress['empty']['HEAD']
                data_list_stress = []
                
                for row in result_data_stress['empty']['DATA']:
                    data_list_stress.append(dict(zip(headers_stress, row)))
                
                civil_result_df = pd.DataFrame(data_list_stress)
                st.success(f"✅ Stress data: {len(civil_result_df)} rows loaded")
                return civil_result_df, True
            else:
                st.error("❌ **CRITICAL ERROR**: Stress data format is incorrect. Cannot proceed.")
                return pd.DataFrame(), False
                
        except Exception as e:
            st.error(f"💥 **CRITICAL ERROR**: Error loading stress data: {str(e)}")
            return pd.DataFrame(), False

    @staticmethod
    def fetch_force_data_sequential(base_url: str, headers: Dict[str, str], 
                                  allelement: list, load_case_list: list) -> Tuple[Optional[pd.DataFrame], bool]:
        """부재력 데이터를 순차적으로 가져오기"""
        try:
            request_data_force = {
                "Argument": {
                    "TABLE_NAME": "BeamForce",
                    "TABLE_TYPE": "BEAMFORCE",
                    "UNIT": {
                        "FORCE": "kN",
                        "DIST": "m"
                    },
                    "STYLES": {
                        "FORMAT": "Fixed",
                        "PLACE": 12
                    },
                    "COMPONENTS": [
                        "Elem", "Load", "Part", "Axial", "Shear-y", "Shear-z",
                        "Torsion", "Moment-y", "Moment-z"
                    ],
                    "NODE_ELEMS": {
                        "KEYS": allelement
                    },
                    "LOAD_CASE_NAMES": load_case_list,
                    "PARTS": ["PartI", "PartJ"]
                }
            }
            
            result_data_force, can_continue = FetchCivilData.safe_api_request(
                f"{base_url}/post/Table", 
                headers, 
                json_data=request_data_force,
                method="POST",
                delay=1.0
            )
            
            if not can_continue:
                st.warning("⚠️ Member force data failed to load, but continuing with other data...")
                return pd.DataFrame(), True  # 부재력은 선택적이므로 계속 진행
            
            if (result_data_force and 'BeamForce' in result_data_force and
                'HEAD' in result_data_force['BeamForce'] and 
                'DATA' in result_data_force['BeamForce']):
                
                headers_force = result_data_force['BeamForce']['HEAD']
                data_rows = result_data_force['BeamForce']['DATA']
                
                data_list_force = []
                for row in data_rows:
                    if len(row) == len(headers_force):
                        data_list_force.append(dict(zip(headers_force, row)))
                
                civil_result_force_df = pd.DataFrame(data_list_force)
                st.success(f"✅ Member force data: {len(civil_result_force_df)} rows loaded")
                return civil_result_force_df, True
            else:
                st.warning("⚠️ Member force data format is incorrect, continuing without it...")
                return pd.DataFrame(), True
                
        except Exception as e:
            st.warning(f"⚠️ Error loading member force data: {str(e)}, continuing...")
            return pd.DataFrame(), True

    @staticmethod
    def fetch_construction_stage_data_sequential(base_url: str, headers: Dict[str, str], 
                                               allelement: list) -> Tuple[Optional[pd.DataFrame], bool]:
        """Construction Stage 데이터를 순차적으로 가져오기"""
        try:
            request_data_conststage = {
                "Argument": {
                    "TABLE_NAME": "BeamStress",
                    "TABLE_TYPE": "COMPSECTBEAMSTRESS",
                    "UNIT": {
                        "FORCE": "N",
                        "DIST": "mm"
                    },
                    "STYLES": {
                        "FORMAT": "Fixed",
                        "PLACE": 12
                    },
                    "COMPONENTS": [
                        "Elem", "DOF", "Load", "SectionPart", "Part", "Axial",
                        "Bend(+y)", "Bend(-y)", "Bend(+z)", "Bend(-z)",
                        "Cb(min/max)", "Cb1(-y+z)", "Cb2(+y+z)", "Cb3(+y-z)", "Cb4(-y-z)",
                        "Sax(Warping)1", "Sax(Warping)2", "Sax(Warping)3", "Sax(Warping)4"
                    ],
                    "NODE_ELEMS": {
                        "KEYS": allelement
                    },
                    "LOAD_CASE_NAMES": ["Summation(CS)"],
                    "PARTS": ["PartI", "PartJ"],
                    "OPT_CS": True
                }
            }
            
            result_data_conststage, can_continue = FetchCivilData.safe_api_request(
                f"{base_url}/post/Table", 
                headers, 
                json_data=request_data_conststage,
                method="POST",
                delay=1.0
            )
            
            if not can_continue:
                st.warning("⚠️ Construction Stage data failed to load, but continuing...")
                return pd.DataFrame(), True  # Construction Stage는 선택적
            
            if (result_data_conststage and 'BeamStress' in result_data_conststage and
                'HEAD' in result_data_conststage['BeamStress'] and 
                'DATA' in result_data_conststage['BeamStress']):
                
                headers_conststage = result_data_conststage['BeamStress']['HEAD']
                data_rows = result_data_conststage['BeamStress']['DATA']
                
                total_rows = len(data_rows)
                st.info(f"📊 Construction Stage data total rows: {total_rows}")
                
                data_list_conststage = []
                for row in data_rows:
                    if len(row) == len(headers_conststage):
                        data_list_conststage.append(dict(zip(headers_conststage, row)))
                
                civil_result_conststage_df = pd.DataFrame(data_list_conststage)
                st.success(f"✅ Construction Stage data: {len(civil_result_conststage_df)} rows loaded")
                return civil_result_conststage_df, True
            else:
                st.warning("⚠️ Construction Stage data format is incorrect, continuing without it...")
                return pd.DataFrame(), True
                
        except Exception as e:
            st.warning(f"⚠️ Error loading construction stage data: {str(e)}, continuing...")
            return pd.DataFrame(), True

    @staticmethod
    def fetch_civil_data():
        """모든 Midas Civil 데이터를 순차적으로 가져오기 (오류 시 중단)"""
        
        # API 설정 확인
        mapi_key = st.session_state.get('current_mapi_key', '')
        base_url = st.session_state.get('current_base_url', '')
        
        if not mapi_key or not base_url:
            st.error("❌ **CRITICAL ERROR**: API settings not found. Please login first.")
            return
        
        headers = {"MAPI-Key": mapi_key}
        
        try:
            # 1. 단면 속성 데이터 로드 (필수)
            if 'section_properties_df' not in st.session_state or st.session_state.section_properties_df.empty:
                with st.spinner("🔧 Loading section properties..."):
                    try:
                        from projects.concrete_fatigue_analysis_ntc2018.calc.section_calculate import fetch_and_process_section_data
                        section_df = fetch_and_process_section_data()
                        if not section_df.empty:
                            st.session_state.section_properties_df = section_df
                            st.success(f"✅ {len(section_df)} section properties loaded")
                        else:
                            st.error("❌ **CRITICAL ERROR**: No supported section types found!")
                            st.error("This model does not contain any COMPOSITE sections that are supported by the fatigue analysis.")
                            st.error("**Process stopped - cannot continue without valid sections.**")
                            st.stop()
                    except Exception as e:
                        st.error(f"❌ **CRITICAL ERROR**: Error loading section properties: {str(e)}")
                        st.error("**Process stopped - cannot continue without section data.**")
                        st.stop()

            # 2. 요소 데이터 로드 (필수)
            if 'civil_all_element_data' not in st.session_state or st.session_state.civil_all_element_data.empty:
                with st.spinner("🏗️ Fetching element data..."):
                    civil_result_df, can_continue = FetchCivilData.fetch_element_data()
                    if not can_continue:
                        st.error("**Process stopped - cannot continue without element data.**")
                        st.stop()
                        
                    if civil_result_df is not None:
                        # 섹션 필터링
                        if 'section_properties_df' in st.session_state and not st.session_state.section_properties_df.empty:
                            target_section_ids = st.session_state.section_properties_df['section_id'].tolist()
                            
                            if 'sect_id' in civil_result_df.columns:
                                civil_result_df['sect_id'] = pd.to_numeric(civil_result_df['sect_id'], errors='coerce')
                                target_section_ids = [int(sid) for sid in target_section_ids if str(sid).isdigit()]
                                
                                filtered_df = civil_result_df[civil_result_df['sect_id'].isin(target_section_ids)]
                                
                                if not filtered_df.empty:
                                    st.success(f"✅ {len(filtered_df)} elements data loaded (filtered by section properties)")
                                    civil_result_df = filtered_df
                                else:
                                    st.error("❌ **CRITICAL ERROR**: No elements found for target sections")
                                    st.error("**Process stopped - no valid elements to analyze.**")
                                    st.stop()
                        
                        st.session_state.civil_all_element_data = civil_result_df
                        
                        # 요소 ID 목록 생성
                        if not civil_result_df.empty:
                            allelement = list(map(int, civil_result_df['elem_id'].tolist()))
                            element_section_mapping = dict(zip(civil_result_df['elem_id'], civil_result_df['sect_id']))
                            st.session_state.element_section_mapping = element_section_mapping
                        else:
                            st.error("❌ **CRITICAL ERROR**: No elements available")
                            st.stop()
                    else:
                        st.error("**Process stopped - element data loading failed.**")
                        st.stop()
            else:
                civil_result_df = st.session_state.civil_all_element_data
                allelement = list(map(int, civil_result_df['elem_id'].tolist())) if not civil_result_df.empty else []
                if not allelement:
                    st.error("❌ **CRITICAL ERROR**: No elements available in session")
                    st.stop()

            # 3. 하중 케이스 순차적 로드 (필수)
            with st.spinner("📋 Loading load cases sequentially..."):
                load_case_list, can_continue = FetchCivilData.fetch_load_cases_sequential(base_url, headers)
                if not can_continue:
                    st.error("**Process stopped - cannot continue without load cases.**")
                    st.stop()
                    
                if load_case_list:
                    st.session_state.civil_load_cases_data = load_case_list
                    st.success(f"✅ Total {len(load_case_list)} load cases loaded")
                else:
                    st.error("❌ **CRITICAL ERROR**: No load cases loaded")
                    st.error("**Process stopped - cannot continue without load cases.**")
                    st.stop()

            # 4. 응력 데이터 순차적 로드 (필수)
            with st.spinner("📊 Loading stress data..."):
                stress_df, can_continue = FetchCivilData.fetch_stress_data_sequential(base_url, headers, allelement, load_case_list)
                if not can_continue:
                    st.error("**Process stopped - cannot continue without stress data.**")
                    st.stop()
                    
                if not stress_df.empty:
                    st.session_state.civil_result_df = stress_df
                else:
                    st.error("❌ **CRITICAL ERROR**: No stress data loaded")
                    st.error("**Process stopped - stress data is required for fatigue analysis.**")
                    st.stop()

            # 5. 부재력 데이터 순차적 로드 (선택적)
            with st.spinner("⚡ Loading member force data..."):
                force_df, can_continue = FetchCivilData.fetch_force_data_sequential(base_url, headers, allelement, load_case_list)
                if can_continue and not force_df.empty:
                    st.session_state.civil_result_force_df = force_df

            # 6. Construction Stage 데이터 순차적 로드 (선택적)
            with st.spinner("🏗️ Loading construction stage data..."):
                conststage_df, can_continue = FetchCivilData.fetch_construction_stage_data_sequential(base_url, headers, allelement)
                if can_continue and not conststage_df.empty:
                    st.session_state.civil_result_conststage_df = conststage_df

            st.success("🎉 **All critical data loaded successfully!**")
            st.info("You can now proceed with fatigue analysis.")

        except Exception as e:
            st.error(f"💥 **CRITICAL ERROR** in fetch_civil_data: {str(e)}")
            st.error("**Process stopped due to unexpected error.**")
            import traceback
            st.code(traceback.format_exc())
            st.stop()






def export_result_df_to_json():
    """result_df를 JSON으로 내보내기"""
    if 'result_df' not in st.session_state or st.session_state.result_df.empty:
        return None
    
    result_data = {
        "export_date": datetime.now().isoformat(),
        "analysis_results": st.session_state.result_df.to_dict('records')
    }
    
    return json.dumps(result_data, indent=2, ensure_ascii=False)

def import_result_df_from_json(uploaded_file):
    """JSON 파일에서 result_df 가져오기"""
    try:
        content = uploaded_file.getvalue().decode('utf-8')
        data = json.loads(content)
        
        if 'analysis_results' not in data:
            st.error("Invalid format")
            return False
        
        imported_df = pd.DataFrame(data['analysis_results'])
        
        if imported_df.empty:
            st.warning("No data found")
            return False
        
        # 기존 데이터와 병합
        if 'result_df' in st.session_state and not st.session_state.result_df.empty:
            st.session_state.result_df = pd.concat([st.session_state.result_df, imported_df], ignore_index=True)
        else:
            st.session_state.result_df = imported_df
        
        st.success(f"✅ Imported {len(imported_df)} cases")
        return True
        
    except Exception as e:
        st.error(f"Import failed: {str(e)}")
        return False

def display_import_export_buttons():
    """Import/Export 버튼 표시"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Export 버튼
        if 'result_df' in st.session_state and not st.session_state.result_df.empty:
            json_data = export_result_df_to_json()
            if json_data:
                filename = f"fatigue_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                st.download_button(
                    label="📤 Export",
                    data=json_data,
                    file_name=filename,
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.button("📤 Export", disabled=True, use_container_width=True)
    
    with col2:
        # Import 버튼만 (파일 선택 다이얼로그)
        # 이 버튼을 누르면 파일 업로드 영역 열림/닫힘
        if st.button("📥 Import", use_container_width=True):
            st.session_state.show_import = not st.session_state.get("show_import", False)

        # Import 모드일 때만 업로더 표시
        if st.session_state.get("show_import", False):
            uploader_holder = st.empty()  # 공간 확보

            uploaded_file = uploader_holder.file_uploader(
                "",
                type=["json"],
                key="import_json",
            )

            if uploaded_file is not None:
                # 처리 함수 호출 예: import_result_df_from_json()
                success = import_result_df_from_json(uploaded_file)
                if success:
                    # 업로드 완료 시 UI 제거
                    uploader_holder.empty()
                    st.session_state.show_import = False
                    st.rerun()



@staticmethod
def connect_check():
    """요소 데이터 가져오기"""
    try:

        mapi_key = st.session_state.get('current_mapi_key', '')
        base_url = st.session_state.get('current_base_url', '')
        
        if not mapi_key or not base_url:
            st.error("❌ **CRITICAL ERROR**: API settings not found. Please login first.")
            return None, False
            
        headers = {"MAPI-Key": mapi_key}
        
        # 요소 데이터 가져오기
        check_data, can_continue = FetchCivilData.safe_api_request(f"{base_url}/db/pjcf", headers)
        if can_continue:
            return True
        else:
            return False
    except:
        # st.error(f"Connection check failed: {str(e)}")
        return False

def safe_selectbox(label, options, default_index=0, key=None, **kwargs):
    """안전한 selectbox 생성 함수"""
    if key and key in st.session_state:
        if st.session_state[key] not in options:
            del st.session_state[key]
    
    return st.selectbox(
        label, 
        options, 
        index=default_index, 
        key=key, 
        **kwargs
    )
def safe_toggle(label, key=None, value=True, **kwargs):
    """안전한 toggle 위젯 생성 함수"""
    if key:
        # session state에서 안전하게 값 가져오기
        if key in st.session_state:
            current_value = st.session_state[key]
            if isinstance(current_value, bool):
                value = current_value
            elif isinstance(current_value, (int, float)):
                value = bool(current_value) and current_value != 0
            else:
                # 잘못된 타입이면 삭제하고 기본값 사용
                del st.session_state[key]
                value = value  # 매개변수로 받은 기본값 사용
    
    return st.toggle(label, key=key, value=value, **kwargs)