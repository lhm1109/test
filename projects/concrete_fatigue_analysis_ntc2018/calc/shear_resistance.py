# calc/shear_resistance.py
import math
import pandas as pd
import numpy as np
import streamlit as st
import requests

# 전역 변수로 설정된 주요 파라미터들
if st.session_state.get('Fatigue_method') == "Concrete Shear(Not Require Reinforcement)" and st.session_state.get('temp_result_df', {}).get('element_number_Vsdmax') is not None:
    get_Elem = st.session_state.get('temp_result_df', {}).get('element_number_Vsdmax', 0)[0]
    get_ij = st.session_state.get('temp_result_df', {}).get('element_part_Vsdmax', 0)[0]
    get_load_case_name = st.session_state.get('temp_result_df', {}).get('shear_load_case', 0)[0]
else:
    pass
get_Part = "Minimum"
get_Section_Part = "1" #Comosite Section 에서 아래 (고정)

 
st.session_state.section_properties_df
# st.session_state.get_d = section_properties.get('girder_height', 0)  # 또는 실제 키 이름
# st.session_state.get_bw = section_properties.get('bw', 0)
# st.session_state.get_Qn = section_properties.get('qn_girder_totcenter', 0)
# st.session_state.get_J = section_properties.get('iyy_girder', 0)
# st.session_state.get_total_centroid_height = section_properties.get('total_centroid_height', 0)
# st.session_state.get_girder_centroid_height = section_properties.get('girder_centroid_height', 0)
# st.session_state.get_girder_height = section_properties.get('girder_height', 0)
# st.session_state.get_total_area = section_properties.get('total_area', 0)
# st.session_state.get_total_first_moment = section_properties.get('total_first_moment', 0)
# st.session_state.get_iyy_total = section_properties.get('iyy_total', 0)



# section properties for girder
get_section_area = st.session_state.get_total_area
get_section_second_moment_y = st.session_state.get_iyy_total
get_section_yb = st.session_state.get_total_centroid_height
get_first_qn = st.session_state.get_Qn 
get_section_second_moment_Ig = st.session_state.get_J
get_bw = st.session_state.get_bw
get_totalHeight = st.session_state.get_total_height
get_girder_centroid_height = st.session_state.get_girder_centroid_height
# section properties for composite section
get_first_qc_composite = st.session_state.get_total_first_moment
get_section_second_moment_Ic = st.session_state.get_iyy_total

