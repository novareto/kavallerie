Kavallerie
==========

Full-blown WSGI Framework using Horseman.


.. code-block:: python

  from kavallerie.app import RoutingApplication
  from kavallerie.response import Response


  app = RoutingApplication()

  @app.routes.register('/json')
  def json(request):
      return Response.to_json(body={'message': "Hello, world!"})


  if __name__ == "__main__":
      import bjoern
      bjoern.run(app, "127.0.0.1", 8000)
