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
    
def fetch_historical_prices(ticker, start_date, end_date):
    """
    Fetch historical prices for a given stock ticker between specified dates.
    
    Args:
    ticker (str): The stock ticker symbol.
    start_date (str): Start date in 'YYYY-MM-DD' format.
    end_date (str): End date in 'YYYY-MM-DD' format.
    
    Returns:
    DataFrame: Historical prices with date and closing price.
    """
    
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date).sort_values(by='Date', ascending=False)
        return [float(val) for val in data[['Close']]['Close']]
    except Exception as e:
        raise ValueError(f"An error occurred while fetching historical prices for {ticker}: {e}")