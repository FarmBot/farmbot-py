# Local development

If you are working on farmbot-py itself,

(1) Clone the repository.
```bash
git clone https://github.com/FarmBot/farmbot-py
```

(2) Navigate to the project directory.
```bash
cd farmbot-py
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

Update the version number in `farmbot/main.py`.
```python
VERSION = "2.0.0"
```

Verify that tests pass and coverage is still at 100%.
```bash
coverage run -m unittest discover
coverage html
```

Commit and push the version bump (and any other changes already committed).
```bash
git add farmbot/main.py
git commit -m "v2.0.0"
git push origin main
```
Review GitHub Actions, verifying that the `test` workflow has passed,
and approve the "Publish to TestPyPI" workflow.
This will upload the package to TestPyPI.

Once the package has been published to TestPyPI,
install it in a new virtual environment to verify that it works as expected.
```bash
python -m venv test_venv
source test_venv/bin/activate
python -m pip install requests paho-mqtt

python -m pip install --index-url https://test.pypi.org/simple/ --no-deps --upgrade farmbot
```

If it does, create and upload a tag.
```bash
git tag v2.0.0
git push origin v2.0.0
```

Approve the "Publish to PyPI" workflow in GitHub Actions. This will upload the package to PyPI and create a GitHub release.

Review the GitHub release, and add a change log to the release notes.
