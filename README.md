# YAML Git Web Api

[![Build Status](https://travis-ci.org/Graham42/yaml_git_web_api.png)](https://travis-ci.org/Graham42/yaml_git_web_api)

Serves up a git repo of YAML files as a RESTful web api.

This project is licensed under The MIT License (MIT) see the [LICENSE](LICENSE) file.


## Table of Contents
* [Required Structure of Data Repo](#required-structure-of-data-repo)
* [Install](#install)
* [Usage](#usage)
* [Making API Calls](#making-api-calls)


## Required Structure of Data Repo
Probably validate with somehting like https://github.com/Queens-Hacks/data-schema-validate
```
root:
  data:
    - folder_X:
      - data_file_XN.yaml

    - data_file_Z.yaml

  schema:
    - folder_X:
      - schema_X.yaml

    - schema.yaml
```

## Install

### 1. Python & Git

Python 2.7 or 3.3 and git must be installed on your system.

### 2. Application Requirements

You'll probably want to use a [virtualenv](http://www.virtualenv.org/en/latest/), maybe with [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/).
Once you've created and activated your virtualenv, install the dependcies with:

```bash
(venv_name) $ pip install -r requirements.txt
```

### 3. Local Configuration

A couple variables can be set locally. You can either copy the file `api/local_config.py.example` to `api/local_config.py` and define the variables there, or export them to your environment.

The definitive list of config variables can be found [in the config module](api/config.py#L36) on line 36.

### 4. Get Data

Run `init` to grab data from the repo. The exact repo to pull from is set by your config.

```bash
(venv_name) $ ./manage.py init
```


## Usage

The `manage.py` script provides commands to do stuff. Run it with no arguments to see the full list of available commands. The two you might want:

```bash
$ ./manage.py init            # Get the data from the remote
$ ./manage.py runserver       # Run a local development server
$ ./manage.py test            # Run the app's test suite
```

## Making API Calls
Something like `https://{host}/folder_X/data_file_XN`

Should return
```js
{
  "metadata": {
    // git meta data here...
  },
  "data": {
    // contents of the yaml file 'folder_X/data_file_XN.yaml' transformed to JSON
  }
}
```
