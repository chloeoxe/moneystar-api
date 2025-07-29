import yfinance as yf

def fetch_live_price(ticker):
    """
    Fetch the live price of a stock using yfinance API.
    
    Args:
    ticker (str): The stock ticker symbol (e.g., 'AAPL', 'TSLA').
    
    Returns:
    float: The latest closing price of the stock.
    """
    
    try: 
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d", interval="1m")
    except Exception as e:
        raise ValueError(f"An error occurred while fetching data for {ticker}: {e}")
    
    if not data.empty:
        return float(data['Close'].iloc[-1])
    else:
        raise ValueError("No data returned. Check the ticker symbol or market status.")