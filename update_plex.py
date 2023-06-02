import configparser
import os
import sys
import xml.etree.cElementTree as etree

import click
import requests

config_path = "~/.config/update_plex"

s = requests.Session()


def get_config(key):
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(config_path))

    return config["DEFAULT"][key]


def exit_with_error(msg):
    click.echo(
        f'{msg} Have you created the config file in "{config_path}"?',
        err=True,
    )
    sys.exit(1)


@click.command()
@click.option("--host")
@click.option("--token")
@click.version_option()
def run(host, token):
    if not host:
        try:
            host = get_config("host")
        except KeyError:
            exit_with_error("Don't know where plex is.")

    if not token:
        try:
            token = get_config("token")
        except KeyError:
            exit_with_error("Can't authenticate without a token.")

    url = f"https://{host}/library/sections"

    s.headers = {"X-Plex-Token": token}
    r = s.get(url)
    r.raise_for_status()

    path = './/Directory[@type="show"]'
    for section in etree.fromstring(r.content).findall(path):
        r = s.get(f"{url}/{section.attrib['key']}/refresh")
        r.raise_for_status()


if __name__ == "__main__":
    run()
