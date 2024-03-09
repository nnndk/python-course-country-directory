"""
Функции для формирования выходной информации.
"""

import datetime as dt
from decimal import ROUND_HALF_UP, Decimal

from collectors.models import LocationInfoDTO


class Renderer:
    """
    Генерация результата преобразования прочитанных данных.
    """

    def __init__(self, location_info: LocationInfoDTO) -> None:
        """
        Конструктор.

        :param location_info: Данные о географическом месте.
        """

        self.location_info = location_info

    async def render(self) -> tuple[str, ...]:
        """
        Форматирование прочитанных данных.

        :return: Результат форматирования
        """
        time_with_timezone = (
            self.location_info.weather.dt + self.location_info.weather.timezone
        )

        country_part = {
            "Страна": f"{self.location_info.location.name}",
            "Регион": f"{self.location_info.location.subregion}",
            "Площадь страны": f"{self.location_info.location.area} км²",
            "Языки": f"{await self._format_languages()}",
            "Население страны": f"{await self._format_population()} чел.",
            "Курсы валют": f"{await self._format_currency_rates()}",
        }

        capital_part = {
            "Столица": f"{self.location_info.location.capital}",
            "Широта столицы": f"{self.location_info.location.capital_latitude}",
            "Долгота столицы": f"{self.location_info.location.capital_longitude}",
            "Погода в столице": f"{self.location_info.weather.temp} °C",
            "Описание погоды в столице": f"{self.location_info.weather.description}",
            "Скорость ветра в столице": f"{self.location_info.weather.wind_speed} м/с",
            "Видимость в столице": f"{self.location_info.weather.visibility} м",
            "Часовой пояс столицы": f"{await self._format_timezone()}",
            "Время в столице": f"{dt.datetime.fromtimestamp(time_with_timezone)}",
        }

        max_key_length, max_val_length = 0, 0

        for key, val in country_part.items():
            max_key_length = max(max_key_length, len(key))
            max_val_length = max(max_val_length, len(val))

        for key, val in capital_part.items():
            max_key_length = max(max_key_length, len(key))
            max_val_length = max(max_val_length, len(val))

        country_part_header, capital_part_header = (
            "Информация о стране",
            "Информация о столице",
        )
        result = [
            "_" * (max_key_length + max_val_length + 9) + "\n",
            "| "
            + country_part_header
            + " " * (max_key_length + max_val_length + 5 - len(country_part_header))
            + " |\n",
            "|" + "-" * (max_key_length + max_val_length + 7) + "|\n",
        ]

        for key, val in country_part.items():
            result.append(
                "| "
                + key
                + " " * (max_key_length - len(key))
                + " | "
                + val
                + " " * (max_val_length - len(val) + 2)
                + " |\n"
            )
            result.append("|" + "-" * (max_key_length + max_val_length + 7) + "|\n")

        result.append(
            "| "
            + capital_part_header
            + " " * (max_key_length + max_val_length + 5 - len(capital_part_header))
            + " |\n"
        )
        result.append("|" + "-" * (max_key_length + max_val_length + 7) + "|\n")

        for key, val in capital_part.items():
            result.append(
                "| "
                + key
                + " " * (max_key_length - len(key))
                + " | "
                + val
                + " " * (max_val_length - len(val) + 2)
                + " |\n"
            )
            result.append("|" + "-" * (max_key_length + max_val_length + 7) + "|\n")

        result.append(f"\n\n{await self._format_news()}")

        return tuple(result)

    async def _format_languages(self) -> str:
        """
        Форматирование информации о языках.

        :return:
        """

        return ", ".join(
            f"{item.name} ({item.native_name})"
            for item in self.location_info.location.languages
        )

    async def _format_population(self) -> str:
        """
        Форматирование информации о населении.

        :return:
        """

        # pylint: disable=C0209
        return "{:,}".format(self.location_info.location.population).replace(",", ".")

    async def _format_currency_rates(self) -> str:
        """
        Форматирование информации о курсах валют.

        :return:
        """

        return ", ".join(
            f"{currency} = {Decimal(rates).quantize(exp=Decimal('.01'), rounding=ROUND_HALF_UP)} руб."
            for currency, rates in self.location_info.currency_rates.items()
        )

    async def _format_timezone(self) -> str:
        """
        Форматирование информации о часовом поясе.

        :return:
        """

        base = "UTC"

        if self.location_info.weather.timezone >= 0:
            base += "+"

        return base + f"{self.location_info.weather.timezone // 3600}"

    async def _format_news(self) -> str:
        """
        Форматирование информации о новостях.

        :return:
        """

        result = "Новости по данной стране\n"

        for news_item in self.location_info.news:
            result += f"{news_item.title}\n{news_item.description}\n{news_item.url}\n{news_item.published_at}\n\n"

        return result
