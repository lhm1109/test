import streamlit as st
st.set_page_config(layout="wide")
from streamlit.components.v1 import html
import pandas as pd
from projects.concrete_fatigue_analysis_ntc2018.session_manager import initialize_session
from streamlit_extras.switch_page_button import switch_page
from projects.concrete_fatigue_analysis_ntc2018.fatigue_concrete_simple_ui import fatigue_concrete_simple_ui_page
from projects.concrete_fatigue_analysis_ntc2018.fatigue_concrete_desm_rail_ui import fatigue_concrete_desm_rail_ui_page
from projects.concrete_fatigue_analysis_ntc2018.fatigue_reinforcedsteel_desm_road_ui import fatigue_reinforcedsteel_desm_road_ui_page
from projects.concrete_fatigue_analysis_ntc2018.fatigue_concrete_shear_ui import fatigue_concrete_shear_ui_page
from projects.concrete_fatigue_analysis_ntc2018.fatigue_concrete_shear_reqreinf_ui import fatigue_concrete_shear_reqreinf_ui_page
from projects.concrete_fatigue_analysis_ntc2018.fatigue_steel_girder_direct_ui import fatigue_steel_girder_direct_ui_page
from projects.concrete_fatigue_analysis_ntc2018.fatigue_steel_girder_shear_ui import fatigue_steel_girder_shear_ui_page
from projects.concrete_fatigue_analysis_ntc2018.fatigue_reinforcedsteel_desm_rail_ui import fatigue_reinforcedsteel_desm_rail_ui_page
from projects.concrete_fatigue_analysis_ntc2018.calc.section_calculate import *
from PIL import Image
from projects.concrete_fatigue_analysis_ntc2018.first_setting import Setting_Bridge, Setting_Parameter
import requests
from projects.concrete_fatigue_analysis_ntc2018.fetching_page import fetching_page  # 새로 추가

