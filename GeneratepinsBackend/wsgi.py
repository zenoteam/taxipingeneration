from generatepins_backend.app import create_app

application = create_app()
application.run(host="localhost", port=5002, debug=True)
