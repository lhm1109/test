# fatigue_reinforcedsteel_desm_rail_ui.py
import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import math
from projects.concrete_fatigue_analysis_ntc2018.session_manager import *
from streamlit_extras.switch_page_button import switch_page
from projects.concrete_fatigue_analysis_ntc2018.calc.fatigue_prestressing_steel_desm_rail_design import *
from projects.concrete_fatigue_analysis_ntc2018.calc.railway_prestressing_steel_lambda import *
import re
# 세션 초기화
# PageManager 네비게이션 import
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from projects.concrete_fatigue_analysis_ntc2018.utils.navigator import back_to_fatigue_case

initialize_session()
# 모달 다이얼로그 가져오기
import_dialogs = SessionManager.initialize_import_dialogs() if 'SessionManager' in globals() else None
civil_stress_import = import_dialogs['steel_stress'] if 'steel_stress' in import_dialogs else None
civil_stress_import2 = import_dialogs['moving_stress'] if 'moving_stress' in import_dialogs else None
def calculate_resistance_axial(tensilstress):
    """fb 계산 함수 - 간소화 버전"""
    
    # 요소 정보
    get_Elem = st.session_state.temp_result_df.at[0, 'element_number_ds1']
    get_ij = st.session_state.temp_result_df.at[0, 'element_part_ds1']

    # Construction Stage 데이터에서 응력만 추출
    if st.session_state.civil_result_conststage_df is not None:
        df = st.session_state.civil_result_conststage_df
        
        # 선택된 요소로 필터링
        elem_to_find = str(get_Elem)     
        df = df[df['Elem'].astype(str).isin([elem_to_find])]
        df = df.iloc[:-8]
        df = df.iloc[-4:]

        # 응력 계산을 위한 데이터 처리
        df['Cb3(+y-z)'] = pd.to_numeric(df['Cb3(+y-z)'], errors='coerce')
        df['Cb4(-y-z)'] = pd.to_numeric(df['Cb4(-y-z)'], errors='coerce')

        # 최소 응력 계산
        df['Cb_min'] = df[['Cb3(+y-z)', 'Cb4(-y-z)']].min(axis=1)

        # get_ij에서 실제 part 추출
        target_part = get_ij.replace('Part ', '') if get_ij.startswith('Part ') else get_ij

        # fb 계산
        fb_list = []
        for _, row in df.iterrows():
            part = row['Part']
            comb_stress = float(row['Cb_min'])
            
            # I, J인 경우 정확히 매치, 그 외에는 모든 값 포함
            if target_part in ['I', 'J']:
                if part == target_part:
                    fb = comb_stress + tensilstress
                    fb_list.append(fb)
            else:
                # 2/4, 3/4 등의 경우 모든 값 중 최대값 사용
                fb = comb_stress + tensilstress
                fb_list.append(fb)

        # 최종 fb는 fb_list의 최대값
        fb = max(fb_list) if fb_list else 0
        return fb
    
    return 0
