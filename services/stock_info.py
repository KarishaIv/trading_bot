import yfinance as yf

def format_market_cap(value):
    if not isinstance(value, (int, float)):
        return "Нет данных"
    if value >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f} трлн $"
    elif value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f} млрд $"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f} млн $"
    elif value >= 1_000:
        return f"{value / 1_000:.2f} тыс. $"
    else:
        return f"{value:.2f} $"


def format_dividends(value):
    if isinstance(value, float):
        return f"{value * 100:.2f}%"
    return "Нет данных"


def get_stock_info(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        company_data = {
            "Название": info.get("longName", "Нет данных"),
            "Описание": info.get("longBusinessSummary", "Нет описания"),
            "Сектор": info.get("sector", "Нет данных"),
            "Отрасль": info.get("industry", "Нет данных"),
            "Страна": info.get("country", "Нет данных"),
            "Рыночная капитализация": format_market_cap(info.get("marketCap")),
            "Дивиденды (годовая доходность)": format_dividends(info.get("dividendYield")),
            "Веб-сайт": info.get("website", "Нет данных"),
        }

        description = company_data["Описание"]
        description = ". ".join(description.split(". ")[:3]) + "."

        company_text = f"""
📊 <b>{company_data['Название']}</b>
{description}
🌍 Сектор: {company_data['Сектор']}
🏢 Отрасль: {company_data['Отрасль']}
💰 Рыночная капитализация: {company_data['Рыночная капитализация']}
💵 Дивиденды: {company_data['Дивиденды (годовая доходность)']}
🔗 Веб-сайт: {company_data['Веб-сайт']}
"""
        return company_text

    except Exception:
        return f"Я не нашел общей информации по тикеру {ticker_symbol}."
