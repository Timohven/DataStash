from backend.note import Note
from pathlib import Path


class NoteService:
    def __init__(self, database):
        self.database = database

    def create_note(self, author, note_type, note_text):
        query = '''
            INSERT INTO notes (author, note_type, text)
            VALUES (:author, :type, :text)
            RETURNING note_id, created_at, author, note_type, text
        '''
        params = {'author': author, 'type': note_type, 'text': note_text}
        results = self.database.execute_query(query, params, write=True)
        return Note(*results[0]) if results else None

    def get_notes_by_author(self, author):
        query = '''
            SELECT * FROM notes 
            WHERE author = :author
            ORDER BY created_at DESC
        '''
        params = {'author': author}
        results = self.database.execute_query(query, params)
        return [Note(*row) for row in results]

    def get_notes_by_author_and_tags(self, author: str, tag_names: list[str]) -> list:
        """
        Возвращает заметки автора отфильтрованные по тегам.
        Если tag_names пустой — возвращает все заметки автора.
        Логика: заметка должна содержать ВСЕ указанные теги (AND).
        """
        if not tag_names:
            print('WRONG TAGS! COUNT:')
            print(len(tag_names))
            return self.get_notes_by_author(author)

        query = '''
            SELECT n.* FROM notes n
            WHERE n.author = :author
            AND (
                SELECT COUNT(DISTINCT t.name)
                FROM tags t
                JOIN note_tags nt ON t.tag_id = nt.tag_id
                WHERE nt.note_id = n.note_id
                AND t.name = ANY(:tag_names)
            ) = :tag_count
            ORDER BY n.created_at DESC
        '''
        params = {
            'author': author,
            'tag_names': tag_names,
            'tag_count': len(tag_names),
        }
        results = self.database.execute_query(query, params)
        return [Note(*row) for row in results]

    def update_note(self, note_id, note_type, note_text):
        query = '''
            UPDATE notes SET text = :text, note_type = :type WHERE note_id = :id RETURNING * 
        '''
        params = {'text': note_text, 'type': note_type , 'id': note_id}
        results = self.database.execute_query(query, params, write=True)
        return Note(*results[0]) if results else None

    def delete_note(self, note_id):
        from core.config import UPLOAD_DIR
        from core.utils.thumbnail import get_thumbnail_path

        query = 'DELETE FROM notes WHERE note_id = :id RETURNING *'
        params = {'id': note_id}
        results = self.database.execute_query(query, params, write=True)

        if not results:
            print('something wrong')
            return None

        deleted = Note(*results[0])

        # Удаляем файл и превью если заметка файлового типа
        if deleted.note_type in ('photo', 'video', 'pdf', 'file'):
            note_path = Path(deleted.text)
            parts = note_path.parts

            type_folders = {'photo', 'video', 'pdf', 'file'}
            type_idx = next(
                (i for i, p in enumerate(parts) if p in type_folders),
                None
            )

            if type_idx is not None:
                file_path = UPLOAD_DIR / Path(*parts[type_idx:])
            else:
                file_path = UPLOAD_DIR / note_path.name

            print(f'DELETE PATH: {file_path}')
            print(f'EXISTS: {file_path.exists()}')

            if file_path.exists():
                file_path.unlink()
                print(f'FILE DELETED: {file_path}')

            thumbnail_path = Path(get_thumbnail_path(str(file_path)))
            thumbnail_path.unlink(missing_ok=True)
            print(f'THUMBNAIL DELETED: {thumbnail_path}')

        return deleted
