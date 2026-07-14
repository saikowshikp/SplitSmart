class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:password@localhost/splitsmartdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "supersecretkey"