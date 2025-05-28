import datetime
from enum import Enum
from typing import Optional

import requests
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from constants import NOTION_API_KEY, NOTION_DATABASE_ID, NOTION_API_URL

# Create an MCP server
mcp = FastMCP("notion")

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


class Date(BaseModel):
    year: int
    month: int
    day: int

class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Status(str, Enum):
    NOT_STARTED = "Not started"
    IN_PROGRESS = "In progress"
    DONE = "Done"


class RoadmapItem(BaseModel):
    title: str
    status: Optional[Status] = None
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    priority: Optional[Priority] = None
    content: Optional[str] = None


@mcp.tool()
def create_roadmap_item(item: RoadmapItem):
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": item.title
                        }
                    }
                ]
            }
        }
    }

    if item.status:
        payload["properties"]["Status"] = {"status": {"name": item.status.value}}

    if item.start_date:
        start_date = datetime.date(year=item.start_date.year, month=item.start_date.month, day=item.start_date.day)
        payload["properties"]["Date"] = {"date": {"start": start_date.isoformat()}}
        if item.end_date:
            end_date = datetime.date(year=item.end_date.year, month=item.end_date.month, day=item.end_date.day)
            payload["properties"]["Date"]["date"]["end"] = end_date.isoformat()

    if item.priority:
        payload["properties"]["Priority"] = {"select": {"name": item.priority.value}}

    if item.content:
        payload["children"] = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": item.content}}
                    ]
                }
            }
        ]

    response = requests.post(NOTION_API_URL, headers=HEADERS, json=payload)
    if response.ok:
        return
    else:
        raise ValueError(f"Failed to create roadmap item: {response.status_code} - {response.text}")


if __name__ == "__main__":
    mcp.run()
