import sys

from github import Github, Tag
from github.Commit import Commit
from github.PaginatedList import PaginatedList


class RepositoryTagger:
    """Automatic tag and release generator"""

    def __init__(self, token: str, repo_name: str):
        self.token = token
        self.repo_name = repo_name
        # github authentication through an access token
        self.github_obj = Github(self.token)
        # fetching the repository
        self.repository = self.github_obj.get_repo('{}'.format(self.repo_name))

    def tag_latest_commit(self):
        """Function that tags the latest commit"""
        latest_commit = self._get_latest_commits(number_commits=1)
        if not self._check_commit_has_tag(latest_commit):
            next_tag_name = self._get_next_tag_name()
            new_tag = self.repository.create_git_tag(
                tag=next_tag_name,
                message=next_tag_name,
                object=latest_commit[0].sha,
                type='commit'
            )
            # creating reference to the tag
            reference = self.repository.create_git_ref('refs/tags/{}'.format(next_tag_name), new_tag.sha)

    def create_semantic_release(self):
        """Function that creates a release for the latest tag contains the word -release-"""
        tag = self._get_latest_tag()
        if tag:
            latest_release = self._get_latest_release()
            if latest_release and not self._check_tag_has_release(tag) and 'release' in str(tag.name):
                next_release_description = self._create_release_notes(
                    head_commit=tag.commit.commit,
                    base_commit=self._get_commit_from_tagname(latest_release.tag_name)
                )
                release = self.repository.create_git_release(
                    tag=tag.name,
                    name=tag.name,
                    message=next_release_description,
                    draft=False,
                    prerelease=False
                )

    def create_release(self, tag: Tag = None):
        """Function that creates a release for the latest tag found or the one provided"""
        if not tag:
            tag = self._get_latest_tag()

        latest_release = self._get_latest_release()
        if latest_release and not self._check_tag_has_release(tag):
            next_release_description = self._create_release_notes(
                head_commit=tag.commit.commit,
                base_commit=self._get_commit_from_tagname(latest_release.tag_name)
            )
            release = self.repository.create_git_release(
                tag=tag.name,
                name=tag.name,
                message=next_release_description,
                draft=False,
                prerelease=False
            )

    def _get_latest_tag(self):
        """Function to fetch the latest tag"""
        all_tags = self.repository.get_tags()
        if not isinstance(all_tags, PaginatedList):
            all_tags = [all_tags]
        if all_tags:
            ordered_tags = sorted(all_tags, key=lambda x: x.commit.commit.committer.date, reverse=True)
            return ordered_tags[0]
        return None

    def _get_latest_release(self):
        """Function to fetch the latest release"""
        all_releases = self.repository.get_releases()
        if not isinstance(all_releases, PaginatedList):
            all_releases = [all_releases]
        if all_releases:
            ordered_releases = sorted(all_releases, key=lambda x: x.created_at, reverse=True)
            return ordered_releases[0]
        return None

    def _get_latest_commits(self, number_commits: int = 2):
        """Fetching the latest N commits"""
        all_commits = self.repository.get_commits()
        if not isinstance(all_commits, PaginatedList) and all_commits:
            return all_commits
        if all_commits:
            ordered_commits = sorted(all_commits, key=lambda x: x.commit.committer.date, reverse=True)
            return ordered_commits[0:number_commits]
        else:
            return None

    def _check_commit_has_tag(self, commit: Commit):
        """Function to check if a commit has a tag"""
        all_tags = self.repository.get_tags()
        if not isinstance(all_tags, PaginatedList) and all_tags:
            all_tags = [all_tags]
        for tag in all_tags:
            if tag.commit.commit == commit:
                return True
        return False

    def _check_tag_has_release(self, tag: Tag):
        """Function to check if a tag has a release"""
        all_releases = self.repository.get_releases()
        if not isinstance(all_releases, PaginatedList):
            all_releases = [all_releases]
        for release in all_releases:
            if release.tag_name == tag.name:
                return True
        return None

    def _get_commit_from_tagname(self, tag_name: str):
        """Function to retrieve the commit associated to a tag"""
        all_tags = self.repository.get_tags()
        if not isinstance(all_tags, PaginatedList) and all_tags:
            all_tags = [all_tags]
        for tag in all_tags:
            if tag.name == tag_name:
                return tag.commit.commit
        return None

    def _get_next_tag_name(self):
        """Function that retrieves the next tag to create"""
        all_tags = self.repository.get_tags()
        if not isinstance(all_tags, PaginatedList) and all_tags:
            all_tags = [all_tags]
        if all_tags:
            ordered_tags = sorted(all_tags, key=lambda x: x.commit.commit.committer.date, reverse=True)
            tag_name = str(ordered_tags[0].name).split('.')
            tag_name[3] = str(int(tag_name[3]) + 1)
            return '.'.join(tag_name)
        else:
            return "v.0.0.1"

    def _create_release_notes(self, base_commit: Commit, head_commit: Commit):
        comparison = self.repository.compare(base=base_commit.sha, head=head_commit.sha)
        result = '# Diff url \n' + comparison.diff_url + '\n'
        result += '# Changes \n # Files \n'
        for file in comparison.files:
            result += '## ' + str(file.raw_data['filename']) + '\n'
            result += '- status = ' + str(file.raw_data['status']) + '\n'
            result += '- additions = ' + str(file.raw_data['additions']) + ' lines \n'
            result += '- deletions = ' + str(file.raw_data['deletions']) + ' lines \n'
            result += '- changes = ' + str(file.raw_data['changes']) + ' lines \n'
            result += '- blob_url = ' + str(file.raw_data['blob_url']) + '\n'
        return result


if __name__ == "__main__":
    parameters = sys.argv[1:]
    repository_wrapper = RepositoryTagger(parameters[0], parameters[1])
    repository_wrapper.tag_latest_commit()
    repository_wrapper.create_release()
