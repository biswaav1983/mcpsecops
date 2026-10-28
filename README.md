Compromised Third Party Package
we will install the malicious version of fastmcp from the local index.

Uploading to the Internal Index (PyPi Server needs to be installed )
Upload with twine using the internal index URL.
cd  /malicious-fastmcp-build
python3 -m twine upload --repository-url http://192.168.40.147:5001 dist/*

Execute a Poisoned Pipeline Attack Against an MCP Deployment
When a CI/CD pipeline builds an MCP deployment, it installs Python dependencies automatically using pip. Without a pinned source index, the pipeline will accept any package that matches the name and satisfies the version range, including one from an attacker-controlled index.

Legitimate Project Versus Exercise Build

Real fastmcp on public PyPI is maintained by its authors and is appropriate for normal development.

The malicious fastmcp build exists only on the lab-scoped internal index for training purposes.

Never push the exercise build to public PyPI or under a typosquatted name, even for testing.


