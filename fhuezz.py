import sys, os
import requests
import json
from pygments import highlight, lexers, formatters
from termcolor import colored
import click
import socket

class Credentials(object):
    def __init__(self, host=None, key=None, verbose=False):
        self.host = host
        self.key = key
        self.verbose = verbose

def validate_host(ctx, param, value):
    if value:
        try:
            valid_host = socket.gethostbyname(value)
            return(valid_host)
        except socket.gaierror:
            raise click.BadParameter('Not an hostname or IP')
    else:
        click.echo(click.UsageError("Need a host. Check help"))
        sys.exit(2)

def run_auth(host, verbose):
    user = click.prompt('Please enter a username', type=str)
    if len(user) > 32:
        click.echo(click.UsageError("Username too long."))
        click.Context(exit(3))
    if click.confirm('Please press the Hue button in order to get the token'):
        json_data_user = "{\"devicetype\":\"my_hue_app#%s\"}" % user
        r = requests.post("http://%s/api" % host, data=json_data_user)
        if verbose:
            click.echo(highlight(json.dumps(json.loads(r.text), sort_keys=True, indent=4),
                lexers.JsonLexer(), formatters.TerminalFormatter()))
        else:
            if 'error' in json.loads(r.text)[0]:
                click.secho("Error: " + json.loads(r.text)[0]['error']['description'], fg='red')
                click.Context(exit(100))
            if 'success' in json.loads(r.text)[0]:
                click.secho("Your token: " + json.loads(r.text)[0]['success']['username'], fg='green')
                click.Context(exit(0))
            else:
                click.secho("unexpected output.", fg='yellow')
                click.Context(exit(4))
    sys.exit(0)

@click.group(invoke_without_command=True)
@click.option('--auth', help="To retrieve the API key for the Hue (use with --host option)", is_flag=True)
@click.option('--host', help="Your Hue hostname or IP", callback=validate_host, metavar='IP')
@click.option('--key', help="Your API key", metavar='API_KEY', type=click.STRING)
@click.option('--ask-key', is_flag=True)
@click.option('--verbose', help="Give more output", is_flag=True, default=False)
@click.pass_context

def cli(ctx, auth, host, key, ask_key, verbose):
    """A commandline interface, to the Philips Hue"""
    ctx.obj = Credentials(host, key, verbose)
    if ctx.invoked_subcommand is None:
        if auth and host and not key and not ask_key:
            run_auth(host, verbose)
        else:
            click.echo(ctx.get_help())
    else:
        if ask_key:
            ctx.obj.key = click.prompt('API key', type=str, hide_input=True)
        elif not key and not ask_key:
            click.echo(click.UsageError("Need a method to authenticate."))
            click.echo(ctx.get_help())
            click.Context(exit())

@cli.command('list', short_help='List the available lights')
@click.pass_obj
def list(credentials):
    """Display the available light in a JSON format"""
    api_prefix = "http://%s/api/%s" % (credentials.host, credentials.key)
    r = requests.get("%s/lights" % api_prefix)
    if credentials.verbose:
        click.echo(highlight(json.dumps(json.loads(r.text), sort_keys=True, indent=4),
            lexers.JsonLexer(), formatters.TerminalFormatter()))
    else:
        j = json.loads(r.text)
        for i in range(len(j)):
            if j[str(i + 1)]['state']['on']:
                col = 'green'
            else:
                col = 'red'
            click.echo(str(i + 1) + " " + colored(j[str(i + 1)]['name'], col))

@cli.command('on', short_help='Turn a light on')
@click.argument('light', nargs=-1, type=click.INT)
@click.pass_obj
def on(credentials, light):
    api_prefix = "http://%s/api/%s" % (credentials.host, credentials.key)
    for l in light:
        r = requests.put("%s/lights/%s/state" % (api_prefix, l), '{"on":true}')
        click.secho(r.text, fg='green')

@cli.command('off', short_help='Turn a light off')
@click.argument('light', nargs=-1, type=click.INT)
@click.pass_obj
def on(credentials, light):
    api_prefix = "http://%s/api/%s" % (credentials.host, credentials.key)
    for l in light:
        r = requests.put("%s/lights/%s/state" % (api_prefix, l), '{"on":false}')
        click.secho(r.text, fg='red')

if __name__ == '__main__':
    cli(auto_envvar_prefix='HUE')
