import vk_api
import random
import schedule
import time

# Вставьте ваш токен доступа
vk_session = vk_api.VkApi(
    token="vk1.a.biIYehSRrTdfMcDJCD-bzqIPf5SVpkxkn1nXhHB-41uMmyi9kdb2GgleK1UJ6MviiXSLl8yU_Pi8Tc42nNhLmZ_rMOmzH0AHbDHM5nwZc29sXz8LsB8hiav77BqnLB6wxcNcEmILtDCfREnnP3o0CjI3YI-WZBGixSyrk3H8Gohq0si4cnXYZSpFVNRXjGGnJRIZ5ljBD8US2ro_y6GLzw")
vk = vk_session.get_api()

GROUP_ID = 224106070  # Числовой идентификатор вашей группы


def get_active_subscribers():
    try:
        # Получаем список подписчиков группы
        subscribers = vk.groups.getMembers(group_id=GROUP_ID, fields='activity')['items']
        if not subscribers:
            print("У вас нет подписчиков.")
            return []

        # Фильтруем подписчиков по активности (наличию лайков и комментариев)
        active_subscribers = [subscriber for subscriber in subscribers if 'activity' in subscriber]

        return active_subscribers
    except Exception as e:
        print(f"Произошла ошибка при получении активных подписчиков: {e}")
        return []


def get_random_photos(users, count):
    try:
        random_photos = []
        sampled_users = random.sample(users, min(count, len(users)))
        for user in sampled_users:
            # Получаем первый пост со стены пользователя
            posts = vk.wall.get(owner_id=user['id'], count=1)['items']
            for post in posts:
                if 'attachments' in post:
                    for attachment in post['attachments']:
                        if attachment['type'] == 'photo':
                            random_photos.append((user['id'], attachment['photo']))
                            if len(random_photos) == count:
                                return random_photos
        print("Не удалось получить достаточное количество фотографий.")
        return random_photos
    except Exception as e:
        print(f"Произошла ошибка при получении фотографий: {e}")
        return []


def publish_photos(photos):
    try:
        attachments = []
        for user_id, photo in photos:
            attachments.append(f"photo{user_id}_{photo['id']}")
        if not attachments:
            print("Не удалось получить фотографии.")
            return

        # Создаем пост с прикрепленными фотографиями
        message = "💛Лайкайте фотографии участников💛\n\nХотите попасть в следующий пост? Подписывайтесь на сообщество и лайкайте посты!"
        vk.wall.post(owner_id=f"-{GROUP_ID}", message=message, attachments=",".join(attachments), from_group=1)
        print("Фотографии успешно опубликованы на стене группы.")
    except Exception as e:
        print(f"Произошла ошибка при публикации фотографий: {e}")


def like_time():
    try:
        # Получаем активных подписчиков
        active_subscribers = get_active_subscribers()
        photos = get_random_photos(active_subscribers, count=5)

        # Если недостаточно фотографий от подписчиков, дополняем друзьями
        if len(photos) < 5:
            recommended_users = vk.users.getRecommended(count=5 - len(photos))
            recommended_photos = [(user['id'], user['photo_200']) for user in recommended_users]
            photos.extend(recommended_photos)

        if not photos:
            print("Не удалось получить фотографии.")
            return

        # Публикуем пост с пятью фотографиями
        publish_photos(photos)

    except Exception as e:
        print(f"Произошла ошибка: {e}")


# Запускаем функцию каждую минуту
schedule.every(1).minute.do(like_time)

while True:
    schedule.run_pending()
    time.sleep(1)


