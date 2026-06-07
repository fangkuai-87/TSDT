import random
from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run

# 已经替换成了你自己的 GitHub 仓库
REPO_URL = 'https://github.com/fangkuai-87/TSDT.git'


def deploy():
    # env.user 和 env.host 会在运行时自动获取（fangkuai 和 123.57.141.186）
    site_folder = f'/home/{env.user}/sites/{env.host}'
    source_folder = site_folder + '/source'

    # 1. 检查并创建基础文件夹 (database, static, virtualenv, source)
    _create_directory_structure_if_necessary(site_folder)

    # 2. 从 GitHub 拉取最新代码
    _get_latest_source(source_folder)

    # 3. 自动修改 settings.py (关闭 DEBUG，自动填入 IP，生成密钥)
    _update_settings(source_folder, env.host)

    # 4. 创建虚拟环境并安装 requirements.txt 里的依赖
    _update_virtualenv(source_folder)

    # 5. 自动收集静态文件 (CSS/JS) 给 Nginx
    _update_static_files(source_folder)

    # 6. 自动执行数据库建表/更新
    _update_database(source_folder)


# ================== 下面是各个步骤的具体实现 ==================

def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database', 'static', 'virtualenv', 'source'):
        run(f'mkdir -p {site_folder}/{subfolder}')


def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run(f'cd {source_folder} && git fetch')
    else:
        run(f'git clone {REPO_URL} {source_folder}')
    # 获取本地最新的 commit 记录，让服务器与本地保持绝对同步
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f'cd {source_folder} && git reset --hard {current_commit}')


def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/notes/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path,
        'ALLOWED_HOSTS =.+$',
        f'ALLOWED_HOSTS = ["{site_name}"]'
        )
    secret_key_file = source_folder + '/notes/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, f'SECRET_KEY = "{key}"')
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run(f'python3.9 -m venv {virtualenv_folder}')
    run(f'{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt')


def _update_static_files(source_folder):
    run(
        f'cd {source_folder}'
        ' && ../virtualenv/bin/python manage.py collectstatic --noinput'
    )


def _update_database(source_folder):
    run(
        f'cd {source_folder}'
        ' && ../virtualenv/bin/python manage.py migrate --noinput'
    )