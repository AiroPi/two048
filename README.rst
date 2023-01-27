two048 python module
====================

This module provides a backend for the two048 game.

Find its documentation at https://two048.readthedocs.org/en/latest/. Not really useful, the code is simple you can check it directly.

Install it with :
``pip install two048``

Use it with :

.. code-block:: python

    from two048 import Two048

    game = Two048()

    while not game.is_over():
        print(game)
        direction = input("Choose a direction (up/down/right/left): ")
        game.play(direction)

You can easily create an interface using this module. ``game.play()`` return a list of all the tile movements, so you can easily animate them.
