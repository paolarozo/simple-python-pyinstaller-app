import sys

from github import Github


class RepositoryTagWrapper:
    def __init__(self, username, token, repo_name):
        self.username = username
        self.token = token
        self.repo_name = repo_name
        print('parameter user:{} token:{} repo:{}'.format(self.username, self.token, self.repo_name))

    def tag_repository(self):
        # github authentication through an access token
        github_obj = Github(self.token)
        # fetching the repository
        repository = github_obj.get_repo('{}/{}'.format(self.username, self.repo_name))
        # # creating the tag
        new_tag = repository.create_git_tag('v.0.0.1', 'First tag', 'a6316ac76bf7725ea4a9c6f10940b3183ad12a60',
                                            'commit')
        # # creating reference to the tag
        reference = repository.create_git_ref('refs/tags/v.0.0.1', new_tag.sha)

    def _find_next_tag(self):
        pass


if __name__ == "__main__":
    parameters = sys.argv[1:]
    repository_wrapper = RepositoryTagWrapper(parameters[0], parameters[1], parameters[2])
    repository_wrapper.tag_repository()