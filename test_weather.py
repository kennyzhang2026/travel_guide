"""
和风天气 API 诊断脚本
用于测试 API Key 是否有效
"""

import requests
import json

def test_weather_api(api_key: str):
    """测试和风天气 API"""

    print("=" * 50)
    print("和风天气 API 诊断")
    print("=" * 50)
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    print()

    # 测试端点列表
    tests = [
        {
            "name": "城市查找 (免费版)",
            "url": "https://devapi.qweather.com/v2/city/lookup",
            "params": {"location": "101010100", "key": api_key}  # 北京的 ID
        },
        {
            "name": "城市查找 (付费版)",
            "url": "https://geoapi.qweather.com/v2/city/lookup",
            "params": {"location": "101010100", "key": api_key}
        },
        {
            "name": "天气预报 (免费版)",
            "url": "https://devapi.qweather.com/v7/weather/7d",
            "params": {"location": "101010100", "key": api_key}
        }
    ]

    for test in tests:
        print(f"测试: {test['name']}")
        print(f"URL: {test['url']}")

        try:
            response = requests.get(test['url'], params=test['params'], timeout=10)

            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                code = data.get('code')
                if code == '200' or code == 200:
                    print("✅ 成功!")
                    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")
                else:
                    print(f"❌ API 返回错误: code={code}")
                    print(f"消息: {data.get('msg', 'Unknown')}")
            elif response.status_code == 401:
                print("❌ 认证失败 - API Key 可能无效或过期")
            elif response.status_code == 403:
                print("❌ 权限不足 - 请检查 API 权限配置")
            elif response.status_code == 404:
                print("❌ 端点不存在 - 请检查 API 版本")
            else:
                print(f"❌ HTTP 错误: {response.status_code}")
                print(f"响应: {response.text[:200]}")

        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 错误: {e}")

        print()

    print("=" * 50)
    print("诊断建议:")
    print("=" * 50)
    print("1. 检查 API Key 是否正确复制")
    print("2. 登录 https://console.qweather.com/ 查看 Key 状态")
    print("3. 确认 Key 类型（免费版/付费版）")
    print("4. 检查每日请求额度是否用完")
    print("5. 确认项目域名白名单设置（如有）")
    print()

if __name__ == "__main__":
    # 从配置文件读取 API Key
    api_key = "40192d26d4d1428ea55fc2af4aaf62a1"

    test_weather_api(api_key)
