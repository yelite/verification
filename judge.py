# coding=utf-8
import os
import csv
import time

from subprocess import Popen, PIPE
from functools import lru_cache
from collections import defaultdict

cache_folder = 'cache/'
code_folder = '590/p1/'
basename = 'project-1-multithreaded-wordcount'

massive_target = [
    "king-james-version-bible.txt",
    "random.txt",
    "random2.txt",
    "random2.txt",
    "war-and-peace.txt"
] * 8

testcases = [
    (1, ["random.txt"]),
    (2, ["random.txt", "random2.txt"]),
    (2, massive_target[:]),
    (4, massive_target[:]),
    (6, massive_target[:]),
]

testcases = [(n, [os.path.join('data', f) for f in files]) for n, files in testcases]


def get_homework_directories(name=None):
    if name:
        return [os.path.join(code_folder, "{}-{}".format(basename, name))]
    else:
        return [d.path for d in os.scandir(code_folder) if d.name.startswith(basename)]


def get_username(d):
    d = os.path.split(d)[-1]
    return d[len(basename) + 1:]


def compile_homework(name=None):
    directories = get_homework_directories(name)
    for d in directories:
        p = Popen("find . -name '*.java' -exec javac -d . {} +", shell=True, cwd=d)
        p.communicate()


def scan_empty_repo():
    directories = get_homework_directories()
    for d in directories:
        if not [d for d in os.scandir(d) if not d.name.startswith('.')]:
            yield get_username(d)


def scan_missing_class():
    directories = get_homework_directories()
    empty_name = set(scan_empty_repo())

    for d in directories:
        if not (os.path.isfile(os.path.join(d, 'wordcount.class'))
                or os.path.isfile(os.path.join(d, 'WordCount.class'))):

            name = get_username(d)
            if name not in empty_name:
                yield name


def test_output(test_arguments, threads, path='.', cls_name='wordcount'):
    p = Popen(['java', '-cp', path, '-Dfile.encoding=utf-8', cls_name, str(threads)] + test_arguments,
              stdout=PIPE)
    stdout, _ = p.communicate()
    return stdout


@lru_cache(16)
def ref_output(*args):
    cache_name = os.path.join(cache_folder, str(hash(args)))
    if os.path.exists(cache_name):
        return open(cache_name).read()
    else:
        p = Popen(['python', 'wordcount.py'] + list(args), stdout=PIPE)
        stdout, _ = p.communicate()
        with open(cache_name, 'wb') as f:
            f.write(stdout)
        return stdout


def test(name, cls_path, cls_name, thread_num, args, result):
    t = time.time()
    java_result = test_output(args, thread_num, cls_path, cls_name=cls_name)
    result.record_time(name, time.time() - t)

    ref_result = ref_output(*args)

    if java_result != ref_result:
        return "failed"
    else:
        return ""


possible_names = ['wordcount', 'WordCount', 'WordCount1', 'Wordcount1', 'Wordcount', 'wordCount']
def find_cls(name):
    root = get_homework_directories(name)[0]
    walk = list(os.walk(root))
    for n in possible_names:
        for d, _, f in walk:
            if "{}.class".format(n) in f:
                return root, "{}.{}".format(d[len(root) + 1:], n) if d != root else n
    else:
        raise Exception("Class not found for {}".format(name))


class TestResult:
    def __init__(self):
        self.result = defaultdict(list)

    def record(self, name, result):
        self.result[name].append(result)

    def record_time(self, name, t):
        t = "{:.2f}".format(t)
        self.record(name, t)

    def persist(self, path="report.csv"):
        result = sorted(self.result.items(), key=lambda x: x[0])

        with open(path, 'w') as f:
            writer = csv.writer(f)
            for name, data in result:
                writer.writerow([name, *data])


def test_all(name, result):
    print("testing {}".format(name))
    cls_path, cls_name = find_cls(name)
    for i, (thread_num, args) in enumerate(testcases, start=1):
        r = test(name, cls_path, cls_name, thread_num, args, result)
        result.record(name, r)


def grade_homework(name=None, skips=None):
    if skips is None:
        skips = set()

    result = TestResult()

    empty_repo = set(scan_empty_repo())
    for d in get_homework_directories(name):
        username = get_username(d)
        if username not in empty_repo and username not in skips:
            test_all(username, result)

    if name is None:
        result.persist()
    else:
        print(result.result)


if __name__ == '__main__':
    # print('\n'.join(scan_missing_class()))
    grade_homework(skips={"apple11"})
    # compile_homework()
