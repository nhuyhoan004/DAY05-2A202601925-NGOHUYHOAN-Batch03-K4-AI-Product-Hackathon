from typing import List
import openai
from src import config
from src.prompts import SYSTEM_PROMPT, RAG_PROMPT_TEMPLATE

# Khởi tạo client OpenAI cho phần Text Generation
client = openai.OpenAI(
    api_key=config.OPENAI_API_KEY,
    base_url=config.OPENAI_BASE_URL if config.OPENAI_BASE_URL else None
)

# Client riêng cho OpenRouter Embeddings API. Không tải model vào RAM.
embedding_client = openai.OpenAI(
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.EMBEDDING_BASE_URL,
)


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Tạo embeddings cho một batch văn bản qua OpenRouter."""
    if not config.OPENROUTER_API_KEY:
        raise RuntimeError(
            "Chưa thiết lập OPENROUTER_API_KEY (hoặc OPENAI_API_KEY tương thích)."
        )

    cleaned_texts = [text.replace("\n", " ") for text in texts]
    if not cleaned_texts:
        return []

    response = embedding_client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=cleaned_texts,
        dimensions=config.EMBEDDING_DIMENSIONS,
        encoding_format="float",
    )
    ordered = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in ordered]

def generate_embedding(text: str) -> List[float]:
    """
    Tạo một vector nhúng cho văn bản qua OpenRouter Embeddings API.
    """
    return generate_embeddings([text])[0]

def generate_answer(question: str, context_chunks: List[str], conversation_history: List[dict] = None) -> str:
    """
    Sinh câu trả lời cho một câu hỏi CHỈ DỰA TRÊN ngữ cảnh (context chunks) được cung cấp.
    Có thể kèm lịch sử hội thoại để duy trì ngữ cảnh cuộc trò chuyện.
    """
    if conversation_history is None:
        conversation_history = []
        
    # Nếu không có ngữ cảnh nào, trả về câu trả lời mặc định
    if not context_chunks:
        return "[KHONG_BIET]"
        
    context_text = "\n\n---\n\n".join(context_chunks)
    user_prompt = RAG_PROMPT_TEMPLATE.format(context=context_text, question=question)
    
    import datetime
    current_time_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    dynamic_system_prompt = f"Thông tin hệ thống: Thời gian hiện tại là {current_time_str}.\n\n{SYSTEM_PROMPT}"
    
    # Xây dựng danh sách messages: System Prompt → Lịch sử hội thoại → Câu hỏi hiện tại
    messages = [{"role": "system", "content": dynamic_system_prompt}]
    
    # Thêm lịch sử hội thoại (nếu có)
    for msg in conversation_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Thêm câu hỏi hiện tại (kèm ngữ cảnh RAG)
    messages.append({"role": "user", "content": user_prompt})
    
    # Debug: Thống kê kích thước prompt
    total_chars = sum(len(m["content"]) for m in messages)
    estimated_tokens = total_chars // 4  # Ước tính: 1 token ≈ 4 ký tự
    print(f"[DEBUG] 📊 Thống kê prompt:")
    print(f"  - System Prompt: {len(SYSTEM_PROMPT)} ký tự")
    print(f"  - Lịch sử hội thoại: {len(conversation_history)} tin nhắn")
    print(f"  - Context chunks: {len(context_chunks)} đoạn")
    print(f"  - Tổng: {total_chars} ký tự (~{estimated_tokens} tokens ước tính)")
    
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=messages,
        temperature=0.5, # Giữ temperature ở mức 0 để tránh việc AI tự bịa thông tin
        max_tokens=1024   # Giới hạn output để tiết kiệm credits
    )
    
    # Debug: Thống kê token thực tế từ API
    usage = response.usage
    if usage:
        print(f"[DEBUG] 💰 Token thực tế: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}")
    
    return response.choices[0].message.content
