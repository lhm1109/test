import streamlit as st
import sys
import os

# PageManager import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.page_manager import page_manager

def navigate_to_page(page_key):
    """
    PageManager를 사용하여 특정 페이지로 이동합니다.
    
    Args:
        page_key (str): 이동할 페이지의 키
    """
    st.empty()
    try:
        # 페이지가 존재하는지 확인
        if page_manager.page_exists(page_key):
            # 페이지 설정 가져오기
            page_config = page_manager.get_page_config(page_key)
            if page_config and 'page_source' in page_config:
                # 현재 페이지를 쿼리 파라미터에 저장
                st.query_params["page"] = page_key
                
                # 페이지 함수를 직접 호출
                page_source = page_config['page_source']
                if callable(page_source):
                    page_source()
                else:
                    st.error(f"페이지 소스가 호출 가능한 함수가 아닙니다: {page_key}")
            else:
                st.error(f"페이지 설정을 찾을 수 없습니다: {page_key}")
        else:
            st.error(f"페이지를 찾을 수 없습니다: {page_key}")
    except Exception as e:
        st.error(f"페이지 이동 중 오류 발생: {str(e)}")

    st.rerun()

def get_current_page():
    """
    현재 페이지 정보를 반환합니다.
    
    Returns:
        tuple: (page_key, page_config) 또는 (None, None)
    """
    current_page = st.query_params.get("page")
    if current_page:
        current_config = page_manager.get_page_config(current_page)
        return current_page, current_config
    return None, None

def render_current_page():
    """
    현재 페이지를 렌더링합니다.
    """
    st.empty()
    current_page, current_config = get_current_page()
    
    if current_page and current_config:
        page_source = current_config.get('page_source')
        if callable(page_source):
            page_source()
        else:
            st.error(f"현재 페이지를 렌더링할 수 없습니다: {current_page}")
    else:
        # 기본 페이지 표시
        st.error("현재 페이지 정보가 없습니다. 페이지를 선택해주세요.")
