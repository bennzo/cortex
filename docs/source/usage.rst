.. _usage:

Usage
=====

CLI
^^^

The package includes a CLI which allows execution of the basic functionality of each module.

Client
~~~~~~


*
  ``upload-sample --host <server_host> --port <server_port> <path_to_sample>``

    Uploads a sample to a server.

    Example:

  .. code-block:: bash

       python -m cortex.client upload-sample \
             --host '127.0.0.1'              \
             --port 8000                     \
             'littlesample.mind.gz'

Server
~~~~~~


*
  ``run-server --host <server_host> --port <server_port> <mq_url>``

    Runs a server which listens on host:port and publishes messages received to a message queue.

    Example:

  .. code-block:: bash

       python -m cortex.server run-server \
             --host '127.0.0.1'           \
             --port 8000                  \
             'rabbitmq://127.0.0.1:5672/'

Parsers
~~~~~~~


*
  ``parse <parser_name> <path_to_data>``

    Run a specific parser on raw data and return the parsed result (optionally redirect the output to a file).

    Example:

  .. code-block:: bash

       python -m cortex.parsers parse 'pose' 'snapshot.raw' > 'pose.result'

*
  ``run-parser <parser_name> <mq_url>``

    Run a parser as a service. The parser listens to a message queue in the URL given and will consume
    and publish parsed data indefinitely.

    Example:

  .. code-block:: bash

       python -m cortex.parsers run-parser 'pose' 'rabbitmq://127.0.0.1:5672/'

Saver
~~~~~


*
  ``save --database <db_url> <field_name> <field_result_path>``

    Takes a field name and a path to a field result and saves it to a database in the URL given.

    Example:

  .. code-block:: bash

       python -m cortex.saver save                 \
            --database 'mongodb://127.0.0.1:27017' \
            'pose'                                 \
            'pose.result'

*
  ``run-saver <mq_url> <db_url>``

    Run a saver as a service. The saver subscribes to the relevant message queue topics and saves the
    consumed messages to the database.

    Example:

  .. code-block:: bash

       python -m cortex.saver run-saver  \
             'mongodb://127.0.0.1:27017' \
             'rabbitmq://127.0.0.1:5672/'

API
~~~


*
  ``run-server --host <server_host> --port <server_port> --database <db_url>``

    Runs an API server which listens on host:port and serves data from db_url.\ :raw-html-m2r:`<br>`
    Note: For a list of points that the API exposes follow the link to the docs in the bottom of the page.

    Example:

  .. code-block:: bash

       python -m cortex.api run-server \
             --host '127.0.0.1'        \
             --port 5000               \
             --database 'mongodb://127.0.0.1:27017'

CLI
~~~

The CLI consumes an API server and reflects it


*
  ``get-users``

    Returns a list of ids and names of all the users in the database.

    Example:

  .. code-block:: bash

       python -m cortex.cli get-users

*
  ``get-user <user_id>``

    Returns the specified user information.

    Example:

  .. code-block:: bash

       python -m cortex.cli get-user 42

*
  ``get-snapshots <user_id>``

    Returns a list of the specified user snapshots information.

    Example:

  .. code-block:: bash

       python -m cortex.cli get-snapshots 42

*
  ``get-snapshot <user_id> <snapshot_id>``

    Returns a specific snapshot of a specific user.

    Example:

  .. code-block:: bash

       python -m cortex.cli get-snapshot 42 1

*
  ``get-result <user_id> <snapshot_id> <field_name>``

    Returns a specific snapshot field value.

    Example:

  .. code-block:: bash

       python -m cortex.cli get-result 42 1 'pose'

GUI
~~~


*
  ``run-server --host <server_host> --port <server_port> --api-host <api_host> --api-port <api_port>``

    Runs the GUI web server on host:port which reflects the API on api_host:api_port.

    Example:

  .. code-block:: bash

       python -m cortex.gui run-server \
             --host '127.0.0.1'       \
             --port 8080              \
             --api-host '127.0.0.1'   \
             --api-port 5000

Library
^^^^^^^

The package can be utilized as a library by using the exposed API of each module.

Client
~~~~~~


*
  ``upload_sample(host=<server_host>, port=<server_port>, path=<path_to_sample>)``

    Uploads a sample to a server.

    Example:

  .. code-block:: python

       from cortex.client import upload_sample
       upload_sample(host='127.0.0.1', port=8000, path='sample.mind.gz')

Server
~~~~~~


*
  ``run_server(host=<server_host>, port=<server_port>, publish=<publish_func>)``

    Runs a server which listens on host:port and passes messages received to a publish function.

    Example:

  .. code-block:: python

       from cortex.server import run_server
       def print_message(message):
           print(message)
       run_server(host='127.0.0.1', port=8000, publish=print_message)

Parsers
~~~~~~~


*
  ``run_parser(field=<parser_name>, data=data)``

    Run a specific parser on raw data and return the parsed result.

    Example:

  .. code-block:: python

       from cortex.parsers import run_parser
       data = '...'
       result = run_parser('pose', data)

Saver
~~~~~


*
  ``Saver(db_url)``

    Saver class which connects to a database and saves data by calling its ``save`` method.

    Example:

  .. code-block:: python

       from cortex.saver import Saver
       saver = Saver(db_url=db_url)
       data = '...'
       saver.save('pose', data)

API
~~~


*
  ``run_api_server(host=<server_host>, port=<server_port>, database_url=<db_url>)``

    Runs an API server which listens on host:port and serves data from db_url.\ :raw-html-m2r:`<br>`
    Note: For a list of points that the API exposes follow the link to the docs in the bottom of the page.

    Example:

  .. code-block:: python

       from cortex.api import run_api_server
       run_api_server(host='127.0.0.1', port=5000, database_url='mongodb://127.0.0.1:27017')

GUI
~~~


*
  ``run_server(host=<server_host>, port=<server_port>, api_host=<api_host>, api_port=<api_port>``

    Runs the GUI web server on host:port which reflects the API on api_host:api_port.

    Example:

  .. code-block:: python

       from cortex.gui import run_server
       run_server(host='127.0.0.1', port=8080, api_host='127.0.0.1', api_port=5000)

Pipeline script
^^^^^^^^^^^^^^^


* Run the ``run-pipeline.sh`` script:

  * Deploy the full pipeline
  * Deploy a specific component individually
