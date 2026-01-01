import streamlit as st
import time
from main import CafeAgent

# 1. 頁面配置：專業、簡潔
st.set_page_config(
    page_title="CAFÉ Finder: 跑咖找找",
    page_icon="☕",
    layout="wide"
)

# 2. 初始化後端代理人與對話紀錄
if "agent" not in st.session_state:
    st.session_state.agent = CafeAgent()
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 側邊欄：產品資訊與技術狀態
with st.sidebar:
    st.title("系統資訊 🛠️")
    st.markdown("""
    本助手採用 **RAG (檢索增強生成)** 技術，整合了：
    - **Google Places API**: 店家與評論數據
    - **Web Search**: 網路食記與部落格佐證 
    - **Ollama LLM**: GPT-OSS 120B 推理核心
    """)
    st.divider()
    # 放置狀態機圖表，符合專案必備要求
    # st.image("diagrams/state_machine.png", caption="系統運作邏輯 (State Machine)")

# 4. 主介面標題
st.title("☕ CAFÉ Finder: 跑咖找找")
# st.subheader("基於 AI 推理的深度咖啡廳分析系統")
st.subheader("一個幫助你找到理想咖啡廳的小工具")

# 5. 顯示歷史對話紀錄
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. 使用者互動區
if prompt := st.chat_input("輸入您的需求（例如：台南成大附近有插座、適合讀書的深夜咖啡廳）"):
    # 紀錄使用者問題
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 執行 Agent 邏輯並動態顯示進度
    with st.chat_message("assistant"):
        with st.status("Agent 正在處理請求...", expanded=True) as status:
            # # 第一步：意圖分析
            # st.write("🔍 分析使用者意圖中...")
            # # 這裡的邏輯會由 agent.run 內部執行，我們僅在 UI 呈現進度感
            
            # # 第二步：工具檢索
            # st.write("📍 檢索地圖與評論數據...")
            
            # # 第三步：網路佐證
            # st.write("🌐 搜尋外部部落格與網誌...")
            
            # 取得最終推薦報告 
            try:
                response = st.session_state.agent.run(prompt)
                status.update(label="分析完成！", state="complete", expanded=False)
            except Exception as e:
                response = f"⚠️ 系統發生異常：{str(e)}"
                status.update(label="處理失敗", state="error")

        # 呈現最終 Markdown 報告 
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# 頁尾說明
st.divider()
st.caption("CAFÉ Finder Project 2025 | Powered by Ollama & Google Cloud Platform")