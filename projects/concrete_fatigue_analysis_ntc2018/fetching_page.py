# fetching_page.py
import streamlit as st
import time
import pandas as pd
from projects.concrete_fatigue_analysis_ntc2018.session_manager import FetchCivilData, update_temp_with_all_params, initialize_session

# PageManager 네비게이션 import
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from projects.concrete_fatigue_analysis_ntc2018.utils.navigator import (
    back_to_design_settings,
    back_to_bridge_type,
)

from utils.page_manager import (
    page_manager,
)

def clear_all_cache_except_api():
    """API 설정을 제외한 모든 사용자 데이터 삭제"""
    
    # 절대 지우면 안 되는 키들
    protected_keys = {
        # API 설정
        'current_mapi_key',
        'current_base_url', 
        'api_connected',
        'unit_data'
    }
    
    # 삭제할 키들 수집
    keys_to_delete = []
    for key in list(st.session_state.keys()):
        # 보호된 키가 아니고, Streamlit 내부 키(_로 시작)가 아닌 경우
        if key not in protected_keys and not key.startswith('_'):
            keys_to_delete.append(key)
    
    # 삭제 실행
    deleted_count = 0
    for key in keys_to_delete:
        if key in st.session_state:  # 안전 체크
            del st.session_state[key]
            deleted_count += 1
    
    # 필수 초기값들 재설정
    initialize_session()
    
    preserved_apis = [k for k in protected_keys if k in st.session_state]
    
    return deleted_count

def reset_loading_state():
    """로딩 상태 완전 초기화"""
    loading_keys = [
        'loading_step', 'loading_error', 'loading_complete', 'is_loading'
    ]
    for key in loading_keys:
        if key in st.session_state:
            del st.session_state[key]

