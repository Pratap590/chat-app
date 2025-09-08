#!/usr/bin/env python3
"""
Playwright MCP Server for Advanced Web Automation
Provides real-time web scraping and current information retrieval
"""

import asyncio
import json
import sys
import os
import logging
from typing import Any, Dict, List, Optional
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

# Playwright imports
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    print("Warning: Playwright not installed. Install with: pip install playwright")
    PLAYWRIGHT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlaywrightMCPServer:
    """Advanced Web Automation MCP Server using Playwright"""
    
    def __init__(self):
        self.server = Server("playwright-web")
        self.browser = None
        self.context = None
        self.rate_limit_cache = {}
        self.rate_limit_window = 60
        self.max_requests_per_minute = 8
        
        self._register_tools()
        self._register_handlers()
    
    def _register_tools(self):
        """Register available web automation tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="scrape_live_news",
                    description="Scrape live news from major news websites for current information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query or topic"},
                            "source": {"type": "string", "description": "News source: bbc, reuters, timesofindia, ndtv", "default": "bbc"},
                            "max_articles": {"type": "integer", "description": "Max articles (1-5)", "default": 3}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="search_google_news",
                    description="Search Google News for current events and breaking news",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "query": {"type": "string", "description": "Search query for Google News"},
                            "region": {"type": "string", "description": "Region code (in/us/uk)", "default": "in"}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_breaking_news",
                    description="Get breaking news and live updates",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string", "description": "Topic to get breaking news for"}
                        },
                        "required": ["topic"]
                    }
                )
            ]
    
    def _register_handlers(self):
        """Register tool call handlers"""
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if not self._check_rate_limit():
                    return [TextContent(type="text", text="⚠️ Rate limit exceeded. Please wait.")]
                
                if not self.browser:
                    await self._init_browser()
                
                if name == "scrape_live_news":
                    result = await self._scrape_live_news(arguments)
                elif name == "search_google_news": 
                    result = await self._search_google_news(arguments)
                elif name == "get_breaking_news":
                    result = await self._get_breaking_news(arguments)
                else:
                    result = f"❌ Unknown tool: {name}"
                
                return [TextContent(type="text", text=result)]
                
            except Exception as e:
                logger.error(f"Error in tool call {name}: {e}")
                return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
    
    def _check_rate_limit(self) -> bool:
        """Rate limiting implementation"""
        now = time.time()
        self.rate_limit_cache = {k: v for k, v in self.rate_limit_cache.items() if now - v < self.rate_limit_window}
        
        if len(self.rate_limit_cache) >= self.max_requests_per_minute:
            return False
        
        self.rate_limit_cache[now] = now
        return True
    
    async def _init_browser(self):
        """Initialize Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not available. Install: pip install playwright")
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            logger.info("Playwright browser initialized")
        except Exception as e:
            logger.error(f"Failed to init browser: {e}")
            raise
    
    async def _scrape_live_news(self, args: Dict[str, Any]) -> str:
        """Scrape news from major websites"""
        query = args.get("query", "")
        source = args.get("source", "bbc").lower()
        max_articles = min(args.get("max_articles", 3), 5)
        
        if not query:
            return "❌ Please provide a search query"
        
        logger.info(f"Scraping {source} for: {query}")
        
        try:
            page = await self.context.new_page()
            articles = []
            
            if source == "bbc":
                await page.goto(f"https://www.bbc.com/search?q={query.replace(' ', '+')}", timeout=30000)
                await page.wait_for_selector("article", timeout=10000)
                elements = await page.query_selector_all("article")
                
                for element in elements[:max_articles]:
                    try:
                        title_elem = await element.query_selector("h1, h2, h3")
                        link_elem = await element.query_selector("a")
                        
                        if title_elem and link_elem:
                            title = await title_elem.inner_text()
                            href = await link_elem.get_attribute("href")
                            if href and not href.startswith("http"):
                                href = f"https://www.bbc.com{href}"
                            
                            articles.append({"title": title.strip(), "url": href, "source": "BBC"})
                    except Exception:
                        continue
            
            elif source == "timesofindia":
                await page.goto(f"https://timesofindia.indiatimes.com/topic/{query.replace(' ', '-')}", timeout=30000)
                await page.wait_for_timeout(3000)
                elements = await page.query_selector_all("article, .story-list li")
                
                for element in elements[:max_articles]:
                    try:
                        title_elem = await element.query_selector("h1, h2, h3, .story-title")
                        link_elem = await element.query_selector("a")
                        
                        if title_elem and link_elem:
                            title = await title_elem.inner_text()
                            href = await link_elem.get_attribute("href")
                            if href and not href.startswith("http"):
                                href = f"https://timesofindia.indiatimes.com{href}"
                            
                            articles.append({"title": title.strip(), "url": href, "source": "Times of India"})
                    except Exception:
                        continue
            
            await page.close()
            
            if not articles:
                return f"📰 No recent articles found for '{query}' on {source.upper()}."
            
            result = f"📰 **Live News from {source.upper()} - '{query}':**\\n\\n"
            for i, article in enumerate(articles, 1):
                result += f"**{i}. {article['title']}**\\n"
                result += f"🔗 {article['url']}\\n\\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {source}: {e}")
            return f"❌ Error scraping {source}: {str(e)}"
    
    async def _search_google_news(self, args: Dict[str, Any]) -> str:
        """Search Google News"""
        query = args.get("query", "")
        region = args.get("region", "in")
        
        if not query:
            return "❌ Please provide a search query"
        
        logger.info(f"Searching Google News for: {query}")
        
        try:
            page = await self.context.new_page()
            search_url = f"https://news.google.com/search?q={query.replace(' ', '+')}&hl=en-{region.upper()}&gl={region.upper()}"
            
            await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            
            articles = []
            article_elements = await page.query_selector_all("article")
            
            for element in article_elements[:5]:
                try:
                    title_elem = await element.query_selector("h3, h4")
                    source_elem = await element.query_selector("[data-n-tid]")
                    time_elem = await element.query_selector("time")
                    link_elem = await element.query_selector("a")
                    
                    if title_elem and link_elem:
                        title = await title_elem.inner_text()
                        href = await link_elem.get_attribute("href")
                        source = await source_elem.inner_text() if source_elem else "Unknown"
                        time_ago = await time_elem.inner_text() if time_elem else "Recent"
                        
                        if href and href.startswith("./"):
                            href = f"https://news.google.com{href[1:]}"
                        
                        articles.append({
                            "title": title.strip(),
                            "source": source.strip(),
                            "time": time_ago.strip(),
                            "url": href
                        })
                except Exception:
                    continue
            
            await page.close()
            
            if not articles:
                return f"📰 No recent news found for '{query}' on Google News."
            
            result = f"📰 **Google News Results - '{query}':**\\n\\n"
            for i, article in enumerate(articles, 1):
                result += f"**{i}. {article['title']}**\\n"
                result += f"📰 {article['source']} | ⏰ {article['time']}\\n"
                result += f"🔗 {article['url']}\\n\\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching Google News: {e}")
            return f"❌ Error searching Google News: {str(e)}"
    
    async def _get_breaking_news(self, args: Dict[str, Any]) -> str:
        """Get breaking news updates"""
        topic = args.get("topic", "")
        
        if not topic:
            return "❌ Please provide a topic"
        
        logger.info(f"Getting breaking news for: {topic}")
        
        try:
            page = await self.context.new_page()
            
            # Check BBC Live for breaking news
            await page.goto("https://www.bbc.com/news/live", timeout=30000)
            await page.wait_for_timeout(3000)
            
            breaking_items = []
            live_elements = await page.query_selector_all("[data-testid*='live'], .live-reporting")
            
            for element in live_elements[:3]:
                try:
                    text = await element.inner_text()
                    if topic.lower() in text.lower():
                        breaking_items.append(text.strip()[:200])
                except Exception:
                    continue
            
            await page.close()
            
            if breaking_items:
                result = f"🔴 **Breaking News - '{topic}':**\\n\\n"
                for i, item in enumerate(breaking_items, 1):
                    result += f"**{i}.** {item}\\n\\n"
                return result
            else:
                return (f"🔍 **No immediate breaking news found for '{topic}'.**\\n\\n"
                       "💡 **Suggestions:**\\n"
                       "• Check live news feeds: BBC Live, Reuters Live\\n"
                       "• Monitor news aggregators: Google News\\n"
                       "• Follow verified news accounts on social media\\n"
                       "• Set up Google Alerts for this topic")
            
        except Exception as e:
            logger.error(f"Error getting breaking news: {e}")
            return f"❌ Error getting breaking news: {str(e)}"

async def main():
    """Main entry point for the MCP server"""
    try:
        web_server = PlaywrightMCPServer()
        
        async with stdio_server() as (read_stream, write_stream):
            await web_server.server.run(
                read_stream, 
                write_stream,
                InitializationOptions(
                    server_name="playwright-web",
                    server_version="1.0.0",
                    capabilities={}
                )
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not MCP_AVAILABLE:
        print("❌ MCP not available. Install: pip install mcp")
        sys.exit(1)
    
    print("🚀 Starting Playwright Web MCP Server...")
    print("📊 Server: playwright-web v1.0.0")
    print("🔍 Tools: scrape_live_news, search_google_news, get_breaking_news")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 Shutting down Playwright MCP Server...")
    except Exception as e:
        print(f"❌ Server failed: {e}")
        sys.exit(1)