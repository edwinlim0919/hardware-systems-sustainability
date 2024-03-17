import subprocess
import signal
import time

from threading import Timer


currently_logging = True


def remove_existing_pcm_logs(
    log_file_path: str,
    pcm_cmds: list[str]
):
    for pcm_cmd in pcm_cmds:
        log_file_name = log_file_path + f'_{pcm_cmd}'
        
        try:
            subprocess.run(
                ['sudo', 'rm', log_file_name],
                check=True
            )
            print(f'deleted {log_file_name}')
        except FileNotFoundError:
            print(f'file {log_file_name} not found')
        except PermissionError:
            print(f'permission denied to delete {log_file_name}')
        except Exception as e:
            print(f'error deleting {log_file_name}: {e}')


def run_pcm_commands(
    log_file_path: str,
    logging_interval: int,
    cmd_runtime: int,
    pcm_cmds: list[str]
):
    global currently_logging
    if not currently_logging:
        return

    for pcm_cmd in pcm_cmds:
        log_file_name = log_file_path + f'_{pcm_cmd}'

        with open(log_file_name, 'a') as log_file:
            log_file.write(f'TIMESTAMP: {time.time()}\n')
            full_pcm_cmd = f'sudo {pcm_cmd} >> {log_file_name}'
            kill_pcm_cmd = f"pgrep -x '{pcm_cmd}' | grep -v grep | grep -v python | xargs sudo kill"

            try:
                print(f'run_pcm_commands starting pcm_process: {full_pcm_cmd}')
                pcm_process = subprocess.Popen(
                    full_pcm_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                print(f'run_pcm_commands sleeping {cmd_runtime} seconds...')
                time.sleep(cmd_runtime)

                print(f'killing all pcm process with sudo...')
                subprocess.run(
                    kill_pcm_cmd,
                    shell=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                log_file.write(f'Error running {full_pcm_cmd}: {e}\n')

    Timer(
        logging_interval,
        run_pcm_commands,
        args=(
            log_file_path,
            logging_interval,
            cmd_runtime,
            pcm_cmds
        )
    ).start()