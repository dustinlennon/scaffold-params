# pyapp-scaffold

Search order for YAML config
----

Nothing specified, use `dotenv`

```
dnlennon@carolina:~/Workspace/Sandbox/pyapp-scaffold$ PRINTF_DEBUG=True python3 example.py > /dev/null
>>> searching for config: trying from_args()    
>>> searching for config: trying from_env()
>>> searching for config: trying from_dotenv()   <------------------- using dotenv
2025-03-22 16:25:25 | __main__ | INFO | The time is: 09:25 PDT
```

`EXAMPLE_CONFIG_PATH` overrides `dotenv`.

```
dnlennon@carolina:~/Workspace/Sandbox/pyapp-scaffold$ EXAMPLE_CONFIG_PATH=./conf/example.yaml PRINTF_DEBUG=True python3 example.py > /dev/null
>>> searching for config: trying from_args()
>>> searching for config: trying from_env()      <------------------- using EXAMPLE_CONFIG_PATH
2025-03-22 16:25:38 | __main__ | INFO | The time is: 09:25 PDT
```

Command line parameter `--config` overrides `EXAMPLE_CONFIG_PATH`

```
dnlennon@carolina:~/Workspace/Sandbox/pyapp-scaffold$ EXAMPLE_CONFIG_PATH=./conf/example.yaml PRINTF_DEBUG=True python3 example.py --config ./conf/example.yaml > /dev/null
>>> searching for config: trying from_args()     <------------------- using --config 
2025-03-22 16:25:54 | __main__ | INFO | The time is: 09:25 PDT
```
