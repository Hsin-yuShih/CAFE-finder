import googlemaps
import config

class GoogleMapsTool:
    """
    處理所有與 Google Maps API 相關的動作。
    包含搜尋店家以及獲取店家的詳細評論資訊。
    """

    def __init__(self):
        # 初始化 Google Maps 客戶端，使用 config.py 中的金鑰
        try:
            self.gmaps = googlemaps.Client(key=config.GOOGLE_MAPS_API_KEY)
        except Exception as e:
            print(f"Google Maps 初始化失敗：{e}")

    def search_cafes(self, query, location=None):
        """
        第一階段：根據關鍵字搜尋店家。
        :param query: 搜尋關鍵字 (例如: "成大附近 有插座 咖啡廳")
        :return: 店家簡要資訊列表
        """
        # 使用 Text Search 搜尋店家
        # 如果有提供座標(location)，會以該處為中心搜尋
        places_result = self.gmaps.places(
            query=query, 
            location=location, 
            language='zh-TW',
            type='cafe' # 限制只搜尋咖啡廳類別
            )
        
        cafes = []
        # 只取前 3~5 筆，避免後續 LLM 處理資訊量過大
        for place in places_result.get('results', [])[:5]:
            cafes.append({
                'name': place.get('name'),
                'place_id': place.get('place_id'),
                'rating': place.get('rating'),
                'address': place.get('formatted_address')
            })
        return cafes

    def get_cafe_details(self, place_id):
        """
        第二階段：獲取特定店家的詳細資訊與評論。
        這是為了讓 LLM 能判斷評論中是否提到「巴斯克」或「插座」等細節。
        """
        # 請求欄位包含：評論、營業時間、地圖網址
        fields = ['name', 'review', 'opening_hours', 'url']
        details = self.gmaps.place(place_id=place_id, fields=fields, language='zh-TW')
        
        result = details.get('result', {})
        reviews = result.get('reviews', [])
        
        # 整理評論文字，只取前 5 則最有用的評論
        review_texts = [r.get('text', '') for r in reviews[:5]]
        
        return {
            'name': result.get('name'),
            'opening_hours': result.get('opening_hours', {}).get('weekday_text', '未提供'),
            'url': result.get('url'),
            'reviews': review_texts
        }

# --- 測試區塊 ---
# 方便你確認 Google Maps API 是否能正確抓到成大附近的資料
if __name__ == "__main__":
    print("正在測試 Google Maps Tool...")
    tool = GoogleMapsTool()
    
    # 測試搜尋
    test_query = "成功大學 附近 適合讀書 咖啡廳"
    print(f"執行搜尋：{test_query}")
    results = tool.search_cafes(test_query)
    
    for cafe in results:
        print(f"\n找到店家：{cafe['name']} (ID: {cafe['place_id']})")
        # 測試抓取評論
        print(f"正在抓取 {cafe['name']} 的詳細資訊...")
        detail = tool.get_cafe_details(cafe['place_id'])
        print(f"評論數量：{len(detail['reviews'])}")
        if detail['reviews']:
            print(f"首條評論摘要：{detail['reviews'][0][:50]}...")