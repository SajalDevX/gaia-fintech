#!/usr/bin/env python3
"""
GAIA Company Analysis Test Script

Tests the analysis API with 5 demo companies:
- AAPL (Apple) - Tech, high ESG expected
- MSFT (Microsoft) - Tech, high ESG expected
- TSLA (Tesla) - EV, environmental focus
- XOM (Exxon Mobil) - Oil/Gas, greenwashing detection test
- NKE (Nike) - Consumer, supply chain focus

Usage:
    python test_companies.py
    python test_companies.py --ticker AAPL
    python test_companies.py --all --verbose
"""

import asyncio
import argparse
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

import httpx

# Configuration
API_BASE_URL = "http://localhost:8000"
ANALYSIS_TIMEOUT = 120  # 2 minutes max per analysis

# Test companies
TEST_COMPANIES = [
    {"ticker": "AAPL", "name": "Apple Inc.", "expected_esg": "high"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "expected_esg": "high"},
    {"ticker": "TSLA", "name": "Tesla, Inc.", "expected_esg": "high"},
    {"ticker": "XOM", "name": "Exxon Mobil Corporation", "expected_esg": "moderate"},
    {"ticker": "NKE", "name": "NIKE, Inc.", "expected_esg": "moderate"},
]


class Colors:
    """Terminal colors for output."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")


def print_success(text: str):
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} {text}")


def print_warning(text: str):
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {text}")


def print_error(text: str):
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {text}")


def print_info(text: str):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {text}")


async def check_health() -> bool:
    """Check if the API is healthy."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                print_success("API health check passed")
                return True
            else:
                print_error(f"API health check failed: {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Cannot connect to API: {e}")
        return False


