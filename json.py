import json

print("1:")
with open('sample-data.json', 'r') as f:
    data = json.load(f)

print("Interface Status")
print("DN" + " " * 50 + "Description" + " " * 10 + "Speed" + " " * 10 + "MTU")
print("-" * 80)

for item in data['imdata']:
    attrs = item['l1PhysIf']['attributes']
    dn = attrs['dn']
    descr = attrs['descr']
    speed = attrs['speed']
    mtu = attrs['mtu']
    print(f"{dn:<60} {descr:<20} {speed:<15} {mtu}")
