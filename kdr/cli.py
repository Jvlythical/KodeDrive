import click
import cli_syncthing_adapter
import os

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.version_option()
@click.group(
  epilog="Run 'kdr COMMAND --help' for more information on a command.", 
  context_settings=CONTEXT_SETTINGS
)

@click.pass_context
def main(ctx):
  ''' A tool to synchronize remote/local directories. '''
  pass

# 
# Subcommands start
#

@main.command()
@click.option('-c', '--client', is_flag=True, help="Set Kodedrive into client mode.")
@click.option('-s', '--server', is_flag=True, help="Set Kodedrive into server mode.")
@click.option('-a', '--about', is_flag=True, help="List KodeDrive information.")
@click.option('-i', '--init', is_flag=True, help="Init KodeDrive daemon.")
@click.option('-e', '--exit', is_flag=True, help="Exit KodeDrive daemon.")
@click.option('-t', '--test', help="Test random functions :)")
def sys(**kwargs):
  ''' Manage application configuration. '''

  output = cli_syncthing_adapter.sys(**kwargs)

  if output:
    click.echo("%s" % output)
  else:
    click.echo(click.get_current_context().get_help())

@main.command()
def ls():
  ''' List synchronized directories. '''

  metadata = cli_syncthing_adapter.ls()
  
  if not metadata:
    return

  headers = []
  lengths = []

  # Preprocess

  # Iterate through list
  for i, record in enumerate(metadata):
    lengths.append(0)

    # Iterate through dictionary
    for header in record:
      headers.append(header)
      num_data = len(record[header])

      for data in record[header]:
        cur = len(data)
        prev = lengths[i] 

        lengths[i] = cur if cur > prev else prev
  
  # Process
  body = str()
  for i in range(0, num_data):
    for n in range(0, len(metadata)):
      value = metadata[n][headers[n]][i]
      s = "{:<%i}" % (lengths[n] + 5)
      body += s.format(value.strip())

    body += "\n"
  
  if len(body) == 0:
    return

  heading = str()
  # Iterate through list
  for i, record in enumerate(metadata):
    # Iterate through dictionary
    for header in record:
      s = "{:<%i}" % (lengths[i] + 5)
      heading += s.format(header)
  
  # Postprocess
  click.echo(heading)
  click.echo(body.strip())

@main.command()
@click.argument('key', nargs=1)
@click.option(
  '-t', '--tag', nargs=1, 
  metavar=" <TEXT>", 
  help="Associate this folder with a tag."
)
@click.option(
  '-p', '--path', 
  type=click.Path(exists=True, writable=True, resolve_path=True), 
  default=".", nargs=1, metavar="<PATH>",
  help="Specify which folder to link."
)
@click.option(
  '-y', '--yes', nargs=1, is_flag=True,
  default=False,
  help="Bypass confirmation step."
)
def link(**kwargs):
  ''' Synchronize remote/local directory. '''
  
  key = kwargs['key']
  tag = kwargs['tag'] if 'tag' in kwargs else None
  path = kwargs['path']
  
  if kwargs['yes']:
    output = cli_syncthing_adapter.link(key, tag, path)
    click.echo("%s" % output)
  else:
    if click.confirm("Are you sure you want to link %s?" % path):
      output = cli_syncthing_adapter.link(key, tag, path)
      click.echo("%s" % output)

''' 
  *** Make the catch more specific 

  output = None

  if click.confirm("Are you sure you want to link to %s?" % path):
    try:
      output = cli_syncthing_adapter.init(key, tag, path)

    except ValueError:
      raise

    except:
      cli_syncthing_adapter.start()
      sleep(1.5)
      output = cli_syncthing_adapter.init(key, tag, path)

    finally:
      if output:
        click.echo("%s" % output)
'''

@main.command()
@click.option(
  '-t', '--tag', nargs=1, metavar=" <TEXT>", 
  default="my-sync",
  help="Associate this folder with a tag."
)
@click.argument(
  'path',
  type=click.Path(exists=True, writable=True, resolve_path=True), 
  nargs=1, metavar="PATH",
)
def add(**kwargs):
  ''' Make a folder shareable. '''

  output = cli_syncthing_adapter.add(**kwargs)
  click.echo("%s" % output)

@main.command()
@click.argument(
  'path',
  type=click.Path(exists=True, writable=True, resolve_path=True), 
  nargs=1, metavar="PATH",
)
def free(**kwargs):
  ''' Stop synchronization of directory. '''

  output = cli_syncthing_adapter.free(kwargs['path'])
  click.echo("%s" % output)

@main.command()
@click.argument(
  'path',
  type=click.Path(exists=True, writable=True, resolve_path=True), 
  nargs=1, metavar="PATH",
)
@click.argument('name', nargs=1)
def tag(path, name):
  ''' Change tag associated with directory. '''

  output = cli_syncthing_adapter.tag(path, name)
  click.echo("%s" % output)

@main.command()
@click.argument(
  'path',
  type=click.Path(exists=True, writable=True, resolve_path=True), 
  nargs=1, metavar="PATH",
)
def key(path):
  ''' Display synchronization key for directories. '''

  output = cli_syncthing_adapter.key(path)
  click.echo("%s" % output)

