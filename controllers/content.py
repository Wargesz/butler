from os import makedirs, walk

PREFIXES = ['./content/public/', './content/private/']


def createContentDir(user):
    for p in PREFIXES:
        makedirs(f'{p}user-{user.username}')


def buildVaults(username):
    public = dict()
    private = dict()
    for (root, dirs, files) in walk('./content/public/'):
        root = root.replace('./content/public/', '')
        if root == '':
            continue
        public[root] = files
    for (root, dirs, files) in walk(f'./content/public/{username}'):
        root = root.replace(f'./content/public/{username}', '')
        if root == '':
            continue
        private[root] = files
    return [public, private]


def getUsers():
    for (_, dirs, _) in walk('./content/public/'):
        return dirs
