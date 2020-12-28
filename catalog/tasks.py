# from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
import time
from datetime import timedelta, date
# import datetime
from plyer import notification

from .models import Product

logger = get_task_logger(__name__)


@periodic_task(
    run_every=(crontab(minute='*/30')),
    name="task_save_10_days_to_expire_product",
    ignore_result=True
)
def expiry_date():
    try:
        products = Product.objects.all()
        for product in products:
            dt = date.today() + timedelta(10)
            print(dt)
            if product.expiring_date > dt:
                logger.info("{pro} expires on {dt}. 10 days before the expiring date.".format(
                    pro=product.name, dt=dt))
                return notification.notify(
                    title="URGENT INFORMATION ON PRODUCT!",
                    message="{pro} expires on {dt}. 10 days before the expiring date.".format(
                        pro=product.name, dt=dt),
                    app_name="JKF-VICTORY LIMITED",
                    ticker='URGENT PRODUCT INFORMATION',
                    timeout=20
                )
                time.sleep(15)
            else:
                return notification.notify(
                    title="INVENTORY INFORMATION!",
                    message="Inventory up to Date!!!",
                    app_name="JKF-VICTORY LIMITED",
                    ticker='PRODUCT INFORMATION',
                    timeout=20
                )
                time.sleep(15)
    except Exception:
        return 'Field "name" does not exist.'
    return


@periodic_task(
    run_every=(crontab(minute='*/30')),
    name="task_save_expired_products",
    ignore_result=True
)
def expired():
    try:
        products = Product.objects.all()
        for product in products:
            dt = date.today()
            if product.expiring_date == dt:
                logger.info("{pro} has expired.".format(
                    pro=product.name))
                return notification.notify(
                    title="EXPIRED PRODUCT NOTIFICATION!",
                    message="{pro} has expired.".format(
                        pro=product.name),
                    app_name="JKF-VICTORY LIMITED",
                    ticker='URGENT PRODUCT INFORMATION',
                    timeout=15
                )
                time.sleep(30)
    except Exception:
        return 'Field "name" does not exist'
    return


@periodic_task(
    run_every=(crontab(minute='*/30')),
    name="task_stock_level",
    ignore_result=True
)
def stock_level():
    try:
        products = Product.objects.all()
        for product in products:
            if product.stock == product.minimum_stock:
                logger.info("{pro} has reached it's minimum stock level.".format(
                    pro=product.name))
                return notification.notify(
                    title="STOCK LEVEL NOTIFICATION!",
                    message="{pro} has reached it's minimum stock level.".format(
                        pro=product.name),
                    app_name="JKF-VICTORY LIMITED",
                    ticker='INVENTORY INFORMATION',
                    timeout=15
                )
                time.sleep(30)
    except Exception:
        return 'Field "name" does not exist'
    return
