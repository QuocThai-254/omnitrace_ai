from datetime import datetime
from services.identity import suggest_usernames

def get_initial_greeting(model_id: str, api_key: str):
    if api_key == "test":
        return "Xin chào, đây là key test"
    
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M")
    return f"Xin chào, bây giờ là {current_time}, tôi có thể giúp gì cho bạn?"

def process_chat_message(message: str, api_key: str):
    # Logic for test key auto-trigger
    if api_key == "test":
        if "sơn tùng" in message.lower() or "son tung" in message.lower():
            results = suggest_usernames("sơn tùng", api_key)
            return f"Tôi đã tìm thấy thông tin cho Sơn Tùng: {results['data']}"
    
    # Placeholder for actual LLM interaction
    return f"Bạn đã nói: {message}"
