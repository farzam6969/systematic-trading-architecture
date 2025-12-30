"""
INSTITUTIONAL-GRADE BACKTESTING FRAMEWORK
=========================================

A production-quality backtesting and visualization pipeline demonstrating:
- Event-driven signal processing
- GARCH-based regime adaptation
- Session-aware execution filtering  
- Comprehensive trade analytics and charting

NOTE: Signal confirmation logic is proprietary and not included.
      This framework demonstrates backtesting infrastructure only.

Architecture:
    ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
    │  Market Data    │ ──▶ │  Signal Events   │ ──▶ │  Trade Engine   │
    │  (M1 OHLCV)     │     │  (External Feed) │     │  (Execution)    │
    └─────────────────┘     └──────────────────┘     └─────────────────┘
                                    │                        │
                                    ▼                        ▼
                            ┌──────────────────┐     ┌─────────────────┐
                            │  Context Data    │     │  Analytics &    │
                            │  (GARCH, L2, VP) │     │  Visualization  │
                            └──────────────────┘     └─────────────────┘

Output Structure:
    output/
    ├── trades/           (Individual trade charts)
    └── analysis/         (Performance reports & equity curves)
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# CONFIGURATION (Template - Actual values are proprietary)
# ============================================================================

@dataclass
class BacktestConfig:
    """Configuration container for backtest parameters."""
    
    # Time range
    start_date: str = '2025-01-01'
    end_date: str = '2025-12-31'
    
    # Capital management
    initial_capital: float = 100.0
    risk_per_trade: float = 5.0  # Fixed $ risk per trade
    
    # Execution rules
    cooldown_hours: int = 12
    
    # Session filtering (UTC hours)
    allowed_sessions: List[str] = None
    
    # Chart generation
    lookback_days: int = 3
    lookforward_days: int = 3
    
    def __post_init__(self):
        if self.allowed_sessions is None:
            self.allowed_sessions = ["London", "New_York"]


# ============================================================================
# ABSTRACT BASE CLASSES (Define interfaces)
# ============================================================================

class SignalConfirmation(ABC):
    """
    Abstract base class for signal confirmation logic.
    
    Actual implementation is proprietary. This demonstrates the interface
    that confirmation modules must implement.
    """
    
    @abstractmethod
    def confirm_signal(
        self, 
        signal: pd.Series, 
        context: Dict[str, Any],
        price: float
    ) -> bool:
        """
        Determine if a signal should be executed.
        
        Args:
            signal: Signal event data
            context: Market context (GARCH, L2, Volume Profile, etc.)
            price: Current entry price
            
        Returns:
            True if signal is confirmed, False otherwise
        """
        pass
    
    @abstractmethod
    def calculate_confirmation_score(
        self,
        signal: pd.Series,
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate weighted confirmation score.
        
        Returns:
            Score between 0.0 and 1.0
        """
        pass


class RiskCalculator(ABC):
    """Abstract base class for risk calculation."""
    
    @abstractmethod
    def calculate_stops(
        self,
        entry_price: float,
        direction: str,
        volatility: float,
        params: Dict[str, Any]
    ) -> Tuple[float, float]:
        """
        Calculate stop loss and take profit levels.
        
        Returns:
            Tuple of (stop_loss_price, take_profit_price)
        """
        pass


# ============================================================================
# CONCRETE IMPLEMENTATIONS (Framework code - not alpha)
# ============================================================================

