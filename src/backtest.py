# src/backtest.py

import bt
import pandas as pd


def create_strategy(name, signal_df, initial_capital=100000):
    """
    Build a bt strategy using Buy/Hold signals from signal_df.
    signal_df must have a datetime index, asset tickers as columns, and signals as values:
    1 = Buy, 0 = Hold, -1 = Sell

    """
    def strategy_logic(target):
        current_weights = signal_df.loc[target.now]
        target.temp['weights'] = current_weights
        return True

    strategy = bt.Strategy(name,
        [
            bt.algos.RunDaily(),
            bt.algos.SelectAll(),
            bt.algos.WeighTarget(strategy_logic),
            bt.algos.Rebalance()
        ]
    )

    return strategy


def run_backtest(price_data, signal_df, strategy_name="AI_Signals_Strategy"):
    """
    Run a backtest with the given price data and signals.
    price_data: pd.DataFrame with datetime index and crypto prices
    signal_df: pd.DataFrame with same shape, containing -1/0/1 signals
    """
    print("[*] Running backtest...")

    price_data = price_data.ffill().bfill()  # handle missing values
    signal_df = signal_df.reindex(price_data.index).ffill().bfill()

    strategy = create_strategy(strategy_name, signal_df)
    portfolio = bt.Backtest(strategy, price_data)

    result = bt.run(portfolio)

    return result


def analyze_backtest(result):
    """
    Display performance summary and return key metrics.
    """
    print("[✓] Backtest complete. Summary:")
    stats = result.stats
    print(stats.to_string())

    metrics = {
        "Total Return (%)": round(stats.loc['total_return'] * 100, 2),
        "Sharpe Ratio": round(stats.loc['daily_sharpe'], 3),
        "Max Drawdown (%)": round(stats.loc['max_drawdown'] * 100, 2),
        "Win Rate (%)": round(stats.loc['win_year'] * 100, 2)
    }

    return metrics
