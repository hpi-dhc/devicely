# How to add documentation for a new module in devicely

We use [sphinx](https://www.sphinx-doc.org/en/master/index.html), a tool to document Python packages based on the [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html) markup language.

To get started, you need the packages **sphinx**, **sphinx_rtd_theme** and **nbsphinx**, all of which can be installed with pip. You also need to pip install devicely itself.

The main file to work on is **index.rst**. Please add a short example use case for your newly written module to it. The existing examples should provide enough help. The example will be seen on the [main documentation page](https://hpi-dhc.github.io/devicely/index.html).
Also you need to add docstrings to your module. The docstrings will be seen in the [module reference](https://hpi-dhc.github.io/devicely/index.html#module-reference). Please write one docstring for your class and one for each method that you want users to access. You can just copy the docstrings of existing modules and adjust them for your needs. Also add an *automodule* tag for your module to the bottom of **index.rst**.

When you are done, run **make html**. You can ignore the warnings. This will create some files in _build/html. Move them to the **docs** directory in the root of the repo, but make sure the **docs** directory contains an empty file called **.nojekyll**. Then you should be able to see your docs online. Please run **make clean** before pushing.
