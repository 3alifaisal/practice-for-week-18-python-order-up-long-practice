from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError, NumberRange


class LoginForm(FlaskForm):
    # Field definitions
    employee_number = StringField("Employee number", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class TableAssignmentForm(FlaskForm):
    tables = SelectField(
        "Tables",
        coerce=int,
        validators=[DataRequired(message="Please select a table.")],
    )
    servers = SelectField(
        "Servers",
        coerce=int,
        validators=[DataRequired(message="Please select a server.")],
    )
    assign = SubmitField("Assign")

    def validate_tables(form, field):
        if field.data == -1:  # The value for the placeholder
            raise ValidationError("Please select a valid table.")

    def validate_servers(form, field):
        if field.data == -1:  # The value for the placeholder
            raise ValidationError("Please select a valid server.")


class TableActionsForm(FlaskForm):
    close_table = SubmitField("Close Table")
    add_to_order = SubmitField("Add to Order")


class MenuItemsForm(FlaskForm):
    menu_item = IntegerField(
        "item",
        default=0,
        validators=[
            NumberRange(min=0, message="Value cannot be negative."),
            DataRequired("Cannot be empty"),
        ],
    )
