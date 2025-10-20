"""
SPARQL语义搜索服务
基于知识库进行智能搜索和推理
"""

from knowledge_base import knowledge_base
import jieba
import re

class SPARQLSemanticSearch:
    """SPARQL语义搜索服务类"""
    
    def __init__(self):
        self.kb = knowledge_base
        self.g = knowledge_base.g
    
    def semantic_search(self, query_text, limit=20):
        """
        主要的语义搜索接口
        
        Args:
            query_text (str): 用户查询文本
            limit (int): 返回结果数量限制
            
        Returns:
            list: 搜索结果列表，每个结果包含书籍信息
        """
        results = []
        
        # 1. 直接关键词搜索
        keyword_results = self.keyword_search(query_text, limit//3)
        results.extend(keyword_results)
        
        # 2. 语义扩展搜索（同义词）
        if len(results) < limit:
            semantic_results = self.semantic_expansion_search(query_text, limit - len(results))
            results.extend(semantic_results)
        
        # 3. 分类推理搜索
        if len(results) < limit:
            category_results = self.category_inference_search(query_text, limit - len(results))
            results.extend(category_results)
        
        # 4. 相关性搜索
        if len(results) < limit:
            related_results = self.related_books_search(query_text, limit - len(results))
            results.extend(related_results)
        
        # 去重并排序
        unique_results = self.deduplicate_results(results)
        return unique_results[:limit]
    
    def keyword_search(self, query, limit=10):
        """
        基于关键词的SPARQL搜索
        在标题、描述、关键词中进行精确和模糊匹配
        """
        # 预处理查询
        query_words = self.preprocess_query(query)
        if not query_words:
            return []
        
        # 构建SPARQL过滤条件
        title_filters = []
        desc_filters = []
        keyword_filters = []
        
        for word in query_words:
            title_filters.append(f'CONTAINS(LCASE(str(?title)), "{word}")')
            desc_filters.append(f'CONTAINS(LCASE(str(?description)), "{word}")')
            keyword_filters.append(f'CONTAINS(LCASE(str(?keyword)), "{word}")')
        
        sparql_query = f"""
        PREFIX wb: <http://webook.com/ontology#>
        
        SELECT DISTINCT ?book ?title ?description ?price ?condition
        WHERE {{
            ?book a wb:Book ;
                  wb:hasTitle ?title ;
                  wb:hasPrice ?price .
            
            OPTIONAL {{ ?book wb:hasDescription ?description }}
            OPTIONAL {{ ?book wb:hasCondition ?condition }}
            OPTIONAL {{ ?book wb:hasKeyword ?keyword }}
            
            FILTER (
                {' || '.join(title_filters)} ||
                {' || '.join(desc_filters)} ||
                {' || '.join(keyword_filters)}
            )
        }}
        ORDER BY ?title
        LIMIT {limit}
        """
        
        return self.execute_sparql_query(sparql_query)
    
    def semantic_expansion_search(self, query, limit=10):
        """
        基于同义词的语义扩展搜索
        利用知识库中的同义词映射扩展查询范围
        """
        expanded_terms = self.expand_query_with_synonyms(query)
        if not expanded_terms:
            return []
        
        # 构建扩展搜索的SPARQL查询
        filters = []
        for term in expanded_terms:
            filters.extend([
                f'CONTAINS(LCASE(str(?title)), "{term}")',
                f'CONTAINS(LCASE(str(?description)), "{term}")',
                f'CONTAINS(LCASE(str(?keyword)), "{term}")'
            ])
        
        sparql_query = f"""
        PREFIX wb: <http://webook.com/ontology#>
        
        SELECT DISTINCT ?book ?title ?description ?price ?condition ?language ?difficulty
        WHERE {{
            ?book a wb:Book ;
                  wb:hasTitle ?title ;
                  wb:hasPrice ?price .
            
            OPTIONAL {{ ?book wb:hasDescription ?description }}
            OPTIONAL {{ ?book wb:hasCondition ?condition }}
            OPTIONAL {{ ?book wb:hasKeyword ?keyword }}
            OPTIONAL {{ ?book wb:hasLanguage ?language }}
            OPTIONAL {{ ?book wb:hasDifficulty ?difficulty }}
            
            FILTER ({' || '.join(filters[:50])})  # 限制过滤条件数量避免查询过大
        }}
        ORDER BY ?title
        LIMIT {limit}
        """
        
        return self.execute_sparql_query(sparql_query)
    
    def category_inference_search(self, query, limit=10):
        """
        基于分类推理的搜索
        从查询中推断用户意图的分类，然后搜索相关分类的书籍
        """
        inferred_categories = self.infer_categories_from_query(query)
        if not inferred_categories:
            return []
        
        # 构建分类搜索的SPARQL查询（支持层次推理）
        category_conditions = []
        for category in inferred_categories:
            category_uri = f'<http://webook.com/resource/category/{category}>'
            category_conditions.append(f'?category = {category_uri}')
        
        sparql_query = f"""
        PREFIX wb: <http://webook.com/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?book ?title ?description ?price ?condition ?categoryLabel
        WHERE {{
            ?book a wb:Book ;
                  wb:hasTitle ?title ;
                  wb:hasPrice ?price ;
                  wb:belongsToCategory ?category .
            
            OPTIONAL {{ ?book wb:hasDescription ?description }}
            OPTIONAL {{ ?book wb:hasCondition ?condition }}
            OPTIONAL {{ ?category rdfs:label ?categoryLabel }}
            
            # 直接分类匹配或父分类匹配
            {{ 
                FILTER ({' || '.join(category_conditions)})
            }} UNION {{
                ?subcategory rdfs:subClassOf ?category .
                ?book wb:belongsToCategory ?subcategory .
                FILTER ({' || '.join(category_conditions)})
            }}
        }}
        ORDER BY ?categoryLabel ?title
        LIMIT {limit}
        """
        
        return self.execute_sparql_query(sparql_query)
    
    def related_books_search(self, query, limit=5):
        """
        相关书籍推荐搜索
        基于书籍的相似属性进行推荐
        """
        # 如果查询中包含具体的技术词汇，搜索相同技术栈的书籍
        tech_terms = self.extract_tech_terms(query)
        if not tech_terms:
            return []
        
        filters = []
        for term in tech_terms:
            filters.append(f'CONTAINS(LCASE(str(?language)), "{term}") || CONTAINS(LCASE(str(?keyword)), "{term}")')
        
        sparql_query = f"""
        PREFIX wb: <http://webook.com/ontology#>
        
        SELECT DISTINCT ?book ?title ?description ?price ?language
        WHERE {{
            ?book a wb:Book ;
                  wb:hasTitle ?title ;
                  wb:hasPrice ?price .
            
            OPTIONAL {{ ?book wb:hasDescription ?description }}
            OPTIONAL {{ ?book wb:hasLanguage ?language }}
            OPTIONAL {{ ?book wb:hasKeyword ?keyword }}
            
            FILTER ({' || '.join(filters)})
        }}
        ORDER BY ?language ?title
        LIMIT {limit}
        """
        
        return self.execute_sparql_query(sparql_query)
    
    def preprocess_query(self, query):
        """预处理查询文本"""
        query_lower = query.lower().strip()
        
        # 中文分词
        chinese_words = jieba.lcut(query_lower)
        
        # 英文单词提取
        english_words = re.findall(r'\b[a-zA-Z]{2,}\b', query_lower)
        
        # 合并并过滤停用词
        stopwords = {'的', '是', '在', '和', '与', '等', '了', '也', '就', 'the', 'and', 'or', 'in', 'on', 'at'}
        words = []
        
        for word in chinese_words + english_words:
            if len(word) > 1 and word not in stopwords:
                words.append(word)
        
        return list(set(words))  # 去重
    
    def expand_query_with_synonyms(self, query):
        """使用同义词扩展查询"""
        expanded_terms = set()
        query_lower = query.lower()
        
        # 检查同义词映射
        for main_term, synonyms in self.kb.synonyms.items():
            # 检查主词或任何同义词是否在查询中
            if main_term in query_lower or any(syn in query_lower for syn in synonyms):
                expanded_terms.add(main_term)
                expanded_terms.update(synonyms)
        
        # 添加原始查询词
        expanded_terms.update(self.preprocess_query(query))
        
        return list(expanded_terms)
    
    def infer_categories_from_query(self, query):
        """从查询中推断目标分类"""
        query_lower = query.lower()
        inferred_categories = []
        
        # 检查分类关键词映射
        for category, keywords in self.kb.category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                inferred_categories.append(category)
        
        # 检查编程语言
        for language, keywords in self.kb.programming_languages.items():
            if any(keyword in query_lower for keyword in keywords):
                inferred_categories.append(language)
        
        return inferred_categories
    
    def extract_tech_terms(self, query):
        """提取查询中的技术术语"""
        query_lower = query.lower()
        tech_terms = []
        
        # 提取编程语言
        for language, keywords in self.kb.programming_languages.items():
            if any(keyword in query_lower for keyword in keywords):
                tech_terms.append(language.lower())
        
        # 提取技术关键词
        tech_keywords = ['ai', 'ml', 'web', 'database', 'algorithm', 'python', 'java', 'javascript']
        for keyword in tech_keywords:
            if keyword in query_lower:
                tech_terms.append(keyword)
        
        return tech_terms
    
    def execute_sparql_query(self, sparql_query):
        """
        执行SPARQL查询并返回格式化结果
        
        Args:
            sparql_query (str): SPARQL查询语句
            
        Returns:
            list: 格式化的查询结果
        """
        results = []
        
        try:
            query_result = self.g.query(sparql_query)
            
            for row in query_result:
                # 提取书籍ID
                book_id = str(row.book).split('/')[-1]
                
                # 构建结果对象
                result = {
                    'id': book_id,
                    'title': str(row.title) if hasattr(row, 'title') and row.title else '',
                    'description': str(row.description) if hasattr(row, 'description') and row.description else '',
                    'price': float(row.price) if hasattr(row, 'price') and row.price else 0.0,
                    'condition': str(row.condition).split('#')[-1] if hasattr(row, 'condition') and row.condition else 'unknown'
                }
                
                # 添加可选字段
                if hasattr(row, 'language') and row.language:
                    result['language'] = str(row.language)
                
                if hasattr(row, 'difficulty') and row.difficulty:
                    result['difficulty'] = str(row.difficulty).split('#')[-1]
                
                if hasattr(row, 'categoryLabel') and row.categoryLabel:
                    result['category'] = str(row.categoryLabel)
                
                results.append(result)
                
        except Exception as e:
            print(f"SPARQL查询执行错误: {e}")
            print(f"查询语句: {sparql_query}")
        
        return results
    
    def deduplicate_results(self, results):
        """去除重复结果并按相关性排序"""
        seen_ids = set()
        unique_results = []
        
        for result in results:
            if result['id'] not in seen_ids:
                unique_results.append(result)
                seen_ids.add(result['id'])
        
        # 简单的相关性排序（可以进一步优化）
        return sorted(unique_results, key=lambda x: x['price'])
    
    def get_recommendations_by_book_id(self, book_id, limit=5):
        """根据书籍ID获取相关推荐"""
        sparql_query = f"""
        PREFIX wb: <http://webook.com/ontology#>
        
        SELECT DISTINCT ?relatedBook ?title ?price ?category
        WHERE {{
            # 获取目标书籍的分类
            <http://webook.com/resource/book/{book_id}> wb:belongsToCategory ?sharedCategory .
            
            # 查找同分类的其他书籍
            ?relatedBook a wb:Book ;
                        wb:hasTitle ?title ;
                        wb:hasPrice ?price ;
                        wb:belongsToCategory ?sharedCategory .
            
            OPTIONAL {{ ?sharedCategory rdfs:label ?category }}
            
            # 排除自己
            FILTER (?relatedBook != <http://webook.com/resource/book/{book_id}>)
        }}
        ORDER BY ?price
        LIMIT {limit}
        """
        
        return self.execute_sparql_query(sparql_query)
    
    def get_search_suggestions(self, partial_query):
        """根据部分查询获取搜索建议"""
        suggestions = []
        partial_lower = partial_query.lower()
        
        # 从同义词中提取建议
        for main_term, synonyms in self.kb.synonyms.items():
            if partial_lower in main_term or any(partial_lower in syn for syn in synonyms):
                suggestions.extend([main_term] + synonyms[:2])
        
        # 从分类中提取建议
        for category, keywords in self.kb.category_keywords.items():
            if any(partial_lower in keyword for keyword in keywords):
                suggestions.extend(keywords[:3])
        
        return list(set(suggestions))[:10]  # 返回前10个建议

# 创建全局搜索服务实例
semantic_search_service = SPARQLSemanticSearch()