class GARCHRegimeRiskCalculator(RiskCalculator):
    """
    GARCH volatility regime-based SL/TP calculator.
    
    Adapts stop distance based on current volatility regime:
    - Low vol: Tighter stops (smaller ATR multiple)
    - Med vol: Baseline stops
    - High vol: Wider stops (larger ATR multiple)
    """
    
    def __init__(
        self,
        low_vol_threshold: float = 25.0,
        high_vol_threshold: float = 35.0,
        sl_low: int = 200,
        sl_med: int = 250,
        sl_high: int = 350,
        reward_risk_ratio: float = 2.0
    ):
        self.low_vol_threshold = low_vol_threshold
        self.high_vol_threshold = high_vol_threshold
        self.sl_low = sl_low
        self.sl_med = sl_med
        self.sl_high = sl_high
        self.rr_ratio = reward_risk_ratio
    
    def get_volatility_regime(self, garch_vol: float) -> str:
        """Classify current volatility regime."""
        if garch_vol < self.low_vol_threshold:
            return "LOW"
        elif garch_vol < self.high_vol_threshold:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def calculate_stops(
        self,
        entry_price: float,
        direction: str,
        garch_vol: float,
        params: Optional[Dict[str, Any]] = None
    ) -> Tuple[float, float]:
        """Calculate regime-adapted SL/TP."""
        
        regime = self.get_volatility_regime(garch_vol)
        
        if regime == "LOW":
            sl_distance = self.sl_low
        elif regime == "MEDIUM":
            sl_distance = self.sl_med
        else:
            sl_distance = self.sl_high
        
        tp_distance = sl_distance * self.rr_ratio
        
        is_long = direction.upper() in ["LONG", "BUY"]
        
        if is_long:
            sl_price = entry_price - sl_distance
            tp_price = entry_price + tp_distance
        else:
            sl_price = entry_price + sl_distance
            tp_price = entry_price - tp_distance
        
        return sl_price, tp_price


# ============================================================================
# DATA LOADERS
# ============================================================================

class DataLoader:
    """
    Unified data loading for backtesting.
    
    Handles:
    - M1 OHLCV price data
    - Signal events (from signal generators)
    - Context data (GARCH, Volume Profile, L2, etc.)
    """
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
    
    def load_price_data(self, filepath: Path) -> pd.DataFrame:
        """
        Load M1 price data with standardized column names.
        
        Returns DataFrame with columns: Open, High, Low, Close, Volume
        Index: DatetimeIndex (UTC)
        """
        print(f'Loading price data from {filepath.name}...')
        
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        df = df.set_index('timestamp')
        
        # Standardize column names
        column_mapping = {
            'open': 'Open', 'high': 'High',
            'low': 'Low', 'close': 'Close',
            'tick_volume': 'Volume', 'volume': 'Volume'
        }
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist
        for col in ['Open', 'High', 'Low']:
            if col not in df.columns:
                df[col] = df['Close']
        if 'Volume' not in df.columns:
            df['Volume'] = 0
        
        print(f'[OK] Loaded {len(df):,} M1 bars')
        print(f'     Range: {df.index.min()} to {df.index.max()}')
        
        return df
    
    def load_signals(self, filepath: Path) -> pd.DataFrame:
        """Load signal events with standardized direction."""
        print(f'Loading signals from {filepath.name}...')
        
        df = pd.read_csv(filepath)
        
        # Handle various timestamp column names
        ts_col = next(
            (c for c in ['timestamp_utc', 'timestamp', 'time'] if c in df.columns),
            None
        )
        if ts_col:
            df['timestamp'] = pd.to_datetime(df[ts_col], utc=True)
        
        # Standardize direction
        df['direction'] = df['direction'].str.upper()
        df.loc[df['direction'] == 'BUY', 'direction'] = 'LONG'
        df.loc[df['direction'] == 'SELL', 'direction'] = 'SHORT'
        
        print(f'[OK] Loaded {len(df)} signals')
        
        return df.sort_values('timestamp')
    
    def load_jsonl_events(
        self, 
        filepath: Path, 
        parser_func: callable
    ) -> pd.DataFrame:
        """
        Load JSONL event data with custom parser.
        
        Args:
            filepath: Path to JSONL file
            parser_func: Function to parse each JSON record
        """
        records = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    rec = json.loads(line.strip())
                    parsed = parser_func(rec)
                    if parsed:
                        records.append(parsed)
                except json.JSONDecodeError:
                    continue
        
        if not records:
            return None
        
        df = pd.DataFrame(records)
        df = df.set_index('timestamp').sort_index()
        
        return df
    
    @staticmethod
    def get_nearest_context(df: pd.DataFrame, timestamp: pd.Timestamp) -> Optional[Dict]:
        """Get nearest context record at or before timestamp."""
        if df is None or len(df) == 0:
            return None
        
        mask = df.index <= timestamp
        if not mask.any():
            return None
        
        return df.loc[mask].iloc[-1].to_dict()


