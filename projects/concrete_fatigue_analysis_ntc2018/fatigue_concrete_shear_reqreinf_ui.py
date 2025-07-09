# fatigue_concrete_shear_reqreinf_ui.py
#0611 check
import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import math
from projects.concrete_fatigue_analysis_ntc2018.session_manager import *
from projects.concrete_fatigue_analysis_ntc2018.calc.road_concrete_lambda import *
import re
from projects.concrete_fatigue_analysis_ntc2018.calc.fatigue_prestressing_steel_desm_rail_design import *

# PageManager 네비게이션 import
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from projects.concrete_fatigue_analysis_ntc2018.utils.navigator import back_to_fatigue_case

# 세션 초기화
initialize_session()
# 모달 다이얼로그 가져오기 
import_dialogs = SessionManager.initialize_import_dialogs() if 'SessionManager' in globals() else None
civil_stress_import = import_dialogs['shear_force_reqreinf'] if import_dialogs else None
civil_stress_import2 = import_dialogs['moving_stress']


get_lambda_s= 1.61
get_delta_sigma_Rsk = 180



# UI 용 간소화된 스틸 피로 계산 클래스
class cal_for_steel_desm_rail:
    @staticmethod
    def calculate_lambda_s_values_rail():
        #람다계산
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
            p_staffe = st.session_state.p_staffe
            n_braccia = st.session_state.n_braccia
            Vsd = abs(st.session_state.Vsd)
            s = st.session_state.s
            d = st.session_state.d
            lambda_s = st.session_state.lambda_s
            # 스터럽 면적 계산 (area = (P staffe/2)²*π*n braccia)
            area = ((p_staffe/2)**2 * math.pi) * n_braccia
            
            # 응력 계산 (σs = (Vsd*1000*s)/(0.9*d*area))
            sigma_s = ((Vsd*1000) * s) / (0.9 * d * area)

            delta_sigma_equ = lambda_s * sigma_s


            st.session_state.delta_sigma_equ = delta_sigma_equ
            st.session_state.sigma_s_equ = delta_sigma_equ
            st.session_state.area = area
            st.session_state.sigma_s = sigma_s

            # temp_result_df 업데이트
            update_temp_from_input_multi([
                'delta_sigma_equ', 'area', 'sigma_s', 'sigma_s_equ'
            ])
            
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
            p_staffe = st.session_state.p_staffe
            shear_reinforcement_type = st.session_state.shear_reinforcement_type
            d_mandrel = st.session_state.d_mandrel
            gamma_fat = st.session_state.factor_rsfat
            gamma_F = st.session_state.factor_rf
            gamma_Sd = st.session_state.factor_rsd
            sigma_s_equ = st.session_state.sigma_s_equ

            # 계산용 임시 데이터프레임
            if 'temp_result_df' not in st.session_state or st.session_state.temp_result_df.empty:
                st.session_state.temp_result_df = pd.DataFrame([{"case_id": inputs["case_id"]}])
            
            # 기준 응력 범위 가져오기
            temp_df = st.session_state.temp_result_df
            # temp_df = update_delta_sigma_Rsk_prestressing_steel_rail(inputs, temp_df)
            # delta_sigma_Rsk = temp_df.loc[temp_df["case_name"] == inputs["case_id"], "delta_sigma_Rsk"].values[0]
            # delta_sigma_Rsk = temp_df.loc[temp_df["case_id"] == inputs["case_id"], "delta_sigma_Rsk"].values[0]
            # delta_sigma_Rsk = temp_df["delta_sigma_Rsk"].iloc[0]
            delta_sigma_Rsk = 180
            reduction_factor = st.session_state.reduction_factor
            if  p_staffe < 25 and shear_reinforcement_type == "Stirrup":
                reduction_factor = 0.9
            elif  p_staffe < 25 and shear_reinforcement_type == "Others":
                reduction_factor = 0.35 +0.026*p_staffe/d_mandrel
            else:
                reduction_factor =1
            # 계산 결과 세션에 저장
            
            left_side =  gamma_F * gamma_Sd * sigma_s_equ
            right_side = delta_sigma_Rsk / gamma_fat *reduction_factor
            
            # 판정 결과
            is_steel_ok = left_side <= right_side

            if is_steel_ok == True:
                is_ok = "OK"
            else:
                is_ok = "NG"
            st.session_state.is_ok = is_ok
            
            # 계산 결과 저장


            st.session_state.stress_left = left_side
            st.session_state.stress_right = right_side
            st.session_state.reduction_factor = reduction_factor
            st.session_state.is_ok = is_ok

            # 세션 상태에 저장
            st.session_state.reduction_factor = reduction_factor
            st.session_state.left_side = left_side
            st.session_state.right_side = right_side
            st.session_state.is_steel_ok = is_steel_ok

            st.session_state.delta_sigma_Rsk = delta_sigma_Rsk

            
            # temp_result_df 업데이트
            update_temp_from_input_multi([
                'delta_sigma_Rsk', 'left_side', 'right_side', 'is_ok', 'reduction_factor','stress_left','stress_right'
            ])
            
            return is_steel_ok
            
        except Exception as e:
            # st.error(f"판정 계산 중 오류 발생: {str(e)}")
            return False, 0.0







# UI 용 간소화된 스틸 피로 계산 클래스
class cal_for_steel_desm_ui_road:
    """스틸 피로 계산을 위한 UI 용 클래스"""
