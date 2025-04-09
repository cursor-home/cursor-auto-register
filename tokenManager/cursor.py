import requests


class Cursor:
    """
    Cursor类 - 用于管理和查询Cursor应用的API接口
    提供对Cursor账户信息、使用额度和订阅状态的访问
    """
    
    # Cursor支持的AI模型列表
    models = [
        "claude-3-5-sonnet-20241022",  # Claude 3.5 Sonnet (特定版本)
        "claude-3-opus",               # Claude 3 Opus模型
        "claude-3.5-haiku",            # Claude 3.5 Haiku模型 
        "claude-3.5-sonnet",           # Claude 3.5 Sonnet模型
        "cursor-fast",                 # Cursor快速模型
        "cursor-small",                # Cursor小型模型
        "deepseek-r1",                 # DeepSeek R1模型
        "deepseek-v3",                 # DeepSeek V3模型
        "gemini-2.0-flash-exp",        # Gemini 2.0 Flash实验版
        "gemini-2.0-flash-thinking-exp", # Gemini 2.0思考版实验版
        "gemini-exp-1206",             # Gemini实验版(1206)
        "gpt-3.5-turbo",               # GPT-3.5 Turbo模型
        "gpt-4",                       # GPT-4模型
        "gpt-4-turbo-2024-04-09",      # GPT-4 Turbo(特定日期版本)
        "gpt-4o",                      # GPT-4o模型
        "gpt-4o-mini",                 # GPT-4o Mini模型
        "o1",                          # Anthropic O1模型
        "o1-mini",                     # Anthropic O1 Mini模型
        "o1-preview",                  # Anthropic O1预览版
        "o3-mini",                     # Anthropic O3 Mini模型
    ]

    @classmethod
    def get_remaining_balance(cls, user, token):
        """
        获取用户剩余的API使用额度
        
        参数:
            user: 用户ID或用户名
            token: 用户认证令牌
            
        返回:
            剩余的API请求次数，如果无法获取则返回None
        """
        # 构建API请求URL，包含用户参数
        url = f"https://www.cursor.com/api/usage?user={user}"

        # 设置请求头，包含内容类型和认证Cookie
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"WorkosCursorSessionToken={user}%3A%3A{token}",
        }
        
        # 发送GET请求获取使用情况
        response = requests.get(url, headers=headers)
        
        # 从响应中提取GPT-4的使用情况
        usage = response.json().get("gpt-4", None)
        
        # 检查是否成功获取到使用数据
        if (
            usage is None
            or "maxRequestUsage" not in usage
            or "numRequests" not in usage
        ):
            return None
            
        # 计算并返回剩余的使用次数(最大请求数减去已使用请求数)
        return usage["maxRequestUsage"] - usage["numRequests"]

    @classmethod
    def get_trial_remaining_days(cls, user, token):
        """
        获取用户试用期剩余天数
        
        参数:
            user: 用户ID或用户名
            token: 用户认证令牌
            
        返回:
            试用期剩余天数，如果无法获取则返回None
        """
        # Stripe支付系统API的URL
        url = "https://www.cursor.com/api/auth/stripe"

        # 设置请求头，包含内容类型和认证Cookie
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"WorkosCursorSessionToken={user}%3A%3A{token}",
        }
        
        # 发送GET请求获取订阅信息
        response = requests.get(url, headers=headers)
        
        # 从响应中提取试用期剩余天数
        remaining_days = response.json().get("daysRemainingOnTrial", None)
        return remaining_days
