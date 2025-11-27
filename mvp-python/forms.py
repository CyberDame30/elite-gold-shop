from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo


class RegisterForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            InputRequired(),
            Email(message="Введіть коректний email"),
            Length(min=5),
        ],
    )
    password = PasswordField(
        "Пароль",
        validators=[
            InputRequired(),
            Length(min=6, message="Пароль має бути не менше 6 символів"),
        ],
    )
    confirm_password = PasswordField(
        "Повторіть пароль",
        validators=[
            InputRequired(),
            EqualTo("password", message="Паролі не співпадають"),
        ],
    )
    submit = SubmitField("Зареєструватися")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            InputRequired(),
            Email(message="Введіть коректний email"),
        ],
    )
    password = PasswordField(
        "Пароль",
        validators=[
            InputRequired(),
            Length(min=6),
        ],
    )
    submit = SubmitField("Увійти")

