# fatigue_steel_girder_direct_ui.py
import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from projects.concrete_fatigue_analysis_ntc2018.session_manager import *
from streamlit_extras.switch_page_button import switch_page
from projects.concrete_fatigue_analysis_ntc2018.calc.fatigue_steel_grider_design import *

from projects.concrete_fatigue_analysis_ntc2018.utils.navigator import back_to_fatigue_case

# Initialize session
initialize_session()

# Set fatigue method
st.session_state.Fatigue_method = "Steel Girder(Shear Stress)"




# Get import dialogs
import_dialogs = SessionManager.initialize_import_dialogs() if 'SessionManager' in globals() else None
civil_stress_import = import_dialogs['steel_shear_force'] if import_dialogs else None

# Get import dialogs
import_dialogs2 = SessionManager.initialize_import_dialogs() if 'SessionManager' in globals() else None
civil_stress_import2 = import_dialogs2['steel_stress'] if import_dialogs2 else None


 




def display_sn_curves_streamlit():
    """S-N 커브를 Streamlit 네이티브 차트로 표시 (로그 스케일 적용)"""
    # 체크박스에 고유 키 추가
    # col1, col2 = st.columns(2)
    # with col1:
    #     show_direct = st.checkbox(
    #         "Show Direct Stress S-N Curve", 
    #         value=True, 
    #         disabled="Direct Stress" not in st.session_state.get('verification_options', []),
    #         key="sn_direct_checkbox"
    #     )
    # with col2:
    #     show_shear = st.checkbox(
    #         "Show Shear Stress S-N Curve", 
    #         value=True,
    #         disabled="Shear Stress" not in st.session_state.get('verification_options', []),
    #         key="sn_shear_checkbox"
    #     )
    #여기서 선택
    show_direct = st.session_state.get('show_direct_stress_sn_curve', True)
    show_shear = st.session_state.get('show_shear_stress_sn_curve', False)
    # S-N 커브 데이터 준비
    if (show_direct and "Direct Stress" in st.session_state.get('verification_options', [])) or \
       (show_shear and "Shear Stress" in st.session_state.get('verification_options', [])):
        
        import pandas as pd
        import numpy as np
        
        # 로그 스케일용 x 값 생성 (4=10^4, 8=10^8)
        log_N = np.linspace(4, 8, 100)
        N_values = 10**log_N
        
        # 데이터프레임 생성 (로그 스케일)
        log_data = pd.DataFrame({
            'log N': log_N
        })
        
        # Direct Stress 커브 데이터
        if show_direct and "Direct Stress" in st.session_state.get('verification_options', []):
            # 설계 피로 강도 가져오기
            delta_sigma_rsk = st.session_state.get('calc_delta_sigma_rsk', 0)
            
            # S-N 커브 값 계산
            direct_stress = np.zeros_like(N_values)
            for i, N in enumerate(N_values):
                if N <= 5e6:
                    # N ≤ 5×10^6인 경우 m=3 적용
                    direct_stress[i] = delta_sigma_rsk * (2e6 / N)**(1/3)
                else:
                    # 5×10^6 < N ≤ 10^8인 경우 m=5 적용
                    delta_sigma_d = delta_sigma_rsk * (2/5)**(1/3)  # 일정 진폭 피로 한계
                    direct_stress[i] = delta_sigma_d * (5e6 / N)**(1/5)
            
            # 로그 스케일 데이터 추가
            log_data['log Direct Stress'] = np.log10(direct_stress)
        
        # Shear Stress 커브 데이터
        if show_shear and "Shear Stress" in st.session_state.get('verification_options', []):
            # 설계 피로 강도 가져오기
            delta_tau_rsk = st.session_state.get('calc_delta_tau_rsk', 0)
            
            # S-N 커브 값 계산
            shear_stress = np.zeros_like(N_values)
            for i, N in enumerate(N_values):
                if N <= 5e6:
                    # N ≤ 5×10^6인 경우 m=5 적용 (전단 응력은 m=5)
                    shear_stress[i] = delta_tau_rsk * (2e6 / N)**(1/5)
                else:
                    # 5×10^6 < N ≤ 10^8인 경우 일정 진폭 피로 한계 (cut-off limit)
                    delta_tau_l = delta_tau_rsk * (2/5)**(1/5)  # 전단 응력의 cut-off limit
                    shear_stress[i] = delta_tau_l
            
            # 로그 스케일 데이터 추가
            log_data['log Shear Stress'] = np.log10(shear_stress)
        
        # 차트 생성
        st.markdown("<h5><b>Steel</b></h5>", unsafe_allow_html=True)
        # 로그 스케일 차트 표시
        st.line_chart(
            data=log_data.set_index('log N'),
            use_container_width=True,
            height=400
        )
        
        # 스케일 정보 표시
        st.caption("X-axis: Log10(N), Y-axis: Log10(Stress Range [MPa])")
               
        # 주요 포인트 표시 (텍스트로)
        st.subheader("Reference Points")
        
        ref_col1, ref_col2 = st.columns(2)
        
        # Direct Stress 레퍼런스 포인트
        if show_direct and "Direct Stress" in st.session_state.get('verification_options', []):
            with ref_col1:
                st.markdown("<b>Direct Stress:</b>", unsafe_allow_html=True)
                delta_sigma_rsk = st.session_state.get('calc_delta_sigma_rsk', 0)
                delta_sigma_equ = st.session_state.get('calc_delta_sigma_equ', 0)
                direct_stress_ratio = delta_sigma_equ / delta_sigma_rsk
                if delta_sigma_rsk > 0:
                    st.write(f"ΔσRsk (2M cycles): {delta_sigma_rsk:.1f} MPa")
                if delta_sigma_equ > 0:
                    st.write(f"Δσequ: {delta_sigma_equ:.1f} MPa")
                    st.write(f"Stress Ratio: {direct_stress_ratio:.2f}")
        
        # Shear Stress 레퍼런스 포인트
        if show_shear and "Shear Stress" in st.session_state.get('verification_options', []):
            with ref_col2:
                st.markdown("<b>Shear Stress:</b>", unsafe_allow_html=True)
                delta_tau_rsk = st.session_state.get('calc_delta_tau_rsk', 0)
                delta_tau_equ = st.session_state.get('calc_delta_tau_equ', 0)
                shear_ratio = st.session_state.get('calc_shear_stress_ratio', 0)
                
                if delta_tau_rsk > 0:
                    st.write(f"ΔτRsk (2M cycles): {delta_tau_rsk:.1f} MPa")
                if delta_tau_equ > 0:
                    st.write(f"Δτequ: {delta_tau_equ:.1f} MPa")
                    st.write(f"Stress Ratio: {shear_ratio:.2f}")
        
        # 설명 추가
        st.info("""
        **S-N 커브 설명:**
        - **Direct Stress**: m=3 (N ≤ 5×10^6), m=5 (5×10^6 < N ≤ 10^8)
        - **Shear Stress**: m=5 (N ≤ 5×10^6), constant after 5×10^6 cycles
        - ΔσRsk, ΔτRsk: 2백만 사이클에서의 설계 피로 강도
        - Δσequ, Δτequ: 등가 응력 범위
        """)


# S-N 커브 계산 함수
def calculate_direct_stress_sn_curve():
    """S-N 커브 계산 - Direct Stress"""
    # S-N 커브 파라미터
    delta_sigma_c = st.session_state.get('delta_sigma_amm', 180.0)  # 2백만 사이클에서의 피로 강도
    gamma_m = st.session_state.get('factor_rm', 1.35)  # 안전 계수
    delta_sigma_rsk = delta_sigma_c / gamma_m  # 설계 피로 강도
    
    # S-N 커브 점 계산
    cycles = [1e4, 5e4, 1e5, 5e5, 1e6, 2e6, 5e6, 1e7, 5e7, 1e8]
    stress_ranges = []
    
    for N in cycles:
        if N <= 5e6:
            # N ≤ 5×10^6인 경우 m=3 적용
            delta_sigma = delta_sigma_rsk * (2e6 / N)**(1/3)
        else:
            # 5×10^6 < N ≤ 10^8인 경우 m=5 적용
            delta_sigma_d = delta_sigma_rsk * (2/5)**(1/3)  # 일정 진폭 피로 한계
            delta_sigma = delta_sigma_d * (5e6 / N)**(1/5)
        
        stress_ranges.append(delta_sigma)
    
    return cycles, stress_ranges