# UI 용 간소화된 스틸 피로 계산 클래스
class cal_for_steel_desm_rail:
    """스틸 피로 계산을 위한 UI 용 클래스"""
    @staticmethod
    def calculate_lambda_s_values_rail():
        """모든 lambda_s 계수 계산"""
        try:
            # 계산에 필요한 데이터 수집
            case_id = st.session_state.case_name
            steel_type = st.session_state.steel_type
            support_type = st.session_state.support_type_rail
            traffic_type = st.session_state.traffic_type_rail
            span_length = st.session_state.span_length
            vol = st.session_state.vol
            nyear = st.session_state.nyear
            nc = st.session_state.nc
            nt = st.session_state.nt
            delta_sigma_1 = st.session_state.delta_sigma_1
            delta_sigma_12 = st.session_state.delta_sigma_12
            
            # 계산용 임시 데이터프레임 생성 (case_id 컬럼 확인)
            if 'temp_result_df' not in st.session_state or st.session_state.temp_result_df.empty:
                st.session_state.temp_result_df = pd.DataFrame([{"case_id": case_id}])
            elif 'case_id' not in st.session_state.temp_result_df.columns:
                # case_id 컬럼이 없으면 추가
                st.session_state.temp_result_df['case_id'] = case_id
            
            temp_df = st.session_state.temp_result_df.copy()
            
            # S-N 곡선 지수(k2) 가져오기
            k2 = get_k2_value_rail(steel_type)
            
            # 각 람다값 계산 (각 계산 사이에 컬럼 존재 여부 확인 추가)
            # lambda1 계산
            if "lambda1" not in temp_df.columns:
                temp_df["lambda1"] = 0.0
            lambda1 = get_lambda1_rail(support_type, steel_type, span_length, traffic_type)
            temp_df.loc[temp_df["case_id"] == case_id, "lambda1"] = lambda1
            
            # lambda2 계산
            if "lambda2" not in temp_df.columns:
                temp_df["lambda2"] = 0.0
            lambda2 = calculate_lambda2_rail(vol, k2)
            temp_df.loc[temp_df["case_id"] == case_id, "lambda2"] = lambda2
            
            # lambda3 계산
            if "lambda3" not in temp_df.columns:
                temp_df["lambda3"] = 0.0
            lambda3 = calculate_lambda3_rail(nyear, k2)
            temp_df.loc[temp_df["case_id"] == case_id, "lambda3"] = lambda3
            
            # lambda4 계산
            if "lambda4" not in temp_df.columns:
                temp_df["lambda4"] = 0.0
            lambda4 = calculate_lambda4_rail(delta_sigma_1, delta_sigma_12, nc, nt, k2)
            temp_df.loc[temp_df["case_id"] == case_id, "lambda4"] = lambda4
            
            # lambda_s 계산
            if "lambda_s" not in temp_df.columns:
                temp_df["lambda_s"] = 0.0
            lambda_s = lambda1 * lambda2 * lambda3 * lambda4
            temp_df.loc[temp_df["case_id"] == case_id, "lambda_s"] = lambda_s
            
            # 계산된 데이터프레임을 세션에 다시 저장
            st.session_state.temp_result_df = temp_df
            
            # 계산된 값을 세션 상태에 저장
            st.session_state.lambda1 = lambda1
            st.session_state.lambda2 = lambda2
            st.session_state.lambda3 = lambda3
            st.session_state.lambda4 = lambda4
            st.session_state.lambda_s = lambda_s
            st.session_state.k2 = k2  # k2 값도 저장
            
            # temp_result_df 업데이트
            update_temp_from_input_multi([
                'lambda1', 'lambda2', 'lambda3', 'lambda4', 'lambda_s', 'k2'
            ])
            
            return lambda_s
            
        except Exception as e:
            st.error(f"Lambda 계수 계산 중 오류 발생: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return 1.0
    
    @staticmethod
    def calculate_delta_sigma_equ_rail():
        """등가 응력 범위 계산"""
        try:
            # 필요한 입력값 수집
            inputs = {
                "case_id": st.session_state.case_name,
                "lambda_s": st.session_state.lambda_s,
                "delta_sigma_1": st.session_state.delta_sigma_1,
                "section_type": st.session_state.section_type
            }
            
            # 계산용 임시 데이터프레임
            if 'temp_result_df' not in st.session_state or st.session_state.temp_result_df.empty:
                st.session_state.temp_result_df = pd.DataFrame([{"case_id": inputs["case_id"]}])
            
            # 등가 응력 범위 계산
            temp_df = st.session_state.temp_result_df
            temp_df = update_delta_sigma_equ_prestressing_steel_rail(inputs, temp_df)
            Es=st.session_state.Es
            Ec=st.session_state.Ec
            # 계산된 값 세션에 저장
            delta_sigma_equ = temp_df.loc[temp_df["case_id"] == inputs["case_id"], "delta_sigma_equ"].values[0]
            st.session_state.delta_sigma_equ = delta_sigma_equ* Es/Ec
            
            # temp_result_df 업데이트
            update_temp_from_input('delta_sigma_equ')
            
            return delta_sigma_equ
        except Exception as e:
            st.error(f"등가 응력 범위 계산 중 오류 발생: {str(e)}")
            return 0.0

    @staticmethod
    def calculate_result_rail():
        """최종 피로 판정 계산"""
        try:
            # 필요한 입력값 수집
            inputs = {
                "case_id": st.session_state.case_name,
                "steel_type": st.session_state.steel_type,
                "delta_sigma_equ": st.session_state.delta_sigma_equ,
                "factor_rf": st.session_state.factor_rf,
                "factor_rsfat": st.session_state.factor_rsfat
            }
            
            # 계산용 임시 데이터프레임
            if 'temp_result_df' not in st.session_state or st.session_state.temp_result_df.empty:
                st.session_state.temp_result_df = pd.DataFrame([{"case_id": inputs["case_id"]}])
            
            # 기준 응력 범위 가져오기
            temp_df = st.session_state.temp_result_df
            temp_df = update_delta_sigma_Rsk_prestressing_steel_rail(inputs, temp_df)
            lambda_s = st.session_state.lambda_s
            # 판정 계산
            temp_df = calculate_verification_prestressing_steel_rail(inputs, temp_df)
            
            # 계산 결과 세션에 저장
            left_side = temp_df.loc[temp_df["case_id"] == inputs["case_id"], "left_side"].values[0]
            right_side = temp_df.loc[temp_df["case_id"] == inputs["case_id"], "right_side"].values[0]
            is_steel_ok = temp_df.loc[temp_df["case_id"] == inputs["case_id"], "is_steel_ok"].values[0]
            if is_steel_ok == True:
                is_ok = "OK"
            else:
                is_ok = "NG"
            st.session_state.is_ok = is_ok
            discriminant_steel = temp_df.loc[temp_df["case_id"] == inputs["case_id"], "discriminant_steel"].values[0]
            delta_sigma_Rsk = temp_df.loc[temp_df["case_id"] == inputs["case_id"], "delta_sigma_Rsk"].values[0]
            gamma_F = temp_df.loc[temp_df["case_id"] == inputs["case_id"], "gamma_F"].values[0]
            gamma_Sd = temp_df.loc[temp_df["case_id"] == inputs["case_id"], "gamma_Sd"].values[0]
            gamma_fat = temp_df.loc[temp_df["case_id"] == inputs["case_id"], "gamma_fat"].values[0]
            st.session_state.delta_sigma_equ = temp_df.loc[temp_df["case_id"] == inputs["case_id"], "delta_sigma_equ"].values[0] * lambda_s
            # 세션 상태에 저장
            st.session_state.left_side = left_side
            st.session_state.right_side = right_side
            st.session_state.is_steel_ok = is_steel_ok

            st.session_state.discriminant_steel = discriminant_steel
            st.session_state.delta_sigma_Rsk = delta_sigma_Rsk
            st.session_state.gamma_F = gamma_F
            st.session_state.gamma_Sd = gamma_Sd
            st.session_state.gamma_fat = gamma_fat
            
            # temp_result_df 업데이트
            update_temp_from_input_multi([
                'delta_sigma_Rsk', 'gamma_F', 'gamma_Sd', 'gamma_fat',
                'left_side', 'right_side', 'is_steel_ok', 'discriminant_steel', 'is_ok','delta_sigma_equ'
            ])
            
            return is_steel_ok, discriminant_steel
            
        except Exception as e:
            st.error(f"판정 계산 중 오류 발생: {str(e)}")
            return False, 0.0


def fatigue_reinforcedsteel_desm_rail_ui_page():
    st.session_state.Fatigue_method = "Reinforcing Steel(Rail_DES)"
    # Initialize variables at the beginning
    notyetchecked = False  # Add this line
    exception_exist = False  # Add this line
    is_cracked_section = st.session_state.get('section_type', '') == 'Cracked section'
    def save_fatigue_case():

        """피로 케이스 저장 함수"""
        case_id = st.session_state.get('case_name', )
        
        # 수정 모드가 아닐 때만 중복 체크
        if not hasattr(st.session_state, 'edit_mode') or not st.session_state.edit_mode:
            if not st.session_state.result_df.empty and 'case_id' in st.session_state.result_df.columns and case_id in st.session_state.result_df['case_id'].values:
                st.error(f"'{case_id}' 케이스가 이미 존재합니다. 다른 이름을 사용해주세요.")
                return False
        
        # 필수 값 체크
        required_fields = ['span_length', 'steel_type', 'delta_sigma_1']
        if not all(k in st.session_state for k in required_fields):
            st.error("필수 입력값이 누락되었습니다. 모든 필드를 입력해주세요.")
            return False
        
        # temp_result_df 데이터 업데이트
        if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
            # 현재 케이스 데이터 업데이트
            st.session_state.temp_result_df.at[0, 'case_id'] = case_id
            st.session_state.temp_result_df.at[0, 'case_method'] = "Steel Grider(DES)"
            
            # 판정값 저장 (있는 경우에만)
            if 'discriminant_steel' in st.session_state:
                st.session_state.temp_result_df.at[0, 'discriminant_steel'] = st.session_state.discriminant_steel
            
            # save_to_result_df 함수 사용하여 저장
            if save_to_result_df():
                st.success(f"'{case_id}' 케이스가 저장되었습니다.")
                back_to_fatigue_case()
                return True
            else:
                st.error("저장 중 오류가 발생했습니다.")
        
        return False
    
    # 편집 모드 체크
    is_edit_mode = st.session_state.get('edit_mode', False)
    
    # 편집 모드일 경우 페이지 제목 변경
    if is_edit_mode:
        st.markdown(f"<h5><b>[Edit]Reinforcing Steel(DESM) : Railway:{st.session_state.get('fatigue_case_name', '')}</b></h5>", unsafe_allow_html=True)
    else:
        st.markdown("<h5><b>Reinforcing Steel(DESM) : Railway</b></h5>", unsafe_allow_html=True)
    
    # 탭 제목
    tabs = [
        "Fatigue Settings",
        "Fatigue Parameters",
        "Correction Factor",
        "Fatigue Result",
    ]

    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(tabs)

    # 첫번째 탭 Fatigue Settings
    with tab1:

        with st.container(height=800, border=False):
            st.markdown("<h6><b>Fatigue Settings</b></h6>", unsafe_allow_html=True)
            import pandas as pd
            
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
            case_id = st.session_state['case_name']
            # 중복 체크
            is_duplicate = (
                not is_edit_mode
                and case_name in st.session_state.get("result_df", pd.DataFrame()).get("case_id", [])
            )
            if is_duplicate:
                st.toast(f"'{case_name}' case already exists. Please use a different name.")

            col1, col2 = st.columns(2)
            with col1:
                # 스팬 길이
                 st.number_input(r"Span length (m), $L$", 
                            value=st.session_state.get('span_length', 35.0),
                            key='widget_span_length', 
                            on_change=update_temp_from_input, 
                            args=('widget_span_length','span_length'))
                

            with col2:

                # 강재 탄성계수
                Es = st.number_input(
                    r"Steel elastic modulus, $E_s$ [N/mm²]", 
                    value=st.session_state.get('Es', 1.95e5),
                    key='Es', 
                    on_change=update_temp_from_input, 
                    args=('Es',)
                )

            
            # 단면 특성
            col1, col2 = st.columns(2)
            with col1:

                # 콘크리트 탄성계수
                Ec = st.number_input(
                    r"Concrete elastic modulus, $E_c$ [N/mm²]", 
                    value=st.session_state.get('Ec', 3.7e4),
                    key='Ec', 
                    on_change=update_temp_from_input, 
                    args=('Ec',)
                )


                
            with col2:

                
                # 유효높이
                d = st.number_input(
                    r"Effective height, $d$ [mm]", 
                    value=st.session_state.get('d', 2700),
                    key='d', 
                    on_change=update_temp_from_input, 
                    args=('d',)
                )
            # 균열 비균열 단면 상태 
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h6><b>Crack State Detection</b></h6>", unsafe_allow_html=True)
            with col2:
                use_midas = st.session_state.get('manual_input2', True)

                # value 값을 미리 계산
                if  st.session_state.get('manual_input_correction', True) == False:
                    toggle_value = False
                else:
                    toggle_value =  st.session_state.get('manual_input_correction', True)
                crack_option = st.toggle(
                    "Crack State: Manual/Auto",
                    value=toggle_value,
                    key="widget_crack_option", 
                    disabled=not use_midas,
                    help="Automatic crack state detection is only available when importing loads from MIDAS model",
                    on_change=update_temp_from_input,
                    args=("widget_crack_option", "crack_option")
                )  
    
            if crack_option == False:
                # 수동 모드
                if st.session_state.get('section_type', '') == "":
                    st.session_state.section_type = "Non-cracked section"
                    update_temp_from_input(['section_type'])
                section_type = st.selectbox(
                    "Section Type",
                    ["Non-cracked section", "Cracked section"],
                    index=0,
                    key="section_type",
                    on_change=update_temp_from_input,
                    args=("section_type",)
                )

                if st.session_state.section_type == "Non-cracked section":
                    expander = True
                else:
                    expander = False
            else:
                if st.session_state.section_type == "Non-cracked section" or st.session_state.section_type == "":
                    expander = True
                else:
                    expander = False          
        
            
                if st.button("Calculate Crack State", key="calculate_crack_state", use_container_width=True):
                    try:
                        axial_stress =  st.session_state.get('delta_sigma_1')
                        fb = calculate_resistance_axial(axial_stress)
                        st.session_state.fb = fb
                            # temp_result_df에도 저장
                        update_temp_from_input_multi(['section_type', 'is_cracked_section', 'fctd', 'fb'])
                            
                        #     st.success("Crack state calculation completed!")
                        # else:
                        #     st.error("Failed to calculate crack state. Please check your input data.")
                        fb = calculate_resistance_axial(axial_stress)
                    except Exception as e:
                        st.error(f"Error during crack state calculation: Please load load from below.")
                        # Initialize exception_exist flag
                        exception_exist = True
                get_fck =  st.session_state.get('fck', 0)

                rc = st.session_state.factor_rcfat

                # fctm 계산
                fctm = 0.30 * pow(get_fck, 2/3) if get_fck <= 50 else 2.12 * math.log(1 + get_fck/10)
                fctk005 = 0.7 * fctm
                fctd = fctk005 / rc
                fb = st.session_state.get('fb', 0)
                st.session_state.fctd = fctd

                if 'fb' in st.session_state and 'fctd' in st.session_state and st.session_state.get('fb', 0) != 0:
                    if st.session_state.fb > st.session_state.fctd:
                        st.success(f"Cracked section ($\\sigma_{{c,\\mathrm{{traz}}}}$ ($f_b$) = {fb:.2f} MPa > $f_{{ctd}}$ = {fctd:.2f} MPa)")
                        st.session_state.section_type = "Cracked section"
                        is_cracked_section = True
                        
                        update_temp_from_input_multi(['section_type', 'is_cracked_section', 'fctd', 'fb'])



                    else:
                        st.success(f"Non-cracked section ($\\sigma_{{c,\\mathrm{{traz}}}}$ ($f_b$) = {fb:.2f} MPa ≤ $f_{{ctd}}$ = {fctd:.2f} MPa)")
                        st.session_state.section_type = "Non-cracked section"  
                        is_cracked_section = False   
                        update_temp_from_input_multi(['section_type', 'is_cracked_section', 'fctd', 'fb'])
                else:
                    # Check if exception occurred during calculation
                    if exception_exist:
                        pass
                    else:
                        st.info("Please check section shear resistance by clicking 'Calculate shear resistance' button")
                    notyetchecked = True
            is_cracked_section = st.session_state.get('section_type', 'Non-cracked section') == 'Cracked section'

            if is_cracked_section:
                expandertitle = "Crack State Detection Load"
            else:
                expandertitle = "Non-cracked Section Input"
            #non-cracked section
            with st.expander(expandertitle, expanded=expander):
                with st.container(border=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("<h6><b>Moving load</b></h6>", unsafe_allow_html=True)
                    with col2:
                        use_midas = safe_toggle(
                            "Load From Midas Model", 
                            key="manual_input_correction", 
                            value=True, 
                            on_change=update_temp_from_input,
                            args=("manual_input_correction",)
                        )
                    col1, col2, col3 = st.columns(3, vertical_alignment="bottom")

                    with col1:
                        # 하중2 모달불러오기
                        if st.button("Import", use_container_width=True, key="for_midas_nx_correction", 
                                    disabled=not use_midas):
                            if civil_stress_import2:
                                civil_stress_import2("Import")

                    with col2:
                        if use_midas == True:
                            st.session_state.delta_sigma_1 = st.session_state.get('ds1', 0)
                            st.session_state.delta_sigma_12 = st.session_state.get('ds12', 0)
                        else:
                            pass
                        # 단일 트랙 응력
                        st.number_input(
                            r"Stress from one track, $\sigma_1$ [MPa]", 
                            value=float(st.session_state.get('delta_sigma_1', 60.0)), 
                            step=0.5, 
                            key="widget_delta_sigma_1",
                            on_change=update_temp_from_input,
                            args=("widget_delta_sigma_1", "delta_sigma_1"),
                            disabled=use_midas
                        )
                        
                    with col3:

                        # 이중 트랙 응력
                        st.number_input(
                            r"Stress from two tracks, $\sigma_{1+2}$ [MPa]", 
                            value=float(st.session_state.get('delta_sigma_12', 70.0)), 
                            step=0.5, 
                            key="widget_delta_sigma_12",
                            on_change=update_temp_from_input,
                            args=("widget_delta_sigma_12", "delta_sigma_12"),
                            disabled=use_midas
                        )
                        if use_midas == False:
                            st.session_state.ds1 = st.session_state.delta_sigma_1
                            st.session_state.ds12 = st.session_state.delta_sigma_12
                        else:
                            pass
                    # print(f"delta_sigma_1: {st.session_state.get('delta_sigma_1', 0)}")
                    # print(f"ds1: {st.session_state.get('ds1', 0)}")
                    # print(f"delta_sigma_12: {st.session_state.get('delta_sigma_12', 0)}")
                    # print(f"ds12: {st.session_state.get('ds12', 0)}")
                    st.markdown("<small><i>note) The dynamic factor Φ is not applied in this review. If necessary, it should be applied to the modeling load factor.</i></small>", unsafe_allow_html=True)
    
                    if use_midas == False and crack_option == True:
                        st.error(f"Automatic crack state detection is not available when entering loads manually")
                    else:
                        pass
 
            current_is_cracked = st.session_state.get('section_type', '') == 'Cracked section'
            if is_cracked_section:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<h6><b>Import Fatigue Load(Carcked Section)</b></h6>", unsafe_allow_html=True)
                with col2:
                    # 하중 불러오기 옵션
                    use_midas = st.toggle("Import From Midas NX", key="manual_input", value=True)
                
                # 하중불러오기
                
                with st.container(border=True):
                    col1, col2 = st.columns(2, vertical_alignment="bottom")
                    with col1:
                        if st.button("Import", use_container_width=True, key="from_midas_nx_moment", 
                                    disabled=not use_midas):
                            # 모멘트 임포트 다이얼로그 호출
                            import_dialogs = SessionManager.initialize_import_dialogs()
                            import_dialogs['moment_force_reqreinf']("Import")
                    
                    with col2:
                        st.number_input(r"Moment value, $Msd$ [kN·m]",
                                    value=float(st.session_state.get('Msd', 1000.0)),
                                    step=1.0, 
                                    key="widget_Msd",
                                    on_change=update_temp_from_input,
                                    args=("widget_Msd", "Msd"),
                                    disabled=use_midas)
                        
                        if not use_midas and 'widget_Msd' in st.session_state:
                            st.session_state.Msd = st.session_state.widget_Msd
                st.markdown("<small><i>note) The dynamic factor Φ is not applied in this review. If necessary, it should be applied to the modeling load factor.</i></small>", unsafe_allow_html=True)

        # 네비게이션 버튼
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- Back", use_container_width=True):
                back_to_fatigue_case()
        with col3:
            def has_validation_errors1():

                # 필수 입력값 체크
                if abs(st.session_state.get('span_length', 0)) == 0:
                    return True
                if abs(st.session_state.get('Es', 0)) == 0:
                    return True
                if abs(st.session_state.get('Ec', 0)) == 0:
                    return True
                if notyetchecked == True:
                    return True
                if abs(st.session_state.get('d', 0)) == 0:
                    return True
                if crack_option == True:
                    if abs(st.session_state.get('ds1', 0)) == 0:
                        return True
                    if abs(st.session_state.get('ds12', 0)) == 0:
                        return True
                if is_cracked_section:
                    if abs(st.session_state.get('Msd', 0)) == 0:
                        return True
                else:
                    if abs(st.session_state.get('ds1', 0)) == 0:
                        return True
                return False

            validation_errors1 = has_validation_errors1()
            if validation_errors1:
                # 일반 버튼
                if st.button("Next →", use_container_width=True, key="next_button_with_error"):
                    if abs(st.session_state.get('span_length', 0)) == 0:
                        st.toast("Please enter span length(L)", icon="⚠️")
                    if abs(st.session_state.get('Es', 0)) == 0:
                        st.toast("Please enter Es value(Es)", icon="⚠️")
                    if abs(st.session_state.get('Ec', 0)) == 0:
                        st.toast("Please enter Concrete elastic modulus(Ec)", icon="⚠️")
                    if st.session_state.get('section_type') == "":
                        st.toast("Please enter section type", icon="⚠️")
                    if abs(st.session_state.get('d', 0)) == 0:
                        st.toast("Please enter Effective height(d)", icon="⚠️")
                    if crack_option == True  :
                        if abs(st.session_state.get('ds1', 0)) == 0:
                            st.toast("Please enter Maximum stress in steel(Δσ₁)", icon="⚠️")
                        if abs(st.session_state.get('ds12', 0)) == 0:
                            st.toast("Please enter Maximum stress in steel(Δσ₁₂)", icon="⚠️")
                    if notyetchecked == True:
                        st.toast("Please check crack state", icon="⚠️")
                    if is_cracked_section:
                        if abs(st.session_state.get('Msd', 0)) == 0:
                            st.toast("Please enter moment value($Msd$).", icon="⚠️")
                    else:
                        if abs(st.session_state.get('ds1', 0)) == 0:
                            st.toast("Please enter fatigue stress values.", icon="⚠️")

            else:
                # Primary 버튼
                if st.button("Next →", use_container_width=True, type="primary", key="next_button_without_error"):
                    update_temp_from_input_multi(['section_type', 'is_cracked_section', 'fctd', 'fb'])
                    update_temp_from_input_multi([
                        'span_length', 'Es', 'Ec', 'd',
                        'crack_option', 'section_type', 'is_cracked_section', 'fctd','widget_crack_option',
                        'fb', 'delta_sigma_1', 'delta_sigma_12', 'Msd'
                    ])
                    add_tab_switch_button("Next", tabs[1])
    
    def fatigue_tab(method, back_tab, next_tab=None):
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back", key=f"back_{method}", use_container_width=True):
                add_tab_switch_button("Back", back_tab)
        with col2:
            pass
        with col3:
            if next_tab and st.button("Next →", key=f"next_{method}", use_container_width=True):
                add_tab_switch_button("Next", next_tab)

    with tab2:

        with st.container(height=800, border=False):


            st.markdown("<h6><b>Reinforced Steel Properties</b></h6>", unsafe_allow_html=True)
            # 강재 타입 선택
            col1, col2 = st.columns(2)
            with col1:
                steel_type = st.selectbox(
                    "Steel Type",
                    [
                        "Straight and bent bars",
                        "Welded bars and wire fabrics",
                        "Splicing devices (reinforcing)",
                        "Pre-tensioning",
                        "Single strands in plastic ducts",
                        "Straight tendons or curved in plastic ducts",
                        "Curved tendons in steel ducts",
                        "Splicing devices (prestressing)"
                    ],
                    index=0,
                    key="steel_type",
                    on_change=update_temp_from_input,
                    args=("steel_type",)
                )

            inputs = {
                "case_id": st.session_state.case_name,
                "steel_type": st.session_state.steel_type,
                "delta_sigma_equ": st.session_state.delta_sigma_equ,
                "factor_rf": st.session_state.factor_rf,
                "factor_rsfat": st.session_state.factor_rsfat
            }
            
            # temp_result_df 초기화 또는 case_id 업데이트
            if 'temp_result_df' not in st.session_state or st.session_state.temp_result_df.empty:
                st.session_state.temp_result_df = pd.DataFrame([{"case_id": inputs["case_id"]}])
            else:
                # 기존 데이터가 있으면 case_id만 업데이트
                st.session_state.temp_result_df.at[0, 'case_id'] = inputs["case_id"]

            # 기준 응력 범위 가져오기
            temp_df = st.session_state.temp_result_df
            temp_df = update_delta_sigma_Rsk_prestressing_steel_rail(inputs, temp_df)


            delta_sigma_Rsk = st.session_state.get('delta_sigma_Rsk', 0)
            with col2:
                st.number_input("Resisting stress range, "+ f"ΔσRsk [MPa]",
                                value=delta_sigma_Rsk,
                                disabled=True,
                )
            if st.session_state.section_type == "Non-cracked section":
                pass
            else:
                # 단면 특성
                col1, col2 = st.columns(2)
                with col1:
                    # key="widget_Vsd",
                    # on_change=update_temp_from_input,
                    # args=("widget_Vsd", "Vsd"),
                    # 강재 단면적
                    A_steel = st.number_input(
                        r"Steel area, $A$ [mm²]", 
                        value=st.session_state.get('A_steel', 98.7),
                        key='widget_A_steel', 
                        on_change=update_temp_from_input, 
                        args=('widget_A_steel', 'A_steel')
                    )            
                with col2:
                    # 강재 개수
                    n_steel = st.number_input(
                        r"Number of steel elements, $n$", 
                        value=float(st.session_state.get('n_steel', 44)),
                        key='widget_n_steel', 
                        on_change=update_temp_from_input, 
                        args=('widget_n_steel', 'n_steel')
                    )  



            st.markdown("<h6><b>Traffic Conditions</b></h6>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:

                st.number_input(
                    r"Number of Tracks, $N_{c}$", 
                    min_value=0, 
                    value=int(st.session_state.get('nc', 2)), 
                    step=1, 
                    key="widget_nc",
                    on_change=update_temp_from_input,
                    args=("widget_nc", "nc")
                )
                st.session_state.nt = 1
                # st.number_input(
                #     r"Number of loaded tracks, $N_{t}$", 
                #     min_value=0, 
                #     value=int(st.session_state.get('nt', 1)), 
                #     step=1, 
                #     key="widget_nt",
                #     on_change=update_temp_from_input,
                #     args=("widget_nt", "nt")
                # )
                st.session_state.traffic_type = "Standard traffic"
                st.selectbox(
                    "Traffic Type",
                    ["Standard traffic", "Heavy traffic"],
                    index=0,
                    key="traffic_type_rail",
                    on_change=update_temp_from_input,
                    args=("traffic_type_rail", "traffic_type_rail")
                )
            with col2:
                st.number_input(
                    r"Tons of weight trains passing per year per track, $Vol$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('vol', 100000.0)), 
                    step=1000.0, 
                    format="%.0f",
                    key="widget_vol",
                    on_change=update_temp_from_input,
                    args=("widget_vol", "vol")
                )
                st.selectbox(
                    "Support Type",
                    [
                        "Simply supported beams", 
                        "Continuous beams (mid span)", 
                        "Continuous beams (end span)", 
                        "Continuous beams (intermediate support)"
                    ],
                    index=0,
                    key="support_type_rail",
                    on_change=update_temp_from_input,
                    args=("support_type_rail", "support_type_rail")
                )

        # 네비게이션 및 저장 버튼
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- Back", use_container_width=True, key="back_to_fatigue_settings2"):
                add_tab_switch_button("Back", tabs[0])

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
                if st.session_state.get('nc', 0) == 0:
                    return True
                if st.session_state.get('vol', 0) == 0:
                    return True
                if not st.session_state.get('traffic_type_rail'):
                    return True
                if not st.session_state.get('support_type_rail'):
                    return True
                if st.session_state.get('section_type', 'Non-cracked section') == "Non-cracked Section Input":
                    if abs(st.session_state.get('n_steel', 0)) == 0:
                        return True
                    if abs(st.session_state.get('A_steel', 0)) == 0:
                        return True
                return False

            # 중복일 경우 또는 유효성 검사 실패 시 Next 버튼 비활성화
            validation_errors = has_validation_errors()
            if validation_errors:
                if st.button("Next →", use_container_width=True, key="next_button1_with_error"):
                    if st.session_state.get('nc', 0) == 0:
                        st.toast("Please enter the Number of tracks.(nc)", icon="⚠️")
                    if st.session_state.get('vol', 0) == 0:
                        st.toast("Please enter the Tons of weight trains passing per year per track.(vol)", icon="⚠️")
                    if not st.session_state.get('traffic_type_rail'):
                        st.toast("Please select the Traffic Type.(traffic_type_rail)", icon="⚠️")
                    if not st.session_state.get('support_type_rail'):
                        st.toast("Please select the Support Type.(support_type_rail)", icon="⚠️")
                    if st.session_state.get('section_type', 'Non-cracked section') == "Non-cracked Section Input":
                        if abs(st.session_state.get('n_steel', 0)) == 0:
                            st.toast("Please enter Number of steel elements(n)", icon="⚠️")
                        if abs(st.session_state.get('A_steel', 0)) == 0:
                            st.toast("Please enter Steel area(A)", icon="⚠️")
            else:
                if st.button("Next →", use_container_width=True, type="primary", key="next_button2_without_error"):
                    update_temp_from_input_multi([
                        'steel_type', 'A_steel', 'n_steel', 'nc',
                        'traffic_type_rail', 'vol', 'support_type_rail'
                    ])
                    add_tab_switch_button("Next", tabs[2])


    # 두번째 탭 - Correction Factor
    with tab3:
        with st.container(height=800, border=False):
            col1, col2 = st.columns(2, vertical_alignment="bottom")
            with col1:
                st.markdown("<h6><b>Correction Factor</b></h6>", unsafe_allow_html=True)
            with col2:
                use_auto_calc = st.toggle(
                    "Correction Factor Auto Calculate", 
                    key="correction_factor_auto_calculate", 
                    value=True, 
                    on_change=update_temp_from_input, 
                    args=("correction_factor_auto_calculate",)
                )
            # 계수 계산 버튼
            if st.button("Calculate Correction Factors", use_container_width=True, 
                        disabled=not st.session_state.correction_factor_auto_calculate, key="calculate_correction_factors2"):
                # 계산 함수 호출
                lambda_s = cal_for_steel_desm_rail.calculate_lambda_s_values_rail() 
                st.toast(f"Lambda coefficient calculation completed: λs = {lambda_s:.3f}", icon="✅")

            col1, col2 = st.columns(2)
            with col1:
                # Lambda1
                st.number_input(
                    r"$\lambda_{s1}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('lambda1', 0.0)),
                    step=0.05, 
                    key="lambda1",
                    on_change=update_temp_from_input,
                    args=("lambda1", ),
                    disabled=st.session_state.correction_factor_auto_calculate
            ) 
                
                # st.session_state.temp_result_df.at[0, 'lambda1']
                
                # Lambda3
                st.number_input(
                    r"$\lambda_{s3}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('lambda3', 0.0)),
                    step=0.05, 
                    key="lambda3",
                    on_change=update_temp_from_input,
                    args=("lambda3", ),
                    disabled=st.session_state.correction_factor_auto_calculate
                )
                
                if st.session_state.get("correction_factor_auto_calculate", False):
                    st.session_state.setdefault("lambda_s", )
                else:
                    st.session_state["lambda_s"] = (
                        st.session_state.get('lambda1', ) *
                        st.session_state.get('lambda2', ) *
                        st.session_state.get('lambda3', ) *
                        st.session_state.get('lambda4', )
                    )
                
                # Lambda_s (총 보정계수)
                st.number_input(
                    r"$\lambda_{s}$ (Total)", 
                    min_value=0.0, 
                    value=float(st.session_state.get('lambda_s', 0.0)),
                    step=0.05, 
                    key="lambda_s",
                    on_change=update_temp_from_input,
                    args=("lambda_s", ),
                    disabled=True
                )
                
            with col2:
                # Lambda2
                st.number_input(
                    r"$\lambda_{s2}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('lambda2', 0.0)),
                    step=0.05, 
                    key="lambda2",
                    on_change=update_temp_from_input,
                    args=("lambda2", ),
                    disabled=st.session_state.correction_factor_auto_calculate
                )
                # Lambda4
                st.number_input(
                    r"$\lambda_{s4}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('lambda4', 0.0)),
                    step=0.05, 
                    key="lambda4",
                    on_change=update_temp_from_input,
                    args=("lambda4", ),
                    disabled=st.session_state.correction_factor_auto_calculate
                )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- Back", use_container_width=True, key="fatigue_correction_back"):
                add_tab_switch_button("Back", tabs[1])  # tabs[1]으로 변경


        with col3:
            # 유효성 검사 실패 여부 확인 함수
            def has_validation_errors2():
                # 필수 입력값 체크
                if abs(st.session_state.get('lambda_s', 0)) == 0:
                    return True
                if is_cracked_section:
                    if abs(st.session_state.get('Msd', 0)) == 0:
                        return True
                else:
                    if abs(st.session_state.get('delta_sigma_1', 0)) == 0:
                        return True
                    if abs(st.session_state.get('delta_sigma_12', 0)) == 0:
                        return True

                return False

            # 중복일 경우 또는 유효성 검사 실패 시 Next 버튼 비활성화  
            validation_errors2 = has_validation_errors2()
            if validation_errors2:
                # 버튼 먼저!
                if st.button("Next →", use_container_width=True, key="next_button3_with_error"):
                    if abs(st.session_state.get('lambda_s', 0)) == 0:
                        st.toast(r"Please enter value ($\lambda_s$)")
                    if is_cracked_section:
                        if abs(st.session_state.get('Msd', 0)) == 0:
                            st.toast("Please enter moment value($Msd$).", icon="⚠️")
                    else:   
                        if abs(st.session_state.get('delta_sigma_1', 0)) == 0:
                            st.toast(r"Please enter value ($\Delta\sigma_1$)", icon="⚠️")
                        if abs(st.session_state.get('delta_sigma_12', 0)) == 0:
                            st.toast(r"Please enter value ($\Delta\sigma_{12}$)", icon="⚠️")

            else:
                if st.button("Calculate Fatigue Result →", key=f"save_result_correction", use_container_width=True, type="primary"):
                    add_tab_switch_button("Next", tabs[3])
                    # save_fatigue_case()
                    if st.session_state.get("correction_factor_auto_calculate", False):
                        lambda_s = cal_for_steel_desm_rail.calculate_lambda_s_values_rail()
                    delta_sigma_equ = cal_for_steel_desm_rail.calculate_delta_sigma_equ_rail()
                    is_ok, discriminant = cal_for_steel_desm_rail.calculate_result_rail()
                    update_temp_from_input_multi([
                        'lambda1', 'lambda2', 'lambda3', 'lambda4','widget_lambda1', 'widget_lambda2',
                        'widget_lambda3', 'widget_lambda4','widget_lambda_s',
                        'lambda_s', 'correction_factor_auto_calculate'
                    ])

    # def final_check():
    #     try:
    #         if st.session_state.get('is_ok') == "N/A" :
    #             return True
    #         if notyetchecked == True:
    #             return True
    #         elif st.session_state.get('is_ok') == "OK" or  st.session_state.get('is_ok') == "NG":
    #             return False
    #     except:
    #         return False
    # test=final_check()
    # 세번째 탭 - Fatigue Result 결과표시 계산과정
    with tab4:          
        if  validation_errors or validation_errors1 or validation_errors2 :
            with st.container(height=800, border=False):
                
                st.error("Input values are not valid. Please check your input again.")
                if abs(st.session_state.get('span_length', 0)) == 0:
                    st.error("Please enter span length(L).", icon="⚠️")
                if abs(st.session_state.get('Es', 0)) == 0:
                    st.error("Please enter Es value(Es).", icon="⚠️")
                if abs(st.session_state.get('Ec', 0)) == 0:
                    st.error("Please enter Concrete elastic modulus(Ec).", icon="⚠️")
                if abs(st.session_state.get('n_steel', 0)) == 0:
                    st.error("Please enter Number of steel elements(n).", icon="⚠️")
                if abs(st.session_state.get('A_steel', 0)) == 0:
                    st.error("Please enter Steel area(A).", icon="⚠️")
                if abs(st.session_state.get('d', 0)) == 0:
                    st.error("Please enter Effective height(d).", icon="⚠️")
                if abs(st.session_state.get('vol', 0)) == 0:
                    st.error("Please enter Tons of weight trains passing per year per track(vol).", icon="⚠️")
                if abs(st.session_state.get('nc', 0)) == 0:
                    st.error("Please enter Number of tracks(nc).", icon="⚠️")
                if abs(st.session_state.get('lambda_s', 0)) == 0:
                    st.error("Please enter correction factor ($\lambda_s$) value.", icon="⚠️")
                if notyetchecked == True:
                    st.error("Please check crack state (Fatigue Settings - crack state detection load expnader).", icon="⚠️")
                if is_cracked_section:
                    if abs(st.session_state.get('Msd', 0)) == 0:
                        st.error("Please enter moment value($Msd$).", icon="⚠️")
                    if abs(st.session_state.get('delta_sigma_1', 0)) == 0:
                        st.error("Please enter Maximum stress in steel(Δσ₁ : Fatigue Settings - crack state detection load expnader).", icon="⚠️")
                    if abs(st.session_state.get('delta_sigma_12', 0)) == 0:
                        st.error("Please enter value (Δσ₁₂ : Fatigue Settings - crack state detection load expnader).", icon="⚠️")
                else:
                    if abs(st.session_state.get('delta_sigma_1', 0)) == 0:
                        st.error("Please enter Maximum stress in steel(Δσ₁ : Fatigue Settings - crack state detection load expnader).", icon="⚠️")
                    if abs(st.session_state.get('delta_sigma_12', 0)) == 0:
                        st.error("Please enter value (Δσ₁₂ : Fatigue Settings - crack state detection load expnader).", icon="⚠️")

                # if st.button("Calculate Fatigue Result.", key="calculate_fatigue_result", use_container_width=True):

                # if st.button("Calculate Fatigue Result", key="calculate_fatigue_result", use_container_width=True):
                #     lambda_s = cal_for_steel_desm_rail.calculate_lambda_s_values_rail()
                #     delta_sigma_equ = cal_for_steel_desm_rail.calculate_delta_sigma_equ_rail() 
                #     is_ok, discriminant = cal_for_steel_desm_rail.calculate_result_rail()

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("<- Back", key="back_to_fatigue_settings33", use_container_width=True):
                    add_tab_switch_button("Back", tabs[2])
        else:

            if 'discriminant_steel' in st.session_state:
                # 3개 열로 나누기
                with st.container(border=True, height=800):
                    if st.session_state.get('input_changed', False):
                        st.warning("🔄 Input values have been changed. Please recalculate to see updated results.")
                        if st.button("Fatigue Result Recalculate", key="calculate_fatigue_result2", use_container_width=True):
                            if st.session_state.get("correction_factor_auto_calculate", False):
                                lambda_s = cal_for_steel_desm_rail.calculate_lambda_s_values_rail()
                            delta_sigma_equ = cal_for_steel_desm_rail.calculate_delta_sigma_equ_rail()
                            is_ok, discriminant = cal_for_steel_desm_rail.calculate_result_rail()
                            st.session_state.input_changed = False
                            st.rerun()
                    st.markdown("<h6><b>Reinforcing Steel Fatigue Result for Railway (DESM)</b></h6>", unsafe_allow_html=True)
                    
                    # 판정값 가져오기
                    left_side = st.session_state.get('left_side', 0.0)
                    right_side = st.session_state.get('right_side', 0.0)
                    is_ok = st.session_state.get('is_steel_ok', False)
                    
                    # 판정 결과 표시
                    with st.container(border=True, height=80):
                        # Main equation at the top
                        # Horizontal comparison layout
                        col1, col2, col3, col4 = st.columns([10, 1, 9, 5], vertical_alignment="center")
                        with col1:
                            st.latex(r"\gamma_F \cdot \gamma_{Sd} \cdot \Delta\sigma_{s,equ} = " + f"{left_side:.3f}\\text{{ MPa}}")
                        with col2:
                            st.latex(r"\leq" if is_ok else r">")
                        with col3:
                            st.latex(r"\frac{\Delta\sigma_{Rsk}}{\gamma_{s,fat}} = " + f"{right_side:.3f}\\text{{ MPa}}")
                        with col4:
                            if is_ok:
                                st.markdown("<h5 style='color: green;'>OK</h5>", unsafe_allow_html=True)
                            else:
                                st.markdown("<h5 style='color: red;'>NG</h5>", unsafe_allow_html=True)
                    
                    # 상세 계산 결과 표시
                    st.markdown("<h6><b>Detail Calculation of Reinforcing Steel Fatigue Result for Railway (DESM)</b></h6>", unsafe_allow_html=True)

                    # 결과 탭에 S-N 커브 표시 기능 추가
                    # st.write("S-N Curve for Steel Fatigue")

                    # 계산에 필요한 값 가져오기
                    steel_type = st.session_state.get('steel_type', "Straight and bent bars")
                    k1 = 5  # 대부분의 강재 유형에 대한 기본값
                    k2 = st.session_state.get('k2', 9.0)  # 강재 유형에 따라 다름
                    delta_sigma_Rsk = st.session_state.get('delta_sigma_Rsk', 162.5)

                    # 강재 유형에 따라 k1 값 설정
                    if "Welded bars" in steel_type or "Splicing devices" in steel_type:
                        k1 = 3

                    # N* 값 계산 (10^6 또는 10^7)
                    N_star = 10**6
                    if "Welded bars" in steel_type or "Splicing devices" in steel_type:
                        N_star = 10**7

                    # S-N 커브 계산
                    import numpy as np
                    import pandas as pd

                    # 로그 스케일용 x 값 생성
                    log_N = np.linspace(4, 9, 100)
                    N_values = 10**log_N
                    stress_values = np.zeros_like(N_values)

                    # S-N 커브 계산
                    for i, N in enumerate(N_values):
                        if N <= N_star:
                            stress_values[i] = delta_sigma_Rsk * (N_star / N)**(1/k1)
                        else:
                            stress_values[i] = delta_sigma_Rsk * (N_star / N)**(1/k2)

                    # 데이터프레임 생성
                    sn_curve_data = pd.DataFrame({
                        'Cycles (N)': N_values,
                        'Stress Range (MPa)': stress_values
                    })

                    # 차트 표시
                    # with st.container(border=True):
                    #     # S-N 커브 그래프
                    #     col1, col2 = st.columns([3, 1])
                        
                    #     with col1:
                    #         # 로그 스케일로 표시할 데이터 준비
                    #         log_data = pd.DataFrame({
                    #             'log N': log_N,
                    #             'log Stress': np.log10(stress_values)
                    #         })
                            
                    #         # 로그 스케일 차트 표시
                    #         st.line_chart(
                    #             log_data,
                    #             x='log N',
                    #             y='log Stress',
                    #             use_container_width=True
                    #         )
                    
                    #     with col2:
                    #         # 표 형태로 핵심 값 표시
                    #         st.markdown("**S-N Curve Parameters**")
                            
                    #         # 핵심 파라미터 정보
                    #         st.markdown(f"Steel type: **{steel_type}**")
                    #         st.markdown(f"ΔσRsk: **{delta_sigma_Rsk:.1f} MPa**")
                    #         st.markdown(f"k₁ (slope 1): **{k1}**")
                    #         st.markdown(f"k₂ (slope 2): **{k2}**")
                    #         st.markdown(f"N* (transition): **{N_star:.0e}** cycles")
                    if st.session_state.correction_factor_auto_calculate ==False:
                        pass
                    else:        
                        # Lambda1 계산 과정
                        lambda1 = st.session_state.get('lambda1', 0.0)
                        st.write(r"Correction factor of $\lambda_{s,1}$ = " + f"{lambda1:.3f}")
                        with st.container(border=True, height=120):
                            support_type = st.session_state.get('support_type_rail', 'Simply supported beams')
                            steel_type = st.session_state.get('steel_type', 'Straight and bent bars')
                            span_length = st.session_state.get('span_length', 35.0)
                            traffic_type = st.session_state.get('traffic_type_rail', 'Standard traffic')
                            
                            st.latex(r"\lambda_{s,1} = \begin{cases} & \text{Support Type: " + str(support_type) + r"} \\" + 
                                    r"      & \text{Steel Type: " + str(steel_type) + r"} \\" +
                                    r"      & \text{Span Length: " + str(span_length) + r"m ("r"between 2m and 20m liner interpolated)} \\" +
                                    r"      & \text{Traffic Type: " + str(traffic_type) + r"} \end{cases} = " + 
                                    f"{lambda1:.3f}")
                        
                        # Lambda2 계산 과정
                        lambda2 = st.session_state.get('lambda2', 0.0)
                        k2 = st.session_state.get('k2', 9.0)
                        vol = st.session_state.get('vol', 100000.0)
                        
                        st.write(r"Correction factor of $\lambda_{s,2}$ = " + f"{lambda2:.3f}")
                        with st.container(border=True, height=210):
                            st.latex(r"\lambda_{s,2} = \left(\frac{Vol}{25 \times 10^6}\right)^{1/k_2} = \left(\frac{" + 
                                    f"{vol:.0f}" + r"}{25 \times 10^6}\right)^{1/" + f"{k2:.1f}" + r"} = " + f"{lambda2:.3f}")
                            st.markdown(f"Steel type: **{steel_type}**")
                            st.markdown(f"Reference stress range (ΔσRsk): **{delta_sigma_Rsk} MPa**")
                            st.markdown(f"S-N curve slope (k₂): **{k2}**")
                            st.markdown("<small><i>Reference values according to EN 1992-2 Tables 6.3N and 6.4N</i></small>", unsafe_allow_html=True)
                        # Lambda3 계산 과정
                        lambda3 = st.session_state.get('lambda3', 0.0)
                        nyear = st.session_state.get('nyear', 50.0)
                        
                        st.write(r"Correction factor of $\lambda_{s,3}$ = " + f"{lambda3:.3f}")
                        with st.container(border=True, height=80):
                            st.latex(r"\lambda_{s,3} = \left(\frac{N_{years}}{100}\right)^{1/k_2} = \left(\frac{" + 
                                    f"{nyear:.0f}" + r"}{100}\right)^{1/" + f"{k2:.1f}" + r"} = " + f"{lambda3:.3f}")
                        
                        # Lambda4 계산 과정
                        lambda4 = st.session_state.get('lambda4', 0.0)
                        delta_sigma_1 = st.session_state.get('delta_sigma_1', 60.0)
                        delta_sigma_12 = st.session_state.get('delta_sigma_12', 70.0)
                        nc = st.session_state.get('nc', 2)
                        nt = st.session_state.get('nt', 1)
                        
                        
                        st.write(r"Correction factor of $\lambda_{s,4}$ = " + f"{lambda4:.3f}")
                        s1 = delta_sigma_1 / delta_sigma_12 if delta_sigma_12 != 0 else 0
                        s2 = s1  # 간소화 가정
                        n = 0.12
                        
                        st.markdown(
                            r"Ratio between dual and single-track under LM71 : $s_1 = \frac{\Delta\sigma_1}{\Delta\sigma_{1+2}} = \frac{" +
                            f"{delta_sigma_1:.1f}" + r"}{" + f"{delta_sigma_12:.1f}" + r"}$",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            "The simultaneity factor $n$ is fixed at 0.12 / assumed that $S_1 = S_2$",
                            unsafe_allow_html=True
                        )
                        with st.container(border=True, height=120):
                            # s1 계산

                            if s1 <= 0:
                                st.latex(r"\lambda_{s,4} = 1.0 \;\; \text{(only compression stresses)}")
                            else:
                                st.latex(r"\lambda_{s,4} = \left[n + (1-n) \cdot s_1^{k_2} + (1-n) \cdot s_2^{k_2} \right]^{1/k_2}")

                                st.latex(r"\lambda_{s,4} = \left[" + f"{n:.3f}" + r" + (1-" + f"{n:.3f}" + r") \cdot " +
                                        f"{s1:.3f}^{{{k2:.1f}}}" + r" + (1-" + f"{n:.3f}" + r") \cdot " +
                                        f"{s2:.3f}^{{{k2:.1f}}}" + r" \right]^{1/" + f"{k2:.1f}" + r"} = " + f"{lambda4:.3f}")
                    # Lambda4 계산 과정
                    lambda4 = st.session_state.get('lambda4', 0.0)
                    delta_sigma_1 = st.session_state.get('delta_sigma_1', 60.0)
                    delta_sigma_12 = st.session_state.get('delta_sigma_12', 70.0)
                    nc = st.session_state.get('nc', 2)
                    nt = st.session_state.get('nt', 1)     
                    lambda1 = st.session_state.get('lambda1', 0.0)
                    lambda2 = st.session_state.get('lambda2', 0.0)
                    lambda3 = st.session_state.get('lambda3', 0.0)
                    lambda4 = st.session_state.get('lambda4', 0.0)
                
                    # Lambda_s 총 보정계수 계산
                    lambda_s = st.session_state.get('lambda_s', 0.0)
                    st.write(r"Total correction factor $\lambda_{s}$ = " + f"{lambda_s:.3f}")
                    with st.container(border=True, height=60):
                        st.latex(r"\lambda_{s} = \lambda_{s,1} \cdot \lambda_{s,2} \cdot \lambda_{s,3} \cdot \lambda_{s,4} = " + 
                                f"{lambda1:.3f}" + r" \cdot " + f"{lambda2:.3f}" + r" \cdot " + 
                                f"{lambda3:.3f}" + r" \cdot " + f"{lambda4:.3f}" + r" = " + f"{lambda_s:.3f}")
                    

                    
                    delta_sigma_equ = st.session_state.get('delta_sigma_equ', 0.0)
                    section_type = st.session_state.get('section_type')
                                                # 균열 단면 계산식 표시
                    sigma_c_traz = st.session_state.get('sigma_c_traz', 0.0)
                    delta_s_sigma_ec = st.session_state.get('delta_s_sigma_ec', 0.0)
                    steel_type = st.session_state.get('steel_type', 'Straight and bent bars')
                    delta_s_sigma_equ = st.session_state.get('delta_s_sigma_equ', 0.0)
                    gamma_s_fat = st.session_state.get('factor_rsfat', 1.15)
                    gamma_F = st.session_state.get('factor_rf', 1.0)
                    gamma_Sd = st.session_state.get('factor_rsd', 1.0)
                    n_cables = st.session_state.get('n_steel', 1.0)
                    A_cable = st.session_state.get('A_steel', 98.7)
                    Msd = st.session_state.get('Msd', 0.0)
                    d = st.session_state.get('d', 0.0)
                    # right_side = delta_sigma_Rsk / gamma_s_fat
                    # left_side = gamma_F * gamma_Sd * delta_s_sigma_equ
                    
                    
                    # 판정 계산 표시
                    st.markdown("<h6><b>Fatigue Result Calculation</b></h6>", unsafe_allow_html=True)
                    # 등가 응력 범위 계산 표시
                    # st.write("Equivalent Stress Calculation")
                    if section_type != "Non-cracked section":
                        
                        st.markdown(
                            r"Equivalent stress : $\Delta\sigma_{s,equ} = \frac{M_{sd}}{d \cdot n_{cables} \cdot A_{cable}} \cdot \lambda_s$" +  
                            r" = $\frac{" + f"{Msd:.3f}" + r" \cdot 10^6}{" + f"{d:.3f}" + r" \cdot " + f"{n_cables}" + r" \cdot " + f"{A_cable:.3f}" + r"} \cdot " + f"{lambda_s:.3f}" + r"$" +  
                            r" = $" + f"{delta_sigma_equ:.3f}" + r"\text{ MPa}$",
                            unsafe_allow_html=True
                        )

                    else:
                        delta_sigma_1_1 =delta_sigma_1*Es/Ec
                        st.markdown(r"Stress : $\Delta\sigma_1 = \sigma_1 \cdot \frac{E_s}{E_c} = " + f"{delta_sigma_1:.3f}" + r" \cdot \frac{" + f"{Es:.0f}" + "}{" + f"{Ec:.0f}" + "} = " + f"{delta_sigma_1_1:.3f}" + r"\text{ MPa}$", unsafe_allow_html=True)
                        st.markdown(
                            r"Equivalent stress : $\Delta\sigma_{s,equ} = \lambda_s \cdot \Delta\sigma_1 = " + 
                            f"{lambda_s:.3f}" + r" \cdot " + f"{delta_sigma_1_1:.3f}" + r" = " + 
                            f"{delta_sigma_equ:.3f}" + r"\text{ MPa}$", 
                            unsafe_allow_html=True
                        )
                    delta_sigma_Rsk = st.session_state.get('delta_sigma_Rsk', 162.5)
                    st.markdown(
                        r"Design strength check: $\frac{\Delta\sigma_{Rsk}}{\gamma_{s,fat}} = \frac{" + 
                        f"{delta_sigma_Rsk:.3f}" + "}{" + f"{gamma_s_fat:.3f}" + "} = " + 
                        f"{right_side:.3f}" + r"\text{ MPa}$", 
                        unsafe_allow_html=True
                    )
                    with st.container(border=True, height=290):
                        # Main equation at the top
                        st.latex(r"\gamma_F \cdot \gamma_{Sd} \cdot \Delta\sigma_{s,equ} \leq \frac{\Delta\sigma_{Rsk}}{\gamma_{s,fat}}")
                        
                        # Horizontal comparison layout
                        col1, col2, col3, col4 = st.columns([10, 1, 9, 5], vertical_alignment="center")
                        with col1:
                            st.latex(r"\gamma_F \cdot \gamma_{Sd} \cdot \Delta\sigma_{s,equ} = " + f"{left_side:.3f}\\text{{ MPa}}")
                        with col2:
                            st.latex(r"\leq" if is_ok else r">")
                        with col3:
                            st.latex(r"\frac{\Delta\sigma_{Rsk}}{\gamma_{s,fat}} = " + f"{right_side:.3f}\\text{{ MPa}}")
                        with col4:
                            if is_ok:
                                st.markdown("<h5 style='color: green;'>OK</h5>", unsafe_allow_html=True)
                            else:
                                st.markdown("<h5 style='color: red;'>NG</h5>", unsafe_allow_html=True)
                        if section_type == "Non-cracked section":
                            st.markdown("**where :**")
                            st.markdown(rf"""
                            - $\gamma_F$ = {gamma_F} (Partial factor for fatigue actions)  
                            - $\gamma_{{Sd}}$ = {gamma_Sd} (Partial factor for uncertainty)  
                            - $\Delta\sigma_{{s,equ}}$ = {delta_sigma_equ:.3f} MPa (Equivalent stress range)  
                            - $\Delta\sigma_{{Rsk}}$ = {delta_sigma_Rsk:.3f} MPa (Characteristic fatigue strength)  
                            - $\gamma_{{s,fat}}$ = {gamma_s_fat:.3f} (Partial factor for fatigue of steel)
                            """)
                        else:
                            st.markdown("**where :**")
                            st.markdown(rf"""
                            - $\gamma_F = {gamma_F}$ (Partial factor for fatigue actions)  
                            - $\gamma_{{Sd}} = {gamma_Sd}$ (Partial factor for uncertainty)   
                            - $\Delta\sigma_{{s,equ}} = {delta_sigma_equ:.3f}$ MPa (Equivalent stress range)  
                            - $\Delta\sigma_{{Rsk}} = {delta_sigma_Rsk:.3f}$ MPa  
                            - $\gamma_{{s,fat}} = {gamma_s_fat:.3f}$
                            """)


            # 네비게이션 및 저장 버튼
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("<- Back", key="back_to_fatigue_settings", use_container_width=True):
                    add_tab_switch_button("Back", tabs[2])
            
            with col3:
                button_text = "Update" if is_edit_mode else "Save Result"
                if st.button(button_text, key="save_fatigue_result", use_container_width=True, type="primary"):
                    # 계산 수행 (아직 수행되지 않은 경우)
                    # if 'is_ok' not in st.session_state:
                    #     if not calculate_results():
                    #         st.toast("Please calculate")
                    #         return
                    update_temp_from_input_multi(['section_type', 'is_cracked_section', 'fctd', 'fb'])
                    update_temp_from_input_multi([
                        'span_length', 'Es', 'Ec', 'd',
                        'crack_option', 'section_type', 'is_cracked_section', 'fctd','widget_crack_option',
                        'fb', 'delta_sigma_1', 'delta_sigma_12', 'Msd'
                    ])
                    update_temp_from_input_multi([
                        'steel_type', 'A_steel', 'n_steel', 'nc',
                        'traffic_type_rail', 'vol', 'support_type_rail'
                    ])
                    update_temp_from_input_multi([
                        'lambda1', 'lambda2', 'lambda3', 'lambda4',
                        'lambda_s', 'correction_factor_auto_calculate'
                    ])

                    # temp_result_df 업데이트
                    if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
                        # 케이스 정보 업데이트
                        st.session_state.temp_result_df.at[0, 'case_id'] = st.session_state.case_name
                        st.session_state.temp_result_df.at[0, 'case_method'] = "Reinforcing Steel(Rail_DES)"
                        
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



''' 이코드의 입력값들
Reinforcing Steel(DESM) : Railway

1page  
- span_length  
- section_type  
- steel_type  
- Es  
- Ec  
- n_steel  
- A_steel  
- d  
- delta_sigma_1  

2page  
- nc  
- traffic_type_rail  
- vol  
- support_type_rail  

3page  
- delta_sigma_1  
- delta_sigma_12  
- lambda1  
- lambda2  
- lambda3  
- lambda4  
- lambda_s  


'''