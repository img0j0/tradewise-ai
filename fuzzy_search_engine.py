"""
Fuzzy Search Engine with RapidFuzz
Advanced search functionality with typo correction and smart suggestions
"""

import logging
from rapidfuzz import fuzz, process
from typing import List, Dict, Optional, Tuple
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FuzzySearchEngine:
    def __init__(self):
        """Initialize fuzzy search engine with comprehensive stock database"""
        self.stock_database = self._build_stock_database()
        self.search_history = []
        logger.info("Fuzzy Search Engine initialized with fuzzy matching capabilities")
    
    def _build_stock_database(self) -> List[Dict]:
        """Build comprehensive searchable stock database"""
        return [
            # Technology Giants
            {"symbol": "AAPL", "name": "Apple Inc", "sector": "Technology", "logo": "🍎", "keywords": ["apple", "iphone", "mac", "tech"]},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "logo": "🪟", "keywords": ["microsoft", "windows", "office", "cloud"]},
            {"symbol": "GOOGL", "name": "Alphabet Inc", "sector": "Technology", "logo": "🔍", "keywords": ["google", "alphabet", "search", "android"]},
            {"symbol": "AMZN", "name": "Amazon.com Inc", "sector": "E-commerce", "logo": "📦", "keywords": ["amazon", "aws", "ecommerce", "cloud"]},
            {"symbol": "META", "name": "Meta Platforms Inc", "sector": "Technology", "logo": "👥", "keywords": ["meta", "facebook", "instagram", "social"]},
            {"symbol": "TSLA", "name": "Tesla Inc", "sector": "Automotive", "logo": "⚡", "keywords": ["tesla", "electric", "elon", "musk", "ev"]},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "logo": "🖥️", "keywords": ["nvidia", "gpu", "ai", "graphics"]},
            {"symbol": "NFLX", "name": "Netflix Inc", "sector": "Media", "logo": "🎬", "keywords": ["netflix", "streaming", "movies", "shows"]},
            
            # Financial Services
            {"symbol": "JPM", "name": "JPMorgan Chase & Co", "sector": "Financial", "logo": "🏦", "keywords": ["jpmorgan", "chase", "bank", "financial"]},
            {"symbol": "BAC", "name": "Bank of America Corp", "sector": "Financial", "logo": "🏛️", "keywords": ["bank", "america", "bofa", "financial"]},
            {"symbol": "WFC", "name": "Wells Fargo & Company", "sector": "Financial", "logo": "🐎", "keywords": ["wells", "fargo", "bank", "financial"]},
            {"symbol": "GS", "name": "Goldman Sachs Group Inc", "sector": "Financial", "logo": "💼", "keywords": ["goldman", "sachs", "investment", "bank"]},
            
            # Healthcare & Biotech
            {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "logo": "🏥", "keywords": ["johnson", "j&j", "healthcare", "pharma"]},
            {"symbol": "PFE", "name": "Pfizer Inc", "sector": "Healthcare", "logo": "💊", "keywords": ["pfizer", "pharma", "vaccine", "drugs"]},
            {"symbol": "UNH", "name": "UnitedHealth Group Inc", "sector": "Healthcare", "logo": "🩺", "keywords": ["united", "health", "insurance", "healthcare"]},
            {"symbol": "MRNA", "name": "Moderna Inc", "sector": "Biotech", "logo": "🧬", "keywords": ["moderna", "mrna", "vaccine", "biotech"]},
            
            # Consumer & Retail
            {"symbol": "WMT", "name": "Walmart Inc", "sector": "Retail", "logo": "🛒", "keywords": ["walmart", "retail", "shopping", "groceries"]},
            {"symbol": "HD", "name": "Home Depot Inc", "sector": "Retail", "logo": "🔨", "keywords": ["home", "depot", "hardware", "construction"]},
            {"symbol": "NKE", "name": "Nike Inc", "sector": "Consumer", "logo": "👟", "keywords": ["nike", "shoes", "athletic", "sports"]},
            {"symbol": "SBUX", "name": "Starbucks Corporation", "sector": "Consumer", "logo": "☕", "keywords": ["starbucks", "coffee", "cafe", "drinks"]},
            
            # Electric Vehicles & Green Energy
            {"symbol": "RIVN", "name": "Rivian Automotive Inc", "sector": "Automotive", "logo": "🚛", "keywords": ["rivian", "electric", "truck", "ev"]},
            {"symbol": "LCID", "name": "Lucid Group Inc", "sector": "Automotive", "logo": "🏎️", "keywords": ["lucid", "motors", "electric", "luxury", "ev"]},
            {"symbol": "F", "name": "Ford Motor Company", "sector": "Automotive", "logo": "🚗", "keywords": ["ford", "motor", "cars", "automotive"]},
            {"symbol": "GM", "name": "General Motors Company", "sector": "Automotive", "logo": "🏭", "keywords": ["gm", "general", "motors", "automotive"]},
            
            # Semiconductors
            {"symbol": "AMD", "name": "Advanced Micro Devices", "sector": "Technology", "logo": "💻", "keywords": ["amd", "processor", "cpu", "gpu"]},
            {"symbol": "INTC", "name": "Intel Corporation", "sector": "Technology", "logo": "🔧", "keywords": ["intel", "processor", "cpu", "chips"]},
            {"symbol": "TSM", "name": "Taiwan Semiconductor", "sector": "Technology", "logo": "⚙️", "keywords": ["tsmc", "taiwan", "semiconductor", "chips"]},
            {"symbol": "QCOM", "name": "QUALCOMM Incorporated", "sector": "Technology", "logo": "📱", "keywords": ["qualcomm", "mobile", "chips", "wireless"]},
            
            # Meme Stocks & Popular Trading
            {"symbol": "GME", "name": "GameStop Corp", "sector": "Retail", "logo": "🎮", "keywords": ["gamestop", "gaming", "meme", "retail"]},
            {"symbol": "AMC", "name": "AMC Entertainment Holdings", "sector": "Entertainment", "logo": "🎭", "keywords": ["amc", "movies", "cinema", "entertainment"]},
            {"symbol": "BB", "name": "BlackBerry Limited", "sector": "Technology", "logo": "📞", "keywords": ["blackberry", "mobile", "security", "software"]},
            
            # Fintech & Crypto
            {"symbol": "PYPL", "name": "PayPal Holdings Inc", "sector": "Fintech", "logo": "💳", "keywords": ["paypal", "payments", "digital", "fintech"]},
            {"symbol": "SQ", "name": "Block Inc", "sector": "Fintech", "logo": "⏹️", "keywords": ["square", "block", "payments", "bitcoin"]},
            {"symbol": "COIN", "name": "Coinbase Global Inc", "sector": "Fintech", "logo": "₿", "keywords": ["coinbase", "crypto", "bitcoin", "exchange"]},
            
            # Popular Tech Stocks
            {"symbol": "PLTR", "name": "Palantir Technologies", "sector": "Technology", "logo": "🔮", "keywords": ["palantir", "data", "analytics", "ai"]},
            {"symbol": "SNOW", "name": "Snowflake Inc", "sector": "Technology", "logo": "❄️", "keywords": ["snowflake", "cloud", "data", "warehouse"]},
            {"symbol": "ZM", "name": "Zoom Video Communications", "sector": "Technology", "logo": "📹", "keywords": ["zoom", "video", "meetings", "remote"]},
            {"symbol": "UBER", "name": "Uber Technologies Inc", "sector": "Technology", "logo": "🚕", "keywords": ["uber", "rideshare", "transport", "delivery"]},
            {"symbol": "LYFT", "name": "Lyft Inc", "sector": "Technology", "logo": "🚗", "keywords": ["lyft", "rideshare", "transport", "mobility"]},
        ]
    
    def fuzzy_search(self, query: str, threshold: int = 60, max_results: int = 8) -> Tuple[List[Dict], List[str]]:
        """
        Perform fuzzy search with typo correction and suggestions
        Returns: (results, suggestions)
        """
        query = query.strip().lower()
        if not query:
            return [], []
        
        # Track search
        self.search_history.append(query)
        
        # Create searchable strings for each stock
        search_strings = []
        for stock in self.stock_database:
            # Multiple search targets
            targets = [
                stock["symbol"].lower(),
                stock["name"].lower(),
                stock["sector"].lower()
            ] + [kw.lower() for kw in stock.get("keywords", [])]
            
            for target in targets:
                search_strings.append((target, stock))
        
        # Perform fuzzy matching
        matches = process.extract(
            query,
            [s[0] for s in search_strings],
            scorer=fuzz.WRatio,
            limit=max_results * 2
        )
        
        # Process results
        results = []
        seen_symbols = set()
        suggestions = []
        
        for match_text, score, _ in matches:
            if score >= threshold:
                # Find corresponding stock
                stock = next((s[1] for s in search_strings if s[0] == match_text), None)
                if stock and stock["symbol"] not in seen_symbols:
                    results.append({
                        **stock,
                        "match_score": score,
                        "match_reason": self._get_match_reason(query, match_text, stock)
                    })
                    seen_symbols.add(stock["symbol"])
            elif score >= 40:  # Lower threshold for suggestions
                stock = next((s[1] for s in search_strings if s[0] == match_text), None)
                if stock:
                    suggestions.append(f"{stock['symbol']} - {stock['name']}")
        
        # Limit results
        results = results[:max_results]
        suggestions = list(set(suggestions))[:5]  # Remove duplicates and limit
        
        logger.info(f"Fuzzy search for '{query}': {len(results)} results, {len(suggestions)} suggestions")
        return results, suggestions
    
    def _get_match_reason(self, query: str, match_text: str, stock: Dict) -> str:
        """Determine why this stock matched the query"""
        query_lower = query.lower()
        
        if query_lower == stock["symbol"].lower():
            return "exact_symbol"
        elif query_lower in stock["name"].lower():
            return "company_name"
        elif query_lower in stock["sector"].lower():
            return "sector"
        elif any(query_lower in kw for kw in stock.get("keywords", [])):
            return "keyword"
        else:
            return "fuzzy_match"
    
    def get_autocomplete_suggestions(self, query: str, limit: int = 6) -> List[Dict]:
        """Get autocomplete suggestions with enhanced display info"""
        if not query or len(query) < 2:
            # Return popular stocks for empty/short queries
            return self.stock_database[:limit]
        
        results, _ = self.fuzzy_search(query, threshold=30, max_results=limit)
        
        # Enhance results for autocomplete display
        enhanced_results = []
        for result in results:
            enhanced_results.append({
                "symbol": result["symbol"],
                "name": result["name"],
                "sector": result["sector"],
                "logo": result["logo"],
                "match_score": result.get("match_score", 0),
                "match_reason": result.get("match_reason", "fuzzy_match")
            })
        
        return enhanced_results
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """Get 'Did you mean?' suggestions for failed searches"""
        _, suggestions = self.fuzzy_search(query, threshold=100, max_results=0)  # High threshold to get no results
        
        if not suggestions:
            # Generate alternative suggestions based on common patterns
            suggestions = self._generate_alternative_suggestions(query)
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def _generate_alternative_suggestions(self, query: str) -> List[str]:
        """Generate alternative search suggestions"""
        query_lower = query.lower()
        suggestions = []
        
        # Common company name patterns
        name_mappings = {
            "apple": "AAPL - Apple Inc",
            "microsoft": "MSFT - Microsoft Corporation",
            "google": "GOOGL - Alphabet Inc",
            "amazon": "AMZN - Amazon.com Inc",
            "tesla": "TSLA - Tesla Inc",
            "netflix": "NFLX - Netflix Inc",
            "facebook": "META - Meta Platforms Inc",
            "nvidia": "NVDA - NVIDIA Corporation"
        }
        
        # Check for partial matches in common names
        for name, suggestion in name_mappings.items():
            if query_lower in name or name in query_lower:
                suggestions.append(suggestion)
        
        # Sector-based suggestions
        if any(term in query_lower for term in ["tech", "technology"]):
            suggestions.extend(["AAPL - Apple Inc", "MSFT - Microsoft Corporation", "GOOGL - Alphabet Inc"])
        elif any(term in query_lower for term in ["bank", "financial"]):
            suggestions.extend(["JPM - JPMorgan Chase", "BAC - Bank of America", "WFC - Wells Fargo"])
        elif any(term in query_lower for term in ["car", "auto", "electric"]):
            suggestions.extend(["TSLA - Tesla Inc", "RIVN - Rivian Automotive", "F - Ford Motor Company"])
        
        return suggestions
    
    def get_search_analytics(self) -> Dict:
        """Get search analytics and insights"""
        return {
            "total_searches": len(self.search_history),
            "recent_searches": self.search_history[-10:] if self.search_history else [],
            "database_size": len(self.stock_database),
            "supported_sectors": list(set(stock["sector"] for stock in self.stock_database))
        }

# Initialize global fuzzy search engine
fuzzy_search_engine = FuzzySearchEngine()

def search_stocks_fuzzy(query: str, limit: int = 8) -> Dict:
    """Main fuzzy search function for API endpoints"""
    try:
        results, suggestions = fuzzy_search_engine.fuzzy_search(query, max_results=limit)
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "suggestions": suggestions,
            "result_count": len(results),
            "has_suggestions": len(suggestions) > 0
        }
    except Exception as e:
        logger.error(f"Fuzzy search error: {str(e)}")
        return {
            "success": False,
            "error": "Search temporarily unavailable",
            "results": [],
            "suggestions": []
        }

def get_autocomplete_fuzzy(query: str, limit: int = 6) -> Dict:
    """Autocomplete with fuzzy matching"""
    try:
        suggestions = fuzzy_search_engine.get_autocomplete_suggestions(query, limit)
        
        return {
            "success": True,
            "query": query,
            "suggestions": suggestions,
            "count": len(suggestions)
        }
    except Exception as e:
        logger.error(f"Autocomplete error: {str(e)}")
        return {
            "success": False,
            "error": "Autocomplete temporarily unavailable",
            "suggestions": []
        }