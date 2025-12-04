from __future__ import annotations

from textwrap import dedent

from .base_tool import BaseTool


class MarketplaceTools(BaseTool):
    """Specialised tooling for marketplace procurement workflows."""

    _SEARCH_PROMPT = dedent(
        """
        You are an elite motorcycle procurement scout.
        Research 2-stroke dirt bikes for sale that match all hard filters.

        Sources to cover (summarise; do not scrape live data): Facebook Marketplace,
        Gumtree, BikeSales, CycleTrader (prefer AU), local dealer classifieds, top Google
        classifieds, motorcycle forums, and local buy/sell groups.

        Hard filters:
        - Category: dirt / motocross / enduro / off-road motorcycle.
        - Engine: 2-stroke only (match 2-stroke, 2 stroke, two stroke, 2T).
        - Displacement: 200–300 cc inclusive.
        - Price: ≤ 10,000 AUD (convert other currencies at current indicative rate).
        - Location: within 500 km of Brisbane, QLD, Australia (lat -27.4698, lon 153.0251).
        - Model year: 2006 or newer.
        - Condition: new or used with preference for listings offering photos/maintenance history.

        Matching logic:
        1. Apply native site filters for price, year, and radius where supported.
        2. Retain listings only when the description explicitly references a 2-stroke indicator
           (2T, 2-stroke, two stroke, etc.) and does not mention 4-stroke, electric, or pit bikes.
        3. Parse or infer cc from title/description using cues such as 250cc, YZ250, KX250, etc.
        4. Normalise prices to AUD before filtering and record original currency.
        5. Estimate distance from Brisbane using the provided coordinates; exclude > 500 km.
        6. Mark fields as incomplete if year or cc missing; attempt inference from model codes.
        7. Remove duplicates (same title, price, seller, timestamp); prefer richer listings.

        Ranking:
        - Order results that pass all filters by distance asc, then price asc, then completeness.
        - Identify the highest priority Top 5 based on the same ordering.
        - Limit the full set to the top 20 matches.

        Output requirements:
        - Return ONLY a JSON object matching this schema:
          {
            "scraped_at": "<ISO 8601 timestamp>",
            "listings": [
              {
                "id": "<site unique id>",
                "title": "<listing title>",
                "price_aud": <numeric>,
                "currency_original": "<currency code>",
                "price_original": <numeric>,
                "year": <int|null>,
                "cc": <int|null>,
                "stroke": "2-stroke",
                "make_model": "<canonical make + model>",
                "location_city": "<city>",
                "location_postcode": "<postcode or null>",
                "distance_km_from_brisbane": <numeric>,
                "condition": "<condition string>",
                "photos_count": <int|null>,
                "seller_name": "<seller display name|null>",
                "seller_type": "<private|dealer|null>",
                "contact_info": "<primary contact info|null>",
                "url": "<direct listing url>",
                "notes": "<short note on inference/completeness>",
                "status": "<complete|incomplete>",
                "priority_rank": <1-based rank|null>
              }
            ],
            "top_5_ids": ["<listing id>", "..."]
          }
        - Each listing must include all keys shown above; use null where data missing.
        - Set `status` to "complete" when year and cc confirmed; otherwise "incomplete".
        - Populate `priority_rank` for listings in the Top 5; use null for others.
        - Ensure `top_5_ids` matches the Top 5 listing ids in priority order.
        - Keep all numeric fields as numbers (no quotes); distances in km with at most one decimal.
        - Do not emit commentary, markdown, or additional text outside the JSON object.
        """
    ).strip()

    def search_motorcycles(self, requirements: str | None = None) -> str:
        """
        Compose and execute the detailed procurement prompt for 2-stroke motorcycles.

        Optional `requirements` lets callers provide user-specific preferences that act as
        soft constraints on top of the hard filters baked into the prompt.
        """
        prompt = self._SEARCH_PROMPT
        if requirements and requirements.strip():
            prompt += (
                "\n\nThe user supplied additional preferences. Treat them as soft constraints "
                "when ranking and annotating the listings:\n"
                f"{requirements.strip()}"
            )

        response = self.model.generate_content(prompt)
        if not response.text:
            raise RuntimeError("Motorcycle search returned an empty response from the model.")
        return response.text.strip()