def calculate_shear_stress_sn_curve():
    """S-N 커브 계산 - Shear Stress"""
    # S-N 커브 파라미터
    delta_tau_c = st.session_state.get('delta_tau_amm', 80.0)  # 2백만 사이클에서의 피로 강도
    gamma_m = st.session_state.get('factor_rf', 1.35)  # 안전 계수
    delta_tau_rsk = delta_tau_c / gamma_m  # 설계 피로 강도
    
    # S-N 커브 점 계산
    cycles = [1e4, 5e4, 1e5, 5e5, 1e6, 2e6, 5e6, 1e7, 5e7, 1e8]
    stress_ranges = []
    
    for N in cycles:
        if N <= 5e6:
            # N ≤ 5×10^6인 경우 m=5 적용 (전단 응력은 m=5)
            delta_tau = delta_tau_rsk * (2e6 / N)**(1/5)
        else:
            # 5×10^6 < N ≤ 10^8인 경우 일정 진폭 피로 한계 (cut-off limit)
            delta_tau_l = delta_tau_rsk * (2/5)**(1/5)  # 전단 응력의 cut-off limit
            delta_tau = delta_tau_l
        
        stress_ranges.append(delta_tau)
    
    return cycles, stress_ranges

#피로검토계산 피로계산 결과계산 전단계산
def fatigue_steel_girder_shear_calculate():
    """Calculate fatigue verification for steel girder"""
    # Get input values
    gamma_m = st.session_state.get('factor_rm', 1.35)
    delta_tau_amm = st.session_state.get("delta_tau_amm", 80)
    Vs1 = abs(st.session_state.get("Vs1", 0))
    Vs12 = abs(st.session_state.get("Vs12", 0))

    # get_bw = 18
    # get_J=41050000000
    # get_H=2300
    get_bw = st.session_state.get('get_bw', 0)
    get_J = st.session_state.get('get_J', 0)
    get_H = st.session_state.get('get_total_height', 0)
    get_Qn = st.session_state.get('get_Qn_steel', 0)


    if get_H > 0 and get_bw > 0 and get_J > 0:
        delta_tau = (Vs1 * 1000 * get_Qn) / (get_bw * get_J)
    else:
        get_Qn = 0 
        delta_tau = 0
    # Calculate design values
    delta_tau_rsk = delta_tau_amm / gamma_m

    # Calculate equivalent stress
    lambda_s = st.session_state.get('calc_lambda_s', 0.0)
    delta_tau_equ = delta_tau * lambda_s
    
    # Calculate verification ratio
    shear_stress_ratio = delta_tau_equ / delta_tau_rsk if delta_tau_rsk != 0 else float('inf')
    
    # Save results to session state
    st.session_state.delta_tau = delta_tau
    st.session_state.calc_delta_tau_rsk = delta_tau_rsk
    st.session_state.calc_delta_tau_equ = delta_tau_equ
    st.session_state.calc_shear_stress_ratio = shear_stress_ratio
    st.session_state.calc_is_ok = shear_stress_ratio <= 1.0
    st.session_state.is_ok = "OK" if shear_stress_ratio <= 1.0 else "NG"
    
    # Update temp_result_df
    if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
        st.session_state.temp_result_df.at[0, 'delta_tau'] = delta_tau
        st.session_state.temp_result_df.at[0, 'delta_tau_rsk'] = delta_tau_rsk
        st.session_state.temp_result_df.at[0, 'delta_tau_equ'] = delta_tau_equ
        st.session_state.temp_result_df.at[0, 'shear_stress_ratio'] = shear_stress_ratio
        st.session_state.temp_result_df.at[0, 'is_ok'] = st.session_state.is_ok
    
    # Update multiple fields to temp_result_df
    update_temp_from_input_multi(['case_name', 'delta_tau_amm', 'span_length', 'shear_stress_ratio',
                                 'Vs1', 'Vs12', 'Fatigue_method', 'is_ok','delta_tau', 'delta_tau_rsk', 'delta_tau_equ',])
    
