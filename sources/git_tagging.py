import sys

from github import Github, Tag
from github.PaginatedList import PaginatedList


class RepositoryTagger:
    def __init__(self, username:str, token:str, repo_name:str):
        self.username = username
        self.token = token
        self.repo_name = repo_name
        self._fetch_repository()

    def _fetch_repository(self):
        # github authentication through an access token
        self.github_obj = Github(self.token)
        # fetching the repository
        self.repository = self.github_obj.get_repo('{}/{}'.format(self.username, self.repo_name))

    def tag_latest_commit(self):
        latest_commits = self._get_latest_commits()
        if not self._check_tagged_commit(latest_commits[0].sha):
            next_tag_name = self._next_tag_name()
            new_tag = self.repository.create_git_tag(
                tag=next_tag_name,
                message=next_tag_name,
                object=latest_commits[0].sha,
                type='commit'
            )
            # creating reference to the tag
            reference = self.repository.create_git_ref('refs/tags/{}'.format(next_tag_name), new_tag.sha)

    def create_release(self, tag:Tag=None):
        if not tag:
            tag = self._get_latest_tag()
        latest_release = self._get_latest_release()
        if latest_release:
            next_release_description = self._add_tag_note(head_commit=tag.commit.commit, base_commit=self._check_commit_from_tag(latest_release.tag_name))
        else:
            next_release_description = tag.commit.comments_url
        release = self.repository.create_git_release(tag.name, tag.name, next_release_description, draft=False, prerelease=False)
        return release

    def _get_latest_tag(self):
        all_tags = self.repository.get_tags()
        if all_tags:
            ordered_tags = sorted(all_tags, key=lambda x: x.commit.commit.committer.date, reverse=True)
            return ordered_tags[0]
        return None

    def _get_latest_release(self):
        all_releases = self.repository.get_releases()
        if all_releases:
            if isinstance(all_releases, PaginatedList):
                ordered_releases = sorted(all_releases, key=lambda x: x.created_at, reverse=True)
                return ordered_releases[0]
            else:
                return all_releases
        return None

    def _get_latest_commits(self):
        'Fetching the latest commit to tag'
        all_commits = self.repository.get_commits()
        if all_commits:
            ordered_commits = sorted(all_commits, key=lambda x: x.commit.committer.date, reverse=True)
            return ordered_commits[0:2]
        else:
            return None

    def _check_tagged_commit(self, sha_commit):
        all_tags = self.repository.get_tags()
        for tag in all_tags:
            if tag.commit.commit.sha == sha_commit:
                return True
        return False

    def _check_commit_from_tag(self, tag_name):
        all_tags = self.repository.get_tags()
        for tag in all_tags:
            if tag.name == tag_name:
                return tag.commit.commit
        return None

    def _next_tag_name(self):
        all_tags = self.repository.get_tags()
        ordered_tags = sorted(all_tags, key=lambda x: x.commit.commit.committer.date, reverse=True)
        tag_name = str(ordered_tags[0].name).split('.')
        tag_name[3] = str(int(tag_name[3]) +1)
        return '.'.join(tag_name)

    def _add_tag_note(self, base_commit, head_commit):
        comparison = self.repository.compare(base=base_commit.sha, head=head_commit.sha)
        result = 'Diff url = ' + comparison.diff_url + '\n \n'
        result += 'Changes:'
        for file in comparison.files:
            result += 'Filename = '+str(file.raw_data['filename']) + '\n'
            result += '     status' + str(file.raw_data['status']) + '\n'
            result += '     additions' + str(file.raw_data['additions']) + '\n'
            result += '     deletions' + str(file.raw_data['deletions']) + '\n'
            result += '     changes' + str(file.raw_data['changes']) + '\n'
            result += '     blob_url' + str(file.raw_data['blob_url']) + '\n'
            result += '     patch' + str(file.raw_data['patch']) + '\n \n'
        return result


if __name__ == "__main__":
    parameters = sys.argv[1:]
    repository_wrapper = RepositoryTagger(parameters[0], parameters[1], parameters[2])
    #repository_wrapper.tag_latest_commit()
    repository_wrapper.create_release()