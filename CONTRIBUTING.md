# Local development

If you are working on the sidecar-starter-pack itself,

(1) Clone the repository.
```bash
git clone https://github.com/FarmBot-Labs/sidecar-starter-pack
```

(2) Navigate to the project directory.
```bash
cd sidecar-starter-pack
```

(3) Create a virtual environment.
```bash
python -m venv py_venv
```

(4) Activate the virtual environment.
```bash
source py_venv/bin/activate
```

(5) Install the required libraries within the virtual environment:
```bash
python -m pip install requests paho-mqtt coverage
```

Ensure any changes pass all tests before submitting a pull request.

```bash
coverage run -m unittest discover
coverage html
```

You can review test coverage by opening `htmlcov/index.html` in a browser.

# Uploading package to PyPI (For FarmBot employees)

Follow [this tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/).
```bash
python -m pip install --upgrade pip build twine
rm dist/*
python -m build
python -m twine upload dist/*
```
