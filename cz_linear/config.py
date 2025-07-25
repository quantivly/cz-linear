"""Configuration handling for the cz-linear plugin."""

from __future__ import annotations

import logging
from typing import Any, cast

from commitizen.config.base_config import BaseConfig

from .constants import ISSUE_ID_PATTERN, VERB_MAP
from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class LinearConfig:
    """Configuration handler for Linear plugin settings."""

    def __init__(self, base_config: BaseConfig) -> None:
        """Initialize configuration from Commitizen config.

        Parameters
        ----------
        base_config : BaseConfig
            Base Commitizen configuration
        """
        self.base_config = base_config
        self._custom_verbs: dict[str, str] = {}
        self._issue_pattern: str = ISSUE_ID_PATTERN
        self._load_custom_config()

    def _load_custom_config(self) -> None:
        """Load custom configuration from settings."""
        try:
            # Get custom settings under tool.commitizen.cz_linear
            settings = cast(dict[str, Any], self.base_config.settings)
            cz_settings: dict[str, Any] = settings.get("cz_linear", {})

            # Load custom verbs
            custom_verbs = cz_settings.get("custom_verbs", {})
            if custom_verbs:
                self._validate_custom_verbs(custom_verbs)
                self._custom_verbs = custom_verbs
                logger.debug(f"Loaded {len(custom_verbs)} custom verbs")

            # Load custom issue pattern
            custom_pattern = cz_settings.get("issue_pattern")
            if custom_pattern:
                self._validate_pattern(custom_pattern)
                self._issue_pattern = custom_pattern
                logger.debug(f"Using custom issue pattern: {custom_pattern}")

        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}") from e

    def _validate_custom_verbs(self, verbs: dict[str, str]) -> None:
        """Validate custom verb mappings.

        Parameters
        ----------
        verbs : dict[str, str]
            Custom verb mappings to validate
        """
        valid_increments = {"MAJOR", "MINOR", "PATCH", "NONE"}

        for verb, increment in verbs.items():
            if not isinstance(verb, str) or not verb:
                raise ConfigurationError(f"Invalid verb: {verb}")

            if increment not in valid_increments:
                raise ConfigurationError(
                    f"Invalid increment '{increment}' for verb '{verb}'. "
                    f"Must be one of: {valid_increments}"
                )

    def _validate_pattern(self, pattern: str) -> None:
        """Validate regex pattern.

        Parameters
        ----------
        pattern : str
            Regex pattern to validate
        """
        import re

        try:
            re.compile(pattern)
        except re.error as e:
            raise ConfigurationError(f"Invalid regex pattern: {e}") from e

    @property
    def verb_map(self) -> dict[str, str]:
        """Get combined verb mappings including custom verbs.

        Custom verbs take precedence over built-in verbs, allowing users
        to override default behavior or add new verbs.

        Returns
        -------
        dict[str, str]
            Combined verb mappings with custom verbs taking precedence
        """
        # Custom verbs override default ones
        return {**VERB_MAP, **self._custom_verbs}

    @property
    def issue_pattern(self) -> str:
        """Get the issue ID pattern.

        Returns
        -------
        str
            Issue ID regex pattern
        """
        return self._issue_pattern

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting.

        Parameters
        ----------
        key : str
            Setting key
        default : Any
            Default value if not found

        Returns
        -------
        Any
            Setting value
        """
        settings = cast(dict[str, Any], self.base_config.settings)
        cz_settings: dict[str, Any] = settings.get("cz_linear", {})
        return cz_settings.get(key, default)
