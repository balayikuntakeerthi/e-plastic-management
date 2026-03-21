class Config:
    SECRET_KEY = 'eplastic-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root%40123@localhost/e_plastic_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False