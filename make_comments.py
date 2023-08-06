from unidiff import PatchSet
import requests
import subprocess
import json

def run_cmd(cmd_str, allow_failure=False, capture_output=True):
    # print(cmd_str)
    output = subprocess.run(cmd_str, shell=True, capture_output=capture_output)
    if output.returncode != 0 and not allow_failure:
        if capture_output:
            stdout = output.stdout.decode()
            stderr = output.stderr.decode()

            print(f"ERROR [{output.returncode}]")
            print("===== STDOUT =====")
            for line in stdout.splitlines():
                print("  ", line)

            print("===== STDERR =====")
            for line in stderr.splitlines():
                print("  ", line)

        exit(output.returncode)

    if capture_output:
        return (output.returncode, output.stdout.decode())
    else:
        return (output.returncode, "")

retcode, pr_info_json = run_cmd('gh pr view --json id,number,title,url,headRefOid', allow_failure=True)
if retcode != 0:
    print('Could not find a pull request associated with this branch')
    exit(1)

pr_info_dict = json.loads(pr_info_json)
print(f'Found PR #{pr_info_dict["number"]}: {pr_info_dict["title"]}')

retcode, repo_diff = run_cmd('git diff --staged -U0')
if retcode != 0:
    print('Could not run git diff')
    exit(1)
if repo_diff == '':
    print('Stage some changes that you want turned into code suggestions')
    exit(1)

repo_ps = PatchSet(repo_diff)

# Need to get the PR diff to check if every repo diff is within the PR diff
pull_diff_resp = requests.get(pr_info_dict['url'] + '.diff')
if pull_diff_resp.status_code != 200:
    print('Failed to get PR diff from GitHub')
pull_ps = PatchSet(pull_diff_resp.text)

for file in repo_ps:
    for hunk in file:
        print(f'Sending {hunk}')
        target_lines = [str(l)[1:] for l in repo_ps[0][0].target_lines()]
        comment_text = '```suggestion\n' + ''.join(target_lines) + '```'
        cmd_str = f"""
            gh api \
            --method POST \
            repos/{{owner}}/{{repo}}/pulls/{pr_info_dict['number']}/comments \
            -H Accept:application/vnd.github+json \
            -F body='{comment_text}' \
            -F commit_id='{pr_info_dict['headRefOid']}' \
            -F path={file.source_file[2:]} \
        """

        if hunk.source_length == 1:
            cmd_str += f' -F line={hunk.source_start}'
        else:
            cmd_str += f""" \
                -F start_line={hunk.source_start} \
                -F line={hunk.source_start + hunk.source_length - 1}
            """

        retcode, output = run_cmd(cmd_str)
