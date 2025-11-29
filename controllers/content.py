from os import makedirs, walk
from models.models import User

PREFIXES = ['./content/public/', './content/private/']


class UserContent():
    def __init__(self, username):
        self.username = username
        self.content = []

    def __repr__(self):
        return f'{self.username}: {self.content}'

    def empty(self):
        return not len(self.content)


def createContentDir(user):
    for p in PREFIXES:
        makedirs(f'{p}user-{user.username}')


def buildVaults(username):
    userContents = []
    for user in getUsers():
        vault = buildPublicVaultForUser(user)
        if vault.empty():
            continue
        userContents.append(vault)
    privateContent = buildPrivateVaultForAuthedUser(username)
    return [userContents, privateContent]


def buildPublicVaultForUser(username):
    userContent = UserContent(username)
    for (root, dirs, files) in walk(f'./content/public/user-{username}'):
        root = root.replace(f'./content/public/user-{username}', '')
        if len(dirs) == 0 and len(files) == 0:
            continue
        files.sort()
        userContent.content.append((root, files))
    return userContent


def buildPrivateVaultForAuthedUser(username):
    privateContent = UserContent(username)
    for (root, dirs, files) in walk(f'./content/private/user-{username}'):
        root = root.replace(f'./content/private/user-{username}', '')
        if len(dirs) == 0 and len(files) == 0:
            continue
        files.sort()
        privateContent.content.append((root, files))
    return privateContent


def getUsers():
    return [x[0] for x in User.query.with_entities(User.username).all()]
