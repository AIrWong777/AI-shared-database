"""
测试文本提取和分块功能
"""

import os
import unittest
from app.utils.text_extractor import extract_metadata_from_file
from app.utils.text_processor import process_literature_text
import shutil  # 用于递归删除目录

class TestTextProcessing(unittest.TestCase):
    def setUp(self):
        # 创建测试文件目录
        self.test_dir = "test/test_files"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        
        # 创建一个测试文本文件
        self.test_content = """测试文献标题
作者：张三

摘要：
这是一个测试文档，用于验证文本提取和分块功能。
本文包含多个段落，以测试文本分块的效果。

第一章 引言
这是引言部分的内容。我们需要确保文本能够被正确提取和分块。
这个测试文件包含了标题、作者、摘要等基本元素。

第二章 方法
在这一章中，我们将详细说明测试方法。
1. 首先创建测试文件
2. 然后提取文本内容
3. 最后进行分块处理

第三章 结论
通过这个测试，我们可以验证：
- 文本提取功能是否正常
- 分块是否合理
- 元数据是否正确"""
        
        # 将测试内容写入文件
        self.test_file_path = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file_path, "w", encoding="utf-8") as f:
            f.write(self.test_content)
    
    def test_text_processing(self):
        """测试文本分块功能"""
        # 直接使用测试内容进行分块处理
        chunks = process_literature_text(
            text=self.test_content,
            literature_id="test_id",
            group_id="test_group",
            chunk_size=200,  # 使用较小的块大小以便测试
            chunk_overlap=50
        )
        
        # 验证分块结果
        self.assertIsNotNone(chunks)
        self.assertTrue(len(chunks) > 0)
        
        # 打印分块信息（用于调试）
        print(f"\n总共生成了 {len(chunks)} 个文本块:")
        for i, chunk in enumerate(chunks):
            print(f"\n块 {i + 1}:")
            print(f"文本长度: {chunk['char_length']} 字符")
            print(f"预估Token数: {chunk['estimated_tokens']}")
            print(f"文本内容: {chunk['text'][:100]}...")  # 只打印前100个字符
        
        # 验证每个块的属性
        for chunk in chunks:
            self.assertIn("chunk_index", chunk)
            self.assertIn("text", chunk)
            self.assertIn("char_length", chunk)
            self.assertIn("estimated_tokens", chunk)
            self.assertEqual(chunk["literature_id"], "test_id")
            self.assertEqual(chunk["group_id"], "test_group")
            self.assertEqual(chunk["chunk_type"], "literature_text")
            self.assertEqual(chunk["embedding_status"], "pending")
            
            # 验证块的大小
            self.assertLess(chunk["char_length"], 300)  # 考虑到重叠，单个块不应该超过 chunk_size + chunk_overlap
    
    def tearDown(self):
        # 清理测试目录及其所有内容
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

if __name__ == "__main__":
    unittest.main() 