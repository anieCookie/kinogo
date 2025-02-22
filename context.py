
class ContexManager:
    def __init__(self):
        self.base_instruction = {
            'role': 'user',
            'content': (
                'Ты теперь модель, которая помогает найти интересующий фильм по описанию. '
                'Все данные о фильмах ты должен брать из базы данных "movies.db". '
                'Ты должен выдавать информацию о названии, годе выпуска, жанре и режиссёре фильма. Понял?'
            )
        }
        self.context = {}
        self.count = 0



    def add_message(self, user_id, message):
        if user_id not in self.context:
            self.context[user_id] = [self.base_instruction]
        # if len(self.context[user_id]) >= 5:
        #     print("Контекст обнуляется")
        #     self.context[user_id] = []
        self.context[user_id].append(message)
        # if user_id in self.context and len(self.context[user_id]) < 5:
        #     self.context[user_id].append(message)
        # else:
        #     self.context[user_id] = []

    def get_context(self, user_id):
        return self.context.get(user_id, [])

    def clear_context(self, user_id):
        if user_id in self.context:
            self.context[user_id] = []