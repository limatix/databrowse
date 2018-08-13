# Databrowse Github WorkFlow

## [Branching Model](https://nvie.com/posts/a-successful-git-branching-model/)
![Git Branching Model](git-model@2x.png "Git Branching Model")

## Cutting a Release
Following a merge of the release branch into Master as per the above diagram:

1. Pull Master branch to development environment
2. Tag the release (i.e. 0.8.2)
3. Push tags back to Github remote (git push --tags)
4. Confirm that latest commit in Master is cryptographically signed
    1. A green "Verified" tag should accompany the commit [number](https://github.com/limatix/databrowse/commits/master) 
    2. If not, [here](https://help.github.com/articles/signing-commits-using-gpg/).
5. Draft new [release](https://github.com/limatix/databrowse/releases) using version tag from above
6. Upload assets:
    1. databrowse-*ver*.tar.gz
        1. Run *python setup.py bdist --format=gztar*
        2. File located in *dist* directory
    2. databrowse-*ver*.tar.gz.asc
        1. [Run](https://www.gnupg.org/) *gpg --armor --detach-sig databrowse-*ver*.tar.gz* in *dist* directory
    3. databrowse-*ver*.tar.gz.md5
        1. Windows - [FCIV](https://support.microsoft.com/en-us/help/889768/how-to-compute-the-md5-or-sha-1-cryptographic-hash-values-for-a-file)
            1. Run *FCIV -md5 -sha1 databrowse-*ver*.tar.gz*
            2. Copy md5 and sha checksum into respective files
        2. Linux:
            1. Run *echo databrowse-*ver*.tar.gz | tee >(md5sum) >(sha1sum) > output.txt*
            2. Copy md5 and sha checksum from output.txt into respective files
    4. databrowse-*ver*.tar.gz.sha
        1. See above.
    5. databrowse-*ver*.win-amd64.msi
        1. Run *python setup.py bdist_msi*
        2. File located in *dist* directory
7. Upload to [PIP](https://packaging.python.org/tutorials/packaging-projects/)
    1. Run *python setup.py sdist bdist_wheel*
    2. Run *twine upload dist/*