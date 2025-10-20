"""
WeBook 语义知识库
实现RDF三元组存储、本体定义和智能推理
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
import jieba
import re
import json

class WeBookKnowledgeBase:
    """WeBook语义知识库管理类"""
    
    def __init__(self):
        # 初始化RDF图
        self.g = Graph()
        
        # 定义命名空间
        self.WB = Namespace("http://webook.com/ontology#")
        self.BOOK = Namespace("http://webook.com/resource/book/")
        self.CATEGORY = Namespace("http://webook.com/resource/category/")
        self.AUTHOR = Namespace("http://webook.com/resource/author/")
        
        # 绑定命名空间前缀
        self.g.bind("wb", self.WB)
        self.g.bind("book", self.BOOK)
        self.g.bind("category", self.CATEGORY)
        self.g.bind("author", self.AUTHOR)
        
        # 初始化本体和知识规则
        self.init_ontology()
        self.init_knowledge_rules()
        
    def init_ontology(self):
        """初始化本体结构 - 定义实体、属性和关系"""
        
        # ===== 实体类定义 =====
        # 核心实体
        self.g.add((self.WB.Book, RDF.type, RDFS.Class))
        self.g.add((self.WB.Book, RDFS.label, Literal("图书")))
        
        self.g.add((self.WB.Category, RDF.type, RDFS.Class))
        self.g.add((self.WB.Category, RDFS.label, Literal("分类")))
        
        self.g.add((self.WB.Author, RDF.type, RDFS.Class))
        self.g.add((self.WB.Author, RDFS.label, Literal("作者")))
        
        self.g.add((self.WB.Publisher, RDF.type, RDFS.Class))
        self.g.add((self.WB.Publisher, RDFS.label, Literal("出版社")))
        
        # 条件和状态类
        self.g.add((self.WB.Condition, RDF.type, RDFS.Class))
        self.g.add((self.WB.Condition, RDFS.label, Literal("书籍状态")))
        
        self.g.add((self.WB.DifficultyLevel, RDF.type, RDFS.Class))
        self.g.add((self.WB.DifficultyLevel, RDFS.label, Literal("难度级别")))
        
        # ===== 对象属性定义 (实体间关系) =====
        # 书籍关系
        self.g.add((self.WB.belongsToCategory, RDF.type, RDF.Property))
        self.g.add((self.WB.belongsToCategory, RDFS.domain, self.WB.Book))
        self.g.add((self.WB.belongsToCategory, RDFS.range, self.WB.Category))
        self.g.add((self.WB.belongsToCategory, RDFS.label, Literal("属于分类")))
        
        self.g.add((self.WB.writtenBy, RDF.type, RDF.Property))
        self.g.add((self.WB.writtenBy, RDFS.domain, self.WB.Book))
        self.g.add((self.WB.writtenBy, RDFS.range, self.WB.Author))
        
        self.g.add((self.WB.publishedBy, RDF.type, RDF.Property))
        self.g.add((self.WB.publishedBy, RDFS.domain, self.WB.Book))
        self.g.add((self.WB.publishedBy, RDFS.range, self.WB.Publisher))
        
        self.g.add((self.WB.hasCondition, RDF.type, RDF.Property))
        self.g.add((self.WB.hasCondition, RDFS.domain, self.WB.Book))
        self.g.add((self.WB.hasCondition, RDFS.range, self.WB.Condition))
        
        self.g.add((self.WB.hasDifficulty, RDF.type, RDF.Property))
        self.g.add((self.WB.hasDifficulty, RDFS.domain, self.WB.Book))
        self.g.add((self.WB.hasDifficulty, RDFS.range, self.WB.DifficultyLevel))
        
        # 推荐关系
        self.g.add((self.WB.relatedTo, RDF.type, RDF.Property))
        self.g.add((self.WB.relatedTo, RDFS.domain, self.WB.Book))
        self.g.add((self.WB.relatedTo, RDFS.range, self.WB.Book))
        self.g.add((self.WB.relatedTo, RDFS.label, Literal("相关书籍")))
        
        # ===== 数据属性定义 (实体的具体属性) =====
        # 书籍基本属性
        self.g.add((self.WB.hasTitle, RDF.type, RDF.Property))
        self.g.add((self.WB.hasTitle, RDFS.domain, self.WB.Book))
        self.g.add((self.WB.hasTitle, RDFS.range, XSD.string))
        
        self.g.add((self.WB.hasDescription, RDF.type, RDF.Property))
        self.g.add((self.WB.hasDescription, RDFS.domain, self.WB.Book))
        self.g.add((self.WB.hasDescription, RDFS.range, XSD.string))
        
        self.g.add((self.WB.hasPrice, RDF.type, RDF.Property))
        self.g.add((self.WB.hasPrice, RDFS.domain, self.WB.Book))
        self.g.add((self.WB.hasPrice, RDFS.range, XSD.float))
        
        self.g.add((self.WB.hasKeyword, RDF.type, RDF.Property))
        self.g.add((self.WB.hasKeyword, RDFS.domain, self.WB.Book))
        self.g.add((self.WB.hasKeyword, RDFS.range, XSD.string))
        
        self.g.add((self.WB.hasLanguage, RDF.type, RDF.Property))
        self.g.add((self.WB.hasLanguage, RDFS.domain, self.WB.Book))
        self.g.add((self.WB.hasLanguage, RDFS.range, XSD.string))
        
        self.g.add((self.WB.hasISBN, RDF.type, RDF.Property))
        self.g.add((self.WB.hasISBN, RDFS.domain, self.WB.Book))
        self.g.add((self.WB.hasISBN, RDFS.range, XSD.string))
        
        # 创建分类层次结构
        self.create_category_hierarchy()
        
    def create_category_hierarchy(self):
        """创建领域分类的层次结构"""
        
        # 定义分类层次结构
        categories = {
            'ComputerScience': {
                'label': '计算机科学',
                'subcategories': {
                    'Programming': {
                        'label': '编程开发',
                        'subcategories': ['Python', 'Java', 'JavaScript', 'CPlusPlus', 'Go', 'PHP']
                    },
                    'ArtificialIntelligence': {
                        'label': '人工智能',
                        'subcategories': ['MachineLearning', 'DeepLearning', 'NLP', 'ComputerVision', 'DataScience']
                    },
                    'WebDevelopment': {
                        'label': '网页开发',
                        'subcategories': ['Frontend', 'Backend', 'FullStack', 'Mobile']
                    },
                    'Database': {
                        'label': '数据库',
                        'subcategories': ['SQL', 'NoSQL', 'BigData', 'DataWarehouse']
                    },
                    'Algorithm': {
                        'label': '算法',
                        'subcategories': ['DataStructure', 'AlgorithmDesign', 'Optimization']
                    },
                    'SoftwareEngineering': {
                        'label': '软件工程',
                        'subcategories': ['DesignPattern', 'Architecture', 'Testing', 'DevOps']
                    }
                }
            },
            'Mathematics': {
                'label': '数学',
                'subcategories': ['LinearAlgebra', 'Statistics', 'Calculus', 'DiscreteMath']
            },
            'Business': {
                'label': '商业管理',
                'subcategories': ['Management', 'Marketing', 'Finance', 'Economics']
            },
            'Literature': {
                'label': '文学',
                'subcategories': ['Novel', 'Poetry', 'Biography', 'History']
            }
        }
        
        self._create_category_tree(categories, None)
    
    def _create_category_tree(self, categories, parent_uri):
        """递归创建分类树"""
        for category_key, category_data in categories.items():
            category_uri = URIRef(f"{self.CATEGORY}{category_key}")
            
            # 添加分类实体
            self.g.add((category_uri, RDF.type, self.WB.Category))
            
            if isinstance(category_data, dict):
                # 有标签和子分类
                label = category_data.get('label', category_key)
                self.g.add((category_uri, RDFS.label, Literal(label)))
                
                # 添加父子关系
                if parent_uri:
                    self.g.add((category_uri, RDFS.subClassOf, parent_uri))
                
                # 处理子分类
                subcategories = category_data.get('subcategories', {})
                if isinstance(subcategories, dict):
                    self._create_category_tree(subcategories, category_uri)
                else:
                    # 简单的子分类列表
                    for sub_cat in subcategories:
                        sub_uri = URIRef(f"{self.CATEGORY}{sub_cat}")
                        self.g.add((sub_uri, RDF.type, self.WB.Category))
                        self.g.add((sub_uri, RDFS.label, Literal(sub_cat)))
                        self.g.add((sub_uri, RDFS.subClassOf, category_uri))
            else:
                # 简单分类
                self.g.add((category_uri, RDFS.label, Literal(category_data)))
                if parent_uri:
                    self.g.add((category_uri, RDFS.subClassOf, parent_uri))
    
    def init_knowledge_rules(self):
        """初始化知识规则和语义映射"""
        
        # 同义词映射 - 支持中英文语义理解
        self.synonyms = {
            'programming': ['编程', '程序设计', '代码', 'coding', 'development', '开发', 'dev'],
            'python': ['蟒蛇', 'py', 'python3', 'python编程'],
            'ai': ['人工智能', 'artificial intelligence', 'machine learning', '机器学习', 'ml', 
                   'deep learning', '深度学习', 'dl', '神经网络', 'neural network'],
            'web': ['网站', '网页', 'website', 'html', 'css', 'javascript', '前端', 'frontend', 
                    '后端', 'backend', '全栈', 'fullstack'],
            'database': ['数据库', 'db', 'sql', 'mysql', 'postgresql', '存储', 'storage', 'nosql'],
            'algorithm': ['算法', 'algo', '数据结构', 'data structure', '算法设计'],
            'java': ['java语言', 'javase', 'javaee', 'spring', 'java开发'],
            'tutorial': ['教程', '入门', '学习', '指南', 'guide', 'learn', 'course', '课程'],
            'advanced': ['高级', '进阶', '深入', '精通', 'master', '专家', 'expert'],
            'beginner': ['初学者', '新手', '入门', 'basic', '基础', '零基础', 'starter'],
            'book': ['书籍', '图书', '书本', '教材', 'textbook', '参考书'],
            'practice': ['实践', '实战', '项目', 'project', 'hands-on', '动手'],
            'theory': ['理论', '原理', 'theory', '基础理论', 'fundamental']
        }
        
        # 技能级别映射
        self.difficulty_levels = {
            'beginner': ['入门', '初级', '基础', '新手', '零基础', 'basic', 'intro', '初学'],
            'intermediate': ['中级', '进阶', '实战', 'intermediate', '提高', '实用'],
            'advanced': ['高级', '深入', '精通', '专家', 'advanced', 'expert', 'master', '资深']
        }
        
        # 编程语言关键词映射
        self.programming_languages = {
            'Python': ['python', 'py', '蟒蛇', 'python3', 'django', 'flask', 'pandas'],
            'Java': ['java', 'spring', 'javase', 'javaee', 'springboot'],
            'JavaScript': ['javascript', 'js', 'node', 'react', 'vue', 'angular', 'nodejs'],
            'CPlusPlus': ['c++', 'cpp', 'c plus plus'],
            'Go': ['golang', 'go语言', 'go开发'],
            'PHP': ['php', 'laravel', 'symfony'],
            'CSharp': ['c#', 'csharp', 'dotnet', '.net']
        }
        
        # 分类关键词映射
        self.category_keywords = {
            'Programming': ['编程', 'programming', 'code', '代码', 'develop', '开发'],
            'ArtificialIntelligence': ['ai', '人工智能', 'machine learning', '机器学习', 'deep learning', '深度学习'],
            'WebDevelopment': ['web', '网页', 'html', 'css', 'javascript', '前端', 'frontend', 'backend'],
            'Database': ['database', '数据库', 'sql', 'mysql', 'mongodb', '存储'],
            'Algorithm': ['algorithm', '算法', 'data structure', '数据结构'],
            'MachineLearning': ['machine learning', '机器学习', 'ml', 'sklearn', 'tensorflow'],
            'DeepLearning': ['deep learning', '深度学习', 'neural network', '神经网络', 'pytorch']
        }
    
    def add_book_to_kb(self, book_data):
        """将书籍数据添加到知识库"""
        book_uri = URIRef(f"{self.BOOK}{book_data['id']}")
        
        # 添加基本三元组
        self.g.add((book_uri, RDF.type, self.WB.Book))
        self.g.add((book_uri, self.WB.hasTitle, Literal(book_data['name'])))
        
        if book_data.get('description'):
            self.g.add((book_uri, self.WB.hasDescription, Literal(book_data['description'])))
        
        self.g.add((book_uri, self.WB.hasPrice, Literal(float(book_data['price']), datatype=XSD.float)))
        
        if book_data.get('degree_of_wear'):
            condition_uri = URIRef(f"{self.WB}{book_data['degree_of_wear'].replace(' ', '').replace('-', '')}")
            self.g.add((book_uri, self.WB.hasCondition, condition_uri))
        
        # 智能分析和推理
        self.analyze_and_enrich_book(book_uri, book_data)
        
        return book_uri
    
    def analyze_and_enrich_book(self, book_uri, book_data):
        """智能分析书籍并丰富知识库"""
        text = f"{book_data['name']} {book_data.get('description', '')}".lower()
        
        # 1. 提取和添加关键词
        keywords = self.extract_smart_keywords(text)
        for keyword in keywords[:15]:  # 限制关键词数量
            self.g.add((book_uri, self.WB.hasKeyword, Literal(keyword)))
        
        # 2. 自动分类
        categories = self.classify_book_intelligently(text)
        for category in categories:
            category_uri = URIRef(f"{self.CATEGORY}{category}")
            self.g.add((book_uri, self.WB.belongsToCategory, category_uri))
        
        # 3. 推断难度级别
        difficulty = self.infer_difficulty_level(text)
        if difficulty:
            difficulty_uri = URIRef(f"{self.WB}{difficulty}")
            self.g.add((book_uri, self.WB.hasDifficulty, difficulty_uri))
        
        # 4. 推断编程语言
        languages = self.infer_programming_languages(text)
        for language in languages:
            self.g.add((book_uri, self.WB.hasLanguage, Literal(language)))
    
    def extract_smart_keywords(self, text):
        """智能提取关键词"""
        keywords = set()
        
        # 中文分词
        chinese_words = jieba.lcut(text)
        for word in chinese_words:
            if len(word) > 1 and word not in ['的', '是', '在', '和', '与', '等', '了', '也', '就']:
                keywords.add(word.lower())
        
        # 英文单词提取
        english_words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
        for word in english_words:
            if word.lower() not in ['the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with']:
                keywords.add(word.lower())
        
        # 技术关键词增强
        tech_keywords = []
        for main_term, synonyms in self.synonyms.items():
            if main_term in text or any(syn in text for syn in synonyms):
                tech_keywords.append(main_term)
                
        keywords.update(tech_keywords)
        return list(keywords)
    
    def classify_book_intelligently(self, text):
        """智能书籍分类"""
        categories = []
        confidence_scores = {}
        
        # 计算每个分类的匹配得分
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            
            # 同义词匹配
            for main_term, synonyms in self.synonyms.items():
                if any(syn in keywords for syn in [main_term] + synonyms):
                    if main_term in text or any(syn in text for syn in synonyms):
                        score += 0.5
            
            if score > 0:
                confidence_scores[category] = score
        
        # 选择得分最高的分类
        if confidence_scores:
            # 取得分最高的分类
            max_score = max(confidence_scores.values())
            categories = [cat for cat, score in confidence_scores.items() if score >= max_score * 0.7]
        
        # 如果没有匹配的分类，使用通用分类
        if not categories:
            categories = ['General']
            
        return categories[:3]  # 最多返回3个分类
    
    def infer_difficulty_level(self, text):
        """推断书籍难度级别"""
        for level, indicators in self.difficulty_levels.items():
            if any(indicator in text for indicator in indicators):
                return level
        
        # 基于其他线索推断
        if any(word in text for word in ['项目', 'project', '实战', '案例']):
            return 'intermediate'
        elif any(word in text for word in ['理论', 'theory', '原理', '深入']):
            return 'advanced'
        else:
            return 'intermediate'  # 默认中级
    
    def infer_programming_languages(self, text):
        """推断涉及的编程语言"""
        languages = []
        
        for lang, keywords in self.programming_languages.items():
            if any(keyword in text for keyword in keywords):
                languages.append(lang)
        
        return languages
    
    def get_book_count(self):
        """获取知识库中书籍数量"""
        query = """
        PREFIX wb: <http://webook.com/ontology#>
        SELECT (COUNT(?book) as ?count)
        WHERE { ?book a wb:Book }
        """
        result = list(self.g.query(query))[0]
        return int(result.count) if result.count else 0
    
    def get_category_stats(self):
        """获取分类统计信息"""
        query = """
        PREFIX wb: <http://webook.com/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?category ?label (COUNT(?book) as ?bookCount)
        WHERE {
            ?book a wb:Book ;
                  wb:belongsToCategory ?category .
            OPTIONAL { ?category rdfs:label ?label }
        }
        GROUP BY ?category ?label
        ORDER BY DESC(?bookCount)
        """
        
        results = []
        for row in self.g.query(query):
            category_name = str(row.category).split('/')[-1]
            label = str(row.label) if row.label else category_name
            count = int(row.bookCount) if row.bookCount else 0
            results.append({
                'category': category_name,
                'label': label,
                'count': count
            })
        
        return results
    
    def export_ontology(self, format='turtle'):
        """导出本体为文件"""
        return self.g.serialize(format=format)
    
    def get_stats(self):
        """获取完整的知识库统计信息"""
        try:
            book_count = self.get_book_count()
            category_stats = self.get_category_stats()
            
            # 统计作者数量
            author_query = """
            PREFIX wb: <http://webook.com/ontology#>
            SELECT (COUNT(DISTINCT ?author) as ?authorCount)
            WHERE {
                ?book a wb:Book ;
                      wb:writtenBy ?author .
            }
            """
            
            author_count = 0
            for row in self.g.query(author_query):
                author_count = int(row.authorCount) if row.authorCount else 0
                break
            
            # 统计关系数量（三元组数量）
            triple_count = len(self.g)
            
            return {
                'books': book_count,
                'categories': len(category_stats),
                'authors': author_count,
                'triples': triple_count,
                'category_details': category_stats
            }
        except Exception as e:
            print(f"获取知识库统计失败: {e}")
            return {
                'books': 0,
                'categories': 0,
                'authors': 0,
                'triples': 0,
                'category_details': []
            }

# 创建全局知识库实例
knowledge_base = WeBookKnowledgeBase()