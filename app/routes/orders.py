from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from app.forms import TableAssignmentForm, TableActionsForm, MenuItemsForm
from app.models import Menu, MenuItem, Order, OrderDetail, Table, Employee, db
from collections import defaultdict
from sqlalchemy.orm import joinedload
import json

bp = Blueprint("orders", __name__, url_prefix="")


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Instantiate the form
    form = TableAssignmentForm()
    formOrders = TableActionsForm()
    menuItemsForm = MenuItemsForm()
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
    # Query the data and structure it
    menus = Menu.query.options(joinedload(Menu.items).joinedload(MenuItem.type)).all()

    # Structure the data into the nested dictionary
    menus_data = defaultdict(lambda: defaultdict(list))

    for menu in menus:
        for menu_item in menu.items:
            menu_type_name = menu_item.type.name  # Access the MenuItemType name
            menus_data[menu.name][menu_type_name].append(menu_item)
    # Query the data and structure it

    if formOrders.validate_on_submit():
        table_number = request.form.get(
            "table_number"
        )  # Get table_number directly from form
        if table_number:
            table_number = int(table_number)
        orders = (
            Order.query.join(Table)
            .filter(Table.number == table_number, Order.finished == False)
            .all()
        )
        if formOrders.close_table.data:
            # Handle "Close Table" action

            orders[0].finished = True
            db.session.commit()
            return redirect(url_for("orders.index"))

        action = request.form.get("action")
        if action == "add_to_order":
            menu_items = json.loads(request.form.get("menu_item"))
            print(menu_items)
            if menu_items:
                for menu_item in menu_items:
                    item_id = int(menu_item[0])  # Menu item ID
                    quantity = int(menu_item[1])  # Quantity

                    for _ in range(quantity):
                        # Assuming orders[0] is the relevant order ID
                        orderDetail = OrderDetail(
                            order_id=orders[0].id, menu_item_id=item_id
                        )
                        db.session.add(orderDetail)
            db.session.commit()
            return redirect(url_for("orders.index"))

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
        menus_data=menus_data,
        menuItemsForm=menuItemsForm,
    )
