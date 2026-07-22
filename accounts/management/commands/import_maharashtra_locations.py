"""
Management command: import_maharashtra_locations

Seeds District, Taluka, and VillageCity records from the official
Maharashtra LGD (Local Government Directory) web services.

Usage:
    python3 manage.py import_maharashtra_locations
    python3 manage.py import_maharashtra_locations --use-live-api
    python3 manage.py import_maharashtra_locations --districts Pune Nashik

Notes:
    - By default this runs against a small static fallback dataset
      (3 sample districts) so the command is testable without
      official LGD API credentials.
    - Pass --use-live-api once LGD_API_BASE_URL / LGD_API_KEY are
      configured in settings, to hit the real government web services
      instead.
    - Safe to re-run: uses update_or_create keyed on name + parent,
      so existing rows are updated (e.g. lgd_code corrections) rather
      than duplicated.
"""

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import State, District, Taluka, VillageCity


# ---------------------------------------------------------------------
# Fallback dataset — used until official LGD API credentials are wired
# up in settings. Covers 3 real districts so the command is verifiable
# end-to-end right now.
# ---------------------------------------------------------------------
FALLBACK_DATA = {
    "Pune": {
        "lgd_code": "521",
        "talukas": {
            "Haveli": {
                "lgd_code": "3811",
                "villages": [
                    {"name": "Wagholi", "lgd_code": "560621"},
                    {"name": "Kesnand", "lgd_code": "560601"},
                    {"name": "Uruli Devachi", "lgd_code": "560640"},
                ],
            },
            "Maval": {
                "lgd_code": "3812",
                "villages": [
                    {"name": "Talegaon Dabhade", "lgd_code": "561201"},
                    {"name": "Kamshet", "lgd_code": "561215"},
                ],
            },
        },
    },
    "Nashik": {
        "lgd_code": "518",
        "talukas": {
            "Niphad": {
                "lgd_code": "3742",
                "villages": [
                    {"name": "Niphad", "lgd_code": "554201"},
                    {"name": "Pimpalgaon Baswant", "lgd_code": "554210"},
                ],
            },
            "Sinnar": {
                "lgd_code": "3744",
                "villages": [
                    {"name": "Sinnar", "lgd_code": "554501"},
                    {"name": "Musalgaon", "lgd_code": "554512"},
                ],
            },
        },
    },
    "Nagpur": {
        "lgd_code": "512",
        "talukas": {
            "Hingna": {
                "lgd_code": "3651",
                "villages": [
                    {"name": "Hingna", "lgd_code": "541201"},
                    {"name": "Wanadongri", "lgd_code": "541209"},
                ],
            },
            "Kamptee": {
                "lgd_code": "3652",
                "villages": [
                    {"name": "Kamptee", "lgd_code": "541301"},
                ],
            },
        },
    },
}


class Command(BaseCommand):
    help = "Seed District/Taluka/VillageCity data from the Maharashtra LGD web services (or fallback dataset)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--use-live-api",
            action="store_true",
            help="Call the real Maharashtra LGD web services instead of the fallback dataset. "
                 "Requires LGD_API_BASE_URL (and LGD_API_KEY, if applicable) in settings.",
        )
        parser.add_argument(
            "--districts",
            nargs="+",
            default=None,
            help="Restrict import to specific district names (default: all in the source).",
        )

    def handle(self, *args, **options):
        use_live_api = options["use_live_api"]
        district_filter = options["districts"]

        state, _ = State.objects.update_or_create(name="Maharashtra")

        if use_live_api:
            base_url = getattr(settings, "LGD_API_BASE_URL", None)
            if not base_url:
                raise CommandError(
                    "LGD_API_BASE_URL is not set in settings. "
                    "Add it (and LGD_API_KEY if required) before using --use-live-api."
                )
            districts_data = self._fetch_live_districts(base_url, district_filter)
        else:
            self.stdout.write(self.style.WARNING(
                "Running against the local fallback dataset (3 sample districts). "
                "Use --use-live-api once official LGD credentials are configured."
            ))
            districts_data = FALLBACK_DATA
            if district_filter:
                districts_data = {
                    name: data for name, data in districts_data.items()
                    if name in district_filter
                }

        districts_created = talukas_created = villages_created = 0

        with transaction.atomic():
            for district_name, district_info in districts_data.items():
                district, created = District.objects.update_or_create(
                    name=district_name,
                    state=state,
                    defaults={"lgd_code": district_info.get("lgd_code", "")},
                )
                districts_created += created

                talukas = district_info.get("talukas", {})
                if use_live_api:
                    talukas = self._fetch_live_talukas(base_url, district)

                for taluka_name, taluka_info in talukas.items():
                    taluka, created = Taluka.objects.update_or_create(
                        name=taluka_name,
                        district=district,
                        defaults={"lgd_code": taluka_info.get("lgd_code", "")},
                    )
                    talukas_created += created

                    villages = taluka_info.get("villages", [])
                    if use_live_api:
                        villages = self._fetch_live_villages(base_url, district, taluka)

                    for village in villages:
                        _, created = VillageCity.objects.update_or_create(
                            name=village["name"],
                            taluka=taluka,
                            defaults={"lgd_code": village.get("lgd_code", "")},
                        )
                        villages_created += created

        self.stdout.write(self.style.SUCCESS(
            f"Done. Districts processed: {len(districts_data)} "
            f"(new: {districts_created}), Talukas new: {talukas_created}, "
            f"Villages/Cities new: {villages_created}."
        ))

    # -----------------------------------------------------------------
    # Live API helpers — wire these up once official LGD credentials
    # are available. Left explicit (not guessed) so nobody assumes a
    # response shape that doesn't match the real service.
    # -----------------------------------------------------------------
    def _fetch_live_districts(self, base_url, district_filter):
        resp = requests.get(f"{base_url}/GetAllDistricts", timeout=15)
        resp.raise_for_status()
        raise CommandError(
            "Live API response parsing for GetAllDistricts is not implemented yet — "
            "map the real response fields once you have LGD API access and docs."
        )

    def _fetch_live_talukas(self, base_url, district):
        resp = requests.get(
            f"{base_url}/GetTalukasOfDistrict",
            params={"district_lgd_code": district.lgd_code},
            timeout=15,
        )
        resp.raise_for_status()
        raise CommandError(
            "Live API response parsing for GetTalukasOfDistrict is not implemented yet."
        )

    def _fetch_live_villages(self, base_url, district, taluka):
        resp = requests.get(
            f"{base_url}/GetVillagesOfDistrictAndTaluka",
            params={
                "district_lgd_code": district.lgd_code,
                "taluka_lgd_code": taluka.lgd_code,
            },
            timeout=15,
        )
        resp.raise_for_status()
        raise CommandError(
            "Live API response parsing for GetVillagesOfDistrictAndTaluka is not implemented yet."
        )
