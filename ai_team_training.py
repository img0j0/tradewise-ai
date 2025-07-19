"""
AI Team Training System
Advanced machine learning system that trains AI team members to improve their performance over time
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
import os
from dataclasses import dataclass, asdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from textblob import TextBlob

logger = logging.getLogger(__name__)

@dataclass
class ConversationAnalysis:
    """Analysis of a conversation for training purposes"""
    query: str
    response: str
    member: str
    user_satisfaction: float
    response_time: float
    confidence: float
    topics: List[str]
    sentiment: str
    effectiveness_score: float
    timestamp: datetime

@dataclass
class LearningPattern:
    """Identified learning pattern for improvement"""
    pattern_id: str
    member: str
    topic_cluster: str
    successful_phrases: List[str]
    common_issues: List[str]
    improvement_suggestions: List[str]
    confidence_boost: float

class AITeamTrainer:
    """Advanced training system for AI team members"""
    
    def __init__(self):
        self.db_path = "ai_team_training.db"
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.conversation_history = []
        self.learning_patterns = {}
        self.member_performance = {
            'sarah': {'accuracy': 0.75, 'confidence': 0.8, 'user_satisfaction': 0.85},
            'alex': {'accuracy': 0.87, 'confidence': 0.9, 'user_satisfaction': 0.82},
            'maria': {'accuracy': 0.92, 'confidence': 0.85, 'user_satisfaction': 0.88}
        }
        self._initialize_database()
        self._load_training_data()
        logger.info("AI Team Trainer initialized with advanced learning capabilities")

    def _initialize_database(self):
        """Initialize training database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    member TEXT NOT NULL,
                    user_satisfaction REAL DEFAULT 0.0,
                    response_time REAL DEFAULT 0.0,
                    confidence REAL DEFAULT 0.0,
                    topics TEXT,
                    sentiment TEXT,
                    effectiveness_score REAL DEFAULT 0.0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Learning patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT UNIQUE,
                    member TEXT,
                    topic_cluster TEXT,
                    successful_phrases TEXT,
                    common_issues TEXT,
                    improvement_suggestions TEXT,
                    confidence_boost REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member TEXT,
                    accuracy REAL,
                    confidence REAL,
                    user_satisfaction REAL,
                    total_conversations INTEGER,
                    successful_resolutions INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Training database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing training database: {e}")

    def _load_training_data(self):
        """Load existing training data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load recent conversations
            cursor.execute('''
                SELECT * FROM conversations 
                WHERE timestamp > datetime('now', '-30 days')
                ORDER BY timestamp DESC
                LIMIT 1000
            ''')
            
            conversations = cursor.fetchall()
            self.conversation_history = []
            
            for conv in conversations:
                analysis = ConversationAnalysis(
                    query=conv[1],
                    response=conv[2], 
                    member=conv[3],
                    user_satisfaction=conv[4],
                    response_time=conv[5],
                    confidence=conv[6],
                    topics=json.loads(conv[7]) if conv[7] else [],
                    sentiment=conv[8],
                    effectiveness_score=conv[9],
                    timestamp=datetime.fromisoformat(conv[10])
                )
                self.conversation_history.append(analysis)
            
            conn.close()
            logger.info(f"Loaded {len(self.conversation_history)} conversations for training")
            
        except Exception as e:
            logger.error(f"Error loading training data: {e}")

    def analyze_conversation(self, query: str, response: str, member: str, 
                           user_feedback: Optional[float] = None) -> ConversationAnalysis:
        """Analyze a conversation for training purposes"""
        try:
            # Extract topics using TF-IDF
            combined_text = f"{query} {response}"
            topics = self._extract_topics(combined_text)
            
            # Analyze sentiment
            sentiment_analysis = TextBlob(query)
            sentiment = "positive" if sentiment_analysis.sentiment.polarity > 0 else \
                       "negative" if sentiment_analysis.sentiment.polarity < 0 else "neutral"
            
            # Calculate effectiveness score
            effectiveness_score = self._calculate_effectiveness_score(query, response, member)
            
            # Estimate user satisfaction if not provided
            if user_feedback is None:
                user_feedback = self._estimate_user_satisfaction(response, effectiveness_score)
            
            analysis = ConversationAnalysis(
                query=query,
                response=response,
                member=member,
                user_satisfaction=user_feedback,
                response_time=1.2,  # Simulated response time
                confidence=self.member_performance.get(member, self.member_performance['sarah'])['confidence'],
                topics=topics,
                sentiment=sentiment,
                effectiveness_score=effectiveness_score,
                timestamp=datetime.now()
            )
            
            # Store in database
            self._store_conversation_analysis(analysis)
            
            # Add to history
            self.conversation_history.append(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing conversation: {e}")
            return None

    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text using NLP"""
        try:
            # Simple keyword extraction
            words = text.lower().split()
            trading_keywords = {
                'stock', 'invest', 'buy', 'sell', 'portfolio', 'market', 'price', 
                'analysis', 'recommendation', 'risk', 'return', 'profit', 'loss',
                'apple', 'tesla', 'microsoft', 'google', 'amazon', 'nvidia',
                'search', 'login', 'account', 'problem', 'error', 'help',
                'beginner', 'learn', 'start', 'guide', 'tutorial', 'how'
            }
            
            found_topics = [word for word in words if word in trading_keywords]
            return list(set(found_topics))[:5]  # Top 5 topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []

    def _calculate_effectiveness_score(self, query: str, response: str, member: str) -> float:
        """Calculate effectiveness score for a response"""
        try:
            score = 0.0
            
            # Validate member exists in performance tracking
            if member not in self.member_performance:
                logger.warning(f"Unknown member '{member}' - using default performance")
                member = 'sarah'  # Default fallback
            
            # Base score from member performance
            score += self.member_performance[member]['accuracy'] * 0.4
            
            # Response length (optimal range)
            response_length = len(response)
            if 100 <= response_length <= 500:
                score += 0.2
            elif response_length > 500:
                score += 0.1
            
            # Actionable content detection
            actionable_words = ['recommend', 'suggest', 'try', 'check', 'consider', 'use']
            if any(word in response.lower() for word in actionable_words):
                score += 0.2
            
            # Professional tone
            if any(word in response for word in ['analysis', 'data', 'confident', 'professional']):
                score += 0.1
            
            # Member-specific bonuses
            if member == 'sarah' and any(word in response.lower() for word in ['market', 'stock', 'invest']):
                score += 0.1
            elif member == 'alex' and any(word in response.lower() for word in ['step', 'solution', 'fix']):
                score += 0.1
            elif member == 'maria' and any(word in response.lower() for word in ['guide', 'help', 'start']):
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating effectiveness score: {e}")
            return 0.5

    def _estimate_user_satisfaction(self, response: str, effectiveness_score: float) -> float:
        """Estimate user satisfaction based on response quality"""
        try:
            # Base satisfaction from effectiveness
            satisfaction = effectiveness_score * 0.8
            
            # Bonus for helpful indicators
            helpful_indicators = ['here', 'help', 'solution', 'recommend', 'suggest']
            if any(indicator in response.lower() for indicator in helpful_indicators):
                satisfaction += 0.1
            
            # Bonus for confidence indicators
            if any(conf in response for conf in ['confident', 'certain', '95%', '90%']):
                satisfaction += 0.1
            
            return min(satisfaction, 1.0)
            
        except Exception as e:
            logger.error(f"Error estimating user satisfaction: {e}")
            return 0.5

    def _store_conversation_analysis(self, analysis: ConversationAnalysis):
        """Store conversation analysis in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations 
                (query, response, member, user_satisfaction, response_time, confidence,
                 topics, sentiment, effectiveness_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis.query,
                analysis.response,
                analysis.member,
                analysis.user_satisfaction,
                analysis.response_time,
                analysis.confidence,
                json.dumps(analysis.topics),
                analysis.sentiment,
                analysis.effectiveness_score,
                analysis.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing conversation analysis: {e}")

    def identify_learning_patterns(self, member: str = None) -> List[LearningPattern]:
        """Identify learning patterns for improvement"""
        try:
            patterns = []
            
            # Filter conversations by member if specified
            conversations = [c for c in self.conversation_history if not member or c.member == member]
            
            if len(conversations) < 5:
                logger.warning("Not enough conversation data for pattern analysis")
                return patterns
            
            # Group conversations by member
            member_conversations = {}
            for conv in conversations:
                if conv.member not in member_conversations:
                    member_conversations[conv.member] = []
                member_conversations[conv.member].append(conv)
            
            # Analyze patterns for each member
            for mem, convs in member_conversations.items():
                # Identify successful response patterns
                successful_convs = [c for c in convs if c.effectiveness_score > 0.7]
                unsuccessful_convs = [c for c in convs if c.effectiveness_score < 0.5]
                
                if successful_convs:
                    # Extract successful phrases
                    successful_phrases = self._extract_successful_phrases(successful_convs)
                    
                    # Identify common issues
                    common_issues = self._identify_common_issues(unsuccessful_convs)
                    
                    # Generate improvement suggestions
                    improvements = self._generate_improvement_suggestions(mem, successful_phrases, common_issues)
                    
                    pattern = LearningPattern(
                        pattern_id=f"{mem}_{datetime.now().strftime('%Y%m%d')}",
                        member=mem,
                        topic_cluster=self._get_primary_topic_cluster(convs),
                        successful_phrases=successful_phrases,
                        common_issues=common_issues,
                        improvement_suggestions=improvements,
                        confidence_boost=0.05  # 5% confidence boost
                    )
                    
                    patterns.append(pattern)
            
            # Store patterns
            for pattern in patterns:
                self._store_learning_pattern(pattern)
            
            logger.info(f"Identified {len(patterns)} learning patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"Error identifying learning patterns: {e}")
            return []

    def _extract_successful_phrases(self, conversations: List[ConversationAnalysis]) -> List[str]:
        """Extract phrases from successful conversations"""
        successful_phrases = []
        
        for conv in conversations:
            # Extract key phrases from successful responses
            response = conv.response.lower()
            
            # Look for action phrases
            if 'i recommend' in response:
                successful_phrases.append('i recommend')
            if 'here\'s what' in response:
                successful_phrases.append('here\'s what')
            if 'let me help' in response:
                successful_phrases.append('let me help')
            if 'based on' in response:
                successful_phrases.append('based on')
        
        return list(set(successful_phrases))[:10]  # Top 10 unique phrases

    def _identify_common_issues(self, conversations: List[ConversationAnalysis]) -> List[str]:
        """Identify common issues in unsuccessful conversations"""
        issues = []
        
        for conv in conversations:
            response = conv.response.lower()
            
            # Check for vague responses
            if len(response) < 50:
                issues.append('responses too short')
            
            # Check for lack of specificity
            if 'maybe' in response or 'might' in response:
                issues.append('lack of confidence')
            
            # Check for missing actionable advice
            actionable_words = ['try', 'use', 'check', 'consider', 'recommend']
            if not any(word in response for word in actionable_words):
                issues.append('missing actionable advice')
        
        return list(set(issues))

    def _generate_improvement_suggestions(self, member: str, successful_phrases: List[str], 
                                        common_issues: List[str]) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        # General improvements
        if 'responses too short' in common_issues:
            suggestions.append('Provide more detailed explanations (aim for 150-300 words)')
        
        if 'lack of confidence' in common_issues:
            suggestions.append('Use more confident language and provide specific confidence percentages')
        
        if 'missing actionable advice' in common_issues:
            suggestions.append('Always include 2-3 specific actionable recommendations')
        
        # Member-specific suggestions
        if member == 'sarah':
            suggestions.append('Include market data and specific stock analysis')
            suggestions.append('Provide confidence scores for investment recommendations')
        elif member == 'alex':
            suggestions.append('Provide step-by-step troubleshooting instructions')
            suggestions.append('Include estimated resolution times')
        elif member == 'maria':
            suggestions.append('Adapt explanations to user experience level')
            suggestions.append('Provide learning resources and next steps')
        
        return suggestions

    def _get_primary_topic_cluster(self, conversations: List[ConversationAnalysis]) -> str:
        """Get primary topic cluster for conversations"""
        all_topics = []
        for conv in conversations:
            all_topics.extend(conv.topics)
        
        if not all_topics:
            return 'general'
        
        # Find most common topic
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return max(topic_counts.items(), key=lambda x: x[1])[0]

    def _store_learning_pattern(self, pattern: LearningPattern):
        """Store learning pattern in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO learning_patterns
                (pattern_id, member, topic_cluster, successful_phrases, common_issues,
                 improvement_suggestions, confidence_boost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.pattern_id,
                pattern.member,
                pattern.topic_cluster,
                json.dumps(pattern.successful_phrases),
                json.dumps(pattern.common_issues),
                json.dumps(pattern.improvement_suggestions),
                pattern.confidence_boost
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing learning pattern: {e}")

    def train_member_performance(self, member: str = None) -> Dict[str, Any]:
        """Train and improve member performance based on learning patterns"""
        try:
            training_results = {}
            
            # Get learning patterns
            patterns = self.identify_learning_patterns(member)
            
            members_to_train = [member] if member else ['sarah', 'alex', 'maria']
            
            for mem in members_to_train:
                member_patterns = [p for p in patterns if p.member == mem]
                
                if not member_patterns:
                    continue
                
                # Calculate performance improvements
                current_performance = self.member_performance[mem]
                
                # Apply confidence boosts from patterns
                confidence_boost = sum(p.confidence_boost for p in member_patterns)
                new_confidence = min(current_performance['confidence'] + confidence_boost, 1.0)
                
                # Calculate accuracy improvement based on recent conversations
                recent_convs = [c for c in self.conversation_history[-50:] if c.member == mem]
                if recent_convs:
                    avg_effectiveness = sum(c.effectiveness_score for c in recent_convs) / len(recent_convs)
                    accuracy_improvement = (avg_effectiveness - current_performance['accuracy']) * 0.1
                    new_accuracy = min(current_performance['accuracy'] + accuracy_improvement, 1.0)
                else:
                    new_accuracy = current_performance['accuracy']
                
                # Update performance
                self.member_performance[mem] = {
                    'accuracy': new_accuracy,
                    'confidence': new_confidence,
                    'user_satisfaction': current_performance['user_satisfaction']
                }
                
                training_results[mem] = {
                    'previous_accuracy': current_performance['accuracy'],
                    'new_accuracy': new_accuracy,
                    'previous_confidence': current_performance['confidence'],
                    'new_confidence': new_confidence,
                    'patterns_applied': len(member_patterns),
                    'improvement_suggestions': [s for p in member_patterns for s in p.improvement_suggestions]
                }
            
            logger.info(f"Training completed for {len(training_results)} members")
            return training_results
            
        except Exception as e:
            logger.error(f"Error training member performance: {e}")
            return {}

    def get_training_report(self) -> Dict[str, Any]:
        """Generate comprehensive training report"""
        try:
            report = {
                'total_conversations': len(self.conversation_history),
                'training_period': '30 days',
                'member_performance': self.member_performance,
                'recent_improvements': [],
                'training_statistics': {},
                'recommendations': []
            }
            
            # Calculate training statistics
            for member in ['sarah', 'alex', 'maria']:
                member_convs = [c for c in self.conversation_history if c.member == member]
                
                if member_convs:
                    avg_satisfaction = sum(c.user_satisfaction for c in member_convs) / len(member_convs)
                    avg_effectiveness = sum(c.effectiveness_score for c in member_convs) / len(member_convs)
                    
                    report['training_statistics'][member] = {
                        'total_conversations': len(member_convs),
                        'average_satisfaction': round(avg_satisfaction, 3),
                        'average_effectiveness': round(avg_effectiveness, 3),
                        'top_topics': self._get_top_topics_for_member(member)
                    }
            
            # Generate recommendations
            report['recommendations'] = [
                'Continue monitoring user feedback for real-time improvements',
                'Implement A/B testing for response variations',
                'Expand training data with more diverse conversation scenarios',
                'Consider advanced neural network models for response generation'
            ]
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating training report: {e}")
            return {}

    def _get_top_topics_for_member(self, member: str) -> List[str]:
        """Get top topics for a specific member"""
        member_convs = [c for c in self.conversation_history if c.member == member]
        all_topics = []
        
        for conv in member_convs:
            all_topics.extend(conv.topics)
        
        # Count topic frequency
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Return top 5 topics
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:5]]

# Initialize global trainer instance
ai_team_trainer = AITeamTrainer()