# scaffold-params

`scaffold-params` provides a customizable parameterization scaffolding.  The intent is to provide a template based framework with coherent behavior across adhoc, dockerized, and/or systemd use cases.

Quickstart
====

```bash
git clone git@github.com:dustinlennon/scaffold-params.git
cd scaffold-params/
pipenv run python3 src/scaffold/samples/basic.py \
  --config src/scaffold/samples/conf/basic.yaml
```

The distribution also includes a [github.sh](https://github.com/dustinlennon/scaffold-params/blob/main/gitpip.sh) script.  This assumes a pipenv installation exists in the specified directory.  If it doesn't, the script creates a pipenv environment.  It then installs `scaffold-params` into the pivenv, provides a symbolic link to the `samples`, and dynamically creates a dotenv file for running `basic.py` without an explicit --config parameter.


First Run
===

```bash
pipenv run python3 src/scaffold/samples/basic.py
```

Without a configuration file, you'll see the following:

```
Loading .env environment variables...
basic.py: error: the following arguments are required: --config
```

And with a configuration file:

```bash
pipenv run python3 src/scaffold/samples/basic.py \
  --config src/scaffold/samples/conf/basic.yaml
```

the apparently unexciting result:

```
Loading .env environment variables...
2025-03-27 18:02:49 | __main__ | INFO | The time is: 11:02 PDT
>>>

    Template
    ---

    The time is: 11:02 PDT

<<<
```

### templates

The `basic.py` example is perhaps more interesting when invoked with the "-h" flag:

```bash
pipenv run python3 src/scaffold/samples/basic.py \
  --config src/scaffold/samples/conf/basic.yaml -h
```

```
Loading .env environment variables...
usage: basic.py [-h] [--config] [--template-path] [--timezone] [--log-config-path] [--logs-path] [--install-path]

options:
  -h, --help          show this help message and exit
  --config            BASIC_CONFIG_PATH         <dotenv>
                      'src/scaffold/samples/conf/basic.yaml'
                      
  --template-path     BASIC_TEMPLATE_PATH       env.template_path
                      '/home/dnlennon/Workspace/Sandbox/scaffold-params/src/scaffold/samples/templates'
                      
  --timezone          BASIC_TIMEZONE            env.timezone
                      'US/Pacific'
                      
  --log-config-path   BASIC_LOG_CONFIG_PATH     env.log_config_path
                      '/home/dnlennon/Workspace/Sandbox/scaffold-params/src/scaffold/samples/conf/logger.yaml'
                      
  --logs-path         BASIC_LOGS_PATH           env.logs_path
                      './logs'
                      
  --install-path      BASIC_INSTALL_PATH        env.install_path
                      '/home/dnlennon/Workspace/Sandbox/scaffold-params'
                      
```

Above, there are a number of command line flags, each with a corresponding environment variable and the key for a default value defined in the config yaml.  The output also shows a working value of each parameter; that is, the value that will be used should the command line parameter be left unspecified.  


Templatized Parameters
====

[basic.py](https://github.com/dustinlennon/scaffold-params/blob/main/src/scaffold/samples/basic.py), backed by [basic.yaml](https://github.com/dustinlennon/scaffold-params/blob/main/src/scaffold/samples/conf/basic.yaml), provides a simple example of how we templatize parameters.

The key structure here (see code below) is `BasicParams`.  This derives from `BaseParams` and `CommonParams`, the latter composed of three `BaseMixin` mixins.  Each of these mixins defines a subset of parameters utilizing a well-defined fallback scheme.  Specifically, a command line parameter falls back to an environment variable which falls back to a value specified in a YAML configuration file.  Alongside these default values, the YAML file provides the necessary metadata to dynamically create an `argparse.ArgumentParser` object.

The corresponding code follows:

```bash
# samples/basic.py (excerpt)

from scaffold.params.base_params import BaseParams
from scaffold.params.mixins import *

if __name__ == '__main__':

  class CommonParams(NowMixin, LoggerInitMixin, JinjaTemplateMixin):
    pass

  class BasicParams(BaseParams, CommonParams):
    _prefix = "BASIC"

  params = BasicParams.build()
  args = params.parse_args()
```

We utilize YAML references to emphasize how parameter collections are built up over the three BaseParams derived classes.  In reality, these could be combined: the only component of the YAML that is parsed internally is `env`. 

```yaml
# samples/conf/basic.yaml
env_base: &base
  install_path: !env ${PWD}

env_timezone: &timezone
  timezone: US/Pacific

env_logger: &logger
  log_config_path: !env ${SCAFFOLD_PATH}/samples/conf/logger.yaml
  logs_path: ./logs

env_template: &template
  template_path: !env ${SCAFFOLD_PATH}/samples/templates

env:
  <<: [*base, *logger, *timezone, *template]
```

The YAML keys defined in `env` have a correspondence with command line flags and environment variable names.  E.g., "timezone" (YAML) becomes "--timezone" (argparse) and "BASIC_TIMEZONE" (env var); the "BASIC" prefix is picked up from the class variable, `_prefix`.


### mixins

Mixins are a useful way to package and group functionality that is associated with disparate parameter sets.  [NowMixin.py](https://github.com/dustinlennon/scaffold-params/blob/main/src/scaffold/params/mixins/now_mixin.py) is probably the simplest.

The idea is to keep it simple.  We inherit from `BaseMixin` and implement the `assign_args` method.  On initialization, we only need copy the provided timezone from `args` to the instance.  For post-initialization use, `NowMixin` provides the `now` method that ensures that a datetime instance is timezone aware and created with a timezone specified apriori.

```python
# params/mixins/now_mixin.py
import datetime, pytz
from .base_mixin import BaseMixin

class NowMixin(BaseMixin):
  def assign_args(self, args):
    super().assign_args(args)
    self.timezone = args.timezone

  def now(self) -> datetime:
    self._tz  = pytz.timezone(self.timezone)
    return datetime.datetime.now(self._tz)
```


YAML Config Search
===

`scaffold-params` implements a two pass strategy for building parameter sets.  So far, we've focused on the second stage, that is, after the config YAML is available.  The first stage employs a search strategy to find the YAML config file.  That looks like the following:


If, nothing is specified, use `dotenv`

```
scaffold-params$ \
  PRINTF_DEBUG=True \
  pipenv run python3 \
    src/scaffold/samples/basic.py 
Loading .env environment variables...
>>> searching for config: trying from_args()
>>> searching for config: trying from_env()
>>> searching for config: trying from_dotenv()   <------------------- using dotenv
```

Setting `BASIC_CONFIG_PATH` in the environment overrides `dotenv`.

```
scaffold-params$ \
  BASIC_CONFIG_PATH=src/scaffold/samples/conf/basic.yaml \
  PRINTF_DEBUG=True \
  pipenv run python3 \
    src/scaffold/samples/basic.py 
Loading .env environment variables...
>>> searching for config: trying from_args()
>>> searching for config: trying from_env()      <------------------- using environment
```

Finally, any parameters set at the command line take precedence.  Thus, parameter `--config` will override `BASIC_CONFIG_PATH`.

```
scaffold-params$ \
  BASIC_CONFIG_PATH=./not/going/to/matter \
  PRINTF_DEBUG=True \
  pipenv run python3 \
    src/scaffold/samples/basic.py \
      --config src/scaffold/samples/conf/basic.yaml
>>> searching for config: trying from_args()     <------------------- using --config 
```

### dotenv

The dotenv file, if available, provides a default for environment variables.  For example,

```
# ./dotenv
BASIC_CONFIG_PATH=${PWD}/scaffold-params/src/scaffold/samples/conf/basic.yaml
```

This can be useful when code needs to be invoked from outside the working directory.  One examples is via systemd, where the dotenv may be specified by an `EnvironmentFile`.