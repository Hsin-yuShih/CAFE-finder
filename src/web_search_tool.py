import ddgs
import json

class WebSearchTool:
    """
    處理所有與網路搜尋相關的動作。
    負責尋找部落格文章、食記或官方網站資訊，以提供搜尋結果的佐證。
    """

    def __init__(self):
        # 初始化 DuckDuckGo 搜尋客戶端
        self.ddgs = ddgs.DDGS()

    def search_blogs(self, cafe_name, keywords=None):
        """
        搜尋特定咖啡廳的相關部落格或評論網頁。
        :param cafe_name: 咖啡廳名稱
        :param keywords: 額外的關鍵字 (例如: "插座", "不限時", "巴斯克")
        :return: 包含網頁標題、連結與摘要的列表
        """
        
        # 組合搜尋語句，例如："A咖啡廳 推薦 部落格 插座"
        search_query = f"{cafe_name}"
        if keywords:
            search_query += f" {' '.join(keywords)}"
            
        print(f"DEBUG: 正在進行網路搜尋：{search_query}")
        
        # 執行搜尋，限制回傳 5 筆結果
        # region='tw-tzh' 確保搜尋結果以台灣繁體中文為主
        results = self.ddgs.text(search_query, region='tw-tzh', max_results=5)
        
        refined_results = []
        for r in results:
            refined_results.append({
                'title': r.get('title'),
                'href': r.get('href'),
                'body': r.get('body')  # 這包含了網頁的內容摘要
            })
            
        return refined_results

# --- 測試區塊 ---
# 方便你確認網路搜尋功能是否能正確抓到資訊
if __name__ == "__main__":
    print("正在測試 Web Search Tool...")
    search_tool = WebSearchTool()
    
    # 測試情境：搜尋成大附近的咖啡廳部落格
    test_cafe = "自己的房間"
    test_keywords = ["咖啡廳", "食記", "台南"]
    
    print(f"執行搜尋任務：{test_cafe}")
    blog_results = search_tool.search_blogs(test_cafe, test_keywords)
    
    if blog_results:
        print(f"\n找到 {len(blog_results)} 筆相關資料：")
        for i, blog in enumerate(blog_results, 1):
            print(f"{i}. 標題：{blog['title']}")
            print(f"   連結：{blog['href']}")
            print(f"   摘要：{blog['body'][:100]}...\n")
    else:
        print("未找到相關部落格資訊。")