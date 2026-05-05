import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

# ========== Модели комплексного показателя ==========
def evaluate_models(q_values, weights, model='arithmetic'):
    if model == 'arithmetic':
        return np.dot(q_values, weights)
    elif model == 'geometric':
        # Заменяем clip(min=...) на clip(lower=...)
        return np.exp(np.dot(weights, np.log(np.clip(q_values, 1e-10, None))))
    elif model == 'harmonic':
        # Заменяем clip(min=...) на clip(lower=...)
        return 1 / np.dot(weights, 1 / np.clip(q_values, 1e-10, None))
    elif model == 'quadratic':
        return np.sqrt(np.dot(weights, q_values ** 2))
    else:
        raise ValueError("Неизвестная модель")

# ========== Конфигурация типов продукции ==========
PRODUCTS = {
    1: {
        "key": "quadcopter_video",
        "name": "Квадрокоптеры для видеосъемки",
        "params": [
            {"id": "flight_time", "name": "Время полёта, мин", "direction": "direct"},
            {"id": "range", "name": "Дальность передачи видео, км", "direction": "direct"},
            {"id": "resolution", "name": "Разрешение камеры, Мп", "direction": "direct"},
            {"id": "position_accuracy", "name": "Точность позиционирования, м", "direction": "inverse"},
            {"id": "payload", "name": "Грузоподъёмность, кг", "direction": "direct"},
            {"id": "wind_resistance", "name": "Ветроустойчивость, м/с", "direction": "direct"},
            {"id": "thermal", "name": "Наличие тепловизора (0/1)", "direction": "direct"}
        ]
    },
    2: {
        "key": "wing_uav",
        "name": "БПЛА типа крыло",
        "params": [
            {"id": "flight_time", "name": "Время полёта, мин", "direction": "direct"},
            {"id": "range", "name": "Дальность полёта, км", "direction": "direct"},
            {"id": "resolution", "name": "Разрешение камеры, Мп", "direction": "direct"},
            {"id": "position_accuracy", "name": "Точность позиционирования, м", "direction": "inverse"},
            {"id": "payload", "name": "Грузоподъёмность, кг", "direction": "direct"},
            {"id": "max_speed", "name": "Максимальная скорость, км/ч", "direction": "direct"}
        ]
    },
    3: {
        "key": "camera_aerial",
        "name": "Видеокамеры для съемки местности",
        "params": [
            {"id": "resolution_mpx", "name": "Разрешение матрицы, Мп", "direction": "direct"},
            {"id": "fps", "name": "Частота кадров при макс. разрешении, к/с", "direction": "direct"},
            {"id": "sensor_size", "name": "Размер матрицы (усл. ед.)", "direction": "direct"},
            {"id": "stabilization", "name": "Оптическая стабилизация (0/1)", "direction": "direct"},
            {"id": "fov", "name": "Угол обзора, градусы", "direction": "direct"},
            {"id": "min_illum", "name": "Минимальная освещённость, люкс", "direction": "inverse"}
        ]
    }
}

def load_product_config():
    """Отображает список доступных типов и возвращает выбранный."""
    print("\nДоступные типы продукции. Выберите 1 если используете тестовый файл:")
    for num, info in PRODUCTS.items():
        print(f"  {num}. {info['name']}")
    while True:
        try:
            choice = int(input("\nВведите номер типа продукции: "))
            if choice in PRODUCTS:
                config = PRODUCTS[choice]
                print(f"\nВыбран: {config['name']}")
                return config
            else:
                print("Пожалуйста, введите номер из списка.")
        except ValueError:
            print("Введите корректное число.")

def normalize_data(df, params_info):
    """Нормирует показатели образцов."""
    q_dict = {}
    for p in params_info:
        col = p['id']
        if col not in df.columns:
            raise ValueError(f"Столбец '{col}' отсутствует в данных.")
        if p['direction'] == 'direct':
            q_dict[col] = df[col] / df[col].max()
        else:
            # Заменяем clip(min=...) на clip(lower=...)
            q_dict[col] = df[col].min() / df[col].clip(lower=1e-10)
    return pd.DataFrame(q_dict)

def load_from_file():
    """Загружает данные образцов из файла CSV или JSON."""
    while True:
        filename = input("\nВведите полный путь к файлу с данными и имя файла с расширением(CSV или JSON): ").strip()
        if not filename:
            print("Имя файла не может быть пустым.")
            continue
        if not os.path.exists(filename):
            print(f"Файл '{filename}' не найден. Проверьте путь и попробуйте снова.")
            continue
        try:
            if filename.lower().endswith('.json'):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                df = pd.read_csv(filename)
            
            if 'name' not in df.columns:
                print("Ошибка: файл должен содержать столбец 'name' с названиями образцов.")
                continue
            
            print(f"\nЗагружено {len(df)} образцов.")
            return df
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            retry = input("Попробовать снова? (y/n, по умолч. y): ").strip().lower()
            if retry and retry != 'y':
                return None

def manual_input(params):
    """Ручной ввод данных образцов."""
    try:
        n = int(input("\nКоличество образцов: "))
    except ValueError:
        print("Некорректное число.")
        return None
    
    samples = []
    for i in range(n):
        print(f"\n--- Образец {i+1} ---")
        sample = {}
        sample['name'] = input("Название образца: ")
        for p in params:
            while True:
                try:
                    val = float(input(f"  {p['name']}: "))
                    sample[p['id']] = val
                    break
                except ValueError:
                    print("  Введите число.")
        samples.append(sample)
    return pd.DataFrame(samples)

