"""
External Data Sources Module for GAIA
Provides clients for fetching real data from various APIs.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from urllib.parse import quote

import structlog

from config import get_settings

logger = structlog.get_logger()
settings = get_settings()


@dataclass
class NewsArticle:
    """Represents a news article."""
    title: str
    description: str
    content: str
    source: str
    author: Optional[str]
    url: str
    published_at: datetime
    image_url: Optional[str] = None
    sentiment: Optional[float] = None  # To be filled by analysis


@dataclass
class CompanyFinancials:
    """Represents company financial data."""
    symbol: str
    name: str
    description: str
    sector: str
    industry: str
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    revenue: Optional[float] = None
    profit_margin: Optional[float] = None
    beta: Optional[float] = None
    high_52_week: Optional[float] = None
    low_52_week: Optional[float] = None
    analyst_target: Optional[float] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SECFiling:
    """Represents an SEC filing."""
    accession_number: str
    filing_type: str  # 10-K, 10-Q, 8-K, etc.
    filing_date: datetime
    accepted_date: datetime
    company_name: str
    cik: str
    document_url: str
    description: str
    items: List[str] = field(default_factory=list)


class NewsAPIClient:
    """
    Client for NewsAPI.org

    Get your API key at: https://newsapi.org/register
    Free tier: 100 requests/day, 1 month old articles
    """

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.NEWS_API_KEY
        if not self.api_key:
            logger.warning("newsapi_key_not_set", message="NEWS_API_KEY not configured")

    async def search_news(
        self,
        query: str,
        days_back: int = 30,
        language: str = "en",
        sort_by: str = "relevancy",
        page_size: int = 20,
    ) -> List[NewsArticle]:
        """
        Search for news articles about a company or topic.

        Args:
            query: Search query (company name, topic, etc.)
            days_back: How many days back to search
            language: Language filter
            sort_by: Sort order (relevancy, popularity, publishedAt)
            page_size: Number of articles to return

        Returns:
            List of NewsArticle objects
        """
        if not self.api_key:
            logger.warning("newsapi_skipped", reason="No API key")
            return []

        from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        url = f"{self.BASE_URL}/everything"
        params = {
            "q": query,
            "from": from_date,
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "apiKey": self.api_key,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error("newsapi_error", status=response.status, error=error_text)
                        return []

                    data = await response.json()

                    if data.get("status") != "ok":
                        logger.error("newsapi_failed", message=data.get("message"))
                        return []

                    articles = []
                    for article in data.get("articles", []):
                        try:
                            published = datetime.fromisoformat(
                                article["publishedAt"].replace("Z", "+00:00")
                            )
                            articles.append(NewsArticle(
                                title=article.get("title", ""),
                                description=article.get("description", ""),
                                content=article.get("content", ""),
                                source=article.get("source", {}).get("name", "Unknown"),
                                author=article.get("author"),
                                url=article.get("url", ""),
                                published_at=published,
                                image_url=article.get("urlToImage"),
                            ))
                        except Exception as e:
                            logger.warning("newsapi_parse_error", error=str(e))
                            continue

                    logger.info(
                        "newsapi_success",
                        query=query,
                        articles_found=len(articles),
                    )
                    return articles

        except asyncio.TimeoutError:
            logger.error("newsapi_timeout", query=query)
            return []
        except Exception as e:
            logger.error("newsapi_exception", error=str(e))
            return []

    async def get_top_headlines(
        self,
        query: str = None,
        category: str = "business",
        country: str = "us",
        page_size: int = 10,
    ) -> List[NewsArticle]:
        """Get top headlines, optionally filtered by query."""
        if not self.api_key:
            return []

        url = f"{self.BASE_URL}/top-headlines"
        params = {
            "category": category,
            "country": country,
            "pageSize": page_size,
            "apiKey": self.api_key,
        }
        if query:
            params["q"] = query

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        return []

                    data = await response.json()
                    articles = []
                    for article in data.get("articles", []):
                        try:
                            published = datetime.fromisoformat(
                                article["publishedAt"].replace("Z", "+00:00")
                            )
                            articles.append(NewsArticle(
                                title=article.get("title", ""),
                                description=article.get("description", ""),
                                content=article.get("content", ""),
                                source=article.get("source", {}).get("name", "Unknown"),
                                author=article.get("author"),
                                url=article.get("url", ""),
                                published_at=published,
                                image_url=article.get("urlToImage"),
                            ))
                        except Exception:
                            continue
                    return articles
        except Exception:
            return []


class AlphaVantageClient:
    """
    Client for Alpha Vantage financial data.

    Get your API key at: https://www.alphavantage.co/support/#api-key
    Free tier: 5 calls/minute, 500 calls/day
    """

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.ALPHA_VANTAGE_API_KEY
        if not self.api_key:
            logger.warning("alphavantage_key_not_set", message="ALPHA_VANTAGE_API_KEY not configured")

    async def get_company_overview(self, symbol: str) -> Optional[CompanyFinancials]:
        """
        Get comprehensive company overview including financials.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "MSFT")

        Returns:
            CompanyFinancials object or None
        """
        if not self.api_key:
            logger.warning("alphavantage_skipped", reason="No API key")
            return None

        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, params=params, timeout=30) as response:
                    if response.status != 200:
                        logger.error("alphavantage_error", status=response.status)
                        return None

                    data = await response.json()

                    if "Error Message" in data or "Note" in data:
                        logger.warning(
                            "alphavantage_limit",
                            message=data.get("Note") or data.get("Error Message"),
                        )
                        return None

                    if not data.get("Symbol"):
                        logger.warning("alphavantage_no_data", symbol=symbol)
                        return None

                    def safe_float(value, default=None):
                        try:
                            return float(value) if value and value != "None" else default
                        except (ValueError, TypeError):
                            return default

                    company = CompanyFinancials(
                        symbol=data.get("Symbol", symbol),
                        name=data.get("Name", ""),
                        description=data.get("Description", ""),
                        sector=data.get("Sector", ""),
                        industry=data.get("Industry", ""),
                        market_cap=safe_float(data.get("MarketCapitalization")),
                        pe_ratio=safe_float(data.get("PERatio")),
                        eps=safe_float(data.get("EPS")),
                        dividend_yield=safe_float(data.get("DividendYield")),
                        revenue=safe_float(data.get("RevenueTTM")),
                        profit_margin=safe_float(data.get("ProfitMargin")),
                        beta=safe_float(data.get("Beta")),
                        high_52_week=safe_float(data.get("52WeekHigh")),
                        low_52_week=safe_float(data.get("52WeekLow")),
                        analyst_target=safe_float(data.get("AnalystTargetPrice")),
                        extra_data={
                            "exchange": data.get("Exchange"),
                            "currency": data.get("Currency"),
                            "country": data.get("Country"),
                            "fiscal_year_end": data.get("FiscalYearEnd"),
                            "latest_quarter": data.get("LatestQuarter"),
                            "book_value": safe_float(data.get("BookValue")),
                            "dividend_per_share": safe_float(data.get("DividendPerShare")),
                            "revenue_per_share": safe_float(data.get("RevenuePerShareTTM")),
                            "operating_margin": safe_float(data.get("OperatingMarginTTM")),
                            "return_on_assets": safe_float(data.get("ReturnOnAssetsTTM")),
                            "return_on_equity": safe_float(data.get("ReturnOnEquityTTM")),
                            "quarterly_earnings_growth": safe_float(data.get("QuarterlyEarningsGrowthYOY")),
                            "quarterly_revenue_growth": safe_float(data.get("QuarterlyRevenueGrowthYOY")),
                        }
                    )

                    logger.info(
                        "alphavantage_success",
                        symbol=symbol,
                        name=company.name,
                    )
                    return company

        except asyncio.TimeoutError:
            logger.error("alphavantage_timeout", symbol=symbol)
            return None
        except Exception as e:
            logger.error("alphavantage_exception", error=str(e))
            return None

    async def get_income_statement(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get annual and quarterly income statements."""
        if not self.api_key:
            return None

        params = {
            "function": "INCOME_STATEMENT",
            "symbol": symbol,
            "apikey": self.api_key,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, params=params, timeout=30) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    if "Error Message" in data or "Note" in data:
                        return None
                    return data
        except Exception:
            return None


