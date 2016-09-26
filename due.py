# coding=utf-8

import pytz
import os
import shutil

from git import Repo
from github3 import login
from datetime import datetime


base_dir = './inbox/'
project_basename = 'project-1-multithreaded-wordcount'
local_timezone = pytz.timezone('EST')

gh = login(token="<your_token>")

repos = [r for r in gh.iter_repos(type='private') if r.name.startswith(project_basename)]


if os.path.isdir(base_dir):
    shutil.rmtree(base_dir)

cloned = 0
for r in repos:
    pushed_time = r.pushed_at.astimezone(local_timezone)
    from_now = int((datetime.now(tz=local_timezone) - pushed_time).total_seconds()) // 60
    print("Cloning {:<50} pushed at {}, {:>6} minutes from now".format(r.name, pushed_time, from_now))
    Repo.clone_from(r.ssh_url, os.path.join(base_dir, r.name))
    cloned += 1

print("Cloned {} repos".format(cloned))
