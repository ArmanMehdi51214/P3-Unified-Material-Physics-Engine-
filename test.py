from p3_cdda.cdda_loader import CddaLoader

loader = CddaLoader("path/to/CDDA/data/json")
items = loader.load_all_items()

print("Loaded:", len(items))
print(items[:5])
