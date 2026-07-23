from backend.note import Note
from core.utils.thumbnail import get_thumbnail_path
import os
from pathlib import Path
from dotenv import load_dotenv


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

    def update_note(self, note_id, note_type, note_text):
        query = '''
            UPDATE notes SET text = :text, note_type = :type WHERE note_id = :id RETURNING * 
        '''
        params = {'text': note_text, 'type': note_type , 'id': note_id}
        results = self.database.execute_query(query, params, write=True)
        return Note(*results[0]) if results else None

    def delete_note(self, note_id):
        query = 'DELETE FROM notes WHERE note_id = :id RETURNING *'
        params = {'id': note_id}
        results = self.database.execute_query(query, params, write=True)

        if not results:
            print('something wrong')
            return None

        deleted = Note(*results[0])

        # Удаляем файл и превью если заметка файлового типа
        if deleted.note_type in ('photo', 'video', 'pdf', 'file'):
            env_path = Path(__file__).parent.parent.parent / '.env'
            print(f'ENV PATH: {env_path}')
            print(f'ENV EXISTS: {env_path.exists()}')
            load_dotenv(dotenv_path=env_path)
            print(f'UPLOAD_DIR: {os.environ.get("UPLOAD_DIR", "NOT SET")}')

            upload_dir = os.environ.get('UPLOAD_DIR', '')

            # Извлекаем относительную часть после uploads/
            # "uploads\pdf\file.pdf" → "pdf\file.pdf"
            note_path = Path(deleted.text)
            parts = note_path.parts

            # Находим индекс папки типа (photo/video/pdf/file)
            type_folders = {'photo', 'video', 'pdf', 'file'}
            type_idx = next(
                (i for i, p in enumerate(parts) if p in type_folders),
                None
            )

            if type_idx is not None:
                # Строим путь от UPLOAD_DIR
                relative = Path(*parts[type_idx:])  # pdf\file.pdf
                file_path = Path(upload_dir) / relative
            else:
                file_path = Path(upload_dir) / note_path.name

            print(f'DELETE PATH: {file_path}')
            print(f'EXISTS: {file_path.exists()}')

            if file_path.exists():
                file_path.unlink()
                print(f'FILE DELETED: {file_path}')

                thumbnail_path = Path(upload_dir).parent / Path(get_thumbnail_path(str(file_path)))
                print(f'thumbnail_path: {thumbnail_path}')
                if thumbnail_path.exists():
                    thumbnail_path.unlink()
                    print(f'THUMBNAIL DELETED: {thumbnail_path}')

        return deleted
