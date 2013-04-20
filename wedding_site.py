#!/usr/bin/env python

from ournewballandchain import create_app, DefaultConfig

app = create_app(DefaultConfig())
app.run(debug=True)