class SECEdgarClient:
    """
    Client for SEC EDGAR filings.

    No API key required, but must include User-Agent header.
    Rate limit: 10 requests/second
    """

    BASE_URL = "https://data.sec.gov"
    SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"

    def __init__(self, user_agent: str = None):
        self.user_agent = user_agent or settings.SEC_EDGAR_USER_AGENT
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

    async def get_company_cik(self, ticker: str) -> Optional[str]:
        """Look up a company's CIK number by ticker."""
        url = f"{self.BASE_URL}/submissions/CIK{ticker.upper()}.json"

        try:
            async with aiohttp.ClientSession() as session:
                # Try direct lookup first (for when ticker is actually CIK)
                async with session.get(url, headers=self.headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("cik")

                # Search by ticker
                tickers_url = "https://www.sec.gov/files/company_tickers.json"
                async with session.get(tickers_url, headers=self.headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        for entry in data.values():
                            if entry.get("ticker", "").upper() == ticker.upper():
                                return str(entry.get("cik_str", "")).zfill(10)

        except Exception as e:
            logger.warning("sec_cik_lookup_error", ticker=ticker, error=str(e))

        return None

    async def get_recent_filings(
        self,
        ticker: str,
        filing_types: List[str] = None,
        limit: int = 10,
    ) -> List[SECFiling]:
        """
        Get recent SEC filings for a company.

        Args:
            ticker: Stock ticker symbol
            filing_types: Filter by filing types (10-K, 10-Q, 8-K, etc.)
            limit: Maximum number of filings to return

        Returns:
            List of SECFiling objects
        """
        if filing_types is None:
            filing_types = ["10-K", "10-Q", "8-K"]

        cik = await self.get_company_cik(ticker)
        if not cik:
            logger.warning("sec_cik_not_found", ticker=ticker)
            return []

        # Pad CIK to 10 digits
        cik_padded = str(cik).zfill(10)
        url = f"{self.BASE_URL}/submissions/CIK{cik_padded}.json"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=30) as response:
                    if response.status != 200:
                        logger.error("sec_filings_error", status=response.status)
                        return []

                    data = await response.json()
                    filings = []

                    recent = data.get("filings", {}).get("recent", {})
                    forms = recent.get("form", [])
                    accession_numbers = recent.get("accessionNumber", [])
                    filing_dates = recent.get("filingDate", [])
                    primary_docs = recent.get("primaryDocument", [])
                    descriptions = recent.get("primaryDocDescription", [])

                    company_name = data.get("name", "")

                    for i in range(min(len(forms), limit * 3)):  # Look at more to filter
                        form = forms[i] if i < len(forms) else ""

                        if filing_types and form not in filing_types:
                            continue

                        if len(filings) >= limit:
                            break

                        try:
                            accession = accession_numbers[i].replace("-", "")
                            filing_date = datetime.strptime(filing_dates[i], "%Y-%m-%d")
                            primary_doc = primary_docs[i] if i < len(primary_docs) else ""
                            description = descriptions[i] if i < len(descriptions) else form

                            doc_url = (
                                f"https://www.sec.gov/Archives/edgar/data/"
                                f"{cik}/{accession}/{primary_doc}"
                            )

                            filings.append(SECFiling(
                                accession_number=accession_numbers[i],
                                filing_type=form,
                                filing_date=filing_date,
                                accepted_date=filing_date,  # Simplified
                                company_name=company_name,
                                cik=cik_padded,
                                document_url=doc_url,
                                description=description,
                            ))
                        except Exception as e:
                            logger.warning("sec_filing_parse_error", error=str(e))
                            continue

                    logger.info(
                        "sec_filings_success",
                        ticker=ticker,
                        filings_found=len(filings),
                    )
                    return filings

        except asyncio.TimeoutError:
            logger.error("sec_filings_timeout", ticker=ticker)
            return []
        except Exception as e:
            logger.error("sec_filings_exception", error=str(e))
            return []

    async def get_filing_content(self, filing: SECFiling, max_chars: int = 50000) -> str:
        """
        Fetch the content of a filing (HTML/text).

        Note: For very large filings, consider extracting specific sections.

        Args:
            filing: SECFiling object
            max_chars: Maximum characters to return

        Returns:
            Filing content as text
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    filing.document_url,
                    headers=self.headers,
                    timeout=60,
                ) as response:
                    if response.status != 200:
                        return ""

                    content = await response.text()

                    # Basic HTML stripping (for proper parsing, use BeautifulSoup)
                    import re
                    text = re.sub(r'<[^>]+>', ' ', content)
                    text = re.sub(r'\s+', ' ', text)
                    text = text.strip()

                    if len(text) > max_chars:
                        text = text[:max_chars] + "..."

                    return text

        except Exception as e:
            logger.error("sec_content_error", error=str(e))
            return ""


# Factory functions for getting client instances
def get_news_client() -> NewsAPIClient:
    """Get a NewsAPI client instance."""
    return NewsAPIClient()


def get_financial_client() -> AlphaVantageClient:
    """Get an Alpha Vantage client instance."""
    return AlphaVantageClient()


# Alias for compatibility
get_alpha_vantage_client = get_financial_client


def get_sec_client() -> SECEdgarClient:
    """Get an SEC EDGAR client instance."""
    return SECEdgarClient()
