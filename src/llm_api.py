import requests
import json
# 從主目錄匯入設定檔，取得 API Key 與 URL
import config 

class LLMAgent:
    """
    處理所有與 Ollama API 溝通的類別。
    負責封裝 HTTP 請求，並處理認證與錯誤處理。 [cite: 73, 81]
    """

    def __init__(self):
        # 根據作業規範，認證格式必須為 Bearer <your-api-key> 
        self.headers = {
            "Authorization": f"Bearer {config.OLLAMA_API_KEY}",
            "Content-Type": "application/json"
        }
        self.url = config.OLLAMA_API_URL

    def chat(self, user_prompt, system_prompt="你是一個專業的咖啡廳探店小助手。"):
        """
        傳送訊息給 Ollama 原生 API (generate 端點) 並取得回應。
        """
        
        # 準備符合 Ollama /api/generate 規範的資料
        payload = {
            "model": "gpt-oss:120b", # 請確保這是助教提供的模型名稱 [cite: 44]
            "prompt": f"System: {system_prompt}\nUser: {user_prompt}", # generate 端點通常合併寫在 prompt
            "stream": False,  # 必須設定為 False，API 才會一次回傳完整結果
            "options": {
                "temperature": 0.7,
                "num_predict": 4096,  # 增加回應長度上限
                "top_p": 0.9
            }
        }

        try:
            # 發送 POST 請求，記得 Bearer Token 認證 
            response = requests.post(
                self.url, 
                headers=self.headers, 
                data=json.dumps(payload),
                timeout=60  # 設定較長的逾時時間以應對大型模型
            )

            if response.status_code == 200:
                result = response.json()
                # --- 關鍵修正處：從 'choices' 改為 'response' ---
                if 'response' in result:
                    return result['response']
                else:
                    return f"找不到 'response' 欄位，API 回傳內容為：{result}"
            else:
                return f"API 錯誤：狀態碼 {response.status_code}, 訊息：{response.text}"

        except Exception as e:
            return f"連線發生異常：{str(e)}"

# --- 測試區塊 ---
# 這個區塊只有在直接執行此檔案時才會跑，方便你確認 API 是否運作正常
if __name__ == "__main__":
    print("正在測試 LLM API 連線狀態...")
    agent = LLMAgent()
    
    test_query = "你好，請用一句話介紹你自己，並確認你收到了這則訊息。"
    response = agent.chat(test_query)
    
    print("-" * 30)
    print(f"測試請求：{test_query}")
    print(f"模型回應：{response}")
    print("-" * 30)