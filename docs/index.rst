Brewlog
=======

Homebrewer's log web application. There are many other but mine is special in
that is mostly prose. It's not a recipe design app, nor tasting note
collection. It was intended to keep track of my brewing and collect my recipes
for easier reuse. And because my brewing is sometimes a bit of improvisation,
the application was designed to account for it. Most of input is not required,
recipes can be made as incomplete (or complete) as one sees fit. Almost nothing
is calculated, there are almost no dependencies, because this is brew tracking,
not recipe design. Seasoned homebrewers know that to grasp a spirit of brew the
recipe is almost nothing, and the process is almost everything.

This is web application written in Python (Flask, SQLAlchemy, Jinja and other
usual suspects). I wanted it to be lightweight so it's not "rich" by any means,
rather simplistic. And by "lightweight" I mean both sides, server and client.
It had to be cheap in maintenance too, so it's just database + app server + web
server because not much more will fit cheap VPS with 1 core and 1 GB RAM.

I use it mostly on my mobile phone so I made it with that usage model in mind,
with all implications like intentional lack of Internet Explorer compatibility.
It should look normal in other modern browsers though.


Practicalia
-----------

.. toctree::
    :maxdepth: 2

    deployment


Project documents
-----------------

.. toctree::
    :maxdepth: 2

    coc
    contributing
    changelog



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
