def validate_sensor_data(data):
    """
    Returns True if the sensor data is valid, otherwise False.
    """

    if not (0 <= data["temperature"] <= 15):
        return False

    if not (0 <= data["humidity"] <= 100):
        return False

    if not (0 <= data["vibration"] <= 10):
        return False

    if not (0 <= data["battery"] <= 100):
        return False

    if data["door_status"] not in ["OPEN", "CLOSED"]:
        return False

    return True