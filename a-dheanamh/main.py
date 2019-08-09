import argparse
import configparser

import configparser
import sys
from functools import reduce
from json import loads
from typing import List


import requests


def parse_args(args) -> configparser.ConfigParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", dest='config_file', required=True, type=str)
    args = parser.parse_args(args)

    config_file = args.config_file
    print(f"Reading configuration from {config_file}")
    config = configparser.ConfigParser()
    config.read(args.config_file)
    return config


def get_labels(tasks: List) -> List:
    label_with_meta_list = [task['labels'] for task in tasks if 'labels' in task]
    return [label['name'] for label in reduce(list.__add__, label_with_meta_list)]


def main(args) -> None:
    config: configparser.ConfigParser = parse_args(args)
    board_id = config.get("default", "board_id")
    key = config.get("default", "key")
    token = config.get("default", "token")
    list_id = config.get("default", "list_id")

    url_to_list_cards = f"https://api.trello.com/1/boards/{board_id}/cards?key={key}&token={token}"
    response = requests.get(url=url_to_list_cards)
    list_of_cards_on_board = loads(response.text)

    completed_tasks = list(filter(lambda task: task['idList'] == list_id, list_of_cards_on_board))
    number_of_tasks_completed = len(completed_tasks)
    print(f"This week you completed {number_of_tasks_completed} tasks\n")

    # distribution of each task
    all_labels = get_labels(completed_tasks)
    unique_labels = set(all_labels)

    label_distribution = {}
    for label in unique_labels:
        label_count = all_labels.count(label)
        label_distribution[label] = label_count
        print(f"Completed {label_count} tasks for: {label}")

    # insert to db: tasks, label count
    # insert_completed_tasks_to_db()
    # archive_completed_tasks()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
