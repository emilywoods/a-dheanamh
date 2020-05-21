import os
from configparser import ConfigParser
from json import loads
from typing import List

import click
import requests

LATER: str = "later"
BOOKS_LEARNING: str = "books.learning"
BOOKS_FUN: str = "books.fun"
CODE: str = "code"
BLOG_AND_TALKS: str = "blog_and_talks"
BHAG: str = "bhag"
DONE: str = "done"
TODAY: str = "today"
HOMEPLACE: str = "homeplace"
HABITS: str = "habits"
VACATION: str = "vacation"
CONFERENCES: str = "conferences"

BOARD_NAME_WEEKLY: str = "weekly"
BOARD_NAME_PROJECTS: str = "projects"
BOARD_NAME_BOOKS: str = "books"
BOARD_NAME_EXPLORE: str = "explore"
BOARD_NAME_GOALS: str = "goals"

URL: str = "https://api.trello.com/1/lists/{}/cards"

def _print_each_to_console(items: List) -> None:
    i = 1
    for item in items:
        click.echo(str(i) + ". " + item["name"])
        i += 1


@click.pass_context
def _get_list_items(ctx, list_id=None) -> List:
    query_params = {"key": ctx.obj["api_key"], "token": ctx.obj["api_token"]}
    response = requests.get(URL.format(list_id), params=query_params)
    return loads(response.text) or []


@click.group()
@click.option("--api-key", "-a", help="your API key for the Trello API")
@click.option("--config-file", "-c", type=click.Path(), default="~/.aw-yay.config")
@click.pass_context
def main(ctx, api_key: str, config_file: str):
    filepath = os.path.expanduser(config_file)

    if not api_key and os.path.exists(filepath):
        config = ConfigParser()
        config.read(filepath)
        ctx.obj = {
            "api_key": config.get("trello", "key"),
            "api_token": config.get("trello", "token"),
            TODAY: config.get(BOARD_NAME_WEEKLY, TODAY),
            DONE: config.get(BOARD_NAME_WEEKLY, DONE),
            LATER: config.get(BOARD_NAME_WEEKLY, LATER),
            BOOKS_LEARNING: config.get(BOARD_NAME_BOOKS, "learning"),
            BOOKS_FUN: config.get(BOARD_NAME_BOOKS, "fun"),
            CODE: config.get(BOARD_NAME_PROJECTS, CODE),
            BLOG_AND_TALKS: config.get(BOARD_NAME_PROJECTS, BLOG_AND_TALKS),
            BHAG: config.get(BOARD_NAME_GOALS, BHAG),
            HABITS: config.get(BOARD_NAME_GOALS, HABITS),
            HOMEPLACE: config.get(BOARD_NAME_EXPLORE, HOMEPLACE),
            VACATION: config.get(BOARD_NAME_EXPLORE, VACATION),
            CONFERENCES: config.get(BOARD_NAME_EXPLORE, CONFERENCES),
        }


@click.command()
@click.pass_context
def today(ctx):
    click.echo(click.style("today.. or this week!\n", fg="blue"))
    everything = _get_list_items(list_id=ctx.obj[TODAY])
    _print_each_to_console(everything)


@click.command()
@click.pass_context
def later(ctx):
    click.echo(click.style("Upcoming stuff\n", fg="blue"))
    inprogress = _get_list_items(list_id=ctx.obj[TODAY])
    everything_else = _get_list_items(list_id=ctx.obj[LATER])

    _print_each_to_console(inprogress + everything_else)


@click.command()
@click.pass_context
def done(ctx):
    click.echo(click.style("Already completed\n", fg="blue"))
    everything = _get_list_items(list_id=ctx.obj[DONE])

    _print_each_to_console(everything)


@click.command()
@click.pass_context
def books(ctx):
    click.echo(click.style("Reading lists!\n", fg="magenta"))
    fun = _get_list_items(list_id=ctx.obj[BOOKS_FUN])
    learning = _get_list_items(list_id=ctx.obj[BOOKS_LEARNING])

    _print_each_to_console(fun + learning)


@click.command()
@click.pass_context
def goals(ctx):
    click.echo(click.style("BIG HaIRy audacious goals!\n", fg="green"))
    everything = _get_list_items(list_id=ctx.obj[BHAG])

    _print_each_to_console(everything)


@click.command()
@click.pass_context
def habits(ctx):
    click.echo(click.style(HABITS + " \n", fg="green"))
    everything_else = _get_list_items(list_id=ctx.obj[HABITS])

    _print_each_to_console(everything_else)


@click.command()
@click.pass_context
def travel(ctx):
    click.echo(click.style("~Exploring~\n", fg="yellow"))
    click.echo("{}:".format(HOMEPLACE))
    code = _get_list_items(list_id=ctx.obj[HOMEPLACE])
    _print_each_to_console(code)

    click.echo("\n{}:".format(VACATION))
    blog_and_talks = _get_list_items(list_id=ctx.obj[VACATION])
    _print_each_to_console(blog_and_talks)

    click.echo("\n{}:".format(CONFERENCES))
    blog_and_talks = _get_list_items(list_id=ctx.obj[CONFERENCES])
    _print_each_to_console(blog_and_talks)


@click.command()
@click.pass_context
def projects(ctx):
    click.echo(click.style("Things for fun and learning and sharing\n", fg="cyan"))
    click.echo("code:")
    code = _get_list_items(list_id=ctx.obj[CODE])
    _print_each_to_console(code)

    click.echo("\nblog posts and talks:")
    blog_and_talks = _get_list_items(list_id=ctx.obj[BLOG_AND_TALKS])
    _print_each_to_console(blog_and_talks)


main.add_command(today)
main.add_command(later)
main.add_command(done)
main.add_command(books)
main.add_command(goals)
main.add_command(habits)
main.add_command(travel)
main.add_command(projects)
