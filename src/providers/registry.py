from src.providers.base import (
    BaseProvider,
)

from src.providers.openrouter import (
    OpenRouterProvider,
)

from src.providers.together_ai import (
    TogetherAIProvider,
)

from src.providers.featherless import (
    FeatherlessProvider,
)

from src.config.models import (
    ProviderConfig,
)


_REGISTRY: dict[str, type[BaseProvider]] = {
    "openrouter": OpenRouterProvider,
    "together_ai": TogetherAIProvider,
    "featherless": FeatherlessProvider,
}


def get_provider(
    name: str,
    config: ProviderConfig,
) -> BaseProvider:

    cls = _REGISTRY.get(name)

    if not cls:
        raise ValueError(
            f"Unknown provider: {name!r}. "
            f"Available: {list(_REGISTRY)!r}"
        )

    return cls(config)


def register_provider(
    name: str,
    cls: type[BaseProvider],
) -> None:

    _REGISTRY[name] = cls