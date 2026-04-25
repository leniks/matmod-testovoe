from __future__ import annotations

from typing import Any

import httpx


def _city_candidates(city: str) -> list[str]:
    city = city.strip()
    variants = [city]
    lower = city.lower()
    if lower.endswith("и") and len(city) > 3:
        root = city[:-1]
        variants.extend([root + "ь", root + "я", root + "а"])
    return list(dict.fromkeys(variants))


class ExternalDataService:
    async def get_weather(self, city: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20) as client:
            place: dict[str, Any] | None = None
            for candidate in _city_candidates(city):
                geo_resp = await client.get(
                    "https://geocoding-api.open-meteo.com/v1/search",
                    params={
                        "name": candidate,
                        "count": 1,
                        "language": "ru",
                        "format": "json",
                    },
                )
                geo_resp.raise_for_status()
                geo_data = geo_resp.json()
                results = geo_data.get("results") or []
                if results:
                    place = results[0]
                    break

            if not place:
                return {"ok": False, "error": f"Город '{city}' не найден"}

            weather_resp = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "current": ["temperature_2m", "wind_speed_10m"],
                    "timezone": "auto",
                },
            )
            weather_resp.raise_for_status()
            current = (weather_resp.json() or {}).get("current", {})

        return {
            "ok": True,
            "city": place.get("name", city),
            "country": place.get("country"),
            "temperature_c": current.get("temperature_2m"),
            "wind_kmh": current.get("wind_speed_10m"),
        }

    async def get_fx_rate(self, base: str, target: str) -> dict[str, Any]:
        base = base.upper()
        target = target.upper()

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(f"https://open.er-api.com/v6/latest/{base}")
            resp.raise_for_status()
            data = resp.json()

        rate = (data.get("rates") or {}).get(target)
        if rate is None:
            return {"ok": False, "error": f"Курс {base}->{target} недоступен"}

        return {
            "ok": True,
            "base": base,
            "target": target,
            "rate": rate,
            "date": data.get("time_last_update_utc"),
        }