# ============================================================================
# BACKTESTING ENGINE
# ============================================================================

@dataclass
class Trade:
    """Container for trade information."""
    signal_time: pd.Timestamp
    entry_time: pd.Timestamp
    session: str
    direction: str
    entry_price: float
    sl_price: float
    tp_price: float
    exit_type: str  # 'SL', 'TP', 'TIMEOUT'
    exit_time: pd.Timestamp
    exit_price: float
    pnl: float
    r_multiple: float
    equity: float
    garch_vol: float


class BacktestEngine:
    """
    Event-driven backtesting engine.
    
    Processes signals sequentially with:
    - Cooldown enforcement
    - Session filtering
    - Context-aware confirmation (abstracted)
    - Regime-adapted risk management
    """
    
    def __init__(
        self,
        config: BacktestConfig,
        risk_calculator: RiskCalculator,
        confirmation: Optional[SignalConfirmation] = None
    ):
        self.config = config
        self.risk_calculator = risk_calculator
        self.confirmation = confirmation
        
        self.trades: List[Trade] = []
        self.equity_curve: List[Tuple[pd.Timestamp, float]] = []
        self.filter_stats: Dict[str, int] = {}
    
    def get_session(self, timestamp: pd.Timestamp) -> str:
        """Determine trading session from UTC timestamp."""
        hour = timestamp.hour
        
        if 0 <= hour < 8:
            return "Asian"
        elif 8 <= hour < 13:
            return "London"
        elif 13 <= hour < 22:
            return "New_York"
        else:
            return "Off_Hours"
    
    def run_backtest(
        self,
        price_data: pd.DataFrame,
        signals: pd.DataFrame,
        context_data: Dict[str, pd.DataFrame]
    ) -> Tuple[List[Trade], List[Tuple], Dict[str, int]]:
        """
        Execute backtest over signal set.
        
        Args:
            price_data: M1 OHLCV data
            signals: Signal events to process
            context_data: Dict of context DataFrames (garch, vp, etc.)
        
        Returns:
            Tuple of (trades, equity_curve, filter_statistics)
        """
        print('='*80)
        print('RUNNING BACKTEST')
        print('='*80)
        
        # Initialize state
        equity = self.config.initial_capital
        last_trade_time = None
        cooldown_delta = timedelta(hours=self.config.cooldown_hours)
        
        self.trades = []
        self.equity_curve = [(pd.Timestamp(self.config.start_date, tz='UTC'), equity)]
        self.filter_stats = {
            'total_signals': 0,
            'cooldown_blocked': 0,
            'session_blocked': 0,
            'no_entry_bar': 0,
            'no_context': 0,
            'not_confirmed': 0,
            'trades_executed': 0
        }
        
        # Filter signals to date range
        start_ts = pd.Timestamp(self.config.start_date, tz='UTC')
        end_ts = pd.Timestamp(self.config.end_date, tz='UTC')
        signals = signals[
            (signals['timestamp'] >= start_ts) &
            (signals['timestamp'] <= end_ts)
        ]
        
        print(f'Processing {len(signals)} signals...')
        
        for idx, sig in signals.iterrows():
            signal_time = sig['timestamp']
            self.filter_stats['total_signals'] += 1
            
            # 1. Cooldown Check
            if last_trade_time and (signal_time - last_trade_time) < cooldown_delta:
                self.filter_stats['cooldown_blocked'] += 1
                continue
            
            # 2. Session Filter
            session = self.get_session(signal_time)
            if session not in self.config.allowed_sessions:
                self.filter_stats['session_blocked'] += 1
                continue
            
            # 3. Get Entry Bar (next bar open after signal)
            try:
                entry_bar = price_data[price_data.index > signal_time].iloc[0]
                entry_price = entry_bar['Open']
                entry_time = entry_bar.name
            except IndexError:
                self.filter_stats['no_entry_bar'] += 1
                continue
            
            # 4. Load Context
            context = {}
            for ctx_name, ctx_df in context_data.items():
                context[ctx_name] = DataLoader.get_nearest_context(ctx_df, signal_time)
            
            if 'garch' not in context or context['garch'] is None:
                self.filter_stats['no_context'] += 1
                continue
            
            garch_vol = context['garch'].get('vol', 30.0)
            
            # 5. Signal Confirmation (PROPRIETARY - abstracted)
            if self.confirmation:
                if not self.confirmation.confirm_signal(sig, context, entry_price):
                    self.filter_stats['not_confirmed'] += 1
                    continue
            
            # 6. Calculate SL/TP (Regime-adapted)
            direction = sig['direction']
            sl_price, tp_price = self.risk_calculator.calculate_stops(
                entry_price, direction, garch_vol
            )
            
            # 7. Simulate Trade Outcome
            trade_result = self._simulate_trade(
                price_data, entry_time, entry_price,
                direction, sl_price, tp_price
            )
            
            if trade_result:
                exit_type, exit_time, exit_price, r_multiple = trade_result
                pnl = self.config.risk_per_trade * r_multiple
                equity += pnl
                
                trade = Trade(
                    signal_time=signal_time,
                    entry_time=entry_time,
                    session=session,
                    direction=direction,
                    entry_price=entry_price,
                    sl_price=sl_price,
                    tp_price=tp_price,
                    exit_type=exit_type,
                    exit_time=exit_time,
                    exit_price=exit_price,
                    pnl=pnl,
                    r_multiple=r_multiple,
                    equity=equity,
                    garch_vol=garch_vol
                )
                
                self.trades.append(trade)
                self.equity_curve.append((signal_time, equity))
                self.filter_stats['trades_executed'] += 1
                last_trade_time = signal_time
        
        self._print_summary()
        
        return self.trades, self.equity_curve, self.filter_stats
    
    def _simulate_trade(
        self,
        price_data: pd.DataFrame,
        entry_time: pd.Timestamp,
        entry_price: float,
        direction: str,
        sl_price: float,
        tp_price: float,
        max_bars: int = 10080  # 7 days of M1 bars
    ) -> Optional[Tuple[str, pd.Timestamp, float, float]]:
        """
        Simulate trade execution and determine outcome.
        
        Returns:
            Tuple of (exit_type, exit_time, exit_price, r_multiple)
            or None if no outcome within max_bars
        """
        future_bars = price_data[price_data.index > entry_time].iloc[:max_bars]
        is_long = direction.upper() in ["LONG", "BUY"]
        
        for timestamp, bar in future_bars.iterrows():
            if is_long:
                sl_hit = bar['Low'] <= sl_price
                tp_hit = bar['High'] >= tp_price
            else:
                sl_hit = bar['High'] >= sl_price
                tp_hit = bar['Low'] <= tp_price
            
            # Assume worst-case: if both hit in same bar, SL wins
            if sl_hit and tp_hit:
                return ('SL', timestamp, sl_price, -1.0)
            elif sl_hit:
                return ('SL', timestamp, sl_price, -1.0)
            elif tp_hit:
                rr = abs(tp_price - entry_price) / abs(sl_price - entry_price)
                return ('TP', timestamp, tp_price, rr)
        
        return None  # No outcome within timeframe
    
    def _print_summary(self):
        """Print backtest summary statistics."""
        print('\n' + '='*80)
        print('BACKTEST SUMMARY')
        print('='*80)
        
        for key, value in self.filter_stats.items():
            print(f'  {key:25}: {value:,}')
        
        if self.trades:
            total_r = sum(t.r_multiple for t in self.trades)
            wins = sum(1 for t in self.trades if t.r_multiple > 0)
            losses = len(self.trades) - wins
            win_rate = wins / len(self.trades) * 100
            
            print('\n  PERFORMANCE:')
            print(f'  {"Total R":25}: {total_r:+.2f}R')
            print(f'  {"Win Rate":25}: {win_rate:.1f}% ({wins}W / {losses}L)')
            print(f'  {"Final Equity":25}: ${self.equity_curve[-1][1]:.2f}')