def extract_construction_stage_values_local(response_data):
    # 응답 데이터에서 실제 데이터 추출
    if 'Example' in response_data:
        data_info = response_data['Example']
        headers = data_info['HEAD']
        data_rows = data_info['DATA']
    else:
        # 다른 키 이름인 경우 첫 번째 키 사용
        first_key = list(response_data.keys())[0]
        data_info = response_data[first_key]
        headers = data_info['HEAD']
        data_rows = data_info['DATA']
    
    # 데이터프레임 생성
    df = pd.DataFrame(data_rows, columns=headers)
    
    # 숫자 컬럼들을 float로 변환
    numeric_columns = ['Axial', 'Shear-y', 'Shear-z', 'Torsion', 'Moment-y', 'Moment-z']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Min/Max 스테이지 제외
    df_filtered = df[~df['Stage'].str.contains('Min/Max|MIN|MAX|min|max', case=False, na=False)]
    
    # 고유 스테이지 목록 확인
    unique_stages = df_filtered['Stage'].unique()
    first_stage = unique_stages[0] if len(unique_stages) > 0 else None
    last_stage = unique_stages[-1] if len(unique_stages) > 0 else None
    
    moment_y_at_max_shear = None
    max_axial_tendon = None
    shear_max = None
    
    # 첫 번째 스테이지 처리
    if first_stage:
        first_stage_data = df_filtered[df_filtered['Stage'] == first_stage].copy()
        
        if not first_stage_data.empty:
            steps_in_first_stage = first_stage_data['Step'].unique()
            last_steps = [step for step in steps_in_first_stage if 'last' in step.lower()]
            last_step_first_stage = last_steps[0] if last_steps else steps_in_first_stage[-1]
            
            summation_data = first_stage_data[
                (first_stage_data['Step'] == last_step_first_stage) & 
                (first_stage_data['Load'] == 'Summation')
            ].copy()
            
            if not summation_data.empty:
                summation_data['abs_shear_z'] = summation_data['Shear-z'].abs()
                max_shear_idx = summation_data['abs_shear_z'].idxmax()
                shear_max = summation_data.loc[max_shear_idx, 'Shear-z']
                moment_y_at_max_shear = summation_data.loc[max_shear_idx, 'Moment-y']
    
    # 마지막 스테이지 처리
    if last_stage:
        last_stage_data = df_filtered[df_filtered['Stage'] == last_stage].copy()
        
        if not last_stage_data.empty:
            steps_in_last_stage = last_stage_data['Step'].unique()
            last_steps = [step for step in steps_in_last_stage if 'last' in step.lower()]
            last_step_last_stage = last_steps[0] if last_steps else steps_in_last_stage[-1]
            
            tendon_data = last_stage_data[
                (last_stage_data['Step'] == last_step_last_stage) & 
                (last_stage_data['Load'] == 'Tendon Primary')
            ].copy()
            
            if not tendon_data.empty:
                tendon_data['abs_axial'] = tendon_data['Axial']
                max_axial_tendon = tendon_data['abs_axial'].max()
    
    return {
        'abs_shear_z': shear_max,
        'moment_y_at_max_shear': moment_y_at_max_shear,
        'max_axial_tendon': max_axial_tendon,
        'first_stage': first_stage,
        'last_stage': last_stage,
        'all_stages': df['Stage'].unique().tolist(),
        'filtered_stages': unique_stages.tolist()
    }

def calculate_shear_resistance():
    # MV 하중 케이스 찾기 로직
