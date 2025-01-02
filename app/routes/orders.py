from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from app.forms import TableAssignmentForm, TableActionsForm
from app.models import MenuItem, Order, OrderDetail, Table, Employee, db

bp = Blueprint("orders", __name__, url_prefix="")


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Instantiate the form
    form = TableAssignmentForm()
    formOrders = TableActionsForm()
    tables = Table.query.order_by(Table.number).all()
    open_orders = Order.query.filter(Order.finished == False)

    # Get the table ids for the open orders
    busy_table_ids = [order.table_id for order in open_orders]

    # Filter the list of tables for only the open tables
    open_tables = [table for table in tables if table.id not in busy_table_ids]

    # Populate the select fields with tables and employees
    form.tables.choices = [(-1, "Select Table")] + [
        (t.id, f"Table {t.number}") for t in open_tables
    ]
    form.servers.choices = [(-1, "Select Server")] + [
        (employee.id, employee.name) for employee in Employee.query.all()
    ]

    # handling employee specific orders
    order_sums = (
        db.session.query(
            Table.number.label("table_number"),
            func.coalesce(func.sum(MenuItem.price), 0).label("total_price"),
        )
        .outerjoin(Order, Table.orders)
        .outerjoin(OrderDetail, Order.details)
        .outerjoin(MenuItem, OrderDetail.menu_item)
        .filter(Order.employee_id == current_user.id)
        .filter(Order.finished == False)
        .group_by(Table.id)
        .all()
    )
    if formOrders.validate_on_submit():
        table_number = request.form.get(
            "table_number"
        )  # Get table_number directly from form
        if table_number:
            table_number = int(table_number)  # Convert to int if needed
            # Now you can perform actions based on table_number

            if formOrders.close_table.data:
                # Handle "Close Table" action
                orders = (
                    Order.query.join(Table)
                    .filter(Table.number == table_number, Order.finished == False)
                    .all()
                )
                if orders:
                    for order in orders:
                        order.finished = True
                    db.session.commit()
                    return redirect(url_for("orders.index"))
                else:
                    print(f"No open orders found for table {table_number}")

            elif formOrders.add_to_order.data:
                # Handle "Add to Order" action
                print(f"Adding to order for table {table_number}")
                # Add your "Add to Order" logic here

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
        "orders.html",
        form=form,
        tables=tables,
        employees=employees,
        orders=orders,
        order_sums=order_sums,
        formOrders=formOrders,
    )
