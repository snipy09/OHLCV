"""
Streamlit dashboard for OHLCV Data Validation & Monitoring System

A professional web interface for exploring and analyzing OHLCV market data
with real-time technical indicators, data quality metrics, and interactive charts.
"""

# Configure Python path FIRST - before any imports from src modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Now import from src modules
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from loguru import logger
from storage import OHLCVStorage
from utils import setup_logger, calculate_data_quality_score, get_quality_rating
from config import DEFAULT_TICKERS

# Import external packages


# Page configuration
st.set_page_config(
    page_title="OHLCV Monitoring Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
/* Main layout */
.main { 
    background-color: #f9fafb;
    padding-top: 2rem;
}

/* Typography */
h1 { 
    color: #1e3a8a; 
    font-weight: 700;
    margin-bottom: 0.5rem;
    font-size: 2.5rem;
}

h2 { 
    color: #1e40af; 
    font-weight: 600;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

h3 { 
    color: #1e40af; 
    font-weight: 600;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}

/* Metrics cards */
[data-testid="metric-container"] {
    background-color: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] button {
    font-size: 1rem;
    font-weight: 600;
    color: #4b5563;
    border-bottom: 2px solid transparent;
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #1e40af;
    border-bottom-color: #1e40af;
}

/* Info boxes */
.stAlert {
    border-radius: 0.5rem;
    padding: 1rem;
}

/* Dataframe styling */
[data-testid="stDataFrame"] {
    border-radius: 0.5rem;
    overflow: hidden;
}

/* Sidebar */
.css-1d391kg {
    background-color: #f3f4f6;
}

/* Radio and select buttons */
.stRadio > label, .stSelectbox > label {
    font-weight: 600;
    color: #1e3a8a;
}

/* Dividers */
hr {
    border-color: #e5e7eb;
    margin: 1.5rem 0;
}

/* Subtitles and descriptions */
.stMarkdown > div {
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

# Setup logging
setup_logger()


def setup_page():
    """Setup page title and styling"""
    st.title("OHLCV Data Validation & Monitoring System")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Professional Market Data Analysis Dashboard**")
        st.markdown(
            "Explore validated OHLCV data with technical indicators and quality metrics")
    with col2:
        st.metric("System Status", "OPERATIONAL", delta="Live")

    st.divider()


def load_data(ticker: str) -> dict:
    """Load raw and clean data for ticker"""
    storage = OHLCVStorage()
    raw_data = storage.load_raw(ticker)
    clean_data = storage.load_clean(ticker)
    return {
        'raw': raw_data,
        'clean': clean_data
    }


def calculate_bollinger_bands(data: pd.DataFrame, window: int = 20, num_std: float = 2) -> dict:
    """Calculate Bollinger Bands"""
    data_copy = data.copy()
    data_copy['SMA'] = data_copy['close'].rolling(window=window).mean()
    data_copy['STD'] = data_copy['close'].rolling(window=window).std()
    data_copy['BB_Upper'] = data_copy['SMA'] + (data_copy['STD'] * num_std)
    data_copy['BB_Lower'] = data_copy['SMA'] - (data_copy['STD'] * num_std)
    return data_copy


def calculate_rsi(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def create_professional_candlestick_chart(data: pd.DataFrame, title: str, data_type: str) -> go.Figure:
    """Create professional candlestick chart with Bollinger Bands and MA"""

    # Calculate indicators
    data_copy = calculate_bollinger_bands(data, window=20, num_std=2)
    data_copy['MA20'] = data_copy['close'].rolling(window=20).mean()
    data_copy['MA50'] = data_copy['close'].rolling(window=50).mean()

    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.75, 0.25],
        subplot_titles=(
            f"{title} - Price Action with Bollinger Bands", "Volume"),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )

    # Add candlestick
    fig.add_trace(
        go.Candlestick(
            x=data_copy.index,
            open=data_copy['open'],
            high=data_copy['high'],
            low=data_copy['low'],
            close=data_copy['close'],
            name='OHLC',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef553b',
            showlegend=True
        ),
        row=1, col=1
    )

    # Add Bollinger Band Upper
    fig.add_trace(
        go.Scatter(
            x=data_copy.index,
            y=data_copy['BB_Upper'],
            name='BB Upper',
            line=dict(color='rgba(255, 127, 14, 0.5)', width=1, dash='dash'),
            showlegend=True
        ),
        row=1, col=1
    )

    # Add Bollinger Band Middle (SMA20)
    fig.add_trace(
        go.Scatter(
            x=data_copy.index,
            y=data_copy['SMA'],
            name='BB Middle (SMA20)',
            line=dict(color='#1f77b4', width=2),
            showlegend=True
        ),
        row=1, col=1
    )

    # Add Bollinger Band Lower
    fig.add_trace(
        go.Scatter(
            x=data_copy.index,
            y=data_copy['BB_Lower'],
            name='BB Lower',
            line=dict(color='rgba(255, 127, 14, 0.5)', width=1, dash='dash'),
            showlegend=True,
            fill='tonexty'
        ),
        row=1, col=1
    )

    # Add 50-day moving average
    fig.add_trace(
        go.Scatter(
            x=data_copy.index,
            y=data_copy['MA50'],
            name='MA50',
            line=dict(color='#2ca02c', width=2),
            showlegend=True
        ),
        row=1, col=1
    )

    # Add volume bars with gradient colors
    colors = ['#26a69a' if data_copy['close'].iloc[i] >= data_copy['open'].iloc[i] else '#ef553b'
              for i in range(len(data_copy))]

    fig.add_trace(
        go.Bar(
            x=data_copy.index,
            y=data_copy['volume'],
            marker=dict(color=colors),
            name='Volume',
            showlegend=True
        ),
        row=2, col=1
    )

    # Add outlier markers if they exist and data type is clean
    if data_type == "Clean Data" and 'is_outlier' in data_copy.columns:
        outliers = data_copy[data_copy['is_outlier'] == True]
        if not outliers.empty:
            fig.add_trace(
                go.Scatter(
                    x=outliers.index,
                    y=outliers['close'],
                    mode='markers',
                    marker=dict(size=10, color='red', symbol='diamond',
                                line=dict(width=2, color='darkred')),
                    name='Outliers Flagged',
                    showlegend=True
                ),
                row=1, col=1
            )

    # Update axes
    fig.update_xaxes(title_text="Date", row=2, col=1, gridcolor='#e5e5e5')
    fig.update_yaxes(title_text="Price (USD)", row=1,
                     col=1, gridcolor='#e5e5e5')
    fig.update_yaxes(title_text="Volume", row=2, col=1, gridcolor='#e5e5e5')

    # Update layout
    fig.update_layout(
        height=800,
        hovermode='x unified',
        template='plotly_white',
        font=dict(size=11, family='Arial'),
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        margin=dict(l=50, r=50, t=80, b=50)
    )

    return fig


def create_enhanced_volume_chart(data: pd.DataFrame) -> go.Figure:
    """Create enhanced volume analysis chart"""

    data_copy = data.copy()
    vol_ma20 = data_copy['volume'].rolling(window=20).mean()
    vol_ma50 = data_copy['volume'].rolling(window=50).mean()

    fig = go.Figure()

    # Volume bars
    colors = ['#26a69a' if data_copy['close'].iloc[i] >= data_copy['open'].iloc[i] else '#ef553b'
              for i in range(len(data_copy))]

    fig.add_trace(go.Bar(
        x=data_copy.index,
        y=data_copy['volume'],
        marker=dict(color=colors, opacity=0.7),
        name='Volume',
        hovertemplate='<b>%{x}</b><br>Volume: %{y:,.0f}<extra></extra>'
    ))

    # MA20
    fig.add_trace(go.Scatter(
        x=data_copy.index,
        y=vol_ma20,
        name='MA20',
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>%{x}</b><br>MA20: %{y:,.0f}<extra></extra>'
    ))

    # MA50
    fig.add_trace(go.Scatter(
        x=data_copy.index,
        y=vol_ma50,
        name='MA50',
        line=dict(color='#2ca02c', width=2, dash='dash'),
        hovertemplate='<b>%{x}</b><br>MA50: %{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='Volume Analysis with Moving Averages',
        yaxis_title='Volume',
        xaxis_title='Date',
        height=500,
        hovermode='x unified',
        template='plotly_white',
        plot_bgcolor='#f8f9fa',
        font=dict(size=11),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    return fig


def create_rsi_chart(data: pd.DataFrame) -> go.Figure:
    """Create RSI (Relative Strength Index) chart"""

    data_copy = data.copy()
    data_copy['RSI'] = calculate_rsi(data_copy, window=14)

    fig = go.Figure()

    # RSI line
    fig.add_trace(go.Scatter(
        x=data_copy.index,
        y=data_copy['RSI'],
        name='RSI (14)',
        line=dict(color='#d62728', width=2),
        hovertemplate='<b>%{x}</b><br>RSI: %{y:.2f}<extra></extra>'
    ))

    # Overbought line (70)
    fig.add_hline(y=70, line_dash="dash", line_color="red",
                  annotation_text="Overbought (70)", annotation_position="right")

    # Oversold line (30)
    fig.add_hline(y=30, line_dash="dash", line_color="green",
                  annotation_text="Oversold (30)", annotation_position="right")

    # Neutral line (50)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.5)

    fig.update_layout(
        title='Relative Strength Index (RSI)',
        yaxis_title='RSI',
        xaxis_title='Date',
        height=400,
        hovermode='x unified',
        template='plotly_white',
        plot_bgcolor='#f8f9fa',
        font=dict(size=11),
        yaxis=dict(range=[0, 100]),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    return fig


def create_price_comparison_chart(data: pd.DataFrame) -> go.Figure:
    """Create price comparison chart with high/low bands"""

    data_copy = data.copy()

    fig = go.Figure()

    # High/Low band
    fig.add_trace(go.Scatter(
        x=data_copy.index,
        y=data_copy['high'],
        name='High',
        line=dict(color='rgba(38, 166, 154, 0)'),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=data_copy.index,
        y=data_copy['low'],
        name='High-Low Range',
        line=dict(color='rgba(38, 166, 154, 0)'),
        fillcolor='rgba(38, 166, 154, 0.2)',
        fill='tonexty'
    ))

    # Close price
    fig.add_trace(go.Scatter(
        x=data_copy.index,
        y=data_copy['close'],
        name='Close Price',
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>%{x}</b><br>Close: $%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='Price Trend with High-Low Range',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        height=400,
        hovermode='x unified',
        template='plotly_white',
        plot_bgcolor='#f8f9fa',
        font=dict(size=11),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    return fig


def display_metrics(ticker: str, data: pd.DataFrame, data_type: str):
    """Display key metrics"""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        latest_close = data['close'].iloc[-1]
        st.metric("Latest Close", f"${latest_close:.2f}",
                  "▼" if latest_close < data['close'].iloc[0] else "▲")

    with col2:
        price_change = data['close'].iloc[-1] - data['close'].iloc[0]
        pct_change = (price_change / data['close'].iloc[0]) * 100
        st.metric("Period Change",
                  f"${price_change:.2f}", f"{pct_change:+.2f}%")

    with col3:
        high_price = data['high'].max()
        low_price = data['low'].min()
        st.metric("52-Week Range",
                  f"${high_price - low_price:.2f}", f"High: ${high_price:.2f}")

    with col4:
        avg_volume = data['volume'].mean()
        st.metric("Avg Volume", f"{avg_volume/1e6:.2f}M")

    with col5:
        volatility = data['close'].pct_change().std() * 100
        st.metric("Volatility", f"{volatility:.2f}%",
                  "High" if volatility > 3 else "Normal")


def display_quality_panel(data: pd.DataFrame, data_type: str):
    """Display data quality information"""
    if data is None or data.empty:
        st.warning("No data available")
        return

    quality_score = calculate_data_quality_score(data, [])
    quality_rating = get_quality_rating(quality_score)

    # Color-code the quality score
    if quality_score >= 90:
        score_color = "🟢"
        rating_desc = "Excellent data quality - Ready for analysis"
    elif quality_score >= 75:
        score_color = "🟡"
        rating_desc = "Good data quality - Minor issues detected"
    elif quality_score >= 50:
        score_color = "🟠"
        rating_desc = "Fair data quality - Review recommended"
    else:
        score_color = "🔴"
        rating_desc = "Poor data quality - Clean data recommended"

    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Quality Score",
                  f"{quality_score:.1f}/100", delta=score_color)

    with col2:
        st.metric("Rating", quality_rating)

    with col3:
        if 'is_outlier' in data.columns:
            outlier_count = int(data['is_outlier'].sum())
            st.metric("Anomalies", outlier_count,
                      delta="Flagged" if outlier_count > 0 else "None")
        else:
            st.metric("Anomalies", 0)

    with col4:
        null_count = data.isnull().sum().sum()
        st.metric("Data Gaps", null_count,
                  delta="Missing" if null_count > 0 else "Clean")

    with col5:
        record_count = len(data)
        st.metric("Records", record_count, delta=f"{len(data)} rows")

    # Show detailed info
    st.info(f"{score_color} {rating_desc}")

    # Date range info
    date_min = data.index.min().date()
    date_max = data.index.max().date()
    days_span = (data.index.max() - data.index.min()).days

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Date Range Start", str(date_min))
    with col2:
        st.metric("Date Range End", str(date_max))
    with col3:
        st.metric("Days Covered", f"{days_span} days")

    st.divider()


# Main App Execution
def main():
    """Main application"""
    setup_page()

    # Sidebar configuration
    with st.sidebar:
        st.title("⚙️ Configuration")

        # Ticker selection
        ticker = st.selectbox(
            "📈 Select Ticker",
            DEFAULT_TICKERS,
            key='ticker_select',
            help="Choose which ticker to analyze"
        )

        # Data type selection
        data_type = st.radio(
            "Data Source",
            ["Clean Data", "Raw Data"],
            key='data_type_radio',
            help="Clean: Validated & processed | Raw: Unprocessed market data"
        )

        st.divider()

        # Information section
        st.markdown("## Information")
        with st.expander("Data Quality Legend", expanded=False):
            st.markdown("""
- **Clean Data**: Validated, deduplicated, outliers flagged, corporate actions processed
- **Raw Data**: Direct from yfinance, no processing applied
            """)

        with st.expander("Technical Indicators", expanded=False):
            st.markdown("""
- **Bollinger Bands**: Volatility measure (±2σ)
- **MA20/MA50**: 20 & 50-day moving averages
- **RSI(14)**: Momentum indicator (0-100)
- **Volume MA**: Volume trends
            """)

        st.divider()

        # System status
        st.markdown("## System Status")
        st.markdown("✅ **Status**: Operational")
        st.markdown("📊 **Data Source**: Yahoo Finance")
        st.markdown("💾 **Database**: SQLite")

    # Load data
    all_data = load_data(ticker)

    # Select data based on radio button
    if data_type == "Clean Data":
        data = all_data['clean']
        subtitle = "Clean OHLCV Data (Validated & Processed)"
    else:
        data = all_data['raw']
        subtitle = "Raw OHLCV Data (Unprocessed)"

    # Check if data exists
    if data is None or data.empty:
        st.error(
            f"No {data_type.lower()} found for {ticker}. Please run the pipeline first.")
        return

    # Display header
    st.subheader(f"{ticker} - {subtitle}")
    st.markdown("---")

    # Display metrics
    display_metrics(ticker, data, data_type)

    # Display quality panel
    st.markdown("### Data Quality Assessment")
    display_quality_panel(data, data_type)

    st.markdown("---")

    # Display charts in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Price Chart", "Volume", "RSI Indicator", "Price Trend", "Statistics"])

    with tab1:
        chart = create_professional_candlestick_chart(
            data, f"{ticker} Price Action", data_type)
        st.plotly_chart(chart, use_container_width=True)

    with tab2:
        vol_chart = create_enhanced_volume_chart(data)
        st.plotly_chart(vol_chart, use_container_width=True)

    with tab3:
        rsi_chart = create_rsi_chart(data)
        st.plotly_chart(rsi_chart, use_container_width=True)

    with tab4:
        price_chart = create_price_comparison_chart(data)
        st.plotly_chart(price_chart, use_container_width=True)

    with tab5:
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Price Statistics**")
            price_stats = data[['open', 'high',
                                'low', 'close']].describe().round(2)
            st.dataframe(price_stats, use_container_width=True)

        with col2:
            st.write("**Volume Statistics**")
            vol_stats = data[['volume']].describe().round(0)
            st.dataframe(vol_stats, use_container_width=True)

    # Display data table
    st.markdown("---")
    st.markdown("### Raw Data")
    st.dataframe(data.sort_index(ascending=False), use_container_width=True)


if __name__ == "__main__":
    main()