# 전역 변수로 설정된 주요 파라미터들
    if st.session_state.get('Fatigue_method') == "Concrete Shear(Not Require Reinforcement)" and st.session_state.get('temp_result_df', {}).get('element_number_Vsdmax') is not None:
        get_Elem = st.session_state.get('temp_result_df', {}).get('element_number_Vsdmax', 0)[0]
        get_ij = st.session_state.get('temp_result_df', {}).get('element_part_Vsdmax', 0)[0]
        get_load_case_name = st.session_state.get('temp_result_df', {}).get('shear_load_case', 0)[0]
    get_section_area = st.session_state.get_total_area
    get_section_second_moment_y = st.session_state.get_iyy_total
    get_section_totla_yb = st.session_state.get_total_centroid_height
    get_section_yb= st.session_state.get_girder_centroid_height
    get_first_qn = st.session_state.get_Qn 
    get_section_second_moment_Ig = st.session_state.get_J
    get_bw = st.session_state.get_bw
    get_totalHeight = st.session_state.get_total_height
    # section properties for composite section
    get_first_qc_composite = st.session_state.get_total_first_moment
    get_section_second_moment_Ic = st.session_state.get_iyy_total
    get_girder_centroid_height = st.session_state.get_girder_centroid_height


    mapi_key = st.session_state.get('current_mapi_key', '')
    base_url = st.session_state.get('current_base_url', '')
    headers = {"MAPI-Key": mapi_key}
    
    if not mapi_key or not base_url:
        st.error("API 설정을 찾을 수 없습니다. 먼저 로그인해주세요.")
        return None

    # 하중 케이스 데이터 요청
    load_responses = [
        requests.get(f"{base_url}/db/lcom-{type}", headers=headers) 
        for type in ['gen', 'conc', 'steel', 'steel-conc', 'stlcomp', 'seismic']
    ]
    
    all_comb_data = [response.json() for response in load_responses]
    (st.session_state.shear_load_case)
    # MV 하중 케이스 찾기
    mv_load_case = None
    shear_load_case = st.session_state.shear_load_case.split('(')[0] # 괄호 이전 부분만 추출
    
    for data in all_comb_data:
        for key in data.keys():
            if key.startswith('LCOM-'):
                for case_num, case_data in data[key].items():
                    if case_data.get('NAME') == shear_load_case:
                        for comb in case_data.get('vCOMB', []):
                            if comb.get('ANAL') == 'MV':
                                mv_load_case = comb.get('LCNAME')
                                break
                        if mv_load_case:
                            break
                if mv_load_case:
                    break
        if mv_load_case:
            break

    if not mv_load_case:
        st.error("MV load case not found. (Check if Midas Civil Post is set to CS stage)")

        return None

    # 하중 케이스 저장
    mvloadlist = st.session_state['mv_load_case'] = [f"{mv_load_case}(MV:max)", f"{mv_load_case}(MV:min)"]
    
    # 응력 데이터 요청
    mv_request_data_stress = {
        "Argument": {
            "TABLE_NAME": "BeamForceViewByMaxValue",
            "TABLE_TYPE": "BEAMFORCEVBM",
            "EXPORT_PATH": "C:\\MIDAS\\Result\\Output.JSON",
            "UNIT": {
                "FORCE": "N",
                "DIST": "mm"
            },
            "STYLES": {
                "FORMAT": "Fixed",
                "PLACE": 4
            },
            "COMPONENTS": [
                "Elem", "Load", "Part", "Component", 
                "Axial", "Shear-y", "Shear-z", 
                "Torsion", "Moment-y", "Moment-z"
            ],
            "NODE_ELEMS": {
                "KEYS": [float(get_Elem)]
            },
            "LOAD_CASE_NAMES": mvloadlist,
            "PARTS": ["PartI", "PartJ"],
            "ITEM_TO_DISPLAY": ["Shear-z"]
        }
    }

    mv_response_stress = requests.post(f"{base_url}/post/Table", headers=headers, json=mv_request_data_stress)
    response_data = mv_response_stress.json()

    mvloadstress_dict = {}

    if 'BeamForceViewByMaxValue' in response_data:
        data_list = response_data['BeamForceViewByMaxValue']['DATA']
        
        for row in data_list:
            elem = row[1]      # Element 번호
            load_name = row[2] # 무빙 로드 이름 (max, min)
            part = row[3]      # Part (I or J)
            moment_y = float(row[9])  # Moment-y 값
            axial = float(row[5])     # Axial 값
            
            mvloadstress = moment_y / get_section_second_moment_Ig * get_section_yb + axial / get_section_area
            
            # 딕셔너리에 Element, 로드 이름, Part를 키로 사용
            mvloadstress_dict[(elem, load_name, part)] = mvloadstress

    # print(mvloadstress_dict)

    # 추가 계산 로직
