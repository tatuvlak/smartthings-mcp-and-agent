"""Expanded SmartThings MCP tool definitions.

This module defines all MCP tools exposed for SmartThings API domains:
- Locations
- Rooms
- Devices and Device Profiles
- Capabilities
- Scenes
- Rules/Automations
- Installed Apps
- Subscriptions/Webhooks
- Health/Hub

Tools are categorized as:
- READ_ONLY: Query tools (list_*, get_*)
- DEVICE_COMMAND: Device control (execute_command)
- STATE_CHANGING: Entity modification (create_*, update_*, delete_*)
"""

from typing import Any


class SmartThingsToolsCatalog:
    """Catalog of all SmartThings MCP tool definitions grouped by domain."""
    
    # ========== LOCATIONS DOMAIN ==========
    
    LOCATIONS_TOOLS = [
        {
            "name": "list_locations",
            "category": "READ_ONLY",
            "description": "List all smart home locations",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "get_location",
            "category": "READ_ONLY",
            "description": "Get details of a specific location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    }
                },
                "required": ["location_id"],
            },
        },
        {
            "name": "create_location",
            "category": "STATE_CHANGING",
            "description": "Create a new location (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Location name",
                    },
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (e.g., 'America/New_York')",
                    },
                    "country_code": {
                        "type": "string",
                        "description": "ISO 3166-1 country code (e.g., 'US')",
                    },
                },
                "required": ["name", "country_code"],
            },
        },
        {
            "name": "update_location",
            "category": "STATE_CHANGING",
            "description": "Update a location (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "New location name",
                    },
                    "timezone": {
                        "type": "string",
                        "description": "New timezone",
                    },
                },
                "required": ["location_id"],
            },
        },
        {
            "name": "delete_location",
            "category": "STATE_CHANGING",
            "description": "Delete a location (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    }
                },
                "required": ["location_id"],
            },
        },
    ]
    
    # ========== ROOMS DOMAIN ==========
    
    ROOMS_TOOLS = [
        {
            "name": "list_rooms",
            "category": "READ_ONLY",
            "description": "List all rooms in a location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    }
                },
                "required": ["location_id"],
            },
        },
        {
            "name": "get_room",
            "category": "READ_ONLY",
            "description": "Get details of a specific room",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "room_id": {
                        "type": "string",
                        "description": "Room ID",
                    }
                },
                "required": ["location_id", "room_id"],
            },
        },
        {
            "name": "create_room",
            "category": "STATE_CHANGING",
            "description": "Create a new room in a location (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "Room name",
                    },
                },
                "required": ["location_id", "name"],
            },
        },
        {
            "name": "update_room",
            "category": "STATE_CHANGING",
            "description": "Update a room (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "room_id": {
                        "type": "string",
                        "description": "Room ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "New room name",
                    },
                },
                "required": ["location_id", "room_id"],
            },
        },
        {
            "name": "delete_room",
            "category": "STATE_CHANGING",
            "description": "Delete a room (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "room_id": {
                        "type": "string",
                        "description": "Room ID",
                    }
                },
                "required": ["location_id", "room_id"],
            },
        },
    ]
    
    # ========== DEVICES DOMAIN ==========
    
    DEVICES_TOOLS = [
        {
            "name": "list_devices",
            "category": "READ_ONLY",
            "description": "List devices, optionally filtered by location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Optional location ID to filter",
                    }
                },
                "required": [],
            },
        },
        {
            "name": "get_device",
            "category": "READ_ONLY",
            "description": "Get details of a specific device",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID",
                    }
                },
                "required": ["device_id"],
            },
        },
        {
            "name": "get_device_state",
            "category": "READ_ONLY",
            "description": "Get current state of a device",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID",
                    }
                },
                "required": ["device_id"],
            },
        },
        {
            "name": "execute_command",
            "category": "DEVICE_COMMAND",
            "description": "Execute a command on a device (NO confirmation required)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID",
                    },
                    "capability": {
                        "type": "string",
                        "description": "Capability type (e.g., 'switch', 'brightness')",
                    },
                    "command": {
                        "type": "string",
                        "description": "Command name (e.g., 'on', 'off', 'setLevel')",
                    },
                    "arguments": {
                        "type": "object",
                        "description": "Optional command arguments",
                    },
                },
                "required": ["device_id", "capability", "command"],
            },
        },
        {
            "name": "update_device",
            "category": "STATE_CHANGING",
            "description": "Update device properties like label or room (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID",
                    },
                    "label": {
                        "type": "string",
                        "description": "New device label/name",
                    },
                    "room_id": {
                        "type": "string",
                        "description": "New room ID",
                    },
                },
                "required": ["device_id"],
            },
        },
    ]
    
    # ========== DEVICE PROFILES & CAPABILITIES DOMAIN ==========
    
    CAPABILITIES_TOOLS = [
        {
            "name": "list_capabilities",
            "category": "READ_ONLY",
            "description": "List available SmartThings capabilities",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "get_capability",
            "category": "READ_ONLY",
            "description": "Get details of a specific capability",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "capability_id": {
                        "type": "string",
                        "description": "Capability ID (e.g., 'switch', 'brightness')",
                    }
                },
                "required": ["capability_id"],
            },
        },
        {
            "name": "list_device_profiles",
            "category": "READ_ONLY",
            "description": "List available device profiles",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "get_device_profile",
            "category": "READ_ONLY",
            "description": "Get details of a device profile",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile_id": {
                        "type": "string",
                        "description": "Device profile ID",
                    }
                },
                "required": ["profile_id"],
            },
        },
    ]
    
    # ========== SCENES DOMAIN ==========
    
    SCENES_TOOLS = [
        {
            "name": "list_scenes",
            "category": "READ_ONLY",
            "description": "List all scenes in a location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    }
                },
                "required": ["location_id"],
            },
        },
        {
            "name": "get_scene",
            "category": "READ_ONLY",
            "description": "Get details of a specific scene",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "scene_id": {
                        "type": "string",
                        "description": "Scene ID",
                    }
                },
                "required": ["location_id", "scene_id"],
            },
        },
        {
            "name": "create_scene",
            "category": "STATE_CHANGING",
            "description": "Create a new scene (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "Scene name",
                    },
                    "actions": {
                        "type": "array",
                        "description": "List of device commands to execute",
                    },
                },
                "required": ["location_id", "name"],
            },
        },
        {
            "name": "update_scene",
            "category": "STATE_CHANGING",
            "description": "Update a scene (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "scene_id": {
                        "type": "string",
                        "description": "Scene ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "New scene name",
                    },
                    "actions": {
                        "type": "array",
                        "description": "Updated device commands",
                    },
                },
                "required": ["location_id", "scene_id"],
            },
        },
        {
            "name": "delete_scene",
            "category": "STATE_CHANGING",
            "description": "Delete a scene (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "scene_id": {
                        "type": "string",
                        "description": "Scene ID",
                    }
                },
                "required": ["location_id", "scene_id"],
            },
        },
        {
            "name": "execute_scene",
            "category": "DEVICE_COMMAND",
            "description": "Execute a scene (NO confirmation required)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "scene_id": {
                        "type": "string",
                        "description": "Scene ID",
                    }
                },
                "required": ["location_id", "scene_id"],
            },
        },
    ]
    
    # ========== RULES/AUTOMATIONS DOMAIN ==========
    
    RULES_TOOLS = [
        {
            "name": "list_rules",
            "category": "READ_ONLY",
            "description": "List all automation rules in a location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    }
                },
                "required": ["location_id"],
            },
        },
        {
            "name": "get_rule",
            "category": "READ_ONLY",
            "description": "Get details of a specific rule",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "rule_id": {
                        "type": "string",
                        "description": "Rule ID",
                    }
                },
                "required": ["location_id", "rule_id"],
            },
        },
        {
            "name": "create_rule",
            "category": "STATE_CHANGING",
            "description": "Create a new automation rule (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "Rule name",
                    },
                    "triggers": {
                        "type": "array",
                        "description": "Trigger conditions",
                    },
                    "actions": {
                        "type": "array",
                        "description": "Actions to execute",
                    },
                },
                "required": ["location_id", "name", "triggers", "actions"],
            },
        },
        {
            "name": "update_rule",
            "category": "STATE_CHANGING",
            "description": "Update an automation rule (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "rule_id": {
                        "type": "string",
                        "description": "Rule ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "New rule name",
                    },
                    "triggers": {
                        "type": "array",
                        "description": "Updated triggers",
                    },
                    "actions": {
                        "type": "array",
                        "description": "Updated actions",
                    },
                },
                "required": ["location_id", "rule_id"],
            },
        },
        {
            "name": "delete_rule",
            "category": "STATE_CHANGING",
            "description": "Delete an automation rule (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "rule_id": {
                        "type": "string",
                        "description": "Rule ID",
                    }
                },
                "required": ["location_id", "rule_id"],
            },
        },
        {
            "name": "enable_rule",
            "category": "DEVICE_COMMAND",
            "description": "Enable an automation rule (NO confirmation required)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "rule_id": {
                        "type": "string",
                        "description": "Rule ID",
                    }
                },
                "required": ["location_id", "rule_id"],
            },
        },
        {
            "name": "disable_rule",
            "category": "DEVICE_COMMAND",
            "description": "Disable an automation rule (NO confirmation required)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "rule_id": {
                        "type": "string",
                        "description": "Rule ID",
                    }
                },
                "required": ["location_id", "rule_id"],
            },
        },
    ]
    
    # ========== INSTALLED APPS DOMAIN ==========
    
    APPS_TOOLS = [
        {
            "name": "list_installed_apps",
            "category": "READ_ONLY",
            "description": "List installed SmartThings apps",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "get_installed_app",
            "category": "READ_ONLY",
            "description": "Get details of an installed app",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "app_id": {
                        "type": "string",
                        "description": "Installed app ID",
                    }
                },
                "required": ["app_id"],
            },
        },
        {
            "name": "uninstall_app",
            "category": "STATE_CHANGING",
            "description": "Uninstall an app (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "app_id": {
                        "type": "string",
                        "description": "Installed app ID",
                    }
                },
                "required": ["app_id"],
            },
        },
    ]
    
    # ========== SUBSCRIPTIONS/WEBHOOKS DOMAIN ==========
    
    SUBSCRIPTIONS_TOOLS = [
        {
            "name": "list_subscriptions",
            "category": "READ_ONLY",
            "description": "List event subscriptions/webhooks",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Optional location ID",
                    }
                },
                "required": [],
            },
        },
        {
            "name": "get_subscription",
            "category": "READ_ONLY",
            "description": "Get details of a subscription",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "subscription_id": {
                        "type": "string",
                        "description": "Subscription ID",
                    }
                },
                "required": ["subscription_id"],
            },
        },
        {
            "name": "create_subscription",
            "category": "STATE_CHANGING",
            "description": "Create a webhook subscription (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    },
                    "webhook_url": {
                        "type": "string",
                        "description": "Webhook endpoint URL",
                    },
                    "event_types": {
                        "type": "array",
                        "description": "Event types to subscribe to",
                    },
                },
                "required": ["location_id", "webhook_url"],
            },
        },
        {
            "name": "delete_subscription",
            "category": "STATE_CHANGING",
            "description": "Delete a subscription (requires confirmation)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "subscription_id": {
                        "type": "string",
                        "description": "Subscription ID",
                    }
                },
                "required": ["subscription_id"],
            },
        },
    ]
    
    # ========== HEALTH/HUB DOMAIN (Read-only) ==========
    
    HEALTH_TOOLS = [
        {
            "name": "get_hub_health",
            "category": "READ_ONLY",
            "description": "Get hub connectivity and health status",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    }
                },
                "required": ["location_id"],
            },
        },
        {
            "name": "list_hubs",
            "category": "READ_ONLY",
            "description": "List hubs in a location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Location ID",
                    }
                },
                "required": ["location_id"],
            },
        },
        {
            "name": "get_hub",
            "category": "READ_ONLY",
            "description": "Get hub details",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "hub_id": {
                        "type": "string",
                        "description": "Hub ID",
                    }
                },
                "required": ["hub_id"],
            },
        },
    ]
    
    @classmethod
    def get_all_tools(cls) -> list[dict[str, Any]]:
        """Get all available tools organized by domain.
        
        Returns:
            List of tool definitions
        """
        return (
            cls.LOCATIONS_TOOLS +
            cls.ROOMS_TOOLS +
            cls.DEVICES_TOOLS +
            cls.CAPABILITIES_TOOLS +
            cls.SCENES_TOOLS +
            cls.RULES_TOOLS +
            cls.APPS_TOOLS +
            cls.SUBSCRIPTIONS_TOOLS +
            cls.HEALTH_TOOLS
        )
    
    @classmethod
    def get_tools_by_category(cls, category: str) -> list[dict[str, Any]]:
        """Get tools filtered by category.
        
        Args:
            category: "READ_ONLY", "DEVICE_COMMAND", or "STATE_CHANGING"
            
        Returns:
            Filtered list of tools
        """
        return [t for t in cls.get_all_tools() if t.get("category") == category]
    
    @classmethod
    def get_tools_by_domain(cls, domain: str) -> list[dict[str, Any]]:
        """Get tools by domain.
        
        Args:
            domain: "locations", "rooms", "devices", "scenes", "rules", etc.
            
        Returns:
            Tools for that domain
        """
        domain_map = {
            "locations": cls.LOCATIONS_TOOLS,
            "rooms": cls.ROOMS_TOOLS,
            "devices": cls.DEVICES_TOOLS,
            "capabilities": cls.CAPABILITIES_TOOLS,
            "scenes": cls.SCENES_TOOLS,
            "rules": cls.RULES_TOOLS,
            "apps": cls.APPS_TOOLS,
            "subscriptions": cls.SUBSCRIPTIONS_TOOLS,
            "health": cls.HEALTH_TOOLS,
        }
        return domain_map.get(domain, [])
