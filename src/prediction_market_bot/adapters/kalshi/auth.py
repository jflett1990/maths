from __future__ import annotations

import base64
import os
import time
from dataclasses import dataclass
from typing import Mapping


@dataclass(slots=True)
class KalshiCredentials:
    api_key_id: str
    private_key_pem: str
    passphrase: str | None = None


class MissingKalshiCredentialsError(RuntimeError):
    pass


def load_credentials_from_env(prefix: str = "KALSHI") -> KalshiCredentials:
    api_key = os.getenv(f"{prefix}_API_KEY")
    private_key = os.getenv(f"{prefix}_PRIVATE_KEY")
    passphrase = os.getenv(f"{prefix}_PASSPHRASE")
    if not api_key or not private_key:
        raise MissingKalshiCredentialsError("Missing Kalshi credentials in environment")
    return KalshiCredentials(api_key_id=api_key, private_key_pem=private_key, passphrase=passphrase)


def build_auth_headers(credentials: KalshiCredentials, method: str, path: str, body: str = "") -> Mapping[str, str]:
    """Return header names expected by Kalshi APIs.

    Signature is intentionally a deterministic placeholder in this migration because
    live order/authenticated trading flows are disabled fail-closed.
    """
    ts = str(int(time.time() * 1000))
    signing_payload = f"{ts}{method.upper()}{path}{body}".encode("utf-8")
    signature = base64.b64encode(signing_payload).decode("ascii")
    return {
        "KALSHI-ACCESS-KEY": credentials.api_key_id,
        "KALSHI-ACCESS-SIGNATURE": signature,
        "KALSHI-ACCESS-TIMESTAMP": ts,
    }
