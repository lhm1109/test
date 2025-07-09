# PageManager - 동적 Streamlit 페이지 관리 시스템

`PageManager`는 Streamlit 애플리케이션에서 페이지를 동적으로 등록하고 해제할 수 있는 시스템입니다. Key-Value 기반으로 페이지를 관리하여 런타임에 페이지를 추가하거나 제거할 수 있습니다.

## 주요 기능

- ✅ **동적 페이지 등록/해제**: 런타임에 페이지를 추가하거나 제거
- ✅ **Key-Value 기반 관리**: 의미있는 키로 페이지를 식별하고 관리
- ✅ **페이지 업데이트**: 등록된 페이지의 정보를 동적으로 변경
- ✅ **기본 페이지 설정**: 기본 페이지를 동적으로 변경
- ✅ **페이지 정보 조회**: 등록된 페이지들의 정보를 조회
- ✅ **에러 처리**: 안전한 페이지 관리와 에러 처리

## 기본 사용법

### 1. PageManager 임포트

```python
from utils.page_manager import page_manager
```

### 2. 페이지 등록

```python
# 함수 기반 페이지 등록
def my_page():
    st.title("내 페이지")
    st.write("페이지 내용")

page_manager.register_page(
    key="my_page",
    title="내 페이지",
    url_path="/my_page",
    page_source=my_page,
    is_default=False
)

# 파일 기반 페이지 등록
page_manager.register_page(
    key="analysis_page",
    title="분석 페이지",
    url_path="/analysis",
    page_source="routes/analysis.py",
    is_default=False
)
```

### 3. 페이지 해제

```python
page_manager.unregister_page("my_page")
```

### 4. 페이지 업데이트

```python
page_manager.update_page(
    key="my_page",
    title="새로운 제목",
    url_path="/new_path"
)
```

### 5. 네비게이션 생성

```python
pg = page_manager.create_navigation()
if pg:
    pg.run()
```

## 고급 기능

### 기본 페이지 설정

```python
# 기본 페이지 설정
page_manager.set_default_page("my_page")

# 기본 페이지 조회
default_key = page_manager.get_default_page()
```

### 페이지 정보 조회

```python
# 모든 페이지 키 조회
keys = page_manager.get_page_keys()

# 특정 페이지 설정 조회
config = page_manager.get_page_config("my_page")

# 페이지 존재 여부 확인
exists = page_manager.page_exists("my_page")

# 등록된 페이지 수
count = page_manager.get_page_count()
```

### 모든 페이지 해제

```python
page_manager.clear_all_pages()
```

## 실제 사용 예시

### 조건부 페이지 등록

```python
# 사용자 권한에 따라 페이지 등록
if user.has_admin_permission():
    page_manager.register_page(
        key="admin_panel",
        title="관리자 패널",
        url_path="/admin",
        page_source="routes/admin.py"
    )

# 환경 설정에 따라 페이지 등록
if st.secrets.get("ENABLE_BETA_FEATURES"):
    page_manager.register_page(
        key="beta_feature",
        title="베타 기능",
        url_path="/beta",
        page_source="routes/beta.py"
    )
```

### 동적 페이지 생성

```python
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
```

## API 참조

### PageManager 클래스

#### `register_page(key, title, url_path, page_source, is_default=False)`

새로운 페이지를 등록합니다.

**매개변수:**
- `key` (str): 페이지 식별자
- `title` (str): 페이지 제목
- `url_path` (str): URL 경로
- `page_source` (Union[str, Callable]): 페이지 소스 (파일 경로 또는 함수)
- `is_default` (bool): 기본 페이지 여부 (기본값: False)

**반환값:**
- `bool`: 등록 성공 여부

#### `unregister_page(key)`

페이지를 해제합니다.

**매개변수:**
- `key` (str): 페이지 식별자

**반환값:**
- `bool`: 해제 성공 여부

#### `update_page(key, title=None, url_path=None, page_source=None)`

등록된 페이지의 정보를 업데이트합니다.

**매개변수:**
- `key` (str): 페이지 식별자
- `title` (Optional[str]): 새로운 제목
- `url_path` (Optional[str]): 새로운 URL 경로
- `page_source` (Optional[Union[str, Callable]]): 새로운 페이지 소스

**반환값:**
- `bool`: 업데이트 성공 여부

#### `set_default_page(key)`

기본 페이지를 설정합니다.

**매개변수:**
- `key` (str): 페이지 식별자

**반환값:**
- `bool`: 설정 성공 여부

#### `get_page_keys()`

모든 등록된 페이지 키를 반환합니다.

**반환값:**
- `List[str]`: 페이지 키 리스트

#### `get_page_config(key)`

특정 페이지의 설정을 반환합니다.

**매개변수:**
- `key` (str): 페이지 식별자

**반환값:**
- `Optional[dict]`: 페이지 설정 또는 None

#### `create_navigation()`

등록된 페이지들로 네비게이션을 생성합니다.

**반환값:**
- `st.navigation`: 생성된 네비게이션 객체 또는 None

## 모범 사례

1. **키 명명 규칙**: 의미있는 키를 사용하세요 (예: `home`, `user_profile`, `admin_dashboard`)
2. **URL 경로**: RESTful 규칙을 따르세요 (예: `/users`, `/users/{id}`)
3. **에러 처리**: 항상 반환값을 확인하고 적절한 에러 처리를 하세요
4. **메모리 관리**: 사용하지 않는 페이지는 해제하여 메모리를 절약하세요
5. **기본 페이지**: 항상 하나의 기본 페이지를 설정하세요

## 파일 구조

```
streamlit/
├── utils/
│   ├── page_manager.py          # PageManager 클래스
│   ├── page_manager_demo.py     # 사용 예시 데모
│   └── README.md               # 이 파일
├── routes/                     # 페이지 파일들
└── app.py                     # 메인 애플리케이션
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 