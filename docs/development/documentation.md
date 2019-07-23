

# Documentation

## Building the documentation locally

Building the documentation locally requires a working installation of [Pandoc](https://pandoc.org/installing.html)
plus a number of Python dependencies that can be installed by executing the following from the `docs` directory:
```bash
pip install -r requirements.txt
```

Once that is done, the HTML documentation can be built by issuing (in the same directory):
```bash
make html
```

An alternative to the last two steps is to run `tox -e docs` in the project root in order to use the `tox` environment
that is used to build the documentation by the continuous integration tests.