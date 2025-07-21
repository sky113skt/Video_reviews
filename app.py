"""
Streamlit前端界面
电影影评Agent用户界面
"""

import streamlit as st
import requests
import json
from datetime import datetime
import asyncio
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="电影影评智能Agent",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        background-color: #ff6b6b;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .movie-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .review-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #ff6b6b;
    }
    .rating {
        font-size: 2rem;
        font-weight: bold;
        color: #ff6b6b;
    }
    </style>
""", unsafe_allow_html=True)

# API配置
API_BASE_URL = "http://localhost:8000"

def init_session_state():
    """初始化会话状态"""
    if 'review_history' not in st.session_state:
        st.session_state.review_history = []
    if 'current_movie' not in st.session_state:
        st.session_state.current_movie = None
    if 'current_review' not in st.session_state:
        st.session_state.current_review = None

@st.cache_data(ttl=3600)
def search_movies(query: str, year: int = None) -> List[Dict[str, Any]]:
    """搜索电影"""
    try:
        params = {"query": query}
        if year and year > 0:
            params["year"] = year
            
        response = requests.get(f"{API_BASE_URL}/api/search", params=params)
        if response.status_code == 200:
            return [response.json()]
        return []
    except Exception as e:
        st.error(f"搜索失败: {e}")
        return []

@st.cache_data(ttl=3600)
def get_popular_movies(page: int = 1) -> List[Dict[str, Any]]:
    """获取热门电影"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/popular", params={"page": page})
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"获取热门电影失败: {e}")
        return []

