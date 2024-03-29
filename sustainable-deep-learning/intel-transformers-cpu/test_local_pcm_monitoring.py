import argparse
import time

import local_pcm_monitoring


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Testing PCM monitoring daemon.')
    parser.add_argument(
        '--log-file-path',
        required=True,
        type=str,
        help='The prefix path for logging files.'
    )
    parser.add_argument(
        '--logging-interval',
        required=True,
        type=int,
        help='The number of seconds in between PCM logging events.'
    )
    parser.add_argument(
        '--cmd-runtime',
        required=True,
        type=float,
        help='The number of seconds to run each PCM command for.'
    )
    parser.add_argument(
        '--pcm-cmds',
        required=True,
        type=str,
        help='The list of pcm commands to run as root.'
    )
    parser.add_argument(
        '--sleep-time',
        required=True,
        type=int,
        help='The amount of time to let the pcm monitoring to run for.'
    )
    args = parser.parse_args()
    pcm_cmds = args.pcm_cmds.split()

    print(f'Deleting existing log files with the same name...')
    local_pcm_monitoring.remove_existing_pcm_logs(
        args.log_file_path,
        pcm_cmds
    )

    print(f'Starting local PCM monitoring...')
    print(f'log_file_path: {args.log_file_path}')
    print(f'logging_interval: {args.logging_interval}')
    print(f'cmd_runtime: {args.cmd_runtime}')
    print(f'pcm_cmds: {pcm_cmds}')
    local_pcm_monitoring.run_pcm_commands(
        args.log_file_path,
        args.logging_interval,
        args.cmd_runtime,
        pcm_cmds
    )
    print(f'Sleeping for {args.sleep_time} seconds...')
    time.sleep(args.sleep_time)
    local_pcm_monitoring.currently_logging = False
    print('Done.')
    
