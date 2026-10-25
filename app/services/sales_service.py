from datetime import datetime
from decimal import Decimal
from app.extensions import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.customer import Customer

class SalesService:
    @staticmethod
    def create_order(customer_id, items_data, user_id=None, payment_method='Credit Card',
                     order_status='Completed', payment_status='Paid', order_date=None):
        """
        Creates an order inside a strict ACID database transaction.
        items_data: list of dicts: [{'product_id': int, 'quantity': int, 'discount': Decimal}]
        Validates stock availability, snapshots current price and cost, and records order items.
        Rolls back entirely if any error occurs.
        """
        if not customer_id:
            raise ValueError("Customer must be selected for the order.")
        if not items_data or len(items_data) == 0:
            raise ValueError("An order must contain at least one line item.")

        customer = Customer.query.get(customer_id)
        if not customer:
            raise ValueError("Selected customer does not exist.")

        if not order_date:
            order_date = datetime.utcnow()

        try:
            # 1. Instantiate the Order Header
            order = Order(
                customer_id=customer_id,
                order_date=order_date,
                order_status=order_status,
                payment_status=payment_status,
                payment_method=payment_method,
                created_by=user_id
            )
            db.session.add(order)
            db.session.flush() # Allocates order.order_id

            # 2. Process each Line Item
            for item in items_data:
                prod_id = item.get('product_id')
                qty = int(item.get('quantity', 1))
                discount = Decimal(str(item.get('discount', 0.00)))

                if qty <= 0:
                    raise ValueError(f"Quantity must be positive (received {qty}).")
                if discount < Decimal('0.00'):
                    raise ValueError("Discount cannot be negative.")

                product = Product.query.get(prod_id)
                if not product:
                    raise ValueError(f"Product #{prod_id} not found in catalog.")
                if product.product_status != 'Active':
                    raise ValueError(f"Product '{product.product_name}' is not currently Active.")

                # Check inventory if completing order
                if order_status in ['Completed', 'Processing']:
                    if product.stock_quantity < qty:
                        raise ValueError(
                            f"Insufficient stock for '{product.product_name}'. "
                            f"Available: {product.stock_quantity}, Requested: {qty}"
                        )
                    # Deduct inventory atomically
                    product.stock_quantity -= qty

                gross_amount = product.unit_price * qty
                if discount > gross_amount:
                    raise ValueError(f"Discount (${discount}) cannot exceed item gross total (${gross_amount}).")

                # Point-in-time price and cost snapshot
                order_item = OrderItem(
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=qty,
                    unit_price_at_sale=product.unit_price,
                    unit_cost_at_sale=product.unit_cost,
                    discount_amount=discount
                )
                db.session.add(order_item)

            # 3. Commit entire transaction
            db.session.commit()
            return order

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_order_status(order_id, new_order_status, new_payment_status=None):
        """Updates order status with appropriate inventory adjustments."""
        order = Order.query.get_or_404(order_id)
        old_status = order.order_status

        # If transitioning from Completed to Cancelled or Returned, replenish stock
        if old_status == 'Completed' and new_order_status in ['Cancelled', 'Returned']:
            for item in order.items:
                product = Product.query.get(item.product_id)
                if product:
                    product.stock_quantity += item.quantity

        # If transitioning from Cancelled to Completed, deduct stock
        elif old_status in ['Cancelled', 'Returned'] and new_order_status == 'Completed':
            for item in order.items:
                product = Product.query.get(item.product_id)
                if product:
                    if product.stock_quantity < item.quantity:
                        raise ValueError(f"Cannot complete order: Insufficient stock for '{product.product_name}'.")
                    product.stock_quantity -= item.quantity

        order.order_status = new_order_status
        if new_payment_status:
            order.payment_status = new_payment_status

        db.session.commit()
        return order
