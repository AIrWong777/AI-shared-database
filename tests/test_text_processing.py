import unittest
from app.utils.token_counter import TokenCounter
from app.utils.text_processor import (
    split_text_into_chunks,
    prepare_chunks_for_embedding,
    process_literature_text
)

class TestTextProcessing(unittest.TestCase):
    def setUp(self):
        # 测试用的示例文本，包含中英文混合
        self.test_text = """
        这是一个测试文本。它包含了中文和English混合的内容。
        这是第二段。It contains multiple paragraphs!
        
        这是第三段，用于测试分块。This is for testing text splitting.
        让我们确保它有足够的长度。Let's make sure it's long enough.
        """
        
    def test_token_counter(self):
        # 测试不同的token计数方法
        text = "这是一个测试。This is a test."
        
        # 测试字符计数方法
        chars_count = TokenCounter.estimate_tokens(text, method="chars")
        self.assertGreater(chars_count, 0)
        
        # 测试分词方法
        words_count = TokenCounter.estimate_tokens(text, method="words")
        self.assertGreater(words_count, 0)
        
        # 测试tiktoken方法
        tiktoken_count = TokenCounter.estimate_tokens(text, method="tiktoken")
        self.assertGreater(tiktoken_count, 0)
        
        # 测试自动方法
        auto_count = TokenCounter.estimate_tokens(text, method="auto")
        self.assertGreater(auto_count, 0)
        
    def test_text_splitting(self):
        # 测试文本分块
        chunks = split_text_into_chunks(
            self.test_text,
            chunk_size=100,
            chunk_overlap=20
        )
        
        # 验证基本属性
        self.assertIsInstance(chunks, list)
        self.assertTrue(len(chunks) > 0)
        
        # 验证每个块的结构
        for chunk in chunks:
            self.assertIn("chunk_index", chunk)
            self.assertIn("text", chunk)
            self.assertIn("char_length", chunk)
            self.assertIn("estimated_tokens", chunk)
            self.assertIn("start_char", chunk)
            
    def test_chunk_preparation(self):
        # 先分块
        chunks = split_text_into_chunks(self.test_text)
        
        # 测试元数据添加
        literature_id = "test_lit_001"
        group_id = "test_group_001"
        
        enriched_chunks = prepare_chunks_for_embedding(
            chunks,
            literature_id,
            group_id
        )
        
        # 验证元数据
        for chunk in enriched_chunks:
            self.assertEqual(chunk["literature_id"], literature_id)
            self.assertEqual(chunk["group_id"], group_id)
            self.assertEqual(chunk["chunk_type"], "literature_text")
            self.assertEqual(chunk["embedding_status"], "pending")
            
    def test_full_process(self):
        # 测试完整的处理流程
        result = process_literature_text(
            text=self.test_text,
            literature_id="test_lit_002",
            group_id="test_group_002",
            chunk_size=100,
            chunk_overlap=20
        )
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main() 