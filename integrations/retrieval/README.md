# Retrieval Integration

当前检索集成模块，供 `WeClaw_console` 与运行时检索能力复用。

## 目录职责

- `engine.py`：统一入口，负责启动、停止、重建索引、对外检索。
- `source_sessions.py`：读取 agent runtime 下的 `history.jsonl` 会话文件并规范化消息记录。
- `chunking.py`：文本分片。
- `sqlite_store.py`：SQLite 持久化。
- `strategy_keyword.py`：关键词检索。
- `strategy_vector.py`：向量检索。
- `strategy_hybrid.py`：混合检索与按会话归并。
- `embeddings.py`：嵌入后端。
- `indexer.py`：增量索引构建。
- `watcher.py`：文件轮询与防抖重建。
- `types.py` / `utils.py`：共享类型与工具函数。

## 当前行为

1. 引擎启动后会先执行一次索引，再启动 watcher。
2. 文件变化后会延迟触发重建，避免频繁写入。
3. 检索时融合关键词与向量得分，按会话去重后返回结果。
4. 默认优先使用本地 embedding 模型；模型不可用时退化到 hash 向量加关键词检索。
