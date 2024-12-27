import os

class Config:
    SECRET_KEY = "your_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # تأكد من تخزين البريد الإلكتروني في البيئة أو متغيرات النظام
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # تأكد من تخزين كلمة المرور في البيئة أو متغيرات النظام
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True