# scaffold-params

`scaffold-params` provides a customizable parameterization scaffolding.  The intent is to provide a template based framework with coherent behavior across adhoc, dockerized, and/or systemd use cases.

Quickstart
====

```bash
git clone git@github.com:dustinlennon/scaffold-params.git
cd scaffold-params/
pipenv install -e .
```

The distribution also includes a [github.sh](https://github.com/dustinlennon/scaffold-params/blob/main/gitpip.sh) script.  This assumes a pipenv installation, or creates one if necessary.  It then installs `scaffold-params` into the pivenv, provides a symbolic link to the `samples`, and dynamically creates a dotenv file for running `basic.py` without an explicit --config parameter.


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
usage: basic.py [-h] [--config] [--app-path] [--logconf-path] [--timezone] [--template-path]

options:
  -h, --help        show this help message and exit
  --config          BASIC_CONFIG_PATH         <dotenv>
                    'src/scaffold/samples/conf/basic.yaml'
                    
  --app-path        BASIC_APP_PATH            env.app_path
                    './app'
                    
  --logconf-path    BASIC_LOGCONF_PATH        env.logconf_path
                    '/home/dnlennon/Workspace/Sandbox/scaffold-params/src/scaffold/samples/conf/logger.yaml'
                    
  --timezone        BASIC_TIMEZONE            env.timezone
                    'US/Pacific'
                    
  --template-path   BASIC_TEMPLATE_PATH       env.template_path
                    '/home/dnlennon/Workspace/Sandbox/scaffold-params/src/scaffold/samples/templates'
```

Above, we see a number of command line flags, a corresponding environment variable, and the key for a default value defined in the config yaml.  The help output also shows a working value of each parameter; that is, the value that will be used should the command line parameter be left unspecified.  


Templatized Parameters
====

[basic.py], backed by [basic.yaml](https://github.com/dustinlennon/scaffold-params/blob/main/src/scaffold/samples/conf/basic.yaml), provides a simple example of how we templatize parameters.

The key structure here is `BasicParams` which derives from `CommonParams` which, in the background, derives from `BaseParams`.  Each of these defines a subset of parameters with a well defined fallback scheme.  That is, a command line parameter falls back to an environment variable which falls back to a YAML definition.  On the other hand, the YAML file defines the collection of parameters and provides default values.  We use the YAML file to dynamically create an `argparse.ArgumentParser` object.

The corresponding code follows:

```bash
# basic.py (excerpt)

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
# basic.yaml
env_base: &base
  app_path: ./app

env_common: &common
  <<: *base
  logconf_path: !env ${SCAFFOLD_PATH}/samples/conf/logger.yaml
  timezone: US/Pacific
  template_path: !env ${SCAFFOLD_PATH}/samples/templates

env:
  <<: *common
```

The YAML keys defined in `env` have a correspondence with command line flags and environment variable names.  E.g., "timezone" (YAML) becomes "--timezone" (argparse) and "BASIC_TIMEZONE" (env var); the "BASIC" prefix is picked up from the class variable, `_prefix`.


### mixins

Mixins are a useful way to package and group functionality that is associated with disparate parameter sets.  [NowMixin.py](https://github.com/dustinlennon/scaffold-params/blob/main/src/scaffold/params/mixins/now_mixin.py) is probably the simplest.

The idea is to keep it simple.  We inherit from `BaseMixin` and implement the `assign_args` method.  On initialization, we only need copy the provided timezone from `args` to the instance.  For post-initialization use, `NowMixin` provides the `now` method that ensures that a datetime instance is timezone aware and created with a timezone specified apriori.

```python
# mixins/now_mixin.py
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
