import logging
from collections.abc import Callable
from typing import Any, cast

import httpx

from config.settings import get_settings

logger = logging.getLogger(__name__)


class EvolutionApiClient:
    """Cliente HTTP para Evolution API (provedor WhatsApp self-hosted).

    Documentação: https://evolution-api.readme.io/
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        settings = get_settings()
        self._base_url = (base_url or settings.WHATSAPP_BASE_URL).rstrip("/")
        self._api_key = api_key or settings.WHATSAPP_API_KEY
        self._instance = settings.WHATSAPP_INSTANCE
        self._http = httpx.AsyncClient(timeout=30)

    async def send_text(self, to: str, text: str) -> dict[str, Any]:
        url = f"{self._base_url}/message/sendText/{self._instance}"
        payload = {
            "number": to,
            "text": text,
            "delay": 1000,
        }
        headers = self._build_headers()
        logger.info("Enviando WhatsApp para %s: %.80s", to, text)
        response = await self._http.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def send_image(self, to: str, image_url: str, caption: str = "") -> dict[str, Any]:
        url = f"{self._base_url}/message/sendMedia/{self._instance}"
        payload = {
            "number": to,
            "mediatype": "image",
            "media": image_url,
            "caption": caption or "",
        }
        headers = self._build_headers()
        response = await self._http.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def send_document(self, to: str, doc_url: str, filename: str) -> dict[str, Any]:
        url = f"{self._base_url}/message/sendMedia/{self._instance}"
        payload = {
            "number": to,
            "mediatype": "document",
            "media": doc_url,
            "fileName": filename,
        }
        headers = self._build_headers()
        response = await self._http.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def mark_read(self, message_id: str) -> dict[str, Any]:
        url = f"{self._base_url}/message/update/{self._instance}"
        payload = {"key": message_id, "read": True}
        headers = self._build_headers()
        response = await self._http.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def instance_status(self) -> dict[str, Any]:
        url = f"{self._base_url}/instance/connectionState/{self._instance}"
        headers = self._build_headers()
        response = await self._http.get(url, headers=headers)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def set_webhook(self, webhook_url: str) -> dict[str, Any]:
        url = f"{self._base_url}/instance/set/{self._instance}"
        payload = {
            "webhook": {"enabled": True, "url": webhook_url, "events": ["messages.upsert"]},
        }
        headers = self._build_headers()
        response = await self._http.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def close(self) -> None:
        await self._http.aclose()

    def _build_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["apiKey"] = self._api_key
        return headers


class FakeWhatsAppClient:
    """Cliente fake para desenvolvimento sem Evolution API."""

    def __init__(self) -> None:
        self._sent: list[dict[str, Any]] = []
        self._on_send: Callable[..., Any] | None = None

    def on_send(self, callback: Callable[..., Any]) -> None:
        self._on_send = callback

    async def send_text(self, to: str, text: str) -> dict[str, Any]:
        msg = {"to": to, "text": text, "status": "sent"}
        self._sent.append(msg)
        logger.info("[FAKE WHATSAPP] Para %s: %s", to, text[:80])
        if self._on_send:
            await self._on_send(to, text)
        return msg

    async def send_image(self, to: str, image_url: str, caption: str = "") -> dict[str, Any]:
        msg = {"to": to, "image_url": image_url, "caption": caption, "status": "sent"}
        self._sent.append(msg)
        return msg

    async def send_document(self, to: str, doc_url: str, filename: str) -> dict[str, Any]:
        msg = {"to": to, "doc_url": doc_url, "filename": filename, "status": "sent"}
        self._sent.append(msg)
        return msg

    async def mark_read(self, message_id: str) -> dict[str, Any]:
        return {"status": "read"}

    async def instance_status(self) -> dict[str, Any]:
        return {"status": "connected", "instance": "fake"}

    async def set_webhook(self, webhook_url: str) -> dict[str, Any]:
        return {"status": "ok", "webhook_url": webhook_url}

    async def close(self) -> None:
        pass
