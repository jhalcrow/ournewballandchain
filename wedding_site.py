#!/usr/bin/env python

from ournewballandchain import create_app, DefaultConfig, ProductionConfig

app = create_app(ProductionConfig)
app.run(debug=True, host='0.0.0.0')