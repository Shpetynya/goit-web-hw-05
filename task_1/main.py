import sys
from datetime import datetime, timedelta
import asyncio
import aiohttp
import platform


class HttpError(Exception):
    pass


class ExchangeRateFetcher:
    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates"
    MAX_DAYS = 10

    def __init__(self, days: int):
        if days > self.MAX_DAYS or days < 1:
            raise ValueError(f"Please enter a number of days between 1 and {self.MAX_DAYS}.")
        self.days = days

    async def fetch_exchange_rates(self, date: str):
        """Запит до API для отримання даних на певну дату."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.BASE_URL}?date={date}"
            async with session.get(url) as response:
                if response.status != 200:
                    raise HttpError(f"Error status: {response.status} for {url}")
                data = await response.json()
                return self._extract_rates(data, date)

    @staticmethod
    def _extract_rates(data, date: str):
        """Отримання курсу EUR та USD з даних API."""
        eur_rate = next((rate for rate in data["exchangeRate"] if rate["currency"] == "EUR"), None)
        usd_rate = next((rate for rate in data["exchangeRate"] if rate["currency"] == "USD"), None)

        return {
            date: {
                'EUR': {
                    'sale': eur_rate['saleRate'],
                    'purchase': eur_rate['purchaseRate']
                } if eur_rate else 'Not available',
                'USD': {
                    'sale': usd_rate['saleRate'],
                    'purchase': usd_rate['purchaseRate']
                } if usd_rate else 'Not available',
            }
        }

    async def get_exchange_rates(self):
        """Запит курсів валют за останні кілька днів."""
        tasks = []
        for i in range(self.days):
            date = (datetime.now() - timedelta(days=i)).strftime("%d.%m.%Y")
            tasks.append(self.fetch_exchange_rates(date))

        return await asyncio.gather(*tasks)


async def main(days):
    try:
        fetcher = ExchangeRateFetcher(days)
        exchange_rates = await fetcher.get_exchange_rates()
        print(exchange_rates)
    except HttpError as err:
        print(f"Failed to fetch data: {err}")
    except ValueError as err:
        print(err)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: py main.py <days>")
        sys.exit(1)

    try:
        days = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid integer for the number of days.")
        sys.exit(1)

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main(days))
