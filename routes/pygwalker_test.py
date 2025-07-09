
# from pygwalker.api.streamlit import StreamlitRenderer
# import pandas as pd
# import streamlit as st
 
# Adjust the width of the Streamlit page
# st.set_page_config(
#     page_title="Use Pygwalker In Streamlit",
#     layout="wide"
# )
 
# # # Add Title
# # st.title("Use Pygwalker In Streamlit")
 
# # You should cache your pygwalker renderer, if you don't want your memory to explode
# @st.cache_resource
# def get_pyg_renderer() -> "StreamlitRenderer":
#     df = pd.read_csv("./resources/pygwalker/day.csv")
#     # If you want to use feature of saving chart config, set `spec_io_mode="rw"`
#     return StreamlitRenderer(df, spec="./gw_config.json", spec_io_mode="rw")
 
 
# renderer = get_pyg_renderer()
 
# renderer.explorer()

import streamlit as st
import pandas as pd
import pygwalker as pyg

# Streamlit 페이지 레이아웃 설정
st.set_page_config(page_title="Use Pygwalker In Streamlit", layout="wide")

# CSV 데이터 로드
@st.cache_data
def load_data():
    return pd.read_csv("./resources/pygwalker/day.csv")

df = load_data()

# HTML 코드로 pygwalker 렌더링 (spec 저장 포함)
pyg_html = pyg.to_html(df, spec="./gw_config.json", spec_io_mode="rw")

# HTML을 Streamlit에 직접 삽입
st.components.v1.html(pyg_html, height=1000, scrolling=True)


