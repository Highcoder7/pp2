import re
import json

with open('raw.txt', 'r', encoding='utf-8') as f:
    content = f.read()

prices = re.findall(r'\d{1,3}(?:\s\d{3})*,\d{2}', content)
prices_clean = [float(p.replace(' ', '').replace(',', '.')) for p in prices]

products = []
product_pattern = re.compile(r'^\d+\.\s+(.+)$', re.MULTILINE)
for match in product_pattern.finditer(content):
    product_name = match.group(1).strip()
    if product_name and not product_name.startswith('Стоимость'):
        products.append(product_name)

total_match = re.search(r'ИТОГО:\s*(\d{1,3}(?:\s\d{3})*,\d{2})', content)
total = float(total_match.group(1).replace(' ', '').replace(',', '.')) if total_match else sum(prices_clean)

datetime_match = re.search(r'Время:\s*(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})', content)
datetime_str = datetime_match.group(1) if datetime_match else None

payment_match = re.search(r'([А-Яа-я\s]+карта):', content)
payment_method = payment_match.group(1).strip() if payment_match else None

result = {
    'prices': prices_clean,
    'products': products,
    'total': total,
    'datetime': datetime_str,
    'payment_method': payment_method
}

print(json.dumps(result, ensure_ascii=False, indent=2))
