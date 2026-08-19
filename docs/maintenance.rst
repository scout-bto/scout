.. _maint:

Maintenance
===========

.. _maint-philosophy:

Philosophy
----------

The development of Scout involved, as much as possible, the implementation of what were identified as "best practices," from the programming languages used to the formatting of the code. The language below outlines these practices.

* Use of open-source, well-established programming languages
* Avoiding deprecated or end-of-life languages or versions of languages
* Adherence to established code formatting guidelines and philosophies, when available (e.g., :pep:`8` and :pep:`20`)


.. _maint-contribute:

Contributions
-------------

.. _maint-vcs:

Version Control with Git and GitHub
-----------------------------------

Scout relies on git for version control. 

Before Each Commit
~~~~~~~~~~~~~~~~~~

Making a commit in git should not be a source of heartburn, but there are several steps that should be taken to ensure each commit is high quality.

* Check all modified files for spelling errors (especially in the comment text)
* Check all modified files against appropriate linters (e.g., :pep:`8` and :pep:`257` for Python) or to make sure the file is syntactically valid (e.g., for JSON files)
* Check that the commit message itself is free of typos and spelling errors.
* Check to make sure that all tests are passing

.. Writing Good Commit Messages
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. https://github.com/erlang/otp/wiki/writing-good-commit-messages

.. If you want to contribute to the documentation, you'll also need to install Sphinx. Please also refer to our maintenance (add link) documentation for requirements and recommendations regarding the formatting of all documentation components.


.. _maint-documentation:

Documentation
-------------

The documentation for Scout is prepared using Sphinx, a package originally developed to document Python. Sphinx builds upon the reStructuredText markup language by adding a lot of handy features, like support for LaTeX equation markup with MathJax, automatic figure numbering, and simplified references to Python documentation. reStructuredText is a "semantic" markup language, and as a result, the documentation files have to be built to obtain their final, desired form. 

Before contributing to or updating the documentation, try to think of documentation that you've encountered in the past that has been particularly helpful. Consider what made that documentation so useful to you - clarity of writing, extent of examples, explanations of edge cases, or overall structure. If nothing comes to mind, visit the `Beautiful Docs`_ page for a list of examples of high-quality documentation.

.. _Beautiful Docs: https://github.com/PharkMillups/beautiful-docs

.. http://www.writethedocs.org/guide/writing/beginners-guide-to-docs/

.. SUBSECTIONS AND CONTENT TO ADD
.. useful reference documentation: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html (restructuredtext detailed spec), 
.. rst markup cheatsheet: https://github.com/ralsina/rst-cheatsheet/blob/master/rst-cheatsheet.rst
.. version numbering (https://docs.readthedocs.io/en/latest/versions.html)
.. handling the many 'residential' and 'commercial' links
.. toctree updates to add new sections
.. figure numbering :numfig:
.. the power (and complexity) of cross-referencing and auto-completion
.. the power of substitutions
.. custom configuration of extlinks
.. syntax specific settings and linters for rst/Sphinx (Sublime Text-specific)
.. how to preview documentation locally
.. set up steps so that one can preview documentation in RTD theme (https://github.com/snide/sphinx_rtd_theme)
.. summary of the different types of references/hyperlinks: http://docutils.sourceforge.net/docs/user/rst/quickref.html#hyperlink-targets


.. _maint-data:

Data Generation
---------------

The Scout model relies on a number of disaggregation factor files. These are generated from a common set of input files using the `scout/supporting_data/base_disagg/generate_geo_maps.py` script.

To run the script and generate all output files, execute the following from the `scout/supporting_data/base_disagg` directory:

.. code-block:: bash

   python generate_geo_maps.py

With no flags, this both regenerates all the CSVs and copies them to their final destination within the Scout package. Use `--no-install` to generate into the scratch `output/` directory without copying, or `--install-only` to skip generation and just copy files already sitting in `output/`.

You can also generate specific files or sets of files using the available command-line arguments. Use the `--help` flag to see all options:

.. code-block:: bash

   python generate_geo_maps.py --help


.. FIGURE THIS OUT
.. documentation formatting rules and best practices
.. reference/citation formatting style
.. figure captions
.. 