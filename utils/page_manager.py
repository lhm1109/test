import streamlit as st
from typing import Dict, List, Optional, Union, Callable
import importlib.util
import os

class PageManager:
    """
    Streamlit 페이지를 동적으로 관리하는 클래스
    Key-Value 기반으로 페이지를 등록하고 해제할 수 있습니다.
    """
    
    def __init__(self):
        self._pages: Dict[str, st.Page] = {}
        self._page_configs: Dict[str, dict] = {}
        self._default_page: Optional[str] = None
    
    def register_page(self, 
                     key: str, 
                     title: str, 
                     url_path: str,
                     page_source: Union[str, Callable],
                     hidden: bool = False,
                     category: str = "Pages",
                     is_default: bool = False) -> bool:
        """
        새로운 페이지를 등록합니다.
        
        Args:
            key: 페이지 식별자
            title: 페이지 제목
            url_path: URL 경로
            page_source: 페이지 소스 (파일 경로 또는 함수)
            is_default: 기본 페이지 여부
            hidden: 페이지 숨김 여부
            category: 페이지 카테고리
            
        Returns:
            bool: 등록 성공 여부
        """
        try:
            if key in self._pages:
                st.warning(f"페이지 '{key}'가 이미 등록되어 있습니다.")
                return False
            
            # 페이지 객체 생성
            if isinstance(page_source, str):
                # 파일 경로인 경우
                page = st.Page(page_source, title=title, url_path=url_path)
            else:
                # 함수인 경우
                page = st.Page(page_source, title=title, url_path=url_path)
            
            self._pages[key] = page
            self._page_configs[key] = {
                'title': title,
                'url_path': url_path,
                'page_source': page_source,
                'is_default': is_default,
                'category': category,
                'hidden': hidden
            }
            
            if is_default:
                self._default_page = key
            
            # st.success(f"페이지 '{key}' ({title})가 성공적으로 등록되었습니다.")
            return True
            
        except Exception as e:
            st.error(f"페이지 등록 중 오류 발생: {str(e)}")
            return False
    
    def unregister_page(self, key: str) -> bool:
        """
        페이지를 해제합니다.
        
        Args:
            key: 페이지 식별자
            
        Returns:
            bool: 해제 성공 여부
        """
        if key not in self._pages:
            st.warning(f"페이지 '{key}'가 등록되어 있지 않습니다.")
            return False
        
        try:
            page_config = self._page_configs[key]
            del self._pages[key]
            del self._page_configs[key]
            
            # 기본 페이지인 경우 기본 페이지 설정 해제
            if self._default_page == key:
                self._default_page = None
            
            st.success(f"페이지 '{key}' ({page_config['title']})가 성공적으로 해제되었습니다.")
            return True
            
        except Exception as e:
            st.error(f"페이지 해제 중 오류 발생: {str(e)}")
            return False
    
    def update_page(self, 
                   key: str, 
                   title: Optional[str] = None, 
                   url_path: Optional[str] = None,
                   hidden: Optional[bool] = None,
                   page_source: Optional[Union[str, Callable]] = None) -> bool:
        """
        등록된 페이지의 정보를 업데이트합니다.
        
        Args:
            key: 페이지 식별자
            title: 새로운 제목 (선택사항)
            url_path: 새로운 URL 경로 (선택사항)
            page_source: 새로운 페이지 소스 (선택사항)
            hidden: 페이지 숨김 여부 (선택사항)
            
        Returns:
            bool: 업데이트 성공 여부
        """
        if key not in self._pages:
            st.warning(f"페이지 '{key}'가 등록되어 있지 않습니다.")
            return False
        
        try:
            config = self._page_configs[key]
            
            # 업데이트할 값들
            new_title = title if title is not None else config['title']
            new_url_path = url_path if url_path is not None else config['url_path']
            new_page_source = page_source if page_source is not None else config['page_source']
            new_hidden = hidden if hidden is not None else config.get('hidden', False)
            
            # 기존 페이지 해제
            del self._pages[key]
            
            # 새 페이지 등록
            if isinstance(new_page_source, str):
                page = st.Page(new_page_source, title=new_title, url_path=new_url_path)
            else:
                page = st.Page(new_page_source, title=new_title, url_path=new_url_path)
            
            self._pages[key] = page
            self._page_configs[key] = {
                'title': new_title,
                'url_path': new_url_path,
                'page_source': new_page_source,
                'is_default': config['is_default'],
                'hidden': new_hidden,
                'category': config['category']
            }
            
            st.success(f"페이지 '{key}'가 성공적으로 업데이트되었습니다.")
            return True
            
        except Exception as e:
            st.error(f"페이지 업데이트 중 오류 발생: {str(e)}")
            return False
    
    def get_page(self, key: str) -> Optional[st.Page]:
        """
        특정 페이지를 반환합니다.
        
        Args:
            key: 페이지 식별자
            
        Returns:
            Optional[st.Page]: 페이지 객체 또는 None
        """
        return self._pages.get(key)
    
    def get_all_pages(self) -> List[st.Page]:
        """
        모든 등록된 페이지를 반환합니다.
        
        Returns:
            List[st.Page]: 페이지 객체 리스트
        """
        return list(self._pages.values())
    
    def get_page_keys(self) -> List[str]:
        """
        모든 등록된 페이지 키를 반환합니다.
        
        Returns:
            List[str]: 페이지 키 리스트
        """
        return list(self._pages.keys())
    
    def get_page_config(self, key: str) -> Optional[dict]:
        """
        특정 페이지의 설정을 반환합니다.
        
        Args:
            key: 페이지 식별자
            
        Returns:
            Optional[dict]: 페이지 설정 또는 None
        """
        return self._page_configs.get(key)
    
    def set_default_page(self, key: str) -> bool:
        """
        기본 페이지를 설정합니다.
        
        Args:
            key: 페이지 식별자
            
        Returns:
            bool: 설정 성공 여부
        """
        if key not in self._pages:
            st.warning(f"페이지 '{key}'가 등록되어 있지 않습니다.")
            return False
        
        self._default_page = key
        self._page_configs[key]['is_default'] = True
        
        # 다른 페이지들의 기본 페이지 설정 해제
        for other_key in self._page_configs:
            if other_key != key:
                self._page_configs[other_key]['is_default'] = False
        
        st.success(f"페이지 '{key}'가 기본 페이지로 설정되었습니다.")
        return True
    
    def get_default_page(self) -> Optional[str]:
        """
        기본 페이지 키를 반환합니다.
        
        Returns:
            Optional[str]: 기본 페이지 키 또는 None
        """
        return self._default_page
    
    def clear_all_pages(self) -> bool:
        """
        모든 페이지를 해제합니다.
        
        Returns:
            bool: 해제 성공 여부
        """
        try:
            self._pages.clear()
            self._page_configs.clear()
            self._default_page = None
            st.success("모든 페이지가 해제되었습니다.")
            return True
        except Exception as e:
            st.error(f"페이지 해제 중 오류 발생: {str(e)}")
            return False
    
    def page_exists(self, key: str) -> bool:
        """
        페이지가 존재하는지 확인합니다.
        
        Args:
            key: 페이지 식별자
            
        Returns:
            bool: 페이지 존재 여부
        """
        return key in self._pages
    
    def get_page_count(self) -> int:
        """
        등록된 페이지 수를 반환합니다.
        
        Returns:
            int: 페이지 수
        """
        return len(self._pages)
    
    def create_navigation(self) -> st.navigation:
        """
        등록된 페이지들로 네비게이션을 생성합니다.
        
        Returns:
            st.navigation: 생성된 네비게이션 객체
        """
        if not self._pages:
            st.warning("등록된 페이지가 없습니다.")
            return None
        
        # 카테고리별로 페이지 그룹화
        categories = {}
        for key, page in self._pages.items():
            config = self._page_configs[key]
            category = config.get('category', 'Pages')
            
            if category not in categories:
                categories[category] = []

            if config.get('hidden', False):
                continue
            
            # 기본 페이지인 경우 해당 카테고리의 첫 번째로 이동
            if config.get('is_default', False):
                categories[category].insert(0, page)
            else:
                categories[category].append(page)
        
        # 네비게이션 딕셔너리 생성
        navigation_dict = {}
        for category, pages in categories.items():
            navigation_dict[category] = pages
        
        return st.navigation(navigation_dict)

# 전역 페이지 매니저 인스턴스
page_manager = PageManager() 