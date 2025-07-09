#fatigue_case_page.py
import streamlit as st
from projects.concrete_fatigue_analysis_ntc2018.session_manager import initialize_session, display_analysis_result_table,   display_import_export_buttons
import pandas as pd

# PageManager 네비게이션 import
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from projects.concrete_fatigue_analysis_ntc2018.utils.navigator import (
    back_to_bridge_type, 
    back_to_design_settings, 
    navigate_to_page_by_fatigue_case
)

# 세션 초기화
initialize_session()

# 메서드별 페이지 매핑 정의 (지연 import 사용)
def get_method_page_mapping():
    """지연 import를 사용하여 메서드별 페이지 매핑을 반환합니다."""
    from projects.concrete_fatigue_analysis_ntc2018.fatigue_concrete_simple_ui import fatigue_concrete_simple_ui_page
    from projects.concrete_fatigue_analysis_ntc2018.fatigue_concrete_desm_rail_ui import fatigue_concrete_desm_rail_ui_page
    from projects.concrete_fatigue_analysis_ntc2018.fatigue_reinforcedsteel_desm_rail_ui import fatigue_reinforcedsteel_desm_rail_ui_page
    from projects.concrete_fatigue_analysis_ntc2018.fatigue_reinforcedsteel_desm_road_ui import fatigue_reinforcedsteel_desm_road_ui_page
    from projects.concrete_fatigue_analysis_ntc2018.fatigue_concrete_shear_ui import fatigue_concrete_shear_ui_page
    from projects.concrete_fatigue_analysis_ntc2018.fatigue_steel_girder_direct_ui import fatigue_steel_girder_direct_ui_page
    from projects.concrete_fatigue_analysis_ntc2018.fatigue_steel_girder_shear_ui import fatigue_steel_girder_shear_ui_page
    from projects.concrete_fatigue_analysis_ntc2018.fatigue_concrete_shear_reqreinf_ui import fatigue_concrete_shear_reqreinf_ui_page
    
    return {
        "Concrete Comp.(simple)": fatigue_concrete_simple_ui_page,
        "Concrete Shear(Not Require Reinforcement)": fatigue_concrete_shear_ui_page,
        "Concrete Shear(Require Reinforcement)": fatigue_concrete_shear_reqreinf_ui_page,
        "Concrete Comp.(Rail_DES)": fatigue_concrete_desm_rail_ui_page,
        "Reinforcing Steel(Rail_DES)": fatigue_reinforcedsteel_desm_rail_ui_page,
        "Steel Girder(Direct Stress)": fatigue_steel_girder_direct_ui_page,
        "Reinforcing Steel(Road_DES)": fatigue_reinforcedsteel_desm_road_ui_page,
        "Steel Girder(Shear Stress)": fatigue_steel_girder_shear_ui_page
    }

# 전역 변수로 method_page_mapping 저장
method_page_mapping = None