# Modified stress calculation section
# Modified stress calculation section
    if st.session_state.civil_result_conststage_df is not None:
        df = st.session_state.civil_result_conststage_df
        df = df.drop(columns=['Axial', 'Bend(+y)', 'Bend(-y)', 'Bend(+z)', 'Bend(-z)', 
                            'Cb(min/max)', 'Sax(Warping)1', 'Sax(Warping)2', 
                            'Sax(Warping)3', 'Sax(Warping)4'])

        elem_to_find = str(get_Elem)     
        df = df[df['Elem'].astype(str).isin([elem_to_find])]
        df = df.iloc[:-8]
        df = df.iloc[-4:]

        # Convert stress columns to numeric for calculation
        df['Cb1(-y+z)'] = pd.to_numeric(df['Cb1(-y+z)'], errors='coerce')
        df['Cb2(+y+z)'] = pd.to_numeric(df['Cb2(+y+z)'], errors='coerce') 
        df['Cb3(+y-z)'] = pd.to_numeric(df['Cb3(+y-z)'], errors='coerce')
        df['Cb4(-y-z)'] = pd.to_numeric(df['Cb4(-y-z)'], errors='coerce')

        # Filter by section part
        df = df[df['Section Part'] == get_Section_Part]
        
        # Create stress dictionary - 이제 16개 조합을 모두 고려
        comb_stress_dict = {}
        
        for _, row in df.iterrows():
            elem = str(row['Elem'])
            part = row['Part']
            print(f"elem: {elem}, part: {part}")
            
            # Extract all four stress values for this row
            cb_stresses = [
                row['Cb1(-y+z)'],
                row['Cb2(+y+z)'],
                row['Cb3(+y-z)'],
                row['Cb4(-y-z)']
            ]
            
            # 각 part에 대해 max와 min 모두 처리
            stress_list = []
            
            # mvloadstress_dict에서 이 element와 part에 해당하는 모든 조합 찾기
            for (mv_elem, load_name, mv_part), mv_stress in mvloadstress_dict.items():
                print(f"mv_elem: {mv_elem} ,  load_name: {load_name} ,  mv_part: {mv_part} ,  mv_stress: {mv_stress}")
                # mv_part에서 [숫자] 부분 제거하여 비교
                clean_mv_part = mv_part.split('[')[0]  # I[2] -> I
                
                if mv_elem == elem and clean_mv_part == part:
                    print(f"mv_elem: {mv_elem} ,  elem: {elem} ,  clean_mv_part: {clean_mv_part} ,  part: {part}")
                    # 각 cb_stress에 대해 mvloadstress 추가
                    for cb_stress in cb_stresses:
                        combined_stress = cb_stress + mv_stress
                        print(f"combined_stress: {combined_stress} ,  mv_stress: {mv_stress} ,  cb_stress: {cb_stress}")
                        stress_list.append(combined_stress)
            
            # 이 element-part 조합의 최대 응력값 저장
            if stress_list:
                max_stress = max(stress_list)
                comb_stress_dict[(elem, part)] = max_stress

        clean_get_ij = get_ij.split('[')[0]  # J[2] -> J

        fb_list = []
        for (elem, part), max_stress in comb_stress_dict.items():
            if part == clean_get_ij:
                fb_list.append(max_stress)
                print(f"max_comb_stress: {max_stress} ,  elem: {elem} ,  part: {part}")

        fb = max(fb_list) if fb_list else 0




        get_fck = st.session_state.get('temp_result_df', {}).get('fck', 0)[0]

        rc = st.session_state.factor_rcfat

        # fctm 계산
        fctm = 0.30 * pow(get_fck, 2/3) if get_fck <= 50 else 2.12 * math.log(1 + get_fck/10)
        fctk005 = 0.7 * fctm
        fctd = fctk005 / rc
        # print(f"fctd: {fctd}")
        # print(f"fb: {fb}")
        is_cracked_section = fb > fctd

        # Construction Stage 데이터 요청
        request_data_conststage_force = {
            "Argument": {
                "TABLE_NAME": "Example",
                "OPT_CS": True,
                "EXPORT_PATH": "C:\\MIDAS\\Result\\Output.JSON",
                "TABLE_TYPE": "BEAMFORCE",
                "NODE_ELEMS": {"TO": str(int(float(get_Elem)))},  # get_Elem 적용
                "LOAD_CASE_NAMES": ["Tendon Primary(CS)", "Summation(CS)"],
                "PARTS": ["Part I", "Part J"],
                "STAGE_STEP": []
            }
        }

        response_conststage = requests.post(f"{base_url}/post/Table", headers=headers, json=request_data_conststage_force)


        response_data = response_conststage.json()
        cs_extracted_values = extract_construction_stage_values_local(response_data)


    # get_section_area = st.session_state.get_total_area
    # get_section_second_moment_y = st.session_state.get_iyy_total
    # get_section_yb = st.session_state.get_total_centroid_height
    # get_first_qn = st.session_state.get_Qn 
    # get_section_second_moment_Ig = st.session_state.get_J
    # get_bw = st.session_state.get_bw
    # get_totalHeight = st.session_state.get_total_height
    # # section properties for composite section
    # get_first_qc_composite = st.session_state.get_total_first_moment
    # get_section_second_moment_Ic = st.session_state.get_iyy_total




        get_ynon = get_girder_centroid_height
        get_ycom = get_section_yb
        y_offset = get_ycom - get_ynon
        get_area_g =get_section_area
        get_section_second_moment_Ig 
        axial_tendon = cs_extracted_values['max_axial_tendon']
        P_for_tot = abs(cs_extracted_values['max_axial_tendon'])
        M_mon = abs(cs_extracted_values['moment_y_at_max_shear'])
        get_tendoncenter_from_bottom = 0 
        eccentricity = get_ynon - get_tendoncenter_from_bottom

        row1 = M_mon * y_offset / get_section_second_moment_Ig * 10**6
        row2 = (P_for_tot)/get_area_g * 10**3 - ((P_for_tot * eccentricity / 1000) * y_offset / get_section_second_moment_Ig * 10**6)
        row_tot = row1 + row2


        # non-cracked 일경우 축력 산출
        cracked_axial_request_data_stress = {
            "Argument": {
                "TABLE_NAME": "BeamForceViewByMaxValue",
                "TABLE_TYPE": "BEAMFORCEVBM",
                "EXPORT_PATH": "C:\\MIDAS\\Result\\Output.JSON",
                "UNIT": {
                    "FORCE": "N",
                    "DIST": "mm"
                },
                "STYLES": {
                    "FORMAT": "Fixed",
                    "PLACE": 4
                },
                "COMPONENTS": [
                    "Elem", "Load", "Part", "Component", 
                    "Axial", "Shear-y", "Shear-z", 
                    "Torsion", "Moment-y", "Moment-z"
                ],
                "NODE_ELEMS": {
                    "KEYS":[float(get_Elem)]
                },
                "LOAD_CASE_NAMES": get_load_case_name,
                "PARTS": ["PartI", "PartJ"],
                "ITEM_TO_DISPLAY": ["Shear-z"]
            }
        }

        cracked_axial_response_stress = requests.post(f"{base_url}/post/Table", headers=headers, json=cracked_axial_request_data_stress)
        cracked_axial_response_data = cracked_axial_response_stress.json()
        axial_values = [float(row[5]) for row in cracked_axial_response_data['BeamForceViewByMaxValue']['DATA']]
        shear_z_values = [float(row[7]) for row in cracked_axial_response_data['BeamForceViewByMaxValue']['DATA']]
        ned_max = (max(axial_values) + (cs_extracted_values['max_axial_tendon'])*1000)*-1
        shear_z_max = max(abs(float(val)) for val in shear_z_values)
        # print(f"ned_max: {ned_max}")
        # print(f"shear_z_max: {shear_z_max}")




        return is_cracked_section, fctk005, rc, cs_extracted_values, row_tot, ned_max, shear_z_max, fb, fctd, get_bw, get_first_qn, get_section_second_moment_Ig, get_section_second_moment_Ic, get_first_qc_composite

    return None