# PageManager import 추가
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.page_manager import page_manager
from utils.page_navigator import render_current_page
from projects.concrete_fatigue_analysis_ntc2018.utils.navigator import navigate_to_bridge_type
from dotenv import load_dotenv
import base64
from utils.ParamHandler import ParamHandler
initialize_session()
st.session_state.bridge_type = "Road"
# Hide header and remove top padding
st.markdown("""
    <style>
        header[data-testid="stHeader"] {
            display: none !important;
        }
        .main > div {
            padding-top: 0rem;
        }
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
        }
        [data-testid="stToolbar"] {
            display: none !important;
        }
        [data-testid="stDecoration"] {
            display: none !important;
        }
        #MainMenu {
            display: none !important;
        }
        [data-testid="stStatusWidget"] {
            display: none !important;
        }
        footer {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- URL 파라미터 읽기 ---
_base_url = ParamHandler.base_url
_mapi_key = ParamHandler.mapi_key
base_url = f"{_base_url}/civil"
#  초기화
if 'section_properties_df' not in st.session_state:
    st.session_state['section_properties_df'] = pd.DataFrame()

if 'case_confirmed' not in st.session_state:
    st.session_state.case_confirmed = False

if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

def get_analysis_settings_pages():
    """Analysis Settings 페이지 목록을 동적으로 생성"""
    base_pages = [
        ("bridge_type", Setting_Bridge, "Bridge Type", "/bridge_type"),
        ("loading_data", fetching_page, "Loading Data", "/loading_data"),
    ]

    # 나머지 페이지들
    base_pages.extend([
        ("design_settings", Setting_Parameter, "Design Settings", "/design_settings"),
        ("fatigue_case", get_setting_fatigue_case(), "Fatigue Case", "/fatigue_case"),
    ])
    
    return base_pages

def get_setting_fatigue_case():
    """지연 import를 사용하여 Setting_Fatigue_Case를 반환합니다."""
    from projects.concrete_fatigue_analysis_ntc2018.fatigue_case_page import Setting_Fatigue_Case
    return Setting_Fatigue_Case

def get_method_page_mapping():
    """지연 import를 사용하여 method_page_mapping을 반환합니다."""
    from projects.concrete_fatigue_analysis_ntc2018.fatigue_case_page import method_page_mapping
    return method_page_mapping

def register_analysis_settings_pages():
    """Analysis Settings 페이지들을 PageManager에 등록"""
    # 새로운 페이지들 등록
    pages = get_analysis_settings_pages()
    for key, page_func, title, url_path in pages:
        full_key = f"analysis_settings_{key}"
        
        # 이미 등록된 페이지인지 확인
        if not page_manager.page_exists(full_key):
            page_manager.register_page(
                key=full_key,
                title=title,
                url_path=url_path,
                page_source=page_func,
                category="Road Bridge Concrete Fatigue Analysis(NTSC 2018)",
                is_default=(key == "bridge_type"),  # Bridge Type을 기본 페이지로 설정
                hidden=True,
            )

def register_analysis_case_pages():
    """Analysis Case 페이지들을 PageManager에 등록"""
    # 선택된 방법에 맞는 페이지 찾기
    selected_method = st.session_state.get('selected_method', '')
    fatigue_case = st.session_state.get('fatigue_case', '')
    
    # 방법에 따른 페이지 매핑
    method_to_page_mapping = {
        "Concrete Comp.(simple)": (fatigue_concrete_simple_ui_page, "Concrete compression [Simplified Method]"),
        "Concrete Shear(Not Require Reinforcement)": (fatigue_concrete_shear_ui_page, "Concrete Shear [Not Require Reinforcement]"),
        "Concrete Shear(Require Reinforcement)": (fatigue_concrete_shear_reqreinf_ui_page, "Concrete Shear [Require Reinforcement]"),
        "Concrete Comp.(Rail_DES)": (fatigue_concrete_desm_rail_ui_page, "Concrete compression [Damage Equivalent Stress Method (Railway)]"),
        "Reinforcing Steel(Rail_DES)": (fatigue_reinforcedsteel_desm_rail_ui_page, "Reinforcing Steel [Damage Equivalent Stress Method (Railway)]"),
        "Steel Girder(Direct Stress)": (fatigue_steel_girder_direct_ui_page, "Steel Girder(Direct Stress)"),
        "Reinforcing Steel(Road_DES)": (fatigue_reinforcedsteel_desm_road_ui_page, "Reinforcing Steel [Damage Equivalent Stress Method (Road)]"),
        "Steel Girder(Shear Stress)": (fatigue_steel_girder_shear_ui_page, "Steel Girder(Shear Stress)")
    }
    
    pages_to_register = []
    
    # 케이스가 있는 경우
    if fatigue_case or selected_method:
        # 선택된 케이스에 맞는 페이지 추가
        if fatigue_case == "Concrete compression [Simplified Method]":
            pages_to_register.append(("concrete_simple", fatigue_concrete_simple_ui_page, "Concrete compression [Simplified Method]", "/concrete_simple"))
        elif fatigue_case == "Concrete Shear(Not Require Reinforcement)":
            pages_to_register.append(("concrete_shear", fatigue_concrete_shear_ui_page, "Concrete Shear [Not Require Reinforcement]", "/concrete_shear"))
        elif fatigue_case == "Concrete Shear(Require Reinforcement)":
            pages_to_register.append(("concrete_shear_reqreinf", fatigue_concrete_shear_reqreinf_ui_page, "Concrete Shear [Require Reinforcement]", "/concrete_shear_reqreinf"))
        elif fatigue_case == "Concrete compression [Damage Equivalent Stress Method (Only for Railway)]":
            pages_to_register.append(("concrete_desm_rail", fatigue_concrete_desm_rail_ui_page, "Concrete compression [Damage Equivalent Stress Method (Railway)]", "/concrete_desm_rail"))
        elif fatigue_case == "Reinforcing Steel [Damage Equivalent Stress Method (Only for Railway)]":
            pages_to_register.append(("reinforcedsteel_desm_rail", fatigue_reinforcedsteel_desm_rail_ui_page, "Reinforcing Steel [Damage Equivalent Stress Method (Railway)]", "/reinforcedsteel_desm_rail"))
        elif fatigue_case == "Steel Girder(Direct Stress)":
            pages_to_register.append(("steel_girder_direct", fatigue_steel_girder_direct_ui_page, "Steel Girder(Direct Stress)", "/steel_girder_direct"))
        elif fatigue_case == "Reinforcing Steel [Damage Equivalent Stress Method (Only for Road)]":
            pages_to_register.append(("reinforcedsteel_desm_road", fatigue_reinforcedsteel_desm_road_ui_page, "Reinforcing Steel [Damage Equivalent Stress Method (Road)]", "/reinforcedsteel_desm_road"))
        elif fatigue_case == "Steel Girder(Shear Stress)":
            pages_to_register.append(("steel_girder_shear", fatigue_steel_girder_shear_ui_page, "Steel Girder(Shear Stress)", "/steel_girder_shear"))
        # 선택된 방법으로 페이지 찾기
        elif selected_method in method_to_page_mapping:
            page_func, page_title = method_to_page_mapping[selected_method]
            key = selected_method.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(".", "")
            pages_to_register.append((key, page_func, page_title, f"/{key}"))
    
    # 페이지가 하나도 없으면 디폴트로 모든 Analysis Case 페이지 추가
    if len(pages_to_register) == 0:
        pages_to_register = [
            ("concrete_simple", fatigue_concrete_simple_ui_page, "Concrete compression [Simplified Method]", "/concrete_simple"),
            ("concrete_shear", fatigue_concrete_shear_ui_page, "Concrete Shear(Not Require Reinforcement)", "/concrete_shear"),
            ("concrete_shear_reqreinf", fatigue_concrete_shear_reqreinf_ui_page, "Concrete Shear(Require Reinforcement)", "/concrete_shear_reqreinf"),
            ("steel_girder_direct", fatigue_steel_girder_direct_ui_page, "Steel Girder(Direct Stress)", "/steel_girder_direct"),
            ("reinforcedsteel_desm_rail", fatigue_reinforcedsteel_desm_rail_ui_page, "Reinforcing Steel [Damage Equivalent Stress Method (Railway)]", "/reinforcedsteel_desm_rail"),
            ("concrete_desm_rail", fatigue_concrete_desm_rail_ui_page, "Concrete compression [Damage Equivalent Stress Method (Railway)]", "/concrete_desm_rail"),
            ("reinforcedsteel_desm_road", fatigue_reinforcedsteel_desm_road_ui_page, "Reinforcing Steel [Damage Equivalent Stress Method (Road)]", "/reinforcedsteel_desm_road"),
            ("steel_girder_shear", fatigue_steel_girder_shear_ui_page, "Steel Girder(Shear Stress)", "/steel_girder_shear")
        ]
    
    # 페이지들 등록 (이미 등록된 페이지는 건너뛰기)
    for key, page_func, title, url_path in pages_to_register:
        full_key = f"analysis_case_{key}"
        
        # 이미 등록된 페이지인지 확인
        if not page_manager.page_exists(full_key):
            page_manager.register_page(
                key=full_key,
                title=title,
                url_path=url_path,
                page_source=page_func,
                category="Concrete Fatigue Analysis(NTSC 2018)",
                is_default=False,
                hidden=True,
            )

def setup_navigation():
    """PageManager를 사용하여 네비게이션 설정"""
    # Analysis Settings 페이지들 등록
    register_analysis_settings_pages()
    
    # case_confirmed가 True인 경우 Analysis Case 페이지들도 등록
    if st.session_state.case_confirmed:
        register_analysis_case_pages()
        
    # 네비게이션 생성
    pg = page_manager.create_navigation()

def fetch(url, mapi_key):
    headers = {"MAPI-Key": mapi_key}
    # 3. UNIT
    res_unit = requests.get(f"{url}/db/unit", headers=headers)
    if res_unit.status_code != 200:
        raise Exception(f"UNIT fetch failed: {res_unit.status_code}")

    # 전처리 & 반환
    unit_data = res_unit.json().get("UNIT", {}).get("1", {})
    return unit_data

st.sidebar.title("Temp API Settings")
url = base_url
mapi_key = _mapi_key

# url = st.sidebar.text_input("Base URL", value="https://moa-engineers.midasit.com:443/civil", key="midas_base_url")
# mapi_key = st.sidebar.text_input("MAPI-KEY", value="eyJ1ciI6ImxlZW5pbmQiLCJwZyI6ImNpdmlsIiwiY24iOiJsQlRNNGhlTVF3In0.41e27aec840cfb77d2ac42a56e087a6f5f0ceb25ab646b282368c429646dec4c", type="password", key="midas_mapi_key")


# 자동 로그인 로직
if __name__ == "__main__":
    if _base_url and _mapi_key and not st.session_state.get('api_connected', False):
        try:
            with st.spinner("API 자동 연결 중..."):
                # API 연결 테스트 및 데이터 가져오기
                unit_data = fetch(url, mapi_key)
                
                # 성공 시 현재 사용 중인 API 설정 저장
                st.session_state.current_base_url = url
                st.session_state.current_mapi_key = mapi_key
                
                # 기본 데이터 저장
                st.session_state.api_connected = True
                st.session_state.unit_data = unit_data

                st.sidebar.success("🚀 API auto-connected successfully!")
                
                # 네비게이션 설정 (API 연결 후에 실행)
                setup_navigation()
                
                # API 연결 성공 시 bridge_type 페이지로 이동
                st.success("초기화가 완료되었습니다! Bridge Type 페이지로 이동합니다.")
                
                # Bridge Type 페이지로 이동
                navigate_to_bridge_type()
                
                # 현재 페이지 렌더링
                render_current_page()
                
        except Exception as e:
            st.sidebar.error(f"❌ Auto-login failed: {e}")
            st.sidebar.info("수동으로 Login 버튼을 클릭해주세요.")

# 메인 페이지 내용
# st.title("Road Bridge Concrete Fatigue Analysis (NTSC 2018)")

# 네비게이션 설정
setup_navigation()

# 현재 페이지 렌더링
render_current_page()
