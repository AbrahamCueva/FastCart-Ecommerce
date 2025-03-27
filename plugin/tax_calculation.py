from plugin.countries import countries

def tax_calculation(country, order_total):
    tax_rate = 0
    for c in countries():
        if country == c['country']:
            tax_rate += int(float(c['tax_rate'])) / 100 * float(order_total)
    return tax_rate