import requests
from datetime import datetime, timedelta
from typing import Annotated
import json


# url = "https://finnews.cubenlp.com/search_curr_news"
url = "http://172.23.148.35:8091/search_curr_news"
# url = "http://work.chatbot.cn:17091/search_curr_news"


class News_utils:
    
    def get_company_news(company: Annotated[str, "公司名称"], 
                         top_k: Annotated[str, "获取TopK条新闻"]=50,):
        """根据公司名称获取topk新闻"""
        # data = {
        #     "query": f"有什么{company}相关的新闻?",    
        #     "start_timestamp": start_time, #开始时间戳   
        #     "end_timestamp": end_time,   #结束时间戳    
        #     "top_k":top_k #最大32
        # }
        data = {"com_name": company, "lsort":"default", "top_k":int(top_k)}
        response = requests.post(url, json=data)

        return response


if __name__ == "__main__":
    # 查找n天内的新闻
    time_range = 30
    time_range_stamp = 86400 * time_range * 1000

    # 获取现在的时间戳
    end_time_stamp = datetime.now().timestamp() * 1000
    # 获取之前的时间戳
    start_time_stamp = end_time_stamp - time_range_stamp
    start_time_stamp = int(start_time_stamp)
    end_time_stamp = int(end_time_stamp)
    
    response = News_utils.get_company_news("津滨发展", 50)
    print(response.json())
    # if response.status_code == 200:
    #     print('Request was successful.')
    #     with open(f'./FinNews.json','w') as f:
    #         # title和snippet是Unicode需要转中文
    #         dic = response.json()
    #         # title是str类型
    #         # 为什么不管用
    #         for i in dic["data"]:
    #             i["title"].encode('utf-8').decode('unicode_escape')
    #             i["content"].encode('utf-8').decode('unicode_escape')
    #         #print(dic["data"][0]["title"])
    #         json.dump(dic,f, ensure_ascii=False)
    #         print(dic)
    #         # data:{[code,url,title,data,snippet], [code, url...]}
    # else:
    #     print(f'Request failed with status code {response.status_code}')


