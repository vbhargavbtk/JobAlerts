"""
Channel Manager Module
Manages public and private Telegram channel configurations from YAML and database.
Supports adding, updating, enabling/disabling, and deleting channels via Web UI and API.
"""
import os
import logging
from typing import List, Dict, Any, Optional
import yaml
from config.settings import settings

logger = logging.getLogger(__name__)


class ChannelConfig:
    def __init__(
        self,
        channel_id: str,
        name: str,
        telegram_channel_id: str,
        channel_type: str = "public",
        enabled: bool = True,
        description: str = ""
    ):
        self.channel_id = channel_id
        self.name = name
        self.telegram_channel_id = telegram_channel_id
        self.channel_type = channel_type
        self.enabled = enabled
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.channel_id,
            "name": self.name,
            "telegram_channel_id": self.telegram_channel_id,
            "type": self.channel_type,
            "enabled": self.enabled,
            "description": self.description
        }


class ChannelManager:
    def __init__(self, config_path: str = "config/channels.yaml"):
        self.config_path = config_path

    def load_channels(self) -> List[ChannelConfig]:
        """Loads configured channels from channels.yaml."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Channels file {self.config_path} not found. Returning empty list.")
            return []

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            raw_channels = data.get("channels", [])
            channels = []
            for ch in raw_channels:
                channels.append(ChannelConfig(
                    channel_id=ch.get("id", str(ch.get("telegram_channel_id"))),
                    name=ch.get("name", "Unnamed Channel"),
                    telegram_channel_id=str(ch.get("telegram_channel_id")),
                    channel_type=ch.get("type", "public"),
                    enabled=ch.get("enabled", True),
                    description=ch.get("description", "")
                ))
            return channels
        except Exception as e:
            logger.error(f"Error loading channels config from {self.config_path}: {e}", exc_info=True)
            return []

    def load_channels_dict(self) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self.load_channels()]

    def save_channels(self, channels: List[Dict[str, Any]]) -> bool:
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump({"channels": channels}, f, sort_keys=False, allow_unicode=True)
            return True
        except Exception as e:
            logger.error(f"Failed to write channels to {self.config_path}: {e}", exc_info=True)
            return False

    def add_channel(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        channels = self.load_channels_dict()
        ch_id = channel_data.get("id") or channel_data.get("telegram_channel_id", "").replace("@", "").replace("-", "ch_")
        
        # Check duplicate
        for ch in channels:
            if ch.get("id") == ch_id or ch.get("telegram_channel_id") == channel_data.get("telegram_channel_id"):
                raise ValueError(f"Channel with ID or Telegram address already exists.")

        new_entry = {
            "id": ch_id,
            "name": channel_data.get("name", "Unnamed Channel"),
            "telegram_channel_id": channel_data.get("telegram_channel_id", "").strip(),
            "type": channel_data.get("type", "public"),
            "enabled": bool(channel_data.get("enabled", True)),
            "description": channel_data.get("description", "")
        }
        channels.append(new_entry)
        self.save_channels(channels)
        return new_entry

    def update_channel(self, channel_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        channels = self.load_channels_dict()
        found = False
        updated_item = None
        for i, ch in enumerate(channels):
            if ch.get("id") == channel_id:
                if "name" in update_data:
                    ch["name"] = update_data["name"]
                if "telegram_channel_id" in update_data:
                    ch["telegram_channel_id"] = update_data["telegram_channel_id"].strip()
                if "type" in update_data:
                    ch["type"] = update_data["type"]
                if "enabled" in update_data:
                    ch["enabled"] = bool(update_data["enabled"])
                if "description" in update_data:
                    ch["description"] = update_data["description"]
                channels[i] = ch
                updated_item = ch
                found = True
                break
        
        if found:
            self.save_channels(channels)
            return updated_item
        return None

    def delete_channel(self, channel_id: str) -> bool:
        channels = self.load_channels_dict()
        initial_len = len(channels)
        channels = [ch for ch in channels if ch.get("id") != channel_id]
        if len(channels) < initial_len:
            self.save_channels(channels)
            return True
        return False
