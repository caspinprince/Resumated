from app import create_app
from werkzeug.middleware.profiler import ProfilerMiddleware

app = create_app()

app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[8], profile_dir='test_results')
app.run(debug=True)