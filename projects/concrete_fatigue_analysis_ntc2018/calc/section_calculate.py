# calc/section_calculate.py
import pandas as pd
import json
import requests
import streamlit as st
from typing import Dict, List, Any, Optional
from projects.concrete_fatigue_analysis_ntc2018.section.processor import SectionProcessor

# 단위 변환 상수 (mm 기준)
UNIT_CONVERSION = {
    # 길이 단위 변환 (mm 기준)
    'LENGTH': {
        'mm': 1.0,
        'm': 1000.0,
        'cm': 10.0,
        'in': 25.4,
        'ft': 304.8
    },
    # 면적 단위 변환 (mm² 기준)
    'AREA': {
        'mm': 1.0,
        'm': 1000000.0,  # 1000^2
        'cm': 100.0,     # 10^2
        'in': 645.16,    # 25.4^2
        'ft': 92903.04   # 304.8^2
    },
    # 4차 모멘트 단위 변환 (mm⁴ 기준)
    'MOMENT4': {
        'mm': 1.0,
        'm': 1000000000000.0,  # 1000^4
        'cm': 10000.0,         # 10^4
        'in': 416231.4256,     # 25.4^4
        'ft': 8635244094.56    # 304.8^4
    },
    # 3차 모멘트 단위 변환 (mm³ 기준)
    'MOMENT3': {
        'mm': 1.0,
        'm': 1000000000.0,  # 1000^3
        'cm': 1000.0,       # 10^3
        'in': 16387.064,    # 25.4^3
        'ft': 28316846.592  # 304.8^3
    }
}

def get_api_config():
    """
    세션 상태에서 API 설정을 가져오는 함수
    
    Returns:
        tuple: (base_url, mapi_key)
    """
    base_url = st.session_state.get('current_base_url', '')
    mapi_key = st.session_state.get('current_mapi_key', '')
    
    if not base_url or not mapi_key:
        raise ValueError("API connection not established. Please login first.")
    
    return base_url, mapi_key

def convert_to_mm(value: float, from_unit: str, dimension_type: str) -> float:
    """
    지정된 단위에서 mm 기준으로 변환하는 함수
    
    Args:
        value: 변환할 값
        from_unit: 원본 단위
        dimension_type: 차원 타입 ('LENGTH', 'AREA', 'MOMENT3', 'MOMENT4')
        
    Returns:
        float: mm 기준으로 변환된 값
    """
    if from_unit.lower() == 'mm' or from_unit == '':
        return value
    
    conversion_factors = UNIT_CONVERSION.get(dimension_type, {})
    factor = conversion_factors.get(from_unit.lower(), 1.0)
    
    if factor == 1.0 and from_unit.lower() != 'mm':
        print(f"⚠️ 알 수 없는 단위: {from_unit}, 변환하지 않음")
    
    return value * factor

def get_data(data_path: str, httpmethod: str = "GET", json_data: Optional[Dict] = None) -> Dict:
    """API에서 데이터를 가져오는 함수 (세션 상태의 API 설정 사용)"""
    try:
        base_url, mapi_key = get_api_config()
    except ValueError as e:
        raise Exception(f"API configuration error: {str(e)}")
    
    headers = {
        "Content-Type": "application/json",
        "MAPI-Key": mapi_key
    }
    
    try:
        if httpmethod == "GET":
            response = requests.get(base_url + data_path, headers=headers)
        elif httpmethod == "POST":
            response = requests.post(base_url + data_path, headers=headers, json=json_data)
        else:
            raise ValueError(f"Invalid HTTP method: {httpmethod}")
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")

