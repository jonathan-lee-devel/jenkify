# jenkify
## (Jenkins Command-Line REST Client Automation Tool)

## Usage
### With Docker
```shell
docker run --rm jenkify --help
```
### Without Docker
Make sure to have Python Poetry installed by running the following command:
```shell
pip install poetry
```

Then you must enable a Poetry virtual environment:

```shell
poetry shell
```

Install all the dependencies inside this virtual environment:

 ```shell
poetry install
```

Now run the tool. Example Usage:

```shell
python -m jenkify --help
```

## Commands
### start-build-jobs-yaml
Example input:
```yaml
build:
  hosts:
    - url: 'http://localhost:8080'
      jobs:
        - end: 'job/TestJob'
        - end: 'job/AnotherTestJob'
        - end: 'job/LongRunningJob'
        - end: 'job/SomeOtherJob'
```

Point the command to the file using the --build-jobs-yaml / -bjy option
```shell
python -m jenkify start-build-jobs-yaml -bjy sample-builds.yaml
```

The command will then attempt to kick off a build for each job listed in the input yaml.
Builds kicked off successfully will have their build number tracked and outputted to a file input-file-tracking-output.yaml such as below:
```yaml
build:
  hosts:
   - url: http://localhost:8080
     jobs:
     - build_index: 47
       end: job/TestJob
     - build_index: 24
       end: job/AnotherTestJob
     - build_index: 9
       end: job/LongRunningJob
     - end: job/SomeOtherJob
```
The build_index is intentionally left empty for failed builds. These builds can be started manually and debugged and
then the user can enter the build_index into the file manually. The failed jobs are listed in the logs and outputted to
a file such as input-file-remaining-output.yaml:
```yaml
build:
  hosts:
  - url: http://localhost:8080
    jobs:
    - end: job/SomeOtherJob

```
Alternatively, you can re-run the failed builds automatically by providing the remaining output yaml file as input.
### track-build-jobs-status
Example input:
```yaml
build:
  hosts:
  - url: http://localhost:8080
    jobs:
    - build_index: 55
      end: job/TestJob
    - build_index: 32
      end: job/AnotherTestJob
    - build_index: 35
      end: job/LongRunningJob
```
Point the command to the file using the --build-jobs-tracking-yaml / -bjty option
```shell
python -m jenkify track-build-jobs-status -bjty sample-builds-tracking.yaml
```
