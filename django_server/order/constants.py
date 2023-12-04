ORDER_STATUS_CHOICES = [
    (1, "pending"),
    (2, "confirmed"),
    (3, "Success"),
    (4, "Rejected"),
]

PAYMENT_STATUS_CHOICES = [
    (1, "pending"),
    (2, "Success"),
    (3, "Rejected"),
]

DELIVERY_STATUS_CHOICES = [
    (1, "pending"),
    (2, "delivering"),
    (3, "delivered"),
    (4, "error"),
]

PAYMENT_METHOD_CHOICES = [
    (1, "Visa"),
    (2, "Mastercard"),
    (3, "Maestro"),
    (4, "American Express"),
    (5, "Union Pay"),
    (6, "Link"),
    (7, "Alipay"),
    (8, "WeChat Pay"),
    (9, "EPS"),
    (10, "FPS"),
    (11, "Payme"),
    (12, "Octopus")
]