"""
轻量级语义搜索模块
使用简单的文本相似度算法，无需下载 AI 模型
"""
import re
from difflib import SequenceMatcher
import jieba  # 中文分词，轻量级


class SimpleSemanticSearch:
    """简单的语义搜索引擎"""
    
    def __init__(self):
        # 预定义的同义词词典
        self.synonyms = {
            # 编程相关
            '编程': ['程序设计', '代码', '开发', 'programming', 'coding'],
            '算法': ['数据结构', 'algorithm', '计算方法'],
            '人工智能': ['AI', '机器学习', '深度学习', '神经网络', 'ML', 'DL'],
            '网页': ['web', '前端', '后端', 'html', 'css', 'javascript'],
            
            # 学科相关
            '数学': ['mathematics', '微积分', '线性代数', '概率论'],
            '物理': ['physics', '力学', '电磁学'],
            '化学': ['chemistry', '有机化学', '无机化学'],
            
            # 语言相关
            'python': ['py', 'python3', 'python编程'],
            'java': ['java编程', 'javase', 'javaee'],
            'c++': ['cpp', 'c plus plus', 'cplus'],
            
            # 学习相关
            '入门': ['基础', '初学', '从零开始', '新手', '教程'],
            '高级': ['进阶', '深入', '精通', '高手'],
            '实战': ['实践', '项目', '案例', '练习'],
        }
    
    def expand_query(self, query):
        """
        扩展查询词，添加同义词
        
        Args:
            query: 原始查询
            
        Returns:
            list: 扩展后的查询词列表
        """
        query_lower = query.lower()
        expanded_terms = [query, query_lower]
        
        # 添加同义词
        for key, synonyms in self.synonyms.items():
            if key in query_lower:
                expanded_terms.extend(synonyms)
            for synonym in synonyms:
                if synonym in query_lower:
                    expanded_terms.append(key)
                    expanded_terms.extend(synonyms)
        
        return list(set(expanded_terms))  # 去重
    
    def calculate_similarity(self, text1, text2):
        """
        计算两个文本的相似度
        
        Args:
            text1, text2: 要比较的文本
            
        Returns:
            float: 相似度分数 (0-1)
        """
        # 方法1：直接字符串相似度
        similarity1 = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
        # 方法2：分词后的重叠度
        try:
            words1 = set(jieba.lcut(text1.lower()))
            words2 = set(jieba.lcut(text2.lower()))
            
            if len(words1) == 0 or len(words2) == 0:
                similarity2 = 0
            else:
                intersection = len(words1.intersection(words2))
                union = len(words1.union(words2))
                similarity2 = intersection / union if union > 0 else 0
        except:
            # 如果 jieba 有问题，就用简单分词
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            similarity2 = intersection / union if union > 0 else 0
        
        # 综合两种相似度
        return max(similarity1, similarity2)
    
    def search(self, query, products, top_k=10):
        """
        执行语义搜索
        
        Args:
            query: 查询文本
            products: 商品列表
            top_k: 返回数量
            
        Returns:
            list: [(product_id, score), ...] 按分数排序
        """
        if not products:
            return []
        
        # 扩展查询词
        expanded_queries = self.expand_query(query)
        
        results = []
        
        for product in products:
            # 组合商品信息
            product_text = f"{product.name} {product.description}"
            
            max_score = 0
            
            # 对每个扩展查询词计算相似度
            for expanded_query in expanded_queries:
                score = self.calculate_similarity(expanded_query, product_text)
                max_score = max(max_score, score)
            
            # 如果包含关键词，额外加分
            for expanded_query in expanded_queries:
                if expanded_query.lower() in product_text.lower():
                    max_score += 0.2
            
            if max_score > 0.1:  # 只返回相关度较高的结果
                results.append((product.id, min(max_score, 1.0)))
        
        # 按分数排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]


# 全局实例
_simple_search = SimpleSemanticSearch()

def get_simple_search():
    """获取简单语义搜索实例"""
    return _simple_search