async def check_blockchain_status() -> Dict[str, Any]:
    """Check blockchain status."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/api/v1/blockchain/status",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"Blockchain status: {data.get('chain_length', 0)} blocks, "
                            f"{data.get('total_transactions', 0)} transactions")
                return data
            return {}
    except Exception as e:
        print_warning(f"Blockchain status check failed: {e}")
        return {}


async def start_analysis(ticker: str, company_name: str) -> Optional[str]:
    """Start an analysis and return the analysis ID."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/analyze",
                json={
                    "ticker": ticker,
                    "company_name": company_name,
                    "include_satellite": False,
                    "include_sentiment": True,
                    "include_supply_chain": True,
                    "debate_rounds": 3,
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("analysis_id")
            else:
                print_error(f"Failed to start analysis: {response.status_code}")
                print_error(f"Response: {response.text[:200]}")
                return None
    except Exception as e:
        print_error(f"Error starting analysis: {e}")
        return None


async def poll_analysis_status(analysis_id: str, verbose: bool = False) -> Optional[Dict[str, Any]]:
    """Poll for analysis status until complete or timeout."""
    start_time = time.time()
    last_status = ""

    async with httpx.AsyncClient() as client:
        while time.time() - start_time < ANALYSIS_TIMEOUT:
            try:
                response = await client.get(
                    f"{API_BASE_URL}/api/v1/analyze/{analysis_id}",
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")

                    if verbose and status != last_status:
                        print_info(f"Status: {status}")
                        last_status = status

                    if status == "completed":
                        # Fetch full results
                        try:
                            results_response = await client.get(
                                f"{API_BASE_URL}/api/v1/analyze/{analysis_id}/results",
                                timeout=10
                            )
                            if results_response.status_code == 200:
                                return results_response.json()
                        except Exception:
                            pass
                        return data.get("results", data)

                    elif status == "failed":
                        print_error(f"Analysis failed: {data.get('error', 'Unknown error')}")
                        return None

                await asyncio.sleep(2)

            except Exception as e:
                if verbose:
                    print_warning(f"Poll error: {e}")
                await asyncio.sleep(2)

    print_error("Analysis timed out")
    return None


def validate_results(ticker: str, results: Dict[str, Any], expected_esg: str) -> Dict[str, bool]:
    """Validate the analysis results."""
    validations = {
        "has_esg_scores": False,
        "has_sdg_impact": False,
        "has_debate": False,
        "esg_in_range": False,
        "agents_completed": False,
    }

    # Check ESG scores
    esg_scores = results.get("esg_scores") or {}
    if not esg_scores:
        # Try alternate structure
        esg_scores = {
            "environmental": results.get("environmental_score", 0),
            "social": results.get("social_score", 0),
            "governance": results.get("governance_score", 0),
            "overall": results.get("overall_score", 0),
        }

    if any(esg_scores.get(k, 0) > 0 for k in ["environmental", "social", "governance", "overall"]):
        validations["has_esg_scores"] = True

    # Check SDG impact
    sdg_impact = results.get("sdg_impact") or results.get("top_sdgs") or []
    if sdg_impact:
        validations["has_sdg_impact"] = True

    # Check debate
    debate = results.get("debate_summary") or results.get("debate_sessions") or []
    if debate:
        validations["has_debate"] = True

    # Check ESG score range (0-100)
    overall = esg_scores.get("overall", 0)
    if 0 <= overall <= 100:
        validations["esg_in_range"] = True

    # Check agents
    agent_reports = results.get("agent_reports") or []
    if len(agent_reports) >= 5:  # At least 5 agents should complete
        validations["agents_completed"] = True
    else:
        # Try alternate structure
        if results.get("orchestrator_summary"):
            validations["agents_completed"] = True

    return validations


async def test_single_company(
    ticker: str,
    company_name: str,
    expected_esg: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Test analysis for a single company."""
    result = {
        "ticker": ticker,
        "company_name": company_name,
        "success": False,
        "duration": 0,
        "scores": {},
        "validations": {},
        "greenwashing_signals": 0,
        "error": None,
    }

    print_info(f"Starting analysis for {ticker} ({company_name})")
    start_time = time.time()

    # Start analysis
    analysis_id = await start_analysis(ticker, company_name)
    if not analysis_id:
        result["error"] = "Failed to start analysis"
        return result

    print_info(f"Analysis ID: {analysis_id}")

    # Poll for results
    results = await poll_analysis_status(analysis_id, verbose)
    duration = time.time() - start_time
    result["duration"] = round(duration, 2)

    if not results:
        result["error"] = "No results received"
        return result

    # Extract scores
    esg_scores = results.get("esg_scores") or {}
    if not esg_scores:
        esg_scores = {
            "environmental": results.get("environmental_score", 0),
            "social": results.get("social_score", 0),
            "governance": results.get("governance_score", 0),
            "overall": results.get("overall_score", 0),
        }
    result["scores"] = esg_scores

    # Count greenwashing signals
    greenwashing = results.get("debate_summary", {}).get("greenwashing_signals", [])
    if not greenwashing:
        greenwashing = results.get("greenwashing_signals", [])
    result["greenwashing_signals"] = len(greenwashing) if greenwashing else 0

    # Validate results
    validations = validate_results(ticker, results, expected_esg)
    result["validations"] = validations
    result["success"] = all(validations.values())

    return result


async def run_all_tests(verbose: bool = False) -> List[Dict[str, Any]]:
    """Run tests for all companies."""
    results = []

    for company in TEST_COMPANIES:
        print_header(f"Testing {company['ticker']}")

        result = await test_single_company(
            company["ticker"],
            company["name"],
            company["expected_esg"],
            verbose
        )
        results.append(result)

        # Print result summary
        if result["success"]:
            print_success(f"{company['ticker']} - Analysis completed successfully")
        else:
            print_error(f"{company['ticker']} - Analysis had issues")

        scores = result["scores"]
        print_info(f"  ESG Scores: E={scores.get('environmental', 0):.1f}, "
                  f"S={scores.get('social', 0):.1f}, G={scores.get('governance', 0):.1f}")
        print_info(f"  Overall: {scores.get('overall', 0):.1f}")
        print_info(f"  Greenwashing Signals: {result['greenwashing_signals']}")
        print_info(f"  Duration: {result['duration']}s")

        # Print validation details
        for check, passed in result["validations"].items():
            if passed:
                print_success(f"  {check}")
            else:
                print_warning(f"  {check}")

        # Small delay between tests
        await asyncio.sleep(2)

    return results


def print_summary(results: List[Dict[str, Any]]):
    """Print test summary."""
    print_header("Test Summary")

    passed = sum(1 for r in results if r["success"])
    total = len(results)

    print(f"\n{Colors.BOLD}Results: {passed}/{total} passed{Colors.RESET}\n")

    # Table header
    print(f"{'Ticker':<8} {'Status':<10} {'E':<6} {'S':<6} {'G':<6} {'Overall':<8} {'GW Signals':<12} {'Time':<8}")
    print("-" * 70)

    for r in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if r["success"] else f"{Colors.RED}FAIL{Colors.RESET}"
        scores = r["scores"]
        print(f"{r['ticker']:<8} {status:<20} "
              f"{scores.get('environmental', 0):<6.1f} "
              f"{scores.get('social', 0):<6.1f} "
              f"{scores.get('governance', 0):<6.1f} "
              f"{scores.get('overall', 0):<8.1f} "
              f"{r['greenwashing_signals']:<12} "
              f"{r['duration']:<8.1f}s")

    # Greenwashing analysis
    print(f"\n{Colors.BOLD}Greenwashing Detection:{Colors.RESET}")
    for r in results:
        if r["greenwashing_signals"] > 0:
            print(f"  {Colors.YELLOW}{r['ticker']}: {r['greenwashing_signals']} signals detected{Colors.RESET}")
        else:
            print(f"  {Colors.GREEN}{r['ticker']}: Clean - no greenwashing signals{Colors.RESET}")


async def main():
    parser = argparse.ArgumentParser(description="GAIA Company Analysis Test Script")
    parser.add_argument("--ticker", help="Test a specific ticker (e.g., AAPL)")
    parser.add_argument("--all", action="store_true", help="Test all 5 demo companies")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--health", action="store_true", help="Only check API health")

    args = parser.parse_args()

    print_header("GAIA Analysis Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API: {API_BASE_URL}")

    # Check API health
    if not await check_health():
        print_error("API is not available. Please start the backend server.")
        sys.exit(1)

    # Check blockchain
    await check_blockchain_status()

    if args.health:
        print_success("Health check complete")
        return

    if args.ticker:
        # Test single ticker
        ticker = args.ticker.upper()
        company = next(
            (c for c in TEST_COMPANIES if c["ticker"] == ticker),
            {"ticker": ticker, "name": f"{ticker} Inc.", "expected_esg": "moderate"}
        )

        result = await test_single_company(
            company["ticker"],
            company["name"],
            company["expected_esg"],
            args.verbose
        )

        print_summary([result])

    elif args.all:
        # Test all companies
        results = await run_all_tests(args.verbose)
        print_summary(results)

    else:
        # Default: test XOM for greenwashing demo
        print_info("Testing XOM (Exxon Mobil) for greenwashing detection demo")
        print_info("Use --all to test all 5 companies, or --ticker AAPL for specific ticker")

        result = await test_single_company(
            "XOM",
            "Exxon Mobil Corporation",
            "moderate",
            args.verbose
        )

        print_summary([result])


if __name__ == "__main__":
    asyncio.run(main())
