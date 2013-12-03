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








# CHECK FOR BANNED ITEMS AROUND LINE 181
            #print "______________________"
            #print "path", path
            #print "root", root
            #print "f", f
            
            '''
            # gotta be a way more pythonic way of doing this
            banned = ['.git', '.py', '.yaml', '.patch', '.hs', '.occ', '.md', '.markdown', '.mdown']
            cont = False
            for b in banned:
                if b in path:
                    cont = True
            if cont:
                continue
            '''
