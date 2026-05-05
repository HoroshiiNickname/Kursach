Программа поддерживает два способа ввода данных об образцах:

Ручной ввод — значения характеристик вводятся в консоли.

Загрузка из файла — CSV или JSON файл с данными образцов

## CSV

    name,flight_time,range,resolution,position_accuracy,payload,wind_resistance,thermal
    DJI Mavic 3 Enterprise Thermal,45,15,48,1.5,1.0,12,1
    Autel EVO Max 4T,42,20,50,1.2,1.2,15,1

## JSON

    [
        {
            "name": "DJI Mavic 3 Enterprise Thermal",
            "flight_time": 45,
            "range": 15,
            "resolution": 48,
            "position_accuracy": 1.5,
            "payload": 1.0,
            "wind_resistance": 12,
            "thermal": 1
        },
        {
            "name": "Autel EVO Max 4T",
            "flight_time": 42,
            "range": 20,
            "resolution": 50,
            "position_accuracy": 1.2,
            "payload": 1.2,
            "wind_resistance": 15,
            "thermal": 1
        }
    ]
