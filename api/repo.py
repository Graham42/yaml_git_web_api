"""
    api.repo
    ~~~~~~~~

    Wrap functionality for the git repo behind the filesystem db.
"""

import os
import pyaml as pretty_yaml
from pygit2 import clone_repository, discover_repository, Repository, Tree,
Signature
from api import config, ConfigException

# Create branch: repo.create_branch("testing", repo[repo.lookup_branch("master").target])
# Commit on branch: repo.create_commit(author, author, "msg", tree, (repo.lookup_branch("testing").target,))
# Delete branch: repo.lookup_branch("testing").delete()

repository_path = discover_repository(config['DATA_LOCAL'])
local_repo = Repository(repository_path)


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


def _get_tree(revision):
    if revision is None:
        commit = local_repo.revparse_single('refs/heads/'+config['MAIN_BRANCH'])
    else:
        commit = local_repo[revision]
    return commit.tree


def path_files(path, revision=None):
    tree = _get_tree(revision)
    try:
        tree_entry = tree[path]
    except KeyError as e:
        return None

    if hasattr(local_repo[tree_entry.id], 'data'):
        # is a file
        return (path,)
    else:
        # is a directory
        return tuple([os.path.join(path, e.name) for e in local_repo[tree_entry.id]])


def file_contents(path, revision=None):
    tree = _get_tree(revision)
    try:
        tree_entry = tree[path]
    except KeyError as e:
        return None

    return getattr(local_repo[tree_entry.id], 'data', None)


def get_commit(revision):
    return local_repo.revparse_single(revision)


def get_named_commit(ref_name):
    return local_repo.revparse_single('refs/heads/' + ref_name)


def get_latest_commit():
    return local_repo.revparse_single(config['MAIN_BRANCH'])


def write_file(path, data, token):
    try:
        branch = local_repo.create_branch(token, get_latest_commit())
    except Exception as e:
        # TODO more specific exception
        branch = repo.lookup_branch('master')

    author = committer = Signature('Joe S', 'joes@example.com')
    print(path)
    print(pretty_yaml.dump(data, string_val_style='>'))

    return token
