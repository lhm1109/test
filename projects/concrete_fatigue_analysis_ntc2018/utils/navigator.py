import streamlit as st
import sys
import os
from time import sleep
# PageManager import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from utils.page_manager import page_manager
from utils.page_navigator import navigate_to_page

def navigate_to_analysis_settings_page(page_name):
    """
    Analysis Settings 페이지로 이동합니다.
    
    Args:
        page_name (str): 페이지 이름 (bridge_type, design_settings, fatigue_case, loading_data)
    """
    page_key = f"analysis_settings_{page_name}"
    navigate_to_page(page_key)

def navigate_to_analysis_case_page(page_name):
    """
    Analysis Case 페이지로 이동합니다.
    
    Args:
        page_name (str): 페이지 이름 (concrete_simple, concrete_shear, etc.)
    """
    page_key = f"analysis_case_{page_name}"
    st.sidebar.write(f"Debug - navigate_to_analysis_case_page: {page_name} -> {page_key}")
    
    try:
        navigate_to_page(page_key)
    except Exception as e:
        st.error(f"Analysis Case 페이지 이동 중 오류: {str(e)}")
        st.sidebar.write(f"Debug - Analysis Case navigation error: {e}")

def navigate_to_bridge_type():
    """Bridge Type 페이지로 이동"""
    navigate_to_analysis_settings_page("bridge_type")

def navigate_to_design_settings():
    """Design Settings 페이지로 이동"""
    navigate_to_analysis_settings_page("design_settings")

def navigate_to_fatigue_case():
    """Fatigue Case 페이지로 이동"""
    navigate_to_analysis_settings_page("fatigue_case")

def navigate_to_loading_data():
    """Loading Data 페이지로 이동"""
    navigate_to_analysis_settings_page("loading_data")

def navigate_to_concrete_simple():
    """Concrete compression [Simplified Method] 페이지로 이동"""
    navigate_to_analysis_case_page("concrete_simple")

def navigate_to_concrete_shear():
    """Concrete Shear [Not Require Reinforcement] 페이지로 이동"""
    navigate_to_analysis_case_page("concrete_shear")

def navigate_to_concrete_shear_reqreinf():
    """Concrete Shear [Require Reinforcement] 페이지로 이동"""
    navigate_to_analysis_case_page("concrete_shear_reqreinf")

def navigate_to_concrete_desm_rail():
    """Concrete compression [Damage Equivalent Stress Method (Railway)] 페이지로 이동"""
    navigate_to_analysis_case_page("concrete_desm_rail")

def navigate_to_reinforcedsteel_desm_rail():
    """Reinforcing Steel [Damage Equivalent Stress Method (Railway)] 페이지로 이동"""
    navigate_to_analysis_case_page("reinforcedsteel_desm_rail")

def navigate_to_steel_girder_direct():
    """Steel Girder(Direct Stress) 페이지로 이동"""
    navigate_to_analysis_case_page("steel_girder_direct")

def navigate_to_reinforcedsteel_desm_road():
    """Reinforcing Steel [Damage Equivalent Stress Method (Road)] 페이지로 이동"""
    navigate_to_analysis_case_page("reinforcedsteel_desm_road")

def navigate_to_steel_girder_shear():
    """Steel Girder(Shear Stress) 페이지로 이동"""
    navigate_to_analysis_case_page("steel_girder_shear")

def navigate_to_page_by_method(selected_method):
    """
    선택된 방법에 따라 해당 페이지로 이동합니다.
    
    Args:
        selected_method (str): 선택된 방법
    """
    method_to_page_mapping = {
        "Concrete Comp.(simple)": "concrete_simple",
        "Concrete Shear(Not Require Reinforcement)": "concrete_shear",
        "Concrete Shear(Require Reinforcement)": "concrete_shear_reqreinf",
        "Concrete Comp.(Rail_DES)": "concrete_desm_rail",
        "Reinforcing Steel(Rail_DES)": "reinforcedsteel_desm_rail",
        "Steel Girder(Direct Stress)": "steel_girder_direct",
        "Reinforcing Steel(Road_DES)": "reinforcedsteel_desm_road",
        "Steel Girder(Shear Stress)": "steel_girder_shear"
    }
    
    if selected_method in method_to_page_mapping:
        page_name = method_to_page_mapping[selected_method]
        navigate_to_analysis_case_page(page_name)
    else:
        st.error(f"알 수 없는 방법입니다: {selected_method}")

def navigate_to_page_by_fatigue_case(fatigue_case):
    """
    피로 케이스에 따라 해당 페이지로 이동합니다.
    
    Args:
        fatigue_case (str): 피로 케이스
    """
    # 디버깅 정보 추가
    st.sidebar.write(f"Debug - navigate_to_page_by_fatigue_case called with: {fatigue_case}")
    
    case_to_page_mapping = {
        "Concrete compression [Simplified Method]": "concrete_simple",
        "Concrete Shear(Not Require Reinforcement)": "concrete_shear",
        "Concrete Shear(Require Reinforcement)": "concrete_shear_reqreinf",
        "Concrete compression [Damage Equivalent Stress Method (Only for Railway)]": "concrete_desm_rail",
        "Reinforcing Steel [Damage Equivalent Stress Method (Only for Railway)]": "reinforcedsteel_desm_rail",
        "Steel Girder(Direct Stress)": "steel_girder_direct",
        "Reinforcing Steel [Damage Equivalent Stress Method (Only for Road)]": "reinforcedsteel_desm_road",
        "Steel Girder(Shear Stress)": "steel_girder_shear"
    }
    
    st.sidebar.write(f"Debug - Available cases: {list(case_to_page_mapping.keys())}")
    st.sidebar.write(f"Debug - Case in mapping: {fatigue_case in case_to_page_mapping}")
    
    if fatigue_case in case_to_page_mapping:
        page_name = case_to_page_mapping[fatigue_case]
        st.sidebar.write(f"Debug - Mapped to page: {page_name}")
        navigate_to_analysis_case_page(page_name)
    else:
        st.error(f"알 수 없는 피로 케이스입니다: {fatigue_case}")
        st.sidebar.write(f"Debug - Unknown case: {fatigue_case}")

# 편의 함수들
def back_to_bridge_type():
    """Bridge Type 페이지로 돌아가기"""
    navigate_to_bridge_type()

def back_to_design_settings():
    """Design Settings 페이지로 돌아가기"""
    navigate_to_design_settings()

def back_to_fatigue_case():
    """Fatigue Case 페이지로 돌아가기"""
    navigate_to_fatigue_case() 