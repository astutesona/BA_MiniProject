from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, text
from app.extensions import db
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.models.order_item import OrderItem

class InventoryService:
    @staticmethod
    def get_inventory_summary():
        """High-level metrics for inventory dashboard."""
        total_products = Product.query.count()
        active_products = Product.query.filter_by(product_status='Active').count()
        low_stock_products = Product.query.filter(
            Product.stock_quantity <= Product.reorder_level,
            Product.product_status == 'Active'
        ).count()
        out_of_stock = Product.query.filter(
            Product.stock_quantity == 0,
            Product.product_status == 'Active'
        ).count()

        # Valuation
        val_query = db.session.query(
            func.coalesce(func.sum(Product.stock_quantity * Product.unit_cost), 0).label('total_cost_val'),
            func.coalesce(func.sum(Product.stock_quantity * Product.unit_price), 0).label('total_retail_val')
        ).filter(Product.product_status == 'Active').one()

        cost_val = float(val_query.total_cost_val)
        retail_val = float(val_query.total_retail_val)
        potential_profit = retail_val - cost_val

        return {
            'total_products': total_products,
            'active_products': active_products,
            'low_stock_count': low_stock_products,
            'out_of_stock_count': out_of_stock,
            'total_cost_valuation': cost_val,
            'total_retail_valuation': retail_val,
            'potential_gross_profit': potential_profit
        }

    @staticmethod
    def get_category_inventory_valuation():
        """Category-wise inventory stock count and valuation."""
        results = db.session.query(
            Category.category_name,
            func.count(Product.product_id).label('product_count'),
            func.sum(Product.stock_quantity).label('total_units'),
            func.sum(Product.stock_quantity * Product.unit_cost).label('inventory_cost_value'),
            func.sum(Product.stock_quantity * Product.unit_price).label('inventory_retail_value')
        ).join(Product, Category.category_id == Product.category_id)\
         .filter(Product.product_status == 'Active')\
         .group_by(Category.category_id, Category.category_name)\
         .order_by(text('inventory_cost_value DESC')).all()

        return [{
            'category_name': r.category_name,
            'product_count': int(r.product_count or 0),
            'total_units': int(r.total_units or 0),
            'cost_value': float(r.inventory_cost_value or 0),
            'retail_value': float(r.inventory_retail_value or 0)
        } for r in results]

    @staticmethod
    def get_velocity_analysis(days=90):
        """
        Calculates fast-moving vs slow-moving products based on actual units sold in the last N days.
        Fast-moving: Top 25% or units sold > threshold.
        Slow-moving: 0 or low units sold in window with positive stock on hand.
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        sales_sub = db.session.query(
            OrderItem.product_id,
            func.coalesce(func.sum(OrderItem.quantity), 0).label('units_sold_window')
        ).join(Order, OrderItem.order_id == Order.order_id)\
         .filter(Order.order_status == 'Completed', Order.payment_status == 'Paid', Order.order_date >= cutoff_date)\
         .group_by(OrderItem.product_id).subquery()

        results = db.session.query(
            Product.product_id,
            Product.product_name,
            Product.SKU,
            Category.category_name,
            Product.stock_quantity,
            Product.reorder_level,
            Product.unit_cost,
            func.coalesce(sales_sub.c.units_sold_window, 0).label('units_sold')
        ).join(Category, Product.category_id == Category.category_id)\
         .outerjoin(sales_sub, Product.product_id == sales_sub.c.product_id)\
         .filter(Product.product_status == 'Active')\
         .order_by(text('units_sold DESC')).all()

        fast_moving = []
        slow_moving = []
        normal = []

        for r in results:
            item = {
                'product_id': r.product_id,
                'product_name': r.product_name,
                'sku': r.SKU,
                'category_name': r.category_name,
                'stock': r.stock_quantity,
                'reorder_level': r.reorder_level,
                'cost': float(r.unit_cost),
                'units_sold': int(r.units_sold)
            }
            if r.units_sold >= 15:
                fast_moving.append(item)
            elif r.units_sold <= 2 and r.stock_quantity > 0:
                slow_moving.append(item)
            else:
                normal.append(item)

        return {
            'days_window': days,
            'fast_moving': fast_moving,
            'slow_moving': slow_moving,
            'normal': normal
        }