def Setting_Fatigue_Case():
    global method_page_mapping
    
    # 지연 import로 method_page_mapping 초기화
    if method_page_mapping is None:
        method_page_mapping = get_method_page_mapping()

    if 'section_properties_df' in st.session_state:
        if st.session_state.bridge_type == '':
            pass
        else:
            try:
                material_type = st.session_state.section_properties_df['type'].values
                # print(material_type)
            except:
                st.markdown("<h5 style='margin-bottom:10px'>Add Fatigue Analysis Case</h5>", unsafe_allow_html=True)
                with st.container(height = 860, border=False):
                    st.error("❌ **MIDAS Civil Analysis File Loading Failed**: Please click 'Load' button on the first page")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("<- Required Data Loading", use_container_width=True):
                        back_to_bridge_type()
    else:
        print("section_properties_df is not in session state.")

    if ('section_properties_df' in st.session_state and 
        st.session_state.get('bridge_type', '') != '' and 
        not st.session_state.section_properties_df.empty and
        len(st.session_state.section_properties_df.get('type', [])) > 0):   
        st.session_state.edit_mode = False
        st.markdown("<h5 style='margin-bottom:10px'>Add Fatigue Analysis Case</h5>", unsafe_allow_html=True)

        # 빈 문자열인 경우 세션에서 제거 (라디오 버튼 생성 직전)
        if 'fatigue_case' in st.session_state and st.session_state.fatigue_case == '':
            del st.session_state.fatigue_case
        
        def update_fatigue_case_method():
            selected_fatigue_case_method = st.session_state.fatigue_case
            method_mapping = {
                "Concrete compression [Simplified Method]": ("ccs", "Concrete Comp.(simple)"), #fatigue_concrete_simple_ui_page,
                "Concrete Shear(Not Require Reinforcement)": ("ccs_shear", "Concrete Shear(Not Require Reinforcement)"), #fatigue_concrete_shear_ui_page,
                "Concrete Shear(Require Reinforcement)": ("ccs_shear_reqreinf", "Concrete Shear(Require Reinforcement)"), #fatigue_concrete_shear_reqreinf_ui_page,
                "Concrete compression [Damage Equivalent Stress Method (Only for Railway)]": ("cdrail", "Concrete Comp.(Rail/DES)"), #fatigue_concrete_desm_rail_ui_page,
                "Reinforcing Steel [Damage Equivalent Stress Method (Only for Railway)]": ("rdrail", "Reinforcing Steel(Rail_DES)"), #fatigue_reinforcedsteel_desm_rail_ui_page,
                "Steel Girder(Direct Stress)": ("sgd", "Steel Girder(Direct Stress)"), #fatigue_steel_girder_direct_ui_page,
                "Steel Girder(Shear Stress)": ("sgd_shear", "Steel Girder(Shear Stress)"), #fatigue_steel_girder_shear_ui_page,
                "Reinforcing Steel [Damage Equivalent Stress Method (Only for Road)]": ("rdroad", "Reinforcing Steel(Road_DES)") #fatigue_reinforcedsteel_desm_road_ui_page,
            }
            
            if selected_fatigue_case_method in method_mapping:
                st.session_state.Fatigue_method, st.session_state.selected_method = method_mapping[selected_fatigue_case_method]

        # if st.session_state.bridge_type == '':
        if st.session_state.get('bridge_type') is None :
            pass
        else:
            # print('section_properties_df' in st.session_state)
            # print(st.session_state.section_properties_df)
            if 'section_properties_df' in st.session_state and st.session_state.section_properties_df.empty:
                with st.container():
                    with st.container(height = 750, border=False):
                        pass
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("<- back", use_container_width=True):
                            # 지연 임포트 사용
                            back_to_bridge_type()

            else:
                if "steel" in material_type:
                    fatigue_cases = {

                        "Railway": [
                            "Concrete compression [Simplified Method]",
                            "Concrete Shear(Not Require Reinforcement)",
                            "Concrete Shear(Require Reinforcement)",
                            "Concrete compression [Damage Equivalent Stress Method (Only for Railway)]",
                            "Reinforcing Steel [Damage Equivalent Stress Method (Only for Railway)]",
                            "Steel Girder(Direct Stress)",
                            "Steel Girder(Shear Stress)"
                        ],
                        "Road": [
                            "Concrete compression [Simplified Method]",
                            "Concrete Shear(Not Require Reinforcement)",
                            "Concrete Shear(Require Reinforcement)",
                            "Reinforcing Steel [Damage Equivalent Stress Method (Only for Road)]",
                            "Steel Girder(Direct Stress)",
                            "Steel Girder(Shear Stress)"
                        ]
                    }
                elif "concrete" in material_type:
                    fatigue_cases = {

                        "Railway": [
                            "Concrete compression [Simplified Method]",
                            "Concrete Shear(Not Require Reinforcement)",
                            "Concrete Shear(Require Reinforcement)",
                            "Concrete compression [Damage Equivalent Stress Method (Only for Railway)]",
                            "Reinforcing Steel [Damage Equivalent Stress Method (Only for Railway)]",
                        ],
                        "Road": [
                            "Concrete compression [Simplified Method]",
                            "Concrete Shear(Not Require Reinforcement)",
                            "Concrete Shear(Require Reinforcement)",
                            "Reinforcing Steel [Damage Equivalent Stress Method (Only for Road)]",
                        ]
                    }
                else:
                    st.error("Only Composite section is supported.")
                    # st.stop()
                # 브릿지 타입이 유효하지 않으면 Railway 사용
                if st.session_state.bridge_type not in fatigue_cases:
                    st.session_state.bridge_type = "Railway"
                
                st.markdown("""
                    <style>
                        div[data-testid="stRadio"] {
                            margin-top: -30px;
                        }
                        div[data-testid="stRadio"] > label {
                            display: none;
                        }
                    </style>
                """, unsafe_allow_html=True)
                
                selected_case = st.radio(
                    "Add Fatigue Case",
                    fatigue_cases[st.session_state.bridge_type],
                    index=None,
                    key="fatigue_case",
                    on_change=update_fatigue_case_method
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("<- back", use_container_width=True):
                        # 지연 임포트 사용
                        back_to_design_settings()
                with col3:
                    if st.button("ADD", use_container_width=True, type="primary"):
                        # ADD 버튼 클릭 시 case_confirmed를 True로 설정
                        st.session_state.case_confirmed = True
                        
                        # 🔥 완전한 temp_result_df 초기화
                        if 'temp_result_df' in st.session_state:
                            del st.session_state['temp_result_df']
                        
                        # 🔥 새로운 케이스를 위한 기본 temp_result_df 생성
                        default_case_name = f"case_{len(st.session_state.get('result_df', pd.DataFrame())) + 1:03d}"
                        st.session_state['temp_result_df'] = pd.DataFrame([{
                            'case_name': default_case_name,
                            'bridge_type': st.session_state.bridge_type,
                            'factor_rcfat': st.session_state.factor_rcfat,
                            'factor_rsfat': st.session_state.factor_rsfat,
                            'factor_rspfat': st.session_state.factor_rspfat,
                            'factor_rf': st.session_state.factor_rf,
                            'factor_rsd': st.session_state.factor_rsd,
                            'factor_rm': st.session_state.factor_rm,
                            'nyear': st.session_state.nyear,
                        }])
                        
                        # 🔥 모든 피로 관련 변수 초기화 (필수 변수 제외)
                        fatigue_variables_to_clear = [
                            'correction_option', 'import_option','widget_import_option', 'vol_auto_calculate','crack_option', 'widget_crack_option',   'correction_factor_auto_calculate' ,'manual_input_correction',
                            'traffic_category','traffic_type_steel','manual_input_direct','manual_input_direct2','annual_traffic', 'manual_shear_resistance', 'manual_input_properties','get_effective_widget',
                            # 응력 관련
                            'scmax', 'scmin', 'scmax71', 'scperm', 'ds1', 'ds12', 'sctraz','is_simple_method',
                            'temp_scmax', 'temp_scmin', 'temp_scmax71', 'temp_scperm', 'temp_ds1', 'temp_ds12', 'temp_sctraz',
                            
                            'detail_category_shear','detail_category','span_error_message',


                            # 전단 무보강일때 변수
                            'fctd', 'fb', 'VRd_c', 'dp', 'is_required_reinforcement', 'bw', 'J', 'Qn',


                            #전단보강시에
                            'support_type',
                            #simple method
                            'import_option',

        
                            # Reinforcing Steel(DESM) : Railway

                            # 계산 결과
                            'fcd', 'scmax_fcd', 'scmin_fcd', 'is_ok', 'discriminant', 'discriminant_rail_des',
                            'sigma_cd_max_equ', 'sigma_cd_min_equ', 'scd_max_equ', 'scd_min_equ', 'requ',
                            
                            # 람다 계산값들
                            'calc_lambda0', 'calc_lambda1', 'calc_lambda2', 'calc_lambda3', 'calc_lambda4', 'calc_lambdac',
                            'lambda0', 'lambda1', 'lambda2', 'lambda3', 'lambda4', 'lambdac', 'calc_lambda_max',
                            
                            # 철강 관련
                            'delta_sigma_1', 'delta_sigma_12', 'delta_sigma_equ', 'delta_sigma_Rsk', 'delta_sigma_rsk',
                            'temp_delta_sigma_1', 'temp_delta_sigma_12',
                            
                            # 전단 관련
                            'Vs1', 'Vs12', 'temp_Vs1', 'temp_Vs12', 'Vsd', 'Vsdmax', 'Vsdmin', 'temp_Vsd', 'temp_Vsdmax', 'temp_Vsdmin',
                            'tau1', 'tau12', 'delta_tau_equ', 'delta_tau_rsk', 'delta_tau_amm',
                            
                            # 모멘트 관련
                            'Msd', 'temp_Msd',
                            
                            # 요소 번호들
                            'element_number_scmax', 'element_number_scmin', 'element_number_scmax71', 'element_number_scperm',
                            'element_number_ds1', 'element_number_ds12', 'element_number_sctraz', 'element_number_delta_sigma_1',
                            'element_number_Vs1', 'element_number_Vs12', 'element_number_Vsd', 'element_number_Vsdmax', 'element_number_Vsdmin',
                            'element_number_Msd', 'final_element',
                            
                            # 임시 요소 번호들
                            'temp_element_number_scmax', 'temp_element_number_scmin', 'temp_element_number_scmax71', 'temp_element_number_scperm',
                            'temp_element_number_ds1', 'temp_element_number_ds12', 'temp_element_number_sctraz', 'temp_element_number_delta_sigma_1',
                            'temp_element_number_Vs1', 'temp_element_number_Vs12', 'temp_element_number_Vsd', 'temp_element_number_Vsdmax', 
                            'temp_element_number_Vsdmin', 'temp_element_number_Msd',
                            
                            # 선택된 요소들
                            'temp_Select_Elements', 'temp_Select_Elements2', 'temp_Select_Elements3', 'temp_Select_Elements4',
                            'temp_Select_Elements_simple', 'temp_Select_Elements_simple2', 'temp_Select_Elements_steel', 'temp_Select_Elements_steel2',
                            'temp_Select_Elements_shear', 'temp_Select_Elements_shear2', 'temp_Select_Elements_sctraz', 'temp_Select_Elements_moment',
                            
                            # 기타 계산 변수들
                            'n_steel', 'A_steel', 'vol', 'nc', 'nt',
                            'steel_type', 'section_type', 'support_type', 'traffic_type', 'sp', 'az', 'tt',
                            'p_staffe', 'd_mandrel', 'reduction_factor', 'detail_category',
                            
                            # 섹션 특성 (get_ 접두사)
                            'get_total_area', 'get_total_first_moment', 'get_iyy_total', 'get_total_centroid_height',
                            'get_girder_centroid_height', 'get_girder_height', 'get_total_height', 'get_slab_height',
                            'get_bw', 'get_Qn', 'get_J', 'get_d',
                            
                            # 편집 모드 관련
                            'edit_mode', 'fatigue_case_name',
                            
                            # 에러 상태들
                            'error_condition', 'next_error',
                            'nobs','qmk','location','traffic_category','traffic_type_steel','manual_input_direct','manual_input_direct2','annual_traffic',
                            'delta_sigma1','delta_sigma12','temp_delta_sigma_1','temp_delta_sigma_12','delta_sigma_1','delta_sigma_12'
                        ]
                        
                        # 🔥 변수들 삭제
                        for var in fatigue_variables_to_clear:
                            if var in st.session_state:
                                del st.session_state[var]
                        
                        # 🔥 케이스 이름 초기화
                        st.session_state.case_name = default_case_name
                        
                        # 🔥 편집 모드 해제
                        st.session_state.edit_mode = False
                        if 'fatigue_case_name' in st.session_state:
                            del st.session_state['fatigue_case_name']

                        if selected_case:  # 선택된 경우만 처리
                            navigate_to_page_by_fatigue_case(selected_case)
                        else:
                            st.warning("Select analysis type.")
                st.markdown("---")             
                # 결과 테이블 표시 (항상 표시)
                # with st.container(height=20, border=False):    
                #     st.markdown("", unsafe_allow_html=True)


                st.markdown("<h5><b>Fatigue Result Status</b></h5>", unsafe_allow_html=True)

                display_import_export_buttons()
            
                display_analysis_result_table(method_page_mapping)  # 항상 호출되도록 함수 내에 위치

        st.session_state.case_name = st.session_state.get('case_name', 'case_001')  # 기본값 설정
        span_length= st.session_state.span_length = st.session_state.get('span_length', 35)
        d= st.session_state.d = st.session_state.get('d', 2762)
    
    # # 디버깅용 데이터 표시
    # if st.checkbox("Show Debug Data", value=False):
    #     st.write("Temp DF", st.session_state.get('temp_result_df'))
    #     st.write("Result DF", st.session_state.get('result_df'))
    #     st.write("Session State:", {k: v for k, v in st.session_state.items() 
    #                              if k not in ['result_df', 'temp_result_df'] and not k.startswith('_')})

# # 디버깅 정보 표시 (옵션)
# st.sidebar.subheader("Debug Session State")
# st.sidebar.write("Case Name:", st.session_state.get('case_name', 'None'))  
# # temp_result_df 직접 확인
# st.sidebar.subheader("Temporary DataFrame:")
# if 'temp_result_df' in st.session_state:
#     temp_df = st.session_state.temp_result_df
#     if isinstance(temp_df, pd.DataFrame):
#         if temp_df.empty:
#             st.sidebar.info("temp_result_df is empty.")
#         else:
#             st.sidebar.dataframe(temp_df)
#     else:
#         st.sidebar.error(f"temp_result_df's type is not DataFrame: {type(temp_df)}")
# else:
#     st.sidebar.warning("temp_result_df is not in session state.")




# # # 디버깅용 데이터 표시

# st.write("Temp DF", st.session_state.get('temp_result_df'))
# st.write("Result DF", st.session_state.get('result_df'))
# st.write("Session State:", {k: v for k, v in st.session_state.items() 
#                             if k not in ['result_df', 'temp_result_df'] and not k.startswith('_')})





