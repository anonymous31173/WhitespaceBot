import requests
import settings
import simplejson
import subprocess
import sys
import argparse
import time
import os
from os.path import join
import shutil
import urllib2
import json

#pseudo
#    take name from list
#    scan names for most names most popular repo
#    fork it - POST /repos/:user/:repo/forks
#    clone it
#    switch branch
#    fix it
#    commit it!
#    push it
#    submit pull req
#    remove name from list


def main():
    parser = argparse.ArgumentParser(description='Whitespace annihilating GitHub robot.\nBy Rich Jones - Gun.io - rich@gun.io')
    parser.add_argument('-u', '--users', help='A text file with usernames.', default='users.txt')
    parser.add_argument('-o', '--old-users', help='A text file with usernames.', default='old_users.txt')
    parser.add_argument('-c', '--count', help='The maximum number of total requests to make.', default=999999)
    parser.add_argument('-v', '--verbose', help='Make this sucker loud? (True/False)', default=True)
    args = parser.parse_args()

    auth = (settings.username, settings.password)

    print args

    old_users_file = args.old_users
    old_users = load_user_list(old_users_file)

    users = args.users
    olders = args.old_users
    new_users = load_user_list(users)
    user = get_user(users, olders)

    #XXX: Potential deal breaker in here!
    count = 0
    while user in old_users:
        print "We've already done that user!"
        user = get_user(users)
        count = count + 1
    if count > len(new_users):
        return

    repos = 'https://api.github.com/users/' + user + '/repos'
    r = requests.get(repos, auth=auth)

    if (r.status_code == 200):
        resp = simplejson.loads(r.content)
        topwatch = 0
        top_repo = ''
        for repo in resp:
            if repo['watchers'] > topwatch:
                top_repo = repo['name']
                topwatch = repo['watchers']
        print dir(repo)

        print user + "'s most watched repo is " + top_repo + " with " + str(topwatch) + " watchers. Forking."

        repo = top_repo
        print "GitHub Forking.."
        clone_url = fork_repo(user, repo)
        print "Waiting.."
        time.sleep(30)
        print "Cloning.."
        time.sleep(5)
        print clone_url
        cloned = clone_repo(clone_url)
        if not cloned:
            return
        print "Changing branch.."
        time.sleep(5)
        branched = change_branch(repo)
        print "Fixing repo.."
        time.sleep(10)
        fixed = fix_repo(repo)
        print "Comitting.."
        time.sleep(5)
        commited = commit_repo(repo)
        print "Pushing.."
        time.sleep(5)
        pushed = push_commit(repo)
        print "Submitting pull request.."
        time.sleep(5)
        submitted = submit_pull_request(user, repo)
        print "Delting local repo.."
        time.sleep(5)
        deleted = delete_local_repo(repo)
        print "Olding user.."
        time.sleep(5)
        old = save_user(old_users_file, user)


def save_user(old_users_file, user):
    with open(old_users_file, "a") as id_file:
        id_file.write(user + '\n')
    return True


def load_user_list(old_users):
    text_file = open(old_users, "r")
    old = text_file.readlines()
    text_file.close()
    x = 0
    for hid in old:
        old[x] = hid.rstrip()
        x = x + 1
    return old


def get_user(users):
    text_file = open(users, "r")
    u = text_file.readlines()
    text_file.close()
    return choice(u).rstrip()

def get_user(users_file, old_users_file):
    # Get the first user not already processed
    old_users = load_user_list(old_users_file)
    users = load_user_list(users_file)
    #new_users = users.difference(old_users)
    new_users = list(set(users) - set(old_users))
    return new_users.pop() if new_users else None

def fork_repo(user, repo):
    url = 'https://api.github.com/repos/' + user + '/' + repo + '/forks'
    auth = (settings.username, settings.password)
    print settings.username
    r = requests.post(url, auth=auth)
    print r.status_code
    #if (r.status_code == 201):
    if (r.status_code == 202):
        resp = simplejson.loads(r.content)
        return resp['ssh_url']
    else:
        return None


def clone_repo(clone_url):
    try:
        args = ['/usr/bin/git', 'clone', clone_url]
        p = subprocess.Popen(args)
        p.wait()
        return True
    except Exception, e:
        return False


def change_branch(repo):
    #XXX fuck this
    #gitdir = os.path.join(settings.username, repo, ".git")
    #repo = os.path.join(settings.username, repo)
    gitdir = os.path.join(repo, ".git")

    try:
        args = ['/usr/bin/git', '--git-dir', gitdir, '--work-tree', repo, 'branch', 'clean']
        p = subprocess.Popen(args)
        p.wait()
        args = ['/usr/bin/git', '--git-dir', gitdir, '--work-tree', repo, 'checkout', 'clean']
        p = subprocess.Popen(args)
        p.wait()
        return True
    except Exception, e:
        return False