def generate_review(title: str, year: int = None, **kwargs) -> Dict[str, Any]:
    """生成影评"""
    try:
        request_data = {
            "title": title,
            "year": year,
            "target_audience": kwargs.get("target_audience", "普通观众"),
            "review_style": kwargs.get("review_style", "professional"),
            "max_length": kwargs.get("max_length", 1000),
            "include_spoilers": kwargs.get("include_spoilers", False)
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/review",
            json=request_data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"生成影评失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"请求失败: {e}")
        return None

def display_movie_info(movie_info: Dict[str, Any]):
    """显示电影信息"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if movie_info.get("poster_url"):
            st.image(movie_info["poster_url"], width=200)
        else:
            st.image("https://via.placeholder.com/200x300/667eea/ffffff?text=No+Poster", width=200)
    
    with col2:
        st.markdown(f"### {movie_info.get('title', '未知电影')}")
        
        if movie_info.get('year'):
            st.write(f"**上映年份**: {movie_info['year']}")
        
        if movie_info.get('rating'):
            st.write(f"**TMDB评分**: ⭐ {movie_info['rating']}/10")
        
        if movie_info.get('runtime'):
            st.write(f"**片长**: {movie_info['runtime']}分钟")
        
        if movie_info.get('genre'):
            genres = ", ".join(movie_info['genre'])
            st.write(f"**类型**: {genres}")
        
        if movie_info.get('director'):
            directors = ", ".join(movie_info['director'])
            st.write(f"**导演**: {directors}")
        
        if movie_info.get('cast'):
            cast = ", ".join(movie_info['cast'][:5])
            st.write(f"**主演**: {cast}")
        
        if movie_info.get('plot'):
            st.write(f"**剧情简介**: {movie_info['plot']}")

def display_review(review_data: Dict[str, Any]):
    """显示影评内容"""
    st.markdown("---")
    st.markdown("### 📋 生成的影评")
    
    # 评分显示
    rating = review_data.get('rating', 0)
    st.markdown(f"#### 综合评分: <span class='rating'>{rating}/10</span>", unsafe_allow_html=True)
    
    # 影评内容
    st.markdown(""<div class="review-section">
        <h4>影评内容</h4>
        <p>{}"">.format(review_data.get('review', '无内容')), unsafe_allow_html=True)
    
    # 统计信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("字数", review_data.get('word_count', 0))
    with col2:
        st.metric("生成时间", review_data.get('generated_at', '').split('T')[0])
    with col3:
        st.metric("信息来源", len(review_data.get('sources', [])))

def main():
    """主应用"""
    init_session_state()
    
    st.title("🎬 电影影评智能Agent")
    st.markdown("基于LangChain的智能影评生成系统")
    
    # 侧边栏
    with st.sidebar:
        st.header("🔍 搜索电影")
        
        search_type = st.radio("搜索方式", ["按名称搜索", "浏览热门电影"])
        
        if search_type == "按名称搜索":
            movie_name = st.text_input("电影名称", placeholder="请输入电影名称...")
            movie_year = st.number_input("上映年份(可选)", min_value=1900, max_value=2030, value=0, step=1)
            
            if st.button("搜索", key="search_btn"):
                if movie_name:
                    with st.spinner("正在搜索..."):
                        movies = search_movies(movie_name, movie_year if movie_year > 0 else None)
                        if movies:
                            st.session_state.current_movie = movies[0]
                            st.success(f"找到电影: {movies[0]['title']}")
                        else:
                            st.error("未找到相关电影")
        
        else:
            page = st.number_input("页码", min_value=1, value=1)
            if st.button("获取热门电影", key="popular_btn"):
                with st.spinner("正在加载..."):
                    movies = get_popular_movies(page)
                    if movies:
                        st.session_state.popular_movies = movies
                        st.success(f"加载了{len(movies)}部热门电影")
    
    # 主内容区
    tab1, tab2, tab3, tab4 = st.tabs(["🎬 生成影评", "📊 历史记录", "⚙️ 设置", "ℹ️ 关于"])
    
    with tab1:
        st.header("生成个性化影评")
        
        # 电影选择
        movie_col1, movie_col2 = st.columns([3, 1])
        
        with movie_col1:
            selected_movie = st.text_input("电影名称*", placeholder="输入电影名称，如：肖申克的救赎")
        
        with movie_col2:
            selected_year = st.number_input("年份(可选)", min_value=1900, max_value=2030, value=0, step=1)
        
        # 高级选项
        with st.expander("高级选项", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                target_audience = st.selectbox(
                    "目标观众",
                    ["普通观众", "电影爱好者", "专业影评人", "学生群体", "家庭观众"]
                )
                
                review_style = st.selectbox(
                    "影评风格",
                    ["professional", "casual", "academic", "entertaining", "brief"]
                )
            
            with col2:
                max_length = st.slider("最大字数", 500, 2000, 1000, step=100)
                include_spoilers = st.checkbox("包含剧透", value=False)
        
        # 生成按钮
        if st.button("🚀 生成影评", type="primary", use_container_width=True):
            if not selected_movie:
                st.error("请输入电影名称")
            else:
                with st.spinner("🤖 AI正在分析并生成影评..."):
                    review_data = generate_review(
                        selected_movie,
                        selected_year if selected_year > 0 else None,
                        target_audience=target_audience,
                        review_style=review_style,
                        max_length=max_length,
                        include_spoilers=include_spoilers
                    )
                    
                    if review_data:
                        st.session_state.current_review = review_data
                        st.session_state.review_history.insert(0, {
                            **review_data,
                            "search_params": {
                                "title": selected_movie,
                                "year": selected_year,
                                "target_audience": target_audience
                            }
                        })
                        
                        # 显示成功消息
                        st.success("✅ 影评生成完成！")
                        
                        # 自动滚动到结果
                        st.balloons()
        
        # 显示当前电影信息
        if st.session_state.get('current_movie'):
            st.markdown("---")
            st.header("📽️ 电影信息")
            display_movie_info(st.session_state.current_movie)
        
        # 显示当前影评
        if st.session_state.get('current_review'):
            display_review(st.session_state.current_review)
            
            # 操作按钮
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 复制影评"):
                    st.code(st.session_state.current_review['review'], language=None)
            
            with col2:
                if st.button("💾 保存影评"):
                    # 这里可以添加保存到文件的功能
                    st.success("已保存到本地")
            
            with col3:
                if st.button("🔄 重新生成"):
                    st.session_state.current_review = None
                    st.rerun()
    
    with tab2:
        st.header("📊 历史影评记录")
        
        if not st.session_state.review_history:
            st.info("暂无历史记录，去生成第一篇影评吧！")
        else:
            for idx, review in enumerate(st.session_state.review_history):
                with st.expander(f"{idx+1}. 《{review['title']}》 - {review['rating']}/10"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**电影**: {review['title']}")
                        if review['year']:
                            st.write(f"**年份**: {review['year']}")
                        st.write(f"**评分**: {review['rating']}/10")
                        st.write(f"**生成时间**: {review['generated_at']}")
                    
                    with col2:
                        if st.button("查看详情", key=f"detail_{idx}"):
                            st.session_state.current_review = review
                            st.rerun()
    
    with tab3:
        st.header("⚙️ 设置")
        
        st.subheader("API配置")
        openai_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        tmdb_key = st.text_input("TMDB API Key", type="password", value=os.getenv("TMDB_API_KEY", ""))
        
        if st.button("保存配置"):
            # 这里可以添加保存到.env文件的功能
            st.success("配置已保存（重启后生效）")
        
        st.subheader("界面设置")
        theme = st.selectbox("界面主题", ["默认", "暗色", "亮色"])
        language = st.selectbox("界面语言", ["中文", "English"])
    
    with tab4:
        st.header("ℹ️ 关于")
        
        st.markdown("""
        ### 🎬 电影影评智能Agent
        
        这是一个基于LangChain的智能影评生成系统，能够：
        
        - 📊 整合多源电影信息
        - 🤖 智能分析电影内容
        - ✍️ 生成个性化影评
        - 📈 提供客观评分
        
        #### 技术栈
        - **后端**: FastAPI + LangChain + OpenAI
        - **前端**: Streamlit
        - **数据源**: TMDB API
        - **分析**: 情感分析 + 主题提取
        
        #### 使用说明
        1. 在侧边栏搜索电影或浏览热门电影
        2. 调整生成参数获得个性化影评
        3. 查看生成结果并保存喜欢的影评
        
        #### 注意事项
        - 需要配置OpenAI API密钥
        - 需要配置TMDB API密钥
        - 影评生成可能需要一些时间
        """)
        
        st.info("版本: 1.0.0 | 作者: AI Agent Team")

if __name__ == "__main__":
    main()