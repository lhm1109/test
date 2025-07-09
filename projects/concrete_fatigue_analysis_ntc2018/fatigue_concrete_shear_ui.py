# fatigue_concrete_shear_ui.py
#0611 check

import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import math
from projects.concrete_fatigue_analysis_ntc2018.session_manager import *
from projects.concrete_fatigue_analysis_ntc2018.calc.shear_resistance import *
import matplotlib.pyplot as plt
import numpy as np
import re

# PageManager 네비게이션 import
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from projects.concrete_fatigue_analysis_ntc2018.utils.navigator import back_to_fatigue_case

# 세션 초기화
initialize_session()
# 모달 다이얼로그 가져오기 
import_dialogs = SessionManager.initialize_import_dialogs() if 'SessionManager' in globals() else None
civil_stress_import = import_dialogs['shear_force'] if import_dialogs else None

def calculate_results():
   
    try:
        # 입력값 가져오기
        Vsdmax = abs((st.session_state.Vsdmax))
        Vsdmin = abs((st.session_state.Vsdmin))
        Qn = float(st.session_state.get_Qn)
        J = float(st.session_state.get_J)
        bw = float(st.session_state.get_bw)
        # girder_d = float(st.session_state.get_d)
        slab_d = float(st.session_state.get_slab_d)
        total_height = float(st.session_state.get_total_height)
        d = total_height *0.85
        Vrd_c = float(st.session_state.Vrd_c)
        if bw == 0:
            bw= 1e-6
        if J == 0:
            J= 1e-6
        if d == 0:
            d= 1e-6
        # 전단응력 계산
        Tmax = (Vsdmax * 1000)*Qn / (bw *J)  # MPa 단위
        Tmin = (Vsdmin * 1000)*Qn / (bw * J)  # MPa 단위
        
        # TRd1 계산 (EC2 기준에 따른 무보강 단면의 전단저항응력)
        TRd1 = (Vrd_c * 1000) / (bw * d )  # MPa 단위
        if TRd1 == 0:
            TRd1 = 1e-6
        # 비율 계산
        Tmax_TRd1 = Tmax / TRd1
        Tmin_TRd1 = Tmin / TRd1
        
        # OK/NG 판정
        # 이미지의 조건식에 따라 판정
        if Tmax == 0:
            ratio = 0
        else:
            ratio = Tmin/Tmax
        if ratio >= 0:
            discriminant = (Tmax_TRd1 <= 0.5 + 0.45*Tmin_TRd1) and (Tmax_TRd1 <= 0.9)
        else:
            discriminant = Tmax_TRd1 <= 0.5 - abs(Tmin_TRd1)
        
        # 계산 결과 저장
        st.session_state.get_effective = d
        st.session_state.Tmax = Tmax
        st.session_state.Tmin = Tmin
        st.session_state.TRd1 = TRd1
        st.session_state.Tmax_TRd1 = Tmax_TRd1
        st.session_state.Tmin_TRd1 = Tmin_TRd1
        if discriminant:
            st.session_state.is_ok = "OK"
        else:
            st.session_state.is_ok = "NG"

        st.session_state.discriminant = 0.9 - Tmax_TRd1  # 판정값
        
        # 결과 저장 - temp_result_df에도 저장
        update_temp_from_input_multi([
            'Tmax', 'Tmin', 'TRd1', 'Tmax_TRd1', 'Tmin_TRd1', 'get_effective',
            'is_ok', 'discriminant', 'Fatigue_method'
        ])
        
        return True
    except Exception as e:
        st.toast(f"Error during calculation: {str(e)}", icon="⚠️")
        return False


