import os
import hashlib
import json
from src import utils, llm, config
from src.vector_db import VectorDB

def run_ingestion():
    print("Bắt đầu quá trình nạp dữ liệu (ingestion)...")
    
    docs_path = "data/discord/documents.json"
    documents = utils.load_documents(docs_path)
        
    if not documents:
        print("Không có tài liệu nào. Vui lòng chạy file collector.py trước.")
        return

    # Check Hash để xem file có bị thay đổi không
    hash_path = "data/discord/documents.json.md5"
    try:
        with open(docs_path, 'rb') as f:
            source_bytes = f.read()
        index_signature = (
            f"{config.EMBEDDING_MODEL}:{config.EMBEDDING_DIMENSIONS}:"
        ).encode("utf-8")
        file_hash = hashlib.md5(index_signature + source_bytes).hexdigest()
            
        if os.path.exists(hash_path) and os.path.exists("data/discord/faiss.index"):
            with open(hash_path, 'r') as f:
                if f.read().strip() == file_hash:
                    print("Dữ liệu không có sự thay đổi, bỏ qua quá trình Embedding để tiết kiệm thời gian.")
                    return
    except Exception as e:
        print(f"Lỗi khi kiểm tra MD5: {e}")

    print(f"Đã tải {len(documents)} tin nhắn.")
    
    all_chunks = []
    metadata_list = []
    
    for doc in documents:
        chunks = utils.chunk_text(doc.get("text", ""))
        for chunk in chunks:
            if chunk.strip():
                all_chunks.append(chunk)
                metadata_list.append({
                    "text": chunk,
                    "channel": doc.get("channel", ""),
                    "thread": doc.get("thread", ""),
                    "url": doc.get("url", ""),
                    "author": doc.get("author", ""),
                    "message_id": doc.get("message_id", ""),
                    "created_at": doc.get("created_at", "")
                })
                
    print(f"Đã tạo ra {len(all_chunks)} đoạn văn bản (chunks). Bắt đầu tạo embeddings...")
    
    cache_path = "data/discord/embeddings_cache.json"
    embedding_cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                embedding_cache = json.load(f)
        except Exception as e:
            print(f"Không thể tải cache cũ: {e}")

    embeddings = [None] * len(all_chunks)
    missing = []
    for i, chunk in enumerate(all_chunks):
        cache_key = hashlib.md5(
            (
                f"{config.EMBEDDING_MODEL}:{config.EMBEDDING_DIMENSIONS}:" + chunk
            ).encode("utf-8")
        ).hexdigest()
        cached = embedding_cache.get(cache_key)
        if cached and len(cached) == config.EMBEDDING_DIMENSIONS:
            embeddings[i] = cached
        else:
            missing.append((i, chunk, cache_key))

    batch_size = max(1, config.EMBEDDING_BATCH_SIZE)
    try:
        for start in range(0, len(missing), batch_size):
            batch = missing[start:start + batch_size]
            batch_vectors = llm.generate_embeddings([item[1] for item in batch])
            if len(batch_vectors) != len(batch):
                raise RuntimeError("OpenRouter trả về sai số lượng embedding.")
            for (index, _chunk, cache_key), vector in zip(batch, batch_vectors):
                if len(vector) != config.EMBEDDING_DIMENSIONS:
                    raise RuntimeError(
                        f"Embedding có {len(vector)} chiều, kỳ vọng "
                        f"{config.EMBEDDING_DIMENSIONS}."
                    )
                embeddings[index] = vector
                embedding_cache[cache_key] = vector
            print(
                f"Đã tạo embedding API {min(start + len(batch), len(missing))}/"
                f"{len(missing)} chunks mới..."
            )
    except Exception as e:
        print(f"Lỗi khi gọi OpenRouter Embeddings API: {e}")
        raise

    new_chunks_count = len(missing)
            
    if new_chunks_count > 0:
        print(f"Đã tạo embedding mới cho {new_chunks_count} chunks. Lưu lại cache...")
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(embedding_cache, f, ensure_ascii=False)
        except Exception as e:
            print(f"Không thể lưu cache: {e}")
    else:
        print("Tất cả chunks đều đã được cache từ trước, không cần gọi model.")
            
    if not embeddings:
        print("Không có embedding nào được tạo thành công.")
        return
        
    print("Đang xây dựng cơ sở dữ liệu FAISS...")
    
    dimension = len(embeddings[0])
    db = VectorDB()
    db.create_index(dimension)
    db.add_embeddings(embeddings, metadata_list)
    
    db.save_index()
    
    # Lưu lại mã Hash mới nhất
    try:
        with open(hash_path, 'w') as f:
            f.write(file_hash)
    except:
        pass
        
    print("Index đã được lưu trữ thành công vào thư mục data/discord/")

if __name__ == "__main__":
    run_ingestion()
