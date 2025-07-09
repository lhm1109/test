# calc/road_concrete_lambda.py
import math
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import streamlit as st

def plot_lambda1_curves_road(current_support_type, current_steel_type, current_span_length):
    """
    도로교량 λ₁ 곡선을 2개 차트로 나누어 표시
    
    Args:
        current_support_type (str): 현재 선택된 지지 조건
        current_steel_type (str): 현재 선택된 강재 유형  
        current_span_length (float): 현재 경간 길이
    
    Returns:
        tuple: (fig1, fig2) - Intermediate Support Area용, 나머지용
    """
    
    # 차트 1: Intermediate Support Area
    fig1 = create_intermediate_support_chart(current_support_type, current_steel_type, current_span_length)
    
    # 차트 2: 나머지 (Continuous Beam, Single Span Beam, Carriageway Slab)
    fig2 = create_other_structures_chart(current_support_type, current_steel_type, current_span_length)
    
    return fig1, fig2

def create_intermediate_support_chart(current_support_type, current_steel_type, current_span_length):
    """Intermediate Support Area용 차트 생성"""
    fig = go.Figure()
    
    # Intermediate Support Area 데이터만 처리
    intermediate_data = lambda1_table.get("Intermediate Support Area", {})
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # 3가지 색상
    color_idx = 0
    
    for steel_key, steel_data in intermediate_data.items():
        if "range" in steel_data and "coefficients" in steel_data:
            x_vals, y_vals = _calculate_curve_points(steel_data["range"], steel_data["coefficients"])
            
            # 현재 선택된 강재 유형인지 확인
            is_current = (current_support_type == "Intermediate Support Area" and 
                         map_steel_type_to_table_key(current_steel_type) == steel_key)
            
            line_width = 4 if is_current else 2
            line_dash = 'solid' if is_current else 'dash'
            
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines',
                name=steel_key,
                line=dict(
                    color=colors[color_idx % len(colors)], 
                    width=line_width,
                    dash=line_dash
                ),
                hovertemplate="<b>%{fullData.name}</b><br>" +
                            "Critical Length: %{x:.1f} m<br>" +
                            "λ₁ Value: %{y:.3f}<br>" +
                            "<extra></extra>"
            ))
            color_idx += 1
    
    # 현재 경간길이에 수직선 추가
    if current_support_type == "Intermediate Support Area":
        fig.add_vline(
            x=current_span_length, 
            line_dash="dot", 
            line_color="red",
            annotation_text=f"Current: {current_span_length}m"
        )
    
    fig.update_layout(
        title="λ₁ value for fatigue verification in the intermediate support area",
        xaxis_title="Critical length of influence line [m]",
        yaxis_title="λ₁",
        width=800,
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
            
        )
    )
    
    fig.update_xaxes(
        range=[0, 100],  # 전체 범위 0-100
        showgrid=True, 
        gridwidth=1, 
        gridcolor='lightgray',
        # 0부터 100까지 10 간격으로 틱 포인트 설정
        tickvals=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        # 틱 레이블 설정
        ticktext=['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']
    )
    
    # y축 범위 설정
    fig.update_yaxes(
        range=[0.8, 2.0], 
        showgrid=True, 
        gridwidth=1, 
        gridcolor='lightgray'
    )
    
    return fig

