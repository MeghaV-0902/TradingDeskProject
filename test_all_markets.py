import numpy as np
import pandas as pd

from selfcheck import find_data_dir, load_bars_and_news, run_measured
from agent_unittest import load_agent

TICKERS = ("VOLT", "ZNTH", "NOVA", "QBIT", "ARIX","BOLM","CYVE","DUNO","ELKA","FENR","GALT","HYMO","IXTA","JURO","")
REGIMES = (
    ("OHLCV-only", True, False),
    ("news-only", False, True),
    ("OHLCV + news", True, True),
)

def main():
    TradingAgent, error = load_agent()
    if TradingAgent is None:
        print("Could not load agent.py:", error)
        return

    results = []
    print("\\n=== ALL FOUR TRAINING MARKETS ===")

    for ticker in TICKERS:
        folder = find_data_dir(ticker)
        if not folder:
            print(f"\\n{ticker}: dataset not found")
            continue

        bars, news = load_bars_and_news(ticker, folder)
        print(f"\\n--- {ticker} ({len(bars)} days) ---")

        for label, use_prices, use_news in REGIMES:
            equity, peak = run_measured(
                TradingAgent, bars, news, use_prices, use_news
            )
            if isinstance(equity, str):
                print(f"{label}: FAILED - {equity}")
                continue

            final_equity = equity[-1]
            return_pct = (final_equity - 10000) / 10000 * 100
            results.append((ticker, label, final_equity, return_pct))
            print(
                f"{label}: equity €{final_equity:.2f} | "
                f"return {return_pct:+.2f}% | peak exposure {peak:.1%}"
            )

    print("\\n=== SUMMARY ===")
    for ticker, label, equity, return_pct in results:
        print(f"{ticker:4} | {label:15} | €{equity:,.2f} | {return_pct:+.2f}%")

if __name__ == "__main__":
    main()
