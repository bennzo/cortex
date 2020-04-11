[![Build Status](https://travis-ci.org/bennzo/cortex.svg?branch=master)](https://travis-ci.org/bennzo/cortex)
[![codecov](https://codecov.io/gh/bennzo/cortex/branch/master/graph/badge.svg)](https://codecov.io/gh/bennzo/cortex)

# Magnificent Brain
The Magnificent Brain is a simple infrastructure project that enables streaming of cognition snapshots between
a client and a server.


**Documentation**  
For a detailed documentation of the package API follow this [link](https://www.example.com) to a ReadTheDocs page.

**Credit:**  
This project is the final assignment in the Advanced System Design (2019) course in Tel-Aviv University instructed by [Dan Gittik](https://github.com/dan-gittik).

## Getting Started
### Requirements:
* Unix-like OS (this project was built and tested on Ubuntu 18.04.4)
* Python >= 3.8, with virtualenv installed
* Docker (for container deployment and pipeline script)

### Quickstart:
1. Clone the repository, run the included script and follow the instructions to get the pipeline running:
    ```bash
    git clone https://github.com/bennzo/cortex.git
    cd cortex
    ./scripts/run-pipeline.sh
    ```
2. Set up and run the virtual environment:
    ```bash
    ./scripts/install.sh
    source .env/bin/activate
    ```
3. Use the Client CLI to upload samples to the server:
    ```bash
    python -m cortex.client upload-sample -h 127.0.0.1 -p 8000 data/littlesample.mind.gz
    ```
4. Open up http://127.0.0.1:8080 to browse your uploaded snapshots.

### Install:

**Note:**
* If you are using a clean OS installation, we recommend the following preliminery steps:
    * Install basic dependencies:
        ```bash
        sudo apt install build-essential curl git llvm libbz2-dev libffi-dev\
        liblzma-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev\
        libssl-dev make python-openssl tk-dev wget xz-utils zlib1g-dev
        ```
    * Install Python 3.8
    * Install virtualenv for Python 3.8
    
1. Clone the repository and enter the directory:
    ```bash
    git clone https://github.com/bennzo/cortex.git
    cd cortex
    ```
2. Install the Python requirements:
    * Either directly with pip to your local Python env:
    ```bash
    pip install -r requirements.txt
    ```
    * Or create a new virtual environment with the install script 
    ```bash
    ./scripts/install.sh
    source .env/bin/activate
    ```
3. Run the tests to ensure everything is working as intended:
    ```bash
    pytest
    ```

### Docker deployment:
If you wish to deploy the project components individually inside containers:
* Install Docker
* Build the Docker image
* Run the run-pipeline.sh script and follow the instructions

## Usage
### CLI:
The package includes a CLI which allows execution of the basic functionality of each module.
<details><summary><b>Show instructions</b></summary>

#### Client:
* ``upload-sample --host <server_host> --port <server_port> <path_to_sample>``  

    Uploads a sample to a server.  
    
    Example:
    ```bash
    python -m cortex.client upload-sample \
          --host '127.0.0.1'              \
          --port 8000                     \
          'littlesample.mind.gz'
    ```

#### Server:
* ``run-server --host <server_host> --port <server_port> <mq_url>``  

    Runs a server which listens on host:port and publishes messages received to a message queue.
    
    Example:
    ```bash
    python -m cortex.server run-server \
          --host '127.0.0.1'           \
          --port 8000                  \
          'rabbitmq://127.0.0.1:5672/'
    ```

#### Parsers:
* ``parse <parser_name> <path_to_data>``  

    Run a specific parser on raw data and return the parsed result (optionally redirect the output to a file).
    
    Example:
    ```bash
    python -m cortex.parsers parse 'pose' 'snapshot.raw' > 'pose.result'
    ```
  
* ``run-parser <parser_name> <mq_url>``  
    
    Run a parser as a service. The parser listens to a message queue in the URL given and will consume
    and publish parsed data indefinitely.
    
    Example:
    ```bash
    python -m cortex.parsers run-parser 'pose' 'rabbitmq://127.0.0.1:5672/'
    ```
    
#### Saver:
* ``save --database <db_url> <field_name> <field_result_path>``  

    Takes a field name and a path to a field result and saves it to a database in the URL given.
    
    Example:
    ```bash
    python -m cortex.saver save                 \
         --database 'mongodb://127.0.0.1:27017' \
         'pose'                                 \
         'pose.result'    
    ```
  
* ``run-saver <mq_url> <db_url>``  

    Run a saver as a service. The saver subscribes to the relevant message queue topics and saves the
    consumed messages to the database.
    
    Example:
    ```bash
    python -m cortex.saver run-saver  \
          'mongodb://127.0.0.1:27017' \
          'rabbitmq://127.0.0.1:5672/'
    ```

#### API:
* ``run-server --host <server_host> --port <server_port> --database <db_url>``  

    Runs an API server which listens on host:port and serves data from db_url.  
    Note: For a list of points that the API exposes follow the link to the docs in the bottom of the page.
    
    Example:
    ```bash
    python -m cortex.api run-server \
          --host '127.0.0.1'        \
          --port 5000               \
          --database 'mongodb://127.0.0.1:27017''
    ```

#### CLI:
The CLI consumes an API server and reflects it

* ``get-users``  
    
    Returns a list of ids and names of all the users in the database.
    
    Example:
    ```bash
    python -m cortex.cli get-users
    ```
* ``get-user <user_id>``  
    
    Returns the specified user information.
    
    Example:
    ```bash
    python -m cortex.cli get-user 42
    ```
* ``get-snapshots <user_id>``  
    
    Returns a list of the specified user snapshots information.
    
    Example:
    ```bash
    python -m cortex.cli get-snapshots 42
    ```
* ``get-snapshot <user_id> <snapshot_id>``  
    
    Returns a specific snapshot of a specific user.
    
    Example:
    ```bash
    python -m cortex.cli get-snapshot 42 1 
    ```
* ``get-result <user_id> <snapshot_id> <field_name>``  
    
    Returns a specific snapshot field value.
    
    Example:
    ```bash
    python -m cortex.cli get-result 42 1 'pose'
    ```
  
#### GUI:
* ``run-server --host <server_host> --port <server_port> --api-host <api_host> --api-port <api_port>``  

    Runs the GUI web server on host:port which reflects the API on api_host:api_port.
    
    Example:
    ```bash
    python -m cortex.gui run-server \
          --host '127.0.0.1'       \
          --port 8080              \
          --api-host '127.0.0.1'   \
          --api-port 5000
    ```

</details>

### Library:
The package can be utilized as a library by using the exposed API of each module.
<details><summary><b>Show instructions</b></summary>

#### Client:
* ``upload_sample(host=<server_host>, port=<server_port>, path=<path_to_sample>)``  

    Uploads a sample to a server.
    
    Example:
    ```python
    from cortex.client import upload_sample
    upload_sample(host='127.0.0.1', port=8000, path='sample.mind.gz')
    ```

#### Server:
* ``run_server(host=<server_host>, port=<server_port>, publish=<publish_func>)``  

    Runs a server which listens on host:port and passes messages received to a publish function.
    
    Example:
    ```python
    from cortex.server import run_server
    def print_message(message):
        print(message)
    run_server(host='127.0.0.1', port=8000, publish=print_message)
    ```
  
#### Parsers:
* ``run_parser(field=<parser_name>, data=data)``  

    Run a specific parser on raw data and return the parsed result.
    
    Example:
    ```python
    from cortex.parsers import run_parser
    data = '...'
    result = run_parser('pose', data)
    ```
  
#### Saver:
* ``Saver(db_url)``  

    Saver class which connects to a database and saves data by calling its `save` method.
    
    Example:
    ```python
    from cortex.saver import Saver
    saver = Saver(db_url=db_url)
    data = '...' 
    saver.save('pose', data)    
    ```
  
#### API:
* ``run_api_server(host=<server_host>, port=<server_port>, database_url=<db_url>)``  

    Runs an API server which listens on host:port and serves data from db_url.  
    Note: For a list of points that the API exposes follow the link to the docs in the bottom of the page.
    
    Example:
    ```python
    from cortex.api import run_api_server
    run_api_server(host='127.0.0.1', port=5000, database_url='mongodb://127.0.0.1:27017')
    ```
  
#### GUI:
* ``run_server(host=<server_host>, port=<server_port>, api_host=<api_host>, api_port=<api_port>``  

    Runs the GUI web server on host:port which reflects the API on api_host:api_port.
    
    Example:
    ```python
    from cortex.gui import run_server
    run_server(host='127.0.0.1', port=8080, api_host='127.0.0.1', api_port=5000)
    ```
</details>

### Pipeline script:
* Run the `run-pipeline.sh` script:
    * Deploy the full pipeline
    * Deploy a specific component individually