def create_other_structures_chart(current_support_type, current_steel_type, current_span_length):
    """나머지 구조형식용 차트 생성"""
    fig = go.Figure()
    
    # 어두운 색상만 사용
    dark_colors = [
        '#1f77b4',  # 어두운 파랑
        '#ff7f0e',  # 어두운 주황
        '#2ca02c',  # 어두운 초록
        '#d62728',  # 어두운 빨강
        '#9467bd',  # 어두운 보라
        '#8c564b',  # 어두운 갈색
        '#e377c2',  # 어두운 핑크
        '#7f7f7f',  # 어두운 회색
        '#bcbd22',  # 어두운 노랑
        '#17becf'   # 어두운 청록
    ]
    
    color_idx = 0
    subtype_colors = {}  # 서브타입별 색상 매핑
    
    # Intermediate Support Area 제외한 나머지 처리
    for section_name, section_data in lambda1_table.items():
        if section_name == "Intermediate Support Area":
            continue
            
        # print(f"Processing section: {section_name}")
        
        # 각 강재 유형 처리
        for steel_key, steel_data in section_data.items():
            # print(f"Processing steel_key: {steel_key}")
            # print(f"Steel data keys: {list(steel_data.keys()) if isinstance(steel_data, dict) else 'Not a dict'}")
            
            # steel_data는 항상 서브타입을 포함하는 딕셔너리
            if isinstance(steel_data, dict):
                # 서브타입 키들 체크 (실제 데이터 구조에 맞게 수정)
                subtype_keys = ['1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b', '2c', '3c', '4c']
                
                # 서브타입 처리
                for subtype_key, subtype_data in steel_data.items():
                    if subtype_key in subtype_keys:
                        # print(f"Processing subtype: {subtype_key}")
                        
                        # 서브타입별 색상 할당 (한 번만)
                        if subtype_key not in subtype_colors:
                            subtype_colors[subtype_key] = dark_colors[color_idx % len(dark_colors)]
                            color_idx += 1
                        
                        try:
                            # 다중 범위 처리
                            if "ranges" in subtype_data and "coefficients" in subtype_data:
                                ranges = subtype_data["ranges"]
                                coeffs_list = subtype_data["coefficients"]
                                
                                for i, range_val in enumerate(ranges):
                                    coeffs = coeffs_list[i]
                                    x_vals, y_vals = _calculate_curve_points(range_val, coeffs)
                                    
                                    # 현재 선택된 조건인지 확인
                                    is_current = (current_support_type == section_name and 
                                                map_steel_type_to_table_key(current_steel_type) == steel_key)
                                    
                                    line_width = 4 if is_current else 2
                                    line_dash = 'solid'
                                    
                                    # 첫 번째 범위만 범례에 표시
                                    show_legend = (i == 0)
                                    
                                    # Carriageway Slab의 경우 특별한 이름 형식
                                    if section_name == "Carriageway Slab":
                                        trace_name = f"{subtype_key}"
                                    else:
                                        trace_name = subtype_key
                                    
                                    fig.add_trace(go.Scatter(
                                        x=x_vals,
                                        y=y_vals,
                                        mode='lines',
                                        name=trace_name,
                                        legendgroup=subtype_key,  # 같은 그룹으로 묶기
                                        showlegend=show_legend,
                                        line=dict(
                                            color=subtype_colors[subtype_key], 
                                            width=line_width,
                                            dash=line_dash
                                        ),
                                        hovertemplate="<b>%{fullData.name}</b><br>" +
                                                    "Critical Length: %{x:.1f} m<br>" +
                                                    "λ₁ Value: %{y:.3f}<br>" +
                                                    f"Range: {i+1}<br>" +
                                                    "<extra></extra>"
                                    ))
                            
                            # 단일 범위 처리
                            elif "range" in subtype_data and "coefficients" in subtype_data:
                                x_vals, y_vals = _calculate_curve_points(subtype_data["range"], subtype_data["coefficients"])
                                
                                is_current = (current_support_type == section_name and 
                                            map_steel_type_to_table_key(current_steel_type) == steel_key)
                                
                                line_width = 4 if is_current else 2
                                line_dash = 'solid'
                                
                                # Carriageway Slab의 경우 특별한 이름 형식
                                if section_name == "Carriageway Slab":
                                    trace_name = f"{subtype_key}"
                                else:
                                    trace_name = subtype_key
                                
                                fig.add_trace(go.Scatter(
                                    x=x_vals,
                                    y=y_vals,
                                    mode='lines',
                                    name=trace_name,
                                    line=dict(
                                        color=subtype_colors[subtype_key], 
                                        width=line_width,
                                        dash=line_dash
                                    ),
                                    hovertemplate="<b>%{fullData.name}</b><br>" +
                                                "Critical Length: %{x:.1f} m<br>" +
                                                "λ₁ Value: %{y:.3f}<br>" +
                                                "<extra></extra>"
                                ))
                            
                            else:
                                print(f"No valid range/coefficients structure found for {subtype_key}")
                                print(f"Available keys in subtype_data: {list(subtype_data.keys())}")
                        
                        except Exception as e:
                            print(f"Error processing subtype {subtype_key}: {e}")
                            continue
                    else:
                        print(f"Skipping unknown subtype: {subtype_key}")
            else:
                print(f"Steel data for {steel_key} is not a dictionary")
    
    # 현재 경간길이에 수직선 추가 (Intermediate Support Area가 아닌 경우)
    if current_support_type != "Intermediate Support Area":
        fig.add_vline(
            x=current_span_length, 
            line_dash="dot", 
            line_color="red",
            annotation_text=f"Current: {current_span_length}m"
        )
    
    fig.update_layout(
        title="Verification span and for carriageway slab",
        xaxis_title="Critical length of influence line [m]",
        yaxis_title="λ₁",
        width=800,
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    # x축 범위 및 틱 설정
    fig.update_xaxes(
        range=[0, 100], 
        showgrid=True, 
        gridwidth=1, 
        gridcolor='lightgray',
        tickvals=[0, 2, 4, 6, 8, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        ticktext=['0', '2', '4', '6', '8', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']
    )
    fig.update_yaxes(range=[0.8, 2.0], showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig

def _calculate_curve_points(range_vals, coeffs, num_points=100):
    """다항식 곡선의 점들을 계산하는 헬퍼 함수"""
    x_vals = np.linspace(range_vals[0], range_vals[1], num_points)
    y_vals = np.array([polynomial_interpolation(x, coeffs) for x in x_vals])
    return x_vals, y_vals

def get_current_lambda1_info(support_type, steel_type, span_length):
    """현재 설정에서의 λ₁ 값과 정보 반환"""
    lambda1_value = get_lambda1_road(support_type, steel_type, span_length)
    mapped_steel = map_steel_type_to_table_key(steel_type)
    
    return {
        'lambda1_value': lambda1_value,
        'support_type': support_type,
        'steel_type': steel_type,
        'mapped_steel_type': mapped_steel,
        'span_length': span_length
    }


def polynomial_interpolation(x, coefficients):
    """다항식 보간 함수"""
    y = 0
    degree = len(coefficients) - 1
    for i, coeff in enumerate(coefficients):
        y += coeff * x**(degree - i)
    return y
lambda1_table = {
    "Intermediate Support Area": {
        "Splicing Devices": {
            "range": (10, 90),
            "coefficients": [
                0.0000000007088725422491540,
                -0.0000001871960411379570000,
                0.0000172669325903960000000,
                -0.0006201557578997430000000,
                0.0107635033698971000000000,
                1.2660531706711200000000000
            ]
        },
        "Curved Tendons in Steel Ducts": {
            "range": (10, 90),
            "coefficients": [
                0.0000000000599045054622900,
                -0.0000000269448365672640000,
                0.0000032656218870114700000,
                -0.0001150680378267440000000,
                0.0043635338476368600000000,
                0.9894041628065690000000000
            ]
        },
        "Rebar, Pre/Post Tension": {
            "range": (10, 90),
            "coefficients": [
                0.0000000002776216805476150,
                -0.0000000742348635830221000,
                0.0000069780928682598400000,
                -0.0002541170453835740000000,
                0.0073446064649340600000000,
                0.8449062978862340000000000
            ]
        }
    },
    "Continuous Beam": {
        "Splicing Devices": {
            # 1a: Continuous beam - Splicing Devices
            "1a": {
                "ranges": [(10, 46), (46, 90)],
                "coefficients": [
                    [
                        -0.0000000043196199473252700,
                        0.0000007321917228925860,
                        -0.0000479355257679073,
                        0.0013572174837343100,
                        -0.0091661207161161800,
                        1.5956805403546000
                    ],
                    [
                        0.0000000000000000416333634,
                        -0.0000000000000174305014866,
                        0.0000000000019763080061352,
                        -0.0000000000758988427662644,
                        1.7686470006208300
                    ]
                ]
            }
        },
        "Curved Tendons in Steel Ducts": {
            # 2a: Continuous beam - Curved Tendons in Steel Ducts
            "2a": {
                "ranges": [(10, 52.75), (52.75, 90)],
                "coefficients": [
                    [
                        -0.0000000013601873460021600,
                        0.0000003323126913324860000,
                        -0.0000281955034941127000,
                        0.0009402845789730150000,
                        -0.0055579439263345700000,
                        1.1868372940870600
                    ],
                    [
                        -0.0000000000002498240329885,
                        0.0000000000851335296746594,
                        -0.0000000115069185193241000,
                        0.0000007712863665410590000,
                        0.0007415643900883130000,
                        1.3489096846579700
                    ]
                ]
            }
        },
        "Rebar, Pre/Post Tension": {
            # 3a: Continuous beam - Rebar, Pre/Post Tension
            "3a": {
                "ranges": [(10, 40), (40, 90)],
                "coefficients": [
                    [
                        -0.0000000061606106370806800,
                        0.0000009187340501548960000,
                        -0.0000548825004293449000,
                        0.0014761202551913900000,
                        -0.0101081967490761000000,
                        1.0519483008362700
                    ],
                    [
                        0.0000000000336719916814616,
                        -0.0000000105031126699552000,
                        0.0000013050950671347800,
                        -0.0000815681951167879000,
                        0.0037172076813603000,
                        1.1397692407768800
                    ]
                ]
            }
        },
        "Shear Reinforcement": {
            # 4a: Continuous beam - Shear Reinforcement
            "4a": {
                "ranges": [(10, 40), (40, 90)],
                "coefficients": [
                    [
                        -0.0000000061606106370806800,
                        0.0000009187340501548960000,
                        -0.0000548825004293449000,
                        0.0014761202551913900000,
                        -0.0101081967490761000000,
                        1.0519483008362700
                    ],
                    [
                        0.0000000000336719916814616,
                        -0.0000000105031126699552000,
                        0.0000013050950671347800,
                        -0.0000815681951167879000,
                        0.0037172076813603000,
                        1.1397692407768800
                    ]
                ]
            }
        }
    },
    "Single Span Beam": {
        "Splicing Devices": {
            # 1b: Single span beam - Splicing Devices
            "1b": {
                "range": (10, 51),
                "coefficients": [
                    0.0000000000010658932503987,
                    -0.0000000001687590783262800,
                    0.0000000102742730868216000,
                    -0.0000002987705426289730000,
                    0.0000018288416821533900000,
                    1.7173148381389200
                ]
            }
        },
        "Curved Tendons in Steel Ducts": {
            # 2b: Single span beam - Curved Tendons in Steel Ducts
            "2b": {
                "range": (10, 50),
                "coefficients": [
                    0.0000000000002427500474939,
                    -0.0000000000313083396827254,
                    0.0000000014874047797128300,
                    -0.0000000324952962177544000,
                    0.0003633318279271500000,
                    1.3146762486588100
                ]
            }
        },
        "Rebar, Pre/Post Tension": {
            # 3b: Single span beam - Rebar, Pre/Post Tension
            "3b": {
                "range": (10, 50),
                "coefficients": [
                    0.0000000000000125600484874,
                    0.0000000000065408340907142,
                    -0.0000000008596755124242360,
                    0.0000000354564166412465000,
                    0.0003767790586088320000,
                    1.1503402558019300
                ]
            }
        },
        "Shear Reinforcement": {
            # 4b: Single span beam - Shear Reinforcement
            "4b": {
                "ranges": [(10, 40), (40, 90)],
                "coefficients": [
                    [
                        -0.0000000061606106370806800,
                        0.0000009187340501548960000,
                        -0.0000548825004293449000,
                        0.0014761202551913900000,
                        -0.0101081967490761000000,
                        1.0519483008362700
                    ],
                    [
                        0.0000000000336719916814616,
                        -0.0000000105031126699552000,
                        0.0000013050950671347800,
                        -0.0000815681951167879000,
                        0.0037172076813603000,
                        1.1397692407768800
                    ]
                ]
            }
        }
    },
    "Carriageway Slab": {
        "Curved Tendons in Steel Ducts": {
            # 2c: Carriageway slab - Curved Tendons in Steel Ducts
            "2c": {
                "range": (2.53829, 9.495417),
                "coefficients": [
                    -0.0000172013580987951000,
                    0.0006655090452650890000,
                    -0.0092990709658604000000,
                    0.0526984736958446000000,
                    -0.0594107497996482000000,
                    1.1567535295761300
                ]
            }
        },
        "Rebar, Pre/Post Tension": {
            # 3c: Carriageway slab - Rebar, Pre/Post Tension
            "3c": {
                "range": (2.842679, 9.495417),
                "coefficients": [
                    -0.0000668624928916728000,
                    0.0021180728785876900000,
                    -0.0253621630643829000000,
                    0.1364095218132770000,
                    -0.2719485867510570000,
                    1.2110151456198900
                ]
            }
        },
        "Shear Reinforcement": {
            # 4c: Carriageway slab - Shear Reinforcement
            "4c": {
                "range": (2.842679, 9.495417),
                "coefficients": [
                    -0.0000668624928916728000,
                    0.0021180728785876900000,
                    -0.0253621630643829000000,
                    0.1364095218132770000,
                    -0.2719485867510570000,
                    1.2110151456198900
                ]
            }
        }
    }
}


# 강재 유형을 표준 유형으로 매핑하는 함수 (철도와 동일한 패턴)


steel_type_map = {
    "Straight and bent bars": "Rebar, Pre/Post Tension",
    "Welded bars and wire fabrics": "Rebar, Pre/Post Tension",
    "Splicing devices (reinforcing)": "Splicing Devices",
    "Curved Tendons in Steel Ducts": "Curved Tendons in Steel Ducts",
    "Pre-tensioning": "Rebar, Pre/Post Tension",
    "Post-tensioning[Single strands in plastic ducts]": "Rebar, Pre/Post Tension",
    "Post-tensioning[Straight tendons or curved in plastic ducts]": "Rebar, Pre/Post Tension",
    "Post-tensioning[Curved tendons in steel ducts]": "Curved Tendons in Steel Ducts",
    "Post-tensioning[Splicing devices]": "Splicing Devices",
    "Shear reinforcement": "Shear Reinforcement"
}


def map_steel_type_to_table_key(ui_steel_type):
    return steel_type_map.get(ui_steel_type, "Rebar, Pre/Post Tension")
        
def get_lambda1_road(support_type, steel_type, span_length, traffic_type="Standard traffic"):
    """
    도로교량 λs,1 값 계산
    
    Args:
        support_type (str): 지지 조건
        steel_type (str): 강재 유형
        span_length (float): 경간 길이 (m)
        traffic_type (str): 교통 하중 유형
    
    Returns:
        float: 계산된 lambda1 값
    """
    # 강재 유형을 표준 유형으로 변환
    std_steel_type = steel_type_map.get(steel_type, "Rebar, Pre/Post Tension")
    
    print(f"Debug: support_type={support_type}, steel_type={steel_type}, std_steel_type={std_steel_type}, span_length={span_length}")
    
    # 테이블에서 해당 지지 조건 찾기
    type_table = lambda1_table.get(support_type, {})

    
    print(f"Debug: type_table keys: {list(type_table.keys())}")
    
    # 강재 유형 찾기
    steel_type_table = type_table.get(std_steel_type, {})
    if not steel_type_table:
        print(f"Warning: Steel type '{std_steel_type}' not found for support type '{support_type}'")
        # 폴백 메커니즘 시도
        available_steel_types = list(type_table.keys())
        fallback_priority = [
            "Splicing Devices",
            "Rebar, Pre/Post Tension", 
            "Curved Tendons in Steel Ducts",
            "Shear Reinforcement"
        ]
        
        for fallback_type in fallback_priority:
            if fallback_type in available_steel_types:
                steel_type_table = type_table[fallback_type]
                print(f"Debug: Using fallback steel type: {fallback_type}")
                break
        
        if not steel_type_table:
            print("Error: No steel type data available")
            return "lambdaerror"
    
    print(f"Debug: steel_type_table structure: {steel_type_table}")
    
    # 새로운 서브타입 키들 정의
    subtype_keys = ['1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b', '2c', '3c', '4c']
    
    # 서브타입이 있는 경우 처리
    if any(key in subtype_keys for key in steel_type_table.keys()):
        print("Debug: Found subtypes in steel_type_table")
        
        # 모든 서브타입에 대해 검사
        for subtype_key, subtype_data in steel_type_table.items():
            print(f"Debug: Checking subtype {subtype_key}")
            
            result = calculate_from_subtype_data(subtype_data, span_length, subtype_key)
            if result is not None:
                return result
        
        print(f"Warning: No suitable range found in any subtype for span_length={span_length}")
        return "lambdaerror"
    
    # 직접적인 범위 처리 (서브타입이 없는 경우)
    else:
        result = calculate_from_subtype_data(steel_type_table, span_length, "direct")
        if result is not None:
            return result
        
        print(f"Warning: No matching lambda1 found for {support_type}, {std_steel_type}, {span_length}")
        return "lambdaerror"
        

def calculate_from_subtype_data(subtype_data, span_length, subtype_key):
    """
    서브타입 데이터에서 lambda 값 계산
    
    Args:
        subtype_data (dict): 서브타입 데이터
        span_length (float): 경간 길이
        subtype_key (str): 서브타입 키 (디버깅용)
    
    Returns:
        float or None: 계산된 lambda 값 또는 None
    """
    try:
        # 다중 범위 처리
        if "ranges" in subtype_data:
            ranges = subtype_data["ranges"]
            coeffs_list = subtype_data["coefficients"]
            
            for i, (min_range, max_range) in enumerate(ranges):
                if min_range <= span_length <= max_range:
                    coeffs = coeffs_list[i]
                    result = polynomial_interpolation2(span_length, coeffs)
                    print(f"Debug: Found match in {subtype_key}, range [{min_range}, {max_range}], result={result}")
                    return result
            
            print(f"Debug: Span length {span_length} outside all ranges for {subtype_key}")
        
        # 단일 범위 처리
        elif "range" in subtype_data:
            min_range, max_range = subtype_data["range"]
            if min_range <= span_length <= max_range:
                coeffs = subtype_data["coefficients"]
                result = polynomial_interpolation2(span_length, coeffs)
                print(f"Debug: Found match in {subtype_key}, range [{min_range}, {max_range}], result={result}")
                return result
            else:
                print(f"Debug: Span length {span_length} outside range [{min_range}, {max_range}] for {subtype_key}")
        
        return None
        
    except Exception as e:
        print(f"Error in calculate_from_subtype_data: {e}")
        return None

def polynomial_interpolation2(x, coefficients):
    """
    다항식 보간법으로 값 계산
    
    Args:
        x (float): 입력값 (경간 길이)
        coefficients (list): 다항식 계수들 (최고차항부터 상수항까지)
    f
    Returns:
        float: 계산된 값
    """
    try:
        result = 0.0
        n = len(coefficients)
        for i, coeff in enumerate(coefficients):
            power = n - 1 - i
            result += coeff * (x ** power)
        
        # 결과값이 너무 작거나 음수인 경우 최소값 보장
        return max(result, 0.1)
        
    except Exception as e:
        print(f"Error in polynomial_interpolation: {e}")
        return 1.0
    
# Splicing devices (reinforcing)



    # "Straight and bent bars": "Rebar, Pre/Post Tension",
    # "Welded bars and wire fabrics": "Rebar, Pre/Post Tension",
    # "Splicing devices (reinforcing)": "Splicing Devices",
    # "Curved Tendons in Steel Ducts": "Curved Tendons in Steel Ducts",
    # "Pre-tensioning": "Rebar, Pre/Post Tension",
    # "Post-tensioning[Single strands in plastic ducts]": "Rebar, Pre/Post Tension",
    # "Post-tensioning[Straight tendons or curved in plastic ducts]": "Rebar, Pre/Post Tension",
    # "Post-tensioning[Curved tendons in steel ducts]": "Curved Tendons in Steel Ducts",
    # "Post-tensioning[Splicing devices]": "Splicing Devices",
    # "Reinforcing steel": "Rebar, Pre/Post Tension",
    # "Shear reinforcement": "Shear Reinforcement"

# 1a): Continuous beam - Splicing Devices
# 1b): Single span beam - Splicing Devices
# 2a): Continuous beam - Curved Tendons in Steel Ducts
# 2b): Single span beam - Curved Tendons in Steel Ducts
# 2c): Carriageway slab - Curved Tendons in Steel Ducts
# 3a)  Continuous beam  - Rebar, Pre/Post Tension
# 4a) Continuous beam "- Shear Reinforcement"
# 4b): Single span beam - "Shear Reinforcement"
# 3b): Single span beam -  Rebar, Pre/Post Tension
# 3c) Carriageway slab -  Rebar, Pre/Post Tension
# 4c): Carriageway slab - "Shear Reinforcement"
# 테스트 함수
def test_lambda1_calculation_road():
    """lambda1 계산 테스트 함수"""
    test_cases = [
        ("Carriageway Slab", "Reinforcing steel", 9),  
        # ("Single Span Beam", "Straight and bent bars", 21.0),  # 3b 사용
        # ("Single Span Beam", "Shear reinforcement", 21.0),    # 4b 사용
        # ("Single Span Beam", "Splicing devices (reinforcing)", 21.0),  # 1b 사용
        # ("Continuous Beam", "Straight and bent bars", 21.0),   # 3a 사용
        # ("Carriageway Slab", "Straight and bent bars", 5.0),   # 3c 사용
    ]
    
    for support_type, steel_type, span_length in test_cases:
        result = get_lambda1_road(support_type, steel_type, span_length)
        print(f"\nTest: {support_type}, {steel_type}, {span_length}m → λ1 = {result}")
        print("-" * 80)

# 테스트 실행
if __name__ == "__main__":
    test_lambda1_calculation_road()

# steel_type = st.selectbox(
#     "Steel Type",
#     [
#         "Straight and bent bars",
#         "Welded bars and wire fabrics",
#         "Splicing devices (reinforcing)",
#         "Pre-tensioning",
#         "Post-tensioning[Single strands in plastic ducts]",
#         "Post-tensioning[Straight tendons or curved in plastic ducts]",
#         "Post-tensioning[Curved tendons in steel ducts]",
#         "Post-tensioning[Splicing devices]"
#     ],
# "Straight and bent bars": "Rebar, Pre/Post Tension",
# "Welded bars and wire fabrics": "Rebar, Pre/Post Tension",
# "Splicing devices (reinforcing)": "Splicing Devices",
# "Curved Tendons in Steel Ducts": "Curved Tendons in Steel Ducts",
# "Pre-tensioning": "Rebar, Pre/Post Tension",
# "Post-tensioning[Single strands in plastic ducts]": "Rebar, Pre/Post Tension",
# "Post-tensioning[Straight tendons or curved in plastic ducts]": "Rebar, Pre/Post Tension",
# "Post-tensioning[Curved tendons in steel ducts]": "Curved Tendons in Steel Ducts",
# "Post-tensioning[Splicing devices]": "Splicing Devices",
# "Reinforcing steel": "Rebar, Pre/Post Tension",
# "Shear reinforcement": "Shear Reinforcement"
# 강재 유형별 S-N 곡선 지수 (k2) - 도로교량용
road_steel_k2_values = {
    "Straight and bent bars": 9,
    "Welded bars and wire fabrics": 5,
    "Splicing devices (reinforcing)": 5,
    "Pre-tensioning": 9,
    "Post-tensioning[Single strands in plastic ducts]": 9,
    "Post-tensioning[Straight tendons or curved in plastic ducts]": 10,
    "Post-tensioning[Curved tendons in steel ducts]": 7,
    "Post-tensioning[Splicing devices]":5,
    "Shear reinforcement": 9
}

# 강재 유형별 기준 응력 범위 테이블 (2×10^6 주기 기준) [N/mm²]
road_steel_stress_range_table = {
    "Straight and bent bars": 180,
    "Welded bars and wire fabrics": 100,
    "Splicing devices (reinforcing)": 100,
    "Pre-tensioning": 170,
    "Post-tensioning[Single strands in plastic ducts]": 170,
    "Post-tensioning[Straight tendons or curved in plastic ducts]":145,
    "Post-tensioning[Curved tendons in steel ducts]": 110,
    "Post-tensioning[Splicing devices]":70,
    "Shear reinforcement": 180
}

def get_k2_value_road(steel_type):
    """도로교량용 강재 유형에 따른 S-N 곡선 지수(k2) 반환"""
    return road_steel_k2_values.get(steel_type, 9)  # 기본값 9

def get_stress_range_road(steel_type):
    """도로교량용 강재 유형에 따른 기준 응력 범위(ΔσRsk) 반환"""
    return road_steel_stress_range_table.get(steel_type, 0)  # 기본값 162.5 MPa

def calculate_lambda2_road(vol, steel_type, traffic_type):
    """
    도로교량용 λs,2 계산
    
    Args:
        vol (float): 연간 교통량 (백만 대/년)
        steel_type (str): 강재 유형
        traffic_type (str): 교통 유형 ('Long distance', 'Medium distance', 'Local traffic')
    
    Returns:
        float: 계산된 lambda2 값
    """
    # Q̄ 값 테이블 (교통 유형별)
    Q_bar_values = {
        5: {'Long distance': 1.0, 'Medium distance': 0.90, 'Local traffic': 0.73},
        7: {'Long distance': 1.0, 'Medium distance': 0.92, 'Local traffic': 0.78},
        9: {'Long distance': 1.0, 'Medium distance': 0.94, 'Local traffic': 0.82}
    }
    
    k2 = get_k2_value_road(steel_type)
    Q_bar = Q_bar_values.get(k2, Q_bar_values[9]).get(traffic_type, 0.94)
    
    # λs,2 = Q̄^k2 * (Nobs/2.0)^0.5
    lambda2 = Q_bar * ((vol / (2 * 10**6)) ** (1 / k2))
    
    return lambda2, Q_bar

def calculate_lambda3_road(nyear, k2):
    """도로교량용 λs,3 계산 - 설계 수명에 따른 보정"""
    return (nyear / 100) ** (1 / k2)

def calculate_lambda4_road(n_obs_list, k2):
    if not n_obs_list or len(n_obs_list) == 0:
        return 1.0
    
    
    # ΣN_obs,i 계산 (모든 차선의 합)
    sum_n_obs = sum(n_obs_list)
    
    # λs,4 = k2√(ΣN_obs,i / N_obs,1) 공식 적용
    lambda4 = ((sum_n_obs / 1) ** (1/k2))
    
    return lambda4
# calc/road_concrete_lambda.py에 추가


