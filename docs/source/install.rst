.. _gettingstarted:

Getting Started
===============

Requirements
^^^^^^^^^^^^

* Unix-like OS (this project was built and tested on Ubuntu 18.04.4)
* Python >= 3.8, with virtualenv installed
* Docker (for container deployment and pipeline script)

Quickstart
^^^^^^^^^^


#. Clone the repository, run the included script and follow the instructions to get the pipeline running:

   .. code-block:: bash

       git clone https://github.com/bennzo/cortex.git
       cd cortex
       ./scripts/run-pipeline.sh

#. Set up and run the virtual environment:

   .. code-block:: bash

       ./scripts/install.sh
       source .env/bin/activate

#. Use the Client CLI to upload samples to the server:

   .. code-block:: bash

       python -m cortex.client upload-sample -h 127.0.0.1 -p 8000 data/littlesample.mind.gz

#. Open up http://127.0.0.1:8080 to browse your uploaded snapshots.

Install
^^^^^^^

**Note:**


* If you are using a clean OS installation, we recommend the following preliminery steps:

  * Install basic dependencies:

    .. code-block:: bash

         sudo apt install build-essential curl git llvm libbz2-dev libffi-dev\
         liblzma-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev\
         libssl-dev make python-openssl tk-dev wget xz-utils zlib1g-dev

  * Install Python 3.8
  * Install virtualenv for Python 3.8


#. Clone the repository and enter the directory:

   .. code-block:: bash

       git clone https://github.com/bennzo/cortex.git
       cd cortex

#. Install the Python requirements:

   * Either directly with pip to your local Python env:

     .. code-block:: bash

        pip install -r requirements.txt

   * Or create a new virtual environment with the install script:

     .. code-block:: bash

        ./scripts/install.sh
        source .env/bin/activate

#. Run the tests to ensure everything is working as intended:

   .. code-block:: bash

       pytest

Docker deployment
^^^^^^^^^^^^^^^^^

If you wish to deploy the project components individually inside containers:


* Install Docker
* Build the Docker image
* Run the run-pipeline.sh script and follow the instructions
