import aiohttp
from datetime import datetime, timedelta


class ExchangeRateFetcher:
    API_URL = "https://api.privatbank.ua/p24api/exchange_rates?date={}"

    @staticmethod
    async def get_exchange_rate(days=1):
        current_date = datetime.now()
        exchange_data = []
        async with aiohttp.ClientSession() as session:
            for day in range(days):
                date_str = (current_date - timedelta(days=day)).strftime("%d.%m.%Y")
                url = ExchangeRateFetcher.API_URL.format(date_str)
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        exchange_data.append({
                            date_str: {
                                'USD': ExchangeRateFetcher.extract_currency(data, 'USD'),
                                'EUR': ExchangeRateFetcher.extract_currency(data, 'EUR')
                            }
                        })
        return exchange_data

    @staticmethod
    def extract_currency(data, currency_code):
        for currency in data.get("exchangeRate", []):
            if currency.get("currency") == currency_code:
                return {
                    "sale": currency.get("saleRate", "N/A"),
                    "purchase": currency.get("purchaseRate", "N/A")
                }
        return {"sale": "N/A", "purchase": "N/A"}