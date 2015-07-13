"""Command line interface for executor invocations."""
import sys
import time

from argparse import ArgumentParser
from mirakuru import all_executors


parser = ArgumentParser(description='Execute a process, check when actually '
                        'starts working and terminate the process when '
                        'terminating `mirakuru` due to a received signal.')
subcommands = parser.add_subparsers()

for executor_class in all_executors:
    name = executor_class.CLI_NAME
    if name is not None:
        executor_subcommand = subcommands.add_parser(name)
        executor_class.populate_command(executor_subcommand)
        executor_subcommand.set_defaults(func=executor_class.as_command)


def cli_entry():
    """Dispatch and run the executor."""
    args = sys.argv[1:]
    # Find the '--' separator that splits the executor command line and the
    # one of the executed process.
    try:
        separator = args.index('--')
    except ValueError:
        print '-- needed'
        return

    executor_args, process_args = args[:separator], args[separator + 1:]

    args = parser.parse_args(executor_args)
    args.process_args = process_args
    args.func(args)

    # Here we should probably sleep indefinitely and handle signals sent to
    # mirakuru to be able to exit.
    # Or maybe exit (with an error?) when the subprocess exits.
    print 'checks passed'
    time.sleep(100000)