# ============================================================================
# ANALYTICS & VISUALIZATION
# ============================================================================

class PerformanceAnalytics:
    """Calculate institutional-grade performance metrics."""
    
    @staticmethod
    def calculate_metrics(trades: List[Trade], initial_capital: float) -> Dict[str, Any]:
        """Calculate comprehensive performance statistics."""
        if not trades:
            return {}
        
        r_multiples = [t.r_multiple for t in trades]
        equity_values = [t.equity for t in trades]
        
        # Basic stats
        total_r = sum(r_multiples)
        wins = sum(1 for r in r_multiples if r > 0)
        losses = len(r_multiples) - wins
        win_rate = wins / len(r_multiples) if r_multiples else 0
        
        # Drawdown analysis
        peak = initial_capital
        max_drawdown = 0
        max_drawdown_pct = 0
        
        for equity in equity_values:
            if equity > peak:
                peak = equity
            drawdown = peak - equity
            drawdown_pct = drawdown / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
            max_drawdown_pct = max(max_drawdown_pct, drawdown_pct)
        
        # Profit factor
        gross_profit = sum(r for r in r_multiples if r > 0)
        gross_loss = abs(sum(r for r in r_multiples if r < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Expectancy: E = (Win% × Avg Win) - (Loss% × Avg Loss)
        avg_win = gross_profit / wins if wins > 0 else 0
        avg_loss = gross_loss / losses if losses > 0 else 0
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        # Sharpe Ratio (using R-multiples as returns)
        # Sharpe = Mean(R) / StdDev(R) * sqrt(N trades per year)
        # Assuming ~250 trading days, estimate trades per year
        if len(r_multiples) >= 2:
            mean_r = np.mean(r_multiples)
            std_r = np.std(r_multiples, ddof=1)
            
            # Calculate trading period in days
            first_trade = trades[0].signal_time
            last_trade = trades[-1].signal_time
            trading_days = (last_trade - first_trade).days or 1
            
            # Annualization factor
            trades_per_year = len(trades) / trading_days * 252
            
            # Sharpe ratio (annualized)
            sharpe_ratio = (mean_r / std_r * np.sqrt(trades_per_year)) if std_r > 0 else 0
        else:
            sharpe_ratio = 0
            mean_r = r_multiples[0] if r_multiples else 0
        
        # Monthly breakdown
        monthly_r = {}
        for trade in trades:
            month = trade.signal_time.strftime('%Y-%m')
            monthly_r[month] = monthly_r.get(month, 0) + trade.r_multiple
        
        return {
            'total_trades': len(trades),
            'total_r': total_r,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct * 100,
            'avg_r_per_trade': total_r / len(trades),
            'expectancy': expectancy,
            'sharpe_ratio': sharpe_ratio,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'monthly_r': monthly_r,
            'final_equity': equity_values[-1] if equity_values else initial_capital
        }
    
    @staticmethod
    def print_report(metrics: Dict[str, Any]):
        """Print formatted performance report."""
        print('\n' + '='*80)
        print('PERFORMANCE REPORT')
        print('='*80)
        
        print(f"\n{'Total Trades:':<30} {metrics.get('total_trades', 0)}")
        print(f"{'Total R-Multiple:':<30} {metrics.get('total_r', 0):+.2f}R")
        print(f"{'Win Rate:':<30} {metrics.get('win_rate', 0)*100:.1f}%")
        print(f"{'Profit Factor:':<30} {metrics.get('profit_factor', 0):.2f}")
        print(f"{'Max Drawdown:':<30} {metrics.get('max_drawdown_pct', 0):.1f}%")
        print(f"{'Average R per Trade:':<30} {metrics.get('avg_r_per_trade', 0):+.3f}R")
        
        # New metrics
        print(f"\n{'--- Risk-Adjusted Metrics ---'}")
        print(f"{'Expectancy:':<30} {metrics.get('expectancy', 0):+.3f}R")
        print(f"{'Sharpe Ratio (Annualized):':<30} {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"{'Average Win:':<30} {metrics.get('avg_win', 0):+.2f}R")
        print(f"{'Average Loss:':<30} {metrics.get('avg_loss', 0):-.2f}R")
        
        print(f"\n{'Final Equity:':<30} ${metrics.get('final_equity', 0):.2f}")
        
        print(f"\n{'Monthly Breakdown:'}")
        for month, r in sorted(metrics.get('monthly_r', {}).items()):
            print(f"  {month}: {r:+.2f}R")


class ChartGenerator:
    """Generate institutional-grade trade and performance charts."""
    
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def create_equity_curve(
        self,
        equity_curve: List[Tuple[pd.Timestamp, float]],
        trades: List[Trade],
        filepath: Path
    ):
        """Generate equity curve with drawdown visualization."""
        if not equity_curve:
            return
        
        timestamps, equities = zip(*equity_curve)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                        gridspec_kw={'height_ratios': [3, 1]})
        
        # Equity curve
        ax1.plot(timestamps, equities, linewidth=2, color='#2E86AB')
        ax1.fill_between(timestamps, equities[0], equities, alpha=0.3, color='#2E86AB')
        ax1.set_ylabel('Equity ($)', fontsize=12)
        ax1.set_title('Equity Curve', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Mark wins and losses
        for trade in trades:
            color = 'green' if trade.r_multiple > 0 else 'red'
            marker = '^' if trade.direction == 'LONG' else 'v'
            ax1.scatter(trade.signal_time, trade.equity, 
                       color=color, marker=marker, s=50, zorder=5)
        
        # Drawdown
        equity_series = pd.Series(equities, index=timestamps)
        rolling_max = equity_series.expanding().max()
        drawdown = (equity_series - rolling_max) / rolling_max * 100
        
        ax2.fill_between(timestamps, 0, drawdown, color='red', alpha=0.5)
        ax2.set_ylabel('Drawdown (%)', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f'[OK] Saved equity curve: {filepath.name}')


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution entry point.
    
    NOTE: This is a framework demonstration. Actual signal confirmation
    logic and parameters are proprietary.
    """
    print('='*80)
    print('INSTITUTIONAL BACKTESTING FRAMEWORK')
    print('='*80)
    print()
    print('This framework demonstrates:')
    print('  - Event-driven signal processing')
    print('  - GARCH-based regime adaptation')
    print('  - Session-aware execution filtering')
    print('  - Comprehensive analytics and charting')
    print()
    print('NOTE: Signal confirmation logic is proprietary.')
    print('      This code shows infrastructure only.')
    print('='*80)
    
    # Configuration (actual values are proprietary)
    config = BacktestConfig(
        start_date='2025-01-01',
        end_date='2025-12-31',
        initial_capital=100.0,
        risk_per_trade=5.0,
        cooldown_hours=12,
        allowed_sessions=["New_York"]
    )
    
    # Risk calculator with regime adaptation
    risk_calc = GARCHRegimeRiskCalculator(
        low_vol_threshold=25.0,
        high_vol_threshold=35.0,
        sl_low=200,
        sl_med=250, 
        sl_high=350,
        reward_risk_ratio=2.0  # Template value
    )
    
    # Initialize engine
    engine = BacktestEngine(
        config=config,
        risk_calculator=risk_calc,
        confirmation=None  # PROPRIETARY: Would inject confirmation here
    )
    
    print('\n[!] To run actual backtest:')
    print('    1. Load price data: loader.load_price_data(path)')
    print('    2. Load signals: loader.load_signals(path)')
    print('    3. Load context: loader.load_jsonl_events(path, parser)')
    print('    4. Run: engine.run_backtest(price, signals, context)')
    print('    5. Analyze: PerformanceAnalytics.calculate_metrics(trades)')


if __name__ == '__main__':
    main()
