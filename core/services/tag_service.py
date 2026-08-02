# core/services/tag_service.py
from backend.tag import Tag


class TagService:
    def __init__(self, database):
        self.database = database

    def get_all_tags(self) -> list[Tag]:
        """Все теги."""
        results = self.database.execute_query('SELECT * FROM tags ORDER BY name')
        return [Tag(*row) for row in results]

    def get_or_create_tag(self, name: str) -> Tag:
        """Найти тег по имени или создать новый."""
        name = name.strip().lower()
        results = self.database.execute_query(
            'SELECT * FROM tags WHERE name = :name',
            {'name': name}
        )
        if results:
            return Tag(*results[0])

        results = self.database.execute_query(
            'INSERT INTO tags (name) VALUES (:name) RETURNING *',
            {'name': name},
            write=True
        )
        return Tag(*results[0])

    def get_tags_for_note(self, note_id: int) -> list[Tag]:
        """Теги конкретной заметки."""
        results = self.database.execute_query(
            '''
            SELECT t.tag_id, t.name FROM tags t
            JOIN note_tags nt ON t.tag_id = nt.tag_id
            WHERE nt.note_id = :note_id
            ORDER BY t.name
            ''',
            {'note_id': note_id}
        )
        return [Tag(*row) for row in results]

    def set_tags_for_note(self, note_id: int, tag_names: list[str]) -> list[Tag]:
        """Установить теги для заметки (заменяет все существующие)."""
        # Удаляем старые теги заметки
        self.database.execute_query(
            'DELETE FROM note_tags WHERE note_id = :note_id',
            {'note_id': note_id},
            write=True
        )

        tags = []
        for name in tag_names:
            if not name.strip():
                continue
            tag = self.get_or_create_tag(name)
            self.database.execute_query(
                'INSERT INTO note_tags (note_id, tag_id) VALUES (:note_id, :tag_id)',
                {'note_id': note_id, 'tag_id': tag.tag_id},
                write=True
            )
            tags.append(tag)
        return tags

    def delete_tag(self, tag_id: int) -> bool:
        """Удалить тег (и все его связи с заметками через CASCADE)."""
        results = self.database.execute_query(
            'DELETE FROM tags WHERE tag_id = :tag_id RETURNING *',
            {'tag_id': tag_id},
            write=True
        )
        return bool(results)