@main.command()
@click.argument('source', nargs=-1, required=True)
@click.argument('target', nargs=1)
def mv(source, target):
  ''' Move synchronized directory. '''

  if os.path.isfile(target) and len(source) == 1:
    if click.confirm("Are you sure you want to overwrite %s?" % target):

      cli_syncthing_adapter.mv_edge_case(source, target)
      # Edge case: to match Bash 'mv' behavior and overwrite file

      return

  if len(source) > 1 and not os.path.isdir(target):
    click.echo(click.get_current_context().get_help())
    return

  else:
    cli_syncthing_adapter.mv(source, target)

@main.command()
@click.option(
  '-a', '--add', 
  type=(click.Path(exists=True, writable=True, resolve_path=True), str), 
  default=(None, None), nargs=2, metavar="   <PATH> <KEY>",
  help="Authorize a directory."
)
@click.option(
  '-r', '--remove', 
  type=(click.Path(exists=True, writable=True, resolve_path=True), str), 
  default=(None, None), nargs=2, metavar="<PATH> <KEY>",
  help="Deauthorize a directory."
)
@click.option(
  '-l', '--list', 
  is_flag=True, 
  help="List all devices authorized")
@click.option(
  '-y', '--yes', nargs=1, is_flag=True,
  default=False,
  help="Bypass confirmation step."
)
def auth(**kwargs):
  ''' Authorize device synchronization. '''

  """
    kdr auth <path> <device_id (client)>

    1. make sure path has been added to config.xml, server
    2. make sure path is not shared by someone
    3. add device_id to folder in config.xml, server
    4. add device to devices in config.xml, server

  """
  output = None
  option = None
  path = None
  device_id = None

  if all(kwargs['add']): # if tuple doesn't contain all Nones
    (path, device_id) = kwargs['add']
    option = 'add'

  elif all(kwargs['remove']):
    (path, device_id) = kwargs['remove']
    option = 'remove'

  elif kwargs['list']:
    option = 'list'

  if kwargs['yes']:
    output = cli_syncthing_adapter.auth(option, path)
    click.echo("%s" % output)

  else:
    if all(kwargs['add']): 
      if click.confirm("Are you sure you want to authorize %s?" % path):
        output = cli_syncthing_adapter.auth(option, path, device_id)

      else:
        return

    else:
      output = cli_syncthing_adapter.auth(option, path, device_id)

  if output:
    click.echo("%s" % output)
  
  if not output or not option:
    click.echo(click.get_current_context().get_help())


"""
REFERENCE

@main.command()
@click.option(
  '-p', '--port', nargs=1, 
  type=int
)
@click.option(
  '-c', '--config', nargs=1, 
  type=click.Path(exists=True, writable=True, resolve_path=True), 
)
def start(**kwargs):
  ''' Start a KodeDrive instance. '''
  output = cli_syncthing_adapter.start(**kwargs)
  click.echo("%s" % output)  

@main.command()
@click.argument(
  'path',
  type=click.Path(exists=True, writable=True, resolve_path=True), 
  nargs=1, metavar="PATH",
)
def inspect(path):
  ''' Return information regarding directory. '''

  return

@main.command()
@click.argument('arg', nargs=1)
def test(arg):
  ''' Test random functions :) '''

  cli_syncthing_adapter.test(arg)

@cli.command()
@click.argument('src', type=click.Path(exists=True), nargs=1)
@click.argument('dest', nargs=1)
def connect(src, dest):
  ''' Connect to remote server. '''
    
  output = cli_syncthing_adapter.connect()
  click.echo("%s" % output)

@click.group(invoke_without_command=True)
@click.option('-v', '--version', is_flag=True, help='Print version information and quit')
click.echo("%s '%s' is not a valid command." % ('kodedrive:', arg))
click.echo("See 'kodedrive --help'.")

@main.command()
def start():
  ''' Start KodeDrive daemon. '''

  output = cli_syncthing_adapter.start()
  click.echo("%s" % output)

@main.command()
def stop():
  ''' Stop KodeDrive daemon. '''

  output = cli_syncthing_adapter.stop()
  output = output.strip()
  click.echo("%s" % output)

@main.command()
@click.argument('arg', nargs=1)
def test(arg):
  ''' Test random functions :) '''

  cli_syncthing_adapter.test(arg)

Syncthing's scan currently seems buggy

@main.command()
@click.option(
  '-v', '--verbose', is_flag=True,
  help='Show synchronize progress.'
)
@click.argument(
  'path', nargs=1, 
  type=click.Path(exists=True, writable=True, resolve_path=True), 
)
def refresh(**kwargs):
  ''' Force synchronization of directory. '''

  output = cli_syncthing_adapter.refresh(**kwargs)

  if output:
    click.echo("%s" % output)

  if kwargs['verbose']:
    with click.progressbar(
      length=100,
      label='Synchronizing') as bar:

      progress = 0

      while not progress == 100:
        progress = cli_syncthing_adapter.refresh(progress=True)

"""
