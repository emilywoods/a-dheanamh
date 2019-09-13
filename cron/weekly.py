import argparse
import configparser
import itertools
import logging
import sys
from io import open
from json import loads
from time import time, ctime
from typing import Dict, List

import requests

from crate import client
from crate.client.connection import Connection
from crate.client.cursor import Cursor


CREATE_TABLE_STATEMENT: str = """
        CREATE TABLE IF NOT EXISTS tasks (
            ts_completed TIMESTAMP,
            description TEXT,
            name STRING,
            ts_due TIMESTAMP,
            labels ARRAY(string)
        )"""
INSERT_INTO_TABLE_STATEMENT: str = """
        INSERT INTO tasks (ts_completed, description, name, ts_due, labels) 
        VALUES (?, ?, ?, ?, ?)
        """
FILENAME: str = "weekly-report.txt"
URL: str = "https://api.trello.com/1/lists/{}/{}"


def _parse_args(args) -> configparser.ConfigParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", dest="config_file", required=True, type=str)
    args = parser.parse_args(args)

    config_file = args.config_file
    logging.debug(f"Reading configuration from {config_file}")
    config = configparser.ConfigParser()
    config.read(args.config_file)
    return config


def _initialise_db(url: str, username: str, password: str) -> (Connection, Cursor):
    conn, cursor = _connect_to_db(url, username, password)
    _create_table(cursor)
    return conn, cursor


def _connect_to_db(url: str, username: str, password: str) -> (Connection, Cursor):
    conn = client.connect(
        url, username=username, password=password, timeout=10, verify_ssl_cert=False
    )
    cursor: Cursor = conn.cursor()
    return conn, cursor


def _create_table(cursor: Cursor):
    cursor.execute(CREATE_TABLE_STATEMENT)


def _gather_task_insights(list_id: str, query_params: Dict) -> (Dict, Dict):
    tasks = _get_tasks_in_done_column(list_id, query_params)
    cleaned_tasks = _extract_useful_info(tasks=tasks)
    task_distribution = _get_distribution_by_label(cleaned_tasks)
    return cleaned_tasks, task_distribution


def _get_tasks_in_done_column(list_id: str, query_params: Dict) -> List:
    try:
        response = requests.get(URL.format(list_id, "cards"), params=query_params)
        response.raise_for_status()
        return loads(response.text)
    except requests.exceptions.RequestException as e:
        logging.error("Error when fetching and parsing tasks {}:".format(e))


def _extract_useful_info(tasks: List) -> List:
    filtered_tasks = []
    for task in tasks:
        relevant_task_data = _extract_data(task)
        filtered_tasks.append(relevant_task_data)
    return filtered_tasks


def _extract_data(task: Dict) -> Dict:
    return {
        "ts_completed": task["dateLastActivity"],
        "description": task["desc"],
        "name": task["name"],
        "ts_due": task["due"],
        "labels": [label["name"] for label in task["labels"]],
    }


def _get_distribution_by_label(filtered_tasks: List) -> Dict:
    all_labels = get_labels(filtered_tasks)
    unique_labels = set(all_labels)
    distribution = {}
    for label in unique_labels:
        count = all_labels.count(label)
        logging.debug(f"Completed {count} tasks for: {label}")
        distribution[label] = count
    return distribution


def get_labels(tasks: List) -> List:
    label_list_of_lists = [task["labels"] for task in tasks]
    return list(itertools.chain(*label_list_of_lists))


def create_weekly_summary_report(distribution: Dict, tasks: List) -> None:
    f = open(FILENAME, "a+")

    intro = f"""
Date: {ctime(time())}

This week you completed {len(tasks)} tasks.

The distribution of these tasks is broken down as {distribution} 
    """
    contents = intro + "\n"
    count = 1
    for task in tasks:
        contents += f"{count}. {task}\n"
        count += 1
    f.write(contents)
    f.close()


def _insert_to_db(cursor: Cursor, input: List) -> None:
    raw = [tuple(record.values()) for record in input]
    cursor.executemany(INSERT_INTO_TABLE_STATEMENT, raw)


def _archive_completed_tasks(list_id: str, query_params: Dict) -> None:
    try:
        response = requests.post(
            URL.format(list_id, "archiveAllCards"), params=query_params
        )
        response.raise_for_status()
        return loads(response.text)
    except requests.exceptions.RequestException as e:
        logging.error("Error when archiving tasks {}:".format(e))


def main(args) -> None:
    config: configparser.ConfigParser = _parse_args(args)
    list_id = config.get("default", "list_id")
    username = config.get("database", "username")
    password = config.get("database", "password")
    database_connection = config.get("database", "connection")
    query_params = {
        "key": config.get("default", "key"),
        "token": config.get("default", "token"),
    }

    conn, cursor = _initialise_db(database_connection, username, password)

    completed_tasks, task_distribution = _gather_task_insights(list_id, query_params)

    create_weekly_summary_report(task_distribution, completed_tasks)
    _insert_to_db(cursor=cursor, input=completed_tasks)
    _archive_completed_tasks(list_id, query_params)
    conn.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
