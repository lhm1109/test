# fatigue_concrete_simple_ui.py
#0611check
import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import math
from projects.concrete_fatigue_analysis_ntc2018.session_manager import *
import matplotlib.pyplot as plt
import numpy as np
import re
# 세션 초기화
initialize_session()
# 모달 다이얼로그 가져오기 
import_dialogs = SessionManager.initialize_import_dialogs() if 'SessionManager' in globals() else None
civil_stress_import = import_dialogs['simple_stress'] if import_dialogs else None

# PageManager 네비게이션 import
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from projects.concrete_fatigue_analysis_ntc2018.utils.navigator import back_to_fatigue_case

def calculate_results():

    
    fck = st.session_state.fck
    scmax = abs(st.session_state.scmax)
    scmin = abs(st.session_state.scmin)
    gamma_fat = st.session_state.factor_rcfat
    
    # 계산
    if fck == 0:
        fcd = 0.000000000000000000000000000000001
    else:
        fcd = fck / gamma_fat

    scmax_fcd = scmax / fcd
    scmin_fcd = scmin / fcd
    middle_value = 0.5 + 0.45 * scmin_fcd
    # 판정 (0.31 < 0.57 < 0.9 OK)
    discriminant = scmax_fcd <= middle_value and middle_value <= 0.9
    if discriminant:
        st.session_state.is_ok = "OK"

    else:
        st.session_state.is_ok = "NG"
    
    # 계산 결과 저장
    st.session_state.fcd = fcd
    st.session_state.scmax_fcd = scmax_fcd
    st.session_state.scmin_fcd = scmin_fcd

    
    # 결과 저장 - temp_result_df에도 저장
    update_temp_from_input_multi(['fck', 'fcd', 'scmax_fcd', 'scmin_fcd', 'is_ok'])
    
    return True
