from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from app.forms import TableAssignmentForm
from app.models import Order, Table, Employee, db

bp = Blueprint("orders", __name__, url_prefix="")


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Instantiate the form
    form = TableAssignmentForm()

    # Populate the select fields with tables and employees
    form.tables.choices = [(-1, "Select Table")] + [
        (table.id, table.number) for table in Table.query.all()
    ]
    form.servers.choices = [(-1, "Select Server")] + [
        (employee.id, employee.name) for employee in Employee.query.all()
    ]

    # If form is submitted and validated, process the order
    if form.validate_on_submit():
        table_id = form.tables.data
        employee_id = form.servers.data

        try:
            # Create a new order
            order = Order(table_id=table_id, employee_id=employee_id, finished=False)
            db.session.add(order)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            flash(f"Error assigning table: {e}", "error")

        return redirect(url_for("orders.index"))

    # Render the page with table, employee data, and form
    tables = Table.query.all()
    employees = Employee.query.all()
    orders = Order.query.filter_by(finished=False).all()

    return render_template(
        "orders.html", form=form, tables=tables, employees=employees, orders=orders
    )