def calculate_shear_strength():
    mapi_key = st.session_state.get('current_mapi_key', '')
    base_url = st.session_state.get('current_base_url', '')
    headers = {"MAPI-Key": mapi_key}
    
    # 단위 변환 요청
    unit_put = {
        "Assign": {
            "1": {
                "FORCE": "KN", 
                "DIST": "M",
                "HEAT": "KCAL",
                "TEMPER": "C"
            }
        }
    }
    
    unit_response_stress = requests.put(f"{base_url}/db/unit", headers=headers, json=unit_put)
    unit_response_data = unit_response_stress.json()
    
    if unit_response_stress.status_code != 200:
        st.error(f"error: {unit_response_data.get('message', 'API Error')}")
        return None

    result = calculate_shear_resistance()
 

    if result is None:
        return None
    # return is_cracked_section, fctk005, rc, cs_extracted_values, row_tot, ned_max, shear_z_max, fb, fctd
    is_cracked_section, fctk005, rc, cs_extracted_values, row_tot, ned_max, shear_z_max, fb, fctd, get_bw, get_first_qn, get_section_second_moment_Ig, get_section_second_moment_Ic, get_first_qc_composite = result
    get_totalHeight = st.session_state.get_total_height
    dp = get_totalHeight*0.85  # mm
    fctd = fctk005 / rc
    # 균열 단면인 경우
    if is_cracked_section ==False:
        Vs1 = abs(cs_extracted_values['abs_shear_z']) * 1000  # kN to N

        # 균열 단면의 전단응력 계산 (Ts = (Vs1/bw)*(Qn/Ig))
        Ts = (Vs1 / get_bw) * (get_first_qn / get_section_second_moment_Ig)

        # 비균열 단면에 대한 전단응력 계산
        Ic = get_section_second_moment_Ic
        Qc = get_first_qc_composite


        # Vc2 = (Ic * bw / Qc) * √((fctd)^2 + fctd * σtot) - τs
        Vc2 = (Ic * get_bw / Qc) *(math.sqrt((fctd**2) + fctd * row_tot) - Ts)

        # 총 전단력 계산
        VRd_c = (Vs1 + Vc2)/1000

        # 전단 보강 철근 필요성 판단
        if VRd_c < abs(shear_z_max/1000):
            is_required_reinforcement = True
            # print("shear reinforcement is required")
        else:
            is_required_reinforcement = False
            # print("shear reinforcement is not required")
        
        # print(f"VRd,c: {VRd_c:.3f} kN")


        # print(f"균열 단면의 전단응력: {VRd_c:.2f} KN")
        return VRd_c, dp, is_required_reinforcement, fctd, fb
    
    else:
        get_fck = st.session_state.get('temp_result_df', {}).get('fck', 0)[0]
        # 비균열 단면의 경우 전단 강도 계산
        # 주어진 공식 적용
        rc = 1.5  # 일반적인 콘크리트 안전계수
        CRd_c = 0.18 / rc  # CRd,c = 0.18/γ_c

        # k 계산 (200/dp)^(1/2)의 제곱근, 최대 2.0

        k = min(1 + math.sqrt(200 / dp), 2.0)
        
        # νmin 계산
        nu_min = 0.035 * (k**1.5) * (math.sqrt(get_fck))
        
        # k1 값
        k1 = 0.15
        
        # ρ1 계산 (철근비)
        Asl = 0.0  # 전단 철근 면적

        rho1 = min(Asl / (get_bw * dp), 0.02)
        get_section_area = st.session_state.get_total_area
        # σcp 계산 (압축응력)
        fcd = get_fck / rc  # 설계 압축 강도
        sigma_cp = min((ned_max) / get_section_area, 0.2 * fcd)  # N/mm²로 변환

        
        # VRd,min 계산
        VRd_min = (nu_min + k1 * sigma_cp) * get_bw * dp / 1000  # kN으로 변환
        
        # VRd,c 계산
        print((CRd_c * k * (100 * rho1 * get_fck)**(1/3) + k1 * sigma_cp) * get_bw * dp / 1000)
        VRd_c = max((CRd_c * k * (100 * rho1 * get_fck)**(1/3) + k1 * sigma_cp) * get_bw * dp / 1000,VRd_min)  # kN으로 변환
               
        # 전단 보강 철근 필요성 판단
        if VRd_c < abs(shear_z_max):
            is_required_reinforcement = True
            print("전단 보강 철근 필요")
        else:
            is_required_reinforcement = False
            print("전단 보강 철근 불필요")
        
        print(f"VRd,c: {VRd_c:.3f} kN")

        return VRd_c, dp, is_required_reinforcement, fctd, fb
