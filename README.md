## dploy-kickstart

[![codecov](https://codecov.io/gh/dploy-ai/dploy-kickstart/branch/master/graph/badge.svg?token=KypiVRoPJz)](https://codecov.io/gh/dploy-ai/dploy-kickstart)

Expose your Python functions via an HTTP API.

### Current dependency tree

Aim is to keep this as small as possible to not clutter the user space.

```
$ poetry show --no-dev --tree

apispec 3.3.0 A pluggable API specification generator. Currently supports the OpenAPI Specification (f.k.a. the Swagger specification).
click 7.1.2 Composable command line interface toolkit
flask 1.1.2 A simple framework for building complex web applications.
├── click >=5.1
├── itsdangerous >=0.24
├── jinja2 >=2.10.1
│   └── markupsafe >=0.23 
└── werkzeug >=0.15
paste 3.4.0 Tools for using a Web Server Gateway Interface stack
└── six >=1.4.0
waitress 1.4.3 Waitress WSGI server
```