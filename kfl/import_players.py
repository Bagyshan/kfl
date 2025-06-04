import os
from core.models import Players

image_folder = "Азиягол"  # Укажите путь к папке с изображениями

for player in Players.objects.all():
    try:
        # Возможные названия файлов
        file_name_variants = [
            f"{player.first_name} {player.last_name}.JPG",
            f"{player.first_name}_{player.last_name}.JPG",
            f"{player.last_name} {player.first_name}.JPG",
            f"{player.last_name}_{player.first_name}.JPG"
        ]

        image_path = None
        for file_name in file_name_variants:
            full_path = os.path.join(image_folder, file_name)
            if os.path.exists(full_path):
                image_path = full_path
                break

        if image_path:
            player.photo = image_path
            player.save()
            print(f"Фото добавлено для {player.first_name} {player.last_name}: {image_path}")

    except Exception as e:
        print(f"Ошибка при добавлении фото для {player.first_name} {player.last_name}: {e}")

print("Все фото успешно добавлены!")