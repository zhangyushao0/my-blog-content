import subprocess
import time

def fetch_and_check_updates(repo_dir):
    """
    检查指定git仓库是否有更新。
    """
    try:
        # 切换到仓库目录
        # subprocess.run(['cd', repo_dir], check=True, shell=True) # 这种方式在这里不适用
        # 使用cwd参数指定工作目录

        # 先执行git fetch来更新远程仓库状态
        subprocess.run(['git', 'fetch'], check=True, cwd=repo_dir)

        # 检查本地HEAD与远程origin/HEAD是否一致
        local_head = subprocess.run(['git', 'rev-parse', 'HEAD'], check=True, stdout=subprocess.PIPE, cwd=repo_dir).stdout
        remote_head = subprocess.run(['git', 'rev-parse', 'origin/HEAD'], check=True, stdout=subprocess.PIPE, cwd=repo_dir).stdout

        return local_head != remote_head
    except subprocess.CalledProcessError as e:
        print(f'Error checking for updates: {e}')
        return False

def git_pull(repo_dir):
    """
    执行git pull更新仓库。
    """
    try:
        result = subprocess.run(['git', 'pull'], check=True, stdout=subprocess.PIPE, cwd=repo_dir)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f'Error during git pull: {e}')

repo_dir = '/data/myblog'  # 你的仓库目录

while True:
    if fetch_and_check_updates(repo_dir):
        print("发现新的更新，正在拉取...")
        git_pull(repo_dir)
    else:
        print("没有发现新的更新。")
    time.sleep(300)  # 每5分钟检查一次
