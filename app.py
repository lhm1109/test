import streamlit as st
from utils.page_manager import page_manager

def index():
    st.title("Midas User Streamlit App")
    st.write("Welcome to the Midas User Streamlit application.")
    st.write("This app is designed to demonstrate various features and functionalities.")
    
    # 페이지 관리 섹션 추가
    st.header("📋 페이지 관리")
    
    # 현재 등록된 페이지 목록 표시
    st.subheader("현재 등록된 페이지")
    page_keys = page_manager.get_page_keys()
    if page_keys:
        for key in page_keys:
            config = page_manager.get_page_config(key)
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"**{config['title']}** ({key})")
            with col2:
                st.write(f"URL: {config['url_path']}")
            with col3:
                st.write(f"카테고리: {config.get('category', 'Pages')}")
            with col4:
                if config['is_default']:
                    st.write("🏠 **기본 페이지**")
                else:
                    if st.button(f"기본으로 설정", key=f"set_default_{key}"):
                        page_manager.set_default_page(key)
                        st.rerun()
    else:
        st.info("등록된 페이지가 없습니다.")
    
    # 페이지 관리 기능
    st.subheader("페이지 관리 기능")
    
    # 새 페이지 등록
    with st.expander("➕ 새 페이지 등록"):
        with st.form("register_page_form"):
            new_key = st.text_input("페이지 키", placeholder="예: home, test, analysis")
            new_title = st.text_input("페이지 제목", placeholder="예: 홈페이지, 테스트 페이지")
            new_url_path = st.text_input("URL 경로", placeholder="예: /home, /test")
            new_source = st.text_input("페이지 소스 (파일 경로 또는 함수명)", placeholder="예: routes/test.py 또는 index")
            new_category = st.selectbox("카테고리", ["Main", "Analysis", "Standards", "Tools", "Development", "Pages"])
            is_default = st.checkbox("기본 페이지로 설정")
            
            if st.form_submit_button("페이지 등록"):
                if new_key and new_title and new_url_path and new_source:
                    # 함수인지 파일인지 확인
                    if new_source == "index":
                        page_source = index
                    else:
                        page_source = new_source
                    
                    success = page_manager.register_page(
                        key=new_key,
                        title=new_title,
                        url_path=new_url_path,
                        page_source=page_source,
                        category=new_category,
                        is_default=is_default
                    )
                    if success:
                        st.rerun()
                else:
                    st.error("모든 필드를 입력해주세요.")
    
    # 페이지 해제
    with st.expander("🗑️ 페이지 해제"):
        if page_keys:
            page_to_remove = st.selectbox("해제할 페이지 선택", page_keys)
            if st.button("페이지 해제"):
                if page_manager.unregister_page(page_to_remove):
                    st.rerun()
        else:
            st.info("해제할 페이지가 없습니다.")
    
    # 페이지 업데이트
    with st.expander("✏️ 페이지 업데이트"):
        if page_keys:
            page_to_update = st.selectbox("업데이트할 페이지 선택", page_keys, key="update_select")
            config = page_manager.get_page_config(page_to_update)
            
            with st.form("update_page_form"):
                updated_title = st.text_input("새 제목", value=config['title'])
                updated_url_path = st.text_input("새 URL 경로", value=config['url_path'])
                updated_source = st.text_input("새 페이지 소스", value=str(config['page_source']))
                
                if st.form_submit_button("페이지 업데이트"):
                    # 함수인지 파일인지 확인
                    if updated_source == "index":
                        page_source = index
                    else:
                        page_source = updated_source
                    
                    success = page_manager.update_page(
                        key=page_to_update,
                        title=updated_title,
                        url_path=updated_url_path,
                        page_source=page_source
                    )
                    if success:
                        st.rerun()
        else:
            st.info("업데이트할 페이지가 없습니다.")
    
    # 모든 페이지 해제
    with st.expander("🗑️ 모든 페이지 해제"):
        if st.button("모든 페이지 해제", type="secondary"):
            if page_manager.clear_all_pages():
                st.rerun()

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
                st.write(f"**카테고리:** {config.get('category', 'Pages')}")
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
        demo_category = st.selectbox("카테고리", ["Main", "Analysis", "Standards", "Tools", "Development", "Pages"], key="demo_category")
        demo_default = st.checkbox("기본 페이지로 설정")
        
        if st.form_submit_button("데모 페이지 등록"):
            success = page_manager.register_page(
                key=demo_key,
                title=demo_title,
                url_path=demo_url,
                page_source=demo_source,
                category=demo_category,
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

# 초기 페이지 등록
def initialize_pages():
    """애플리케이션 시작 시 기본 페이지들을 등록합니다."""
    if page_manager.get_page_count() == 0:
        # 기본 페이지들 등록
        pages_to_register = [
            {
                "key": "home",
                "title": "Home",
                "url_path": "/",
                "page_source": index,
                "category": "Main",
                "is_default": True
            },
            {
                "key": "pygwalker_test",
                "title": "Pygwalker Test",
                "url_path": "/pygwalker_test",
                "page_source": "routes/pygwalker_test.py",
                "category": "Tools",
                "is_default": False
            },
            {
                "key": "as1170_2_2021",
                "title": "AS1170.2:2021",
                "url_path": "/as1170_2_2021",
                "page_source": "routes/as1170_2_2021.py",
                "category": "Standards",
                "is_default": False
            },
            {
                "key": "as1170_4_2024",
                "title": "AS1170.4:2024",
                "url_path": "/as1170_4_2024",
                "page_source": "routes/as1170_4_2024.py",
                "category": "Standards",
                "is_default": False
            },
            {
                "key": "as1170_4_2024_1",
                "title": "AS1170.4:2024 - Page 1",
                "url_path": "/as1170_4_2024_1",
                "page_source": "routes/as1170_4_2024_1.py",
                "category": "Standards",
                "is_default": False
            },
            {
                "key": "test",
                "title": "Test Page",
                "url_path": "/test",
                "page_source": "routes/test.py",
                "category": "Development",
                "is_default": False
            },
            {
                "key": "ms_1553_2002",
                "title": "MS 1553:2002",
                "url_path": "/ms_1553_2002",
                "page_source": "routes/ms_1553_2002.py",
                "category": "Standards",
                "is_default": False
            },
            {
                "key": "road_bridge_concrete_fatigue_analysis_ntc2018",
                "title": "Road Bridge Concrete Fatigue Analysis NTC 2018",
                "url_path": "/road_bridge_concrete_fatigue_analysis_ntc2018",
                "page_source": "routes/road_bridge_concrete_fatigue_analysis_ntc2018.py",
                "category": "Analysis",
                "is_default": False
            },
            {
                "key": "railway_bridge_fatigue_analysis_ntc2018",
                "title": "Railway Bridge Concrete Fatigue Analysis NTC 2018",
                "url_path": "/railway_bridge_concrete_fatigue_analysis_ntc2018",
                "page_source": "routes/railway_bridge_concrete_fatigue_analysis_ntc2018.py",
                "category": "Analysis",
                "is_default": False
            },
            {
                "key": "page_manager_demo",
                "title": "PageManager 데모",
                "url_path": "/demo",
                "page_source": demo_page,
                "category": "Development",
                "is_default": False
            }
        ]
        
        for page_config in pages_to_register:
            success = page_manager.register_page(**page_config)
            if not success:
                st.error(f"페이지 등록 실패: {page_config['key']}")

# 애플리케이션 초기화
initialize_pages()

# 네비게이션 생성 및 실행
pg = page_manager.create_navigation()
if pg:
    pg.run()
else:
    st.error("네비게이션을 생성할 수 없습니다. 페이지가 등록되어 있는지 확인해주세요.")
    st.write("현재 등록된 페이지:", page_manager.get_page_keys())