def fatigue_concrete_shear_ui_page():
    # Set fatigue method
    st.session_state.Fatigue_method = "Concrete Shear(Not Require Reinforcement)"
    # 편집 모드 체크
    is_edit_mode = st.session_state.get('edit_mode', False)
    
    # 편집 모드일 경우 페이지 제목 변경
    if is_edit_mode:
        st.markdown(f"<h5><b>[Edit]Shear Fatigue(Not Reinforced):{st.session_state.get('fatigue_case_name', '')}</b></h5>", unsafe_allow_html=True)
    else:
        st.markdown("<h5><b>Shear Fatigue(Not Reinforced)</b></h5>", unsafe_allow_html=True)
    
    # 탭 제목
    tabs = [
        "Fatigue Settings",
        "Section Properties",
        "Fatigue Result"

    ]

    # 탭 생성
    tab1, tab2, tab3 = st.tabs(tabs)

    # 첫번째 탭 - Fatigue Settings
    with tab1:
        with st.container(height=800, border=False):
            st.markdown("<h6><b>Fatigue Settings</b></h6>", unsafe_allow_html=True)
        

            # Case name input with automatic generation for new cases
            if not is_edit_mode:
                result_df = st.session_state.get('result_df', pd.DataFrame())
                existing_ids = result_df.get('case_id', [])

                used_nums = []
                for cid in existing_ids:
                    match = re.fullmatch(r"case_(\d+)", str(cid))
                    if match:
                        used_nums.append(int(match.group(1)))

                next_num = 1
                while next_num in used_nums:
                    next_num += 1

                default_case_name = f"case_{next_num:03d}"
            else:
                default_case_name = st.session_state.get('case_name', 'case_001')

            case_name = st.text_input("Case name", value=default_case_name)

            # 세션 상태에 강제 저장
            st.session_state['case_name'] = case_name

            # 중복 체크
            is_duplicate = (
                not is_edit_mode
                and case_name in st.session_state.get("result_df", pd.DataFrame()).get("case_id", [])
            )
            if is_duplicate:
                st.toast(f"'{case_name}' case already exists. Please use a different name.")

            # 이후에도 update_temp_from_input 쓸 수 있음
            update_temp_from_input("case_name", "case_name")


            
            fck = st.number_input(r"Concrete compressive strength, $f_{ck}$ [MPa]", 
                            value=st.session_state.get('fck',20),
                            key='fck_widget', 
                            on_change=update_temp_from_input, 
                            args=('fck_widget','fck'),)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h6><b>Fatigue Load</b></h6>", unsafe_allow_html=True,help="Load combinations are required for concrete design")
            with col2:
                # 하중 불러오기 옵션
                use_midas = st.toggle("Import From Midas NX",
                                    value=st.session_state.get('import_option', True), 
                                    key="manual_input", 
                                    on_change=update_temp_from_input,
                                    args=("widget_import_option", "import_option")
                                    )
                st.session_state.import_option = use_midas


            with st.container(border=True):
                col1, col2, col3 = st.columns(3, vertical_alignment="bottom")
                with col1:
                    if st.button("Import", use_container_width=True, key="from_midas_nx", 
                                disabled=not use_midas or civil_stress_import is None):
                        if civil_stress_import:
                            civil_stress_import("Import")

                with col2:
                    # Vsdmax
                    st.number_input(r"Maximum Shear, $V_{sd,max}$ [KN]", 
                                value=abs(float(st.session_state.get('Vsdmax', 0.00))),
                                step=1.0, 
                                key="widget_Vsdmax",
                                on_change=update_temp_from_input,
                                args=("widget_Vsdmax", "Vsdmax"),
                                disabled=use_midas)
                    
                    # 직접 입력 시 세션 상태 업데이트
                    if not use_midas and 'widget_Vsdmax' in st.session_state:
                        st.session_state.Vsdmax = st.session_state.widget_Vsdmax

                with col3:
                    # Vsdmin
                    st.number_input(r"Minimum Shear, $V_{sd,min}$ [KN]", 
                                value=abs(float(st.session_state.get('Vsdmin', 0.00))),
                                step=1.0, 
                                key="widget_Vsdmin",
                                on_change=update_temp_from_input,
                                args=("widget_Vsdmin", "Vsdmin"),
                                help="Minimum shear force at the same section (Location I or J) where maximum shear occurs",
                                disabled=use_midas)
                    
                    # 직접 입력 시 세션 상태 업데이트
                    if not use_midas and 'widget_Vsdmin' in st.session_state:
                        st.session_state.Vsdmin = st.session_state.widget_Vsdmin
        update_temp_from_input_multi(['Vsdmax', 'Vsdmin', 'fck', 'import_option'])
        # 네비게이션 및 저장 버튼
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- back", use_container_width=True):
                back_to_fatigue_case()

        with col3:

            # 이름 중복 확인 및 오류 메시지 표시    
            case_name = st.session_state.get('case_name', '')
            is_duplicate = False
            # 수정 모드가 아닐 때만 중복 체크
            if not st.session_state.get('edit_mode', False):
                # 세션 상태에 result_df가 있는지 확인
                if 'result_df' in st.session_state:
                    # result_df가 비어있지 않은지 확인 
                    if not st.session_state.result_df.empty:
                        # result_df에 case_id 컬럼이 있는지 확인
                        if 'case_id' in st.session_state.result_df.columns:
                            # 현재 case_name이 기존 case_id들 중에 있는지 확인
                            if case_name in st.session_state.result_df['case_id'].values:
                                # 중복된 경우 처리
                                is_duplicate = True
                                # 중복 알림 메시지 표시
                                st.toast(f"Case '{case_name}' already exists. Please use a different name.", icon="⚠️")
            # 유효성 검사 실패 여부 확인 함수
            def has_validation_errors():
                # 필수 입력값 체크
                if st.session_state.get('Vsdmax', 0) == 0:
                    return True
                if abs(st.session_state.get('Vsdmin', 0)) > abs(st.session_state.get('Vsdmax', 0)):
                    return True
                if abs(st.session_state.get('fck', 0)) == 0:
                    return True
                return False
            # 중복일 경우 또는 유효성 검사 실패 시 Next 버튼 비활성화
            validation_errors = has_validation_errors()
            if validation_errors:
                # 버튼 먼저!
                if st.button("Next →", use_container_width=True, key="next_button_with_error"):
                    # 메시지 출력 후 리턴
                    if st.session_state.get('Vsdmax', 0) == 0:
                        st.toast("Maximum Shear is required(Vsd,max)", icon="⚠️")
                    elif abs(st.session_state.get('Vsdmin', 0)) > abs(st.session_state.get('Vsdmax', 0)):
                        st.toast("Vsd,min must be less than Vsd,max(Vsd,min < Vsd,max).")
                    elif abs(st.session_state.get('fck', 0)) == 0:
                        st.toast("Enter fck value(fck).")
                    calculate_results()
            else:
                if st.button("Next →", use_container_width=True, type="primary", key="next_button_without_error"):
                    update_temp_from_input_multi(['Vsdmax', 'Vsdmin', 'fck', 'import_option'])
                    add_tab_switch_button("Next", tabs[1])

            # if st.button("Next →", use_container_width=True):
            #     add_tab_switch_button("Next", tabs[1])
            # 계산 로직

    with tab2:
        with st.container(border=False, height=800):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("<h6><b>Section Properties</b></h6>", unsafe_allow_html=True)

            with col2:
                # 세션 상태 강제 보정
                if "manual_input_properties" in st.session_state:
                    if not isinstance(st.session_state["manual_input_properties"], bool):
                        st.session_state["manual_input_properties"] = True
                else:
                    st.session_state["manual_input_properties"] = True

                # 토글 렌더링
                if use_midas:
                    use_properties = st.toggle(
                        "Manual/Auto Section Properties",
                        key="manual_input_properties",
                        value=st.session_state.get('manual_input_properties', True),
                        help="Automatic calculation is available only when Midas NX load is imported"
                    )
                else:
                    use_properties = st.toggle(
                        "Manual/Auto Section Properties",
                        key="manual_input_properties",
                        value=False,
                        disabled=True,
                        help="Automatic calculation is available only when Midas NX load is imported"
                    )

            
            # 단면 특성 입력
            col1, col2 = st.columns(2)
                
            with col1:
                if st.session_state.get('get_total_height', 0.00) != 0:
                    st.session_state.get_effective = st.session_state.get('get_total_height', 0.00)*0.85
                elif st.session_state.get('d', 0.00) != 0 and is_edit_mode:
                    st.session_state.get_effective = st.session_state.get('d', 0.00)
                else:
                    st.session_state.get_effective = st.session_state.get('get_effective_widget', 0.00)
                d = st.number_input(r"Effective height, $d$ [mm]", 
                                value=float(st.session_state.get('get_effective', 0.00)),
                                key='get_effective_widget', 
                                on_change=update_temp_from_input, 
                                args=('get_effective_widget','get_effective'),
                                disabled=use_properties)
                
                Qn = st.number_input(r"First moment of Area of Girder alone,$Q_n$ [mm³]", 
                                value=st.session_state.get('get_Qn', 0),
                                key='Qn_widget', 
                                on_change=update_temp_from_input, 
                                args=('Qn_widget','get_Qn'),
                                disabled=use_properties)

            
            with col2:
                bw = st.number_input(r"Web thickness, $b_w$ [mm]", 
                                value=st.session_state.get('get_bw', 0),
                                key='bw_widget', 
                                on_change=update_temp_from_input, 
                                args=('bw_widget','get_bw'),
                                disabled=use_properties)
                J = st.number_input(r"Moment of inertia in Girder alone, $J$ [mm⁴]", 
                                value=st.session_state.get('get_J', 0),
                                key='J_widget', 
                                on_change=update_temp_from_input, 
                                args=('J_widget','get_J'),
                                disabled=use_properties)
            


            col1, col2 = st.columns(2)
            with col1:
                    st.markdown("<h6><b>Section Shear Resistance</b></h6>", unsafe_allow_html=True)
            with col2:
                if use_midas == True and use_properties == True:
                    use_shear_resistance = st.toggle("Manual/Auto Shear Resistance",value=st.session_state.get('manual_shear_resistance', True), key="manual_shear_resistance",)
                else:
                    use_shear_resistance = st.toggle("Manual/Auto Shear Resistance", value=False, key="manual_shear_resistance", disabled=True, help="Automatic calculation is available only when Midas NX load is imported")



            with st.container(border=True):
                col1, col2 = st.columns(2, vertical_alignment="bottom")
                with col1:
                    # Check if all required values are present and non-zero
                    try:
                        required_values_present = (
                            st.session_state.temp_result_df.at[0, 'get_Qn'] > 0 and
                            st.session_state.get('get_bw', 0) > 0 and 
                            st.session_state.get('get_J', 0) > 0
                        )
                    except:
                        required_values_present = False

                    if st.button("Calculate Shear Resistance", help="Automatic calculation is available only when Midas NX Section Properties are defined",
                                key="calculate_vrdc",
                                disabled=not required_values_present or use_shear_resistance == False):
                        update_temp_from_input_multi(['Fatigue_method', 'fck', 'bw', 'J', 'd', 'Qn', 'get_bw', 'get_J', 'get_effective', 'get_Qn', 'get_total_height', 'manual_shear_resistance', 'manual_input_properties'])
                        result = calculate_shear_strength()
                        if result:
                            VRd_c, dp, is_required_reinforcement, fctd, fb = result
                            st.session_state.fctd = fctd
                            st.session_state.fb = fb
                            st.session_state.VRd_c = VRd_c

                with col2:
                    Vrd_c = st.number_input(r"Shear Resistance, $V_{Rd,c}$ [KN]", 
                                    value=st.session_state.get('VRd_c', 0.000),
                                    key='Vrd_c', 
                                    on_change=update_temp_from_input, 
                                    disabled=use_shear_resistance,
                                    args=('Vrd_c',), 
                                    help="The section is classified based on cracking ($f_b > f_{ctd}$). For cracked sections, $V_{Rd,c}$ is calculated using composite properties according to EC2. For uncracked sections, reinforcement ratio and compressive stress are considered. Shear reinforcement is required if $V_{Ed} > V_{Rd,c}$")
            
            #크랙단면 판정
            if 'fb' in st.session_state and 'fctd' in st.session_state:
                fb = st.session_state.fb
                fctd = st.session_state.fctd
                if fb == 0:
                    if Vrd_c != 0 and use_shear_resistance == False:
                        # st.success("Manual input is required for shear resistance calculation.")
                        pass
                    else:
                        st.warning("Shear resistance calculation is required. Please check input values.", icon="⚠️")

                else:
                    if st.session_state.fb > st.session_state.fctd:
                        st.warning(f"Cracked section (($f_b > f_{{ctd}}$ : {fb:.2f} > {fctd:.2f})")
                    else:
                        st.success(f"Non-cracked section (($f_b \\leq f_{{ctd}}$) : {fb:.2f} ≤ {fctd:.2f})")
            else:
                st.info("Please check section shear resistance by clicking 'Calculate shear resistance' button")



        # 네비게이션 및 저장 버튼
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- Back", key="back_to_fatigue_settings2", use_container_width=True):
                add_tab_switch_button("Back", tabs[0])
        with col3:
            # 탭2 유효성 검사 실패 여부 확인 함수
            def has_validation_errors2():
                try:
                    # 필수 입력값 체크
                    if abs(st.session_state.temp_result_df.at[0, 'get_bw']) == 0:
                        return True
                    if abs(st.session_state.temp_result_df.at[0, 'get_J']) == 0:
                        return True
                    if abs(st.session_state.temp_result_df.at[0, 'get_Qn']) == 0:
                        return True
                    if abs(st.session_state.temp_result_df.at[0, 'get_effective']) == 0:
                        return True
                    if Vrd_c == 0:
                        return True
                except:
                    if Vrd_c == 0:
                        return True
                return False

            # 중복일 경우 또는 유효성 검사 실패 시 Next 버튼 비활성화  
            validation_errors2 = has_validation_errors2()
            if validation_errors2:
                # 버튼 먼저!
                if st.button("Next →", use_container_width=True, key="next_tab2_with_error"):
                    # 메시지 출력 후 리턴
                    try:
                        # if abs(st.session_state.temp_result_df.at[0, 'bw']) == 0:
                        #     st.toast("Web thickness is required(b_w)", icon="⚠️")
                        # if abs(st.session_state.temp_result_df.at[0, 'J']) == 0:
                        #     st.toast("Moment of inertia in Girder alone is required(J)", icon="⚠️")
                        # if abs(st.session_state.temp_result_df.at[0, 'Qn']) == 0:
                        #     st.toast("First moment of Area of Girder alone is required(Qn)", icon="⚠️")
                        # if abs(st.session_state.temp_result_df.at[0, 'd']) == 0:
                        #     st.toast("Section height is required(d)", icon="⚠️")
                        if abs(st.session_state.get('get_bw', 0)) == 0:
                            st.toast("Web thickness is required(b_w)", icon="⚠️")
                        if abs(st.session_state.get('get_J', 0)) == 0:
                            st.toast("Moment of inertia in Girder alone is required(J)", icon="⚠️")
                        if abs(st.session_state.get('get_Qn', 0)) == 0:
                            st.toast("First moment of Area of Girder alone is required(Qn)", icon="⚠️")
                        if abs(st.session_state.get('get_effective', 0)) == 0:
                            st.toast("Section height is required(d)", icon="⚠️")
                        if Vrd_c == 0:
                            st.toast("Shear Resistance is required(Vrd_c)", icon="⚠️")
                    except:
                        if Vrd_c == 0:
                            st.toast("Shear Resistance is required(Vrd_c)", icon="⚠️")
                    calculate_results()
            else:
                if st.button("Calculate Fatigue Result →", use_container_width=True, type="primary", key="next_tab2_without_error"):
                    update_temp_from_input_multi(['Fatigue_method', 'fck', 'bw', 'J', 'd', 'Qn', 'get_bw', 'get_J', 'get_effective', 'get_Qn', 'VRd_c', 'get_effective_widget'])
                    calculate_results()
                    add_tab_switch_button("Next", tabs[2])

    def final_check():
        try:
            if st.session_state.get('is_ok') == "N/A" :
                return True
        except:
            return False


    # 두번째 탭 - Fatigue Result
    with tab3:
        if validation_errors2 and validation_errors or final_check():
            with st.container(border=False, height=800):
                calculate_results()
                st.error("Please complete all required fields before calculating fatigue result.")
                if abs(st.session_state.get('Vsdmax', 0)) == 0 and abs(st.session_state.get('Vsdmin', 0)) == 0:
                    st.error("Please enter maximum shear values. (Vsd,max)")
                if abs(st.session_state.get('bw', 0)) == 0:
                    st.error("Please enter web thickness. (b_w)")
                if abs(st.session_state.get('J', 0)) == 0:
                    st.error("Please enter moment of inertia in Girder alone. (J)")
                if abs(st.session_state.get('Qn', 0)) == 0:
                    st.error("Please enter first moment of Area of Girder alone. (Qn)")
                if abs(st.session_state.get('d', 0)) == 0:
                    st.error("Please enter section height. (d)")
                if abs(st.session_state.get('Vrd_c', 0)) == 0:
                    st.error("Please enter shear resistance. (Vrd_c)")
                # if st.session_state.get('is_ok') == "N/A":
                #     st.error("Calculation is needed. Please click the calculation button below.")
                #     if st.button("Calculate Fatigue Result", key="calculate_fatigue_result", use_container_width=True):
                #         calculate_results()
                #         st.rerun()
            # 네비게이션 및 저장 버튼
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("<- Back", key="back_to_fatigue_settings", use_container_width=True):
                    add_tab_switch_button("Back", tabs[1])
        else:              
            with st.container(border=True, height=800):
                if st.session_state.get('input_changed', False):
                    st.warning("🔄 Input values have been changed. Please recalculate to see updated results.")
                    if st.button("Fatigue Result Recalculate", key="calculate_fatigue_result", use_container_width=True):
                        calculate_results()
                        st.session_state.input_changed = False
                        st.rerun()
                # 결과 표시
                if all(k in st.session_state for k in ['Tmax', 'Tmin', 'TRd1', 'Tmax_TRd1', 'Tmin_TRd1']):
                    st.markdown("<h6><b>Concrete Shear Fatigue Design Result</b></h6>", unsafe_allow_html=True)
                    
                    # 계산된 값 가져오기
                    Vsdmax = abs(float(st.session_state.get('Vsdmax', 0)))
                    Vsdmin = abs(float(st.session_state.get('Vsdmin', 0)))
                    Qn = st.session_state.get('Qn', 0)
                    J = st.session_state.get('J', 0)
                    bw = st.session_state.get('bw', 0)
                    d = st.session_state.get('d', 0)
                    Vrd_c = st.session_state.get('Vrd_c', 0)
                    
                    # 전단 응력 값
                    Tmax = st.session_state.get('Tmax', 0)
                    Tmin = st.session_state.get('Tmin', 0)
                    TRd1 = st.session_state.get('TRd1', 0)
                    Tmax_TRd1 = st.session_state.get('Tmax_TRd1', 0)
                    Tmin_TRd1 = st.session_state.get('Tmin_TRd1', 0)
                    # 판정값 계산 (0.65 - Tmax_TRd1 또는 0.9 - Tmax_TRd1 중 작은 값)
                    discriminant = min(0.65 - Tmax_TRd1, 0.9 - Tmax_TRd1)
                    
                    # 판정값 저장
                    st.session_state.discriminant = discriminant
                    
                    # temp_result_df에도 저장
                    update_temp_from_input('discriminant')
                    # 판정 결과 표시
                    # 추가 조건 표시 - 가독성 개선
                    tau_min_tau_max = Tmin / Tmax if Tmax != 0 else 0
                    limit_value = 0.5 + 0.45 * abs(Tmin_TRd1)

                    with st.container(border=True, height=120):
                        st.latex(r"\frac{\tau_{max}}{\tau_{Rd1}} \leq 0.5 + 0.45 \left|\frac{\tau_{min}}{\tau_{Rd1}}\right| \leq 0.9")
                        # 최종 판정
                        if tau_min_tau_max >= 0:
                            if Tmax_TRd1 <= limit_value and limit_value <= 0.9:
                                st.latex(f"{Tmax_TRd1:.2f}" + r"\leq 0.5 + 0.45 \cdot |" + f"{Tmin_TRd1:.2f}| = {limit_value:.2f}"+ r"\leq 0.9  \therefore \text{OK}")
                            else:
                                st.latex(f"{Tmax_TRd1:.2f}" + r"\leq 0.5 + 0.45 \cdot |" + f"{Tmin_TRd1:.2f}| = {limit_value:.2f}"+ r"\leq 0.9  \therefore \text{NG}")
                        else:
                            limit_value = 0.5 - abs(Tmin_TRd1)
                            if Tmax_TRd1 <= limit_value:
                                st.latex(f"{Tmax_TRd1:.2f}" + r"\leq 0.5 - |" + f"{Tmin_TRd1:.2f}| = {limit_value:.2f}"+ r" \therefore \text{OK}")
                            else:
                                st.latex(f"{Tmax_TRd1:.2f}" + r"\leq 0.5 - |" + f"{Tmin_TRd1:.2f}| = {limit_value:.2f}"+ r" \therefore \text{NG}")
                    
                    # 상세 계산 결과 표시
                    st.markdown("<h6><b>Detail Calculation of Concrete Shear Fatigue Result</b></h6>", unsafe_allow_html=True)
                    
                    # 전단 응력 계산 - 공식 수정
                    st.write("Shear Stress Calculation")
                    with st.container(border=True, height=120):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(r"Maximum shear stress: $\tau_{max}$")
                            st.latex(r"\tau_{max} = \frac{V_{sd,max} \cdot Q_n}{J \cdot b_w} = " + f"{Tmax:.2f}{{ MPa}}")
                        with col2:
                            st.write(r"Minimum shear stress: $\tau_{min}$")
                            st.latex(r"\tau_{min} = \frac{V_{sd,min} \cdot Q_n}{J \cdot b_w} = " + f"{Tmin:.2f}{{ MPa}}")
                    
                    # 응력비 계산 - 공식 수정
                    st.write("Stress Ratio Calculation", unsafe_allow_html=True)
                    with st.container(border=True, height=120):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(r"Shear resistance stress:")
                            st.latex(r"\tau_{Rd1} = \frac{V_{Rd,c}}{b_w \cdot d} = " + f"{TRd1:.2f}{{ MPa}}")
                        with col2:
                            st.latex(r"\frac{\tau_{max}}{\tau_{Rd1}} = " + f"{Tmax_TRd1:.2f}")
                            st.latex(r"\frac{\tau_{min}}{\tau_{Rd1}} = " + f"{Tmin_TRd1:.2f}")
                    
                    # 검증 기준 - 가독성 개선
                        # 조건식 표시
                        # st.latex(r"\frac{\tau_{max}}{\tau_{Rd1}} = " + f"{Tmax_TRd1:.2f} " + 
                        #         (r"< 0.65" if Tmax_TRd1 < 0.65 else r"\geq 0.65") + 
                        #         (r"\;\; \therefore \text{OK}" if Tmax_TRd1 < 0.65 else r"\;\; \therefore \text{NG}"))
                        

                        
                        # 조건식 분리
                        # st.text("Minimum Condition Check")
                        # st.latex(r"\text{for } \frac{\tau_{min}}{\tau_{max}} \geq 0:")
                        # if tau_min_tau_max >= 0:
                        #     st.latex(f"{tau_min_tau_max:.2f}"+r" \geq 0 \therefore \text{OK}")
                        # else:
                        #     st.latex(f"{tau_min_tau_max:.2f}"+r" \leq 0 \therefore \text{NG}")
    #차트 -----------------------------------------------------------------------------------------------------------------------

                    # 검증 기준
                    st.write("Concrete Compression Fatigue Allowable Stress Region")

                    # 차트 그리기
                    fig, ax = plt.subplots(figsize=(8, 6))

                    # x축: τmin / τRd1 (-1부터 1까지)
                    x = np.linspace(-1, 1, 200)
                    
                    # 양수 영역 (τmin/τmax ≥ 0)
                    x_pos = np.linspace(0, 0.9, 100)
                    y_pos = 0.5 + 0.45 * x_pos
                    
                    # 음수 영역 (τmin/τmax < 0)
                    x_neg = np.linspace(-0.5, 0, 50)
                    y_neg = 0.5 - np.abs(x_neg)

                    # 허용 영역 그리기 - 양수 구간
                    ax.plot(x_pos, y_pos, label=r'$\frac{\tau_{max}}{\tau_{Rd1}} = 0.5 + 0.45 \cdot \left|\frac{\tau_{min}}{\tau_{Rd1}}\right|$ (for $\tau_{min}/\tau_{max} \geq 0$)', 
                            color='blue', linewidth=2)
                    
                    # 허용 영역 그리기 - 음수 구간
                    ax.plot(x_neg, y_neg, label=r'$\frac{\tau_{max}}{\tau_{Rd1}} = 0.5 - \left|\frac{\tau_{min}}{\tau_{Rd1}}\right|$ (for $\tau_{min}/\tau_{max} < 0$)', 
                            color='blue', linewidth=2)

                    # 상한선 (0.9) 그리기
                    ax.axhline(y=0.9, color='red', linestyle='--', linewidth=2, 
                            label=r'$\frac{\tau_{max}}{\tau_{Rd1}} = 0.9$ (Upper Limit)')
                    
                    # 하한선 (y = x 라인) - 양수 구간에서만
                    x_lower = np.linspace(0, 0.9, 100)
                    ax.plot(x_lower, x_lower, color='gray', linestyle='--', linewidth=1.5, 
                            label=r'$\frac{\tau_{max}}{\tau_{Rd1}} = \frac{\tau_{min}}{\tau_{Rd1}}$ (Lower Limit)')
                    
                    # x축 0선 그리기
                    ax.axvline(x=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.7)
                    
                    # 허용 영역 채우기 - 양수 구간 (x_lower와 y_pos 사이)
                    valid_mask_pos = y_pos <= 0.9
                    x_pos_valid = x_pos[valid_mask_pos]
                    y_pos_valid = y_pos[valid_mask_pos]
                    x_lower_valid = x_pos_valid  # 하한선도 같은 x 범위
                    ax.fill_between(x_pos_valid, x_lower_valid, y_pos_valid, color='lightgreen', alpha=0.3, label='Allowable Region')
                    
                    # 허용 영역 채우기 - 음수 구간 (0부터 y_neg까지)
                    ax.fill_between(x_neg, 0, y_neg, color='lightgreen', alpha=0.3)

                    # 현재 계산된 점 표시
                    current_tau_min_ratio = Tmin_TRd1 if tau_min_tau_max >= 0 else -abs(Tmin_TRd1)
                    
                    # 판정 로직
                    if tau_min_tau_max >= 0:
                        # 양수 영역
                        limit_value = 0.5 + 0.45 * abs(Tmin_TRd1)
                        is_ok = (Tmax_TRd1 <= limit_value) and (limit_value <= 0.9) and (Tmax_TRd1 >= Tmin_TRd1)
                    else:
                        # 음수 영역  
                        limit_value = 0.5 - abs(Tmin_TRd1)
                        is_ok = Tmax_TRd1 <= limit_value
                    
                    current_point_color = 'green' if is_ok else 'red'
                    current_point_marker = 'o' if is_ok else 'X'
                    point_size = 100 if current_point_marker == 'o' else 150

                    ax.scatter(current_tau_min_ratio, Tmax_TRd1, color=current_point_color, s=point_size, 
                            marker=current_point_marker, zorder=5,
                            label=f'Current Point ({current_tau_min_ratio:.3f}, {Tmax_TRd1:.3f})')

                    # 차트 설정
                    ax.set_xlim(-1, 1)
                    ax.set_ylim(0, 1.2)
                    ax.set_xlabel(r'$\frac{\tau_{min}}{\tau_{Rd1}}$', fontsize=12)
                    ax.set_ylabel(r'$\frac{\tau_{max}}{\tau_{Rd1}}$', fontsize=12)
                    ax.grid(True, alpha=0.3)
                    ax.legend(loc='upper left', fontsize=9)

                    # 축에 주요 눈금 표시
                    ax.set_xticks(np.arange(-1.0, 1.1, 0.2))
                    ax.set_yticks(np.arange(0, 1.3, 0.1))

                    # 텍스트 주석 추가
                    ax.text(0.5, 0.1, r'$\frac{\tau_{min}}{\tau_{max}} \geq 0$', 
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7),
                            fontsize=10, ha='center')
                    ax.text(-0.25, 0.1, r'$\frac{\tau_{min}}{\tau_{max}} < 0$', 
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7),
                            fontsize=10, ha='center')

                    # Streamlit에 표시
                    st.pyplot(fig)
 #차트 -----------------------------------------------------------------------------------------------------------------------



            # 네비게이션 및 저장 버튼
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("<- Back", key="back_to_fatigue_settings", use_container_width=True):
                    add_tab_switch_button("Back", tabs[1])
            
            with col3:
                button_text = "Update" if is_edit_mode else "Save Result"
                if st.button(button_text, key="save_fatigue_result", use_container_width=True, type="primary"):
                    # 계산 수행 (아직 수행되지 않은 경우)
                    if 'discriminant' not in st.session_state:
                        if not calculate_results():
                            st.error("Please perform the calculation first.")
                            
                            return
                    update_temp_from_input_multi(['scmax', 'scmin', 'import_option'])
                    update_temp_from_input_multi(['get_effective_widget','Fatigue_method', 'fck', 'bw', 'J', 'd', 'Qn', 'get_bw', 'get_J', 'get_effective', 'get_Qn', 'VRd_c', 'get_total_height', 'manual_shear_resistance', 'manual_input_properties'])
                    
                    # temp_result_df 업데이트
                    if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
                        # 케이스 정보 업데이트
                        st.session_state.temp_result_df.at[0, 'case_id'] = st.session_state.case_name
                        st.session_state.temp_result_df.at[0, 'case_method'] = "Concrete Shear(Not Require Reinforcement)"
                        
                        # 판정값 저장
                        st.session_state.temp_result_df.at[0, 'discriminant'] = st.session_state.discriminant
                        
                        # save_to_result_df 함수 사용하여 저장
                        if save_to_result_df():
                            st.success(f"'{st.session_state.case_name}' case saved.")
                            back_to_fatigue_case()
                        else:
                            st.error("Error saving data.")
                    else:
                        st.error("No data to save.")
    
    # # 디버깅 정보 표시 (옵션)
    # if st.sidebar.checkbox("Show Debug Info"):
    #     st.sidebar.subheader("Debug Session State")
    #     st.sidebar.write("Edit Mode:", is_edit_mode)
    #     st.sidebar.write("Case Name:", st.session_state.get('case_name', 'None'))
        
    #     # 중요 세션 변수들 출력
    #     debug_vars = {
    #         'case_name': st.session_state.get('case_name', 'Not set'),
    #         'Vsdmax': st.session_state.get('Vsdmax', 'Not set'),
    #         'Vsdmin': st.session_state.get('Vsdmin', 'Not set'),
    #         'Tmax': st.session_state.get('Tmax', 'Not calculated'),
    #         'Tmin': st.session_state.get('Tmin', 'Not calculated'),
    #         'TRd1': st.session_state.get('TRd1', 'Not calculated'),
    #         'discriminant': st.session_state.get('discriminant', 'Not calculated')
    #     }
    #     st.sidebar.write("Session Values:", debug_vars)
        
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
        
        # # Result DF 표시
        # if st.sidebar.checkbox("Show Result DF"):
        #     st.sidebar.subheader("Result DataFrame:")
        #     if 'result_df' in st.session_state:
        #         result_df = st.session_state.result_df
        #         if isinstance(result_df, pd.DataFrame):
        #             if result_df.empty:
        #                 st.sidebar.info("result_df is empty.")
        #             else:
        #                 st.sidebar.dataframe(result_df)
        #         else:
        #             st.sidebar.error(f"result_df's type is not DataFrame: {type(result_df)}")
        #     else:
        #         st.sidebar.warning("result_df is not in session state.")

'''이코드의 입력값들  
Concrete Shear (Not Require Reinforcement)  

1page (Fatigue Settings)  
- case_name  
- fck  
- Vsdmax  
- Vsdmin  

2page (Section Properties)  
- d  
- bw  
- Qn  
- J  
- Vrd_c  

3page (Fatigue Result)  
- (입력값 없음)  

자동 계산값  
- Tmax  
- Tmin  
- TRd1  
- Tmax_TRd1  
- Tmin_TRd1  
- discriminant  
- is_ok  
''' 