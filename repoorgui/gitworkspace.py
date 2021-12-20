from datetime import date, datetime, timezone, timedelta
import threading
import git
import os
from commands import commandfn

# see https://stackoverflow.com/a/39956572
# made changes to return repo object if exits


def is_git_repo(path):
    try:
        r = git.Repo(path)
        _ = r.git_dir
        return True, r
    except git.exc.InvalidGitRepositoryError:
        return False, None


def getRemoteIfExits(repo):
    try:
        return repo.remote()
    except ValueError as ve:
        return None


def getRemoteUrl(remote):
    if remote:
        return next(remote.urls)
    else:
        return None


_limit = 25  # 0 for all


def commit_days_text(numdays):
    if numdays == 0:
        return "today"
    elif numdays == 1:
        return "yesterday"
    elif numdays > 1:
        return str(numdays) + " days ago"
    else:
        "invalid"


def getReposList(updateFunc=None, appstate=None):
    table_rows = []
    _now = datetime.now()
    _td_one_day = timedelta(days=1)
    _completion = 0

    if updateFunc:
        updateFunc(_completion)

    # Get all the subdirectories of the repo parent path (might call this workspace folder).
    _, all_subdirs, other_files = next(os.walk(appstate.workspace_folder))

    # getting the dirs is 10% progress
    if updateFunc:
        _completion = 10
        updateFunc(_completion)

    # checking if the repos are git repos and populating repo object
    # is 80% of the progress
    _loading_total_progress = 90.0
    _count = 0
    _total = len(all_subdirs)
    _item_progress = _loading_total_progress / \
        (_limit if _total > _limit else _total)
    # print('total = ', str(_total), ' item progress = ', str(_item_progress))
    for dir in all_subdirs:
        if _limit > 0:
            _count += 1
        if _limit > 0 and _count >= _limit:
            if updateFunc:
                _completion += _item_progress
                updateFunc(_completion)
            break

        dir_abspath = os.path.abspath(
            os.path.join(appstate.workspace_folder, dir))
        flag, repo = is_git_repo(dir_abspath)
        if flag:
            remote_url = str(getRemoteUrl(getRemoteIfExits(repo)))
            last_commit_datetime = str(repo.head.commit.committed_datetime)
            td_since_last_commit = _now - \
                repo.head.commit.committed_datetime.replace(tzinfo=None)
            # print(td_since_last_commit)
            days_since_last_commit, _ = divmod(
                td_since_last_commit, _td_one_day)
            # print(days_since_last_commit)
            appstate.workspace_repos[dir] = (
                repo, remote_url, last_commit_datetime, commit_days_text(days_since_last_commit))
        if updateFunc:
            _completion += _item_progress
            updateFunc(_completion)

    # Create repository table
    for repo_dir, (repo, remote_url, last_commit_datetime, days_since_last_commit) in appstate.workspace_repos.items():
        table_rows.append([
            str(repo_dir), str(repo.working_dir), remote_url, days_since_last_commit
        ])

    # creating the repo table with details is 10% progress
    if updateFunc:
        _completion = 100
        updateFunc(_completion)

    return table_rows


def updateReposListWindow(window, appstate):
    window.write_event_value('-START-LOADING-PROGRESS-', None)
    table_rows = getReposList(lambda progress: window.write_event_value(
        '-UPDATE-LOADING-PROGRESS-', progress), appstate)
    window.write_event_value('-UPDATE-REPOS-LIST-', table_rows)
    window.write_event_value('-DONE-LOADING-PROGRESS-', None)


@commandfn
def cmd_long_update_repos(window, event, values, appstate=None):
    if appstate and values and values['workspace_folder'] != appstate.workspace_folder:
        appstate.workspace_folder = values['workspace_folder']
        appstate.workspace_repos = {}

    threading.Thread(target=updateReposListWindow,
                     args=(window, appstate, ), daemon=True).start()
