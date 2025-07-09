# fatigue_concrete_desm_rail_ui.py
import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
from projects.concrete_fatigue_analysis_ntc2018.session_manager import *
from streamlit_extras.switch_page_button import switch_page
from projects.concrete_fatigue_analysis_ntc2018.calc.fatigue_concrete_desm_rail_design import *
import re

# PageManager 네비게이션 import
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from projects.concrete_fatigue_analysis_ntc2018.utils.navigator import back_to_fatigue_case

# 세션 초기화 - 여기서 초기값들이 설정됨

# 모달 다이얼로그 가져오기
import_dialogs = SessionManager.initialize_import_dialogs()
civil_stress_import = import_dialogs['regular_stress']
civil_stress_import2 = import_dialogs['moving_stress']



def fatigue_concrete_desm_rail_ui_page():
    initialize_session()
    def save_fatigue_case():
        """피로 케이스 저장 함수"""
        case_id = st.session_state.get('case_name', 'New Case')
        if 'next_error' not in st.session_state:
            st.session_state.next_error = False
        # 수정 모드가 아닐 때만 중복 체크
        if not hasattr(st.session_state, 'edit_mode') or not st.session_state.edit_mode:
            if not st.session_state.result_df.empty and 'case_id' in st.session_state.result_df.columns and case_id in st.session_state.result_df['case_id'].values:
                st.error(f"'{case_id}' 케이스가 이미 존재합니다. 다른 이름을 사용해주세요.")
                return False
        
        # 필수 값 체크
        required_fields = ['fcm', 'scmax71', 'scperm']
        if not all(k in st.session_state for k in required_fields):
            st.error("필수 입력값이 누락되었습니다. 모든 필드를 입력해주세요.")
            return False
        
        # temp_result_df 데이터 업데이트
        if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
            # 현재 케이스 데이터 업데이트
            st.session_state.temp_result_df.at[0, 'case_id'] = case_id
            st.session_state.temp_result_df.at[0, 'case_method'] = "Concrete Comp.(Rail_DES)"
            
            # 판정값 저장 (있는 경우에만)
            if 'discriminant_rail_des' in st.session_state:
                st.session_state.temp_result_df.at[0, 'discriminant_rail_des'] = st.session_state.discriminant_rail_des
            
            # 수정 모드일 경우 기존 데이터 삭제
            if hasattr(st.session_state, 'edit_mode') and st.session_state.edit_mode:
                st.session_state.result_df = st.session_state.result_df[
                    st.session_state.result_df['case_id'] != case_id
                ]
            
            # 새로운 데이터 저장
            result_df = pd.concat([st.session_state.result_df, st.session_state.temp_result_df])
            st.session_state.result_df = result_df
            
            # 수정 모드 해제
            if hasattr(st.session_state, 'edit_mode'):
                del st.session_state.edit_mode
            
            # 성공 메시지
            st.success(f"'{case_id}' 케이스가 저장되었습니다.")
            back_to_fatigue_case()
            return True
        
        return False
    
    # 편집 모드 체크
    is_edit_mode = st.session_state.get('edit_mode', False)
    
    # 편집 모드일 경우 페이지 제목 변경
    if is_edit_mode:
        st.markdown(f"<h5><b>[Edit] Concrete Compression(DESM) : Railway :{st.session_state.get('fatigue_case_name', '')}</b></h5>", unsafe_allow_html=True)
    else:
        st.markdown("<h5><b>Concrete Compression(DESM) : Railway</b></h5>", unsafe_allow_html=True)
    
    # 탭 제목
    tabs = [
        "Fatigue Settings",
        "Fatigue Parameters",
        "Correction Factor",
        "Fatigue Result",
    ]

    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(tabs)

