from generatepins_backend.app import create_app

application = create_app()
application.run(port=8080)
