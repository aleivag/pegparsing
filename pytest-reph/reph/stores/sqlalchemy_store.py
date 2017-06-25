
from datetime import datetime
from collections import namedtuple
from reph.stores.base_store import ReportStore


class SQLAlchemyStore(ReportStore):

    def __init__(self, store_uri, session_id):
        super(SQLAlchemyStore, self).__init__(store_uri, session_id)

        from sqlalchemy import (
            create_engine, ForeignKey, Column, Integer, String, Float, DateTime
        )
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import relationship, sessionmaker

        self.engine = create_engine(store_uri, echo=False)
        self.Base = declarative_base(bind=self.engine)
        self.Session = sessionmaker(self.engine)

        class Session(self.Base):
            __tablename__ = 'Session'

            id = Column(String(), primary_key=True)
            start = Column(DateTime, default=datetime.utcnow)
            end = Column(DateTime)

        class Tag(self.Base):
            __tablename__ = 'Tag'

            id = Column(Integer, primary_key=True)
            session_id = Column(String, ForeignKey('Session.id'))
            key = Column(String)
            value = Column(String)

        class Test(self.Base):
            __tablename__ = 'Test'

            nodeid = Column(String(), primary_key=True)

        class TestResult(self.Base):
            __tablename__ = 'TestResult'

            id = Column(Integer, primary_key=True)
            nodeid = Column(String(), ForeignKey('Test.nodeid'))
            session_id = Column(String(), ForeignKey('Session.id'))

            stage_setup_duration = Column(Float)
            stage_call_duration = Column(Float)
            stage_teardown_duration = Column(Float)

            stage_setup_outcome = Column(String())
            stage_call_outcome = Column(String())
            stage_teardown_outcome = Column(String())

            test = relationship('Test', backref='results')
            session = relationship('Session', backref='results')

        class TestTimer(self.Base):
            __tablename__ = 'TestTimer'

            id = Column(Integer, primary_key=True)

            test_result_id = Column(Integer, ForeignKey('TestResult.id'))
            timer_name = Column(String())

            duration = Column(Float, nullable=False)

            test_result = relationship('TestResult', backref='timers')

        self.Base.metadata.create_all()

        self.model = namedtuple(
            'model',
            ['Test', 'TestResult', 'TestTimer', 'Session', 'Tag']
        )(
            Test=Test,
            TestResult=TestResult,
            TestTimer=TestTimer,
            Session=Session,
            Tag=Tag,
        )

        session = self.Session()
        if not session.query(self.model.Session).get(self.session_id):
            session.add(self.model.Session(id=self.session_id))

        session.commit()
        session.close()

    def commit_row(self, row):
        session = self.Session()

        if not session.query(self.model.Session).get(self.session_id):
            session.add(self.model.Session(id=self.session_id))

        if not session.query(self.model.Test).get(row.nodeid):
            session.add(self.model.Test(nodeid=row.nodeid))

        test_result = self.model.TestResult(
            nodeid=row.nodeid, session_id=self.session_id,

            stage_setup_duration=row.stage_setup_duration,
            stage_call_duration=row.stage_call_duration,
            stage_teardown_duration=row.stage_teardown_duration,

            stage_setup_outcome=row.stage_setup_outcome,
            stage_call_outcome=row.stage_call_outcome,
            stage_teardown_outcome=row.stage_teardown_outcome,
        )
        session.add(test_result)

        for timer in row.timers:
            session.add(
                self.model.TestTimer(
                    test_result=test_result,
                    timer_name=timer.name,
                    duration=timer.tf - timer.t0
                )
            )

        session.commit()

    def commit(self):
        session = self.Session()
        for k, v in self.tags.items():
            session.add(self.model.Tag(
                session_id=self.session_id,
                key=k, value=v
            ))
        session.query(self.model.Session).filter_by(id=self.session_id).update(
            {'end': datetime.utcnow()})
        session.commit()
        session.close()