def process_section_data_to_dataframe(processed_data: Dict[str, Any]) -> pd.DataFrame:
    """
    SectionProcessor로 처리된 데이터를 DataFrame으로 변환하는 함수 (단위 변환 포함)
    
    Args:
        processed_data: SectionProcessor.process_all_sections()의 결과
        
    Returns:
        pd.DataFrame: 처리된 단면 속성 데이터프레임 (모든 값이 mm 기준)
    """
    section_data = []
    
    print(f"총 처리된 단면 수: {len(processed_data)}")
    
    for section_id, section_info in processed_data.items():
        try:
            # error가 있는 경우 건너뛰기
            if "error" in section_info:
                print(f"Section {section_id}: 에러 - {section_info['error']}")
                continue
            
            # base_data에서 기본 정보 추출
            base_data = section_info.get('base_data', {})
            section_name = base_data.get('name', f'Section_{section_id}')
            section_type = base_data.get('type', '')
            shape = base_data.get('shape', '')
            unit_system = base_data.get('unit_system', 'mm')
            
            print(f"처리 중: Section {section_id} - {section_name} ({section_type}, {shape}, {unit_system})")
            
            # COMPOSITE 타입만 처리
            if section_type != 'COMPOSITE':
                print(f"  ❌ 건너뛰기 (COMPOSITE 타입 아님)")
                continue
            
            # 기본 행 데이터
            row_data = {
                'section_id': section_id,
                'name': section_name,
                'unit': 'mm',  # 최종 출력은 항상 mm
                'original_unit': unit_system,  # 원본 단위 보관
                'shape': shape,
                'section_type': section_type
            }
            
            # shape에 따라 type 결정
            if shape.startswith('C'):
                row_data['type'] = 'concrete'
            elif shape == 'I':
                row_data['type'] = 'steel'
            else:
                row_data['type'] = 'unknown'
            
            print(f"  Type: {row_data['type']}, 원본 단위: {unit_system}")
            
            # 기본값 설정 (mm 기준)
            row_data['qn_girder_totcenter'] = 0.0
            row_data['iyy_girder'] = 0.0
            row_data['bw'] = 0.0
            row_data['slab_height'] = 0.0
            row_data['girder_height'] = 0.0
            row_data['girder_centroid_height'] = 0.0
            row_data['total_area'] = 0.0
            row_data['total_first_moment'] = 0.0
            row_data['iyy_total'] = 0.0
            row_data['total_height'] = 0.0

            
            # i_data에서 상세 속성 추출
            i_data = section_info.get('i_data', {})
        
            if i_data:
                print(f"  i_data 발견 - 상세 속성 추출 및 단위 변환")
                # properties에서 값 추출
                properties = i_data.get('properties', {})
                
                if row_data['type'] == 'concrete':
                    # Concrete 타입 처리 (shape이 C로 시작)
                    
                    # Qn_girder_totcenter (total > first_moment_of_area > girder > positive_side > Qyy)
                    total_props = properties.get('total', {})
                    total_first_moment = total_props.get('first_moment_of_area', {})
                    total_girder_positive = total_first_moment.get('girder', {}).get('positive_side', {})
                    qn_value = total_girder_positive.get('Qyy', 0.0)
                    # mm³로 변환
                    row_data['qn_girder_totcenter'] = convert_to_mm(qn_value, unit_system, 'MOMENT3')
                    
                    print(f"    qn_girder_totcenter: {qn_value} {unit_system} → {row_data['qn_girder_totcenter']:.2f} mm³")
                    
                    # Iyy_girder (girder > second_moment_of_area > Iyy)
                    girder_props = properties.get('girder', {})
                    girder_second_moment = girder_props.get('second_moment_of_area', {})
                    iyy_value = girder_second_moment.get('Iyy', 0.0)
                    
                    # fallback: girder에서 못 찾은 경우 total에서 찾기
                    if iyy_value == 0.0:
                        total_second_moment = total_props.get('second_moment_of_area', {})
                        if 'girder' in total_second_moment:
                            iyy_value = total_second_moment.get('girder', {}).get('Iyy', 0.0)
                    
                    # mm⁴로 변환
                    row_data['iyy_girder'] = convert_to_mm(iyy_value, unit_system, 'MOMENT4')
                    print(f"    iyy_girder: {iyy_value} {unit_system}⁴ → {row_data['iyy_girder']:.2f} mm⁴")
                    
                elif row_data['type'] == 'steel':
                    # Steel 타입 처리 (shape이 I)
                    # girder properties에서 직접 추출
                    girder_props = properties.get('girder', {})
                    total_props = properties.get('total', {})
                    # Iyy_girder 추출
                    girder_second_moment = girder_props.get('second_moment_of_area', {})
                    iyy_value = girder_second_moment.get('Iyy', 0.0)
                    # mm⁴로 변환
                    row_data['iyy_girder'] = convert_to_mm(iyy_value, unit_system, 'MOMENT4')
                    
                    # qn_girder_totcenter는 steel에서도 추출 가능한 경우 추출
                    girder_first_moment = girder_props.get('first_moment_of_area', {})
                    girder_positive = girder_first_moment.get('positive_side', {})
                    qn_value = girder_positive.get('Qyy', 0.0)
                    # mm³로 변환
                    row_data['qn_girder_totcenter'] = convert_to_mm(qn_value, unit_system, 'MOMENT3')
                    
                    print(f"    iyy_girder: {iyy_value} {unit_system}⁴ → {row_data['iyy_girder']:.2f} mm⁴")
                    print(f"    qn_girder_totcenter: {qn_value} {unit_system}³ → {row_data['qn_girder_totcenter']:.2f} mm³")
                
                # ref_dimension에서 girder_web_thickness 추출 (공통)
                ref_dimension = i_data.get('ref_dimension', {})
                girder_web_thickness = ref_dimension.get('girder_web_thickness', {})
                bw_value = 0.0
                
                # "all" 키가 있으면 사용, 없으면 다른 키들 확인
                if 'all' in girder_web_thickness:
                    bw_value = girder_web_thickness.get('all', 0.0)
                elif 'value' in girder_web_thickness:
                    bw_value = girder_web_thickness.get('value', 0.0)
                elif 'center' in girder_web_thickness:
                    bw_value = girder_web_thickness.get('center', 0.0)
                
                # mm로 변환
                row_data['bw'] = convert_to_mm(bw_value, unit_system, 'LENGTH')
                print(f"    bw: {bw_value} {unit_system} → {row_data['bw']:.2f} mm")
                
                # reference_points에서 높이 계산 (공통)
                reference_points = i_data.get('reference_points', {})
                
                # Slab 높이 계산
                slab_points = reference_points.get('slab', {})
                slab_height_value = 0.0
                if slab_points:
                    slab_point1 = slab_points.get('point_1', [0, 0])
                    slab_point4 = slab_points.get('point_4', [0, 0])
                    if len(slab_point1) >= 2 and len(slab_point4) >= 2:
                        slab_height_value = abs(slab_point1[1] - slab_point4[1])
                
                # mm로 변환
                row_data['slab_height'] = convert_to_mm(slab_height_value, unit_system, 'LENGTH')
                print(f"    slab_height: {slab_height_value} {unit_system} → {row_data['slab_height']:.2f} mm")
                
                # Girder 높이 계산
                girder_points = reference_points.get('girder', {})
                girder_height_value = 0.0
                if girder_points:
                    girder_point1 = girder_points.get('point_1', [0, 0])
                    girder_point4 = girder_points.get('point_4', [0, 0])
                    if len(girder_point1) >= 2 and len(girder_point4) >= 2:
                        girder_height_value = abs(girder_point1[1] - girder_point4[1])
                else:
                    girder_height_info = ref_dimension.get('girder_height', {})
                    if 'center' in girder_height_info:
                        girder_height_value = girder_height_info.get('center', 0.0)
                    elif 'max' in girder_height_info:
                        girder_height_value = girder_height_info.get('max', 0.0)
                
                # mm로 변환
                row_data['girder_height'] = convert_to_mm(girder_height_value, unit_system, 'LENGTH')
                print(f"    girder_height: {girder_height_value} {unit_system} → {row_data['girder_height']:.2f} mm")
                
                # total_height 계산 (girder_height + slab_height) - 이미 mm로 변환된 값들
                row_data['total_height'] = row_data['girder_height'] + row_data['slab_height']
                print(f"    total_height: {row_data['total_height']:.2f} mm")
            

                # Total 중심점  높이 계산
                total_points = reference_points.get('total', {})
                total_centroid_value = total_props.get('centroid', 0.0)
                total_centroid_height_value = total_centroid_value[1]

                if total_points:
                    total_point1 = total_points.get('point_1', [0, 0])
                    total_point4 = total_points.get('point_4', [0, 0])
                    if len(total_point1) >= 2 and len(total_point4) >= 2:
                        total_centroid_height_value = abs(total_centroid_height_value - total_point4[1])

                row_data['total_centroid_height'] = convert_to_mm(total_centroid_height_value, unit_system, 'LENGTH')
                print(f"    total_centroid_height: {total_centroid_height_value} {unit_system} → {row_data['total_centroid_height']:.2f} mm")



                girder_height_value = 0.0
                if girder_points:
                    girder_point4 = girder_points.get('point_4', [0, 0])
                    gierder_centroid=girder_props.get('centroid', {})
                    girder_centroid_height_value = abs(gierder_centroid[1] - girder_point4[1])
                row_data['girder_centroid_height'] = convert_to_mm(girder_centroid_height_value, unit_system, 'LENGTH')
                print(f"    girder_centroid_height: {girder_centroid_height_value} {unit_system} → {row_data['girder_centroid_height']:.2f} mm")


                total_area_value = (total_props.get('area', 0.0)).get('girder', 0.0)
                row_data['total_area'] = convert_to_mm(total_area_value, unit_system, 'AREA')
                print(f"    total_area: {total_area_value} {unit_system} → {row_data['total_area']:.2f} mm²")

                total_first_moment_value = ((total_props.get('first_moment_of_area', 0.0)).get('total', 0.0)).get('positive_side', 0.0).get('Qyy', 0.0)
                row_data['total_first_moment'] = convert_to_mm(total_first_moment_value, unit_system, 'MOMENT3')
                print(f"    total_first_moment: {total_first_moment_value} {unit_system} → {row_data['total_first_moment']:.2f} mm³")

                iyy_total_value = (total_props.get('second_moment_of_area', 0.0)).get('total', 0.0).get('Iyy', 0.0)
                row_data['iyy_total'] = convert_to_mm(iyy_total_value, unit_system, 'MOMENT4')
                print(f"    iyy_total: {iyy_total_value} {unit_system} → {row_data['iyy_total']:.2f} mm⁴")

            section_data.append(row_data)
            print(f"  ✅ 처리 완료 (모든 값이 mm 단위로 변환됨)")
            
        except Exception as e:
            print(f"Section {section_id} 처리 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    return pd.DataFrame(section_data)
#단면속성 불러오기
def fetch_and_process_section_data() -> pd.DataFrame:
    """SectionProcessor를 사용하여 단면 데이터를 가져오고 처리"""
    try:
        print("API에서 데이터 가져오는 중...")
        # API에서 단면 데이터 가져오기 (세션 상태의 API 설정 사용)
        data = get_data("/db/sect")
        unit_system = get_data("/db/unit")
        
        print("SectionProcessor로 데이터 처리 중...")
        processor = SectionProcessor(data, unit_system)
        results = processor.process_all_sections()
        
        # 처리된 결과를 데이터프레임으로 변환 (단위 변환 포함)
        df = process_section_data_to_dataframe(results)
        return df
        
    except Exception as e:
        print(f"데이터 처리 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def filter_sections_by_type(df: pd.DataFrame, section_type: str) -> pd.DataFrame:
    """
    타입별로 단면을 필터링하는 함수
    
    Args:
        df: 단면 데이터프레임
        section_type: 'concrete' 또는 'steel'
        
    Returns:
        pd.DataFrame: 필터링된 데이터프레임
    """
    if not df.empty and 'type' in df.columns:
        return df[df['type'] == section_type].copy()
    return pd.DataFrame()

def get_section_by_name(df: pd.DataFrame, section_name: str) -> Optional[Dict[str, Any]]:
    """
    단면 이름으로 단면 정보를 가져오는 함수
    
    Args:
        df: 단면 데이터프레임
        section_name: 단면 이름
        
    Returns:
        Dict 또는 None: 단면 정보 딕셔너리 (모든 값이 mm 기준)
    """
    if not df.empty and 'name' in df.columns:
        filtered_df = df[df['name'] == section_name]
        if not filtered_df.empty:
            return filtered_df.iloc[0].to_dict()
    return None

def get_section_properties(df: pd.DataFrame, section_name: str) -> Dict[str, float]:
    """
    단면 이름으로 주요 속성값들을 가져오는 함수 (모든 값이 mm 기준)
    
    Args:
        df: 단면 데이터프레임
        section_name: 단면 이름
        
    Returns:
        Dict: 주요 속성값들 (bw, iyy_girder, qn_girder_totcenter, girder_height, slab_height)
                모든 값이 mm 단위
    """
    section_info = get_section_by_name(df, section_name)
    if section_info:
        return {
            "bw": section_info.get("bw", 0.0),                           # mm
            "iyy_girder": section_info.get("iyy_girder", 0.0),          # mm⁴
            "qn_girder_totcenter": section_info.get("qn_girder_totcenter", 0.0),  # mm³
            "girder_height": section_info.get("girder_height", 0.0),    # mm
            "slab_height": section_info.get("slab_height", 0.0),        # mm
            "total_height": section_info.get("total_height", 0.0),      # mm
            "total_centroid_height": section_info.get("total_centroid_height", 0.0),      # mm
            "girder_centroid_height": section_info.get("girder_centroid_height", 0.0),      # mm
            "total_area": section_info.get("total_area", 0.0),      # mm²
            "total_first_moment": section_info.get("total_first_moment", 0.0),      # mm³
            "iyy_total": section_info.get("iyy_total", 0.0),      # mm⁴
            "H": section_info.get("girder_height", 0.0),                # H는 girder_height와 동일 (mm)
            "J": section_info.get("iyy_girder", 0.0),                   # J는 iyy_girder와 동일 (mm⁴)
            "Qn": section_info.get("qn_girder_totcenter", 0.0),         # Qn은 qn_girder_totcenter와 동일 (mm³)
            "unit": "mm",                                                # 단위 정보
            "original_unit": section_info.get("original_unit", "mm")     # 원본 단위 정보
        }
    return {}

def get_section_names_by_type(df: pd.DataFrame, section_type: str) -> List[str]:
    """
    타입별 단면 이름 목록을 가져오는 함수
    
    Args:
        df: 단면 데이터프레임
        section_type: 'concrete' 또는 'steel'
        
    Returns:
        List[str]: 단면 이름 목록
    """
    filtered_df = filter_sections_by_type(df, section_type)
    if not filtered_df.empty and 'name' in filtered_df.columns:
        return filtered_df['name'].tolist()
    return []

def sectionprop_processing():
    """
    실제 API 호출 및 데이터 처리 테스트 함수
    """
    print("=== SectionProcessor를 사용한 API 호출 및 데이터 처리 테스트 (단위 변환 포함) ===")
    
    # API 연결 상태 확인
    if not st.session_state.get('api_connected', False):
        print("❌ API가 연결되지 않았습니다. 먼저 로그인해주세요.")
        return pd.DataFrame()
    
    try:
        # API에서 데이터 가져오기
        df = fetch_and_process_section_data()
        
        print(f"\n✅ 처리 완료 - 처리된 단면 수: {len(df)}")
        
        if not df.empty:
            print("\n=== 처리된 단면 목록 (모든 값이 mm 단위) ===")
            print(df.to_string())
            
            print("\n=== 타입별 단면 수 ===")
            concrete_count = len(df[df['type'] == 'concrete'])
            steel_count = len(df[df['type'] == 'steel'])
            unknown_count = len(df[df['type'] == 'unknown'])
            print(f"Concrete 단면: {concrete_count}개")
            print(f"Steel 단면: {steel_count}개")
            print(f"Unknown 단면: {unknown_count}개")
            
            print("\n=== 단면 속성 추출 테스트 (mm 단위) ===")
            for idx, row in df.iterrows():
                section_name = row['name']
                properties = get_section_properties(df, section_name)
                print(f"\n단면명: {section_name} ({row['type']}) - 원본 단위: {row.get('original_unit', 'mm')}")
                for key, value in properties.items():
                    if key in ['unit', 'original_unit']:
                        print(f"  {key}: {value}")
                    else:
                        unit_suffix = ""
                        if key in ['bw', 'girder_height', 'slab_height', 'total_height', 'H']:
                            unit_suffix = " mm"
                        elif key in ['iyy_girder', 'J']:
                            unit_suffix = " mm⁴"
                        elif key in ['qn_girder_totcenter', 'Qn']:
                            unit_suffix = " mm³"
                        print(f"  {key}: {value:,.2f}{unit_suffix}")
                    
        else:
            print("⚠️ 처리된 COMPOSITE 단면이 없습니다.")
        
        return df
            
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

if __name__ == "__main__":
    # 테스트 실행 (Streamlit 환경이 아닌 경우)
    if 'session_state' not in dir(st):
        print("⚠️ Streamlit 환경이 아닙니다. 테스트를 건너뜁니다.")
    else:
        sectionprop_processing()