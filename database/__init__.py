import sqlalchemy


engine = sqlalchemy.create_engine('postgresql+psycopg2://localhost:5432/bachelor')
# engine = sqlalchemy.create_engine('mysql+pymysql://root:admin@localhost/bachelor?charset=utf8')
connection = engine.connect()
