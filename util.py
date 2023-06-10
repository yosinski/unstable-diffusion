import subprocess as sp


def run_cmd(cmd_tuple, check=False, concat_stderr=False):
    proc = sp.run(cmd_tuple, capture_output=True, check=check)
    #out, err = proc.communicate()
    out = proc.stdout.strip().decode()
    if concat_stderr:
        err = proc.stderr.strip().decode()
        if len(err) > 0:
            out += '\n' + err
    return out
