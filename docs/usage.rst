========
Usage
========

To start astrocoffee for the first time:

.. code-block:: bash

    $ export FLASK_APP=astrocoffee
    $ flask initdb
    $ flask mkuser
    $ flask run

To start astrocoffee without database and user creation:

.. code-block:: bash

    $ export FLASK_APP=astrocoffee
    $ flask run
