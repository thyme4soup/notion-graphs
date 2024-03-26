import logging
from notion_client import Client
from notion_client import APIErrorCode, APIResponseError
import os

if os.getenv("NOTION_TOKEN", default=None):
    NOTION_TOKEN = os.getenv("NOTION_TOKEN", default=None)
    NOTION_TASKS_DATABASE = os.getenv("NOTION_TASKS_DATABASE", default=None)
else:
    from env import NOTION_TOKEN, NOTION_TASKS_DATABASE

notion = Client(auth=NOTION_TOKEN)
database_id = NOTION_TASKS_DATABASE


def get_database_object(database_id=database_id, tag=None):
    try:
        if tag:
            return notion.databases.query(
                database_id=database_id,
                filter={"property": "Tags", "multi_select": {"contains": tag}},
            )
        else:
            return notion.databases.query(database_id=database_id)
    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            logging.error("Database could not be found")
            raise error
        else:
            # Other error handling code
            logging.error(error)
            raise error


def update_page_properties(page_id, properties):
    try:
        return notion.pages.update(page_id, properties=properties)
    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            logging.error("Page could not be found")
            raise error
        else:
            # Other error handling code
            logging.error(error)
            raise error


def unwrap_notion_prop(d):
    if isinstance(d, list):
        if len(d):
            return unwrap_notion_prop(d[0])
        else:
            return d
    elif not isinstance(d, dict):
        return d
    elif d.get("object", None):
        return d
    else:
        prop_type = d.get("type", None)
        if prop_type == None or d.get(prop_type, None) == None:
            if not d.get("content", None) == None:
                return d["content"]
            elif d.get("name", None):
                return d["name"]
            else:
                raise Exception(f"Could not get type for object {d}!")
        else:
            return unwrap_notion_prop(d[prop_type])


def get_page(id):
    # ToDo: get page given id
    return notion.pages.retrieve(id)


if __name__ == "__main__":
    print("notion_helper tests")
