from github import Github


class RepositoryTagWrapper:
    def __init__(self, username, token, repo_name):
        self.username = username
        self.token = token
        self.repo_name = repo_name

    def tag_repository(self):
        # github authentication through an access token
        github_obj = Github(self.token)
        # fetching the repository
        repository = github_obj.get_repo(self.repo_name)
        # manually creating tag. Example new_tag = repository.create_git_tag('v.0.1', 'First tag', 'sha_commit', 'commit')
        new_tag = repository.create_git_tag('tag_name', 'message', 'object', 'type')
        # manually creating reference to the tag. Example  reference = repository.create_git_ref('refs/tags/v.0.1', 'sha_tag')
        reference = repository.create_git_ref('refs/tags/tag_name', 'object')
        # making release. Example release = repository.create_git_release('v.0.1', 'release 0.1', 'first release', draft=False, prerelease=False)
        release = repository.create_git_release('tage_name', 'release_name', 'message', draft=False, prerelease=False)

    def _find_next_tag(self):
        pass
