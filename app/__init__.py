import os
import threading
from flask import Flask, jsonify, render_template, redirect, request, url_for, session
from app.models import db, People, Drink
from app.admin_routes import admin_bp
from app.public_routes import public_bp
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, ConversationHandler
from telegram.ext import filters

# Структура данных для хранения напитков
user_data = []

# Состояния для ConversationHandler
CHOOSE_DRINK, ENTER_VOLUME = range(2)

# Доступные напитки
DRINKS = ["Пиво", "Вискарь", "Водку", "Коньяк", "Текилу", "Ром"]

def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [DRINKS]
    update.message.reply_text(
        "Здорова, заебал! Что бухал:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSE_DRINK

def choose_drink(update: Update, context: CallbackContext) -> int:
    drink = update.message.text
    context.user_data['drink'] = drink
    update.message.reply_text(f"Вы выбрали {drink}. Укажите объем в литрах:")
    return ENTER_VOLUME

def enter_volume(update: Update, context: CallbackContext) -> int:
    try:
        volume = float(update.message.text)
        drink = context.user_data['drink']
        user_data.append({"drink": drink, "volume": volume})
        update.message.reply_text(f"Результат засчитан: {drink}, объем: {volume} л. Отдыхай!")
        return ConversationHandler.END
    except ValueError:
        update.message.reply_text("Пожалуйста, введите число.")
        return ENTER_VOLUME

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

# Функция для создания Flask приложения
def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY")
    
    # Конфигурация базы данных
    db_username = os.getenv("DB_USERNAME")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "db")
    db_name = os.getenv("DB_NAME", "drink_db")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_username}:{db_password}@{db_host}:5432/{db_name}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        # Проверяем, если таблицы пустые, то создаем и инициализируем
        db.create_all()

        try:
            # Пробуем получить пользователей
            people = db.session.query(People).all()
            if not people:
                # Если людей нет, инициализируем
                default_people = [
                    People(name="Иван"),
                    People(name="Мария")
                ]
                db.session.bulk_save_objects(default_people)
                db.session.commit()

                # Добавляем напитки
                ivan = db.session.query(People).filter_by(name="Иван").first()
                maria = db.session.query(People).filter_by(name="Мария").first()
                ivan.drinks = [
                    Drink(drink_name="Пиво", volume=3.0),
                    Drink(drink_name="Виски", volume=0.7)
                ]
                maria.drinks = [
                    Drink(drink_name="Пиво", volume=1.5),
                    Drink(drink_name="Виски", volume=0.5)
                ]
                db.session.commit()
        
        except OperationalError:
            print("Ошибка: не удалось подключиться к базе данных.")
        
    # Регистрируем Blueprint после создания приложения
    app.register_blueprint(admin_bp)
    app.register_blueprint(public_bp)

    # Регистрируем маршруты
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if username == 'admin' and password == 'password':  # Проверка логина
                session['user'] = username
                return redirect(url_for('admin_dashboard'))
            else:
                return "Неверный логин или пароль", 403
        return render_template('login.html')

    @app.route('/admin')
    def admin_dashboard():
        if 'user' not in session:
            return redirect(url_for('login'))
        
        people = People.query.all()
        user_drinks = {}

        for person in people:
            user_drinks[person.name] = {}
            for drink in person.drinks:
                if drink.drink_name in user_drinks[person.name]:
                    user_drinks[person.name][drink.drink_name] += drink.volume
                else:
                    user_drinks[person.name][drink.drink_name] = drink.volume
        
        return render_template('dashboard.html', user_drinks=user_drinks)

    @app.route('/drink')
    def drink_table():
        return render_template('drink_table.html')

    @app.route('/data', methods=['GET'])
    def get_data():
        return jsonify(user_data)

    return app

# Функция для запуска телеграм-бота
def run_telegram_bot():
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token:
        raise ValueError("TELEGRAM_TOKEN не установлен в переменных окружения")

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE_DRINK: [MessageHandler(filters.text & ~filters.command, choose_drink)],
            ENTER_VOLUME: [MessageHandler(filters.text & ~filters.command, enter_volume)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

# Основная функция для запуска приложения
if __name__ == '__main__':
    app = create_app()  # Используем create_app для создания приложения
    threading.Thread(target=run_telegram_bot).start()
    app.run(debug=True, port=5000)