def main():
    print("="*60)
    print("ОЦЕНКА ТЕХНИЧЕСКОГО УРОВНЯ ПРОДУКЦИИ ПРОМЫШЛЕННЫХ ДРОНОВ")
    print("="*60)

    # 1. Выбор типа продукции
    config = load_product_config()
    params = config['params']
    param_ids = [p['id'] for p in params]

    # 2. Ввод данных (по умолчанию загрузка из файла)
    print("\n--- ВВОД ДАННЫХ ОБРАЗЦОВ ---")
    choice = input("Загрузить данные из файла? (Y/n, по умолч. Y): ").strip().lower()
    
    # По умолчанию Y (загрузка из файла)
    if choice == '' or choice == 'y':
        df = load_from_file()
        if df is None:
            print("Не удалось загрузить данные. Завершение программы.")
            return
    else:
        df = manual_input(params)
        if df is None or len(df) == 0:
            print("Данные не введены. Завершение программы.")
            return

    print("\nИсходные данные:")
    print(df.to_string(index=False))

    # 3. Веса показателей
    print("\n--- ВЕСА ПОКАЗАТЕЛЕЙ ---")
    print("Характеристики:")
    for i, p in enumerate(params):
        print(f"  {i+1}. {p['name']}")
    
    weights_input = input(f"\nВведите {len(params)} весов через запятую (или Enter для равных весов): ").strip()
    if weights_input:
        try:
            weights = np.array([float(w.strip()) for w in weights_input.split(',')])
            if len(weights) != len(param_ids):
                print(f"Ошибка: ожидалось {len(param_ids)} весов, получено {len(weights)}.")
                return
            weights = weights / weights.sum()
        except ValueError:
            print("Ошибка: некорректный формат весов.")
            return
    else:
        weights = np.ones(len(param_ids)) / len(param_ids)
        print("Назначены равные веса.")

    # 4. Модель оценки
    print("\n--- МОДЕЛЬ ОЦЕНКИ ---")
    print("Доступные модели:")
    print("  arithmetic - средневзвешенная арифметическая: слабые стороны компенсируются сильными")
    print("  geometric  - средневзвешенная геометрическая: важна сбалансированность")
    print("  harmonic   - средневзвешенная гармоническая: необходимо гарантировать, что ни один показатель не будет катастрофически плохим")
    print("  quadratic  - средневзвешенная квадратическая: особо ценятся выдающиеся характеристики")
    model = input("Выберите модель (по умолч. arithmetic): ").strip().lower() or "arithmetic"
    if model not in ['arithmetic', 'geometric', 'harmonic', 'quadratic']:
        print(f"Неизвестная модель '{model}'. Используется arithmetic.")
        model = 'arithmetic'

    # 5. Расчёт
    print("\n--- РАСЧЁТ ---")
    try:
        q_df = normalize_data(df.drop('name', axis=1), params)
    except Exception as e:
        print(f"Ошибка при нормировании данных: {e}")
        return
    
    q_vals = q_df[param_ids].values
    Q = np.array([evaluate_models(q_vals[i], weights, model) for i in range(len(q_vals))]) * 100

    results = pd.DataFrame({'Образец': df['name'], 'Технический уровень': Q})
    results = results.sort_values('Технический уровень', ascending=False)
    results = results.reset_index(drop=True)

    print("\n===== РЕЗУЛЬТАТЫ ОЦЕНКИ =====")
    print(f"Модель: {model}")
    print(results.to_string(index=False))

    # 6. Визуализация
    print("\nФормирование графиков...")
    
    # Столбчатая диаграмма
    plt.figure(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(results)))
    bars = plt.bar(range(len(results)), results['Технический уровень'], color=colors)
    plt.ylabel('Технический уровень (0-100)')
    plt.title(f'Комплексный показатель качества (модель: {model})', fontsize=14, fontweight='bold')
    plt.ylim(0, 105)
    plt.xticks(range(len(results)), results['Образец'], rotation=30, ha='right')
    for i, (bar, val) in enumerate(zip(bars, results['Технический уровень'])):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{val:.1f}',
                 ha='center', fontsize=10, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()

    # Радиальная диаграмма
    labels = [p['name'] for p in params]
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    colors_radar = [
        '#E6194B',  # красный
        '#3CB44B',  # зелёный
        '#FFE119',  # жёлтый
        '#4363D8',  # синий
        '#F58231',  # оранжевый
        '#911EB4',  # фиолетовый
        '#42D4F4',  # голубой
        '#F032E6',  # маджента
        '#BFEF45',  # лайм
        '#FABED4',  # розовый
    ]
    
    num_samples = len(df)
    
    for idx in range(num_samples):
        values = q_df.iloc[idx][param_ids].tolist()
        values += values[:1]
        
        color = colors_radar[idx % len(colors_radar)]
        
        ax.plot(angles, values, 'o-', 
                linewidth=2.5, 
                markersize=8,
                color=color,
                label=df.loc[idx, 'name'],
                markerfacecolor=color,
                markeredgecolor='white',
                markeredgewidth=1.5)
        
        ax.fill(angles, values, alpha=0.08, color=color)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10, fontweight='bold')
    ax.set_ylim(0, 1.1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=8)
    
    # Исправлено: legend_handles вместо legendHandles
    legend = ax.legend(loc='upper left', 
                       bbox_to_anchor=(1.2, 1.1), 
                       fontsize=10,
                       framealpha=0.9,
                       edgecolor='gray')
    
    # Исправлено: legend_handles вместо legendHandles
    for handle in legend.legend_handles:
        handle.set_markersize(10)
    
    plt.title('Профили нормированных характеристик', 
              fontsize=16, fontweight='bold', pad=30)
    plt.tight_layout()
    plt.show()
    print("\nПрограмма завершена.")

if __name__ == "__main__":
    main()