"""api/serialization - ORJSON low-latency serialization helpers."""
from __future__ import annotations

from typing import Any

import orjson
from fastapi.responses import Response


def dumps(obj: Any) -> bytes:
    return orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY if hasattr(orjson, "OPT_SERIALIZE_NUMPY") else 0)


class ORJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson.dumps(content, default=str)
