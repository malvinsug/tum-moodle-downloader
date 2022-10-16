import argparse
import json

import globals
import authentication
import credential_handler
import moodle_downloader

import os
import datetime
import sys 

# Instantiate the argument parser
arg_parser = argparse.ArgumentParser()


def setup_parser():
    # Add subparsers for the different available commands
    subparsers = arg_parser.add_subparsers()

    list_command_description = "List available resources of the specified \"course\" " \
                               "or, if no course is specified, list available courses"
    list_parser = subparsers.add_parser("list",
                                        description=list_command_description,
                                        help=list_command_description)

    # python src/main.py list -f "<course name>"
    list_parser.add_argument('-f', '--files',
                             action='store_true',
                             help="only prints available files")
    list_parser.add_argument("course",
                             type=str,
                             nargs='?',
                             default='*',
                             help="name of the course of which the resources are to be listed")
    
    # Set the function which is to be executed, if the 'list' command is provided
    list_parser.set_defaults(func=moodle_downloader.list_resources)

    download_command_description = "Download resources which match a \"file_pattern\" " \
                                   "from a \"course\" into a \"destination\" path. " \
                                   "If parameters are omitted they are retrieved from  \"src/course_config.json\""
    download_parser = subparsers.add_parser("download",
                                            description=download_command_description,
                                            help=download_command_description)
    download_parser.add_argument('course',
                                 type=str,
                                 nargs='?',
                                 help="name of the course from which to download")
    download_parser.add_argument('file_pattern',
                                 type=str,
                                 nargs='?',
                                 help="name pattern for the resources which are to be downloaded")
    download_parser.add_argument('destination',
                                 type=str,
                                 nargs='?',
                                 help="path at which the download(s) should be stored")
    # Set the function which is to be executed, if the 'download' command is provided
    download_parser.set_defaults(func=moodle_downloader.download)


def main_download_moodle_tum():
    setup_parser()
    args = arg_parser.parse_args()

    with open(globals.DOWNLOAD_CONFIG_PATH, mode='r', encoding='utf-8') as main_config:
        config_data = json.load(main_config)

    username, password = credential_handler.get_credentials()

    session = authentication.start_session(
        username,
        password
    )
    if session is None:
        print('Could not start Moodle session.')
        exit(1)

    globals.set_global_session(session)

    # Call the function which is set based on the command provided in the arguments
    # (see 'setup_parser' above for details)
    args.func(args)

def commit_and_push_git():

    git_status = "git status --porcelain"
    print(git_status)
    git_status_output = os.popen(git_status).read()

    if git_status_output == "":
        print("No changes. No need to commit.")
        return
    
    git_add = 'git add .'
    print(git_add)
    os.system(git_add)

    date_now = datetime.datetime.now()
    git_commit = f'git commit -m "update by bot {date_now}"'
    print(git_commit)
    os.system(git_commit)

    git_push = 'git push'
    print(git_push)
    os.system(git_push)


if __name__ == "__main__":
    change_dir = ""
    print(change_dir)
    os.system(change_dir)

    date_now = datetime.datetime.now()
    stdoutOrigin=sys.stdout 
    sys.stdout = open(f"log_{date_now}.txt", "w")
    
    print("Start downloading files from TUM Moodle...")
    main_download_moodle_tum()
    print("Downloading process finished.")
    print("")
    print("Start updating git repository...")
    commit_and_push_git()
    print("Update is pushed to repository.")
