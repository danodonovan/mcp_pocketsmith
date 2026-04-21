"""Tests for READ_ONLY mode — write tools must be absent when enabled."""

from unittest.mock import MagicMock, patch

import pytest

from pocketsmith_mcp.server import create_server


WRITE_TOOLS = [
    "update_account",
    "delete_account",
    "create_attachment",
    "update_attachment",
    "delete_attachment",
    "clear_forecast_cache",
    "bulk_update_transactions",
    "create_category",
    "update_category",
    "delete_category",
    "create_event",
    "update_event",
    "delete_event",
    "create_institution",
    "update_institution",
    "delete_institution",
    "update_transaction_account",
    "create_transaction",
    "update_transaction",
    "delete_transaction",
    "update_user",
]

READ_TOOLS = [
    "get_current_user",
    "get_user",
    "list_accounts",
    "get_account",
    "list_transaction_accounts",
    "get_transaction_account",
    "list_transactions",
    "get_transaction",
    "list_categories",
    "get_category",
    "get_budget",
    "get_budget_summary",
    "get_trend_analysis",
    "list_institutions",
    "get_institution",
    "list_events",
    "get_event",
    "list_attachments",
    "get_attachment",
    "list_labels",
    "list_saved_searches",
    "list_currencies",
    "list_time_zones",
]


def _mock_config(**overrides: object) -> MagicMock:
    defaults = {
        "api_key": "test_key",
        "api_timeout": 30.0,
        "max_retries": 3,
        "rate_limit_per_minute": 60,
        "read_only": False,
    }
    defaults.update(overrides)
    return MagicMock(**defaults)


def _tool_names(server: object) -> list[str]:
    return list(server._tool_manager._tools.keys())  # type: ignore[union-attr]


class TestReadOnlyMode:
    """Write tools must not be registered when read_only=True."""

    def test_write_tools_absent_in_read_only_mode(self) -> None:
        with patch("pocketsmith_mcp.server.get_config") as mock_config:
            mock_config.return_value = _mock_config(read_only=True)
            server = create_server()

        names = _tool_names(server)
        for tool in WRITE_TOOLS:
            assert tool not in names, f"Write tool '{tool}' should not be registered in read-only mode"

    def test_read_tools_present_in_read_only_mode(self) -> None:
        with patch("pocketsmith_mcp.server.get_config") as mock_config:
            mock_config.return_value = _mock_config(read_only=True)
            server = create_server()

        names = _tool_names(server)
        for tool in READ_TOOLS:
            assert tool in names, f"Read tool '{tool}' should be registered in read-only mode"

    def test_read_only_tool_count(self) -> None:
        with patch("pocketsmith_mcp.server.get_config") as mock_config:
            mock_config.return_value = _mock_config(read_only=True)
            server = create_server()

        names = _tool_names(server)
        assert len(names) == len(READ_TOOLS), (
            f"Expected {len(READ_TOOLS)} tools in read-only mode, got {len(names)}: {names}"
        )

    def test_all_tools_present_in_default_mode(self) -> None:
        with patch("pocketsmith_mcp.server.get_config") as mock_config:
            mock_config.return_value = _mock_config(read_only=False)
            server = create_server()

        names = _tool_names(server)
        for tool in WRITE_TOOLS + READ_TOOLS:
            assert tool in names, f"Tool '{tool}' should be registered in default mode"

    def test_full_tool_count_in_default_mode(self) -> None:
        with patch("pocketsmith_mcp.server.get_config") as mock_config:
            mock_config.return_value = _mock_config(read_only=False)
            server = create_server()

        names = _tool_names(server)
        assert len(names) == 44, f"Expected 44 tools in default mode, got {len(names)}"


class TestReadOnlyConfig:
    """Config correctly reads READ_ONLY env var."""

    def test_read_only_false_by_default(self) -> None:
        import os
        from pocketsmith_mcp.config import Config, reset_config

        reset_config()
        env = {"POCKETSMITH_API_KEY": "test_key_1234567890"}
        with patch.dict(os.environ, env, clear=False):
            # Ensure READ_ONLY is not set
            os.environ.pop("READ_ONLY", None)
            config = Config.from_env()
        assert config.read_only is False

    def test_read_only_true_when_env_set(self) -> None:
        import os
        from pocketsmith_mcp.config import Config, reset_config

        reset_config()
        env = {"POCKETSMITH_API_KEY": "test_key_1234567890", "READ_ONLY": "true"}
        with patch.dict(os.environ, env, clear=False):
            config = Config.from_env()
        assert config.read_only is True

    def test_read_only_case_insensitive(self) -> None:
        import os
        from pocketsmith_mcp.config import Config, reset_config

        reset_config()
        for value in ("TRUE", "True", "true"):
            env = {"POCKETSMITH_API_KEY": "test_key_1234567890", "READ_ONLY": value}
            with patch.dict(os.environ, env, clear=False):
                config = Config.from_env()
            assert config.read_only is True, f"Expected read_only=True for READ_ONLY={value!r}"

    def test_read_only_false_for_other_values(self) -> None:
        import os
        from pocketsmith_mcp.config import Config, reset_config

        reset_config()
        for value in ("false", "0", "no", ""):
            env = {"POCKETSMITH_API_KEY": "test_key_1234567890", "READ_ONLY": value}
            with patch.dict(os.environ, env, clear=False):
                config = Config.from_env()
            assert config.read_only is False, f"Expected read_only=False for READ_ONLY={value!r}"
