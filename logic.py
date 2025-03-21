def process_data(data):
    # Example: Modify the input data
    if "name" in data:
        data["greeting"] = f"Hello, {data['name']}!"
    return data
