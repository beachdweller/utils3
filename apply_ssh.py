#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import re
import sys
import urllib.parse

import find_git_repos
import git_update_all
import git_util


def main(argv):
    repo_path = argv[1]

    if 3 > len(argv):
        b_arm = False
    elif 'false' in argv[2].lower():
        b_arm = False
    elif 'True' == argv[2]:
        b_arm = True
    else:
        b_arm = False

    updater = ApplySSH(repo_path, 'config', b_arm=b_arm)
    updater.recursively_find_in()


class ApplySSH(find_git_repos.RecursiveGitRepositoryFinderBase):
    def __init__(self, root_path, file_name_spec, b_verbose=False, repo_site_name='bitbucket.org', b_arm=False):
        super(ApplySSH, self).__init__(root_path, file_name_spec, b_verbose)
        self.finder = re.compile(r'https://.*' + repo_site_name + '/.+\.git')
        # if true, overwrite a new url
        self.b_arm = b_arm
        self.start_path = os.path.abspath(os.curdir)

    def is_target(self, url):
        if url is not None:
            result = bool(self.finder.findall(url))
        else:
            result = False
        return result

    def process_git_folder(self, repo_path):
        if not git_update_all.is_ignore(repo_path):
            # if this repo path is not in the ignore list
            # get remote info dictionary
            remote_info_dict_dict = git_util.git_config_remote_info(repo_path)
            for remote_name, remote_info_dict in remote_info_dict_dict.items():
                remote_url = remote_info_dict.get('url', None)
                if self.is_target(remote_url):
                    os.chdir(repo_path)
                    ssh_url = self.convert_url_https_to_ssh(remote_url)
                    git_cmd, git_cmd_push = self.get_git_cmd_remote_set_url(remote_name, ssh_url, remote_url)
                    if not self.b_arm:
                        print(remote_name, remote_url, ssh_url)
                        print(git_cmd)
                        print(git_cmd_push)
                    else:
                        print("** updating %r **" % repo_path)
                        print(remote_name, remote_url)
                        git_util.git(git_cmd)
                        git_util.git(git_cmd_push)
                    os.chdir(self.start_path)

    @staticmethod
    def get_git_cmd_remote_set_url(remote_name, ssh_url, https_url):
        """
        usage: git remote [-v | --verbose]
           or: git remote add [-t <branch>] [-m <master>] [-f] [--tags | --no-tags] [--mirror=<fetch|push>] <name> <url>
           or: git remote rename <old> <new>
           or: git remote remove <name>
           or: git remote set-head <name> (-a | --auto | -d | --delete | <branch>)
           or: git remote [-v | --verbose] show [-n] <name>
           or: git remote prune [-n | --dry-run] <name>
           or: git remote [-v | --verbose] update [-p | --prune] [(<group> | <remote>)...]
           or: git remote set-branches [--add] <name> <branch>...
           or: git remote get-url [--push] [--all] <name>
           or: git remote set-url [--push] <name> <newurl> [<oldurl>]
           or: git remote set-url --add <name> <newurl>
           or: git remote set-url --delete <name> <url>

            -v, --verbose         be verbose; must be placed before a subcommand

        :param remote_name:
        :param ssh_url:
        :return:
        """
        git_cmd = 'remote -v set-url %s %s %s' % (remote_name, ssh_url, https_url)
        git_cmd_push = 'remote -v set-url --push %s %s %s' % (remote_name, ssh_url, https_url)
        return git_cmd, git_cmd_push

    @staticmethod
    def convert_url_https_to_ssh(https_url):
        """
        convert https url to ssh url mainly for bitbucket.org
        see : https://confluence.atlassian.com/bitbucket/set-up-ssh-for-git-728138079.html
              https://<accountname>@bitbucket.org/< accountname>/<reponame>.git
              ssh://git@bitbucket.org /< accountname>/<reponame>.git

        :param str https_url:
        :return:
        """

        parse_result = list(urllib.parse.urlparse(https_url))
        # scheme
        parse_result[0] = 'ssh'

        # netloc
        netloc_split = parse_result[1].split('@')
        parse_result[1] = 'git@' + netloc_split[-1]

        # make ssh url
        ssh_url = urllib.parse.urlunparse(parse_result)
        return ssh_url


if __name__ == '__main__':
    main(sys.argv)