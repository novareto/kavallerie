from webtest import TestApp as WSGIApp

from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import register

from kavallerie.response import Response
from kavallerie.app import RoutingApplication
from kavallerie.pipes.transaction import Transaction


Base = declarative_base()


class Person(Base):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    age = Column(Integer)


def test_middleware():

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    DBSession = scoped_session(sessionmaker(bind=engine))
    register(DBSession)

    app = RoutingApplication(config={
        'database': {
            'session_factory': DBSession
        }
    })
    Transaction().join(app.pipeline)

    @app.routes.register('/create', methods=('POST',))
    def create(request):
        person = Person(name="MacBeth", age=35)
        request.db_session.add(person)
        request.db_session.flush()
        return Response(201)

    @app.routes.register('/person/{id}')
    def fetch(request, id):
        person = request.db_session.query(Person).get(id)
        return Response(200, body=person.name)

    test = WSGIApp(app)
    response = test.post('/create')
    assert response.body == b'Document created, URL follows'

    response = test.get('/person/1')
    assert response.body == b'MacBeth'

    person = DBSession().query(Person).get(1)
    assert person is not None
    assert person.age == 35
