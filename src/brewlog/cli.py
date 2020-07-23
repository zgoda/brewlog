import os
from typing import List
from xml.etree import ElementTree as etree  # noqa: DUO107,N813

import click
from defusedxml.ElementTree import parse
from dotenv import find_dotenv, load_dotenv
from flask import current_app
from flask.cli import FlaskGroup

from . import make_app
from .ext import db


def create_app(info):
    return make_app('dev')


cli = FlaskGroup(create_app=create_app)
cli.help = 'This is a management script for the Brewlog application.'


@cli.command('initdb', short_help='Initialize missing database objects')
def initdb():
    db.create_all()


@cli.command('cleardb', short_help='Remove all database objects')
def cleardb():
    db.drop_all()


@cli.command('recreatedb', short_help='Recreate all database objects from scratch')
def recreatedb():
    db.drop_all()
    db.create_all()


@cli.group(name='generate')
def generate_grp():
    pass


@generate_grp.command(
    name='icons',
    help='Generate Jinja2 include file for SVG icons from specified icon set',
)
@click.argument('iconset')
@click.argument('names', nargs=-1)
def gen_icons(iconset: str, names: List[str]):
    _default_icons = [
        'check',
        'key',
        'lock',
        'log-in',
        'log-out',
        'send',
        'trash',
        'upload',
        'user-plus',
        'user',
    ]
    if names[0] == 'default':
        names = _default_icons
    target = os.path.join(
        current_app.root_path, current_app.template_folder, 'includes'
    )
    os.makedirs(target, exist_ok=True)
    target = os.path.join(target, 'icons.html')
    if os.path.isfile(target) and len(names) < len(_default_icons):
        if not click.confirm(
            'You are about to overwrite existing icon includes with smaller set '
            'than default, you sure want to do this?'
        ):
            return
    ns = 'http://www.w3.org/2000/svg'
    directory = os.path.join(current_app.static_folder, 'vendor', iconset)
    includes = []
    for name in names:
        fname = f'{name}.svg'
        file_path = os.path.join(directory, fname)
        tree = parse(file_path, forbid_dtd=True)
        root = tree.getroot()
        elems = root.findall('*')
        for el in elems:
            _, _, el.tag = el.tag.rpartition('}')
        symbol = etree.Element('symbol', attrib=root.attrib)
        symbol.attrib['id'] = name
        del symbol.attrib['class']
        symbol.attrib['width'] = symbol.attrib['height'] = '100%'
        symbol.extend(elems)
        includes.append(symbol)
    root = etree.Element('svg', attrib={'display': 'none', 'xmlns': ns})
    root.extend(includes)
    with open(target, 'w') as fp:
        fp.write(etree.tostring(root, encoding='unicode', short_empty_elements=False))


def main():
    load_dotenv(find_dotenv())
    cli()
