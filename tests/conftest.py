import pytest
from flexmock import flexmock

from cucoslib.enums import EcosystemBackend
from cucoslib.models import Base, Ecosystem, create_db_scoped_session
from cucoslib.setup_celery import get_dispatcher_config_files
from cucoslib.storages import AmazonS3
from selinon import Config


@pytest.fixture
def rdb():
    session = create_db_scoped_session()
    # TODO: we may need to run actual migrations here
    # make sure all session objects from scoped_session get closed here
    #  otherwise drop_all() would hang indefinitely
    session.close_all()
    # NOTE: this also drops any data created by fixtures (e.g. builtin ecosystems),
    #   so if you want to use these, create them by hand before running your tests
    # We can't use Base.metadata.drop_all(bind=session.bind), since they may be tables from
    #   e.g. bayesian server, that reference cucoslib tables and will prevent dropping them
    tables = session.bind.table_names()
    for t in tables:
        session.execute('drop table if exists "{t}" cascade'.format(t=t))
        session.commit()
    Base.metadata.create_all(bind=session.bind)
    return session


@pytest.fixture
def maven(rdb):
    maven = Ecosystem(name='maven', backend=EcosystemBackend.maven,
                      fetch_url='')
    rdb.add(maven)
    rdb.commit()
    return maven


@pytest.fixture
def npm(rdb):
    npm = Ecosystem(name='npm', backend=EcosystemBackend.npm,
                    fetch_url='https://registry.npmjs.org/')
    rdb.add(npm)
    rdb.commit()
    return npm


@pytest.fixture
def pypi(rdb):
    pypi = Ecosystem(name='pypi', backend=EcosystemBackend.pypi,
                     fetch_url='https://pypi.python.org/pypi')
    rdb.add(pypi)
    rdb.commit()
    return pypi


@pytest.fixture
def rubygems(rdb):
    rubygems = Ecosystem(name='rubygems', backend=EcosystemBackend.rubygems,
                         fetch_url='https://rubygems.org/api/v1')
    rdb.add(rubygems)
    rdb.commit()
    return rubygems


@pytest.fixture()
def dispatcher_setup():
    """ Setup environment for Dispatcher if needed """
    nodes_yaml, flows_yaml = get_dispatcher_config_files()
    Config.set_config_yaml(nodes_yaml, flows_yaml)


@pytest.fixture()
def no_s3_connection():
    flexmock(AmazonS3).should_receive('is_connected').and_return(True)