# 각 탭 내부
    # 첫번째 탭 Fatigue Settings
    with tab1:
        with st.container(height=800, border=False):
            st.markdown("<h5>Fatigue Settings</h5>", unsafe_allow_html=True)
            
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
            

            col1, col2 = st.columns(2)
            with col1:
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
                #유효성검사 fck
                if st.session_state.get('fck', 0) <= 0:
                    st.toast(r"$f_{ck}$ must be greater than 0.", icon="⚠️")
                    st.session_state.next_error = True
                else:
                    st.session_state.next_error = False

                st.session_state['fcm'] = fck
                fcm = st.session_state.fcm
                update_temp_from_input_multi(['fcm'])
                cal_for_rail_desm.update_fcm_and_calculate_fcd()
            with col2:
                st.number_input(r"Span length (m), $L$", 
                                    key='span_length', 
                                    on_change=update_temp_from_input, 
                                    args=('span_length',))
                if st.session_state.get('span_length', 0) <= 0:
                    st.toast(r"$L$ must be greater than 0.", icon="⚠️")
                    st.session_state.next_error = True
                else:
                    st.session_state.next_error = False


            st.markdown("<h5><b>Fatigue Load</b></h5>", unsafe_allow_html=True)
        #하중불러오기
            use_midas = st.toggle("Import From Midas NX",
                                  value=st.session_state.get('import_option', True), 
                                  key="manual_input", 
                                  on_change=update_temp_from_input,
                                  args=("widget_import_option", "import_option")
                                  )
            if st.session_state.manual_input:
                pass
            
            else: 
                if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
                    st.session_state.temp_result_df.at[0, 'element_number_scmax71'] = "User Defined"



            with st.container(border=True):
                col1, col2, col3 = st.columns(3, vertical_alignment="bottom")
                with col1:
                    if st.button("Import", use_container_width=True, key="from_midas_nx", 
                                disabled=not st.session_state.manual_input):
                        civil_stress_import("Import")
                
                with col2:
                    st.number_input(r"$\sigma_{c,max,71}$", 
                                value=float(st.session_state.scmax71),
                                step=0.5, 
                                key="widget_scmax71",
                                on_change=update_temp_from_input,
                                args=("widget_scmax71", "scmax71"),
                                disabled=st.session_state.manual_input,
                                help="The maximum compression stress is calculated.",
                                placeholder="Import from Midas" if st.session_state.manual_input else None)
                    #유효성검사 scmax71
                    if st.session_state.get('scmax71', 0) == 0:
                        st.toast(r"$\sigma_{c,max,71}$ must be greater than 0.", icon="⚠️")
                        st.session_state.next_error = True
                    else:
                        st.session_state.next_error = False


                with col3:
                    st.number_input(r"$\sigma_{c,perm}$", 
                                value=float(st.session_state.scperm), 
                                step=0.05, 
                                key="widget_scperm",
                                on_change=update_temp_from_input,
                                args=("widget_scperm", "scperm"),
                                help="The maximum compressive tension stress is calculated.",
                                disabled=st.session_state.manual_input)

                st.markdown("<small><i>note) The dynamic factor Φ is not applied in this review. If necessary, it should be applied to the modeling load factor.</i></small>", unsafe_allow_html=True)


        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- back", use_container_width=True):
                back_to_fatigue_case()
        with col3:
            # 유효성 검사 실패 여부 확인 함수
            def has_validation_errors():
                # 필수 입력값 체크
                if st.session_state.get('fck', 0) <= 0:
                    return True
                if abs(st.session_state.get('fcm', 0)) == 0:
                    return True
                if abs(st.session_state.get('span_length', 0)) == 0:
                    return True
                if abs(st.session_state.get('scmax71', 0)) == 0:
                    return True
                if abs(st.session_state.get('scperm', 0)) == 0:
                    return True
                return False

            # 유효성 검사 실패 시 Next 버튼 비활성화
            validation_errors = has_validation_errors()
            if  validation_errors:
                if st.button("Next →", use_container_width=True, key="next_button_with_error"):
                    if abs(st.session_state.get('fcm', 0)) == 0:
                        st.toast("Please enter fcm value ($f_{cm}$).", icon="⚠️")
                    if abs(st.session_state.get('span_length', 0)) == 0:
                        st.toast("Please enter span length ($L$).", icon="⚠️")
                    if abs(st.session_state.get('scmax71', 0)) == 0:
                        st.toast("Please enter scmax71 value ($\\sigma_{c,max,71}$).", icon="⚠️")
                    if abs(st.session_state.get('scperm', 0)) == 0:
                        st.toast("Please enter scperm value ($\\sigma_{c,perm}$).", icon="⚠️")
            else:
                if st.button("Next →", use_container_width=True, type="primary", key="next_button_without_error"):
                    update_temp_from_input_multi(['case_name', 'design_factor', 'stress', 'fcm', 'fck', 'scmax71', 'scperm', 'import_option'])
                    add_tab_switch_button("Next", tabs[1])
    def fatigue_tab(method, back_tab, next_tab=None):
        col1,col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back", key=f"back_{method}",use_container_width=True):
                add_tab_switch_button("Back", back_tab)
        with col2:
            pass
        with col3:
            if next_tab != None:
                if next_tab and st.button("Next →", key=f"next_{method}", use_container_width=True):
                    add_tab_switch_button("Next", next_tab)
            else:
                button_text = "Update" if st.session_state.get('edit_mode', False) else "Save Result"
                if st.button(button_text, key=f"save_result_22",use_container_width=True, type="primary"):
                    update_temp_from_input_multi(['case_name', 'design_factor', 'stress', 'fcm', 'fck', 'scmax71', 'scperm', 'import_option'])
                    update_temp_from_input_multi([
                        'vol', 'nc', 'tt', 'sp', 'az'
                    ])
                    update_temp_from_input_multi(['ds1', 'ds12', 
                        'widget_lambda0', 'widget_lambda1', 'widget_lambda2', 'widget_lambda3',
                        'widget_lambda4', 'widget_lambdac', 'widget_ds1', 'widget_ds12'
                    ])
                    save_fatigue_case() 
