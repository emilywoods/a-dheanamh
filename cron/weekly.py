import argparse
import configparser
import itertools
import sys
import time
from copy import deepcopy
from io import open
from json import loads
from typing import Dict, List

import requests

from crate import client
from crate.client.cursor import Cursor


def parse_args(args) -> configparser.ConfigParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", dest="config_file", required=True, type=str)
    args = parser.parse_args(args)

    config_file = args.config_file
    print(f"Reading configuration from {config_file}")
    config = configparser.ConfigParser()
    config.read(args.config_file)
    return config


def create_table(cursor: Cursor):
    import pdb

    pdb.set_trace()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS tasks (
        ts_completed TIMESTAMP,
        description TEXT,
        name STRING,
        ts_due TIMESTAMP,
        labels ARRAY(string))
        """
    )


def get_list_of_cards(board_id, key, token) -> List:
    url_to_list_cards = (
        f"https://api.trello.com/1/boards/{board_id}/cards?key={key}&token={token}"
    )
    response = requests.get(url=url_to_list_cards)  # add try/catch
    return loads(response.text)


def filter_tasks(tasks: List) -> List:
    """
    Extract relevant information
    """
    filtered_tasks = []
    for task in tasks:
        relevant_task_data = extract_data(task)
        filtered_tasks.append(relevant_task_data)
    return filtered_tasks


def extract_data(task: Dict):
    """
    Relevant fields from single element in response:
     {
        'dateLastActivity': '2019-08-09T19:59:30.996Z',
        'desc': '',
        'name': 'I have one task there',
        'due': None,
        'labels': [
            {
                'name': 'sys-admin',
            }
        ],
     }

    """
    return {
        "ts_completed": task["dateLastActivity"],
        "description": task["desc"],
        "name": task["name"],
        "ts_due": task["due"],
        "labels": [label["name"] for label in task["labels"]],
    }


def get_task_distribution(filtered_tasks: List) -> Dict:
    all_labels = get_labels(filtered_tasks)
    unique_labels = set(all_labels)
    distribution = {}
    for label in unique_labels:
        count = all_labels.count(label)
        print(f"Completed {count} tasks for: {label}")
        distribution[label] = count
    return distribution


def get_labels(tasks: List) -> List:
    label_list_of_lists = [task["labels"] for task in tasks]
    return list(itertools.chain(*label_list_of_lists))


def create_weekly_summary_report(num_tasks_completed, distribution, tasks):
    f = open("weekly-report.txt", "a+")

    intro = f"""
Date: {time.time()}

This week you completed {num_tasks_completed} tasks.

The distribution of these tasks is broken down as {distribution} 
    """
    report = intro + "\n"
    count = 1
    for task in tasks:
        report += f"{count}. {task}\n"
        count += 1
    f.write(report)
    f.close()


def insert_to_db(cursor: Cursor, input: List):
    raw = [tuple(record.values()) for record in input]
    import pdb

    pdb.set_trace()
    cursor.executemany(
        "INSERT INTO tasks (ts_completed, description, name, ts_due, labels) "
        "VALUES (?, ?, ?, ?, ?) ",
        raw,  # list of tuples
    )


def archive_completed_tasks():
    requests.post(
        url=f"https://api.trello.com/1/lists/{list_id}/archiveAllCards?key={key}&token={token}"
    )


def main(args) -> None:
    config: configparser.ConfigParser = parse_args(args)
    board_id = config.get("default", "board_id")
    key = config.get("default", "key")
    token = config.get("default", "token")
    list_id = config.get("default", "list_id")

    conn = client.connect(
        "http://localhost:4200",
        username="crate",
        password="",
        timeout=10,
        verify_ssl_cert=False,
    )

    cursor: Cursor = conn.cursor()

    create_table(cursor)
    list_of_cards = get_list_of_cards(board_id, key, token)

    completed_tasks = list(
        filter(lambda task: task["idList"] == list_id, list_of_cards)
    )
    num_tasks_completed = len(completed_tasks)
    print(f"This week you completed {num_tasks_completed} tasks\n")

    tasks = deepcopy(completed_tasks)
    filtered_tasks = filter_tasks(tasks=tasks)

    weekly_summary = {
        "total_completed": num_tasks_completed,
        "task_list": filtered_tasks,
    }

    distribution = get_task_distribution(deepcopy(filtered_tasks))

    create_weekly_summary_report(num_tasks_completed, distribution, filtered_tasks)

    weekly_summary["distribution"] = distribution
    print(weekly_summary)

    insert_to_db(cursor=cursor, input=filtered_tasks)

    archive_completed_tasks()

    conn.close()


archive_completed_tasks()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