#---------------------------------------------road calculate start ---------------------------------------------
def calculate_lambda_s_values_road():
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
        
        # lambda1 계산 road
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
            'pie_fat','lambda1', 'lambda2', 'lambda3', 'lambda4', 'lambda_s', 'k2', "traffic_type_road", "support_type_road", "steel_type", "Q_bar"
        ])
        
        return lambda_s
        
    except Exception as e:
        st.error(f"Lambda 계수 계산 중 오류 발생: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return 1.0
    
def calculate_results_road():
    
    required_fields = ['Vsd', 's', 'd', 'p_staffe', 'n_braccia', 'lambda_s']
    missing_fields = [field for field in required_fields if field not in st.session_state]
    
    if missing_fields:
        st.error(f"The following input values are missing: {', '.join(missing_fields)}")
        return False
    
    try:
        # 입력값 가져오기
        Vsd = abs(float(st.session_state.Vsd))
        s = float(st.session_state.s)
        d = float(st.session_state.d)
        p_staffe = float(st.session_state.p_staffe)
        n_braccia = int(st.session_state.n_braccia)
        lambda_s = float(st.session_state.lambda_s)
        steel_type = st.session_state.steel_type
        # delta_sigma_Rsk = get_stress_range_road(steel_type)
        delta_sigma_Rsk =180
        d_mandrel = float(st.session_state.d_mandrel)
        shear_reinforcement_type = st.session_state.shear_reinforcement_type
        reduction_factor = st.session_state.reduction_factor
        if  p_staffe < 25 and shear_reinforcement_type == "Stirrup":
            reduction_factor = 0.9
        elif  p_staffe < 25 and shear_reinforcement_type == "Others":
            reduction_factor = 0.35 +0.026*p_staffe/d_mandrel
        else:
            reduction_factor =1 
        # 안전계수 가져오기 (first_setting.py에서 설정된 값 사용)
        gamma_fat = st.session_state.factor_rsfat  # 철근 안전계수
        gamma_F = st.session_state.factor_rf      # 하중 안전계수
        gamma_Sd = st.session_state.factor_rsd   # 기본값 1로 설정
        
        # 스터럽 면적 계산 (area = (P staffe/2)²*π*n braccia)
        area = ((p_staffe/2)**2 * math.pi) * n_braccia
        
        # 응력 계산 (σs = (Vsd*1000*s)/(0.9*d*area))
        sigma_s = ((Vsd*1000) * s) / (0.9 * d * area)
        
        # 등가 응력 범위 계산 (Δσs,equ = σs*λs)
        delta_sigma_s_equ = sigma_s * lambda_s
        
        # 허용 응력 범위 계산 (ΔσRsk/γs.fat)
        delta_sigma_Rsd = delta_sigma_Rsk / gamma_fat * reduction_factor
        
        # 판정값 계산 (γF*γSd*Δσs.equ ≤ ΔσRsk/γs.fat)
        stress_left = gamma_F * gamma_Sd * delta_sigma_s_equ
        stress_right = delta_sigma_Rsd
        
        # OK/NG 판정
        verification = stress_left <= stress_right
        if verification:
            is_ok = "OK"
        else:
            is_ok = "NG"
        # 계산 결과 저장
        st.session_state.area = area
        st.session_state.sigma_s = sigma_s
        st.session_state.delta_sigma_s_equ = delta_sigma_s_equ
        st.session_state.delta_sigma_Rsd = delta_sigma_Rsd
        st.session_state.delta_sigma_Rsk = delta_sigma_Rsk
        st.session_state.gamma_fat = gamma_fat
        st.session_state.gamma_F = gamma_F
        st.session_state.gamma_Sd = gamma_Sd
        st.session_state.stress_left = stress_left
        st.session_state.stress_right = stress_right
        st.session_state.reduction_factor = reduction_factor
        st.session_state.is_ok = is_ok
        st.session_state.discriminant = stress_right - stress_left  # 판정값
        
        # 결과 저장 - temp_result_df에도 저장
        update_temp_from_input_multi([
            'area', 'sigma_s', 'delta_sigma_s_equ', 'delta_sigma_Rsd', 'gamma_fat', 
            'gamma_F', 'gamma_Sd', 'stress_left', 'stress_right',
            'is_ok', 'discriminant', 'reduction_factor', 'shear_reinforcement_type', 'delta_sigma_Rsk'
        ])
        
        return True
    except Exception as e:
        st.error(f"계산 중 오류가 발생했습니다: {str(e)}")
        return False
#---------------------------------------------road calculate end ---------------------------------------------


def fatigue_concrete_shear_reqreinf_ui_page():
    from projects.concrete_fatigue_analysis_ntc2018.fatigue_case_page import Setting_Fatigue_Case  # 지연 임포트

    st.session_state.Fatigue_method = "Concrete Shear(Require Reinforcement)"
    # 편집 모드 체크
    is_edit_mode = st.session_state.get('edit_mode', False)

    if is_edit_mode:
        st.markdown(f"<h5><b>[Edit]Concrete Shear Fatigue(Require Reinforcement):{st.session_state.get('fatigue_case_name', '')}</b></h5>", unsafe_allow_html=True)
    else:
        st.markdown("<h5><b>Concrete Shear Fatigue(Require Reinforcement)</b></h5>", unsafe_allow_html=True)

    # 탭 제목
    tabs = [
        "Fatigue Settings",
        "Fatigue Parameters",
        "Correction Factor",
        "Fatigue Result"
    ]

    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(tabs)

    # 첫번째 탭 - Fatigue Settings
    with tab1:
        with st.container(height=800, border=False):
            import pandas as pd
            st.markdown("<h6><b>Fatigue Settings</b></h6>", unsafe_allow_html=True)
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
            st.markdown("<h6><b>Section Definition</b></h6>", unsafe_allow_html=True)
            
            # 단면 특성 입력
            col1, col2 = st.columns(2)
            
            with col1:
                span_length = st.number_input(r"Span length (m), $L$", 
                                    value=float(st.session_state.get('span_length', 35)),
                                    key='span_length', 
                                    on_change=update_temp_from_input, 
                                    args=('span_length',))

                
            with col2:
                d = st.number_input(r"Effective section height, $d$ [mm]", 
                                    value=float(st.session_state.get('d', 1000)),
                                key='d', 
                                on_change=update_temp_from_input, 
                                args=('d',))
                
                
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h6><b>Fatigue Load</b></h6>", unsafe_allow_html=True)
            with col2:
                # 하중 불러오기 옵션
                use_midas = st.toggle("Import From Midas NX",
                                    value=st.session_state.get('import_option', True), 
                                    key="manual_input", 
                                    on_change=update_temp_from_input,
                                    args=("widget_import_option", "import_option")
                                    )
            with st.container(border=True):
                col1, col2 = st.columns(2, vertical_alignment="bottom")
                with col1:
                    if st.button("Import", use_container_width=True, key="from_midas_nx", 
                                disabled=not use_midas or civil_stress_import is None):
                        if civil_stress_import:
                            civil_stress_import("Import")

                with col2:
                    # Vsdmin (피로하중만의 전단력)
                    st.number_input(r"Shear load provided by fatigue case only, $V_{sd}$ [KN]", 
                                value=abs(float(st.session_state.get('Vsd', 0.00))),
                                step=1.0, 
                                key="widget_Vsd",
                                on_change=update_temp_from_input,
                                args=("widget_Vsd", "Vsd"),
                                disabled=use_midas)
                    
                    # 직접 입력 시 세션 상태 업데이트
                    if not use_midas and 'widget_Vsd' in st.session_state:
                        st.session_state.Vsd = st.session_state.widget_Vsd



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
            def has_validation_errors1():
                # 필수 입력값 체크
                if st.session_state.get('span_length', 0) <= 0:
                    return True
                if st.session_state.get('d', 0) == 0:
                    return True
                if st.session_state.get('Vsd', 0) == 0:
                    return True
                if st.session_state.get('E') == "N/A":
                    return True
                support_type = st.session_state.get('support_type', '')
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
                span_error_message = None
                if min_span is not None and max_span is not None:
                    if not (min_span <= current_span <= max_span):
                        st.session_state.span_error_message = f"Span length must be between {min_span}m and {max_span}m for {support_type} (current: {current_span}m)[UNI ENV 1992-2 Figure A106.2]"
                        st.toast(f"Span length must be between {min_span}m and {max_span}m for {support_type} (current: {current_span}m)[UNI ENV 1992-2 Figure A106.2]", icon="⚠️")
                        return True
                    else:
                        # 에러가 없으면 메시지 초기화
                        st.session_state.span_error_message = None
                return False

        # 네비게이션 및 저장 버튼
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- back", use_container_width=True):
                back_to_fatigue_case()

        with col3:
            validation_errors1 = has_validation_errors1()
            if validation_errors1:
                if st.button("Next →", use_container_width=True, key="next_button_with_error"):
                    if abs(st.session_state.get('span_length', 0)) == 0:
                        st.toast("Span length is required(span_length)", icon="⚠️")
                    elif abs(st.session_state.get('d', 0)) == 0:
                        st.toast("Section height is required(d)", icon="⚠️")
                    elif abs(st.session_state.get('Vsd', 0)) == 0:
                        st.toast("Shear force is required(Vsd)", icon="⚠️")
            else:
                if st.button("Next →", use_container_width=True, type="primary", key="next_button_without_error"):
                    update_temp_from_input_multi([
                        'case_name', 'span_length', 'd', 'Vsd', 'import_option', 'widget_import_option'
                    ])
                    add_tab_switch_button("Next", tabs[1])


    with tab2:
        with st.container(height=800, border=False):
            st.markdown("<h6><b>Reinforced Condition</b></h6>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox(
                    "Shear Reinforcement Type",
                    ["Stirrup", "Others"],
                    index=0,
                    key="shear_reinforcement_type",
                    on_change=update_temp_from_input,
                    args=("shear_reinforcement_type", "shear_reinforcement_type"),
                    help="For stirrups, reduction factor ζ=0.9 when P_staffe<25mm. For others, ζ=0.35+0.026*P_staffe/d_mandrel when P_staffe<25mm. Otherwise ζ=1.0"
                )
                if st.session_state.bridge_type == "Road":
                    steel_type =st.session_state.steel_type = "Shear reinforcement"
                else:
                    steel_type =st.session_state.steel_type = "Straight and bent bars"

                mandrel = st.number_input(r"Mandrel diameter, $d_{mandrel}$ [mm]", 
                                value=float(st.session_state.get('d_mandrel', 40.0)),
                                key='d_mandrel', 
                                on_change=update_temp_from_input, 
                                args=('d_mandrel',))

 
                n_braccia = st.number_input(r"Number of Arms, $n_{braccia}$", 
                                value=float(st.session_state.get('n_braccia', 2)),
                                min_value=1.0,
                                step=0.5,
                                key='n_braccia', 
                                on_change=update_temp_from_input, 
                                args=('n_braccia',))
            with col2:
                p_staffe = st.number_input(r"Shear reinforcement diameter, $P_{staffe}$ [mm]", 
                                value=float(st.session_state.get('p_staffe', 10)),
                                key='p_staffe', 
                                on_change=update_temp_from_input, 
                                args=('p_staffe',))
 
                s = st.number_input(r"Shear reinforcement pitch, $s$ [mm]", 
                                value=float(st.session_state.get('s', 100)),
                                key='s', 
                                on_change=update_temp_from_input, 
                                args=('s',))

            st.markdown("<h6><b>Fatigue Traffic Condition</b></h6>", unsafe_allow_html=True)
            #교량 형태에 따른 팩터계산 도로교
            if st.session_state.bridge_type == "Road":
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
                        # st.number_input(
                        #     r"Number of loaded tracks, $N_{t}$", 
                        #     value=int(st.session_state.get('nt', 1)), 
                        #     key="widget_nt",
                        #     on_change=update_temp_from_input,
                        #     args=("widget_nt", "nt")
                        # )
                        roughness_category = safe_selectbox(
                            "Pavement Roughness",
                            ["Good", "Medium"],
                            default_index=1,
                            key="pavement_roughness", 
                            on_change=update_temp_from_input,
                            args=("pavement_roughness",)
                        )
                        # 카테고리에 따른 자동 계산값 설정
                        roughness_values = {
                            "Good": 1.2,
                            "Medium": 1.4,
                        }
                        
                        if roughness_category:
                            # 선택된 카테고리에 따라 자동으로 vol 값 설정
                            st.session_state.pie_fat = roughness_values.get(roughness_category, 0.00)
                        if st.session_state.bridge_type == "Road":
                            support_type = st.selectbox(
                                "Structure Type",
                                ["Continuous Beam", "Single Span Beam", "Carriageway Slab"],
                                index=0,
                                key="support_type_road",
                                on_change=update_temp_from_input,
                                args=("support_type_road",)
                            )


                    vol_auto_calc =  st.toggle("Auto Calculate Volume",
                                            value=st.session_state.get('vol_auto_calculate', True), 
                                            key="vol_auto_calculate_key",  
                                            on_change=update_temp_from_input,
                                            args=("widget_vol_auto_calculate", "vol_auto_calculate"))
                    
                    col1, col2 = st.columns(2)      

                    with col1:
                        # EN 1992-2 Table 4.5(n) 기반 교통 카테고리 선택 (항상 표시)
                        
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
            #교량 형태에 따른 팩터계산  레일
            else: # railway 일때의
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



        if st.session_state.bridge_type == "Road":
            # 유효성 검사 실패 여부 확인 함수
            def has_validation_errors2():
                # 기본 필드 검사
                if st.session_state.get('p_staffe', 0) == 0:
                    return True
                if st.session_state.get('s', 0) == 0:
                    return True
                if st.session_state.get('d_mandrel', 0) == 0:
                    return True
                if st.session_state.get('n_braccia', 0) == 0:
                    return True
                if st.session_state.get('nc', 0) == 0:
                    return True
                if st.session_state.get('vol', 0) == 0:
                    return True
                
                # 스팬 길이 유효성 검사 추가
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
                        st.session_state.span_error_message = f"Span length must be between {min_span}m and {max_span}m for {support_type} (current: {current_span}m)[UNI ENV 1992-2 Figure A106.2]"
                        return True
                    else:
                        st.session_state.span_error_message = None
                return False

        else: #레일일때
            def has_validation_errors2():
                if st.session_state.get('p_staffe', 0) == 0:
                    return True
                if st.session_state.get('s', 0) == 0:
                    return True
                if st.session_state.get('d_mandrel', 0) == 0:
                    return True
                if st.session_state.get('n_braccia', 0) == 0:
                    return True
                if st.session_state.get('nc', 0) == 0:
                    return True
                if st.session_state.get('vol', 0) == 0:
                    return True
                return False 
        validation_errors2 = has_validation_errors2()
                # 네비게이션 및 저장 버튼
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- Back", key="back_to_reinforced_traffic_condition", use_container_width=True):
                add_tab_switch_button("Back", tabs[0])
        with col3:
            if validation_errors2 :
                        if st.session_state.bridge_type == "Road":
                            if st.button("Next →", use_container_width=True, key="next_to_correction_factor", 
                                        disabled=False):
                                pass
                        else:
                            if st.button("Next →", use_container_width=True, key="next_to_correction_factor", 
                                        disabled=False):
                                pass
                        if abs(st.session_state.get('p_staffe', 0)) == 0:
                            st.toast("Please enter Shear reinforcement diameter(P_staffe)")
                        if abs(st.session_state.get('s', 0)) == 0:
                            st.toast("Please enter Shear reinforcement pitch(s)")
                        if abs(st.session_state.get('d_mandrel', 0)) == 0:
                            st.toast("Please enter Mandrel diameter(d_mandrel)")
                        if abs(st.session_state.get('n_braccia', 0)) == 0:
                            st.toast("Please enter Number of Arms(n_braccia)")
                        if abs(st.session_state.get('nc', 0)) == 0:
                            st.toast("Please enter Number of Tracks(Nc)")
                        if abs(st.session_state.get('vol', 0)) == 0:
                            st.toast("Please enter Traffic volume(vol)")

            else:

                
                with col3:
                    if st.button("Next →", use_container_width=True, key="next_to_correction_factor", type="primary",
                                disabled=has_validation_errors2()):
                        update_temp_from_input_multi([
                            'shear_reinforcement_type', 'vol_auto_calculate', 'd_mandrel', 'n_braccia',
                            'p_staffe', 's', 'nc', 'traffic_type_road', 'pavement_roughness',
                            'support_type_road', 'traffic_category_vol', 'vol', 'traffic_type_rail','traffic_category_vol',
                            'support_type_rail'
                        ])
                        add_tab_switch_button("Next", tabs[2])


    with tab3:
        with st.container(height=800, border=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h6><b>Correction Factor</b></h6>", unsafe_allow_html=True)
            with col2:
                st.toggle("Correction Factor Auto Calculate",
                    value=st.session_state.get('correction_factor_auto_calculate', True), 
                    key="correction_factor_auto_calculate",  
                    on_change=update_temp_from_input,
                    args=("correction_factor_auto_calculate", )
                    )


            if st.session_state.bridge_type == "Railway":
                if st.session_state.correction_factor_auto_calculate:
                    with st.container(border=True, ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("<h6>Moving load(for correction factor)</h6>", unsafe_allow_html=True, help="Stress ranges due to Load Model 71 on one (?σ₁, ?σ₂) or two tracks (?σ₁?₂)")
                        with col2:
                            autocorrection=st.toggle(
                                "Load From Midas Model", 
                                key="manual_input_correction", 
                                value=True, 
                                on_change=update_temp_from_input,
                                args=("manual_input_correction",)
                            )

                        col1, col2, col3 = st.columns(3,vertical_alignment="bottom")
                        with col1:
                            #하중2 모달불러오기
                            if st.button("Import", use_container_width=True, key="for_midas_nx_correction", disabled=not st.session_state.manual_input_correction):
                                civil_stress_import2("Import")
                        if autocorrection:
                            if not math.isnan(st.session_state.get('ds1', 0)):
                                st.session_state.delta_sigma_1 = st.session_state.get('ds1', 0)
                            if not math.isnan(st.session_state.get('ds12', 0)):
                                st.session_state.delta_sigma_12 = st.session_state.get('ds12', 0)
                        # if math.isnan(st.session_state.get('delta_sigma_1', 0)) and is_edit_mode:
                        #     st.session_state.widget_delta_sigma_1 = st.session_state.get('ds1', 0)
                        # if math.isnan(st.session_state.get('delta_sigma_12', 0)) and is_edit_mode:
                        #     st.session_state.widget_delta_sigma_12 = st.session_state.get('delta_sigma_12', 0)


                        with col2:
                            #civil max output 무빙 1트랙 압축
                            st.number_input(
                                r"$\Delta\sigma_{1}$", 
                                value=float(st.session_state.delta_sigma_1), 
                                step=0.5, 
                                key="widget_delta_sigma_1",
                                on_change=update_temp_from_input,
                                args=("widget_delta_sigma_1", "delta_sigma_1"),
                                disabled=st.session_state.manual_input_correction
                            )
                        if st.session_state.get('widget_delta_sigma_1', 0) != 0:
                            st.session_state.delta_sigma_1 = st.session_state.get('widget_delta_sigma_1', 0)
                        with col3:
                            #civil max output 무빙 2트랙 압축
                            st.number_input(
                                r"$\Delta\sigma_{1+2}$", 
                                value=float(st.session_state.delta_sigma_12), 
                                step=0.05, 
                                key="widget_delta_sigma_12",
                                on_change=update_temp_from_input,
                                args=("widget_delta_sigma_12", "delta_sigma_12"),
                                disabled=st.session_state.manual_input_correction
                            )
                        if st.session_state.get('widget_delta_sigma_12', 0) != 0:
                            st.session_state.delta_sigma_12 = st.session_state.get('widget_delta_sigma_12', 0)
            if st.session_state.get('span_error_message') == None:
                button_disabled = False
            else: 
                button_disabled = True
            if st.button("Calculate Correction Factors", use_container_width=True, 
                        key="road_calculate_correction_factors",
                        disabled=not st.session_state.correction_factor_auto_calculate or button_disabled):

                # 계산 함수 호출 람다계산
                if st.session_state.bridge_type == "Road":
                    if st.session_state.correction_factor_auto_calculate ==True:
                        lambda_s = calculate_lambda_s_values_road()
                    st.toast(f"Lambda coefficient calculation completed: λs = {lambda_s:.3f}", icon="✅")
                else: #레일 람다계산
                    update_temp_from_input_multi(['delta_sigma_1', 'delta_sigma_12'])
                    if st.session_state.get('delta_sigma_1', 0) == 0:
                       st.toast("Please enter value (Δσ₁).")
                    if st.session_state.get('delta_sigma_12', 0) == 0:
                        st.toast("Please enter value (Δσ₁₂).")
                    else:
                        if st.session_state.correction_factor_auto_calculate ==True:
                            lambda_s = cal_for_steel_desm_rail.calculate_lambda_s_values_rail()
                            st.toast(f"Lambda coefficient calculation completed: λs = {lambda_s:.3f}", icon="✅")

#람다입력
            if st.session_state.bridge_type == "Road":
                col1, col2 = st.columns(2)
                with col1:

                    st.number_input(
                        r"$\phi_{fat}$", 
                        min_value=0.0, 
                        value=float(st.session_state.get('pie_fat', 0.00)),
                        step=0.05, 
                        key="pie_fat",
                        on_change=update_temp_from_input,
                        args=("pie_fat", ),
                        disabled=st.session_state.correction_factor_auto_calculate
                    )
                    
                    # Lambda2
                    st.number_input(
                        r"$\lambda_{s2}$", 
                        min_value=0.0, 
                        value=float(st.session_state.get('lambda2', 0.00)),
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
                        value=float(st.session_state.get('lambda4', 0.00)),
                        step=0.05, 
                        key="lambda4",
                        on_change=update_temp_from_input,
                        args=("lambda4", ),
                        disabled=st.session_state.correction_factor_auto_calculate
                    )

                    
                with col2:
                    # Lambda1
                    st.number_input(
                        r"$\lambda_{s1}$", 
                        min_value=0.0, 
                        value=float(st.session_state.get('lambda1', 0.00)),
                        step=0.05, 
                        key="lambda1",
                        on_change=update_temp_from_input,
                        args=("lambda1", ),
                        disabled=st.session_state.correction_factor_auto_calculate
                ) 
                    # Lambda3
                    st.number_input(
                        r"$\lambda_{s3}$", 
                        min_value=0.0, 
                        value=float(st.session_state.get('lambda3', 0.00)),
                        step=0.05, 
                        key="lambda3",
                        on_change=update_temp_from_input,
                        args=("lambda3", ),
                        disabled=st.session_state.correction_factor_auto_calculate
                    )
                    if st.session_state.get("correction_factor_auto_calculate", False):
                        st.session_state.setdefault("lambda_s", 0.00)
                    else:
                        st.session_state["lambda_s"] = (
                            st.session_state.get('lambda1', 0.00) *
                            st.session_state.get('lambda2', 0.00) *
                            st.session_state.get('lambda3', 0.00) *
                            st.session_state.get('lambda4', 0.00)
                        )
                    # Lambda_s (총 보정계수)
                    st.number_input(
                        r"$\lambda_{s}$ (Total)", 
                        min_value=0.0, 
                        value=float(st.session_state.get('lambda_s', 0.00)),
                        step=0.05, 
                        key="lambda_s",
                        on_change=update_temp_from_input,
                        args=("lambda_s",),
                        disabled=True   
                    )
                # 스팬 길이 범위 에러 메시지 표시 (가장 먼저)
                if st.session_state.get('span_error_message'):
                    st.error(st.session_state.span_error_message)

            else: #레일람다다
                col1, col2 = st.columns(2)    
                with col1:
                    # Lambda1
                    st.number_input(
                        r"$\lambda_{s1}$", 
                        min_value=0.0, 
                        value=float(st.session_state.get('lambda1', 0.00)),
                        step=0.05, 
                        key="lambda1",
                        on_change=update_temp_from_input,
                        args=("lambda1",),
                        disabled=st.session_state.correction_factor_auto_calculate
                    )
                    # Lambda3
                    st.number_input(
                        r"$\lambda_{s3}$", 
                        min_value=0.0, 
                        value=float(st.session_state.get('lambda3', 0.00)),
                        step=0.05, 
                        key="lambda3",
                        on_change=update_temp_from_input,
                        args=("lambda3",),
                        disabled=st.session_state.correction_factor_auto_calculate
                    )
                    # Lambda_s (총 보정계수)
                    if st.session_state.get("correction_factor_auto_calculate", False):
                        st.session_state.setdefault("lambda_s", 0.00)
                    else:
                        st.session_state["lambda_s"] = (
                            st.session_state.get('lambda1', 0.00) *
                            st.session_state.get('lambda2', 0.00) *
                            st.session_state.get('lambda3', 0.00) *
                            st.session_state.get('lambda4', 0.00)
                        )
                    st.number_input(
                        r"$\lambda_{s}$ (Total)", 
                        min_value=0.0, 
                        value=float(st.session_state.get('lambda_s', 0.00)),
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
                        value=float(st.session_state.get('lambda2', 0.00)),
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
                        value=float(st.session_state.get('lambda4', 0.00)),
                        step=0.05, 
                        key="lambda4",
                        on_change=update_temp_from_input,
                        args=("lambda4", ),
                        disabled=st.session_state.correction_factor_auto_calculate
                    )


                        

            # 계수 계산 버튼
            # if st.button("Calculate Correction Factors", use_container_width=True, 
            #             disabled=not st.session_state.correction_factor_auto_calculate):
            #     # 계산 함수 호출
            #     lambda_s = cal_for_concrete_desm_road_ui.calculate_lambda_s_values()
            #     st.success(f"Lambda 계수 계산 완료: λs = {lambda_s:.3f}")
            # 계수 계산 버튼
        def has_validation_errors3():
            if st.session_state.get('lambda_s', 0) == 0:
                return True
            if st.session_state.bridge_type == "Railway" and st.session_state.correction_factor_auto_calculate:
                if st.session_state.get('widget_delta_sigma_1', 0) == 0:
                    return True
                if st.session_state.get('widget_delta_sigma_12', 0) == 0:
                    return True

            return False
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- back", use_container_width=True, key="fatigue_correction_back3"):
                add_tab_switch_button("Back", tabs[1])  # tabs[1]으로 변경
        validation_errors3 = has_validation_errors3()
        if validation_errors3:
            with col3:
                if st.button("Next →", use_container_width=True, key="next_button3_with_error3"):
                    if abs(st.session_state.get('lambda_s', 0)) == 0:
                        st.toast(r"Please enter value ($\lambda_s$)")
                if st.session_state.bridge_type == "Railway" and st.session_state.correction_factor_auto_calculate:
                    if st.session_state.get('widget_delta_sigma_1', 0) == 0:
                        st.toast("Please enter value (Δσ₁).")
                    if st.session_state.get('widget_delta_sigma_12', 0) == 0:
                        st.toast("Please enter value (Δσ₁₂).")
        else:
        # 네비게이션 버튼 첫페이지 저장
            with col3:
                if st.session_state.bridge_type == "Road":
                    if st.button("Calculate Fatigue Result  →", use_container_width=True, key="fatigue_correction_next3", type="primary"):
                        update_temp_from_input_multi(['manual_input_correction','lambda_s','lambda1','lambda2','lambda3','lambda4','s','steel_type', 'Es', 'Ec', 'n_steel', 'A_steel', 'vol', 'nc', 'd', 'span_length', 'delta_sigma_1', 'delta_sigma_12', 'lambda_s', 'correction_option', 'import_option', 'vol_auto_calculate'])
                        if st.session_state.correction_factor_auto_calculate ==True:
                            lambda_s = calculate_lambda_s_values_road()
                        calculate_results_road()
                        add_tab_switch_button("Next", tabs[3])
                else:
                    if st.button("Calculate Fatigue Result  →", use_container_width=True, key="fatigue_correction_next4", type="primary"):
                        update_temp_from_input_multi(['manual_input_correction','lambda_s','lambda1','lambda2','lambda3','lambda4','vol','s','steel_type', 'Es', 'Ec', 'n_steel', 'A_steel', 'vol', 'nc', 'd', 'span_length', 'delta_sigma_1', 'delta_sigma_12', 'lambda_s', 'correction_option', 'import_option', 'vol_auto_calculate'])
                        if st.session_state.correction_factor_auto_calculate ==True:
                            lambda_s = cal_for_steel_desm_rail.calculate_lambda_s_values_rail()
                        delta_sigma_equ = cal_for_steel_desm_rail.calculate_delta_sigma_equ_rail() 
                        is_ok = cal_for_steel_desm_rail.calculate_result_rail()
                        add_tab_switch_button("Next", tabs[3])

  
    with tab4:  

        if validation_errors1 or validation_errors2 or validation_errors3 :
            if st.session_state.bridge_type == "Road":
                with st.container(height=800, border=False):
                    st.error("Input values are not valid. Please check your input again.")
                    if abs(st.session_state.get('span_length', 0)) == 0:
                        st.error("Please enter span length(L).")
                    if abs(st.session_state.get('Vsd', 0)) == 0:
                        st.error("Please enter Shear load.(Vsd)")
                    if abs(st.session_state.get('d', 0)) == 0:
                        st.error("Please enter Effective height(d).")
                    # 스팬 길이 범위 에러 메시지 표시 (가장 먼저)
                    if st.session_state.get('span_error_message'):
                        st.error(st.session_state.span_error_message)
                        # calculate_results_road()
                        # st.rerun()
     
            # railway에 대한 오류 처리
            else:
                st.error("Input values are not valid. Please check your input again.")

                if abs(st.session_state.get('span_length', 0)) == 0:
                    st.error("Please enter span length(L).")
                if abs(st.session_state.get('d', 0)) == 0:
                    st.error("Please enter Effective height(d).")
                if abs(st.session_state.get('Vsd', 0)) == 0:
                    st.error("Please enter Shear load.(Vsd)")
                if abs(st.session_state.get('Es', 0)) == 0:
                    st.error("Please enter Es value(Es).")
                if abs(st.session_state.get('Ec', 0)) == 0:
                    st.error("Please enter Concrete elastic modulus(Ec).")
                if abs(st.session_state.get('n_steel', 0)) == 0:
                    st.error("Please enter Number of steel elements(n).")
                if abs(st.session_state.get('A_steel', 0)) == 0:
                    st.error("Please enter Steel area(A).")
                if abs(st.session_state.get('vol', 0)) == 0:
                    st.error("Please enter Tons of weight trains passing per year per track(vol).")
                if abs(st.session_state.get('nc', 0)) == 0:
                    st.error("Please enter Number of tracks(nc).")
                    
                # if st.button("Calculate Fatigue Result", key="calculate_fatigue_result3", use_container_width=True):
                #     lambda_s = cal_for_steel_desm_rail.calculate_lambda_s_values_rail()
                #     delta_sigma_equ = cal_for_steel_desm_rail.calculate_delta_sigma_equ_rail() 
                #     is_ok, discriminant = cal_for_steel_desm_rail.calculate_result_rail()
                #     st.rerun()

        else :
            with st.container(border=True, height=800):
                if st.session_state.get('input_changed', False):
                    st.warning("🔄 Input values have been changed. Please recalculate to see updated results.")
                    if st.button("Fatigue Result Recalculate", key="calculate_fatigue_result", use_container_width=True):
                        if st.session_state.bridge_type == "Road":
                            if st.session_state.correction_factor_auto_calculate ==True:
                                lambda_s = calculate_lambda_s_values_road()
                            calculate_results_road()    
                        else: #레일 람다계산
                            if st.session_state.correction_factor_auto_calculate ==True:
                                lambda_s = cal_for_steel_desm_rail.calculate_lambda_s_values_rail()
                            delta_sigma_equ = cal_for_steel_desm_rail.calculate_delta_sigma_equ_rail() 
                            is_ok = cal_for_steel_desm_rail.calculate_result_rail()

                        st.session_state.input_changed = False
                        st.rerun()

                # 결과 표시
                if st.session_state.bridge_type == "Road":

                    def chartdrawing():
                        # 현재 설정 정보 가져오기
                        current_support = st.session_state.get('support_type', '')
                        current_steel = st.session_state.get('steel_type', '')
                        current_span = st.session_state.get('span_length', 0.0)
                        
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

                    if all(k in st.session_state for k in ['area', 'sigma_s', 'delta_sigma_s_equ', 'stress_left', 'stress_right']):
                        st.markdown("<h6><b>Concrete Shear Fatigue Design Result(Road)</b></h6>", unsafe_allow_html=True)
                        with st.container(border=True, height=90):
                            col1, col2, col3, col4 = st.columns([10, 1, 9, 5], vertical_alignment="center")
                            with col1:
                                st.latex(r"\gamma_F \cdot \gamma_{Sd} \cdot \Delta\sigma_{s,equ} = " + f"{st.session_state.stress_left:.3f}\\text{{ MPa}}")
                            with col2:
                                st.latex(r"\leq" if st.session_state.is_ok =='OK' else r">")
                            with col3:
                                st.latex(r"\frac{\Delta\sigma_{Rsk} \cdot \zeta}{\gamma_{s,fat}} = " + f"{st.session_state.stress_right:.3f}\\text{{ MPa}}")
                            with col4:
                                if st.session_state.is_ok=='OK':
                                    st.markdown("<h5 style='color: green;'>OK</h5>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<h5 style='color: red;'>NG</h5>", unsafe_allow_html=True)
                        # 상세 계산 결과 표시
                        st.markdown("<h6><b>Detail Calculation of Concrete Shear Fatigue Design (Road)</b></h6>", unsafe_allow_html=True)
                        if st.session_state.correction_factor_auto_calculate ==False:
                            pass
                        else:
                            lambda1 = st.session_state.get('lambda1', 0.0)
                            st.write(r"Correction factor of $\lambda_{s,1}$ = " + f"{lambda1:.3f}")
                            with st.container(border=True, height=620):
                                if st.session_state.bridge_type == "Road":
                                    support_type = st.session_state.get('support_type_road', '')
                                    traffic_type = st.session_state.get('traffic_type_road', '')
                                else:
                                    support_type = st.session_state.get('support_type_rail', '')
                                    traffic_type = st.session_state.get('traffic_type_rail', '')
                                steel_type = st.session_state.get('steel_type', '')
                                span_length = st.session_state.get('span_length', 0.0)

                                
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
                            with st.container(border=True, height=250):
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

                        pie_fat = st.session_state.get('pie_fat', 0.00)
                            # Lambda_s 총 보정계수 계산
                        lambda1 = st.session_state.get('lambda1', 0.0)
                        lambda2 = st.session_state.get('lambda2', 0.0)
                        lambda3 = st.session_state.get('lambda3', 0.0)
                        lambda4 = st.session_state.get('lambda4', 0.0)
                        lambda_s = st.session_state.get('lambda_s', 0.0)
                        st.write(r"Total correction factor $\lambda_{s}$ = " + f"{lambda_s:.3f}")
                        with st.container(border=True, height=60):
                            st.latex(r"\lambda_{s} = \phi_{fat} \cdot \lambda_{s,1} \cdot \lambda_{s,2} \cdot \lambda_{s,3} \cdot \lambda_{s,4} = " + 
                                    f"{pie_fat:.3f}" + r" \cdot " + f"{lambda1:.3f}" + r" \cdot " + f"{lambda2:.3f}" + r" \cdot " + 
                                    f"{lambda3:.3f}" + r" \cdot " + f"{lambda4:.3f}" + r" = " + f"{lambda_s:.3f}")
                        # 기본 값 표시
                        # st.markdown("<h6><b>Input Parameters</b></h6>", unsafe_allow_html=True)
                        # with st.container(border=True, height=200):
                        #     col1, col2, col3 = st.columns(3)
                        #     with col1:
                        #         st.latex(r"V_{sd} = " + f"{abs(st.session_state.Vsd):.3f}\t{{ kN}}")
                        #         st.latex(r"s = " + f"{st.session_state.s}\t{{ mm}}")
                        #         st.latex(r"d = " + f"{st.session_state.d}\t{{ mm}}")

                        #     with col2:
                        #         st.latex(r"\lambda_s = " + f"{st.session_state.lambda_s}")
                        #         st.latex(r"\Delta\sigma_{Rsk} = " + f"{st.session_state.delta_sigma_Rsk}\t{{ MPa}}")
                        #         st.latex(r"P_{staffe} = " + f"{st.session_state.p_staffe}\t{{ mm}}")
                        #     with col3:
                        #         st.latex(r"\gamma_{F} = " + f"{st.session_state.factor_rf}")
                        #         st.latex(r"\gamma_{fat} = " + f"{st.session_state.factor_rsfat}")
                        #         st.latex(r"n_{braccia} = " + f"{st.session_state.n_braccia}")
                        # 응력 계산
                        st.markdown("<h6><b>Fatigue Result Calculation(Road)</b></h6>", unsafe_allow_html=True)
                        st.markdown(r"Stirrup Area: $A_s = \frac{\pi \cdot P_{staffe}^2}{4}  \cdot n_{braccia} = " + f"{st.session_state.area:.3f}" + r"\text{ mm²}$", unsafe_allow_html=True)
                        st.markdown(r"Stress in Reinforcement: $\sigma_s = \frac{V_{sd} \cdot s}{0.9 \cdot d \cdot A_s} = " + f"{st.session_state.sigma_s:.3f}" + r"\text{ MPa}$", unsafe_allow_html=True)
                        st.markdown(r"Equivalent Stress Range: $\Delta\sigma_{s,equ} = \sigma_s \cdot \lambda_s  =" + 
                                f"{st.session_state.sigma_s:.3f}" + r"\cdot "+ f"{st.session_state.lambda_s:.3f} =  {st.session_state.delta_sigma_s_equ:.3f}" +r"\text{ MPa}$", unsafe_allow_html=True)
                        st.markdown(r"Resistance Stress Range: $\sigma_{Rsk} =" + f"{st.session_state.delta_sigma_Rsk:.3f}" + r"\text{ MPa}$", unsafe_allow_html=True)
                        # 검증 기준
                        with st.container(border=True, height=290):
                            # 조건식 표시
                        # if  p_staffe < 25 and shear_reinforcement_type == "Stirrup":
                        #     reduction_factor = 0.9
                        # elif  p_staffe < 25 and shear_reinforcement_type == "Others":
                        #     reduction_factor = 0.35 +0.026*p_staffe/d_mandrel
                        # else:
                        #     reduction_factor =1 
                            # 상세 값 표시
                            # 상세 값 표시 결과표시
                            col1, col2, col3, col4 = st.columns([10, 1, 9, 5],vertical_alignment="center")
                            with col1:
                                st.latex(r"\gamma_F \cdot \gamma_{Sd} \cdot \Delta\sigma_{s,equ} = " + f"{st.session_state.stress_left:.3f}\t{{ MPa}}")
                            with col2:
                                st.latex(r"\leq" if st.session_state.is_ok=='OK' else r">")
                            with col3:
                                st.latex(r"\frac{\Delta\sigma_{Rsk} \cdot \zeta}{\gamma_{s,fat}} = " + f"{st.session_state.stress_right:.3f}\t{{ MPa}}")
                            with col4:
                                if st.session_state.is_ok=='OK':
                                    st.markdown("<h5>OK</h5>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<h5>NG</h5>", unsafe_allow_html=True)

                            # 변수 설명 추가
                            st.markdown("**where :**")
                            st.markdown(rf"""
                            - $\gamma_F = {st.session_state.get('factor_rf', 1.0)}$ (Partial factor for fatigue actions)  
                            - $\gamma_{{Sd}} = {st.session_state.get('factor_rsd', 1.0)}$ (Partial factor for uncertainty)  
                            - $\Delta\sigma_{{s,equ}} = {st.session_state.delta_sigma_s_equ:.3f}$ MPa (Equivalent stress range)  
                            - $\Delta\sigma_{{Rsk}} = {st.session_state.get('delta_sigma_Rsk', 0):.3f}$ MPa (Characteristic fatigue strength)  
                            - $\zeta = {st.session_state.get('reduction_factor', 1.0):.3f}$ (Reduction factor)  
                            - $\gamma_{{s,fat}} = {st.session_state.get('factor_rsfat', 1.15)}$ (Partial factor for fatigue of reinforcing steel)
                            """)
                        
                            if st.session_state.p_staffe < 25 and st.session_state.shear_reinforcement_type == "Stirrup":
                                st.markdown(r"<small>Note) Reduction factor for stirrups : $\zeta = " + f"{st.session_state.reduction_factor:.3f}$</h7>", unsafe_allow_html=True)
                            elif st.session_state.p_staffe < 25 and st.session_state.shear_reinforcement_type == "Others":
                                st.markdown(r"<small>Note) Reduction factor for others : $\zeta = 0.35 + 0.026 \cdot \frac{P_{staffe}}{d_{mandrel}} = 0.35 + 0.026 \cdot \frac{" + f"{st.session_state.p_staffe:.3f}" + "}{" + f"{st.session_state.d_mandrel:.3f}" + "} = " + f"{st.session_state.reduction_factor:.3f}" + r"$</small>", unsafe_allow_html=True)
                            else:
                                st.markdown(r"<h8>Note) Reduction factor : $\zeta = 1$</h8>", unsafe_allow_html=True)
                # railway에 대한 결과
                else:
                    # 3개 열로 나누기
                        st.markdown("<h6><b>Concrete Shear Fatigue Design Result(Railway)</b></h6>", unsafe_allow_html=True)
                        
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
                                st.latex(r"\frac{\Delta\sigma_{Rsk} \cdot \zeta}{\gamma_{s,fat}} = " + f"{right_side:.3f}\\text{{ MPa}}")
                            with col4:
                                if is_ok:
                                    st.markdown("<h5 style='color: green;'>OK</h5>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<h5 style='color: red;'>NG</h5>", unsafe_allow_html=True)
                        
                        # 상세 계산 결과 표시
                        st.markdown("<h6><b>Detail Calculation of Concrete Shear Fatigue Design(Railway)</b></h6>", unsafe_allow_html=True)

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

                        lambda1 = st.session_state.get('lambda1', 0.0)
                        lambda2 = st.session_state.get('lambda2', 0.0)
                        lambda3 = st.session_state.get('lambda3', 0.0)
                        lambda4 = st.session_state.get('lambda4', 0.0)
                        # Lambda_s 총 보정계수 계산
                        lambda_s = st.session_state.get('lambda_s', 0.0)
                        st.write(r"Total correction factor $\lambda_{s}$ = " + f"{lambda_s:.3f}")
                        with st.container(border=True, height=80):
                            st.latex(r"\lambda_{s} = \lambda_{s,1} \cdot \lambda_{s,2} \cdot \lambda_{s,3} \cdot \lambda_{s,4} = " + 
                                    f"{lambda1:.3f}" + r" \cdot " + f"{lambda2:.3f}" + r" \cdot " + 
                                    f"{lambda3:.3f}" + r" \cdot " + f"{lambda4:.3f}" + r" = " + f"{lambda_s:.3f}")
                        

                        
                        delta_sigma_equ = st.session_state.get('delta_sigma_equ', 0.0)
                        section_type = st.session_state.get('section_type')

                        gamma_s_fat = st.session_state.get('factor_rsfat', 1.15)
                        # 판정 계산 표시
                        st.markdown("<h6><b>Fatigue Result Calculation(Railway)</b></h6>", unsafe_allow_html=True)
                        # 등가 응력 범위 계산 표시
                        # st.write("Equivalent Stress Calculation")
                        # if section_type == "Uncracked section":
                        #레일결과
                        st.markdown(r"Stirrup Area: $A_s = \frac{\pi \cdot P_{staffe}^2}{4}  \cdot n_{braccia} = " + f"{st.session_state.area:.3f}" + r"\text{ mm²}$", unsafe_allow_html=True)
                        st.markdown(r"Stress in Reinforcement: $\sigma_s = \frac{V_{sd} \cdot s}{0.9 \cdot d \cdot A_s} = " + f"{st.session_state.sigma_s:.3f}" + r"\text{ MPa}$", unsafe_allow_html=True)
                        st.markdown(r"Equivalent Stress Range: $\Delta\sigma_{s,equ} = \sigma_s \cdot \lambda_s  =" + 
                                f"{st.session_state.sigma_s:.3f}" + r"\cdot"+ f"{st.session_state.lambda_s:.3f} = {st.session_state.sigma_s_equ:.3f}" +r"\text{ MPa}$", unsafe_allow_html=True)
                        st.markdown(r"Resistance Stress Range: $\sigma_{Rsk} =" + f"{st.session_state.delta_sigma_Rsk:.3f}" + r"\text{ MPa}$", unsafe_allow_html=True)

                        
                        # else:
                        #     st.latex(r"\Delta\sigma_{s,equ} = \lambda_s \cdot \Delta\sigma_1 \cdot 5 = " + 
                        #         f"{lambda_s:.3f} \cdot {delta_sigma_1:.1f} \cdot 5 = {delta_sigma_equ:.1f}" + r" \text{ MPa}")
                            # st.markdown("Note: For cracked sections, a factor of 5 is applied according to EN 1992-2.")
                        right_side = st.session_state.get('right_side', 0.0)
                        gamma_F = st.session_state.get('gamma_F', 1.0)
                        gamma_Sd = st.session_state.get('gamma_Sd', 1.0)
                        gamma_fat = st.session_state.get('gamma_fat', 1.15)
                        delta_sigma_Rsk = st.session_state.get('delta_sigma_Rsk', 162.5)
                        # st.markdown(
                        #     r"Design strength check: $\frac{\Delta\sigma_{Rsk}}{\gamma_{s,fat}} = \frac{" + 
                        #     f"{delta_sigma_Rsk:.3f}" + "}{" + f"{gamma_s_fat:.3f}" + "} = " + 
                        #     f"{right_side:.3f}" + r"\text{ MPa}$", 
                        #     unsafe_allow_html=True
                        # )
                        #레일결과
                        with st.container(border=True, height=280):
                            # Main equation at the top
                            # st.latex(r"\gamma_F \cdot \gamma_{Sd} \cdot \Delta\sigma_{s,equ} \leq \frac{\Delta\sigma_{Rsk} \cdot \zeta}{\gamma_{s,fat}}")
                            
                            # Horizontal comparison layout
                            col1, col2, col3, col4 = st.columns([10, 1, 9, 5], vertical_alignment="center")
                            with col1:
                                st.latex(r"\gamma_F \cdot \gamma_{Sd} \cdot \Delta\sigma_{s,equ} = " + f"{left_side:.3f}\t{{ MPa}}")
                            with col2:
                                st.latex(r"\leq" if is_ok else r">")
                            with col3:
                                st.latex(r"\frac{\Delta\sigma_{Rsk} \cdot \zeta}{\gamma_{s,fat}} = " + f"{right_side:.3f}\t{{ MPa}}")
                            with col4:
                                if is_ok:
                                    st.markdown("<h5>OK</h5>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<h5>NG</h5>", unsafe_allow_html=True)

                            # 변수 설명 추가
                            st.markdown("**where :**")
                            st.markdown(f"""
                            - γF = {st.session_state.get('factor_rf', 1.0)} (Partial factor for fatigue actions)
                            - γSd = {st.session_state.get('factor_rsd', 1.0)} (Partial factor for uncertainty)  
                            - Δσs,equ = {st.session_state.get('delta_sigma_equ', 0):.3f} MPa (Equivalent stress range)
                            - ΔσRsk = {st.session_state.get('delta_sigma_Rsk', 0):.3f} MPa (Characteristic fatigue strength)
                            - ζ = {st.session_state.get('reduction_factor', 1.0):.3f} (Reduction factor)
                            - γs,fat = {st.session_state.get('factor_rsfat', 1.15)} (Partial factor for fatigue of reinforcing steel)
                            """)
                            
                            if st.session_state.p_staffe < 25 and st.session_state.shear_reinforcement_type == "Stirrup":
                                st.markdown(r"<small>Note) Reduction factor for stirrups : $\zeta = " + f"{st.session_state.reduction_factor:.3f}$</h7>", unsafe_allow_html=True)
                            elif st.session_state.p_staffe < 25 and st.session_state.shear_reinforcement_type == "Others":
                                st.markdown(r"<small>Note) Reduction factor for others : $\zeta = 0.35 +0.026 \cdot \frac{P_{staffe}}{d_{mandrel}} = " + f"{st.session_state.reduction_factor:.3f}$</h8>", unsafe_allow_html=True)
                            else:
                                st.markdown(r"<small>Note) Reduction factor : $\zeta = 1.0$</h8>", unsafe_allow_html=True)
                # if st.session_state.is_ok:
                #     st.success("판정 결과: OK - The shear stress satisfies the fatigue resistance requirement")
                # else:
                #     st.error("판정 결과: NG - The shear stress does not satisfy the fatigue resistance requirement")
        # 네비게이션 및 저장 버튼
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<- Back", key="back_to_fatigue_settings", use_container_width=True):
                add_tab_switch_button("Back", tabs[2])
        
        with col3:
            button_text = "Update" if is_edit_mode else "Save Result"
            if st.button(button_text, key="save_fatigue_result", use_container_width=True, type="primary"):
                # 계산 수행 (아직 수행되지 않은 경우)
                if 'is_ok' not in st.session_state:
                    if not calculate_results_road():
                        st.error("계산을 먼저 수행해주세요.")
                        return
                update_temp_from_input_multi([
                    'case_name', 'span_length', 'd', 'Vsd', 'import_option', 'widget_import_option',
                    'shear_reinforcement_type', 'vol_auto_calculate', 'd_mandrel', 'n_braccia',
                    'p_staffe', 's', 'nc', 'traffic_type_road', 'pavement_roughness',
                    'support_type_road', 'traffic_category_vol', 'vol', 'traffic_type_rail',
                    'support_type_rail', 'delta_sigma_1', 'delta_sigma_12', 'lambda_s', 
                    'correction_option', 'area', 'sigma_s', 'delta_sigma_s_equ', 
                    'delta_sigma_Rsd', 'delta_sigma_Rsk', 'reduction_factor', 'stress_left', 
                    'stress_right', 'is_ok', 'discriminant','traffic_category_vol'
                ])
                # temp_result_df 업데이트
                if 'temp_result_df' in st.session_state and not st.session_state.temp_result_df.empty:
                    # 케이스 정보 업데이트
                    st.session_state.temp_result_df.at[0, 'case_id'] = st.session_state.case_name
                    st.session_state.temp_result_df.at[0, 'case_method'] = "Concrete Shear(Require Reinforcement)"
                    
                    # 판정값 저장
                    st.session_state.temp_result_df.at[0, 'is_ok'] = st.session_state.is_ok
                    
                    # save_to_result_df 함수 사용하여 저장
                    if save_to_result_df():
                        st.success(f"'{st.session_state.case_name}' 케이스가 저장되었습니다.")
                        back_to_fatigue_case()
                    else:
                        st.error("저장 중 오류가 발생했습니다.")
                else:
                    st.error("저장할 데이터가 없습니다.")

# with st.container(border=True, height=600):
#     debug_df = st.session_state.temp_result_df
#     st.dataframe(debug_df)  
#     debug_result_df = st.session_state.result_df
#     st.dataframe(debug_result_df)
#     st.sidebar.write("Session Values:", st.session_state)


#    # 디버깅 정보 표시 (옵션)
#     if st.sidebar.checkbox("Show Debug Info"):
#         st.sidebar.subheader("Debug Session State")
#         st.sidebar.write("Edit Mode:", is_edit_mode)
#         st.sidebar.write("Case Name:", st.session_state.get('case_name', 'None'))
        
#         st.sidebar.write("Session Values:", {
#             'case_name': st.session_state.case_name,
#             'design_factor': st.session_state.design_factor,
#             'stress': st.session_state.stress,
#             'Fatigue_method': st.session_state.Fatigue_method,
#             'fcm': st.session_state.get('fcm', 'Not set'),
#             'fcd': st.session_state.get('fcd', 'Not calculated'),
#             'discriminant': st.session_state.get('discriminant', 'Not calculated')
#         })
#         if st.button("🧪 temp_result_df 초기화"):
#             if 'temp_result_df' in st.session_state:
#                 del st.session_state.temp_result_df
#                 st.session_state.temp_result_df = pd.DataFrame()
#             st.success("temp_result_df가 초기화되었습니다.")
#         st.sidebar.write("Temp DF:", st.session_state.get('temp_result_df'))
#         if st.sidebar.checkbox("Show Result DF"):
#             st.sidebar.write("Result DF:", st.session_state.get('result_df'))

'''
Concrete Shear Fatigue (Require Reinforcement) 입력값 정리
1page (Fatigue Settings)

case_name - 케이스 이름
span_length - 경간 길이 (m)
support_type - 구조 형식 ("Continuous Beam", "Single Span Beam", "Carriageway Slab")
d - 유효 단면 높이 (mm)
Vsd - 피로하중에 의한 전단력 (kN)

2page (Reinforced & Traffic Condition)

shear_reinforcement_type - 전단보강근 형식 ("Stirrup", "Others")
d_mandrel - 맨드렐 직경 (mm)
steel_type - 강재 유형 ("Shear reinforcement" 고정)
n_braccia - 전단보강근 가닥 수
p_staffe - 전단보강근 직경 (mm)
s - 전단보강근 간격 (mm)
nc - 차선 수
nt - 적재 차선 수
traffic_type - 교통 유형 ("Long distance", "Medium distance", "Local traffic")
pavement_roughness - 포장 거칠기 ("Good", "Medium")
vol_auto_calculate - 교통량 자동 계산 여부
traffic_category_vol - 도로 교통 카테고리
vol - 연간 중차량 통과량

3page (Correction Factor)

correction_factor_auto_calculate - 보정계수 자동 계산 여부
pie_fat - φfat 계수
lambda1 - λs,1 보정계수
lambda2 - λs,2 보정계수
lambda3 - λs,3 보정계수
lambda4 - λs,4 보정계수
lambda_s - 총 보정계수

4page (Fatigue Result)
자동 계산값

area - 스터럽 면적
sigma_s - 보강근 응력
delta_sigma_s_equ - 등가 응력 범위
delta_sigma_Rsd - 허용 응력 범위
delta_sigma_Rsk - 기준 응력 범위
reduction_factor - 감소계수
stress_left - 좌변값 (γF × γSd × Δσs,equ)
stress_right - 우변값 (ΔσRsk × ζ / γs,fat)
is_ok - 판정 결과 ("OK"/"NG")
discriminant - 판정값 (여유도)

추가 세션 상태 변수

bridge_type - 교량 유형 ("Road"/"Railway")
factor_rsfat - 철근 피로 안전계수
factor_rf - 하중 안전계수
nyear - 설계 수명 (년)
k2 - S-N 곡선 지수'''