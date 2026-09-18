"""Provider endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from kernellab.providers.registry import ProviderRegistry, get_provider_registry
from kernellab.schemas.provider import (
    ProviderCapabilitiesSchema,
    ProviderListResponse,
    ProviderResponse,
)

router = APIRouter(prefix="/providers", tags=["providers"])


def _get_registry() -> ProviderRegistry:
    return get_provider_registry()


def _build_provider_response(
    registry: ProviderRegistry, name: str
) -> ProviderResponse:
    info = registry.get_provider_info(name)
    try:
        provider = registry.get(name)
        caps = provider.capabilities() if hasattr(provider, "capabilities") else None
    except Exception:
        caps = None

    cap_schema = None
    if caps is not None:
        cap_schema = ProviderCapabilitiesSchema(
            create=caps.create,
            start=caps.start,
            stop=caps.stop,
            destroy=caps.destroy,
            serial=caps.serial,
            snapshots=caps.snapshots,
            guest_exec=caps.guest_exec,
        )

    return ProviderResponse(
        name=name,
        available=info.available,
        version=info.version,
        executable=info.executable,
        host_info=info.host_info,
        capabilities=cap_schema,
    )


@router.get("", response_model=ProviderListResponse)
async def list_providers(
    registry: Annotated[ProviderRegistry, Depends(_get_registry)],
) -> ProviderListResponse:
    """List all registered providers with availability."""
    providers = []
    for name in registry.list_providers():
        try:
            response = _build_provider_response(registry, name)
            providers.append(response)
        except Exception:
            continue
    return ProviderListResponse(items=providers, total=len(providers))


@router.get("/{name}", response_model=ProviderResponse)
async def get_provider(
    name: str,
    registry: Annotated[ProviderRegistry, Depends(_get_registry)],
) -> ProviderResponse:
    """Get provider details and capabilities."""
    try:
        return _build_provider_response(registry, name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Provider '{name}' not found") from None
    except Exception:
        raise HTTPException(
            status_code=500, detail=f"Failed to query provider '{name}'"
        ) from None
