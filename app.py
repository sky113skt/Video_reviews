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
import time
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
    /* 全局样式 */
    .main {
        padding: 0rem;
    }
    
    /* 标题样式 */
    .app-title {
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 2rem 0;
    }
    
    /* 搜索区域样式 */
    .search-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* 按钮样式 */
    .stButton>button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
    }
    
    /* 输入框样式 */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.8rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 数字输入框样式 */
    .stNumberInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.8rem;
        font-size: 1.1rem;
    }
    
    /* 电影卡片样式 */
    .movie-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    
    /* 影评区域样式 */
    .review-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin: 2rem 0;
        border-left: 5px solid #ff6b6b;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
      
    /* 进度条样式 */
    .loading-container {
        text-align: center;
        padding: 3rem;
    }
    
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* 导航栏样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 25px;
        padding: 0 20px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .search-container {
            margin: 1rem;
            padding: 1.5rem;
        }
        
        .app-title {
            font-size: 2rem;
            padding: 1rem 0;
        }
    }
    </style>
""", unsafe_allow_html=True)

# API配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")

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
    """生成影评 - 使用实时进度显示"""
    try:
        request_data = {
            "title": title,
            "year": year,
            "target_audience": kwargs.get("target_audience", "普通观众"),
            "review_style": kwargs.get("review_style", "professional"),
            "max_length": kwargs.get("max_length", 1000),
            "include_spoilers": kwargs.get("include_spoilers", False)
        }
        
        # 启动任务
        response = requests.post(
            f"{API_BASE_URL}/api/review",
            json=request_data,
            timeout=10
        )
        
        if response.status_code == 200:
            task_info = response.json()
            task_id = task_info["task_id"]
            
            # 轮询状态
            return poll_review_status(task_id)
        else:
            st.error(f"生成影评失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"请求失败: {e}")
        return None


def poll_review_status(task_id: str, max_attempts: int = 120) -> Dict[str, Any]:
    """轮询影评生成状态"""
    # 这些UI元素已经在主函数中创建了，这里不需要重复创建
    progress_bar = st.session_state.get('progress_bar', st.progress(0))
    status_text = st.session_state.get('status_text', st.empty())
    step_text = st.session_state.get('step_text', st.empty())
    time_elapsed = st.session_state.get('time_elapsed', st.empty())
    
    attempt = 0
    start_time = time.time()
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{API_BASE_URL}/api/review/status/{task_id}")
            if response.status_code == 200:
                status = response.json()
                
                # 更新进度显示
                progress = status.get("progress", 0) / 100
                progress_bar.progress(progress)
                status_text.text(status.get("message", "处理中..."))
                step_text.text(f"当前步骤: {status.get('current_step', '未知')}")
                
                # 更新计时器
                elapsed = int(time.time() - start_time)
                time_elapsed.text(f"⏱️ {elapsed}秒")
                
                if status.get("status") == "completed":
                    # 获取最终结果
                    result_response = requests.get(f"{API_BASE_URL}/api/review/result/{task_id}")
                    if result_response.status_code == 200:
                        return result_response.json()
                elif status.get("status") == "error":
                    st.error(f"生成失败: {status.get('error', '未知错误')}")
                    return None
            
            attempt += 1
            time.sleep(1)  # 每秒检查一次
            
        except Exception as e:
            print(f"状态检查失败: {e}")
            attempt += 1
            time.sleep(1)
    
    # 超时处理
    st.error("生成超时，请重试")
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
    
    # 影评内容
    review_text = review_data.get('review', '无内容')
    st.markdown(f"<div class='review-section'><h4>影评内容</h4><p>{review_text}</p></div>", unsafe_allow_html=True)
    
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
    
    # 主标题
    st.markdown('<h1 class="app-title">🎬 电影影评智能Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">基于AI的智能影评生成系统 - 让每一部电影都有专业解读</p>', unsafe_allow_html=True)
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 首页", "📊 历史记录", "⚙️ 设置", "ℹ️ 关于"])
    
    with tab1:
        # 搜索区域
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        # 搜索表单
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            movie_title = st.text_input(
                "",
                placeholder="请输入电影名称...",
                label_visibility="collapsed",
                max_chars=100
            )
        
        with col2:
            search_clicked = st.button("🔍 搜索", type="primary", use_container_width=True)
        
        # 高级选项折叠面板
        with st.expander("⚙️ 高级选项", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                target_audience = st.selectbox(
                    "目标观众",
                    ["普通观众", "电影爱好者", "专业影评人", "学生群体", "家庭观众"],
                    help="选择影评的专业程度"
                )
                
                review_style = st.selectbox(
                    "影评风格",
                    ["专业学术", "轻松休闲", "学术分析", "娱乐导向", "简洁明了"],
                    help="选择影评的表达方式"
                )
            
            with col2:
                max_length = st.slider(
                    "字数限制",
                    500, 2000, 1000, 100,
                    help="控制影评的长度"
                )
                include_spoilers = st.checkbox("包含剧透", value=False)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 处理搜索
        if search_clicked and movie_title:
            # 显示实时生成区域
            st.markdown("---")
            st.markdown("### 🤖 AI正在为您生成影评...")
            
            # 创建状态显示区域
            status_container = st.container()
            with status_container:
                col1, col2 = st.columns([3, 1])
                with col1:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    step_text = st.empty()
                with col2:
                    time_elapsed = st.empty()
                
                # 保存UI元素到session state
                st.session_state.progress_bar = progress_bar
                st.session_state.status_text = status_text
                st.session_state.step_text = step_text
                st.session_state.time_elapsed = time_elapsed
            
            # 风格映射
            style_mapping = {
                "专业学术": "professional",
                "轻松休闲": "casual", 
                "学术分析": "academic",
                "娱乐导向": "entertaining",
                "简洁明了": "brief"
            }
            
            # 开始计时
            start_time = time.time()
            
            # 生成影评（实时显示进度）
            review_data = generate_review(
                movie_title,
                None,  # 年份由TMDB自动确定
                target_audience=target_audience,
                review_style=style_mapping.get(review_style, "professional"),
                max_length=max_length,
                include_spoilers=include_spoilers
            )
            
            # 清理状态显示
            status_container.empty()
            
            if review_data:
                # 计算总用时
                total_time = time.time() - start_time
                
                # 显示完成信息
                st.success(f"🎉 影评生成完成！用时 {total_time:.1f} 秒")
                
                # 保存到历史记录
                st.session_state.current_review = review_data
                st.session_state.review_history.insert(0, {
                    **review_data,
                    "search_params": {
                        "title": movie_title,
                        "year": None,
                        "target_audience": target_audience
                    }
                })
                
                # 显示庆祝效果
                st.balloons()
            else:
                st.error("❌ 生成失败，请重试")
        
        # 显示当前影评
        if st.session_state.get('current_review'):
            display_review(st.session_state.current_review)
            
            # 操作按钮
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📋 复制影评", use_container_width=True):
                    st.code(st.session_state.current_review['review'], language=None)
            
            with col2:
                if st.button("💾 保存到文件", use_container_width=True):
                    # 保存功能
                    filename = f"{st.session_state.current_review['title']}_review.txt"
                    try:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(f"电影: {st.session_state.current_review['title']}\n")
                            f.write(f"年份: {st.session_state.current_review.get('year', '未知')}\n")
                            f.write(f"生成时间: {st.session_state.current_review['generated_at']}\n")
                            f.write("=" * 50 + "\n\n")
                            f.write(st.session_state.current_review['review'])
                        st.success(f"已保存到 {filename}")
                    except Exception as e:
                        st.error(f"保存失败: {e}")
            
            with col3:
                if st.button("🔄 重新生成", use_container_width=True):
                    st.session_state.current_review = None
                    st.rerun()
    
    with tab2:
        st.header("📊 历史影评记录")
        
        if not st.session_state.review_history:
            st.info("暂无历史记录，开始生成第一篇影评吧！")
        else:
            for idx, review in enumerate(st.session_state.review_history):
                with st.expander(f"{idx+1}. 《{review['title']}》"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**电影**: {review['title']}")
                        if review['year']:
                            st.write(f"**年份**: {review['year']}")
                        st.write(f"**生成时间**: {review['generated_at'][:19]}")
                    
                    with col2:
                        if st.button("查看详情", key=f"detail_{idx}"):
                            st.session_state.current_review = review
                            st.rerun()
    
    with tab3:
        st.header("⚙️ 个性化设置")
        
        st.subheader("API配置")
        col1, col2 = st.columns(2)
        with col1:
            kimi_key = st.text_input("Kimi API Key", type="password", value=os.getenv("KIMI_API_KEY", ""))
        with col2:
            tmdb_key = st.text_input("TMDB API Key", type="password", value=os.getenv("TMDB_API_KEY", ""))
        
        if st.button("💾 保存配置", use_container_width=True):
            # 更新环境变量
            os.environ["KIMI_API_KEY"] = kimi_key
            os.environ["TMDB_API_KEY"] = tmdb_key
            st.success("配置已保存（重启后生效）")
        
        st.subheader("界面偏好")
        col1, col2 = st.columns(2)
        with col1:
            theme = st.selectbox("界面主题", ["现代简约", "商务专业", "清新自然"])
        with col2:
            language = st.selectbox("界面语言", ["中文简体", "中文繁体", "English"])
    
    with tab4:
        st.header("ℹ️ 关于系统")
        
        st.markdown("""
        ### 🎬 智能影评系统 v2.0
        
        **核心功能：**
        - 🤖 AI智能分析电影内容
        - ✍️ 生成专业级影评
        - 🎯 个性化推荐
        
        **技术特点：**
        - **AI引擎**: 基于Kimi大模型
        - **数据支持**: TMDB电影数据库
        - **界面框架**: Streamlit现代界面
        - **响应速度**: 30-45秒/篇影评
        
        **使用指南：**
        1. 在首页输入电影名称
        2. 可选：设置年份和偏好
        3. 点击搜索，等待AI生成
        4. 查看、保存或分享影评
        
        **注意事项：**
        - 首次加载可能需要额外时间
        - 网络状况会影响响应速度
        - 建议一次只生成一篇影评
        """)
        
        st.info("💡 **提示**: 系统会记住您的偏好设置，下次使用更加便捷")
    
    
  
if __name__ == "__main__":
    main()