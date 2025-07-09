# fatigue_concrete_desm_road_ui.py

import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import math
from projects.concrete_fatigue_analysis_ntc2018.session_manager import *
from streamlit_extras.switch_page_button import switch_page
from projects.concrete_fatigue_analysis_ntc2018.calc.road_concrete_lambda import *
from projects.concrete_fatigue_analysis_ntc2018.calc.shear_resistance import calculate_shear_resistance  # 추가
import re

from projects.concrete_fatigue_analysis_ntc2018.utils.navigator import back_to_fatigue_case

# 세션 초기화


initialize_session()
# 모달 다이얼로그 가져오기
import_dialogs = SessionManager.initialize_import_dialogs() if 'SessionManager' in globals() else None
civil_stress_import = import_dialogs['road_noncracked_stress'] if 'road_noncracked_stress' in import_dialogs else None
civil_stress_import2 = import_dialogs['road_cracked_moment'] if 'road_cracked_moment' in import_dialogs else None
st.session_state.error_condition=False

def calculate_resistance_axial(tensilstress):
    """fb 계산 함수 - 간소화 버전"""
    
    # 요소 정보
    get_Elem = st.session_state.temp_result_df.at[0, 'element_number_sctraz']
    get_ij = st.session_state.temp_result_df.at[0, 'element_part_sctraz']

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

    return None
def calculate_delta_sigma_equ():
    """결과 계산 등가 응력 범위 계산 - 균열/비균열 단면에 따라 다르게 계산"""
    
    try:
        section_type = st.session_state.get('section_type', 'Non-cracked section')
        lambda_s = st.session_state.get('lambda_s', 1.0)
        
        if section_type == "Non-cracked section":
            # 비균열 단면: σc,traz * λs
            sigma_c_traz = st.session_state.get('sctraz', 0.0)
            Es=st.session_state.Es
            Ec=st.session_state.Ec
            delta_s_sigma_ec = sigma_c_traz * Es/Ec
            steel_type = st.session_state.get('steel_type', 'Straight and bent bars')
            delta_sigma_Rsk = get_stress_range_road(steel_type)
            delta_s_sigma_equ = delta_s_sigma_ec * lambda_s
            gamma_s_fat = st.session_state.get('factor_rsfat', 1.15)
            gamma_F = st.session_state.get('factor_rf', 1.0)
            gamma_Sd = st.session_state.get('factor_rsd', 1.0)
            right_side = delta_sigma_Rsk / gamma_s_fat
            left_side = gamma_F * gamma_Sd * delta_s_sigma_equ
            # left_side가 16이고 right_side가 더 큰 수라면 is_ok는 True가 되어야 함
            # 디버깅을 위해 값 출력

            if float(left_side) <= float(right_side):
                is_ok = "OK"
            else:
                is_ok = "NG"

            
            # 계산 과정 저장stress_left
            st.session_state.sigma_c_traz = sigma_c_traz
            st.session_state.left_side = left_side
            st.session_state.stress_left = left_side
            st.session_state.right_side = right_side
            st.session_state.stress_right = right_side
            st.session_state.is_ok = is_ok
            st.session_state.calculation_method = "Non-cracked section"
            
        else:  # Cracked section
            # 균열 단면: (Msd * 1000) / (d * n_cables * A_cable) * λs
            Msd = st.session_state.get('Msd', 0.0)
            d = st.session_state.get('d', 2700.0) / 1000  # mm to m 변환
            n_cables = st.session_state.get('n_steel', 33)
            A_cable = st.session_state.get('A_steel', 98.7)
            
            delta_s_sigma_ec = (Msd * 1000) / (d * n_cables * A_cable)
            delta_s_sigma_equ = delta_s_sigma_ec * lambda_s
            steel_type = st.session_state.get('steel_type', 'Straight and bent bars')
            delta_sigma_Rsk = get_stress_range_road(steel_type)
            gamma_s_fat = st.session_state.get('factor_rsfat', 1.15)
            gamma_F = st.session_state.get('factor_rf', 1.0)
            gamma_Sd = st.session_state.get('factor_rsd', 1.0)
            right_side = delta_sigma_Rsk / gamma_s_fat
            left_side = gamma_F * gamma_Sd * delta_s_sigma_equ
            stress_left = left_side
            stress_right = right_side
            if float(left_side) <= float(right_side):
                is_ok = "OK"
            else:
                is_ok = "NG"
            # 계산 과정 저장
            st.session_state.delta_s_sigma_ec = delta_s_sigma_ec
            st.session_state.Msd = Msd
            st.session_state.d_m = d  # 미터 단위로 저장
            st.session_state.n_cables = n_cables
            st.session_state.A_cable = A_cable
            st.session_state.calculation_method = "Cracked section"
            st.session_state.is_ok = is_ok
            st.session_state.left_side = left_side
            st.session_state.right_side = right_side
            st.session_state.stress_left = stress_left
            st.session_state.stress_right = stress_right
        # 공통 저장
        st.session_state.delta_s_sigma_equ = delta_s_sigma_equ
        update_temp_from_input_multi([
            'delta_sigma_Rsk', 'gamma_F', 'gamma_Sd', 'gamma_fat',
            'left_side', 'right_side', 'is_ok', 'discriminant','delta_s_sigma_equ','Msd','d','n_cables','A_cable','stress_left','stress_right'
        ])
        return delta_s_sigma_equ
        
    except Exception as e:
        st.session_state.error_condition=True
        return 0.0


