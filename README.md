NXAPI SCRIPTS
=============

These scripts assume you have installed both the `ipaddress` and `requests` modules from PyPI.
```
pip install ipaddress
pip install requests
```

A collection of Python scripts that leverage NXAPI to automate some common
(and maybe some not-so-common) tasks.

These scripts leverage the "requests" python module, which you may need to install, mostly because the NXAPI sandbox generates Python code using that module.  I may work on moving the requests to urllib in the future so that additional modules don't need to be installed.

 - nxapi_base.py - A module with an NXOS device class and some generic functions that can be used to more quickly build scripts.

 - IntfLabel.py - A script that will pull CDP and port-channel information and label interfaces accordingly.

 - ClearDesc.py - A short script to clear all interfaces of descriptions.  Used when testing the IntfLabel.py script.

 - RouteStats.py - A script that will pull the route table and give some basic statistics about next hops and how many routes use them.