def fix_repo(repo):
    #gitdir = os.path.join(settings.username, repo, ".git")
    #repo = os.path.join(settings.username, repo)

    gitdir = os.path.join(repo, ".git")

    for root, dirs, files in os.walk(repo):
        for f in files:
            path = os.path.join(root, f)

            # gotta be a way more pythonic way of doing this
            banned = ['.git', '.html', '.css', '.conf', '.ino', '.manifest', '.htaccess', '.py', '.pl', '.service', '.pem', '.txt', '.sh', '.rst', '.po', '.pot', '.js', '.travis', '.yml', '.yaml', 'Makefile', '.patch', '.hs', '.svg', 'html', '.cfg', '.in', 'plugins', '.buildinfo', '.occ', '.md', '.markdown', 'README', 'gateone', '.directory', '.mdown']
            cont = False
            for b in banned:
                if b in path:
                    cont = True
            if cont:
                continue

            p = subprocess.Popen(['file', '-bi', path], stdout=subprocess.PIPE)

            while True:
                o = p.stdout.readline()
                if o == '':
                    break
                #XXX: Motherfucking OSX is a super shitty and not real operating system
                #XXX: and doesn't do file -bi properly
                if 'text' in o:
                    q = subprocess.Popen(['sed', '-i', 's/[ \\t]*$//', path])
                    q.wait()
                    args = ['/usr/bin/git', '--git-dir', gitdir, '--work-tree', repo, 'add', path]
                    pee = subprocess.Popen(args)
                    pee.wait()
                if o == '' and p.poll() != None: break

    git_ignore = os.path.join(repo, '.gitignore')
    if not os.path.exists(git_ignore):
        ignorefile = open(git_ignore, 'w')
        ignore = '# Compiled source #\n' + \
            '###################\n' + \
            '*.com\n' + \
            '*.class\n' + \
            '*.dll\n' + \
            '*.exe\n' + \
            '*.o\n' + \
            '*.so\n' + \
            '*.pyc\n\n' + \
            '# Numerous always-ignore extensions\n' + \
            '###################\n' + \
            '*.diff\n' + \
            '*.err\n' + \
            '*.orig\n' + \
            '*.log\n' + \
            '*.rej\n' + \
            '*.swo\n' + \
            '*.swp\n' + \
            '*.vi\n' + \
            '*~\n\n' + \
            '*.sass-cache\n' + \
            '# Folders to ignore\n' + \
            '###################\n' + \
            '.hg\n' + \
            '.svn\n' + \
            '.CVS\n' + \
            '# OS or Editor folders\n' + \
            '###################\n' + \
            '.DS_Store\n' + \
            'Icon?\n' + \
            'Thumbs.db\n' + \
            'ehthumbs.db\n' + \
            'nbproject\n' + \
            '.cache\n' + \
            '.project\n' + \
            '.settings\n' + \
            '.tmproj\n' + \
            '*.esproj\n' + \
            '*.sublime-project\n' + \
            '*.sublime-workspace\n' + \
            '# Dreamweaver added files\n' + \
            '###################\n' + \
            '_notes\n' + \
            'dwsync.xml\n' + \
            '# Komodo\n' + \
            '###################\n' + \
            '*.komodoproject\n' + \
            '.komodotools\n'
        ignorefile.write(ignore)
        ignorefile.close()
        try:
            args = ['/usr/bin/git', '--git-dir', gitdir, '--work-tree', repo, 'add', git_ignore]
            p = subprocess.Popen(args)
            p.wait()
            return True
        except Exception, e:
            return False

    return True


def commit_repo(repo):
    #gitdir = os.path.join(settings.username, repo, ".git")
    #repo = os.path.join(settings.username, repo)
    gitdir = os.path.join(repo, ".git")

    try:
        message = "Remove whitespace [Gun.io WhitespaceBot]"
        args = ['/usr/bin/git', '--git-dir', gitdir, '--work-tree', repo, 'commit', '-m', message]
        p = subprocess.Popen(args)
        p.wait()
        return True
    except Exception, e:
        print e
        return False


def push_commit(repo):
    #gitdir = os.path.join(settings.username, repo, ".git")
    #repo = os.path.join(settings.username, repo)
    gitdir = os.path.join(repo, ".git")
    try:
        args = ['/usr/bin/git', '--git-dir', gitdir, '--work-tree', repo, 'push', 'origin', 'clean']
        p = subprocess.Popen(args)
        p.wait()
        return True
    except Exception, e:
        print e
    return False


def basic_authorization(user, password):
    s = user + ":" + password
    return "Basic " + s.encode("base64").rstrip()

def submit_pull_request(user, repo):
    import base64
    gitconfig()
    auth = (settings.username, settings.password)
    basic_auth = basic_authorization(settings.username, settings.password)
    url = 'https://api.github.com/repos/' + user + '/' + repo + '/pulls'
    #url = 'https://salvius:robot8888@api.github.com/repos/' + user + '/' + repo + '/pulls'

    with open('message.txt', 'r') as f:
        message = f.read()

    headers={'Authorization': basic_auth,
             'Content-Type': 'application/json',
             'Accept': '*/*',
             'User-Agent': 'WhitespaceRobot/Gunio'}
    params = {'title': 'Hi! I cleaned up your code for you!',
              'body': message,
              'base': 'master',
              'head': 'GunioRobot:clean'}
    json_data = json.dumps(params)

    req = urllib2.Request(url, data=json.dumps(params))

    base64string = base64.encodestring('%s:%s' % (settings.username, settings.password)).replace('\n', '')
    req.add_header("Authorization", "Basic %s" % base64string)

    f = urllib2.urlopen(req)
    return True

def delete_local_repo(repo):
    repo = os.path.join(settings.username, repo)
    try:
        shutil.rmtree(repo)
        return True
    except Exception, e:
        return False


if __name__ == '__main__':
        sys.exit(main())