# 첫페이지 끝
    with tab2:
        with st.container(height=800, border=False):
            st.markdown("<h5>Fatigue Parameters</h5>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
            
                st.number_input(
                    r"Tons of weight trains passing per year per track), $Vol$", 
                    min_value=0.0, 
                    value=float(st.session_state.vol), 
                    step=0.5, 
                    key="widget_vol",
                    on_change=update_temp_from_input,
                    args=("widget_vol", "vol")
                )
                
                st.number_input(
                    r"Number of Train, $N_{c}$", 
                    min_value=0, 
                    value=int(st.session_state.nc), 
                    step=1, 
                    key="widget_nc",
                    on_change=update_temp_from_input,
                    args=("widget_nc", "nc")
                )
                st.selectbox(
                    "Traffic Type",
                    ("Standard traffic", "Heavy traffic"),
                    index=["Standard traffic", "Heavy traffic"].index(st.session_state.tt),
                    key="widget_tt",
                    on_change=update_temp_from_input,
                    args=("widget_tt", "tt")
                )
                # st.markdown("<br>", unsafe_allow_html=True)    
            with col2:
                st.selectbox(
                    "Support Type",
                    ("Simply Supported Beams", "Continuous Beams (mid span)", "Continuous Beams (end span)", "Continuous Beams (intermediate support area)"),
                    index=["Simply Supported Beams", "Continuous Beams (mid span)", "Continuous Beams (end span)", "Continuous Beams (intermediate support area)"].index(st.session_state.sp),
                    key="widget_sp",
                    on_change=update_temp_from_input,
                    args=("widget_sp", "sp")
                ) 
                
                st.selectbox(
                    "Analysis Zone",
                    ("Compression zone", "Precompressed tensile zone"),
                    index=["Compression zone", "Precompressed tensile zone"].index(st.session_state.az),
                    key="widget_az",
                    on_change=update_temp_from_input,
                    args=("widget_az", "az")
                )
            
            
        # 유효성 검사 실패 여부 확인 함수
        def has_validation_errors1():
            # 필수 입력값 체크
            if abs(st.session_state.get('vol', 0)) == 0:
                return True
            if abs(st.session_state.get('nc', 0)) == 0:
                return True
            return False

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- Back", use_container_width=True, key="fatigue_load_back"):
                add_tab_switch_button("Back", tabs[0])

        with col3:
            # 중복일 경우 또는 유효성 검사 실패 시 Next 버튼 비활성화  
            validation_errors1 = has_validation_errors1()
            if validation_errors1:
                if st.button("Next →", use_container_width=True, key="next_button_with_error1"):
                    if abs(st.session_state.get('vol', 0)) == 0:
                        st.toast(r"Please enter value ($Vol$)", icon="⚠️")
                    if abs(st.session_state.get('nc', 0)) == 0:
                        st.toast(r"Please enter value ($N_c$)", icon="⚠️")
            else:
                if st.button("Next →", key="save_result_load", use_container_width=True, type="primary"):
                    update_temp_from_input_multi([
                        'vol', 'nc', 'tt', 'sp', 'az'
                    ])
                    add_tab_switch_button("Next", tabs[2])

    with tab3:
        with st.container(height=800, border=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h5><b>Correction Factor</b></h5>", unsafe_allow_html=True)
            with col2:
                st.toggle(
                    "Correction Factor Auto Calculate", 
                    key="correction_factor_auto_calculate", 
                    value=True, 
                    on_change=update_temp_from_input, 
                    args=("correction_factor_auto_calculate",)
                )
        

            if st.session_state.correction_factor_auto_calculate:
                with st.container(border=True, ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("<h6>Moving load(for correction factor)</h6>", unsafe_allow_html=True, help="Stress ranges due to Load Model 71 on one (∆σ₁, ∆σ₂) or two tracks (∆σ₁₊₂)")
                    with col2:
                        st.toggle(
                            "Load From Midas Model", 
                            key="manual_input_correction", 
                            value=True, 
                        )


                    col1, col2, col3 = st.columns(3,vertical_alignment="bottom")
                    with col1:
                        #하중2 모달불러오기
                        if st.button("Import", use_container_width=True, key="for_midas_nx_correction", disabled=not st.session_state.manual_input_correction):
                            civil_stress_import2("Import")

                    with col2:
                        #civil max output 무빙 1트랙 압축
                        st.number_input(
                            r"$\Delta\sigma_{1}$", 
                            value=float(st.session_state.ds1), 
                            step=0.5, 
                            key="widget_ds1",
                            on_change=update_temp_from_input,
                            args=("widget_ds1", "ds1"),
                            disabled=st.session_state.manual_input_correction
                        )
                    with col3:
                        #civil max output 무빙 2트랙 압축
                        st.number_input(
                            r"$\Delta\sigma_{1+2}$", 
                            value=float(st.session_state.ds12), 
                            step=0.05, 
                            key="widget_ds12",
                            on_change=update_temp_from_input,
                            args=("widget_ds12", "ds12"),
                            disabled=st.session_state.manual_input_correction
                        )
                    # print(f"ds1: {st.session_state.ds1}")
                    # print(f"ds12: {st.session_state.ds12}")

            #correction factor 계산버튼
            if st.button("Correction Factor Calculate", use_container_width=True,
                    disabled=not st.session_state.correction_factor_auto_calculate):
                # 계산 함수 호출
                cal_for_rail_desm.calculate_all_lambdas_concrete_rail()
            col1, col2 = st.columns(2)
            with col1:
                # SessionManager 클래스의 get_lambda_value 함수 사용 람다계산
                # lambda0
                st.number_input(
                    r"$\lambda_{c0}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('calc_lambda0', 0.0)),  # 계산된 값 참조
                    step=0.05, 
                    key="widget_lambda0",  # 위젯 키는 widget_으로 시작
                    on_change=update_temp_from_input,
                    args=("widget_lambda0", "lambda0"),  # temp_result_df에는 lambda0로 저장
                    disabled=st.session_state.correction_factor_auto_calculate
                )
                

                
                st.number_input(
                    r"$\lambda_{c2}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('calc_lambda2', 0.0)),  # 계산된 값 참조
                    step=0.05, 
                    key="widget_lambda2",
                    on_change=update_temp_from_input,
                    args=("widget_lambda2", "lambda2"),
                    disabled=st.session_state.correction_factor_auto_calculate
                )
                st.number_input(
                    r"$\lambda_{c4}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('calc_lambda4', 0.0)),  # float 타입으로 명시적 변환
                    step=0.05, 
                    key="widget_lambda4",
                    on_change=update_temp_from_input,
                    args=("widget_lambda4","lambda4"),
                    disabled=st.session_state.correction_factor_auto_calculate
                )
            with col2:
                
                # st.markdown("&nbsp;", unsafe_allow_html=True)
                # st.markdown("<br>", unsafe_allow_html=True) 
                st.number_input(
                    r"$\lambda_{c1}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('calc_lambda1', 0.0)),  # 계산된 값 참조
                    step=0.05, 
                    key="widget_lambda1",
                    on_change=update_temp_from_input,
                    args=("widget_lambda1","lambda1"),
                    disabled=st.session_state.correction_factor_auto_calculate
                )
                st.number_input(
                    r"$\lambda_{c3}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('calc_lambda3', 0.0)),  # 계산된 값 참조
                    step=0.05,
                    key="widget_lambda3",
                    on_change=update_temp_from_input,
                    args=("widget_lambda3","lambda3"),
                    disabled=st.session_state.correction_factor_auto_calculate
                )
                if st.session_state.get("correction_factor_auto_calculate", False):
                    st.session_state.setdefault("calc_lambdac", 1.12)
                else:
                    st.session_state["calc_lambdac"] = (
                        st.session_state.get('widget_lambda1', 1.12) *
                        st.session_state.get('widget_lambda2', 0.54) *
                        st.session_state.get('widget_lambda3', 0.93) *
                        st.session_state.get('widget_lambda0', 1.08)
                    )
                st.number_input(
                    r"$\lambda_{c}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('calc_lambdac', 1.0)),
                    step=0.05,
                    key="widget_lambdac",
                    on_change=update_temp_from_input,
                    args=("widget_lambdac","calc_lambdac"),
                    disabled=True  # 계산값이므로 항상 비활성화
                )
                st.session_state.lambdac = st.session_state.get('calc_lambdac', 1.0)


 
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- Back", use_container_width=True, key="fatigue_correction_back"):
                add_tab_switch_button("Back", tabs[1])

        with col3:
            # 유효성 검사
            def has_validation_errors2():
                if st.session_state.correction_factor_auto_calculate == True:
                    if abs(st.session_state.get('ds1', 0)) == 0:
                        return True
                    if abs(st.session_state.get('ds12', 0)) == 0:
                        return True
                    if abs(st.session_state.get('widget_lambda0', 0)) == 0:
                        return True
                    if abs(st.session_state.get('widget_lambda1', 0)) == 0:
                        return True
                    if abs(st.session_state.get('widget_lambda2', 0)) == 0:
                        return True
                    if abs(st.session_state.get('widget_lambda3', 0)) == 0:
                        return True
                    if abs(st.session_state.get('widget_lambda4', 0)) == 0:
                        return True
                else:
                    if abs(st.session_state.get('widget_lambda0', 0)) == 0:
                        return True
                    if abs(st.session_state.get('widget_lambda1', 0)) == 0:
                        return True
                    if abs(st.session_state.get('widget_lambda2', 0)) == 0:
                        return True
                    if abs(st.session_state.get('widget_lambda3', 0)) == 0:
                        return True
                    if abs(st.session_state.get('widget_lambda4', 0)) == 0:
                        return True
                return False

            if st.session_state.correction_factor_auto_calculate == True:
                validation_errors2 = has_validation_errors2()
            else:   
                validation_errors2 = has_validation_errors2()

            if validation_errors2:
                if st.button("Next →", use_container_width=True, key="next_button_with_error2"):
                    if st.session_state.correction_factor_auto_calculate == True:
                        if abs(st.session_state.get('ds1', 0)) == 0:
                            st.toast(r"Please enter value ($\Delta\sigma_1$)")
                        if abs(st.session_state.get('ds12', 0)) == 0:
                            st.toast(r"Please enter value ($\Delta\sigma_{1+2}$)")
                        if abs(st.session_state.get('widget_lambda0', 0)) == 0:
                            st.toast(r"Please enter value ($\lambda_{c0}$)")
                        if abs(st.session_state.get('widget_lambda1', 0)) == 0:
                            st.toast(r"Please enter value ($\lambda_{c1}$)")
                        if abs(st.session_state.get('widget_lambda2', 0)) == 0:
                            st.toast(r"Please enter value ($\lambda_{c2}$)")
                        if abs(st.session_state.get('widget_lambda3', 0)) == 0:
                            st.toast(r"Please enter value ($\lambda_{c3}$)")
                        if abs(st.session_state.get('widget_lambda4', 0)) == 0:
                            st.toast(r"Please enter value ($\lambda_{c4}$)")
                    else:
                        if abs(st.session_state.get('widget_lambda0', 0)) == 0:
                            st.toast(r"Please enter value ($\lambda_{c0}$)")
                        if abs(st.session_state.get('widget_lambda1', 0)) == 0:
                            st.toast(r"Please enter value ($\lambda_{c1}$)")
                        if abs(st.session_state.get('widget_lambda2', 0)) == 0:
                            st.toast(r"Please enter value ($\lambda_{c2}$)")
                        if abs(st.session_state.get('widget_lambda3', 0)) == 0:
                            st.toast(r"Please enter value ($\lambda_{c3}$)")
                        if abs(st.session_state.get('widget_lambda4', 0)) == 0:
                            st.toast(r"Please enter value ($\lambda_{c4}$)")     
            else:
                if st.button("Calculate Fatigue Result  →", key="next_button", use_container_width=True, type="primary"):
                    add_tab_switch_button("Next", tabs[3])
                    cal_for_rail_desm.calculate_all_lambdas_concrete_rail()
                    update_temp_from_input_multi(['ds1', 'ds12', 
                        'widget_lambda0', 'widget_lambda1', 'widget_lambda2', 'widget_lambda3',
                        'widget_lambda4', 'widget_lambdac', 'widget_ds1', 'widget_ds12', 'manual_input_correction'
                    ])
        # col1, col2, col3 = st.columns(3)
        # with col3:
        #     button_text = "Update" if st.session_state.get('edit_mode', False) else "Save Result"
        #     if st.button(button_text, key=f"save_result_",use_container_width=True, type="primary"):
        #         save_fatigue_case()
#결과페이지
    def final_check():
        try:
            if st.session_state.get('is_ok') == "N/A" :
                return True
        except:
            return False
    
    with tab4:
        if validation_errors1 or validation_errors2 or final_check():
            with st.container(height=800, border=False):
                st.error("Input values are not valid. Please check your input again.")
                if abs(st.session_state.get('span_length', 0)) == 0:
                    st.error("Please enter span length(L).")
                if abs(st.session_state.get('Es', 0)) == 0:
                    st.error("Please enter Young's modulus(Es).")
                if abs(st.session_state.get('scmax71', 0)) == 0:
                    st.error("Please enter scmax71 value.")
                if abs(st.session_state.get('scperm', 0)) == 0:
                    st.error("Please enter scperm value.")
                if abs(st.session_state.get('fck', 0)) == 0:
                    st.error("Please enter fck value ($f_{ck}$).")
                if abs(st.session_state.get('vol', 0)) == 0:
                    st.error("Please enter volume ($Vol$).")
                if abs(st.session_state.get('nc', 0)) == 0:
                    st.error("Please enter number of loaded tracks ($N_c$).")
                if abs(st.session_state.get('lambda_c', 0)) == 0:
                    st.error("Please enter correction factor ($\lambda_{c}$) value.")
                if st.session_state.correction_factor_auto_calculate == True:    
                    if abs(st.session_state.get('ds1', 0)) == 0:
                        st.error("Please enter Moving Load ($\Delta\sigma_1$) for correction factor value.")
                    if abs(st.session_state.get('ds12', 0)) == 0:
                        st.error("Please enter Moving Load ($\Delta\sigma_{1+2}$) for correction factor value.")

                if st.session_state.get('is_ok') == "N/A":
                    st.error("Calculation is needed. Please click the calculation button below.")
                    if st.button("Calculate Fatigue Result", key="calculate_fatigue_result", use_container_width=True):
                        cal_for_rail_desm.calculate_all_lambdas_concrete_rail()
                        st.rerun()
        else:
            with st.container(height=800, border=False):
                if st.session_state.get('input_changed', False):
                    st.warning("🔄 Input values have been changed. Please recalculate to see updated results.")
                    if st.button("Fatigue Result Recalculate", key="calculate_fatigue_result2", use_container_width=True):
                        cal_for_rail_desm.calculate_all_lambdas_concrete_rail()
                        st.session_state.input_changed = False
                        st.rerun()


                if 'discriminant_rail_des' in st.session_state:
                    with st.container(border=True, height=800):
                        # 결과 섹션
                        st.markdown("<h5><b>Concrete Compression Fatigue Result(DESM)</b></h5>", unsafe_allow_html=True)
                        
                        # 계산된 fcd 값 가져오기
                        fcd = st.session_state.get('fcd', 0.0)
                        
                        with st.container(border=True, height=80):
                            discriminant = st.session_state.discriminant_rail_des
                            st.latex(
                                r"14 \cdot \frac{1 - S_{cd,max,equ}}{\sqrt{1 - R_{equ}}} = " + 
                                f"{discriminant:.2f} " +
                                (r"\geq 6" if discriminant >= 6 else r"< 6") +
                                (r"\;\; \therefore O.K" if discriminant >= 6 else r"\;\; \therefore N.G")
                            )
                        
                        # 상세 계산 결과 표시
                        st.markdown("<h5><b>Detail Calculation of Concrete Compression Fatigue Result(DESM)</b></h5>", unsafe_allow_html=True)      
                        if st.session_state.correction_factor_auto_calculate ==False:
                            lambda0 = st.session_state.get('lambda0', 0)
                            lambda1 = st.session_state.get('lambda1', 0)
                            lambda2 = st.session_state.get('lambda2', 0)
                            lambda3 = st.session_state.get('lambda3', 0)
                            lambda4 = st.session_state.get('lambda4', 0)
                            pass
                        else:        
                            # Lambda0 결과
                            lambda0 = st.session_state.get('calc_lambda0', 0.0)
                            st.write(r"Correction factor of $\lambda_{0}$ = " + f"{lambda0:.3f}")
                            with st.container(border=True, height=120):
                                scperm = st.session_state.get('scperm', 0.0)
                                st.latex(r"\lambda_{0} = 0.94 + 0.2 \cdot \frac{\sigma_{c,perm}}{f_{cd}} = 0.94 + 0.2 \cdot \frac{" + f"{scperm:.3f}" + "}{" + f"{fcd:.3f}" + "} = " + f"{lambda0:.3f}")
                                st.latex(r"\lambda_{0} = 1 \;\; \text{if} \;\; \sigma_{c,perm} \leq 0.5 \cdot f_{cd}")

                            # Lambda1 결과
                            lambda1 = st.session_state.get('calc_lambda1', 0.0)
                            st.write(r"Correction factor of $\lambda_{1}$ = " + f"{lambda1:.3f}")
                            with st.container(border=True, height=120):
                                sp = st.session_state.get('sp', "Simply Supported Beams")
                                az = st.session_state.get('az', "Compression zone")
                                span_length = st.session_state.get('span_length', 30.0)
                                tt = st.session_state.get('tt', "Standard traffic")
                                
                                st.latex(r"\lambda_{1} = \begin{cases} & \text{Support Type: " + str(sp) + r"} \\" + 
                                        r"      & \text{Analysis Zone: " + str(az) + r"} \\" +
                                        r"      & \text{Span Length: " + str(span_length) + r"m ("r"between 2m and 20m interpolated)} \\" +
                                        r"      & \text{Traffic Type: " + str(tt) + r"} \end{cases} = " + 
                                        f"{lambda1:.3f}")
                                        
                            # Lambda2 결과
                            lambda2 = st.session_state.get('calc_lambda2', 0.0)
                            vol = st.session_state.get('vol', 100000)
                            st.write(r"Correction factor of $\lambda_{2}$ = " + f"{lambda2:.3f}")
                            with st.container(border=True, height=80):        
                                st.latex(r"\lambda_{2} = 1 + \frac{1}{8} \cdot \log_{10} \left(\frac{" + f"{vol}" + r"}{25,000,000}\right) = " + f"{lambda2:.3f}")
                                
                            # Lambda3 결과
                            lambda3 = st.session_state.get('calc_lambda3', 0.0)
                            nyear = st.session_state.get('nyear', 50)
                            st.write(r"Correction factor of $\lambda_{3}$ = " + f"{lambda3:.3f}")
                            with st.container(border=True, height=80):           
                                st.latex(r"\lambda_{3} = 1 + \frac{1}{8} \cdot \log_{10} \left(\frac{" + f"{nyear}" + r"}{100}\right) = " + f"{lambda3:.3f}")
                            
                            # Lambda4 결과
                            lambda4 = st.session_state.get('calc_lambda4', 0.0)
                            ds1 = st.session_state.get('ds1', 0.0)
                            ds12 = st.session_state.get('ds12', 0.0)
                            nc = st.session_state.get('nc', 2)
                            nt = st.session_state.get('nt', 1)
                            
                            st.write(r"Correction factor of $\lambda_{4}$ = " + f"{lambda4:.3f}")

                            if ds12 != 0 and (ds1/ds12 <= 0.8):
                                st.markdown(
                                    "The simultaneity factor $n$ is fixed at 0.12",
                                    unsafe_allow_html=True
                                )
                                st.markdown(
                                    "      assumed that $\sigma_1 = \sigma_2$.",
                                    unsafe_allow_html=True
                                )
                                with st.container(border=True, height=130):
                                    st.latex(
                                        r"\lambda_4 = 1 + \frac{1}{8} \cdot \log_{10}(n) = 1 + \frac{1}{8} \cdot \log_{10}(0.12) = " + f"{lambda4:.3f}"
                                    )

                                    # 조건 수식 아래 줄
                                    ratio = ds1 / ds12 if ds12 != 0 else 0  # 0으로 나눔 방지

                                    st.latex(
                                        r"\text{if} \quad \frac{\sigma_{c1}}{\sigma_{c1+2}} = \frac{" +
                                        f"{ds1:.3f}" + r"}{" + f"{ds12:.3f}" + r"} = " + f"{ratio:.3f}" + r" \leq 0.8"
                                    )

                            else:
                                with st.container(border=True, height=100):
                                    st.latex(r"\lambda_{4} = 1 \;\; \text{if} \;\; \frac{\Delta\sigma_{1,max}}{\Delta\sigma_{1+2}} > 0.8")

                        # Lambda_c 결과
                        lambdac = lambda0 * lambda1 * lambda2 * lambda3 * lambda4
                        st.session_state.calc_lambdac = lambdac  # 계산 결과 저장
                        
                        st.write(r"Correction factor of $\lambda_{c}$ = " + f"{lambdac:.3f}")
                        with st.container(border=True, height=80):
                            st.latex(r"\lambda_{c} = " + f"{lambda0:.3f}" + r" \cdot " + f"{lambda1:.3f}" + r" \cdot " + f"{lambda2:.3f}" + r" \cdot " + f"{lambda3:.3f}" + r" \cdot " + f"{lambda4:.3f}" + r" = " + f"{lambdac:.3f}")
                            
                        # 피로 응력 결과
                        st.markdown("<h5><b>Fatigue Stress for Railway(DESM)</b></h5>", unsafe_allow_html=True)
                        
                        # 필요한 값들 가져오기
                        scmax71 = abs(st.session_state.get('scmax71', 0.0))
                        scperm = st.session_state.get('scperm', 0.0)
                        
                        # 등가 응력 계산 (필요한 경우)
                        sigma_cd_max_equ = scperm + lambdac * (abs(scmax71) - scperm)
                        sigma_cd_min_equ = scperm + lambdac * (scperm - 0)
                        
                        # 저장
                        st.session_state.sigma_cd_max_equ = sigma_cd_max_equ
                        st.session_state.sigma_cd_min_equ = sigma_cd_min_equ
                                    # 정규화된 응력 계산
                        scd_max_equ = sigma_cd_max_equ / fcd if fcd != 0 else 0
                        scd_min_equ = sigma_cd_min_equ / fcd if fcd != 0 else 0
                        # 표시
                        st.write("Upper stresses of the damage equivalent stress spectrum")
                        with st.container(border=True, height=140):
                            st.markdown(r"$\sigma_{cd,max,equ} = \sigma_{c,perm} + \lambda_{c} (\sigma_{c,max,71} - \sigma_{c,perm})$")
                            st.markdown(
                                r"$\sigma_{cd,max,equ} = " + f"{scperm:.3f}" + r" + " + f"{lambdac:.3f}" + r" \cdot (" + 
                                f"{scmax71:.3f}" + r" - " + f"{scperm:.3f}" + r") = " + f"{sigma_cd_max_equ:.3f} MPa$",
                                unsafe_allow_html=True
                            )
                            st.markdown(r"$S_{cd,max,equ} = \frac{\sigma_{cd,max,equ}}{f_{cd}}$")
                            st.markdown(
                                r"$S_{cd,max,equ} = \frac{" + f"{sigma_cd_max_equ:.3f}" + "}{" + f"{fcd:.3f}" + r"} = " + f"{scd_max_equ:.3f}$",
                                unsafe_allow_html=True
                            )
                        st.write("Lower stresses of the damage equivalent stress spectrum")
                        with st.container(border=True, height=140):
                            st.markdown(r"$\sigma_{cd,min,equ} = \sigma_{c,perm} - \lambda_{c} (\sigma_{c,perm} - \sigma_{c,min,71})$")
                            st.markdown(
                                r"$\sigma_{cd,min} = " + f"{scperm:.3f}" + r" + " + f"{lambdac:.3f}" + r" \cdot (" + 
                                f"{scperm:.3f}" + r" - " + f"{0:.3f}" + r") = " + f"{sigma_cd_min_equ:.3f}MPa$",
                                unsafe_allow_html=True
                            )
                            st.markdown(r"$S_{cd,min,equ} = \frac{\sigma_{cd,min,equ}}{f_{cd}}$") 
                            st.markdown(
                                r"$S_{cd,min,equ} = \frac{" + f"{sigma_cd_min_equ:.3f}" + "}{" + f"{fcd:.3f}" + r"} = " + f"{scd_min_equ:.3f}$",
                                unsafe_allow_html=True
                            )
                        st.markdown("<small><i>note) σc,min,71 is conservatively taken as 0.000 MPa for design purposes.</i></small>", unsafe_allow_html=True)
                        st.markdown("<small><i>note) The dynamic factor Φ is not applied in this review. If necessary, it should be applied to the modeling load factor.</i></small>", unsafe_allow_html=True)

                        st.write("Fatigue Result Calculation")
                        # 결과 표시
                        with st.container(border=True, height=120):

                            # 저장
                            st.session_state.scd_max_equ = scd_max_equ
                            st.session_state.scd_min_equ = scd_min_equ
                            
                            # 응력비
                            requ = scd_min_equ / scd_max_equ if scd_max_equ != 0 else 0
                            st.session_state.requ = requ

                            st.markdown(r"$R_{equ} = \frac{S_{cd,min,equ}}{S_{cd,max,equ}} = " + f"{scd_min_equ:.3f}" + r" / " + f"{scd_max_equ:.3f}" + r" = " + f"{requ:.3f}$")
                            st.latex(
                                r"14 \cdot \frac{1 - S_{cd,max,equ}}{\sqrt{1 - R_{equ}}} = " + 
                                f"{discriminant:.2f} " +
                                (r"\geq 6" if discriminant >= 6 else r"< 6") +
                                (r"\;\; \therefore O.K" if discriminant >= 6 else r"\;\; \therefore N.G")
                            )




                else:
                    st.info("계산 결과가 없습니다. 먼저 'Calculation' 버튼을 클릭하여 계산을 수행하세요.")
                    
                    # 계산 버튼 추가
                    if st.button("Calculate", key="calculate_results", use_container_width=True):
                        # 계산 함수 호출
                        cal_for_rail_desm.calculate_all_lambdas_concrete_rail()
                        st.rerun()  # 페이지 리로드

        fatigue_tab(tabs[3], tabs[2], None)
        # col1, col2, col3 = st.columns(3)
        # with col3:
        #     button_text = "Update" if st.session_state.get('edit_mode', False) else "Save Result"
        #     if st.button(button_text, key=f"save_result_2"):
        #         save_fatigue_case()

    # # 디버깅 정보 표시 (옵션)
    # if st.sidebar.checkbox("Show Debug Info"):
    #     st.sidebar.subheader("Debug Session State")
    #     st.sidebar.write("Edit Mode:", is_edit_mode)
    #     st.sidebar.write("Case Name:", st.session_state.get('case_name', 'None'))
        
    #     st.sidebar.write("Session Values:", {
    #         'case_name': st.session_state.case_name,
    #         'design_factor': st.session_state.design_factor,
    #         'stress': st.session_state.stress,
    #         'Fatigue_method': st.session_state.Fatigue_method,
    #         'fcm': st.session_state.get('fcm', 'Not set'),
    #         'fcd': st.session_state.get('fcd', 'Not calculated'),
    #         'discriminant_rail_des': st.session_state.get('discriminant_rail_des', 'Not calculated')
    #     })
    #     if st.button("🧪 temp_result_df 초기화"):
    #         if 'temp_result_df' in st.session_state:
    #             del st.session_state.temp_result_df
    #             st.session_state.temp_result_df = pd.DataFrame()
    #         st.success("temp_result_df가 초기화되었습니다.")
    #     st.sidebar.write("Temp DF:", st.session_state.get('temp_result_df'))
    #     if st.sidebar.checkbox("Show Result DF"):
    #         st.sidebar.write("Result DF:", st.session_state.get('result_df'))


'''이코드의 입력값들  
 Railway  

1page  
- case_name  
- fck (fcm)  
- span_length  
- manual_input (Import 토글)  
- scmax71  
- scperm  

2page  
- vol  
- nc  
- tt (traffic_type)  
- sp (support_type)  
- az (analysis_zone)  

3page  
- correction_factor_auto_calculate  
- manual_input_correction  
- ds1  
- ds12  
- lambda0  
- lambda1  
- lambda2  
- lambda3  
- lambda4  '''