def fatigue_concrete_simple_ui_page():
    st.session_state.Fatigue_method = "Concrete Comp.(simple)"
    # 편집 모드 체크
    is_edit_mode = st.session_state.get('edit_mode', False)
    
    # 편집 모드일 경우 페이지 제목 변경
    if is_edit_mode:
        st.markdown(f"<h5><b>[Edit] Concrete Compression [Simplified Method] : {st.session_state.get('fatigue_case_name', '')}</b></h5>", unsafe_allow_html=True)
    else:
        st.markdown("<h5><b>Concrete Compression [Simplified Method]</b></h5>", unsafe_allow_html=True)
    
    # 탭 제목
    tabs = [
        "Fatigue Settings",
        "Fatigue Result"
    ]
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 0
    # 탭 생성
    tab1, tab2 = st.tabs(tabs)

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

            # fck 
            fck = st.number_input(
                r"Characteristic compressive strength of concrete, $f_{ck}$ (MPa)",
                min_value=0.0,  # 최소값 설정
                max_value=100.0,  # 최대값 설정
                value=float(st.session_state.get('fck', 20.0)),
                step=0.1,  # float 타입으로 step 설정
                format="%.1f",  # 포맷 설정
                key="fck_widget",
                on_change=update_temp_from_input,
                args=("fck_widget", "fck")
            )
            
            # γfat - 이미 설정된 값 사용
            gamma_fat = st.session_state.get('factor_rcfat', 1.5)
            st.success(f"Partial factor for fatigue of concrete, γfat = {gamma_fat}")
            
            # fcd 계산
            fcd = fck / gamma_fat
            st.session_state.fcd = fcd
            update_temp_from_input_multi(['fcd'])
            st.success(f"Design compressive strength of concrete, fcd = fck/γfat = {fck:.1f}/{gamma_fat:.1f} = {fcd:.1f} MPa")

            st.markdown("<h6><b>Fatigue Load</b></h6>", unsafe_allow_html=True)
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
                            disabled=not use_midas):
                        if civil_stress_import:
                            civil_stress_import("Import")
                            
                with col2:
                    # σc max
                    scmax = st.number_input(r"$\sigma_{c,max}$ (MPa)", 
                                value=float(st.session_state.get('scmax', 4.1)),
                                step=0.1, 
                                key="widget_scmax",
                                on_change=update_temp_from_input,
                                args=("widget_scmax", "scmax"),
                                disabled=use_midas)


                with col3:
                    # σc min
                    st.number_input(r"$\sigma_{c,min}$ (MPa)", 
                                value=float(st.session_state.get('scmin', 2.2)),
                                step=0.1, 
                                key="widget_scmin",
                                on_change=update_temp_from_input,
                                args=("widget_scmin", "scmin"),
                                disabled=use_midas)
                    # 직접 입력 시 세션 상태 업데이트
                    if not use_midas and 'widget_scmin' in st.session_state:
                        st.session_state.scmin = st.session_state.widget_scmin                
            update_temp_from_input_multi(['scmax', 'scmin', 'fck', 'import_option'])


            # 직접 입력 시 세션 상태 업데이트
            if not use_midas and 'widget_scmax' in st.session_state:
                st.session_state.scmax = st.session_state.widget_scmax
            # 네비게이션 및 저장 버튼
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- back", use_container_width=True):
                back_to_fatigue_case()

        with col3:
            case_name = st.session_state.get('case_name', '')
            is_duplicate = False
            # 수정 모드가 아닐 때만 중복 체크
            if not st.session_state.get('edit_mode', False):
                if 'result_df' in st.session_state and not st.session_state.result_df.empty and 'case_id' in st.session_state.result_df.columns:
                    if case_name in st.session_state.result_df['case_id'].values:
                        is_duplicate = True
                        st.toast(f"Case '{case_name}' already exists. Please use a different name.")
                        
            # 유효성 검사 실패 여부 확인 함수
            def has_validation_errors():
                # 필수 입력값 체크
                if abs(st.session_state.get('scmin', 0)) == 0 and abs(st.session_state.get('scmax', 0)) == 0:
                    return True
                if abs(st.session_state.get('scmin', 0)) > abs(st.session_state.get('scmax', 0)) :
                    return True
                if abs(st.session_state.get('scmax', 0)) <= 0:
                    return True
                if abs(st.session_state.get('fck', 50)) == 0:
                    return True
                return False
            # 중복일 경우 또는 유효성 검사 실패 시 Next 버튼 비활성화
            validation_errors = has_validation_errors()
            if validation_errors:
                # 버튼 먼저!
                if st.button("Next →", use_container_width=True, key="next_button_with_error"):
                    if abs(st.session_state.get('scmax', 0)) == 0:
                        st.toast("Please select fatigue stress values(scmax).")
                    if abs(st.session_state.get('scmin', 0)) > abs(st.session_state.get('scmax', 0)) :
                        st.toast("scmin must be less than scmax.")
                    if abs(st.session_state.get('fck', 0)) == 0:
                        st.toast("Enter fck value(fck).")
                    calculate_results()    
                
            else:
                if st.button("Calculate Fatigue Result →", use_container_width=True, type="primary",key="next_button_without_error"):
                    add_tab_switch_button("Next", tabs[1])
    def final_check():
        try:
            if st.session_state.get('is_ok') == "N/A" :
                return True
        except:
            return False


    # 두번째 탭 - Fatigue Result
    with tab2:
        if not validation_errors or not final_check():
            calculate_results()
            with st.container(border=True, height=800):
                if st.session_state.get('input_changed', False):
                    st.warning("🔄 Input values have been changed. Please recalculate to see updated results.")
                    if st.button("Fatigue Result Recalculate", key="calculate_fatigue_result", use_container_width=True):
                        calculate_results()
                        st.session_state.input_changed = False
                        st.rerun()
                else:
                    if 'fcd' in st.session_state and 'scmax' in st.session_state and 'scmin' in st.session_state:
                        st.markdown("<h6><b>Concrete Compression Fatigue Result (Simplified Method)</b></h6>", unsafe_allow_html=True)
                        calculate_results()
                        
                        # 계산된 값 가져오기
                        gamma_fat = st.session_state.get('factor_rcfat', 1.5)
                        fcd = st.session_state.get('fcd', 20.0)
                                
                        # 스트레스 값은 세션에서 가져온 다음 절대값으로 변환
                        scmax_raw = st.session_state.get('scmax', -4.1)  # 원래 음수값
                        scmin_raw = st.session_state.get('scmin', -2.2)  # 원래 음수값
                        
                        # 절대값으로 변환하여 계산에 사용
                        scmax = abs(scmax_raw)
                        scmin = abs(scmin_raw)
                        scmax_fcd = scmax / fcd
                        scmin_fcd = scmin / fcd
                        
                        # 중간값 계산 (0.5 + 0.45 * (scmin/fcd))
                        middle_value = 0.5 + 0.45 * scmin_fcd
                        
                        # 판정 결과 표시 (조건: scmax_fcd ≤ 0.5 + 0.45 * scmin_fcd ≤ 0.9)
                        with st.container(border=True, height=110):
                            st.latex(
                                r"\frac{\sigma_{c,max}}{f_{cd}} \leq 0.5 + 0.45 \frac{\sigma_{c,min}}{f_{cd}} \leq 0.9"
                            )
                            st.latex(
                                f"{scmax_fcd:.2f} " + 
                                (r"\leq" if scmax_fcd <= middle_value else r">") + 
                                f" {middle_value:.2f} " +
                                (r"\leq" if middle_value <= 0.9 else r">") +
                                " 0.9" +
                                (r"\;\; \therefore \text{OK}" if scmax_fcd <= middle_value and middle_value <= 0.9 else r"\;\; \therefore \text{NG}")
                            )
                        
                        # 상세 계산 결과 표시 계산결과
                        st.markdown("<h6><b>Detail Calculation of Concrete Compression Fatigue Result (Simplified Method)</b></h6>", unsafe_allow_html=True)        
                        
                        # 설계 강도 계산
                        st.write("Design Strength Calculation")
                        with st.container(border=True, height=80):
                            st.latex(r"f_{cd} = \frac{f_{ck}}{\gamma_{fat}} = \frac{" + f"{fck:.1f}" + "}{" + f"{gamma_fat:.1f}" + "} = " + f"{fcd:.1f}{{ MPa}}")
                        
                        # 응력비 계산
                        st.write("Stress Ratio Calculation")
                        with st.container(border=True, height=80):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.latex(r"\frac{\sigma_{c,max}}{f_{cd}} = \frac{" + f"{scmax:.1f}" + "}{" + f"{fcd:.1f}" + "} = " + f"{scmax_fcd:.2f}")
                            with col2:
                                st.latex(r"\frac{\sigma_{c,min}}{f_{cd}} = \frac{" + f"{scmin:.1f}" + "}{" + f"{fcd:.1f}" + "} = " + f"{scmin_fcd:.2f}")
                        
                        # 중간값 계산
                        st.write("Middle Value Calculation")
                        with st.container(border=True, height=80):
                            st.latex(r"0.5 + 0.45 \cdot \frac{\sigma_{c,min}}{f_{cd}} = 0.5 + 0.45 \cdot " + f"{scmin_fcd:.2f}" + r" = " + f"{middle_value:.2f}")
                        #차트 -----------------------------------------------------------------------------------------------------------------------

                        # 검증 기준
                        st.write("Concrete Compression Fatigue Allowable Stress Region")
                        # 차트 그리기
                        fig, ax = plt.subplots(figsize=(8, 6))

                        # x축: σc,min / fcd (0부터 0.9까지)
                        x = np.linspace(0, 0.9, 100)
                        # y축: σc,max / fcd = 0.5 + 0.45 * (σc,min / fcd)
                        y = 0.5 + 0.45 * x

                        # 허용 영역 그리기
                        ax.plot(x, y, label=r'$\frac{\sigma_{c,\max}}{f_{cd}} = 0.5 + 0.45 \cdot \frac{\sigma_{c,\min}}{f_{cd}}$', 
                                color='blue', linewidth=2)


                        # 상한선 (0.9) 그리기
                        ax.axhline(y=0.9, color='red', linestyle='--', linewidth=2, 
                                label=r'$\frac{\sigma_{c,\max}}{f_{cd}} = 0.9$ (Upper Limit)')
                        ax.plot(x, x, color='gray', linestyle='--', linewidth=1.5, label=r'$\frac{\sigma_{c,\max}}{f_{cd}} = \frac{\sigma_{c,\min}}{f_{cd}}$ (Lower Limit)')
                        ax.fill_between(x, x, y, color='lightblue', alpha=0.3, label='Allowable Region')
                        # 현재 계산된 점 표시
                        current_point_color = 'green' if (scmax_fcd <= middle_value and middle_value <= 0.9) else 'red'
                        current_point_marker = 'o' if (scmax_fcd <= middle_value and middle_value <= 0.9) else 'X'
                        point_size = 100 if current_point_marker == 'o' else 150

                        ax.scatter(scmin_fcd, scmax_fcd, color=current_point_color, s=point_size, 
                                marker=current_point_marker, zorder=5,
                                label=f'Current Point ({scmin_fcd:.2f}, {scmax_fcd:.2f})')

                        # 차트 설정
                        ax.set_xlim(0, 0.9)
                        ax.set_ylim(0, 1.0)
                        ax.set_xlabel(r'$\frac{\sigma_{c,\min}}{f_{cd}}$', fontsize=12)
                        ax.set_ylabel(r'$\frac{\sigma_{c,\max}}{f_{cd}}$', fontsize=12)
                        # ax.set_title('Concrete Compression Fatigue Allowable Stress Region', 
                        #             fontsize=12, fontweight='light')
                        ax.grid(True, alpha=0.3)
                        ax.legend(loc='upper left', fontsize=10)

                        # 축에 주요 눈금 표시
                        ax.set_xticks(np.arange(0, 1.0, 0.1))
                        ax.set_yticks(np.arange(0, 1.1, 0.1))

                        # Streamlit에 표시
                        st.pyplot(fig)

            # 네비게이션 및 저장 버튼
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("<- Back", key="back_to_fatigue_settings", use_container_width=True):
                    add_tab_switch_button("Back", tabs[0])
            
            with col3:
                button_text = "Update" if is_edit_mode else "Save Result"
                if st.button(button_text, key="save_fatigue_result", use_container_width=True, type="primary"):
                    # 계산 수행 (아직 수행되지 않은 경우)
                    if 'is_ok' not in st.session_state:
                        if not calculate_results():
                            st.toast("Please calculate")
                            return
                    update_temp_from_input_multi(['scmax', 'scmin', 'fck', 'import_option'])
                    # temp_result_df 업데이트
                    if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
                        # 케이스 정보 업데이트
                        st.session_state.temp_result_df.at[0, 'case_id'] = st.session_state.case_name
                        st.session_state.temp_result_df.at[0, 'case_method'] = "Concrete Comp.(simple)"
                        
                        # 판정값 저장
                        # st.session_state.temp_result_df.at[0, 'discriminant'] = st.session_state.discriminant
                        st.session_state.temp_result_df.at[0, 'is_ok'] = st.session_state.is_ok
                        # save_to_result_df 함수 사용하여 저장
                        if save_to_result_df():
                            st.success(f"'{st.session_state.case_name}' case has been saved.")
                            back_to_fatigue_case()
                        else:
                            st.toast("Error occurred while saving.")
                    else:
                        st.toast("No data to save.")
        else:
            with st.container(height=800, border=False):
                st.error("Input values are not valid. Please check your input again.")
                if abs(st.session_state.get('scmin', 0)) == 0 and abs(st.session_state.get('scmax', 0)) == 0:
                    st.error("Please enter fatigue stress values(scmin, scmax).")
                if abs(st.session_state.get('fck', 0)) == 0:
                    st.error("Please enter Concrete strength value(fck).")
                if not validation_errors :
                    if st.session_state.get('is_ok') == "N/A":
                        st.error("Calculation is needed. Please click the calculation button below.")
                        if st.button("Calculate Fatigue Result", key="calculate_fatigue_result", use_container_width=True):
                            calculate_results()
                            st.rerun()



            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("<- Back", key="back_to_fatigue_settings3", use_container_width=True):
                    add_tab_switch_button("Back", tabs[0])

''' 이코드의 입력값들
이코드의 입력값들  
Concrete Compression [Simplified Method]  

1page (Fatigue Settings)  
- case_name  
- fck  
- scmax  
- scmin  

2page (Fatigue Result)  
- (입력값 없음)  

자동 계산값  
- gamma_fat  
- fcd  
- scmax_fcd  
- scmin_fcd  
- middle_value  
- is_ok  
''' 