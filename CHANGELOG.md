# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

Note if only 1 issue/commit link is given in a commit then that commit
was the only 1 used. An issue is used in preference to a git commit.

## [0.1.1] - 2024-02-05

### Added
- [add files needed for open publication](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/issues/29):
  - Added link to Open Gov License v3 and included it as a file in the repo
  - Added MIT License

### Changed
- Added support email to README
- Updated installation and support instructions
- Added section specifying key developers
- Added crown copyright to README

## [0.1.0] - 2024-01-16

### Added
- [Make changelog](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/issues/27) added a changelog of all changes backdated to the initial commit

### Changed
- [convert functions with shared inputs into a class](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/issues/16) main has been converted from a string to classes using builder design pattern.

## [0.0.12] - 2023-12-22

### Added
- [Move hardcode variables to config](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/issues/24)


## [0.0.11] - 2023-12-15

### Added
- [Make basic unit tests for functions](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/issues/13)

### Changed
- [add poetry and modified the dockerfile to remove layers](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/f814eb76a42b7d6afe388d34f85d49bdbe9c7d08) Poetry is now on a single dockerfile RUN command

### Fixed

## [0.0.10] - 2023-12-11

### Changed
- [remove top 200 from query](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/issues/23) the input query was artificially limited the team didn't want this so changed to get all comments from last X days.

## [0.0.9] - 2023-11-29

### Changed
- [Add new wards to query string](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/issues/22)

### Fixed
- [updated query with correct ward names](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/ff6801735fecb5646493905dc5dd164e4188884d)

## [0.0.8] - 2023-11-23

### Added
- [New confidence score](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/9241ae615b3b7a399af0781e123b49d0fb70119a). Documentation can be found here: `Z:\Projects\Research\0273 - FFT NLP deployment\UserData\New consensus score\fft_confidence_score.pdf`

### Changed
- pipeline version changed to 0.04

## [0.0.7] - 2023-11-14

### Changed
- [consensus scores incorrect](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/issues/8) consensus scores in origional model were ova not ovo so hot fix added to remove scores

## [0.0.6] - 2023-11-03

### Changed
- [assigned pipeline version to 0.03](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/05dd428fc24cd0681426bd57837646291b801538)
- [added export csv notes on ReadMe](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/28fdc33bd198696bdd01ebeb8caed2a98ed36cde)

### Fixed
- crontab paths
  - [changed crontab to have correct location for main.py](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/f8542e06bf6c2c16c952215b3c921a01fc5d8495)
  - [revised place where main program is in cron file](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/351ad2ff8debb93a69aba55599b7965e35467678)

## [0.0.5] - 2023-11-02

### Changed
- [updated ReadMe](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/dfe09e9237a01254e8c6c72f9053292c97847ef2)
- [Reformated ReadMe markdown](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/c8e2ef576c6cd7a0c4c5816736ddc07a86ec649f)
- [adjusted query and chunk and output table to run on production instance](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/e806ca4f00ef602514a3af4dc1eabf439af0dc5a) query chunk changed to 200 and pipeline version number reverted to 0.02


### Fixed
- [revised model paths for ubuntu](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/9c07858a850ab39763aa895b8680e9f16a649c43)
- [corrected typos on ReadMe](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/b127def2c88b767284d990ce42817d65669b1ab8) typos and errors in README
- reduced size of Docker image
  - [removed transformers and torch from poetry](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/4ba115af62ad2f6936153682b0e0dd5a01e9116f)
  - [install transformers and torch through pip in dockerfile](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/25a3c18adbf0e58d7a22129eda62291865104dd1)

## [0.0.4] - 2023-11-01

### Added
- [revised consesus score percentage calculation](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/b6a1ab7fcac2bfceea6a6bd8914914c7e961a8ad) Made basic sentiment score (based on ovo)

### Changed
- removed commented out queries from main.py
- changed paths to match podman container structure

### Fixed
- main.py added to Dockerfile

## [0.0.3] - 2023-11-01

### Added
- [adjusted ubuntu friendly verision](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/e4e8925b196f8bf864aa78068edf59701590d537) Dockerfile to allow containerisation
- kerberos authentication for database access
- crontab added to automatically run scripts

### Changed
- requirements.txt removed
- Pipeline changed to 0.03

## [0.0.2] - 2023-11-01

### Added
- [initial comment with docker](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/00542d3e400f50cbaf55ae7832d34bbf38119404) Poetry now used for dependency managment

### Changed
- Moved over previous repo files
- Pipeline changed to 0.02

## [0.0.1] - 2023-09-01

### Added
- [Initial commit](https://gitlab.pangosh.nhs.uk/dre-team/re0273-fft/-/commit/53186e8f7f04c575f540292315bcd94d4389ec66).
