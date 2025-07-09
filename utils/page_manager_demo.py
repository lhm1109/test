import streamlit as st
from .page_manager import page_manager

def demo_page():
    """PageManager 사용 예시를 보여주는 데모 페이지"""
    st.title("🔧 PageManager 사용 예시")
    st.write("이 페이지는 PageManager의 다양한 기능을 보여줍니다.")
    
    st.header("1. 기본 사용법")
    
    # 코드 예시
    st.subheader("페이지 등록")
    st.code("""
# 페이지 등록
page_manager.register_page(
    key="my_page",
    title="내 페이지",
    url_path="/my_page",
    page_source="routes/my_page.py",
    is_default=False
)
    """, language="python")
    
    st.subheader("페이지 해제")
    st.code("""
# 페이지 해제
page_manager.unregister_page("my_page")
    """, language="python")
    
    st.subheader("페이지 업데이트")
    st.code("""
# 페이지 업데이트
page_manager.update_page(
    key="my_page",
    title="새로운 제목",
    url_path="/new_path"
)
    """, language="python")
    
    st.header("2. 고급 기능")
    
    st.subheader("기본 페이지 설정")
    st.code("""
# 기본 페이지 설정
page_manager.set_default_page("my_page")
    """, language="python")
    
    st.subheader("페이지 정보 조회")
    st.code("""
# 모든 페이지 키 조회
keys = page_manager.get_page_keys()

# 특정 페이지 설정 조회
config = page_manager.get_page_config("my_page")

# 페이지 존재 여부 확인
exists = page_manager.page_exists("my_page")

# 등록된 페이지 수
count = page_manager.get_page_count()
    """, language="python")
    
    st.header("3. 실시간 데모")
    
    # 현재 상태 표시
    st.subheader("현재 등록된 페이지")
    page_keys = page_manager.get_page_keys()
    
    if page_keys:
        for key in page_keys:
            config = page_manager.get_page_config(key)
            with st.expander(f"{config['title']} ({key})"):
                st.write(f"**URL 경로:** {config['url_path']}")
                st.write(f"**페이지 소스:** {config['page_source']}")
                st.write(f"**기본 페이지:** {'예' if config['is_default'] else '아니오'}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"기본으로 설정", key=f"demo_set_default_{key}"):
                        page_manager.set_default_page(key)
                        st.rerun()
                with col2:
                    if st.button(f"해제", key=f"demo_remove_{key}"):
                        page_manager.unregister_page(key)
                        st.rerun()
    else:
        st.info("등록된 페이지가 없습니다.")
    
    # 새 페이지 등록 데모
    st.subheader("새 페이지 등록 데모")
    with st.form("demo_register_form"):
        demo_key = st.text_input("페이지 키", value="demo_page")
        demo_title = st.text_input("페이지 제목", value="데모 페이지")
        demo_url = st.text_input("URL 경로", value="/demo")
        demo_source = st.text_input("페이지 소스", value="routes/demo.py")
        demo_default = st.checkbox("기본 페이지로 설정")
        
        if st.form_submit_button("데모 페이지 등록"):
            success = page_manager.register_page(
                key=demo_key,
                title=demo_title,
                url_path=demo_url,
                page_source=demo_source,
                is_default=demo_default
            )
            if success:
                st.rerun()
    
    st.header("4. 프로그래밍 방식 사용")
    
    st.subheader("조건부 페이지 등록")
    st.code("""
# 사용자 권한에 따라 페이지 등록
if user.has_admin_permission():
    page_manager.register_page(
        key="admin_panel",
        title="관리자 패널",
        url_path="/admin",
        page_source="routes/admin.py"
    )

# 환경에 따라 페이지 등록
if st.secrets.get("ENABLE_BETA_FEATURES"):
    page_manager.register_page(
        key="beta_feature",
        title="베타 기능",
        url_path="/beta",
        page_source="routes/beta.py"
    )
    """, language="python")
    
    st.subheader("동적 페이지 생성")
    st.code("""
# 데이터베이스에서 페이지 정보를 가져와 등록
def load_pages_from_database():
    pages = database.get_all_pages()
    for page_data in pages:
        page_manager.register_page(
            key=page_data['key'],
            title=page_data['title'],
            url_path=page_data['url_path'],
            page_source=page_data['source'],
            is_default=page_data['is_default']
        )

# 사용자 설정에 따라 페이지 필터링
def filter_pages_by_user_preferences(user_preferences):
    all_keys = page_manager.get_page_keys()
    for key in all_keys:
        config = page_manager.get_page_config(key)
        if not user_preferences.should_show_page(config['title']):
            page_manager.unregister_page(key)
    """, language="python")
    
    st.header("5. 모범 사례")
    
    st.markdown("""
    - **키 명명 규칙**: 의미있는 키를 사용하세요 (예: `home`, `user_profile`, `admin_dashboard`)
    - **URL 경로**: RESTful 규칙을 따르세요 (예: `/users`, `/users/{id}`)
    - **에러 처리**: 항상 반환값을 확인하고 적절한 에러 처리를 하세요
    - **메모리 관리**: 사용하지 않는 페이지는 해제하여 메모리를 절약하세요
    - **기본 페이지**: 항상 하나의 기본 페이지를 설정하세요
    """)

# 데모 페이지를 PageManager에 등록하는 함수
def register_demo_page():
    """데모 페이지를 PageManager에 등록합니다."""
    if not page_manager.page_exists("demo"):
        page_manager.register_page(
            key="demo",
            title="PageManager 데모",
            url_path="/demo",
            page_source=demo_page,
            is_default=False
        )

# 데모 페이지 등록
register_demo_page() 