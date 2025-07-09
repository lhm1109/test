# first_setting.py
import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
from projects.concrete_fatigue_analysis_ntc2018.session_manager import *
from projects.concrete_fatigue_analysis_ntc2018.fatigue_concrete_simple_ui import fatigue_concrete_simple_ui_page
from projects.concrete_fatigue_analysis_ntc2018.fatigue_concrete_desm_rail_ui import fatigue_concrete_desm_rail_ui_page
from PIL import Image

# PageManager 네비게이션 import
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from projects.concrete_fatigue_analysis_ntc2018.utils.navigator import (
    navigate_to_loading_data,
    back_to_bridge_type,
    back_to_fatigue_case
)

initialize_session()
# st.text_input("Case name", value=st.session_state.case_name, key='case_name', 
#             on_change=update_temp_from_input, args=('case_name',), disabled=True)
st.session_state.case_name =""
st.session_state.span_length = 20.0
def Setting_Bridge():    
    # with st.container(height=100, border=False):
    #     st.markdown(f"<h3><b></b></h3>", unsafe_allow_html=True)
    #     st.markdown(f"<h5></h5>", unsafe_allow_html=True)
    if st.session_state.api_connected == False:
        st.error("❌ **API Connection Failed**: API connection is lost. Please start over from the beginning")
    else:
        with st.container(height=870, border=False):
            if st.session_state.bridge_type == "Railway":
                st.markdown("<h4><b>🚆 Railway Bridge Concrete Fatigue Analysis [NTC 2018]</b></h4>", unsafe_allow_html=True)
            else:
                st.markdown("<h4><b>🚗 Road Bridge Concrete Fatigue Analysis [NTC 2018]</b></h4>", unsafe_allow_html=True)
            if "bridge_type" not in st.session_state:
                st.session_state.bridge_type = "Road"

            def select_bridge(bridge_type):
                st.session_state.bridge_type = bridge_type
                st.rerun()
            
            FetchCivilData.initialize_civil_data()
            road_img = Image.open("resources/concrete_fatigue_analysis_ntc2018/roadicon.png")
            rail_img = Image.open("resources/concrete_fatigue_analysis_ntc2018/railwayicon.png")

            # 두 개 타일 나열
            # col1, col2 = st.columns(2)

            # with col1:
            #     if st.session_state.bridge_type == "Railway":
            #         pass
            #     else:
            #         road_selected = st.session_state.bridge_type == "Road"
            #         road_style = "selected-tile" if road_selected else "unselected-tile"
            #         st.markdown(f'<div class="{road_style}">', unsafe_allow_html=True)
            #         if st.button("🚗 Road Bridge", key="road_btn", use_container_width=True):
            #             select_bridge_type("Road")
            #             st.rerun()
            #         st.image(road_img, use_container_width=True)
            #         st.markdown('</div>', unsafe_allow_html=True)

            # with col2:
            #     if st.session_state.bridge_type == "Road":
            #         pass
            #     else:
            #         rail_selected = st.session_state.bridge_type == "Railway"
            #         rail_style = "selected-tile" if rail_selected else "unselected-tile"
            #         st.markdown(f'<div class="{rail_style}">', unsafe_allow_html=True)
            #         if st.button("🚆 Railway Bridge", key="rail_btn", use_container_width=True):
            #             select_bridge_type("Railway")
            #             st.rerun()
            #         st.image(rail_img, use_container_width=True)
            #         st.markdown('</div>', unsafe_allow_html=True)
            with st.container(height=420, border=False):
                col1, col2, col3 = st.columns([0.5,2,0.5])
                with col2:
                    if st.session_state.bridge_type == "Railway":
                        rail_selected = st.session_state.bridge_type == "Railway"
                        rail_style = "selected-tile" if rail_selected else "unselected-tile"
                        st.markdown(f'<div class="{rail_style}">', unsafe_allow_html=True)
                        # if st.button("🚆 Railway Bridge", key="rail_btn", use_container_width=True):
                        #     select_bridge_type("Railway")
                        #     st.rerun()
                        st.image(rail_img, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                    else:
                        road_selected = st.session_state.bridge_type == "Road"
                        road_style = "selected-tile" if road_selected else "unselected-tile"
                        st.markdown(f'<div class="{road_style}">', unsafe_allow_html=True)
                        # if st.button("🚗 Road Bridge", key="road_btn", use_container_width=True):
                        #     select_bridge_type("Road")
                        #     st.rerun()
                        st.image(road_img, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)


            with st.container(height=320, border=True):
                st.markdown("""
                **🔔 Fatigue Check Notice**
                - This plugin is based on the Italian code **NTC 2018**.
                - Only PSC composite sections and steel composite are supported  (PSC, General, User sections and stiffeners are excluded)
                - When viewing results in MIDAS Civil NX, select the PostCS mode(CS mode is not supported and may display incorrect results)
                - Superstructure only: not supported if substructure is modeled (one-directional loading only)  
                - Real-time loading not supported (no cycle counting or accumulation)  
                - Construction stage analysis must be defined (tendon stress required)  
                - Only design after analysis is supported (no modeling support)  
                - Fatigue Load Model 3 coefficients (1.75 for intermediate supports, 1.4 otherwise per EN 1992-2 NN2.1 (101)) are not supported — apply them in load combinations  
                - Only bent bar type shear reinforcement is supported  
                """)
        # Next 버튼
        if st.button("Start Fatigue Analysis (Load Civil NX Data) ➡", use_container_width=True, key="design_setting_btn", type="primary"):
            if st.session_state.bridge_type == "Railway":
                select_bridge_type("Railway")
            else:
                select_bridge_type("Road")


            # 로딩 상태 활성화 (중요!)
            st.session_state.is_loading = True
            navigate_to_loading_data()
def Setting_Parameter():
    if 'section_properties_df' in st.session_state:
        try:
            material_type = st.session_state.section_properties_df['type'].values
        except:
            material_type = None
        if material_type is not None:
            if st.session_state.api_connected == False:
                st.error("❌ **API Connection Failed**: API connection is lost. Please start over from the beginning")
            else:
                st.markdown(f"<h5><b>General Settings</b></h5>", unsafe_allow_html=True)
                if st.session_state.bridge_type == "":
                    with st.container(height = 860, border=False):
                        st.error("Bridge type is not selected")
                else:
                    # st.markdown(f"<h5><b>General Settings</b></h5>", unsafe_allow_html=True)
                    with st.container(height=845, border=False):

                        st.number_input(
                                r"Years of bridge project life, $N_{year}$", 
                                min_value=0.0, 
                                value=float(st.session_state.nyear), # Convert int to float
                                step=0.5, 
                                key="temp_nyear",
                                on_change=update_design_factors 
                                )
                        st.markdown(f"<h5><b>Design Parameters</b></h5>", unsafe_allow_html=True)
                        
                        # 파라미터 입력 필드들
                        st.number_input(
                            r" $\gamma_{C,\mathrm{fat}}$, Partial factor for fatigue of concrete",
                            min_value=0.0,
                            value=st.session_state.factor_rcfat,
                            step=0.5,
                            key="temp_rcfat",
                            on_change=update_design_factors 
                        )

                        st.number_input(
                            r"$\gamma_{S,\mathrm{fat}}$, Partial factor for fatigue of reinforcing steel",
                            min_value=0.0,
                            value=st.session_state.factor_rsfat,
                            step=0.05,
                            key="temp_rsfat",
                            on_change=update_design_factors
                        )

                        st.number_input(
                            r"$\gamma_{Sp,\mathrm{fat}}$, Partial factor for fatigue of prestressing steel",
                            min_value=0.0,
                            value=st.session_state.factor_rspfat,
                            step=0.05,
                            key="temp_rspfat",
                            on_change=update_design_factors
                        )

                        st.number_input(
                            r"$\gamma_{F}$, Partial factor for fatigue actions",
                            min_value=0.0,
                            value=st.session_state.factor_rf,
                            step=0.05,
                            key="temp_rf",
                            on_change=update_design_factors
                        )

                        st.number_input(
                            r"$\gamma_{Sd}$, Partial factor for uncertainty",
                            min_value=0.0,
                            value=st.session_state.factor_rsd,
                            step=0.05,
                            key="temp_rsd",
                            on_change=update_design_factors
                        )
                        
                        st.number_input(
                            r"$\gamma_{M}$, Partial factor for fatigue strength(steel grider)",
                            min_value=0.0,
                            value=st.session_state.factor_rm,
                            step=0.05,
                            key="temp_rm",
                            on_change=update_design_factors
                        )
                
                # Next 버튼
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("<- back", use_container_width=True):
                        back_to_bridge_type()
                if st.session_state.bridge_type == "":
                    pass
                else:
                    with col3:
                        if st.button("Next ➡", use_container_width=True, type="primary"):
                            update_temp_with_all_params()
                            back_to_fatigue_case()
        else:
            st.markdown(f"<h5><b>General Settings</b></h5>", unsafe_allow_html=True)
            with st.container(height = 860, border=False):
                # st.switch_page(st.Page(Setting_Bridge, title="Bridge Type"))
                st.error("❌ **MIDAS Civil Analysis File Loading Failed**: Please click 'Load' button on the first page")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("<- Required Data Loading", use_container_width=True):
                    back_to_bridge_type()