def fetching_page():
    # 초기화
    if 'loading_step' not in st.session_state:
        st.session_state.loading_step = 0
        st.session_state.loading_error = None
        st.session_state.loading_complete = False
    
    # 로딩 UI
    st.markdown("""
        <div style="text-align: center; margin-top: 50px;">
            <h3>🔄 Loading Midas Civil Data...</h3>
            <p>Please wait while we fetch your model data from Midas Civil.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 프로그레스 바와 상태 텍스트
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    # 메인 컨텐츠 영역 - 고정 높이로 설정
    with st.container(height=650, border=False):
        # 에러가 발생한 경우
        if st.session_state.loading_error:
            st.error(f"❌ **Loading Failed**: {st.session_state.loading_error}")
            
            # 에러 상세 정보 표시
            with st.expander("🔍 Show error details"):
                st.code(str(st.session_state.loading_error))
                
                # 에러 타입별 해결 방법 제시
                error_str = str(st.session_state.loading_error).lower()
                if "400" in error_str:
                    st.warning("**HTTP 400 Error**: Bad request - Check your model data and API settings")
                elif "401" in error_str:
                    st.warning("**HTTP 401 Error**: Unauthorized - Check your API key")
                elif "403" in error_str:
                    st.warning("**HTTP 403 Error**: Forbidden - Check your permissions")
                elif "404" in error_str:
                    st.warning("**HTTP 404 Error**: Not found - Check your model and load cases")
                elif "timeout" in error_str:
                    st.warning("**Timeout Error**: Server response too slow - Try again later")
                elif "connection" in error_str:
                    st.warning("**Connection Error**: Check your network and API URL")
        
        # 로딩 완료된 경우
        elif st.session_state.loading_complete:
            st.success("🎉 **Data loaded successfully!**")
            status_text.text("✅ All data ready for analysis")
            progress_bar.progress(100)
            
        # 로딩 중인 경우
        else:
            # 로딩 단계별 처리
            loading_steps = [
                (10, "🔌 Initializing API connection..."),
                (25, "🔧 Loading section properties..."),
                (40, "🏗️ Processing elements..."),
                (55, "📋 Loading load cases..."),
                (70, "📊 Loading stress data..."),
                (85, "⚡ Loading force data..."),
                (95, "🏗️ Loading construction stage data..."),
                (100, "✅ Finalizing...")
            ]
            
            # 현재 단계 표시
            if st.session_state.loading_step < len(loading_steps):
                current_progress, current_status = loading_steps[st.session_state.loading_step]
                progress_bar.progress(current_progress)
                status_text.text(current_status)
                
                # 실제 로딩 작업 수행 (한 번에 하나씩)
                try:
                    if st.session_state.loading_step == 0:
                        # 초기화
                        time.sleep(0.8)  # 시각적 효과
                        st.session_state.loading_step += 1
                        st.rerun()
                        
                    elif st.session_state.loading_step == 1:
                        # 실제 데이터 로딩 시작
                        with st.spinner("Loading data from Midas Civil..."):
                            FetchCivilData.fetch_civil_data()
                        st.session_state.loading_step = len(loading_steps) - 1  # 마지막 단계로 점프
                        st.rerun()
                        
                    elif st.session_state.loading_step == len(loading_steps) - 1:
                        # 마무리
                        update_temp_with_all_params()
                        progress_bar.progress(100)
                        status_text.text("✅ Complete!")
                        st.session_state.loading_complete = True
                        time.sleep(1)  # 완료 메시지 표시 시간
                        st.rerun()
                        
                except Exception as e:
                    st.session_state.loading_error = str(e)
                    st.session_state.is_loading = False
                    st.rerun()
            
            # 로딩 중일 때만 자동 새로고침
            if not st.session_state.loading_error and not st.session_state.loading_complete:
                # 실제 로딩 단계에서는 자동 새로고침 비활성화 (수동 제어)
                if st.session_state.loading_step == 0:
                    st.markdown("""
                        <script>
                        setTimeout(function() {
                            window.location.reload();
                        }, 1000);
                        </script>
                    """, unsafe_allow_html=True)

    # 구분선
    st.markdown("---")
    
    # 하단 버튼 영역 - 상태에 따라 다른 버튼 표시
    # st.markdown("### Actions")
    
    # 로딩 완료된 경우 - Continue 버튼
    if st.session_state.loading_complete:
        if st.button("**Continue to Design Settings** →", use_container_width=True, type="primary", key="continue_main_btn"):
            reset_loading_state()
            page_manager.unregister_page("fetching_page")
            back_to_design_settings()
    
    # 에러 발생한 경우 - 에러 관련 버튼들
    elif st.session_state.loading_error:
        st.markdown("#### 🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 **Retry Now**", use_container_width=True, type="primary"):
                reset_loading_state()
                st.rerun()
        
        with col2:
            if st.button("🧹 **Clear & Retry**", use_container_width=True, type="secondary"):
                clear_all_cache_except_api()
                reset_loading_state()
                st.rerun()
        
        with col3:
            if st.button("← **Back to Home**", use_container_width=True):
                clear_all_cache_except_api()
                reset_loading_state()
                back_to_bridge_type()
    
    # 로딩 중인 경우 - Cancel 버튼과 추가 옵션들
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("❌ Cancel & Go Home", use_container_width=True, type="secondary"):
                clear_all_cache_except_api()
                reset_loading_state()
                back_to_bridge_type()
        
        with col2:
            if st.button("🗑️ Clear Cache", use_container_width=True, help="Clear all cached data except API settings"):
                clear_all_cache_except_api()
                st.rerun()
        
        with col3:
            if st.button("🔄 Refresh Data", use_container_width=True):
                # 데이터만 지우고 다시 로드
                data_keys = {
                    'civil_load_cases_data', 'civil_result_df', 'civil_all_element_data',
                    'civil_result_force_df', 'civil_result_conststage_df', 'section_properties_df'
                }
                for key in data_keys:
                    if key in st.session_state:
                        del st.session_state[key]
                
                # 로딩 상태 초기화
                st.session_state.loading_step = 0
                st.session_state.loading_error = None
                st.session_state.loading_complete = False
                st.session_state.is_loading = True
                
                # 현재 페이지에서 다시 로드
                st.rerun()

# 기존 함수들은 그대로 유지하되 사용하지 않음
def add_cancel_button_with_cache_clear():
    """캔슬 버튼을 추가하고 캐시 클리어 기능을 제공하는 함수 (사용 안함)"""
    pass

def add_analysis_page_buttons():
    """분석 페이지용 버튼들 (사용 안함)"""
    pass

if __name__ == "__main__":
    fetching_page()