def fatigue_steel_girder_shear_ui_page():
    st.session_state.Fatigue_method = "Steel Girder(Shear Stress)"
    def save_fatigue_case():
        """Save fatigue case function"""
        case_id = st.session_state.get('case_name', 'New Case')
        
        # Check for duplicate case when not in edit mode
        if not hasattr(st.session_state, 'edit_mode') or not st.session_state.edit_mode:
            if not st.session_state.result_df.empty and 'case_id' in st.session_state.result_df.columns and case_id in st.session_state.result_df['case_id'].values:
                st.error(f"'{case_id}' case already exists. Please use a different name.")
                return False
        
        # Check required fields
        required_fields = ['delta_sigma1', 'delta_sigma12', 'span_length', 'annual_traffic', 'design_life']
        if not all(k in st.session_state for k in required_fields):
            st.error("Required input values are missing. Please fill in all fields.")
            return False
        
        # Update temporary result dataframe
        if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
            # Update case information
            st.session_state.temp_result_df.at[0, 'case_id'] = case_id  # case_id 명시적 설정
            st.session_state.temp_result_df.at[0, 'case_method'] = "Steel Girder(Direct Stress)"
            st.session_state.temp_result_df.at[0, 'Fatigue_method'] = "Steel Grider [Direct Stress]"
            
            # Save verification results if available
            if 'calc_direct_stress_ratio' in st.session_state:
                st.session_state.temp_result_df.at[0, 'direct_stress_ratio'] = st.session_state.calc_direct_stress_ratio
            if 'calc_shear_stress_ratio' in st.session_state:
                st.session_state.temp_result_df.at[0, 'shear_stress_ratio'] = st.session_state.calc_shear_stress_ratio
            
            # Delete existing case data if in edit mode
            if hasattr(st.session_state, 'edit_mode') and st.session_state.edit_mode:
                st.session_state.result_df = st.session_state.result_df[
                    st.session_state.result_df['case_id'] != case_id
                ]
            
            # Append new data
            result_df = pd.concat([st.session_state.result_df, st.session_state.temp_result_df])
            st.session_state.result_df = result_df
            
            # Clear edit mode
            if hasattr(st.session_state, 'edit_mode'):
                del st.session_state.edit_mode
            
            # Success message
            st.success(f"'{case_id}' case has been saved.")
            back_to_fatigue_case()
            return True
        
        return False
    
    # Check if in edit mode
    is_edit_mode = st.session_state.get('edit_mode', False)
    
    # Page title based on mode
    if is_edit_mode:
        st.markdown(f"<h5><b>[Edit] Steel Girder (Shear Stress) : {st.session_state.get('fatigue_case_name', '')}</b></h5>", unsafe_allow_html=True)
    else:
        st.markdown("<h5><b>Steel Girder (Shear Stress)</b></h5>", unsafe_allow_html=True)
    
    # Tab titles
    tabs = [
        "Fatigue Settings",
        "Design Parameters",
        "Correction Factor", 
        "Fatigue Result",
    ]

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(tabs)

    # First tab - Fatigue Settings
    with tab1:
        with st.container(border=False, height=800):
            st.markdown("<h6><b>Fatigue Settings</b></h6>", unsafe_allow_html=True)
            
            # Case name input with automatic generation for new cases
            if not is_edit_mode:
                # Generate default case name for new cases
                result_df = st.session_state.get('result_df', pd.DataFrame())
                new_case_num = len(result_df) + 1
                # Ensure unique case name
                while f"case_{new_case_num:03d}" in result_df.get('case_id', []):
                    new_case_num += 1
                default_case_name = f"case_{new_case_num:03d}"
            else:
                # Use existing case name for edit mode
                default_case_name = st.session_state.get('case_name', 'case_001')
            
            # Case name input field
            st.text_input("Case name", value=default_case_name, key='case_name', 
                        on_change=update_temp_from_input, args=('case_name',))
            
            # Check for duplicate case names (only for new cases)
            case_name = st.session_state.get('case_name', '')
            is_duplicate = False
            if not is_edit_mode:
                if 'result_df' in st.session_state and not st.session_state.result_df.empty and 'case_id' in st.session_state.result_df.columns:
                    if case_name in st.session_state.result_df['case_id'].values:
                        is_duplicate = True
                        st.error(f"'{case_name}' case already exists. Please use a different name.")

            # Update temp_result_df with case_id
            if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
                st.session_state.temp_result_df.at[0, 'case_id'] = case_name
                st.session_state.temp_result_df.at[0, 'case_method'] = "Steel Girder(Direct Stress)"
            
            # Span length
            span_length = st.number_input(
                r"Span length (m), $L$", 
                min_value=0.5,
                max_value=100.0,
                value=st.session_state.get('span_length', 35.0),
                key='span_length_widget', 
                on_change=update_temp_from_input, 
                args=('span_length_widget', 'span_length')
            )
            
            # Material strength parameters
            st.markdown("<h6><b>Fatigue Strength</b></h6>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                detail_category_shear = st.selectbox(
                    "Detail Category Shear", 
                    [
                        "100", "80"
                    ], 
                    index=["100", "80"].index(str(st.session_state.get('detail_category_shear', "100"))),
                    key="detail_category_shear_widget", 
                    on_change=update_temp_from_input, 
                    args=("detail_category_shear_widget", "detail_category_shear")
                )

            with col2:
                # detail_category 값을 먼저 가져옴
                detail_cat_shear = st.session_state.get('detail_category_shear', "100")
                
                # detail_category 값을 float으로 변환하여 delta_tau_amm의 기본값으로 사용
                delta_tau_amm = st.number_input(
                    r"Nominal fatigue Stress Range, $\Delta\tau_{amm}$ (MPa)", 
                    value=float(detail_cat_shear),
                    key='delta_tau_amm_widget', 
                    on_change=update_temp_from_input, 
                    args=('delta_tau_amm_widget', 'delta_tau_amm'),
                    disabled=True
                )
            st.session_state.delta_tau_amm = float(delta_tau_amm)
            # Auto-update delta_sigma_amm when detail_category changes
            if 'detail_category_widget' in st.session_state:
                st.session_state.delta_sigma_amm = float(st.session_state.detail_category_widget)
                
            st.markdown("<small>Note) For detail category, refer to constructional details in ENV1993-1-1</small>", unsafe_allow_html=True)

            # Direct Stress section
            st.markdown("<h6><b>Shear Stress Load</b></h6>", unsafe_allow_html=True)
            # Load import toggle
            use_midas = st.toggle("Import From Midas NX",
                value=bool(st.session_state.get('manual_input_direct', True)),
                key="manual_input_direct",
                on_change=update_temp_from_input,
                args=("manual_input_direct", )
            )

            with st.container(border=True):
                col1, col2  = st.columns(2, vertical_alignment="bottom")
                with col1:
                    if st.button("Import", use_container_width=True, key="from_midas_nx_shear", 
                                disabled=not st.session_state.manual_input_direct):
                        civil_stress_import("Import Direct Stress")
                
                with col2:
                    st.number_input(
                        r"$V_{s1}$ (kN)", 
                        value=float(st.session_state.get('Vs1', 1828.0)),
                        step=1.0, 
                        key="Vs1_widget",
                        on_change=update_temp_from_input,
                        args=("Vs1_widget", "Vs1"),
                        disabled=st.session_state.manual_input_direct,
                        placeholder="Import from Midas" if st.session_state.manual_input_direct else None
                    )
                    
                    # st.number_input(
                    #     r"$V_{s1+2}$ (kN)", 
                    #     value=float(st.session_state.get('Vs12', 1828.0)), 
                    #     step=1.0, 
                    #     key="Vs12_widget",
                    #     on_change=update_temp_from_input,
                    #     args=("Vs12_widget", "Vs12"),
                    #     disabled=st.session_state.manual_input_direct
                    # )

            # Update multiple fields to temp_result_df
           
        # Navigation buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- back", use_container_width=True):
                back_to_fatigue_case()
        with col3:
            # Validation function
            def has_correction_validation_errors1():
                return (
                    abs(float(st.session_state.get('Vs1', 0))) <= 0 or
                    float(st.session_state.get('span_length', 0)) <= 0
                )
            
            # Validation check with existing style
            validation_errors1 = has_correction_validation_errors1()
            if validation_errors1:
                if st.button("Next →", use_container_width=True, key="next_button_with_error1"):
                    update_temp_from_input_multi([])
                if abs(float(st.session_state.get('Vs1', 0))) <= 0:
                    st.toast("Vs1 value must be greater than 0", icon="⚠️")
                    validation_failed = True
                if st.session_state.get('span_length', 0) <= 0:
                    st.toast("Span length must be greater than 0", icon="⚠️")
                    validation_failed = True
                if not st.session_state.get('case_name'):
                    st.toast("Case name is required", icon="⚠️")
                    validation_failed = True
            else:
                if st.button("Next →", use_container_width=True, type="primary", key="next_button_without_error2"):
                    update_temp_from_input_multi(['case_name', 'span_length', 'Vs1','manual_input_direct','detail_category'])
                    add_tab_switch_button("Next", tabs[1])



    # Second tab - Correction Factor
    with tab2:

        with st.container(border=False, height=800):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h6><b>Section Properties</b></h6>", unsafe_allow_html=True)
            with col2:
                if use_midas == True:
                    use_properties = st.toggle("Manual/Auto Section Properties", key="manual_input_section", value=True)
                else:
                    use_properties = st.toggle("Manual/Auto Section Properties", key="manual_input_section", value=False, disabled=True, help="Automatic calculation is available only when Midas NX load is imported")

        
            col1, col2 = st.columns(2)
            with col1:



                get_Qn = st.session_state.get('get_Qn', 0)

                get_H = st.number_input(r"Section height, $h$ [mm]", 
                                value=st.session_state.get('get_total_height', 0),
                                key='get_total_height', 
                                on_change=update_temp_from_input, 
                                args=('get_total_height',),
                                disabled=use_properties)


                get_J = st.number_input(r"Moment of inertia in Girder alone, $J$ [mm⁴]", 
                        value=st.session_state.get('get_J', 0),
                        key='get_J', 
                        on_change=update_temp_from_input, 
                        args=('get_J',),
                        disabled=use_properties)  
            with col2:
                get_bw = st.number_input(r"Web thickness, $b_w$ [mm]", 
                                value=st.session_state.get('get_bw', 0),
                                key='get_bw', 
                                on_change=update_temp_from_input, 
                                args=('get_bw',),
                                disabled=use_properties)

                if get_H > 0:
                    st.session_state['get_Qn_steel'] =  get_J/get_H*2
                else:
                    st.session_state['get_Qn_steel'] = 0
                Qn = st.number_input(r"First moment of Area in centroid of Girder alone, $Q_n$ [mm³]", 
                        value=st.session_state.get('get_Qn_steel', 0),
                        key='widget_get_Qn_steel', 
                        on_change=update_temp_from_input, 
                        args=('widget_get_Qn_steel','get_Qn_steel'),
                        disabled=True)

            st.markdown("<h6><b>Design Parameters</b></h6>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            if st.session_state.get('bridge_type') == "Railway":
                with col1:
                    def update_category_and_type():
                        # traffic_category_widget 값을 세션에 저장
                        st.session_state['traffic_category'] = st.session_state['traffic_category_widget']
                        # category에 맞는 첫 번째 traffic_type으로 자동 세팅
                        types = {
                            "Standard": ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5", "Type 6", "Type 7", "Type 8", "Mixed EC"],
                            "Multiple/Underground": ["Type 9", "Type 10"],
                            "25t per axle": ["Type 5", "Type 6", "Type 11", "Type 12", "Mixed 25t"]
                        }
                        sel = st.session_state['traffic_category']
                        st.session_state['traffic_type_steel'] = types[sel][0]

                    traffic_category = st.selectbox(
                        "Traffic Category",
                        ["Standard", "Multiple/Underground", "25t per axle"],
                        index=["Standard", "Multiple/Underground", "25t per axle"].index(st.session_state.get('traffic_category', "Standard")),
                        key="traffic_category_widget",
                        on_change=update_category_and_type,  # 여기만 함수명 교체!
                    )

                    traffic_types = {
                        "Standard": ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5", "Type 6", "Type 7", "Type 8", "Mixed EC"],
                        "Multiple/Underground": ["Type 9", "Type 10"],
                        "25t per axle": ["Type 5", "Type 6", "Type 11", "Type 12", "Mixed 25t"]
                    }

                    selected_category = st.session_state.get('traffic_category', "Standard")
                    available_types = traffic_types.get(selected_category, traffic_types["Standard"])

                    traffic_type = st.selectbox(
                        "Traffic Type",
                        available_types,
                        index=min(
                            available_types.index(st.session_state.get('traffic_type_steel', available_types[0]))
                            if st.session_state.get('traffic_type_steel') in available_types else 0,
                            len(available_types) - 1),
                        key="traffic_type_steel_widget",
                        on_change=update_temp_from_input,
                        args=("traffic_type_steel_widget", "traffic_type_steel"),
                        disabled=st.session_state.get('bridge_type') == "Road",
                        help="Select the traffic type based on the selected category refer to EN 1991-2 for traffic categories."
                    )

                    st.session_state['design_life'] = st.session_state.get('nyear')
                with col2:
                    annual_traffic = st.number_input(
                        r"Annual traffic volume (million tons/year), $V$", 
                        min_value=5.0, max_value=50.0,
                        value=float(st.session_state.get('annual_traffic', 25.0)), 
                        step=5.0, 
                        key="annual_traffic_widget",
                        on_change=update_temp_from_input,
                        args=("annual_traffic_widget", "annual_traffic")
                    )
            else:
                with col1:
                    st.session_state['design_life'] = st.session_state.get('nyear')
                    nobs = st.number_input(
                        "Number of lorries per year in slow lane, $N_{obs}$",
                        min_value=0.25e6, max_value=2.00e6,
                        value=float(st.session_state.get('nobs', 1.00e6)),
                        step=0.25e6,
                        key="nobs_widget",
                        on_change=update_temp_from_input,
                        args=("nobs_widget", "nobs"),
                    )
                    qmk = st.number_input(
                        "Average gross weight of lorries (kN), $Q_{mk}$",
                        min_value=200.0, max_value=600.0,
                        value=float(st.session_state.get('qmk', 500.0)),
                        step=10.0,
                        key="qmk_widget",
                        on_change=update_temp_from_input,
                        args=("qmk_widget", "qmk")
                    )

                with col2:
                    location = st.selectbox(
                        "Location",
                        ["midspan", "support"],
                        index=["midspan", "support"].index(st.session_state.get('location', "midspan")),
                        key="location_widget",
                        on_change=update_temp_from_input,
                        args=("location_widget", "location"),
                    )


        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back", key="back_correction", use_container_width=True):
                add_tab_switch_button("Back", tabs[0])
        with col2:
            pass
        with col3:
            # Validation function
            if st.session_state.get('bridge_type') == "Railway":
                def has_correction_validation_errors2():
                    return (
                        float(st.session_state.get('get_bw', 0)) <= 0 or
                        float(st.session_state.get('get_J', 0)) <= 0 or
                        float(st.session_state.get('get_total_height', 0)) <= 0 or
                        float(st.session_state.get('get_Qn_steel', 0)) <= 0 or
                        float(st.session_state.get('annual_traffic', 0)) <= 0 or
                        not st.session_state.get('traffic_category') or
                        not st.session_state.get('traffic_type_steel')
                    )
                
                # Validation check with existing style
                validation_errors2 = has_correction_validation_errors2()
                if validation_errors2:
                    if st.button("Next →", use_container_width=True, key="next_button_with_error2"):
                        update_temp_from_input_multi([])
                        if float(st.session_state.get('get_bw', 0)) <= 0:
                            st.toast("Web thickness must be greater than 0", icon="⚠️")
                        if float(st.session_state.get('get_J', 0)) <= 0:
                            st.toast("Moment of inertia must be greater than 0", icon="⚠️")
                        if float(st.session_state.get('get_total_height', 0)) <= 0:
                            st.toast("Section height must be greater than 0", icon="⚠️")
                        if float(st.session_state.get('get_Qn_steel', 0)) <= 0:
                            st.toast("First moment of area must be greater than 0", icon="⚠️")
                        if float(st.session_state.get('annual_traffic', 0)) <= 0:
                            st.toast("Annual traffic volume must be greater than 0", icon="⚠️")
                        if not st.session_state.get('traffic_category'):
                            st.toast("Traffic category is required", icon="⚠️")
                        if not st.session_state.get('traffic_type_steel'):
                            st.toast("Traffic type is required", icon="⚠️")
                else:
                    if st.button("Next →", use_container_width=True, type="primary", key="next_button_without_error3"):
                        update_temp_from_input_multi([
                            'case_name', 'span_length', 'Vs1', 'get_bw', 'get_J', 'get_total_height', 
                            'get_Qn_steel', 'annual_traffic', 'traffic_category', 'traffic_type_steel','manual_input_direct'
                        ])
                        add_tab_switch_button("Next", tabs[2])
            else:
                # Validation function for Road bridge
                def has_correction_validation_errors2():
                    return (
                        float(st.session_state.get('get_bw', 0)) <= 0 or
                        float(st.session_state.get('get_J', 0)) <= 0 or
                        float(st.session_state.get('get_total_height', 0)) <= 0 or
                        float(st.session_state.get('get_Qn_steel', 0)) <= 0 or
                        float(st.session_state.get('nobs', 0)) <= 0 or
                        float(st.session_state.get('qmk', 0)) <= 0 
                    )
                
                # Validation check with existing style
                validation_errors2 = has_correction_validation_errors2()
                if validation_errors2:
                    if st.button("Next →", use_container_width=True, key="next_button_with_error2_road"):
                        update_temp_from_input_multi([])
                        if float(st.session_state.get('get_bw', 0)) <= 0:
                            st.toast("Web thickness must be greater than 0", icon="⚠️")
                        if float(st.session_state.get('get_J', 0)) <= 0:
                            st.toast("Moment of inertia must be greater than 0", icon="⚠️")
                        if float(st.session_state.get('get_total_height', 0)) <= 0:
                            st.toast("Section height must be greater than 0", icon="⚠️")
                        if float(st.session_state.get('get_Qn_steel', 0)) <= 0:
                            st.toast("First moment of area must be greater than 0", icon="⚠️")
                        if float(st.session_state.get('nobs', 0)) <= 0:
                            st.toast("Number of lorries must be greater than 0", icon="⚠️")
                        if float(st.session_state.get('qmk', 0)) <= 0:
                            st.toast("Average gross weight must be greater than 0", icon="⚠️")
                else:
                    if st.button("Next →", use_container_width=True, type="primary", key="next_button_without_error3_road"):
                        update_temp_from_input_multi([
                            'case_name', 'span_length', 'Vs1', 'get_bw', 'get_J', 'get_total_height', 
                            'get_Qn_steel', 'nobs', 'qmk', 'location','traffic_category','traffic_type_steel','manual_input_direct2'
                        ])
                        add_tab_switch_button("Next", tabs[2])
    with tab3:

        with st.container(border=False, height=800):

            st.markdown("<h6><b>Correction Factor</b></h6>", unsafe_allow_html=True)
            # Auto calculation toggle
            is_correction_auto=st.toggle(
                "Correction Factor Auto Calculate", 
                key="correction_factor_auto_calculate", 
                value=True, 
                on_change=update_temp_from_input, 
                args=("correction_factor_auto_calculate",)
            )   
            if st.session_state.get('bridge_type') == "Railway":
                with st.expander("Fatigue Stress Import Based on Single Track Evaluation Adjusted for Multi-Track Loading", expanded= is_correction_auto):

                    with st.container(border=True):
                        if is_correction_auto == False:
                            st.error("Note: Input is only required when using automatic calculation.")
                        else:
                            st.toggle(
                                "Import From Midas NX", 
                                key="manual_input_direct2", 
                                value=True, 
                                on_change=update_temp_from_input, 
                                args=("manual_input_direct2",)
                            )  

                            col1, col2, col3 = st.columns(3, vertical_alignment="bottom")
                            with col1:


                        
                                if st.button("Import", use_container_width=True, key="from_midas_nx_direct2", 
                                            disabled=not st.session_state.manual_input_direct2):
                                    civil_stress_import2("Import Direct Stress")
                                if not st.session_state.manual_input_direct2:
                                    st.session_state.delta_sigma_1 = st.session_state.get('delta_sigma1', 0)    
                                    st.session_state.delta_sigma_12 = st.session_state.get('delta_sigma12', 0)
                                else:    
                                    st.session_state.delta_sigma_1 = st.session_state.get('temp_delta_sigma_1', 0)
                                    st.session_state.delta_sigma_12 = st.session_state.get('temp_delta_sigma_12', 0)

                            with col2:
                                st.number_input(
                                    r"$\Delta\sigma_{1}$ (MPa)", 
                                    value=float(st.session_state.get('delta_sigma_1', 192.0)),
                                    step=1.0, 
                                    key="widget_delta_sigma_1",
                                    on_change=update_temp_from_input,
                                    args=("widget_delta_sigma_1", "delta_sigma_1"),
                                    disabled=st.session_state.manual_input_direct2,
                                    placeholder="Import from Midas" if st.session_state.manual_input_direct2 else None
                                )
                                
                            with col3:
                                st.number_input(
                                    r"$\Delta\sigma_{1+2}$ (MPa)", 
                                    value=float(st.session_state.get('delta_sigma_12', 229.0)), 
                                    step=1.0, 
                                    key="widget_delta_sigma_12",
                                    on_change=update_temp_from_input,
                                    args=("widget_delta_sigma_12", "delta_sigma_12"),
                                    disabled=st.session_state.manual_input_direct2
                                )
                            update_temp_from_input_multi(['delta_sigma_1', 'delta_sigma_12'])    
                            st.session_state.delta_sigma1 = st.session_state.get('widget_delta_sigma_1', 0)
                            st.session_state.delta_sigma12 = st.session_state.get('widget_delta_sigma_12', 0)    
                            update_temp_from_input_multi(['delta_sigma1', 'delta_sigma12'])




            if st.button("Correction Factor Calculate", use_container_width=True, 
                        disabled=not st.session_state.get('correction_factor_auto_calculate', True)):
                try:
                    # Lambda 계수 계산])
                    calculate_lambda_coefficients()
                    
                    # 피로 계산 수행
                    fatigue_steel_girder_shear_calculate()
                    
                    st.toast(f"Lambda coefficient calculation completed: λs = {st.session_state.get('calc_lambda_s', 0.0):.3f}", icon="✅")
                except Exception as e:
                    st.error(f"Error calculating lambda factors: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
            # Lambda 값들이 변경될 때마다 lambda_s 자동 계산하는 함수
            def update_lambda_and_calculate_lambda_s(widget_key, state_key=None):
                """Lambda 값 업데이트 후 lambda_s 자동 계산"""
                update_temp_from_input(widget_key, state_key)
                # lambda_s 자동 계산 (수동 모드에서만)
                if not st.session_state.get('correction_factor_auto_calculate', True):
                    lambda1 = st.session_state.get('calc_lambda1', 0.01)
                    lambda2 = st.session_state.get('calc_lambda2', 0.01)  
                    lambda3 = st.session_state.get('calc_lambda3', 0.01)
                    lambda4 = st.session_state.get('calc_lambda4', 0.01)
                    lambda_s = lambda1 * lambda2 * lambda3 * lambda4
                    
                    # lambda_max 제한 적용
                    lambda_max = st.session_state.get('calc_lambda_max', 2.0)
                    lambda_s_final = min(lambda_s, lambda_max)
                    
                    st.session_state.calc_lambda_s = lambda_s_final
                    st.session_state.lambda_s = lambda_s_final
            col1, col2 = st.columns(2, vertical_alignment="bottom")
            with col1:
                # Lambda1 
                st.number_input(
                    r"$\lambda_{1}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('calc_lambda1', 0.01)),
                    step=0.05, 
                    key="widget_calc_lambda1",
                    on_change=update_lambda_and_calculate_lambda_s,
                    args=("widget_calc_lambda1", "calc_lambda1"),
                    disabled=st.session_state.get('correction_factor_auto_calculate', True)
                )
                        
                # Lambda3
                st.number_input(
                    r"$\lambda_{3}$", 
                    min_value=0.00, 
                    value=float(st.session_state.get('calc_lambda3', 0.00)),
                    step=0.05, 
                    key="widget_calc_lambda3",
                    on_change=update_lambda_and_calculate_lambda_s,
                    args=("widget_calc_lambda3", "calc_lambda3"),
                    disabled=st.session_state.get('correction_factor_auto_calculate', True)
                )
                

                st.number_input(
                    r"$\lambda_{s}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('calc_lambda_s', 0.01)),
                    step=0.05, 
                    key="widget_calc_lambda_s",
                    on_change=update_temp_from_input,
                    args=("widget_calc_lambda_s", "calc_lambda_s"),
                    disabled=True
                )
                
            with col2:
                # Lambda2
                st.number_input(
                    r"$\lambda_{2}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('calc_lambda2', 0.01)),
                    step=0.05, 
                    key="widget_calc_lambda2",
                    on_change=update_lambda_and_calculate_lambda_s,
                    args=("widget_calc_lambda2", "calc_lambda2"),
                    disabled=st.session_state.get('correction_factor_auto_calculate', True)
                )            
                # Lambda4
                if st.session_state.get('bridge_type') == "Railway":
                    st.number_input(
                        r"$\lambda_{4}$", 
                        min_value=0.0, 
                        value=float(st.session_state.get('calc_lambda4', 0.01)),
                        step=0.05, 
                        key="widget_calc_lambda4",
                        on_change=update_lambda_and_calculate_lambda_s,
                        args=("widget_calc_lambda4", "calc_lambda4"),
                        disabled=st.session_state.get('correction_factor_auto_calculate', True),
                    )
                else:
                    tooltip_lambda4 = "λv4 is taken as 1.0 by simply assuming the same number and type of vehicles in each slow lane."
                    st.number_input(
                        r"$\lambda_{4}$", 
                        min_value=0.0, 
                        value=float(st.session_state.get('calc_lambda4', 0.0)),
                        step=0.05, 
                        key="widget_calc_lambda4",
                        on_change=update_lambda_and_calculate_lambda_s,
                        args=("widget_calc_lambda4", "calc_lambda4"),
                        disabled=st.session_state.get('correction_factor_auto_calculate', True),
                        help=tooltip_lambda4
                    )
                st.number_input(
                    r"$\lambda_{max}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('calc_lambda_max', 2.0)),
                    step=0.05, 
                    key="widget_calc_lambda_max",
                    on_change=update_temp_from_input,
                    args=("widget_calc_lambda_max", "calc_lambda_max"),
                    disabled=st.session_state.get('correction_factor_auto_calculate', True)
                )


            if st.session_state.get('bridge_type') == "Road":
                st.markdown("<small>Note: Assuming that the number of heavy vehicles is the same in each slow lane (𝑁₁ = 𝑁₂), and the type of lorry is also the same (𝑄ₘ₁ = 𝑄ₘ₂).</small>", unsafe_allow_html=True)
            else:
                st.markdown("<small></small>", unsafe_allow_html=True)
            # Lambda check
            if st.session_state.get('correction_factor_auto_calculate', True) == True:
                # Lambda check
                lambdaorigin = st.session_state.get('calc_lambda1', 0.0)* st.session_state.get('calc_lambda2', 0.0)* st.session_state.get('calc_lambda3', 0.0)* st.session_state.get('calc_lambda4', 0.0)
                if lambdaorigin > st.session_state.get('calc_lambda_max', 2.0):
                    st.markdown(f"<small>Since λs (={lambdaorigin:.3f}) > λmax({st.session_state.get('calc_lambda_max', 2.0):.3f}), λs is limited to λmax value ({st.session_state.get('calc_lambda_max', 2.0):.3f})</small>", unsafe_allow_html=True)
                else:
                    st.markdown("<small></small>", unsafe_allow_html=True)
            else:
                # Lambda check
                lambdaorigin = st.session_state.get('calc_lambda1', 0.0)* st.session_state.get('calc_lambda2', 0.0)* st.session_state.get('calc_lambda3', 0.0)* st.session_state.get('calc_lambda4', 0.0)
                if lambdaorigin > st.session_state.get('calc_lambda_max', 2.0):
                    st.markdown(f"<small>Since λs (={lambdaorigin:.3f}) > λmax({st.session_state.get('calc_lambda_max', 2.0):.3f}), λs is limited to λmax value ({st.session_state.get('calc_lambda_max', 2.0):.3f})</small>", unsafe_allow_html=True)
                else:
                    st.markdown("<small></small>", unsafe_allow_html=True)
            st.session_state['verification_options'] = ["Shear Stress"] 
            # Navigation buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back", key="back_design_Parameter", use_container_width=True):
                add_tab_switch_button("Back", tabs[1])
        with col2:
            pass
        with col3:
            # Validation function for lambda_s value only
            def has_correction_validation_errors3():
                return (
                    float(st.session_state.get('calc_lambda_s', 0)) <= 0
                )
            
            # Validation check with existing style
            validation_errors3 = has_correction_validation_errors3()
            if validation_errors3:
                if st.button("Next →", use_container_width=True, key="next_button_with_error3"):
                    update_temp_from_input_multi([])
                    if float(st.session_state.get('calc_lambda_s', 0)) <= 0:
                        st.toast("Calculated Lambda_s value must be greater than 0", icon="⚠️")
                    # if float(st.session_state.get('lambda_s', 0)) <= 0:
                    #     st.toast("Lambda_s value must be greater than 0", icon="⚠️")
            else:
                if st.button("Calculate Fatigue Result  →", use_container_width=True, type="primary", key="next_button_without_error4"):
                    update_temp_from_input_multi([
                        'calc_lambda_s', 'lambda_s', 'calc_lambda1', 'calc_lambda2', 
                        'calc_lambda3', 'calc_lambda4', 'pie_fat','calc_lambda_max', 'correction_factor_auto_calculate',
                        'manual_input_direct2','delta_sigma1','delta_sigma12','manual_input_direct','detail_category'
                    ])
                    add_tab_switch_button("Next", tabs[3])
                    fatigue_steel_girder_shear_calculate()



    # Third tab - Fatigue Result  
    # Fourth tab - Fatigue Result  
    with tab4:
        def final_check():
            try:
                if st.session_state.get('is_ok') == "N/A":
                    return True
            except:
                return False
        
        if validation_errors1 or validation_errors2 or validation_errors3 or final_check():
            if st.button("Calculate Fatigue Result", key="calculate_fatigue_result", use_container_width=True):
                st.error("Input values are not valid. Please check your input again.")
                
                # Common validation errors
                if st.session_state.get('case_name', '') == "":
                    st.error("Please enter Case Name.")
                if abs(st.session_state.get('calc_lambda_s', 0)) == 0:
                    st.error("Please enter Lambda s value.($\lambda_{s}$)")
                if abs(st.session_state.get('Vs1', 0)) == 0:
                    st.error("Please enter Shear force value.($V_{s1}$)")
                if float(st.session_state.get('get_bw', 0)) <= 0:
                    st.error("Please enter web width value.($b_w$)")
                if float(st.session_state.get('get_J', 0)) <= 0:
                    st.error("Please enter moment of inertia value.($J$)")
                if float(st.session_state.get('get_total_height', 0)) <= 0:
                    st.error("Please enter total height value.($h$)")
                if float(st.session_state.get('get_Qn_steel', 0)) <= 0:
                    st.error("Please enter shear lever arm value.($Q_n$)")
                # Bridge type specific validation errors
                if st.session_state.get('bridge_type') == "Railway":
                    if abs(st.session_state.get('annual_traffic', 0)) == 0:
                        st.error("Please enter Annual traffic volume value.($V$)")
                    if abs(st.session_state.get('delta_sigma1', 0)) == 0:
                        st.error("Please enter Direct stress value.($\Delta\sigma_{1}$)")
                    if abs(st.session_state.get('delta_sigma12', 0)) == 0:
                        st.error("Please enter Direct stress value.($\Delta\sigma_{1+2}$)")
                else:  # Road bridge
                    if abs(st.session_state.get('nobs', 0)) == 0:
                        st.error("Please enter Number of lorries per year in slow lane value.($N_{obs}$)")
                    if abs(st.session_state.get('qmk', 0)) == 0:
                        st.error("Please enter Average gross weight of lorries value.($Q_{mk}$)")
                
                if not validation_errors1 and not validation_errors2 and not validation_errors3:
                    if st.session_state.get('is_ok') == "N/A":
                        st.error("Calculation is needed. Please click the calculation button below.")

        else:

                # Results section
                with st.container(border=True, height=800):
                    if ('calc_shear_stress_ratio' in st.session_state and "Shear Stress" in st.session_state.get('verification_options', [])):
                        if st.session_state.get('input_changed', False):
                            st.warning("🔄 Input values have been changed. Please recalculate to see updated results.")
                            if st.button("Fatigue Result Recalculate", key="calculate_fatigue_result2", use_container_width=True):
                                fatigue_steel_girder_shear_calculate()
                                st.session_state.input_changed = False
                                st.rerun()
                    st.markdown("<h6><b>Steel Girder Fatigue Result (Shear Stress)</b></h6>", unsafe_allow_html=True)
                    
                    # Shear stress check result display
                    if 'calc_shear_stress_ratio' in st.session_state and "Shear Stress" in st.session_state.get('verification_options', []):
                        with st.container(border=True):
                            shear_stress_ratio = st.session_state.calc_shear_stress_ratio
                            delta_tau_equ = st.session_state.get('calc_delta_tau_equ', 0.0)
                            delta_tau_rsk = st.session_state.get('calc_delta_tau_rsk', 0.0)
                            is_ok = shear_stress_ratio <= 1.0
                            
                            col1, col2, col3, col4 = st.columns([10, 1, 9, 5], vertical_alignment="center")
                            with col1:
                                st.latex(r"\Delta\tau_{equ} = " + f"{delta_tau_equ:.3f}\t{{ MPa}}")
                            with col2:
                                st.latex(r"\leq" if is_ok else r">")
                            with col3:
                                st.latex(r"\Delta\tau_{Rsk} = " + f"{delta_tau_rsk:.3f}\t{{ MPa}}")
                            with col4:
                                if is_ok:
                                    st.markdown("<h5 style='color: green;'>OK</h5>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<h5 style='color: red;'>NG</h5>", unsafe_allow_html=True)
                    
                    # Detail calculation section
                    st.markdown("<h6><b>Detail Calculation of Steel Fatigue Result (Shear Stress)</b></h6>", unsafe_allow_html=True)
                    if st.session_state.correction_factor_auto_calculate ==False:
                        pass
                    else:
                        # Bridge type specific lambda coefficient displays
                        if st.session_state.get('bridge_type') == "Railway":
                            # Railway Lambda coefficients
                            
                            # Lambda1 results
                            lambda1 = st.session_state.get('calc_lambda1', 0.0)
                            st.write(r"Correction factor of $\lambda_{1}$ = " + f"{lambda1:.3f}")
                            with st.container(border=True):
                                span_length = st.session_state.get('span_length', 35.0)
                                traffic_type = st.session_state.get('traffic_type_steel', "Mixed EC")
                                traffic_category = st.session_state.get('traffic_category', "Standard")
                                st.latex(r"\lambda_{1} = \begin{cases} & \text{Span Length: " + str(span_length) + r"m} \\" + 
                                        r"      & \text{Traffic Type: " + str(traffic_type) + r"} \\" +
                                        r"      & \text{Traffic Category: " + str(traffic_category) + r"} \end{cases} = " + 
                                        f"{lambda1:.3f}")
                            
                            # Lambda2 results
                            lambda2 = st.session_state.get('calc_lambda2', 0.0)
                            annual_traffic = st.session_state.get('annual_traffic', 25.0)
                            st.write(r"Correction factor of $\lambda_{2}$ = " + f"{lambda2:.3f}")
                            with st.container(border=True):        
                                st.latex(r"\lambda_{2} = f(V) = f(" + f"{annual_traffic}" + r"\text{ million tons/year}) = " + f"{lambda2:.3f}")
                            
                            # Lambda3 results
                            lambda3 = st.session_state.get('calc_lambda3', 0.0)
                            design_life = st.session_state.get('design_life', 50)
                            st.write(r"Correction factor of $\lambda_{3}$ = " + f"{lambda3:.3f}")
                            with st.container(border=True):           
                                st.latex(r"\lambda_{3} = f(t_{LD}) = f(" + f"{design_life}" + r"\text{ years}) = " + f"{lambda3:.3f}")
                            
                            # Lambda4 results
                            lambda4 = st.session_state.get('calc_lambda4', 0.0)
                            delta_sigma1 = st.session_state.get('delta_sigma1', 0.0)
                            delta_sigma12 = st.session_state.get('delta_sigma12', 0.0)
                            stress_ratio = delta_sigma1 / delta_sigma12 if delta_sigma12 != 0 else 1.0
                            st.write(r"Correction factor of $\lambda_{4}$ = " + f"{lambda4:.3f}")
                            with st.container(border=True):
                                st.latex(r"\lambda_{4} = f\left(\frac{\Delta\sigma_{1}}{\Delta\sigma_{1+2}}\right) = f\left(\frac{" + 
                                        f"{delta_sigma1:.3f}" + "}{" + f"{delta_sigma12:.3f}" + r"}\right) = f(" + 
                                        f"{stress_ratio:.3f}" + ") = " + f"{lambda4:.3f}")
                        
                        else:  # Road bridge
                            # Road Lambda coefficients
                            
                            # Lambda1 results
                            lambda1 = st.session_state.get('calc_lambda1', 0.0)
                            span_length = st.session_state.get('span_length', 35.0)
                            location = st.session_state.get('location', "midspan")
                            st.write(r"Correction factor of $\lambda_{1}$ = " + f"{lambda1:.3f}")
                            with st.container(border=True):
                                st.latex(r"\lambda_{1} = \begin{cases} & \text{Span Length: " + str(span_length) + r"m} \\" + 
                                        r"      & \text{Location: " + str(location) + r"} \end{cases} = " + 
                                        f"{lambda1:.3f}")
                            
                            # Lambda2 results  
                            lambda2 = st.session_state.get('calc_lambda2', 0.0)
                            nobs = st.session_state.get('nobs', 1.0e6)
                            qmk = st.session_state.get('qmk', 500.0)
                            st.write(r"Correction factor of $\lambda_{2}$ = " + f"{lambda2:.3f}")
                            with st.container(border=True):        
                                # Format nobs properly
                                nobs_formatted = f"{nobs/1e6:.2f}" if nobs >= 1e6 else f"{nobs:.0f}"
                                unit_text = " million" if nobs >= 1e6 else ""
                                
                                st.latex(r"\lambda_{2} = f(N_{obs}, Q_{mk}) = f(" + nobs_formatted + unit_text + r", " + f"{qmk:.0f}" + r"\text{ kN}) = " + f"{lambda2:.3f}")
                            
                            # Lambda3 results
                            lambda3 = st.session_state.get('calc_lambda3', 0.0)
                            design_life = st.session_state.get('design_life', 50)
                            st.write(r"Correction factor of $\lambda_{3}$ = " + f"{lambda3:.3f}")
                            with st.container(border=True):           
                                st.latex(r"\lambda_{3} = f(t_{LD}) = f(" + f"{design_life}" + r"\text{ years}) = " + f"{lambda3:.3f}")
                            
                            # Lambda4 results (Road bridges typically use λ4 = 1.0)
                            lambda4 = st.session_state.get('calc_lambda4', 1.0)
                            st.write(r"Correction factor of $\lambda_{4}$ = " + f"{lambda4:.3f}")
                            with st.container(border=True):
                                st.latex(r"\lambda_{4} = 1.0 \text{ (for road bridges)}")
                    
                    # Common Lambda_s results for both bridge types
                    lambda_s = st.session_state.get('calc_lambda_s', 0.0)
                    lambda_max = st.session_state.get('calc_lambda_max', 2.0)
                    lambda1 = st.session_state.get('calc_lambda1', 0.0)
                    lambda2 = st.session_state.get('calc_lambda2', 0.0)
                    lambda3 = st.session_state.get('calc_lambda3', 0.0)
                    lambda4 = st.session_state.get('calc_lambda4', 0.0)
                    
                    st.write(r"Combined correction factor $\lambda_{s}$ = " + f"{lambda_s:.3f}")
                    with st.container(border=True):
                        st.latex(r"\lambda_{s} = \lambda_{1} \cdot \lambda_{2} \cdot \lambda_{3} \cdot \lambda_{4} = " + 
                                f"{lambda1:.3f}" + r" \cdot " + f"{lambda2:.3f}" + r" \cdot " + 
                                f"{lambda3:.3f}" + r" \cdot " + f"{lambda4:.3f}" + r" = " + f"{lambda_s:.3f}")
                    
                        is_lambda_ok = lambda_s <= lambda_max
                        
                        st.latex(r"\lambda_{s} = " + f"{lambda_s:.3f}" + 
                                (r" \leq " if is_lambda_ok else r" > ") + 
                                r"\lambda_{max} = " + f"{lambda_max:.3f}" + 
                                (r" \;\; \therefore \text{OK}" if is_lambda_ok else r" \;\; \therefore \text{NG}"))
                    
                    # Equivalent stress calculation section
                    st.markdown("<h6><b>Equivalent Stress Calculation</b></h6>", unsafe_allow_html=True)
                    
                    # Shear stress calculation
                    if "Shear Stress" in st.session_state.get('verification_options', []):
                        Vs1 = st.session_state.get('Vs1', 0.0)
                        Vs12 = st.session_state.get('Vs12', 0.0)
                        get_bw = st.session_state.get('get_bw', 0)
                        get_J = st.session_state.get('get_J', 0)
                        get_Qn_steel = st.session_state.get('get_Qn_steel', 0)
                        lambda_s = st.session_state.get('calc_lambda_s', 0.0)
                        
                        # Calculate tau1 from Vs1
                        if get_bw > 0 and get_J > 0:
                            tau1 = (abs(Vs1) * 1000 * get_Qn_steel) / (get_bw * get_J)
                        else:
                            tau1 = 0.0
                        st.markdown(
                            r"Shear stress: $\Delta\tau_{1} = \frac{|V_{s,1}| \cdot 1000 \cdot Q_n}{b_w \cdot J} = \frac{" 
                            + f"{abs(Vs1):.1f} \cdot 1000 \cdot {get_Qn_steel:.1f}" 
                            + "}{" + f"{get_bw:.1f} \cdot {get_J:.1f}" + "} = "
                            + f"{tau1:.3f}" + r"\text{ MPa}$",
                            unsafe_allow_html=True
                        )
                        delta_tau_equ = st.session_state.get('calc_delta_tau_equ', 0.0)
                        st.markdown(r"Equivalent shear stress range: $\Delta\tau_{equ} = \Delta\tau_{1} \cdot \lambda_{s} = " + 
                                f"{tau1:.3f}" + r" \cdot " + f"{lambda_s:.3f}" + r" = " + f"{delta_tau_equ:.3f}" + r"\text{ MPa}$", 
                                unsafe_allow_html=True)

                    # Design strength section
                    gamma_m = st.session_state.get('factor_rm', 1.35)

                    # Shear stress strength
                    if "Shear Stress" in st.session_state.get('verification_options', []):
                        delta_tau_amm = st.session_state.get('delta_tau_amm', 80.0)
                        delta_tau_rsk = st.session_state.get('calc_delta_tau_rsk', 0.0)
                        st.markdown(r"Design shear stress fatigue strength: $\Delta\tau_{Rsk} = \frac{\Delta\tau_{C}}{\gamma_{M}} = \frac{" + 
                                f"{delta_tau_amm:.3f}" + "}{" + f"{gamma_m:.3f}" + "} = " + f"{delta_tau_rsk:.3f}" + r"\text{ MPa}$", 
                                unsafe_allow_html=True)

                    # Shear stress verification
                    if "Shear Stress" in st.session_state.get('verification_options', []):
                        delta_tau_equ = st.session_state.get('calc_delta_tau_equ', 0.0)
                        delta_tau_rsk = st.session_state.get('calc_delta_tau_rsk', 0.0)
                        shear_stress_ratio = st.session_state.get('calc_shear_stress_ratio', 0.0)
                        
                        # 판정 결과
                        is_ok = shear_stress_ratio <= 1.0
                        
                        with st.container(border=True):
                            # 부등식 표시
                            st.latex(r"\Delta\tau_{equ} \leq \Delta\tau_{Rsk}")
                            
                            # 실제 값과 판정 표시
                            st.latex(f"{delta_tau_equ:.3f}" + r" \text{ MPa} " + 
                                    (r"\leq " if is_ok else r"> ") + 
                                    f"{delta_tau_rsk:.3f}" + r" \text{ MPa} " +
                                    (r"\;\; \therefore \text{OK}" if is_ok else r"\;\; \therefore \text{NG}"))
                            
                            # 비율 표시
                            st.latex(r"\frac{\Delta\tau_{equ}}{\Delta\tau_{Rsk}} = " + 
                                    f"{shear_stress_ratio:.3f} " +
                                    (r"\leq 1.0" if is_ok else r"> 1.0"))

                    else:
                        st.info("No calculation results available. Please click 'Calculate' on the Correction Factor tab first.")
                        
                # # Calculate button
                # if st.button("Calculate", key="calculate_results", use_container_width=True):
                #     calculate_lambda_coefficients()
                #     fatigue_steel_girder_shear_calculate()
                #     st.rerun()

        # Navigation buttons 결과저장
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back", key="back_result", use_container_width=True):
                add_tab_switch_button("Back", tabs[2])
        with col2:
            pass
        with col3:
            fatigue_steel_girder_shear_calculate()
            button_text = "Update" if is_edit_mode else "Save Result"
            if st.button(button_text, key="save_fatigue_result", use_container_width=True, type="primary"):
                # 계산 수행 (아직 수행되지 않은 경우)
                if 'calc_shear_stress_ratio' not in st.session_state:
                    if not fatigue_steel_girder_shear_calculate():
                        st.error("Please calculate first.")
                        return
                
                # temp_result_df 업데이트
                if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
                    # 케이스 정보 업데이트
                    st.session_state.temp_result_df.at[0, 'case_id'] = st.session_state.case_name
                    st.session_state.temp_result_df.at[0, 'case_method'] = "Steel Girder(Shear Stress)"
                    
                    # 판정값 저장
                    st.session_state.temp_result_df.at[0, 'shear_stress_ratio'] = st.session_state.get('calc_shear_stress_ratio', 0)
                    st.session_state.temp_result_df.at[0, 'is_ok'] = st.session_state.is_ok
                    update_temp_from_input_multi(['case_name', 'span_length', 'Vs1','manual_input_direct','detail_category'])
                    update_temp_from_input_multi([
                        'case_name', 'span_length', 'Vs1', 'get_bw', 'get_J', 'get_total_height', 
                        'get_Qn_steel', 'nobs', 'qmk', 'location','traffic_category','traffic_type_steel','manual_input_direct2'
                    ])
                    update_temp_from_input_multi([
                        'calc_lambda_s', 'lambda_s', 'calc_lambda1', 'calc_lambda2', 
                        'calc_lambda3', 'calc_lambda4', 'pie_fat','calc_lambda_max', 'correction_factor_auto_calculate',
                        'manual_input_direct2','delta_sigma1','delta_sigma12','manual_input_direct','detail_category'
                    ])
                    # save_to_result_df 함수 사용하여 저장
                    if save_to_result_df():
                        st.success(f"'{st.session_state.case_name}' case has been saved.")
                        back_to_fatigue_case()
                    else:
                        st.error("Error occurred while saving.")
                else:
                    st.error("No data to save.")


#계수계산
def calculate_lambda_coefficients():
    """Calculate lambda coefficients for steel fatigue"""
    if st.session_state.get('bridge_type') == "Railway":
        from projects.concrete_fatigue_analysis_ntc2018.calc.steelgirder_lambda import (
            get_lambda1_rail, get_lambda2_rail, get_lambda3_rail, get_lambda4_rail,
            calculate_lambda_s_rail, check_lambda_max
        )
        
        # 입력값 가져오기
        span_length = st.session_state.get('span_length', 35.0)
        annual_traffic = st.session_state.get('annual_traffic', 25.0)
        design_life = st.session_state.get('design_life', 50)
        delta_sigma1 = st.session_state.get('delta_sigma1', 192.0)
        delta_sigma12 = st.session_state.get('delta_sigma12', 229.0)
        traffic_type = st.session_state.get('traffic_type_steel', "Mixed EC")
        traffic_category = st.session_state.get('traffic_category', "Standard")
        
        # Lambda 계수 계산
        lambda1 = get_lambda1_rail(span_length, traffic_type, traffic_category)
        lambda2 = get_lambda2_rail(annual_traffic)
        lambda3 = get_lambda3_rail(design_life)
        
        # 응력비 계산
        stress_ratio = delta_sigma1 / delta_sigma12 if delta_sigma12 != 0 else 1.0
        lambda4 = get_lambda4_rail(stress_ratio)
        
        # 결합된 Lambda 계수 계산
        lambda_s = calculate_lambda_s_rail(lambda1, lambda2, lambda3, lambda4)
        
        # Lambda max 체크
        is_lambda_ok, lambda_max = check_lambda_max(lambda_s, is_railway=True)
        
        # 최종 lambda_s는 lambda_max를 초과하지 않도록 제한
        lambda_s_final = min(lambda_s, lambda_max)
        
        # 계산 결과를 세션 상태에 저장
        st.session_state.calc_lambda1 = lambda1
        st.session_state.calc_lambda2 = lambda2
        st.session_state.calc_lambda3 = lambda3
        st.session_state.calc_lambda4 = lambda4
        st.session_state.calc_lambda_s = lambda_s_final
        st.session_state.calc_lambda_max = lambda_max
        st.session_state.calc_lambda_check = "OK" if is_lambda_ok else "NG"
        
    elif st.session_state.get('bridge_type') == "Road":
        from projects.concrete_fatigue_analysis_ntc2018.calc.steelgirder_lambda import (
            get_lambda1_road, get_lambda2_road, get_lambda3_road, get_lambda4_road,
            calculate_lambda_s_road, check_lambda_max
        )
        # 입력값 가져오기
        span_length = st.session_state.get('span_length', 35.0)
        print(st.session_state.get('qmk'))
        qmk = st.session_state.get('qmk', 500)  # 트럭 평균 중량 (kN)
        print(st.session_state.get('nobs'))
        nobs = st.session_state.get('nobs', 1e6)  # 연간 트럭 통행량
        design_life = st.session_state.get('design_life', 50)
        location = st.session_state.get('location', "midspan")
        
        # Lambda 계수 계산
        lambda1 = get_lambda1_road(span_length, location)
        lambda2 = get_lambda2_road(qmk, nobs)
        lambda3 = get_lambda3_road(design_life)
        lambda4 = 1
        
        # 결합된 Lambda 계수 계산
        lambda_s = calculate_lambda_s_road(lambda1, lambda2, lambda3, lambda4)
        
        # Lambda max 체크
        is_lambda_ok, lambda_max = check_lambda_max_road(lambda_s, span_length, location)
        
        # 최종 lambda_s는 lambda_max를 초과하지 않도록 제한
        lambda_s_final = min(lambda_s, lambda_max)
        
        # 계산 결과를 세션 상태에 저장
        st.session_state.calc_lambda1 = lambda1
        st.session_state.calc_lambda2 = lambda2
        st.session_state.calc_lambda3 = lambda3
        st.session_state.calc_lambda4 = lambda4
        st.session_state.calc_lambda_s = lambda_s_final
        st.session_state.calc_lambda_max = lambda_max
        st.session_state.calc_lambda_check = "OK" if is_lambda_ok else "NG"
        
    else:
        st.error("Bridge type not found")


# with st.container(border=True, height=600):
#     debug_df = st.session_state.temp_result_df
#     st.dataframe(debug_df)  
#     debug_result_df = st.session_state.result_df
#     st.dataframe(debug_result_df)
#     st.sidebar.write("Session Values:", st.session_state)


'''이코드의 입력값들  
Steel Girder (Shear Stress)  

1page (Fatigue Settings)  
- case_name  
- span_length  
- detail_category_shear  
- delta_tau_amm  
- manual_input_direct  
- Vs12  
- manual_input_direct2  
- delta_sigma1  
- delta_sigma12  

2page (Design Parameters)  
- manual_input_section  
- h  
- bw  
- get_Qn_steel  
- get_J  
- annual_traffic  
- traffic_category  
- traffic_type_steel  
- nobs  
- qmk  
- location  

3page (Correction Factor)  
- correction_factor_auto_calculate  
- lambda1  
- lambda2  
- lambda3  
- lambda4  
- lambda_s  
- lambdamax  

4page (Fatigue Result)  
- (입력값 없음)  

자동 계산값  
- calc_lambda1  
- calc_lambda2  
- calc_lambda3  
- calc_lambda4  
- calc_lambda_s  
- calc_lambda_max  
- calc_lambda_check  
- calc_delta_tau_rsk  
- calc_delta_tau_equ  
- calc_shear_stress_ratio  
- calc_is_ok  
- is_ok  '''