def fatigue_reinforcedsteel_desm_road_ui_page():
    """도로교량 피로 계산을 위한 UI 용 클래스"""
    st.session_state.Fatigue_method = "Reinforcing Steel(Road_DES)"
    @staticmethod
    def calculate_lambda_s_values():
        """모든 lambda_s 계수 계산"""
        try:
            # 계산에 필요한 데이터 수집
            case_id = st.session_state.case_name
            steel_type = st.session_state.steel_type
            support_type = st.session_state.support_type_road
            traffic_type = st.session_state.traffic_type_road
            span_length = st.session_state.span_length
            vol = st.session_state.vol
            nyear = st.session_state.nyear
            nc = st.session_state.nc
            nt = st.session_state.nt

            # 입력 데이터 검증
            if not all([case_id, steel_type, support_type, span_length, vol, nyear]):
                st.error("Required input values are missing.")
                return 1.0
            
            # 계산용 임시 데이터프레임 생성
            if 'temp_result_df' not in st.session_state or st.session_state.temp_result_df.empty:
                st.session_state.temp_result_df = pd.DataFrame([{"case_id": case_id}])
            
            temp_df = st.session_state.temp_result_df.copy()
            
            # 강재 유형 매핑
            std_steel_type = map_steel_type_to_table_key(steel_type)
            
            # k2 값 가져오기
            k2 = get_k2_value_road(steel_type)
            
            # lambda1 계산
            # get_lambda1_road(support_type, steel_type, span_length, traffic_type="Standard traffic")
            lambda1 = get_lambda1_road(
                support_type=support_type, 
                steel_type=steel_type, 
                span_length=span_length, 
                traffic_type=traffic_type
            )
            # lambda1 계산 과정 추적
            print(f"""
            λs,1 계산 과정:
            - 지지 조건: {support_type}
            - 강재 유형: {steel_type}
            - 경간 길이: {span_length} m
            - 교통 하중: {traffic_type}
            - 계산된 λs,1: {lambda1:.3f}
            """)
            # lambda2 계산
            lambda2, Q_bar = calculate_lambda2_road(
                vol=vol, 
                steel_type=steel_type, 
                traffic_type=traffic_type
            )
            
            # lambda3 계산
            lambda3 = calculate_lambda3_road(
                nyear=nyear, 
                k2=k2,
            )
            

            # lambda4 계산
            # 여러 차선의 경우 차선별 통과 트럭 수를 리스트로 전달
            lambda4 = calculate_lambda4_road(
                n_obs_list=[nc],  # 단일 차선 또는 대표 차선 가정
                k2=k2,
            )
        
            pie_fat = st.session_state.pie_fat

            # 총 람다 계수
            lambda_s = lambda1 * lambda2 * lambda3 * lambda4 *pie_fat
            
            # 세션 상태에 저장
            st.session_state.Q_bar = Q_bar
            st.session_state.lambda1 = lambda1
            st.session_state.lambda2 = lambda2
            st.session_state.lambda3 = lambda3
            st.session_state.lambda4 = lambda4
            st.session_state.lambda_s = lambda_s
            st.session_state.k2 = k2
            
            # temp_result_df 업데이트
            update_temp_from_input_multi([
                'pie_fat','lambda1', 'lambda2', 'lambda3', 'lambda4', 'lambda_s', 'k2', 'Q_bar'
            ])
            
            return lambda_s
            
        except Exception as e:
            st.error(f"Lambda 계수 계산 중 오류 발생: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return 1.0



    def save_fatigue_case():
        """피로 케이스 저장 함수"""
        case_id = st.session_state.get('case_name', 'New Case')
        
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
            st.session_state.temp_result_df.at[0, 'case_method'] = "Reinforcing Steel(Road_DES)"
            
            # 판정값 저장 (있는 경우에만)
            if 'is_ok' in st.session_state:
                st.session_state.temp_result_df.at[0, 'is_ok'] = st.session_state.is_ok
            
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
        st.markdown(f"<h5><b>[Edit]Reinforcing Steel(DESM) : Road:{st.session_state.get('fatigue_case_name', '')}</b></h5>", unsafe_allow_html=True)
    else:
        st.markdown("<h5><b>Reinforcing Steel(DESM) : Road</b></h5>", unsafe_allow_html=True)
    notyetchecked = False    
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
        with st.container(border=False, height=800):
            st.markdown("<h6><b>Fatigue Settings</b></h6>", unsafe_allow_html=True)
            # 입력 필드에 현재 세션 상태의 값을 직접 사용
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
                # 스팬 길이
                if st.session_state.bridge_type == "Road":
                    # 강재 타입 선택
                    support_type = st.selectbox(
                        "Structure Type",
                        ["Intermediate Support Area", "Continuous Beam", "Single Span Beam", "Carriageway Slab"],
                        index=0,
                        key="support_type_road",
                        on_change=update_temp_from_input,
                        args=("support_type_road",)
                    )
                if math.isnan(st.session_state.get('fck', 20)) or st.session_state.get('fck') is None:
                    st.session_state.fck = st.session_state.get('get_fck', 20)
                fck = st.number_input(r"Concrete compressive strength, $f_{ck}$ [MPa]", 
                                value=st.session_state.get('fck',20),
                                key='widget_fck', 
                                on_change=update_temp_from_input, 
                                args=('widget_fck','fck'),)

                # 강재 탄성계수
                Es = st.number_input(
                    r"Steel elastic modulus, $E_s$ [MPa]", 
                    value=st.session_state.get('Es', 1.95e5),
                    key='Es', 
                    on_change=update_temp_from_input, 
                    args=('Es',)
                )
            with col2:
                span_length = st.number_input(r"Span length (m), $L$", 
                                    value=st.session_state.get('span_length', 0.00),
                                    key='span_length', 
                                    on_change=update_temp_from_input, 
                                    args=('span_length',))
                # 유효높이
                d = st.number_input(
                    r"Effective height, $d$ [mm]", 
                    value=st.session_state.get('d', 0.00),
                    key='d', 
                    on_change=update_temp_from_input, 
                    args=('d',)
                )

                # 콘크리트 탄성계수
                Ec = st.number_input(
                    r"Concrete elastic modulus, $E_c$ [MPa]", 
                    value=st.session_state.get('Ec', 3.7e4),
                    key='Ec', 
                    on_change=update_temp_from_input, 
                    args=('Ec',)
                )
            # 균열 비균열 단면 상태 
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h6><b>Crack State Detection</b></h6>", unsafe_allow_html=True)
            with col2:
                use_midas = st.session_state.get('manual_input2', True)

                # value 값을 미리 계산
                if use_midas == False:
                    toggle_value = False
                else:
                    toggle_value = st.session_state.get('crack_option', False)
                st.session_state.setdefault("crack_option", True)

                crack_option = st.toggle("Crack State: Manual/Auto",
                                    value=toggle_value,
                                    key="widget_crack_option",
                                    disabled=not use_midas,
                                    help="Automatic crack state detection is only available when importing loads from MIDAS model",
                                    on_change=update_temp_from_input,
                                    args=("widget_crack_option", "crack_option")
                                    )
                
            get_fck =  fck

            rc = st.session_state.factor_rcfat

            # fctm 계산
            fctm = 0.30 * pow(get_fck, 2/3) if get_fck <= 50 else 2.12 * math.log(1 + get_fck/10)
            fctk005 = 0.7 * fctm
            fctd = fctk005 / rc

            try:    
                if crack_option == False:
                    # 수동 모드
                    section_type = st.selectbox(
                        "Section Type",
                        ["Non-cracked section", "Cracked section"],
                        index=0,
                        key="section_type",
                        on_change=update_temp_from_input,
                        args=("section_type",)
                    )
                    if st.session_state.section_type == "Non-cracked section" or st.session_state.section_type =='' :
                        expander = True
                    else:
                        expander = False
                else:
                    # pass
                    # 자동 모드
                    # 계산 버튼
                    if st.session_state.get('sctraz') == 0:
                        expander = True
                    else:
                        expander = False
                    if st.button("Calculate Crack State", key="calculate_crack_state", use_container_width=True):
                        try:
                            axial_stress =  st.session_state.get('sctraz')
                            fb = calculate_resistance_axial(axial_stress)
                            st.session_state.fb = fb
                                # temp_result_df에도 저장
                            update_temp_from_input_multi(['section_type', 'is_cracked_section', 'fctd', 'fb'])
                                
                            #     st.success("Crack state calculation completed!")
                            # else:
                            #     st.error("Failed to calculate crack state. Please check your input data.")
                            # st.rerun()
                        except Exception as e:
                            print(e)
                            st.toast(e)
                            st.error(f"Error during crack state calculation: Please load load from below.")
                            # Initialize exception_exist flag
                            exception_exist = True

                        fb = st.session_state.get('fb', 0)
                        st.session_state.fctd = fctd

                        if 'fb' in st.session_state and 'fctd' in st.session_state and st.session_state.get('fb', 0) != 0:
                            if st.session_state.fb > st.session_state.fctd:
                                # st.success(f"Cracked section ($\\sigma_{{c,\\mathrm{{traz}}}}$ ($f_b$) = {fb:.2f} MPa > $f_{{ctd}}$ = {fctd:.2f} MPa)")
                                # st.session_state.section_type = "Cracked section"
                                is_cracked_section = True
                                update_temp_from_input_multi(['section_type', 'is_cracked_section', 'fctd', 'fb'])
                            else:
                                # st.success(f"Non-cracked section ($\\sigma_{{c,\\mathrm{{traz}}}}$ ($f_b$) = {fb:.2f} MPa ≤ $f_{{ctd}}$ = {fctd:.2f} MPa)")
                                # st.session_state.section_type = "Non-cracked section"  
                                is_cracked_section = False    
                                update_temp_from_input_multi(['section_type', 'is_cracked_section', 'fctd', 'fb'])   
                        notyetchecked = False        

                    else:
                        pass

            except Exception as e: 
                print(e)
                st.toast(e)
                toggle_value = True     
                expander = True     
            is_cracked_section = st.session_state.get('section_type', 'Non-cracked section') == 'Cracked section'
            if 'fb' in st.session_state and 'fctd' in st.session_state and st.session_state.get('fb', 0) != 0 and crack_option == True:
                if st.session_state.fb > st.session_state.fctd:
                    st.success(f"Cracked section ($\\sigma_{{c,\\mathrm{{traz}}}}$ ($f_b$) = {st.session_state.get('fb', 0):.2f} MPa > $f_{{ctd}}$ = {fctd:.2f} MPa)")
                    is_cracked_section = True
                    st.session_state.section_type = "Cracked section"
                else:
                    st.success(f"Non-cracked section ($\\sigma_{{c,\\mathrm{{traz}}}}$ ($f_b$) = {fb:.2f} MPa ≤ $f_{{ctd}}$ = {fctd:.2f} MPa)") 
                    st.session_state.section_type = "Non-cracked section"
                    is_cracked_section = False           
            elif  crack_option == True    :
                   
                st.info("Please check section shear resistance by clicking 'Calculate shear resistance' button")
            else:
                pass
            if is_cracked_section:
                expandertitle = "Crack State Detection Load"
            else:
                expandertitle = "Non-cracked Section Input"

            with st.expander(expandertitle, expanded=expander):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<h6><b>Import Fatigue Load</b></h6>", unsafe_allow_html=True)
                with col2:
                # 하중불러오기
                    if is_cracked_section:
                        pass
                    else:
                        use_midas = st.toggle("Import Fatigue Load From Midas NX", key="manual_input2", value=True)
                with st.container(border=True):
                    if is_cracked_section:
                        col1, col2,  = st.columns(2, vertical_alignment="bottom")
                        with col1:
                            if st.button("Import", use_container_width=True, key="from_midas_nx" ):
                                if civil_stress_import:
                                    civil_stress_import("Import")
                        
                        with col2:
                            st.number_input(r"Tensile stress in concrete, $\sigma_{c,\mathrm{traz}}$ [MPa]",
                                        value=float(st.session_state.get('sctraz', 2.28)),
                                        step=0.5, 
                                        key="widget_sctraz",
                                        on_change=update_temp_from_input,
                                        args=("widget_sctraz", "sctraz"))
                            
                            if 'widget_sctraz' in st.session_state:
                                st.session_state.sctraz = st.session_state.widget_sctraz

                    else:
                        col1, col2,  = st.columns(2, vertical_alignment="bottom")
                        with col1:
                            if st.button("Import", use_container_width=True, key="from_midas_nx", 
                                        disabled=not use_midas):
                                if civil_stress_import:
                                    civil_stress_import("Import")
                        
                        with col2:
                            st.number_input(r"Tensile stress in concrete, $\sigma_{c,\mathrm{traz}}$ [MPa]",
                                        value=float(st.session_state.get('sctraz', 2.28)),
                                        step=0.5, 
                                        key="widget_sctraz",
                                        on_change=update_temp_from_input,
                                        args=("widget_sctraz", "sctraz"),
                                        disabled=use_midas)
                            
                            if not use_midas and 'widget_sctraz' in st.session_state:
                                st.session_state.sctraz = st.session_state.widget_sctraz


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

        def has_validation_errors1():
            # 필수 입력값 체크
            if st.session_state.get('case_name') == "":
                return True
            if st.session_state.get('d', 0) <= 0:
                return True
            if st.session_state.get('span_length', 0) == 0:
                return True
            if st.session_state.get('Es', 0) == 0:
                return True           
            if st.session_state.get('Ec', 0) == 0:
                return True  
            if st.session_state.get('fck', 0) == 0: 
                return True
            if st.session_state.section_type == "":
                return True
            if notyetchecked == True:
                return True
            if is_cracked_section:
                if abs(st.session_state.get('Msd', 0)) == 0:
                    return True
            else:
                if abs(st.session_state.get('sctraz', 0)) == 0:
                    return True

            return False
            # 유효성 검사 실패 시 Next 버튼 비활성화

        # 네비게이션 버튼
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- back", use_container_width=True):
                back_to_fatigue_case()
        with col3:
            validation_errors1 = has_validation_errors1()
            if  validation_errors1:
                if st.button("Next →", use_container_width=True, key="next_button_with_error"):
                    if st.session_state.get('case_name') == "":
                        st.toast("Please enter case name", icon="⚠️")
                    if abs(st.session_state.get('fck', 0)) == 0:
                        st.toast("Please enter concrete compressive strength($f_{ck}$).", icon="⚠️")
                    if abs(st.session_state.get('d', 0)) == 0:
                        st.toast("Please enter effective height value($d$).", icon="⚠️")
                    if abs(st.session_state.get('span_length', 0)) == 0:
                        st.toast("Please enter span length($L$).", icon="⚠️")
                    if abs(st.session_state.get('Es', 0)) == 0:
                        st.toast("Please enter steel elastic modulus($E_s$).", icon="⚠️")
                    if abs(st.session_state.get('Ec', 0)) == 0:
                        st.toast("Please enter concrete elastic modulus($E_c$).", icon="⚠️")
                    if st.session_state.section_type == "":
                        st.toast("Specify whether the section is cracked or uncracked.", icon="⚠️")
                    if notyetchecked == True:
                        st.toast("Please check crack state", icon="⚠️")
                    if is_cracked_section:
                        if abs(st.session_state.get('Msd', 0)) == 0:
                            st.toast("Please enter moment value($Msd$).", icon="⚠️")
                    else:
                        if abs(st.session_state.get('sctraz', 0)) == 0:
                            st.toast("Please enter fatigue stress values.", icon="⚠️")

            else:
                if st.button("Next   →", use_container_width=True,key="fatigue_settings_next",      disabled=has_validation_errors1(), type="primary"):
                    update_temp_from_input_multi([
                        'case_name', 'support_type_road', 'fck', 'Es',
                        'span_length', 'd', 'Ec', 'crack_option',
                        'section_type', 'sctraz', 'Msd', 'manual_input2',
                        'manual_input', 'fb', 'fctd'
                    ])
                    add_tab_switch_button("Next", tabs[1])
    
    def fatigue_tab(method, back_tab, next_tab=None):
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back", key=f"back_{method}"):
                add_tab_switch_button("Back", back_tab)
        with col2:
            pass
        with col3:
            if next_tab and st.button("Next →", key=f"next_{method}"):
                add_tab_switch_button("Next", next_tab)



    with tab2:
        with st.container(border=False, height=800):
            st.markdown("<h6><b>Reinforced Steel Properties</b></h6>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                steel_type = st.selectbox(
                    "Steel Type",
                    [
                        "Straight and bent bars",
                        "Welded bars and wire fabrics",
                        "Splicing devices (reinforcing)",
                        "Pre-tensioning",
                        "Post-tensioning[Single strands in plastic ducts]",
                        "Post-tensioning[Straight tendons or curved in plastic ducts]",
                        "Post-tensioning[Curved tendons in steel ducts]",
                        "Post-tensioning[Splicing devices]",
                    ],
                    index=0,
                    key="steel_type",
                    on_change=update_temp_from_input,
                    args=("steel_type",)
                )
    
            with col2:
                st.number_input("Resisting stress range, "+ f"ΔσRsk [MPa]",
                                value=get_stress_range_road(steel_type),
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
                    min_value=0.0, 
                    value=float(st.session_state.get('nc', 2.0)), 
                    step=1.0, 
                    key="widget_nc",
                    on_change=update_temp_from_input,
                    args=("widget_nc", "nc")
                )

                
                if st.session_state.bridge_type == "Road":
                    st.selectbox(
                        "Traffic Type",
                        ["Long distance", "Medium distance", "Local traffic"],
                        index=0,
                        key="traffic_type_road",
                        on_change=update_temp_from_input,
                        args=("traffic_type_road", "traffic_type_road")
                    )


                
            with col2:          
                st.session_state.nt = 1
                st.number_input(
                    r"Number of loaded tracks, $N_{t}$", 
                    value=int(st.session_state.get('nt', 1)), 
                    key="widget_nt",
                    on_change=update_temp_from_input,
                    args=("widget_nt", "nt")
                )

                #  for pie factor
                roughness_category=st.selectbox(
                    "Pavement Roughness",
                    ["Good", "Medium"],
                    index=1,
                    key="pavement_roughness", 
                    on_change=update_temp_from_input,
                    args=("pavement_roughness", "pavement_roughness")
                )
                # 카테고리에 따른 자동 계산값 설정
                roughness_values = {
                    "Good": 1.2,
                    "Medium": 1.4,
                }
                
                if roughness_category:
                    # 선택된 카테고리에 따라 자동으로 vol 값 설정
                    st.session_state.pie_fat = roughness_values.get(roughness_category, 1.4)
             # 볼륨 교통량 자동 계산 토글--------------------------------------------------------------
            vol_auto_calc = st.toggle(
                "Auto Calculate Volume", 
                key="vol_auto_calculate", 
                value=True, 
                on_change=update_temp_from_input, 
                args=("vol_auto_calculate",)
            )

            col1, col2 = st.columns(2)      

            with col1:
                category_options = [
                    "Category 1: High flow motorways (2.0×10⁶)",
                    "Category 2: Medium flow motorways (0.5×10⁶)", 
                    "Category 3: Main roads, low flow (0.125×10⁶)",
                    "Category 4: Local roads, low flow (0.05×10⁶)"
                ]
                default_idx = category_options.index(st.session_state.get('traffic_category_vol', category_options[1]))
                traffic_category_vol = st.selectbox(
                    "Road Traffic Category (EN 1992-2 Table 4.5(n))",
                    category_options,
                    index=default_idx,
                    key="traffic_category_vol_widget",
                    on_change=update_temp_from_input,
                    args=("traffic_category_vol_widget", "traffic_category_vol"),
                    disabled=not vol_auto_calc
                )
                
                # 카테고리에 따른 자동 계산값 설정
                category_values = {
                    "Category 1: High flow motorways (2.0×10⁶)": 2000000,
                    "Category 2: Medium flow motorways (0.5×10⁶)": 500000,
                    "Category 3: Main roads, low flow (0.125×10⁶)": 125000,
                    "Category 4: Local roads, low flow (0.05×10⁶)": 50000
                }
                
                if vol_auto_calc:
                    # 선택된 카테고리에 따라 자동으로 vol 값 설정
                    selected_vol = category_values.get(traffic_category_vol, 500000)
                    st.session_state.vol = selected_vol
                    # temp_result_df에도 저장
                    update_temp_from_input('vol')
                else:
                    # 수동 모드일 때는 현재 세션 값 사용
                    selected_vol = st.session_state.get('vol', 500000)

            with col2:
                if vol_auto_calc:
                    # 계산된 값 표시 (비활성화됨)
                    st.number_input(
                        r"Heavy vehicles per year, $N_{obs}$", 
                        min_value=0.0, 
                        value=float(selected_vol),
                        step=1000.0, 
                        format="%.0f",
                        key="widget_vol_display",
                        disabled=True
                    )
                else:
                    # 수동 입력 모드
                    st.number_input(
                        r"Heavy vehicles per year, $N_{obs}$", 
                        min_value=0.0, 
                        value=float(st.session_state.get('vol', 500000)),
                        step=1000.0, 
                        format="%.0f",
                        key="widget_vol_manual",
                        on_change=update_temp_from_input,
                        args=("widget_vol_manual", "vol")
                    )

            # 교통량 끝--------------------------------------------------------------
            # 유효성 검사 실패 여부 확인 함수
            def has_validation_errors2():
                if st.session_state.section_type == "Cracked section":
                    # 필수 입력값 체크
                    if abs(st.session_state.get('Msd', 0)) == 0 and abs(st.session_state.get('Msd', 0)) == 0:
                        st.toast("Please select moment value.")
                        return True
                else:
                    pass   
                if st.session_state.get('nc', 0) == 0:
                    st.toast("Please enter number of cycles.")
                    return True
                if st.session_state.get('nt', 0) == 0:
                    return True
                if st.session_state.get('vol', 0) == 0:
                    return True
                support_type = st.session_state.get('support_type_road', '')
                steel_type = st.session_state.get('steel_type', '')  # 실제 선택된 steel type
                current_span = st.session_state.get('span_length', 35.0)
                
                # steel_type_map을 사용해서 lambda1_table의 키로 변환
                steel_type_map = {
                    "Straight and bent bars": "Rebar, Pre/Post Tension",
                    "Welded bars and wire fabrics": "Rebar, Pre/Post Tension",
                    "Splicing devices (reinforcing)": "Splicing Devices",
                    "Pre-tensioning": "Rebar, Pre/Post Tension",
                    "Post-tensioning[Single strands in plastic ducts]": "Rebar, Pre/Post Tension",
                    "Post-tensioning[Straight tendons or curved in plastic ducts]": "Rebar, Pre/Post Tension",
                    "Post-tensioning[Curved tendons in steel ducts]": "Curved Tendons in Steel Ducts",
                    "Post-tensioning[Splicing devices]": "Splicing Devices",
                    "Shear reinforcement": "Shear Reinforcement"
                }
                
                # 매핑된 reinforcement type 가져오기
                mapped_type = steel_type_map.get(steel_type, "")
                
                # 스팬 길이 범위 체크
                min_span, max_span = None, None
                
                if support_type == "Intermediate Support Area":
                    # Intermediate Support Area는 모든 케이스가 (10, 90) 범위
                    min_span, max_span = 10, 90
                    
                elif support_type == "Continuous Beam":
                    if mapped_type == "Splicing Devices":
                        min_span, max_span = 10, 90  # 1a: (10, 46) + (46, 90) = (10, 90)
                    elif mapped_type == "Curved Tendons in Steel Ducts":
                        min_span, max_span = 10, 90  # 2a: (10, 52.75) + (52.75, 90) = (10, 90)
                    elif mapped_type in ["Rebar, Pre/Post Tension", "Shear Reinforcement"]:
                        min_span, max_span = 10, 90  # 3a, 4a: (10, 40) + (40, 90) = (10, 90)
                    else:
                        min_span, max_span = 10, 90  # 기본값
                        
                elif support_type == "Single Span Beam":
                    if mapped_type == "Splicing Devices":
                        min_span, max_span = 10, 51  # 1b: (10, 51)
                    elif mapped_type == "Curved Tendons in Steel Ducts":
                        min_span, max_span = 10, 50  # 2b: (10, 50)
                    elif mapped_type == "Rebar, Pre/Post Tension":
                        min_span, max_span = 10, 50  # 3b: (10, 50)
                    elif mapped_type == "Shear Reinforcement":
                        min_span, max_span = 10, 90  # 4b: (10, 40) + (40, 90) = (10, 90)
                    else:
                        min_span, max_span = 10, 50  # 기본값
                        
                elif support_type == "Carriageway Slab":
                    if mapped_type == "Curved Tendons in Steel Ducts":
                        min_span, max_span = 2.54, 9.50  # 2c: (2.53829, 9.495417)
                    elif mapped_type in ["Rebar, Pre/Post Tension", "Shear Reinforcement"]:
                        min_span, max_span = 2.84, 9.50  # 3c, 4c: (2.842679, 9.495417)
                    else:
                        min_span, max_span = 2.5, 9.5  # 기본값
                
                # 범위 체크
                if min_span is not None and max_span is not None:
                    if not (min_span <= current_span <= max_span):
                        st.toast(f"Span length must be between {min_span}m and {max_span}m for {support_type} (current: {current_span}m)[UNI ENV 1992-2 Figure A106.2]", icon="⚠️")
                        return True
                    return False
                else:
                    if abs(st.session_state.get('sctraz', 0)) == 0:
                        st.toast("Please select fatigue stress values.")
                        return True
                    return False
                return False
        validation_errors2 = has_validation_errors2()
        # 네비게이션 버튼
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- back", use_container_width=True, key="fatigue_load_back"):
                add_tab_switch_button("Back", tabs[0])  # tabs[0]으로 변경
        with col3:
            if  validation_errors2:
                if st.button("Next →", use_container_width=True, key="next_button_with_error2"):
                    if abs(st.session_state.get('nc', 0)) == 0:
                        st.toast("Please enter number of loaded tracks.", icon="⚠️")
                    if abs(st.session_state.get('nt', 0)) == 0:
                        st.toast("Please enter number of loaded tracks.", icon="⚠️")
                    if abs(st.session_state.get('vol', 0)) == 0:
                        st.toast("Please enter volume.", icon="⚠️")   
            else:
                if st.button("Next   →", use_container_width=True, key="fatigue_load_next2", type="primary",
                    disabled = validation_errors2):
                    update_temp_from_input_multi([
                        'steel_type', 'A_steel', 'n_steel', 'nc',
                        'nt', 'pavement_roughness', 'vol_auto_calculate', 'traffic_category_vol',
                        'vol', 'traffic_type_road', 'span_length', 'support_type_road'
                    ])
                    add_tab_switch_button("Next", tabs[2])


    # 두번째 탭 - Correction Factor
# 두번째 탭 - Correction Factor
    with tab3:
        with st.container(border=False, height=800):
            st.markdown("<h6><b>Correction Factor</b></h6>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.toggle("Correction Factor Auto Calculate",
                    value=st.session_state.get('correction_factor_auto_calculate', True), 
                    key="correction_factor_auto_calculate",  
                    on_change=update_temp_from_input,
                    args=("correction_factor_auto_calculate", )
                    )

            with col2:
                if st.button("Calculate Correction Factors", use_container_width=True, 
                            key="road_calculate_correction_factors",
                            disabled=not st.session_state.correction_factor_auto_calculate):
                    
                    # 계산 함수 호출
                    lambda_s = calculate_lambda_s_values()
                    st.toast(f"Lambda coefficient calculation completed: λs = {lambda_s:.3f}", icon="✅")
                    calculate_delta_sigma_equ()



            col1, col2 = st.columns(2, vertical_alignment="bottom")
            with col1:

                st.number_input(
                    r"$\phi_{fat}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('pie_fat', 0.00)),
                    step=0.05, 
                    key="widget_pie_fat",
                    on_change=update_temp_from_input,
                    args=("widget_pie_fat", "pie_fat"),
                    disabled=st.session_state.correction_factor_auto_calculate
                )
                
                # Lambda2
                st.number_input(
                    r"$\lambda_{s2}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('lambda2', 0.00)),
                    step=0.05, 
                    key="widget_lambda2",
                    on_change=update_temp_from_input,
                    args=("widget_lambda2", "lambda2"),
                    disabled=st.session_state.correction_factor_auto_calculate
                )
                
                
                # Lambda4
                st.number_input(
                    r"$\lambda_{s4}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('lambda4', 0.00)),
                    step=0.05, 
                    key="widget_lambda4",
                    on_change=update_temp_from_input,
                    args=("widget_lambda4", "lambda4"),
                    disabled=st.session_state.correction_factor_auto_calculate
                )

                
            with col2:
                # Lambda1
                st.number_input(
                    r"$\lambda_{s1}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('lambda1', 0.00)),
                    step=0.05, 
                    key="widget_lambda1",
                    on_change=update_temp_from_input,
                    args=("widget_lambda1", "lambda1"),
                    disabled=st.session_state.correction_factor_auto_calculate
            ) 
                # Lambda3
                st.number_input(
                    r"$\lambda_{s3}$", 
                    min_value=0.0, 
                    value=float(st.session_state.get('lambda3', 0.00)),
                    step=0.05, 
                    key="widget_lambda3",
                    on_change=update_temp_from_input,
                    args=("widget_lambda3", "lambda3"),
                    disabled=st.session_state.correction_factor_auto_calculate
                )
                if st.session_state.get("correction_factor_auto_calculate", False):
                    st.session_state.setdefault("lambda_s", 0.00)
                else:
                    st.session_state["lambda_s"] = (
                        st.session_state.get('widget_lambda1', 0.00) *
                        st.session_state.get('widget_lambda2', 0.00) *
                        st.session_state.get('widget_lambda3', 0.00) *
                        st.session_state.get('widget_lambda4', 0.00)*
                        st.session_state.get('widget_pie_fat', 0.00)
                    )
                # Lambda_s (총 보정계수)
                st.number_input(
                    r"$\lambda_{s}$ (Total)", 
                    min_value=0.0, 
                    value=float(st.session_state.get('lambda_s', 0.00)),
                    step=0.05, 
                    key="widget_lambda_s",
                    on_change=update_temp_from_input,
                    args=("widget_lambda_s", "lambda_s"),
                    disabled=True
                )


            def has_validation_errors3():
                # 필수 입력값 체크
                if abs(st.session_state.get('lambda_s', 0)) == 0:
                    return True
                return False

        # 네비게이션 및 저장 
        # 네비게이션 버튼
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- back", use_container_width=True, key="fatigue_correction_back"):
                add_tab_switch_button("Back", tabs[1])  # tabs[1]으로 변경
        with col3:
            validation_errors3 = has_validation_errors3()
            if validation_errors3:
                if st.button("Next   →", use_container_width=True, key="fatigue_correction_next"):
                    add_tab_switch_button("Next", tabs[3])
                    if abs(st.session_state.get('lambda_s', 0)) == 0:
                        st.toast(r"Please enter Correction Factor ($λ_s$)")
            else:
                if st.button("Calculate Fatigue Result →", use_container_width=True, key="fatigue_correction_next", type="primary"):
                    update_temp_from_input_multi([
                        'correction_factor_auto_calculate', 'pie_fat', 'lambda2', 'lambda4',
                        'lambda1', 'lambda3', 'lambda_s'
                    ])
                    add_tab_switch_button("Next", tabs[3])
                    calculate_delta_sigma_equ()
            # button_text = "Update" if st.session_state.get('edit_mode', False) else "Save Result"
            # if st.button(button_text, use_container_width=True, key=f"save_result_correction"):
            #     save_fatigue_case()
    def final_check():
        try:
            if st.session_state.get('is_ok') == "N/A" :
                return True
            if st.session_state.get('left_side', 0) == 0 or st.session_state.get('right_side', 0) == 0:
                return True
            if notyetchecked == True:
                return True
        except:
            return False
    # 세번째 탭 - Fatigue Result 결과표시 계산과정
    with tab4:
        if validation_errors1 or validation_errors2 or final_check():
            with st.container(height=800, border=False):
                st.error("Please check your input again.")
                if st.session_state.get('case_name', '') == '':
                    st.error("Please enter case name.", icon="⚠️")
                if abs(st.session_state.get('span_length', 0)) == 0:
                    st.error("Please enter span length($L$).", icon="⚠️")
                if abs(st.session_state.get('Es', 0)) == 0:
                    st.error("Please enter steel elastic modulus($E_s$).", icon="⚠️")
                if abs(st.session_state.get('Ec', 0)) == 0:
                    st.error("Please enter concrete elastic modulus($E_c$).", icon="⚠️")
                if notyetchecked == True:
                    st.error("Please check crack state", icon="⚠️")
                if is_cracked_section:
                    if abs(st.session_state.get('Msd', 0)) == 0:
                        st.error("Please enter moment value($Msd$).", icon="⚠️")
                if st.session_state.section_type == "":
                    st.error("Specify whether the section is cracked or uncracked.(Fatigue Settings Pages)", icon="⚠️")  
                else:
                    if abs(st.session_state.get('sctraz', 0)) == 0:
                        st.error("Please enter fatigue stress values.", icon="⚠️")
                # if not validation_errors1 and not validation_errors2 :
                #     if st.session_state.get('is_ok') == "N/A":
                #         st.error("Calculation is needed. Please click the calculation button below.")
                #         if st.button("Calculate Fatigue Result", key="calculate_fatigue_result", use_container_width=True):
                #             calculate_delta_sigma_equ()
                #             st.rerun()      
                        # 네비게이션 및 저장 버튼
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("<- Back", key="back_to_fatigue_settings5", use_container_width=True):
                    add_tab_switch_button("Back", tabs[2])
#--------------------------------------------차트---------------------------------------------------
        else:

            def chartdrawing():
                # 현재 설정 정보 가져오기
                current_support = st.session_state.get('support_type_road', 'Intermediate Support Area')
                current_steel = st.session_state.get('steel_type', 'Straight and bent bars')
                current_span = st.session_state.get('span_length', 35.0)
                
                # λ₁ 세부 정보 표시
                try:
                    from projects.concrete_fatigue_analysis_ntc2018.calc.road_concrete_lambda import get_current_lambda1_info
                    lambda1_info = get_current_lambda1_info(current_support, current_steel, current_span)
                except Exception as e:
                    st.warning(f"λ₁ 정보 표시 중 오류: {str(e)}")
                                    
                try:
                    from projects.concrete_fatigue_analysis_ntc2018.calc.road_concrete_lambda import plot_lambda1_curves_road
                    
                    # 2개 차트 생성

                    fig1, fig2 = plot_lambda1_curves_road(current_support, current_steel, current_span)
                    if current_support == "Intermediate Support Area":
                        # 차트 1: Intermediate Support Area
                        st.plotly_chart(fig1, use_container_width=True)
                    else:
                        # 차트 2: Other Structures  
                        st.plotly_chart(fig2, use_container_width=True)
                    st.markdown("""<h7> Note): <br> 
                        Steel Type:1) Splicing Devices 
                        2) Curved Tendons in Steel Ducts 
                        3) Reinforcing Steel 
                            - Pre-tensioning (all) 
                            - Post-tensioning: 
                            - Strand in plastic ducts 
                            - Straight tendons in steel ducts 
                        4) Shear Reinforcement <br>
                    Support Type: a) Continuous Beam 
                        b) Single Span Beam 
                        c) Carriageway Slab 
                        </h7>""", unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"디버깅 차트 생성 중 오류 발생: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
            def sn_curve():
                #-----------------------------------------------------------sn curve-----------------------------------------------------------
                # 결과 탭에 S-N 커브 표시 기능 추가
                st.markdown("<h6><b>S-N Curve for Steel Fatigue</b></h6>", unsafe_allow_html=True)

                # 계산에 필요한 값 가져오기
                steel_type = st.session_state.get('steel_type', "Straight and bent bars")
                k2 = st.session_state.get('k2', "999999")  # 강재 유형에 따라 다름
                delta_sigma_Rsk = get_stress_range_road(steel_type)
                
                # 핵심 파라미터 정보
                st.write(f"Steel type: **{steel_type}**")
                st.write(f"ΔσRsk: **{delta_sigma_Rsk:.1f} MPa**")
                st.write(f"k₂ (slope 2): **{k2}**")
                #----------------------------------------sn curve end -------------------------------------------------------




            #----------------------------------------결과표시---------------------------------------------------
            section_type = st.session_state.get('section_type', 'Non-cracked section')
            if st.session_state.get('input_changed', False):
                st.warning("🔄 Input values have been changed. Please recalculate to see updated results.")
                if st.button("Fatigue Result Recalculate", key="calculate_fatigue_result2", use_container_width=True):
                    if st.session_state.correction_factor_auto_calculate ==True:
                        calculate_lambda_s_values()
                    calculate_delta_sigma_equ()
                    st.session_state.input_changed = False
                    st.rerun()
            if section_type=="Cracked section":
                with st.container(border=True, height=800):
                    st.markdown("<h6><b>Fatigue Result</b></h6>", unsafe_allow_html=True)
                    # 결과가 있을 경우 표시
                    if 'is_ok' in st.session_state:
                        
                        # 판정값 가져오기
                        left_side = st.session_state.get('left_side', 0.0)
                        right_side = st.session_state.get('right_side', 0.0)
                        is_ok = st.session_state.get('is_ok', False)
                        
                        # 판정 결과 표시
                        with st.container(border=True, height=80):
                            col1, col2, col3, col4 = st.columns([10, 1, 9, 5], vertical_alignment="center")
                            with col1:
                                st.latex(r"\gamma_F \cdot \gamma_{Sd} \cdot \Delta\sigma_{s,equ} = " + f"{st.session_state.stress_left:.3f}\\text{{ MPa}}")
                            with col2:
                                st.latex(r"\leq" if is_ok == 'OK' else r">")
                            with col3:
                                st.latex(r"\frac{\Delta\sigma_{Rsk}}{\gamma_{s,fat}} = " + f"{st.session_state.stress_right:.3f}\\text{{ MPa}}")
                            with col4:
                                st.markdown(
                                    "<h5 style='color: green;'>OK</h5>" if is_ok == 'OK'
                                    else "<h5 style='color: red;'>NG</h5>",
                                    unsafe_allow_html=True
                                )

                        # 상세 계산 결과 표시
                        st.markdown("<h6><b>Detail Calculation of Steel Fatigue Result (DESM)</b></h6>", unsafe_allow_html=True)
                        if st.session_state.correction_factor_auto_calculate == False:
                            pass
                        else:
                            lambda1 = st.session_state.get('lambda1', 0.0)
                            st.write(r"Correction factor of $\lambda_{s,1}$ = " + f"{lambda1:.3f}")
                            with st.container(border=True, height=620):
                                support_type = st.session_state.get('support_type_road', 'Simply supported beams')
                                steel_type = st.session_state.get('steel_type', 'Straight and bent bars')
                                span_length = st.session_state.get('span_length', 35.0)
                                traffic_type = st.session_state.get('traffic_type_road', 'Standard traffic')
                                
                                st.latex(r"\lambda_{s,1} = \begin{cases} & \text{Support Type: " + str(support_type) + r"} \\" + 
                                        r"      & \text{Steel Type: " + str(steel_type) + r"} \\" +
                                        r"      & \text{Span Length: " + str(span_length) + r"m} \end{cases}" + "=" +
                                        f"{lambda1:.3f}")
                                chartdrawing()


                            # Lambda2 계산 과정
                            lambda2 = st.session_state.get('lambda2', 0.0)
                            k2 = st.session_state.get('k2', 9.0)
                            vol = st.session_state.get('vol', 100000.0)
                            Q_bar = st.session_state.get('Q_bar', 1.0)
                            st.write(r"Correction factor of $\lambda_{s,2}$ = " + f"{lambda2:.3f}")
                            with st.container(border=True, height=240):
                                st.markdown(r"Traffic Type: " + str(traffic_type) + r"  ")
                                st.latex(r"\lambda_{s,2} = Q_{bar} \cdot \left(\frac{N_{obs}}{2 \times 10^6}\right)^{1/k_2} = " + f"{Q_bar:.3f}" + r" \cdot \left(\frac{" + 
                                        f"{vol:.0f}" + r"}{2 \times 10^6}\right)^{1/" + f"{k2:.1f}" + r"} = " + f"{lambda2:.3f}")
                                sn_curve()
                            # Lambda3 계산 과정
                            lambda3 = st.session_state.get('lambda3', 0.0)
                            nyear = st.session_state.get('nyear', 50.0)
                            
                            st.write(r"Correction factor of $\lambda_{s,3}$ = " + f"{lambda3:.3f}")
                            with st.container(border=True, height=80):
                                st.latex(r"\lambda_{s,3} = \left(\frac{N_{years}}{100}\right)^{1/k_2} = \left(\frac{" + 
                                        f"{nyear:.0f}" + r"}{100}\right)^{1/" + f"{k2:.1f}" + r"} = " + f"{lambda3:.3f}")

                            # Lambda4 계산 과정
                            lambda4 = st.session_state.get('lambda4', 1.0)  # 기본값 1.0
                            k2 = st.session_state.get('k2', 9.0)  # S-N 곡선 지수
                            vol = st.session_state.get('vol', 500000.0)  # 연간 트럭 통과 대수
                            nc = st.session_state.get('nc', 1.0)  # 차선 수
                            st.write(r"Correction factor of $\lambda_{s,4}$ = " + f"{lambda4:.3f}")
                            with st.container(border=True, height=90):
                                st.latex(r"\lambda_{s,4} = \sqrt[k_2]{\frac{\sum N_{obs,i}}{N_{obs,1}}} = \left(\frac{" +f"{vol * nc:.0f}" + r"}{" + f"{vol:.0f}" + r"}\right)^{1/" + f"{k2:.1f}" + r"} = " + f"{lambda4:.3f}")

                            pie_fat = st.session_state.get('pie_fat', 1.0)
                            # Lambda_s 총 보정계수 계산

                        pie_fat = st.session_state.get('pie_fat', 1.0)
                            # Lambda_s 총 보정계수 계산
                        lambda1 = st.session_state.get('lambda1', 0.0)
                        lambda2 = st.session_state.get('lambda2', 0.0)
                        lambda3 = st.session_state.get('lambda3', 0.0)
                        lambda4 = st.session_state.get('lambda4', 0.0)
                        lambda_s = st.session_state.get('lambda_s', 0.0)      
                        lambda_s = st.session_state.get('lambda_s', 0.0)
                        st.write(r"Total correction factor $\lambda_{s}$ = " + f"{lambda_s:.3f}")
                        with st.container(border=True, height=60):
                            st.latex(r"\lambda_{s} = \phi_{fat} \cdot \lambda_{s,1} \cdot \lambda_{s,2} \cdot \lambda_{s,3} \cdot \lambda_{s,4} = " + 
                                    f"{pie_fat:.3f}" + r" \cdot " + f"{lambda1:.3f}" + r" \cdot " + f"{lambda2:.3f}" + r" \cdot " + 
                                    f"{lambda3:.3f}" + r" \cdot " + f"{lambda4:.3f}" + r" = " + f"{lambda_s:.3f}")
                        # 등가 응력 범위 계산 표시
                        st.write("Equivalent Stress Calculation")
                        delta_sigma_equ = st.session_state.get('delta_sigma_equ', 0.0)
                        section_type = st.session_state.get('section_type', "Non-cracked section")
                        lambda_s = st.session_state.get('lambda_s', 0.0)


                        # 균열 단면 계산식 표시
                        sigma_c_traz = st.session_state.get('sigma_c_traz', 0.0)
                        delta_s_sigma_ec = st.session_state.get('delta_s_sigma_ec', 0.0)
                        steel_type = st.session_state.get('steel_type', 'Straight and bent bars')
                        delta_sigma_Rsk = get_stress_range_road(steel_type)
                        delta_s_sigma_equ = st.session_state.get('delta_s_sigma_equ', 0.0)
                        gamma_s_fat = st.session_state.get('factor_rsfat', 1.15)
                        gamma_F = st.session_state.get('factor_rf', 1.0)
                        gamma_Sd = st.session_state.get('factor_rsd', 1.0)
                        n_cables = st.session_state.get('n_cables', 1.0)
                        A_cable = st.session_state.get('A_cable', 98.7)
                        Msd = st.session_state.get('Msd', 0.0)
                        d = st.session_state.get('d', 0.0)
                        # right_side = delta_sigma_Rsk / gamma_s_fat
                        # left_side = gamma_F * gamma_Sd * delta_s_sigma_equ
                        st.markdown(
                            r"Stress Range : $\Delta\sigma_{s,ec} = \frac{M_{sd}}{d \cdot n_{cables} \cdot A_{cable}} = \frac{" + 
                            f"{Msd:.3f}" + r" \cdot 10^6}{" + f"{d:.3f}" + r" \cdot " + f"{n_cables}" + r" \cdot " + 
                            f"{A_cable:.3f}" + "} = " + f"{delta_s_sigma_ec:.3f}" + r"\text{ MPa}$", 
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            r"Equivalent Stress Range : $\Delta\sigma_{s,equ} = \Delta\sigma_{s,ec} \cdot \lambda_s = " + 
                            f"{delta_s_sigma_ec:.3f}" + r" \cdot " + f"{lambda_s:.3f}" + r" = " + 
                            f"{delta_s_sigma_equ:.3f}" + r"\text{ MPa}$", 
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            r"Design Strength : $\frac{\Delta\sigma_{Rsk}}{\gamma_{s,fat}} = \frac{" + 
                            f"{delta_sigma_Rsk:.3f}" + "}{" + f"{gamma_s_fat:.3f}" + "} = " + 
                            f"{right_side:.3f}" + r"\text{ MPa}$", 
                            unsafe_allow_html=True
                        )

                            
                        with st.container(border=True, height=240):
                            # 조건식 표시
                        # if  p_staffe < 25 and shear_reinforcement_type == "Stirrup":
                        #     reduction_factor = 0.9
                        # elif  p_staffe < 25 and shear_reinforcement_type == "Others":
                        #     reduction_factor = 0.35 +0.026*p_staffe/d_mandrel
                        # else:
                        #     reduction_factor =1 
                            # 상세 값 표시
                            # 상세 값 표시
                            col1, col2, col3, col4 = st.columns([10, 1, 9, 5], vertical_alignment="center")

                            with col1:
                                st.latex(
                                    r"\gamma_F \cdot \gamma_{Sd} \cdot \Delta\sigma_{s,equ}"
                                    + f" = {st.session_state.stress_left:.3f}\;\\text{{ MPa}}"
                                )
                            with col2:
                                st.latex(r"\leq" if st.session_state.is_ok == 'OK' else r">")
                            with col3:
                                st.latex(
                                    r"\frac{\Delta\sigma_{Rsk}}{\gamma_{s,fat}}"
                                    + f" = {st.session_state.stress_right:.3f}\;\\text{{ MPa}}"
                                )
                            with col4:
                                st.markdown(
                                    "<h5>{}</h5>".format("OK" if st.session_state.is_ok== 'OK' else "NG"),
                                    unsafe_allow_html=True,
                                )

                            # 변수 설명
                            st.markdown("**where :**")
                            st.markdown(
                                rf"""
                            - $\gamma_F = {st.session_state.get('factor_rf', 1.0)}$ (Partial factor for fatigue actions)  
                            - $\gamma_{{Sd}} = {st.session_state.get('factor_rsd', 1.0)}$ (Partial factor for uncertainty)  
                            - $\Delta\sigma_{{s,equ}} = {delta_s_sigma_equ:.3f}$ MPa (Equivalent stress range)  
                            - $\Delta\sigma_{{Rsk}} = {delta_sigma_Rsk:.3f}$ MPa (Characteristic fatigue strength)  
                            - $\gamma_{{s,fat}} = {st.session_state.get('factor_rsfat', 1.15)}$ (Partial factor for fatigue of reinforcing steel)
                            """
                            )  

                    else:
                        st.info("No calculation results. Please click the 'Calculation' button first to perform the calculation.")
                        
                        # 계산 버튼 추가
                        if st.button("Calculate", key="calculate_results", use_container_width=True):
                            # 계산 함수 호출
                            calculate_delta_sigma_equ()
            else:
                #비균열단면 결과표기 비균열결과

                with st.container(border=True, height=800):
                    if section_type == "Non-cracked section":

                        st.markdown("<h6><b>Fatigue Result</b></h6>", unsafe_allow_html=True)
                        # 결과가 있을 경우 표시
                        if 'is_ok' in st.session_state:
                            
                            # 판정값 가져오기
                            left_side = st.session_state.get('left_side', 0.0)
                            right_side = st.session_state.get('right_side', 0.0)
                            is_ok = st.session_state.get('is_ok', False)
                            
                            # 판정 결과 표시
                            with st.container(border=True, height=80):
                                col1, col2, col3, col4 = st.columns([10, 1, 9, 5], vertical_alignment="center")
                                with col1:
                                    st.latex(r"\gamma_F \cdot \gamma_{Sd} \cdot \Delta\sigma_{s,equ} = " + f"{st.session_state.stress_left:.3f}\\text{{ MPa}}")
                                with col2:
                                    st.latex(r"\leq" if st.session_state.is_ok== 'OK' else r">")
                                with col3:
                                    st.latex(r"\frac{\Delta\sigma_{Rsk}}{\gamma_{s,fat}} = " + f"{st.session_state.stress_right:.3f}\\text{{ MPa}}")
                                with col4:
                                    st.markdown(
                                        "<h5 style='color: green;'>OK</h5>" if st.session_state.is_ok == 'OK'
                                        else "<h5 style='color: red;'>NG</h5>",
                                        unsafe_allow_html=True
                                    )
                        
                            # 상세 계산 결과 표시
                            st.markdown("<h6><b>Detail Calculation of Steel Fatigue Result (DESM)</b></h6>", unsafe_allow_html=True)
                            # 상세 계산 결과 표시
                            if st.session_state.correction_factor_auto_calculate == False:
                                pass
                            else:
                                lambda1 = st.session_state.get('lambda1', 0.0)
                                st.write(r"Correction factor of $\lambda_{s,1}$ = " + f"{lambda1:.3f}")
                                with st.container(border=True, height=620):
                                    support_type = st.session_state.get('support_type_road', 'Simply supported beams')
                                    steel_type = st.session_state.get('steel_type', 'Straight and bent bars')
                                    span_length = st.session_state.get('span_length', 35.0)
                                    traffic_type = st.session_state.get('traffic_type_road', 'Standard traffic')
                                    
                                    st.latex(r"\lambda_{s,1} = \begin{cases} & \text{Support Type: " + str(support_type) + r"} \\" + 
                                            r"      & \text{Steel Type: " + str(steel_type) + r"} \\" +
                                            r"      & \text{Span Length: " + str(span_length) + r"m} \end{cases}" + "=" +
                                            f"{lambda1:.3f}")
                                    chartdrawing()


                                # Lambda2 계산 과정
                                lambda2 = st.session_state.get('lambda2', 0.0)
                                k2 = st.session_state.get('k2', 9.0)
                                vol = st.session_state.get('vol', 100000.0)
                                Q_bar = st.session_state.get('Q_bar', 1.0)
                                st.write(r"Correction factor of $\lambda_{s,2}$ = " + f"{lambda2:.3f}")
                                with st.container(border=True, height=240):
                                    st.markdown(r"Traffic Type: " + str(traffic_type) + r"  ")
                                    st.latex(r"\lambda_{s,2} = Q_{bar} \cdot \left(\frac{N_{obs}}{2 \times 10^6}\right)^{1/k_2} = " + f"{Q_bar:.3f}" + r" \cdot \left(\frac{" + 
                                            f"{vol:.0f}" + r"}{2 \times 10^6}\right)^{1/" + f"{k2:.1f}" + r"} = " + f"{lambda2:.3f}")
                                    sn_curve()
                                # Lambda3 계산 과정
                                lambda3 = st.session_state.get('lambda3', 0.0)
                                nyear = st.session_state.get('nyear', 50.0)
                                
                                st.write(r"Correction factor of $\lambda_{s,3}$ = " + f"{lambda3:.3f}")
                                with st.container(border=True, height=80):
                                    st.latex(r"\lambda_{s,3} = \left(\frac{N_{years}}{100}\right)^{1/k_2} = \left(\frac{" + 
                                            f"{nyear:.0f}" + r"}{100}\right)^{1/" + f"{k2:.1f}" + r"} = " + f"{lambda3:.3f}")
                                # Lambda4 계산 과정
                                lambda4 = st.session_state.get('lambda4', 1.0)  # 기본값 1.0
                                k2 = st.session_state.get('k2', 9.0)  # S-N 곡선 지수
                                vol = st.session_state.get('vol', 500000.0)  # 연간 트럭 통과 대수
                                nc = st.session_state.get('nc', 1.0)  # 차선 수
                                st.write(r"Correction factor of $\lambda_{s,4}$ = " + f"{lambda4:.3f}")
                                with st.container(border=True, height=90):
                                    st.latex(r"\lambda_{s,4} = \sqrt[k_2]{\frac{\sum N_{obs,i}}{N_{obs,1}}} = \left(\frac{" +f"{vol * nc:.0f}" + r"}{" + f"{vol:.0f}" + r"}\right)^{1/" + f"{k2:.1f}" + r"} = " + f"{lambda4:.3f}")
                            pie_fat = st.session_state.get('pie_fat', 1.0)
                                # Lambda_s 총 보정계수 계산
                            lambda1 = st.session_state.get('lambda1', 0.0)
                            lambda2 = st.session_state.get('lambda2', 0.0)
                            lambda3 = st.session_state.get('lambda3', 0.0)
                            lambda4 = st.session_state.get('lambda4', 0.0)
                            lambda_s = st.session_state.get('lambda_s', 0.0)        

                            pie_fat = st.session_state.get('pie_fat', 1.0)
                            # Lambda_s 총 보정계수 계산
                            lambda_s = st.session_state.get('lambda_s', 0.0)
                            st.write(r"Total correction factor $\lambda_{s}$ = " + f"{lambda_s:.3f}")
                            with st.container(border=True, height=80):
                                st.latex(r"\lambda_{s} = \phi_{fat} \cdot \lambda_{s,1} \cdot \lambda_{s,2} \cdot \lambda_{s,3} \cdot \lambda_{s,4} = " + 
                                        f"{pie_fat:.3f}" + r" \cdot " + f"{lambda1:.3f}" + r" \cdot " + f"{lambda2:.3f}" + r" \cdot " + 
                                        f"{lambda3:.3f}" + r" \cdot " + f"{lambda4:.3f}" + r" = " + f"{lambda_s:.3f}")
                            
                            # 등가 응력 범위 계산 표시
                            st.markdown("<h6><b>Equivalent Stress Calculation</b></h6>", unsafe_allow_html=True)
                            delta_sigma_equ = st.session_state.get('delta_sigma_equ', 0.0)
                            section_type = st.session_state.get('section_type', "Non-cracked section")
                            lambda_s = st.session_state.get('lambda_s', 0.0)
                            # 비균열 단면 계산식 표시
                            sigma_c_traz = st.session_state.get('sigma_c_traz', 0.0)
                            Es = st.session_state.get('Es', 200000.0)
                            Ec = st.session_state.get('Ec', 35000.0)
                            delta_s_sigma_ec = sigma_c_traz * Es/Ec
                            steel_type = st.session_state.get('steel_type', 'Straight and bent bars')
                            delta_sigma_Rsk = get_stress_range_road(steel_type)
                            delta_s_sigma_equ = delta_s_sigma_ec * lambda_s
                            gamma_s_fat = st.session_state.get('factor_rsfat', 1.15)
                            gamma_F = st.session_state.get('factor_rf', 1.0)
                            gamma_Sd = st.session_state.get('factor_rsd', 1.0)
                            right_side = delta_sigma_Rsk / gamma_s_fat
                            left_side = gamma_F * gamma_Sd * delta_s_sigma_equ
                            st.session_state.stress_left = left_side
                            st.session_state.stress_right = right_side
                            is_ok = st.session_state.get('is_ok', False)
                            st.markdown(r"Stress Range : $\Delta\sigma_{s,ec} = \sigma_{c,traz} \cdot \frac{E_s}{E_c} = " + f"{sigma_c_traz:.3f}" + r" \cdot \frac{" + f"{Es:.0f}" + "}{" + f"{Ec:.0f}" + "} = " + f"{delta_s_sigma_ec:.3f}" + r"\text{ MPa}$", unsafe_allow_html=True)
                            st.markdown(
                                r"Equivalent stress: $\Delta\sigma_{s,equ} = \Delta\sigma_{s,ec} \cdot \lambda_s = " + 
                                f"{delta_s_sigma_ec:.3f}" + r" \cdot " + f"{lambda_s:.3f}" + r" = " + 
                                f"{delta_s_sigma_equ:.3f}" + r"\text{ MPa}$", 
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                r"Design strength : $\frac{\Delta\sigma_{Rsk}}{\gamma_{s,fat}} = \frac{" + 
                                f"{delta_sigma_Rsk:.3f}" + "}{" + f"{gamma_s_fat:.3f}" + "} = " + 
                                f"{right_side:.3f}" + r"\text{ MPa}$", 
                                unsafe_allow_html=True
                            )

                            
                            with st.container(border=True, height=240):
                                # 조건식 표시
                            # if  p_staffe < 25 and shear_reinforcement_type == "Stirrup":
                            #     reduction_factor = 0.9
                            # elif  p_staffe < 25 and shear_reinforcement_type == "Others":
                            #     reduction_factor = 0.35 +0.026*p_staffe/d_mandrel
                            # else:
                            #     reduction_factor =1 
                                # 상세 값 표시
                                # 상세 값 표시
                                col1, col2, col3, col4 = st.columns([10, 1, 9, 5],vertical_alignment="center")
                                with col1:
                                    st.latex(r"\gamma_F \cdot \gamma_{Sd} \cdot \Delta\sigma_{s,equ} = " + f"{st.session_state.stress_left:.3f}\t{{ MPa}}")
                                with col2:
                                    st.latex(r"\leq" if st.session_state.is_ok == 'OK' else r">")
                                with col3:
                                    st.latex(r"\frac{\Delta\sigma_{Rsk}}{\gamma_{s,fat}} = " + f"{st.session_state.stress_right:.3f}\t{{ MPa}}")
                                with col4:
                                    if st.session_state.is_ok== 'OK':
                                        st.markdown("<h5>OK</h5>", unsafe_allow_html=True)
                                    else:
                                        st.markdown("<h5>NG</h5>", unsafe_allow_html=True)    
                                # where 설명
                                st.markdown("**where :**")
                                st.markdown(rf"""
                                - $\Delta\sigma_{{s,equ}}$ = {delta_s_sigma_equ:.3f} MPa (Final equivalent stress)
                                - $\Delta\sigma_{{Rsk}}$ = {delta_sigma_Rsk:.3f} MPa (Characteristic fatigue strength)
                                - $\gamma_{{s,fat}}$ = {gamma_s_fat:.3f} (Partial safety factor for fatigue)
                                - $\gamma_F$ = {gamma_F:.3f} (Partial factor for fatigue actions)
                                - $\gamma_{{Sd}}$ = {gamma_Sd:.3f} (Partial factor for uncertainty)
                                """)


                    else:
                        st.error("No calculation results. Please click the 'Calculation' button first to perform the calculation.")
                        
                        # 계산 버튼 추가
                        if st.button("Calculate", key="calculate_results", use_container_width=True):
                            # 계산 함수 호출
                            calculate_delta_sigma_equ()   

            # 네비게이션 및 저장 버튼
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("<- Back", key="back_to_fatigue_settings", use_container_width=True):
                    add_tab_switch_button("Back", tabs[2])
            
            with col3:
                button_text = "Update" if is_edit_mode else "Save Result"
                if st.button(button_text, key="save_fatigue_result", use_container_width=True, type="primary"):
                    update_temp_from_input_multi([
                        'case_name', 'support_type_road', 'fck', 'Es',
                        'span_length', 'd', 'Ec', 'crack_option',
                        'section_type', 'sctraz', 'Msd', 'manual_input2',
                        'manual_input', 'fb', 'fctd'
                    ])

                    update_temp_from_input_multi([
                        'steel_type', 'A_steel', 'n_steel', 'nc',
                        'nt', 'pavement_roughness', 'vol_auto_calculate', 'traffic_category_vol',
                        'vol', 'traffic_type_road', 'span_length', 'support_type_road', 'is_ok'
                    ])




                    save_fatigue_case()


# 디버깅 정보 표시 (옵션)

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
Reinforcing Steel (DESM) : Road  

1page (Fatigue Settings)  
- case_name  
- span_length  
- support_type_road  
- d  
- fck  
- Es  
- Ec  
- section_type  
- steel_type  
- A_steel  
- n_steel  

2page (Fatigue Load)  
- sctraz  
- Msd  
- nc  
- nt  
- traffic_type_road  
- pavement_roughness  
- vol_auto_calculate  
- traffic_category_vol  
- vol  

3page (Correction Factor)  
- correction_factor_auto_calculate  
- pie_fat  
- lambda1  
- lambda2  
- lambda3  
- lambda4  
- lambda_s  

4page (Fatigue Result)  
- (입력값 없음)  

자동 계산값  
- delta_s_sigma_ec  
- delta_s_sigma_equ  
- delta_sigma_Rsk  
- left_side  
- right_side  
- is_ok  
'''