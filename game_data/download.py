import requests

# 1. 构造与curl完全对应的请求头（清理掉curl中的转义符）
headers = {
    "sec-ch-ua-platform": "Windows",
    "Referer": "https://albionfreemarket.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0",
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua": "Not(A:Brand);v=\"8\", Chromium;v=\"144\", Microsoft Edge;v=\"144\"",
    "sec-ch-ua-mobile": "?0"
}

# 2. 目标URL（与curl中的地址一致）
url = "https://cdn.albionfreemarket.com/AlbionLocalization/processed_spells.json"

try:
    # 3. 发送GET请求（完全模拟curl的GET请求）
    response = requests.get(
        url=url,
        headers=headers,
        # 若遇到SSL证书验证问题，可取消下面注释
        # verify=False
    )
    
    # 4. 检查请求是否成功（状态码200表示成功）
    response.raise_for_status()
    
    # 5. 将返回的数据保存到本地文件
    with open("processed_spells.json", "w", encoding="utf-8") as f:
        f.write(response.text)  # 保存原始响应文本，和curl返回的内容一致
    
    print(f"请求成功！数据已保存到本地文件：merged_localization.json")
    print(f"响应状态码：{response.status_code}")
    print(f"返回数据大小：{len(response.text)} 字符")

except requests.exceptions.RequestException as e:
    # 捕获所有请求异常（网络错误、404/500等）
    print(f"请求失败：{str(e)}")