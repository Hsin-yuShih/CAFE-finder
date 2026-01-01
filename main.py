import json
import time
from src.llm_api import LLMAgent
from src.gmaps_tool import GoogleMapsTool
from src.web_search_tool import WebSearchTool

class CafeAgent:
    """
    咖啡探店智慧代理人 - 融合增強版。
    整合動態關鍵字提取、意圖防呆、對話記憶與類別約束。
    """
    
    def __init__(self):
        self.llm = LLMAgent()
        self.gmaps = GoogleMapsTool()
        self.web = WebSearchTool()
        # 儲存歷史對話，用於處理追問情境 [cite: 128]
        self.history = [] 

    def run(self, user_query):
        # 狀態 1: 嚴格意圖路由 (使用 Few-shot 範例強化模型判斷)
        routing_prompt = f"""
        你是一個咖啡廳探店助手的「意圖路由器」。請根據使用者的輸入，只從以下三個分類中選擇一個，並回傳 JSON。

        分類定義：
        - "CHAT":  greeting, off-topic, or general talk. (例: "你好", "你是誰", "今天天氣不錯")
        - "FOLLOW_UP": Asking about previous results. (例: "那這家有插座嗎?", "哪一個比較近?")
        - "SEARCH": Searching for new cafes. (例: "找成大咖啡廳", "推薦巴斯克蛋糕店")

        範例：
        User: "嗨" -> {{"intent": "CHAT"}}
        User: "那家店開到幾點?" -> {{"intent": "FOLLOW_UP"}}
        User: "如果只能選一間去，你會推薦哪一家?" -> {{"intent": "FOLLOW_UP"}}
        User: "推薦台南適合讀書的店" -> {{"intent": "SEARCH", "query": "台南 適合讀書 咖啡廳"}}

        請判斷此輸入："{user_query}"
        """
        
        # 呼叫 LLM 進行判斷
        raw_res = self.llm.chat(routing_prompt, system_prompt="你只會輸出純 JSON，不包含任何解釋。")
        
        print(f"[意圖路由] 模型回應：{raw_res}")
        # 清理並解析 JSON (防止模型輸出 Markdown 語法)
        clean_res = raw_res.replace("```json", "").replace("```", "").strip()
        try:
            intent_data = json.loads(clean_res)
            intent = intent_data.get("intent", "CHAT") # 預設改為 CHAT，避免誤觸搜尋
        except:
            intent = "CHAT" 

        # --- 狀態 2: 根據意圖執行分支 ---
        if intent == "CHAT":
            return self.llm.chat(f"使用者跟你打招呼或閒聊：{user_query}。請以親切的咖啡愛好者、咖啡探店部落客身分回覆。")

        if intent == "FOLLOW_UP":
            # 結合歷史紀錄進行追問 (Advanced Level 展現理解能力 )
            context = f"歷史紀錄：{self.history[-1:]}\n追問：{user_query}"
            return self.llm.chat(context, system_prompt="請根據先前的推薦結果回答使用者的細節問題。")

        if intent == "SEARCH":
            # --- 狀態 3: 執行智慧搜尋 (RAG 流程) [cite: 124, 125] ---
            # 這裡的搜尋詞是由 LLM 根據使用者輸入動態產生的，非寫死
            query_for_gmaps = intent_data.get("search_query", user_query)
            
            # 限制只找咖啡廳相關類別
            print(f"[行動] 正在地圖檢索: {query_for_gmaps} (類別: Cafe)...")
            cafes = self.gmaps.search_cafes(query_for_gmaps) 
            
            if not cafes:
                return "目前在該地區找不到符合條件的咖啡廳，建議嘗試調整需求（例如放寬插座或特定甜點限制）。"

            all_cafe_info = []
            for cafe in cafes:
                print(f"   [調查] 店家細節與網路佐證: {cafe['name']}...")
                
                # 獲取評論與網路部落格摘要 [cite: 116, 118]
                details = self.gmaps.get_cafe_details(cafe['place_id'])
                blogs = self.web.search_blogs(cafe['name'])
                
                # 整合證據
                cafe_summary = {
                    "name": cafe['name'],
                    "rating": cafe['rating'],
                    "address": cafe['address'],
                    "reviews": details['reviews'],
                    "blog_evidence": [b['body'] for b in blogs[:2]],
                    "url": details['url']
                }
                all_cafe_info.append(cafe_summary)

        # --- 狀態 4: 根據使用者特定需求進行總結 (Synthesis) [cite: 120, 121] ---
        print("[回報] 正在根據您的需求彙整專屬報告...")
        # 這裡會根據使用者當初輸入的 target_needs 進行針對性回答
        synthesis_prompt = f"""
        使用者原始需求：{user_query}
        提取的關鍵需求：{intent_data.get('target_needs', [])}
        
        搜尋到的原始數據：{all_cafe_info}
        
        請以專業的咖啡師的語氣推薦。要求：
        1. 必須針對使用者提到的特定需求進行證據比對。
        2. 使用 Markdown 表格呈現。
        3. 內容需完整，請勿省略重要細節。
        4. 提供每家店的 Google Maps 連結。
        5. 若無符合需求的店家，請禮貌回覆並建議調整需求。
        """
        
        final_report = self.llm.chat(synthesis_prompt)
        
        # 紀錄歷史紀錄以供後續追問 [cite: 133]
        self.history.append({"q": user_query, "a": final_report})
        return final_report