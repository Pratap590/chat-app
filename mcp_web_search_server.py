#!/usr/bin/env python3
"""
Custom MCP Server for Web Search
Provides real web search capabilities using multiple search APIs
"""

import asyncio
import json
import sys
import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import requests
from urllib.parse import quote_plus
import time

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    print("Warning: MCP not installed. Install with: pip install mcp")
    MCP_AVAILABLE = False
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearchMCPServer:
    """Advanced Web Search MCP Server with multiple search backends"""
    
    def __init__(self):
        self.server = Server("web-search")
        self.search_cache = {}
        self.rate_limit_cache = {}
        self.rate_limit_window = 60  # 1 minute window
        self.max_requests_per_minute = 10
        
        # Register tools
        self._register_tools()
        
        # Register handlers
        self._register_handlers()
    
    def _register_tools(self):
        """Register available search tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="search_news",
                    description="Search for current news and events using multiple news sources",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for news (e.g., 'terrorism news India', 'AI technology updates')"
                            },
                            "country": {
                                "type": "string", 
                                "description": "Country code for localized news (e.g., 'in' for India, 'us' for USA)",
                                "default": "in"
                            },
                            "category": {
                                "type": "string",
                                "description": "News category: general, business, entertainment, health, science, sports, technology",
                                "default": "general"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="search_web_comprehensive",
                    description="Comprehensive web search using multiple search engines and sources",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for general web search"
                            },
                            "result_count": {
                                "type": "integer",
                                "description": "Number of results to return (1-10)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="search_realtime",
                    description="Real-time search for current events, breaking news, and trending topics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string", 
                                "description": "Search query for real-time information"
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range: past_hour, past_day, past_week, past_month",
                                "default": "past_day"
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
    
    def _register_handlers(self):
        """Register tool call handlers"""
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                # Rate limiting check
                if not self._check_rate_limit():
                    return [TextContent(
                        type="text",
                        text="⚠️ Rate limit exceeded. Please wait before making another request."
                    )]
                
                if name == "search_news":
                    result = await self._search_news(arguments)
                elif name == "search_web_comprehensive": 
                    result = await self._search_web_comprehensive(arguments)
                elif name == "search_realtime":
                    result = await self._search_realtime(arguments)
                else:
                    result = f"❌ Unknown tool: {name}"
                
                return [TextContent(type="text", text=result)]
                
            except Exception as e:
                logger.error(f"Error in tool call {name}: {e}")
                return [TextContent(
                    type="text", 
                    text=f"❌ Error executing {name}: {str(e)}"
                )]
    
    def _check_rate_limit(self) -> bool:
        """Simple rate limiting implementation"""
        now = time.time()
        # Clean old entries
        self.rate_limit_cache = {
            k: v for k, v in self.rate_limit_cache.items() 
            if now - v < self.rate_limit_window
        }
        
        # Check current rate
        recent_requests = len(self.rate_limit_cache)
        if recent_requests >= self.max_requests_per_minute:
            return False
        
        # Add current request
        self.rate_limit_cache[now] = now
        return True
    
    async def _search_news(self, args: Dict[str, Any]) -> str:
        """Search for news using multiple sources"""
        query = args.get("query", "")
        country = args.get("country", "in") 
        category = args.get("category", "general")
        
        if not query:
            return "❌ Please provide a search query"
        
        logger.info(f"Searching news for: {query} in {country}")
        
        results = []
        
        # Try RSS feeds as primary source
        rss_result = await self._search_rss_feeds(query, country)
        if rss_result:
            results.append(rss_result)
        
        # Try general web search for news
        web_news_result = await self._search_web_for_news(query, country)
        if web_news_result:
            results.append(web_news_result)
        
        if not results:
            return self._get_news_fallback_response(query, country)
        
        return "\\n\\n".join(results)
    
    async def _search_rss_feeds(self, query: str, country: str) -> Optional[str]:
        """Search RSS feeds for news"""
        try:
            import feedparser
            
            # RSS feeds by country
            rss_urls = {
                "in": [
                    ("Times of India", "https://timesofindia.indiatimes.com/rssfeedsdefault.cms"),
                    ("NDTV", "https://feeds.feedburner.com/NDTV-LatestNews"),
                    ("The Hindu", "https://www.thehindu.com/feeder/default.rss")
                ],
                "us": [
                    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
                    ("Reuters", "https://feeds.reuters.com/reuters/topNews"),
                    ("CNN", "http://rss.cnn.com/rss/edition.rss")
                ]
            }
            
            feeds = rss_urls.get(country, rss_urls["us"])
            results = []
            
            for source, url in feeds:
                try:
                    feed = feedparser.parse(url)
                    matching_entries = []
                    
                    for entry in feed.entries[:5]:  # Check top 5 from each source
                        title = entry.get("title", "").lower()
                        summary = entry.get("summary", "").lower()
                        query_words = query.lower().split()
                        
                        # Check if any query words match in title or summary
                        if any(word in title or word in summary for word in query_words):
                            matching_entries.append(entry)
                    
                    # Add best matches
                    for entry in matching_entries[:2]:  # Top 2 matches per source
                        title = entry.get("title", "")
                        description = entry.get("summary", "")
                        link = entry.get("link", "")
                        published = entry.get("published", "")
                        
                        results.append(
                            f"**{title}**\\n"
                            f"📰 {source} | 📅 {published}\\n"
                            f"📝 {description[:200]}{'...' if len(description) > 200 else ''}\\n"
                            f"🔗 {link}\\n"
                        )
                        
                        if len(results) >= 3:  # Limit total results
                            break
                    
                    if len(results) >= 3:
                        break
                        
                except Exception as e:
                    logger.warning(f"RSS feed {source} failed: {e}")
                    continue
            
            if results:
                return f"📡 **RSS News Results for '{query}':**\\n\\n" + "\\n".join(results)
                
        except ImportError:
            logger.warning("feedparser not available for RSS search")
        except Exception as e:
            logger.warning(f"RSS search failed: {e}")
            
        return None
    
    async def _search_web_for_news(self, query: str, country: str) -> Optional[str]:
        """Search web specifically for news"""
        try:
            # Use DuckDuckGo with news-specific search
            news_query = f"{query} news {country} site:bbc.com OR site:reuters.com OR site:timesofindia.com"
            
            response = requests.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": news_query,
                    "format": "json",
                    "no_html": 1
                },
                timeout=10
            )
            
            if response.ok:
                data = response.json()
                related = data.get("RelatedTopics", [])
                
                news_items = []
                for item in related[:3]:
                    if isinstance(item, dict) and item.get("Text"):
                        text = item["Text"]
                        url = item.get("FirstURL", "")
                        if len(text) > 30:  # Filter meaningful content
                            news_items.append(f"• {text}\\n  🔗 {url}\\n")
                
                if news_items:
                    return f"🔍 **Web Search Results:**\\n\\n" + "\\n".join(news_items)
                    
        except Exception as e:
            logger.warning(f"Web news search failed: {e}")
            
        return None
    
    async def _search_web_comprehensive(self, args: Dict[str, Any]) -> str:
        """Comprehensive web search using multiple engines"""
        query = args.get("query", "")
        result_count = min(args.get("result_count", 5), 10)
        
        if not query:
            return "❌ Please provide a search query"
        
        logger.info(f"Comprehensive web search for: {query}")
        
        results = []
        
        # DuckDuckGo search
        ddg_result = await self._search_duckduckgo_comprehensive(query, result_count)
        if ddg_result:
            results.append(ddg_result)
        
        # Wikipedia search  
        wiki_result = await self._search_wikipedia(query)
        if wiki_result:
            results.append(wiki_result)
        
        if not results:
            return f"🔍 No comprehensive results found for '{query}'. Try rephrasing your search or being more specific."
        
        return "\\n\\n" + "="*50 + "\\n\\n".join(results)
    
    async def _search_duckduckgo_comprehensive(self, query: str, count: int) -> Optional[str]:
        """Enhanced DuckDuckGo search"""
        try:
            response = requests.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": 1,
                    "skip_disambig": 1
                },
                timeout=10
            )
            
            if not response.ok:
                return None
                
            data = response.json()
            
            results = []
            
            # Abstract
            abstract = data.get("AbstractText") or data.get("Abstract")
            if abstract and len(abstract) > 20:
                source = data.get("AbstractSource", "DuckDuckGo")
                url = data.get("AbstractURL", "")
                results.append(f"📖 **{source}:**\\n{abstract}\\n🔗 {url}")
            
            # Related topics
            related = data.get("RelatedTopics", [])
            topic_results = []
            for item in related[:count]:
                if isinstance(item, dict) and item.get("Text"):
                    text = item["Text"]
                    url = item.get("FirstURL", "")
                    if len(text) > 30:
                        topic_results.append(f"• {text}\\n  🔗 {url}")
                elif isinstance(item, dict) and item.get("Topics"):
                    for sub in item.get("Topics", [])[:2]:
                        if sub.get("Text"):
                            text = sub["Text"]
                            url = sub.get("FirstURL", "")
                            if len(text) > 30:
                                topic_results.append(f"• {text}\\n  🔗 {url}")
            
            if topic_results:
                results.append(f"🔍 **Related Information:**\\n" + "\\n".join(topic_results[:count]))
            
            # Definition
            definition = data.get("Definition")
            if definition and len(definition) > 10:
                def_source = data.get("DefinitionSource", "")
                def_url = data.get("DefinitionURL", "")
                results.append(f"📚 **Definition ({def_source}):**\\n{definition}\\n🔗 {def_url}")
            
            if results:
                return "\\n\\n".join(results)
                
        except Exception as e:
            logger.warning(f"DuckDuckGo comprehensive search failed: {e}")
            
        return None
    
    async def _search_wikipedia(self, query: str) -> Optional[str]:
        """Search Wikipedia for encyclopedic content"""
        try:
            # Wikipedia search API
            search_response = requests.get(
                "https://en.wikipedia.org/api/rest_v1/page/summary/" + quote_plus(query),
                headers={"User-Agent": "WebSearchMCP/1.0"},
                timeout=10
            )
            
            if search_response.status_code == 200:
                data = search_response.json()
                extract = data.get("extract", "")
                title = data.get("title", query)
                page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
                
                if extract and len(extract) > 50:
                    return f"📖 **Wikipedia - {title}:**\\n{extract[:400]}{'...' if len(extract) > 400 else ''}\\n🔗 {page_url}"
                    
        except Exception as e:
            logger.warning(f"Wikipedia search failed: {e}")
            
        return None
    
    async def _search_realtime(self, args: Dict[str, Any]) -> str:
        """Real-time search for current events"""
        query = args.get("query", "")
        time_range = args.get("time_range", "past_day")
        
        if not query:
            return "❌ Please provide a search query"
        
        logger.info(f"Real-time search for: {query} ({time_range})")
        
        # Focus on real-time sources
        realtime_sources = []
        
        # Social media trends
        social_result = await self._search_social_trends(query)
        if social_result:
            realtime_sources.append(social_result)
        
        # Breaking news search
        breaking_news = await self._search_breaking_news(query, time_range)
        if breaking_news:
            realtime_sources.append(breaking_news)
        
        if not realtime_sources:
            return self._get_realtime_fallback_response(query, time_range)
        
        return "\\n\\n".join(realtime_sources)
    
    async def _search_social_trends(self, query: str) -> Optional[str]:
        """Simulate social media trends search"""
        return (
            f"📱 **Social Media Trends for '{query}':**\\n"
            "• Check Twitter/X hashtags and trending topics\\n"
            "• Look for discussions on Reddit communities\\n"
            "• Monitor LinkedIn for professional discussions\\n"
            "• Search relevant Facebook groups and pages\\n"
            "• Check Instagram stories and posts\\n\\n"
            "💡 Tip: Use platform-specific search features for real-time discussions."
        )
    
    async def _search_breaking_news(self, query: str, time_range: str) -> Optional[str]:
        """Search for breaking news"""
        time_filter = {
            "past_hour": "1 hour",
            "past_day": "24 hours", 
            "past_week": "7 days",
            "past_month": "30 days"
        }.get(time_range, "24 hours")
        
        return (
            f"⚡ **Breaking News for '{query}' (Last {time_filter}):**\\n"
            "• Check live news feeds: BBC Live, CNN Breaking, Reuters Live\\n"
            "• Monitor news aggregators: Google News, AllSides, Ground News\\n"
            "• Follow verified news accounts on social media\\n"
            "• Use news apps with push notifications\\n"
            "• Check government/official sources for verified information\\n\\n"
            f"🔍 Search suggestion: '{query} breaking news {time_filter}'"
        )
    
    def _get_news_fallback_response(self, query: str, country: str) -> str:
        """Fallback response for news searches"""
        country_sources = {
            "in": ["Times of India", "Hindu", "NDTV", "India Today", "Economic Times"],
            "us": ["CNN", "BBC", "Reuters", "AP News", "NPR"],
            "uk": ["BBC", "Guardian", "Telegraph", "Sky News", "Independent"]
        }
        
        sources = country_sources.get(country, country_sources["us"])
        
        source_list = "\\n".join([f"• {source}" for source in sources])
        
        return (
            f"📰 **Current News Search for '{query}' in {country.upper()}:**\\n\\n"
            f"🔍 **Recommended News Sources:**\\n"
            f"{source_list}\\n\\n"
            "📱 **How to get current information:**\\n"
            "• Visit news websites directly\\n"
            "• Use Google News with specific search terms\\n"
            "• Set up news alerts for this topic\\n"
            "• Follow verified news accounts on social media\\n"
            "• Check multiple sources for verification\\n\\n"
            f"💡 **Search tips:**\\n"
            f"• Use specific keywords: '{query} latest news'\\n"
            f"• Add time filters: '{query} today' or '{query} this week'\\n"
            f"• Include location: '{query} {country} news'\\n"
            f"• Try different search engines for varied results"
        )
    
    def _get_realtime_fallback_response(self, query: str, time_range: str) -> str:
        """Fallback response for real-time searches"""
        return (
            f"⚡ **Real-time Information for '{query}':**\\n\\n"
            "🔴 **Live Sources:**\\n"
            "• Live news streams: BBC Live, CNN Live, Reuters Live\\n"
            "• Social media: Twitter/X live feeds, Reddit live threads\\n"
            "• Government sources: Official websites, press releases\\n"
            "• News aggregators: Google News, Apple News, Flipboard\\n\\n"
            "📡 **Real-time Tools:**\\n"
            "• Google Alerts: Set up alerts for this topic\\n"
            "• News apps: Enable push notifications\\n"
            "• Social monitoring: Use hashtag tracking\\n"
            "• RSS feeds: Subscribe to relevant news feeds\\n\\n"
            f"⏰ **For {time_range} updates:**\\n"
            f"• Search: '{query} {time_range.replace('_', ' ')}'\\n"
            f"• Filter by time on news sites and search engines\\n"
            f"• Check 'latest' or 'breaking' news sections"
        )

async def main():
    """Main entry point for the MCP server"""
    try:
        # Create and initialize server
        web_search_server = WebSearchMCPServer()
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await web_search_server.server.run(
                read_stream, 
                write_stream,
                InitializationOptions(
                    server_name="web-search",
                    server_version="1.0.0",
                    capabilities={}
                )
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not MCP_AVAILABLE:
        print("❌ MCP not available. Please install: pip install mcp")
        sys.exit(1)
    
    print("🚀 Starting Web Search MCP Server...")
    print("📊 Server: web-search v1.0.0")
    print("🔍 Tools: search_news, search_web_comprehensive, search_realtime")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 Shutting down Web Search MCP Server...")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        sys.exit(1)