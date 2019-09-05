import os
import click
from configparser import ConfigParser
from json import loads
import requests
from typing import List

BOARD_NAME_WEEKLY = "weekly"
BOARD_NAME_PROJECTS = "projects"
BOARD_NAME_BOOKS = "books"
BOARD_NAME_EXPLORE = "explore"
BOARD_NAME_GOALS = "goals"

URL = "https://api.trello.com/1/lists/{}/cards"


def _print_each_to_console(everything) -> None:
    i = 1
    for item in everything:
        click.echo(str(i) + ". " + item["name"])
        i += 1


@click.pass_context
def _get_list_items(ctx, list_id=None) -> List:
    query_params = {"key": ctx.obj["api_key"], "token": ctx.obj["api_token"]}
    response = requests.get(URL.format(list_id), params=query_params)
    return loads(response.text)


@click.group()
@click.option("--api-key", "-a", help="your API key for the Trello API")
@click.option("--config-file", "-c", type=click.Path(), default="aw-yay.config")
@click.pass_context
def main(ctx, api_key, config_file):
    filename = os.path.expanduser(config_file)

    if not api_key and os.path.exists(filename):
        config = ConfigParser()
        config.read(config_file)
        ctx.obj = {
            "api_key": config.get("trello", "key"),
            "api_token": config.get("trello", "token"),
            "today": config.get(BOARD_NAME_WEEKLY, "today"),
            "done": config.get(BOARD_NAME_WEEKLY, "done"),
            "todo": config.get(BOARD_NAME_WEEKLY, "todo"),
            "books.learning": config.get(BOARD_NAME_BOOKS, "learning"),
            "books.fun": config.get(BOARD_NAME_BOOKS, "fun"),
            "code": config.get(BOARD_NAME_PROJECTS, "code"),
            "blog_and_talks": config.get(BOARD_NAME_PROJECTS, "blog_and_talks"),
            "bhag": config.get(BOARD_NAME_GOALS, "bhag"),
            "habits": config.get(BOARD_NAME_GOALS, "habits"),
            "homeplace": config.get(BOARD_NAME_EXPLORE, "homeplace"),
            "vacation": config.get(BOARD_NAME_EXPLORE, "vacation"),
            "conferences": config.get(BOARD_NAME_EXPLORE, "conferences"),
        }


@click.command()
@click.pass_context
def today(ctx):
    click.echo("today!\n")
    everything = _get_list_items(list_id=ctx.obj["today"])
    _print_each_to_console(everything)


@click.command()
@click.pass_context
def week(ctx):
    click.echo("To do this week\n")
    inprogress = _get_list_items(list_id=ctx.obj["today"])
    everything_else = _get_list_items(list_id=ctx.obj["todo"])

    _print_each_to_console(inprogress + everything_else)


@click.command()
@click.pass_context
def done(ctx):
    click.echo("Already completed\n")
    everything = _get_list_items(list_id=ctx.obj["done"])

    _print_each_to_console(everything)


@click.command()
@click.pass_context
def books(ctx):
    click.echo("Reading lists!\n")
    fun = _get_list_items(list_id=ctx.obj["books.fun"])
    learning = _get_list_items(list_id=ctx.obj["books.learning"])

    _print_each_to_console(fun + learning)


@click.command()
@click.pass_context
def goals(ctx):
    click.echo("BIG HaIRy audacious goals!\n")
    everything = _get_list_items(list_id=ctx.obj["bhag"])

    _print_each_to_console(everything)


@click.command()
@click.pass_context
def habits(ctx):
    click.echo("Weekly habits\n")
    everything_else = _get_list_items(list_id=ctx.obj["habits"])

    _print_each_to_console(everything_else)


@click.command()
@click.pass_context
def travel(ctx):
    click.echo("~Exploring~\n")
    click.echo("homeplace:")
    code = _get_list_items(list_id=ctx.obj["homeplace"])
    _print_each_to_console(code)

    click.echo("\nvacation:")
    blog_and_talks = _get_list_items(list_id=ctx.obj["vacation"])
    _print_each_to_console(blog_and_talks)

    click.echo("\nconferences:")
    blog_and_talks = _get_list_items(list_id=ctx.obj["conferences"])
    _print_each_to_console(blog_and_talks)


@click.command()
@click.pass_context
def projects(ctx):
    click.echo("Things for fun and learning and sharing\n")
    click.echo("code:")
    code = _get_list_items(list_id=ctx.obj["code"])
    _print_each_to_console(code)

    click.echo("\nblog posts and talks:")
    blog_and_talks = _get_list_items(list_id=ctx.obj["blog_and_talks"])
    _print_each_to_console(blog_and_talks)


main.add_command(today)
main.add_command(week)
main.add_command(done)
main.add_command(books)
main.add_command(goals)
main.add_command(habits)
main.add_command(travel)
main.add_command(projects)
