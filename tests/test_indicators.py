
import pandas as pd
from services.technical_indicators.calculate_indicators import calculate_indicators

def test_calculate_indicators_on_data():
    data = {
        'Close': [100 + i for i in range(30)],
        'Open': [100 + i for i in range(30)],
        'High': [101 + i for i in range(30)],
        'Low': [99 + i for i in range(30)]
    }
    df = pd.DataFrame(data)
    df = calculate_indicators(df)
    assert 'SMA10' in df.columns
    assert 'RSI' in df.columns
    assert not df['RSI'].isnull().all()
