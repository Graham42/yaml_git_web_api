"""
    api.repo
    ~~~~~~~~

    Wrap functionality for the git repo behind the filesystem db.
"""

import os
from pygit2 import clone_repository, discover_repository, Repository, Tree
from api import config, ConfigException

# Create branch: repo.create_branch("testing", repo[repo.lookup_branch("master").target])
# Commit on branch: repo.create_commit(author, author, "msg", tree, (repo.lookup_branch("testing").target,))
# Delete branch: repo.lookup_branch("testing").delete()


class NotEmptyRepoError(IOError):
    """Raised when an empty folder was expected, ie., for cloning."""


def clone():
    """Pull in a fresh copy of the data repo."""
    repo_dir = config['DATA_LOCAL']
    repo_uri = config['DATA_REMOTE']

    # set up the directory for the repo
    if not os.path.isdir(repo_dir):
        try:
            os.makedirs(repo_dir)
        except FileExistsError:
            raise ConfigException('The provided DATA_LOCAL directory, {}, is a file.'.format(repo_dir))
        except PermissionError:
            raise ConfigException('No write access for the provided DATA_LOCAL diretory ({}).'.format(repo_dir))

    # make sure we're workin with a fresh directory
    if len(os.listdir(repo_dir)) > 0:
        raise NotEmptyRepoError()

    # grab some data!
    repo = clone_repository(repo_uri, repo_dir)


def path_files(path, revision=None):
    repository_path = discover_repository(config['DATA_LOCAL'])
    repo = Repository(repository_path)
    if revision is None:
        commit = repo.revparse_single('refs/heads/'+config['MAIN_BRANCH'])
    else:
        commit = repo[revision]
    tree = commit.tree
    try:
        tree_entry = tree[path]
    except KeyError as e:
        return None

    if hasattr(repo[tree_entry.id], 'data'):
        # is a file
        return (path,)
    else:
        # is a directory
        return tuple([os.path.join(path, e.name) for e in repo[tree_entry.id]])


def file_contents(path, revision=None):
    repository_path = discover_repository(config['DATA_LOCAL'])
    repo = Repository(repository_path)
    if revision is None:
        commit = repo.revparse_single('refs/heads/'+config['MAIN_BRANCH'])
    else:
        commit = repo[revision]
    tree = commit.tree
    try:
        tree_entry = tree[path]
    except KeyError as e:
        return None

    return getattr(repo[tree_entry.id], 'data', None)


def get_commit(revision):
    repository_path = discover_repository(config['DATA_LOCAL'])
    repo = Repository(repository_path)
    return repo.revparse_single(revision)


def get_named_commit(ref_name):
    return get_commit('refs/heads/' + ref_name)


def get_latest_commit():
    return get_named_commit(config['MAIN_BRANCH'])
